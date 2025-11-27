from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from typing import List

from ..repositories.membership_repository import MembershipRepository
from ..models.membership import MembershipRole, MembershipStatus, Membership


class MembershipController:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)

    def invite_member(self, group_id: UUID, invitation_data, invited_by: str):
        """Create a pending membership (invitation)."""
        try:
            membership = self.repo.create(
                group_id=group_id,
                user_id=invitation_data.user_id,
                role=invitation_data.role,
                status=MembershipStatus.PENDING,
                invited_by=UUID(invited_by) if invited_by else None,
            )
            return membership
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def add_member(self, group_id: UUID, membership_data, added_by: str = None):
        """Add a member directly to a group (immediate membership)."""
        try:
            user_id = membership_data.user_id
            role = membership_data.role
            
            # Check if already a member
            existing = self.repo.get_membership(group_id, user_id)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this group"
                )
            
            # Add as active member
            membership = self.repo.create(
                group_id=group_id,
                user_id=user_id,
                role=role,
                status=MembershipStatus.ACTIVE,
                invited_by=UUID(added_by) if added_by else None
            )
            return membership
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def list_members(self, group_id: UUID, user_id: str, status_filter: str = None):
        """List members. Requester must be a member."""
        if not self.repo.is_member(group_id, user_id):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this group")
             
        return self.repo.list_members(group_id, status_filter)

    def get_member(self, group_id: UUID, user_id: UUID, requester_id: str):
        """Get member details."""
        # Check access
        if not self.repo.is_member(group_id, requester_id):
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this group")
        
        member = self.repo.get_membership(group_id, user_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return member

    def update_member(self, group_id: UUID, user_id: UUID, membership_data, updated_by: str):
        """Update member role."""
        # Check permissions
        if not self.repo.is_admin_or_owner(group_id, updated_by):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins/owner can update members")
        
        target_member = self.repo.get_membership(group_id, user_id)
        if not target_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
            
        # Cannot change owner's role
        if target_member.role == MembershipRole.OWNER:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change role of the group owner")

        return self.repo.update_role(group_id, user_id, membership_data.role)

    def remove_member(self, group_id: UUID, user_id: UUID, removed_by: str):
        """Remove member from group."""
        target_member = self.repo.get_membership(group_id, user_id)
        if not target_member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        
        # Logic: 
        # 1. User removing themselves (leave)
        # 2. Owner/Admin removing others
        
        is_self = str(user_id) == str(removed_by)
        is_admin = self.repo.is_admin_or_owner(group_id, removed_by)
        
        if not (is_self or is_admin):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            
        # Cannot remove owner
        if target_member.role == MembershipRole.OWNER:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the group owner")
             
        self.repo.delete(group_id, user_id)

    def accept_invitation(self, group_id: UUID, user_id: str):
        """Accept a pending invitation: set status to ACTIVE."""
        membership = self.repo.get_membership(group_id, user_id)
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

        if membership.status != MembershipStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation not pending")

        updated = self.repo.update_status(group_id, user_id, MembershipStatus.ACTIVE)
        return updated

    def decline_invitation(self, group_id: UUID, user_id: str):
        """Decline/remove a pending invitation."""
        deleted = self.repo.delete(group_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    def leave_group(self, group_id: UUID, user_id: str):
        """Remove a membership (user leaves). Owner cannot leave."""
        # Check if owner
        if self.repo.is_owner(group_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot leave the group")

        deleted = self.repo.delete(group_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")