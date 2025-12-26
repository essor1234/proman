from sqlalchemy import UUID
from sqlalchemy.orm import Session

from fastapi import HTTPException, status
from typing import Optional

from ..repositories.membership_repository import MembershipRepository
from ..models.membership import MembershipRole, MembershipStatus

class MembershipController:
    """Business Logic for Memberships."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)

    def add_member(self, group_id: int, membership_data, added_by: int = None):
        """Adds a new member directly (skipping invitation)."""
        user_id = membership_data.user_id
        
        # Prevent duplicates
        if self.repo.get_membership(group_id, user_id):
            raise HTTPException(status_code=400, detail="User already member")
            
        return self.repo.create(
            group_id=group_id,
            user_id=user_id,
            role=membership_data.role,
            status=MembershipStatus.ACTIVE,
            invited_by=added_by
        )

    def list_members(self, group_id: int, user_id: int, status_filter: str = None):
        """Lists members if the requester is a member."""
        if not self.repo.is_member(group_id, user_id):
             raise HTTPException(status_code=403, detail="Not a member")
        return self.repo.list_members(group_id, status_filter)

    def get_member(self, group_id: int, user_id: int, requester_id: int):
        """Gets single member details."""
        if not self.repo.is_member(group_id, requester_id):
             raise HTTPException(status_code=403, detail="Not a member")
        
        member = self.repo.get_membership(group_id, user_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        return member
    def update_member(self, group_id: int, user_id: int, membership_data, updated_by: int):
        """Update member role. Only Admin/Owner can do this."""
        # 1. Check permissions (updated_by must be admin/owner)
        if not self.repo.is_admin_or_owner(group_id, updated_by):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins/owner can update members")
        
        target_member = self.repo.get_membership(group_id, user_id)
        if not target_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
            
        # 2. Cannot change the Owner's role
        if target_member.role == MembershipRole.OWNER:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change role of the group owner")

        return self.repo.update_role(group_id, user_id, membership_data.role)

    def invite_member(self, group_id: int, invitation_data, invited_by: int):
        """Create a pending membership."""
        try:
            return self.repo.create(
                group_id=group_id,
                user_id=invitation_data.user_id,
                role=invitation_data.role,
                status=MembershipStatus.PENDING,
                invited_by=UUID(invited_by) if invited_by else None,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def accept_invitation(self, group_id: int, user_id: int):
        """Accept a pending invitation."""
        membership = self.repo.get_membership(group_id, user_id)
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

        if membership.status != MembershipStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation not pending")

        return self.repo.update_status(group_id, user_id, MembershipStatus.ACTIVE)

    def decline_invitation(self, group_id: int, user_id: int):
        """Decline/Delete a pending invitation."""
        deleted = self.repo.delete(group_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    def leave_group(self, group_id: int, user_id: int):
        """User leaves group."""
        if self.repo.is_owner(group_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot leave the group")

        deleted = self.repo.delete(group_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    def remove_member(self, group_id: int, user_id: int, removed_by: int):
        """
        Removes a member.
        Logic: 
        1. User can remove themselves (leave).
        2. Admins/Owner can remove others.
        3. Owner cannot be removed.
        """
        target_member = self.repo.get_membership(group_id, user_id)
        if not target_member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        is_self = user_id == removed_by
        is_admin = self.repo.is_admin_or_owner(group_id, removed_by)
        
        # Check permissions
        if not (is_self or is_admin):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
            
        # Protect the Owner
        if target_member.role == MembershipRole.OWNER:
             raise HTTPException(status_code=400, detail="Cannot remove owner")
             
        self.repo.delete(group_id, user_id)