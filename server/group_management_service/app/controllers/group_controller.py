from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional

from ..repositories.group_repository import GroupRepository 
from ..repositories.membership_repository import MembershipRepository
from ..schemas.group_schemas import GroupCreate, GroupUpdate
from ..models.group import Group
from ..models.membership import MembershipRole, MembershipStatus


class GroupController:
    def __init__(self, db: Session):
        self.db = db
        self.group_repo = GroupRepository(db)
        self.membership_repo = MembershipRepository(db)
    
    def create_group(self, group_data: GroupCreate, owner_id: UUID) -> Group:
        """
        Create a new group with the current user as owner.
        Automatically creates owner membership.
        """
        # Create group
        group = self.group_repo.create(
            name=group_data.name,
            description=group_data.description,
            visibility=group_data.visibility,
            owner_id=owner_id
        )
        
        # Create owner membership
        self.membership_repo.create(
            group_id=group.id,
            user_id=owner_id,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE
        )
        
        return group
    
    def list_user_groups(
        self, 
        user_id: UUID, 
        page: int = 1, 
        size: int = 20,
        search: Optional[str] = None
    ) -> dict:
        """
        List all groups where user is a member.
        Supports pagination and search.
        """
        skip = (page - 1) * size
        
        groups, total = self.group_repo.list_user_groups(
            user_id=user_id,
            skip=skip,
            limit=size,
            search=search
        )
        
        return {
            "items": groups,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    def get_group(self, group_id: UUID, user_id: UUID) -> Group:
        """
        Get group details.
        User must be a member or group must be public.
        """
        group = self.group_repo.get_by_id(group_id)
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check access
        is_member = self.membership_repo.is_member(group_id, user_id)
        is_public = group.visibility == "public"
        
        if not (is_member or is_public):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this group"
            )
        
        return group
    
    def update_group(
        self, 
        group_id: UUID, 
        group_data: GroupUpdate, 
        user_id: UUID
    ) -> Group:
        """
        Update group information.
        Only owner or admins can update.
        """
        group = self.group_repo.get_by_id(group_id)
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check permission
        membership = self.membership_repo.get_membership(group_id, user_id)
        
        if not membership or membership.role not in [MembershipRole.OWNER, MembershipRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group owner or admins can update group"
            )
        
        # Update fields
        update_data = group_data.model_dump(exclude_unset=True)
        updated_group = self.group_repo.update(group_id, **update_data)
        
        return updated_group
    
    def delete_group(self, group_id: UUID, user_id: UUID) -> None:
        """
        Delete a group.
        Only owner can delete.
        """
        group = self.group_repo.get_by_id(group_id)
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Only owner can delete
        if group.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group owner can delete the group"
            )
        
        # Delete all memberships first
        self.membership_repo.delete_all_memberships(group_id)
        
        # Delete group
        self.group_repo.delete(group_id)
    
    def transfer_ownership(
        self, 
        group_id: UUID, 
        new_owner_id: UUID, 
        current_owner_id: UUID
    ) -> Group:
        """
        Transfer group ownership to another member.
        Only current owner can transfer.
        """
        group = self.group_repo.get_by_id(group_id)
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Verify current owner
        if group.owner_id != current_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only current owner can transfer ownership"
            )
        
        # Check new owner is a member
        new_owner_membership = self.membership_repo.get_membership(group_id, new_owner_id)
        
        if not new_owner_membership or new_owner_membership.status != MembershipStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New owner must be an active member of the group"
            )
        
        # Update group owner
        updated_group = self.group_repo.update(group_id, owner_id=new_owner_id)
        
        # Update old owner to admin
        self.membership_repo.update_role(group_id, current_owner_id, MembershipRole.ADMIN)
        
        # Update new owner role to owner
        self.membership_repo.update_role(group_id, new_owner_id, MembershipRole.OWNER)
        
        return updated_group
    
    def get_group_stats(self, group_id: UUID, user_id: UUID) -> dict:
        """
        Get group statistics.
        User must be a member.
        """
        group = self.get_group(group_id, user_id)
        
        member_count = self.membership_repo.count_members(group_id)
        
        return {
            "group_id": group.id,
            "name": group.name,
            "member_count": member_count,
            "created_at": group.created_at,
            "owner_id": group.owner_id
        }