from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.repositories.membership_repository import MembershipRepository
from app.models.membership import MembershipRole, MembershipStatus, Membership


class MembershipController:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MembershipRepository(db)

    def invite_member(self, group_id: UUID, invitation_data, invited_by: str):
        """Create a pending membership (invitation)."""
        # invitation_data should have user_id and role
        try:
            membership = self.repo.create(
                group_id=group_id,
                user_id=invitation_data.user_id,
                role=invitation_data.role,
                status=MembershipStatus.PENDING,
                invited_by=invited_by,
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
            )
            return membership
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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
        """Remove a membership (user leaves). Owner cannot leave.

        If the user is the owner, raise 403.
        """
        # Check if owner
        if self.repo.is_owner(group_id, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner cannot leave the group")

        deleted = self.repo.delete(group_id, user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
