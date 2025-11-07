from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..core.database import get_db
from ..core.security import get_current_user
from ..controllers.membership_controller import MembershipController
from ..schemas.membership_schemas import (
    MembershipCreate,
    MembershipUpdate,
    MembershipResponse
)

router = APIRouter(prefix="/groups/{group_id}/members", tags=["memberships"])


@router.post(
    "",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to group"
)
async def add_member(
    group_id: UUID,
    membership_data: MembershipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new member to the group.
    
    Only group owner or admins can add members.
    - **user_id**: ID of user to add
    - **role**: member or admin (default: member)
    """
    controller = MembershipController(db)
    return controller.add_member(
        group_id=group_id,
        membership_data=membership_data,
        added_by=current_user["id"]
    )


@router.get(
    "",
    response_model=List[MembershipResponse],
    summary="List group members"
)
async def list_members(
    group_id: UUID,
    status_filter: str = Query(None, description="Filter by status: active, pending"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all members of the group.
    
    User must be a member of the group to view members.
    """
    controller = MembershipController(db)
    return controller.list_members(
        group_id=group_id,
        user_id=current_user["id"],
        status_filter=status_filter
    )


@router.get(
    "/{user_id}",
    response_model=MembershipResponse,
    summary="Get member details"
)
async def get_member(
    group_id: UUID,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details about a specific group member.
    """
    controller = MembershipController(db)
    return controller.get_member(
        group_id=group_id,
        user_id=user_id,
        requester_id=current_user["id"]
    )


@router.put(
    "/{user_id}",
    response_model=MembershipResponse,
    summary="Update member role"
)
async def update_member(
    group_id: UUID,
    user_id: UUID,
    membership_data: MembershipUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a member's role in the group.
    
    Only group owner or admins can update member roles.
    Cannot change the owner's role.
    """
    controller = MembershipController(db)
    return controller.update_member(
        group_id=group_id,
        user_id=user_id,
        membership_data=membership_data,
        updated_by=current_user["id"]
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from group"
)
async def remove_member(
    group_id: UUID,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from the group.
    
    - Owner and admins can remove members
    - Members can remove themselves (leave group)
    - Cannot remove the group owner
    """
    controller = MembershipController(db)
    controller.remove_member(
        group_id=group_id,
        user_id=user_id,
        removed_by=current_user["id"]
    )
    return None