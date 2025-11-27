from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from ..repositories.group_repository import GroupRepository 
from ..repositories.membership_repository import MembershipRepository
from ..schemas.group_schemas import GroupCreate, GroupUpdate
from ..models.group import Group
from ..models.membership import MembershipRole, MembershipStatus

class GroupController:
    """Business Logic for Groups."""

    def __init__(self, db: Session):
        self.db = db
        self.group_repo = GroupRepository(db)
        self.membership_repo = MembershipRepository(db)
    
    def create_group(self, group_data: GroupCreate, owner_id: int) -> Group:
        """
        Creates a group and automatically assigns the creator as the Owner.
        """
        # 1. Create the Group record
        group = self.group_repo.create(
            name=group_data.name,
            description=group_data.description,
            visibility=group_data.visibility,
            owner_id=str(owner_id) 
        )
        
        # 2. Create the Membership record for the owner
        # Uses group.id (which is now an auto-generated int)
        self.membership_repo.create(
            group_id=group.id,  # group.id is already a string from the repo
            user_id=str(owner_id),
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE
        )
        
        # 3. CRITICAL: Refresh the group object from the DB.
        # This allows SQLAlchemy to see the new membership we just added
        # so that 'group.member_count' returns 1 instead of 0.
        self.db.refresh(group)
        return group
    
    def list_user_groups(self, user_id: int, page: int = 1, size: int = 20, search: Optional[str] = None) -> dict:
        """Lists groups for a user with pagination metadata."""
        skip = (page - 1) * size
        groups, total = self.group_repo.list_user_groups(
            user_id=str(user_id),
            skip=skip,
            limit=size,
            search=search
        )
        
        # Return dictionary matching GroupListResponse schema
        return {
            "groups": groups,
            "total": total,
            "page": page,
            "size": size,
            "has_more": total > (page * size)
        }
    
    def get_group(self, group_id: int, user_id: int) -> Group:
        """Gets group details if user has access."""
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        
        # Permission check: Must be member OR group must be public
        is_member = self.membership_repo.is_member(group_id, user_id)
        is_public = group.visibility == "public"
        
        if not (is_member or is_public):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return group
    
    def update_group(self, group_id: int, group_data: GroupUpdate, user_id: int) -> Group:
        """Updates group only if user is Owner/Admin."""
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        
        # Permission check
        membership = self.membership_repo.get_membership(group_id, user_id)
        if not membership or membership.role not in [MembershipRole.OWNER, MembershipRole.ADMIN]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        
        # Exclude unset fields (don't overwrite with None)
        update_data = group_data.model_dump(exclude_unset=True)
        return self.group_repo.update(group_id, **update_data)
    
    def delete_group(self, group_id: int, user_id: int) -> None:
        """Deletes group only if user is Owner."""
        group = self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        
        if group.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete")
        
        # Clean up memberships first (good practice, though CASCADE handles it too)
        self.membership_repo.delete_all_memberships(group_id)
        self.group_repo.delete(group_id)