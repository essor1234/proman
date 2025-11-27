from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
from ..models.membership import Membership, MembershipRole, MembershipStatus

class MembershipRepository:
    """Handles database operations for Memberships."""

    def __init__(self, db: Session):
        self.db = db
    
    def create(self, group_id: int, user_id: int, role: MembershipRole = MembershipRole.MEMBER, status: MembershipStatus = MembershipStatus.ACTIVE, invited_by: Optional[int] = None) -> Membership:
        """Creates a new membership record."""
        membership = Membership(
            group_id=group_id,
            user_id=user_id,
            role=role,
            status=status,
            invited_by=invited_by
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership
    
    def get_membership(self, group_id: int, user_id: int) -> Optional[Membership]:
        """Finds a specific user's membership in a specific group."""
        return self.db.query(Membership).filter(
            and_(Membership.group_id == group_id, Membership.user_id == user_id)
        ).first()
    
    def list_members(self, group_id: int, status_filter: Optional[str] = None) -> List[Membership]:
        """Lists members of a group, optionally filtered by status."""
        query = self.db.query(Membership).filter(Membership.group_id == group_id)
        if status_filter:
            query = query.filter(Membership.status == status_filter)
        return query.order_by(Membership.joined_at.desc()).all()
    
    def is_member(self, group_id: int, user_id: int) -> bool:
        """Helper: returns True if user is an ACTIVE member."""
        membership = self.get_membership(group_id, user_id)
        return membership is not None and membership.status == MembershipStatus.ACTIVE
    
    def is_admin_or_owner(self, group_id: int, user_id: int) -> bool:
        """Helper: returns True if user has administrative rights."""
        membership = self.get_membership(group_id, user_id)
        if not membership or membership.status != MembershipStatus.ACTIVE:
            return False
        return membership.role in [MembershipRole.OWNER, MembershipRole.ADMIN]

    def update_role(self, group_id: int, user_id: int, new_role: MembershipRole) -> Optional[Membership]:
        """Updates the role of a member."""
        membership = self.get_membership(group_id, user_id)
        if not membership: return None
        membership.role = new_role
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def delete(self, group_id: int, user_id: int) -> bool:
        """Removes a member from a group."""
        membership = self.get_membership(group_id, user_id)
        if not membership: return False
        self.db.delete(membership)
        self.db.commit()
        return True

    def delete_all_memberships(self, group_id: int) -> int:
        """Deletes all members (used when deleting the group itself)."""
        count = self.db.query(Membership).filter(Membership.group_id == group_id).delete()
        self.db.commit()
        return count
        
    def count_members(self, group_id: int) -> int:
        """Returns total count of members in a group."""
        return self.db.query(Membership).filter(Membership.group_id == group_id).count()

    def update_status(self, group_id: int, user_id: int, new_status: MembershipStatus):
        """Updates status (e.g. pending -> active)."""
        membership = self.get_membership(group_id, user_id)
        if membership:
            membership.status = new_status
            self.db.commit()
            self.db.refresh(membership)
        return membership