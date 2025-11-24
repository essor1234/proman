from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from ..models.membership import Membership, MembershipRole, MembershipStatus


class MembershipRepository:
    """
    Repository for Membership model database operations.
    Handles all CRUD operations for group memberships.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        group_id: UUID,
        user_id: UUID,
        role: MembershipRole = MembershipRole.MEMBER,
        status: MembershipStatus = MembershipStatus.ACTIVE,
        invited_by: Optional[UUID] = None
    ) -> Membership:
        """
        Create a new membership.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
            role: Member role (owner, admin, member)
            status: Membership status (active, pending, removed)
            invited_by: UUID of user who invited (optional)
        
        Returns:
            Created Membership object
        """
        membership = Membership(
            group_id=str(group_id),
            user_id=str(user_id),
            role=role,
            status=status,
            invited_by=str(invited_by) if invited_by else None
        )
        
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        
        return membership
    
    def get_membership(self, group_id: UUID, user_id: UUID) -> Optional[Membership]:
        """
        Get a specific membership.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            Membership object or None if not found
        """
        return self.db.query(Membership).filter(
            and_(
                Membership.group_id == str(group_id),
                Membership.user_id == str(user_id)
            )
        ).first()
    
    def get_by_id(self, membership_id: UUID) -> Optional[Membership]:
        """
        Get membership by ID.
        
        Args:
            membership_id: Membership UUID
        
        Returns:
            Membership object or None if not found
        """
        return self.db.query(Membership).filter(Membership.id == str(membership_id)).first()
    
    def list_members(
        self,
        group_id: UUID,
        status_filter: Optional[str] = None
    ) -> List[Membership]:
        """
        List all members of a group.
        
        Args:
            group_id: Group UUID
            status_filter: Optional filter by status (active, pending, removed)
        
        Returns:
            List of Membership objects
        """
        query = self.db.query(Membership).filter(Membership.group_id == str(group_id))
                
        if status_filter:
            query = query.filter(Membership.status == status_filter)
        
        return query.order_by(Membership.joined_at.desc()).all()
    
    def list_user_memberships(
        self,
        user_id: UUID,
        status_filter: Optional[str] = None
    ) -> List[Membership]:
        """
        List all groups a user is a member of.
        
        Args:
            user_id: User UUID
            status_filter: Optional filter by status
        
        Returns:
            List of Membership objects
        """
        query = self.db.query(Membership).filter(Membership.user_id == str(user_id))
        
        if status_filter:
            query = query.filter(Membership.status == status_filter)
        
        return query.order_by(Membership.joined_at.desc()).all()
    
    def is_member(self, group_id: UUID, user_id: UUID) -> bool:
        """
        Check if user is an active member of the group.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            True if user is active member, False otherwise
        """
        membership = self.get_membership(group_id, user_id)
        return membership is not None and membership.status == MembershipStatus.ACTIVE
    
    def get_user_role(self, group_id: UUID, user_id: UUID) -> Optional[MembershipRole]:
        """
        Get user's role in a group.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            MembershipRole or None if not a member
        """
        membership = self.get_membership(group_id, user_id)
        return membership.role if membership else None
    
    def update_role(
        self,
        group_id: UUID,
        user_id: UUID,
        new_role: MembershipRole
    ) -> Optional[Membership]:
        """
        Update a member's role.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
            new_role: New role to assign
        
        Returns:
            Updated Membership object or None if not found
        """
        membership = self.get_membership(group_id, user_id)
        
        if not membership:
            return None
        
        membership.role = new_role
        membership.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(membership)
        
        return membership
    
    def update_status(
        self,
        group_id: UUID,
        user_id: UUID,
        new_status: MembershipStatus
    ) -> Optional[Membership]:
        """
        Update membership status.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
            new_status: New status to set
        
        Returns:
            Updated Membership object or None if not found
        """
        membership = self.get_membership(group_id, user_id)
        
        if not membership:
            return None
        
        membership.status = new_status
        membership.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(membership)
        
        return membership
    
    def delete(self, group_id: UUID, user_id: UUID) -> bool:
        """
        Delete a membership (remove user from group).
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            True if deleted, False if not found
        """
        membership = self.get_membership(group_id, user_id)
        
        if not membership:
            return False
        
        self.db.delete(membership)
        self.db.commit()
        
        return True
    
    def delete_all_memberships(self, group_id: UUID) -> int:
        """
        Delete all memberships for a group.
        Used when deleting a group.
        
        Args:
            group_id: Group UUID
        
        Returns:
            Number of memberships deleted
        """
        count = self.db.query(Membership).filter(
            Membership.group_id == str(group_id)
        ).delete()
        
        self.db.commit()
        
        return count
    
    def count_members(
        self,
        group_id: UUID,
        status: MembershipStatus = MembershipStatus.ACTIVE
    ) -> int:
        """
        Count members in a group.
        
        Args:
            group_id: Group UUID
            status: Status to count (default: active)
        
        Returns:
            Number of members
        """
        return self.db.query(Membership).filter(
            and_(
                Membership.group_id == str(group_id),
                Membership.status == status
            )
        ).count()
    
    def count_groups_for_user(
        self,
        user_id: UUID,
        status: MembershipStatus = MembershipStatus.ACTIVE
    ) -> int:
        """
        Count groups a user is member of.
        
        Args:
            user_id: User UUID
            status: Status to count (default: active)
        
        Returns:
            Number of groups
        """
        return self.db.query(Membership).filter(
            and_(
                Membership.user_id == str(user_id),
                Membership.status == status
            )
        ).count()
    
    def get_pending_invitations(self, user_id: UUID) -> List[Membership]:
        """
        Get all pending invitations for a user.
        
        Args:
            user_id: User UUID
        
        Returns:
            List of pending Membership objects
        """
        return self.db.query(Membership).filter(
            and_(
                Membership.user_id == str(user_id),
                Membership.status == MembershipStatus.PENDING
            )
        ).order_by(Membership.joined_at.desc()).all()
    
    def has_role(
        self,
        group_id: UUID,
        user_id: UUID,
        required_roles: List[MembershipRole]
    ) -> bool:
        """
        Check if user has one of the required roles in the group.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
            required_roles: List of acceptable roles
        
        Returns:
            True if user has one of the required roles
        """
        membership = self.get_membership(group_id, user_id)
        
        if not membership or membership.status != MembershipStatus.ACTIVE:
            return False
        
        return membership.role in required_roles
    
    def is_owner(self, group_id: UUID, user_id: UUID) -> bool:
        """
        Check if user is the owner of the group.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            True if user is owner
        """
        return self.has_role(group_id, user_id, [MembershipRole.OWNER])
    
    def is_admin_or_owner(self, group_id: UUID, user_id: UUID) -> bool:
        """
        Check if user is admin or owner of the group.
        
        Args:
            group_id: Group UUID
            user_id: User UUID
        
        Returns:
            True if user is admin or owner
        """
        return self.has_role(group_id, user_id, [MembershipRole.OWNER, MembershipRole.ADMIN])