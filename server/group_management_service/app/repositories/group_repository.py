from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from ..models.group import Group, GroupVisibility

class GroupRepository:
    """Handles database operations for Groups."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, name: str, owner_id: int, description: Optional[str] = None, visibility: GroupVisibility = GroupVisibility.PRIVATE) -> Group:
        """Creates and saves a new group."""
        group = Group(
            name=name,
            description=description,
            visibility=visibility,
            owner_id=owner_id 
        )
        self.db.add(group)      # Add to session
        self.db.commit()        # Save to DB (Generates the ID)
        self.db.refresh(group)  # Reload to get the generated ID and timestamps
        return group
    
    def get_by_id(self, group_id: int) -> Optional[Group]:
        """Finds a group by Primary Key."""
        return self.db.query(Group).filter(Group.id == group_id).first()
    
    def list_user_groups(self, user_id: int, skip: int = 0, limit: int = 20, search: Optional[str] = None) -> Tuple[List[Group], int]:
        """
        Complex Query: Finds all groups a specific user belongs to.
        Requires joining Groups table with Memberships table.
        """
        from ..models.membership import Membership, MembershipStatus
        
        # Join Group + Membership
        query = self.db.query(Group).join(
            Membership, 
            Group.id == Membership.group_id
        ).filter(
            and_(
                Membership.user_id == user_id, 
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        
        # Optional search filter
        if search:
            query = query.filter(Group.name.ilike(f"%{search}%"))
        
        # Get count before pagination
        total = query.count()
        
        # Apply pagination
        groups = query.order_by(Group.created_at.desc()).offset(skip).limit(limit).all()
        
        return groups, total

    def update(self, group_id: int, **kwargs) -> Optional[Group]:
        """Updates fields dynamically based on kwargs."""
        group = self.get_by_id(group_id)
        if not group: return None
        
        # Iterate over provided fields and update group object
        for key, value in kwargs.items():
            if hasattr(group, key) and value is not None:
                setattr(group, key, value)
        
        group.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def delete(self, group_id: int) -> bool:
        """Deletes a group."""
        group = self.get_by_id(group_id)
        if not group: return False
        
        self.db.delete(group)
        self.db.commit()
        return True