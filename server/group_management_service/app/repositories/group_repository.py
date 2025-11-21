from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from ..models.group import Group, GroupVisibility


class GroupRepository:
    """
    Repository for Group model database operations.
    Handles all CRUD operations for groups.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        name: str,
        owner_id: UUID,
        description: Optional[str] = None,
        visibility: GroupVisibility = GroupVisibility.PRIVATE
    ) -> Group:
        """
        Create a new group.
        
        Args:
            name: Group name
            owner_id: UUID of the group owner
            description: Optional group description
            visibility: Group visibility (public, private, invite_only)
        
        Returns:
            Created Group object
        """
        # Convert owner_id to string to match SQLite storage
        owner_id_str = str(owner_id) if not isinstance(owner_id, str) else owner_id
        
        group = Group(
            name=name,
            description=description,
            visibility=visibility,
            owner_id=owner_id_str
        )
        
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        
        return group
    
    def get_by_id(self, group_id: UUID) -> Optional[Group]:
        """
        Get a group by ID.
        
        Args:
            group_id: Group UUID
        
        Returns:
            Group object or None if not found
        """
        return self.db.query(Group).filter(Group.id == str(group_id)).first()
    
    def get_by_name(self, name: str) -> Optional[Group]:
        """
        Get a group by exact name.
        
        Args:
            name: Group name
        
        Returns:
            Group object or None if not found
        """
        return self.db.query(Group).filter(Group.name == name).first()
    
    def list_all(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Group], int]:
        """
        List all groups with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            Tuple of (list of groups, total count)
        """
        query = self.db.query(Group)
        total = query.count()
        groups = query.offset(skip).limit(limit).all()
        
        return groups, total
    
    def list_user_groups(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Group], int]:
        """
        List all groups where user is a member.
        Joins with memberships table.
        
        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for group name
        
        Returns:
            Tuple of (list of groups, total count)
        """
        from ..models.membership import Membership, MembershipStatus
        
        # Base query - join groups with memberships
        query = self.db.query(Group).join(
            Membership,
            Group.id == Membership.group_id
        ).filter(
            and_(
                Membership.user_id == str(user_id),
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        
        # Add search filter if provided
        if search:
            query = query.filter(Group.name.ilike(f"%{search}%"))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and order
        groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
        
        return groups, total
    
    def list_by_owner(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Group], int]:
        """
        List all groups owned by a specific user.
        
        Args:
            owner_id: Owner UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            Tuple of (list of groups, total count)
        """
        query = self.db.query(Group).filter(Group.owner_id == str(owner_id))
        total = query.count()
        groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
        
        return groups, total
    
    def list_public_groups(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ) -> Tuple[List[Group], int]:
        """
        List all public groups.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Optional search term for group name
        
        Returns:
            Tuple of (list of groups, total count)
        """
        query = self.db.query(Group).filter(Group.visibility == GroupVisibility.PUBLIC)
        
        if search:
            query = query.filter(Group.name.ilike(f"%{search}%"))
        
        total = query.count()
        groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
        
        return groups, total
    
    def update(self, group_id: UUID, **kwargs) -> Optional[Group]:
        """
        Update group fields.
        
        Args:
            group_id: Group UUID
            **kwargs: Fields to update (name, description, visibility, owner_id)
        
        Returns:
            Updated Group object or None if not found
        """
        group = self.get_by_id(group_id)
        
        if not group:
            return None
        
        # Update only provided fields
        for key, value in kwargs.items():
            if hasattr(group, key) and value is not None:
                setattr(group, key, value)
        
        # Update timestamp
        group.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(group)
        
        return group
    
    def delete(self, group_id: UUID) -> bool:
        """
        Delete a group.
        Note: Memberships should be deleted first (cascade or manually).
        
        Args:
            group_id: Group UUID
        
        Returns:
            True if deleted, False if not found
        """
        group = self.get_by_id(group_id)
        
        if not group:
            return False
        
        self.db.delete(group)
        self.db.commit()
        
        return True
    
    def exists(self, group_id: UUID) -> bool:
        """
        Check if a group exists.
        
        Args:
            group_id: Group UUID
        
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(Group).filter(Group.id == str(group_id)).count() > 0
    
    def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Group], int]:
        """
        Search groups by name or description.
        
        Args:
            query: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            Tuple of (list of groups, total count)
        """
        search_query = self.db.query(Group).filter(
            or_(
                Group.name.ilike(f"%{query}%"),
                Group.description.ilike(f"%{query}%")
            )
        )
        
        total = search_query.count()
        groups = search_query.offset(skip).limit(limit).all()
        
        return groups, total