from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
# removed UUID import

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers.membership_controller import MembershipController
from app.schemas.membership_schemas import (
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
    group_id: int,  # <--- CHANGED
    membership_data: MembershipCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = MembershipController(db)
    return controller.add_member(
        group_id=group_id,
        membership_data=membership_data,
        added_by=int(current_user["id"])
    )


@router.get(
    "",
    response_model=List[MembershipResponse],
    summary="List group members"
)
async def list_members(
    group_id: int,  # <--- CHANGED
    status_filter: str = Query(None, description="Filter by status: active, pending"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = MembershipController(db)
    return controller.list_members(
        group_id=group_id,
        user_id=int(current_user["id"]),
        status_filter=status_filter
    )


@router.get(
    "/{user_id}",
    response_model=MembershipResponse,
    summary="Get member details"
)
async def get_member(
    group_id: int,  # <--- CHANGED
    user_id: int,   # <--- CHANGED
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = MembershipController(db)
    return controller.get_member(
        group_id=group_id,
        user_id=user_id,
        requester_id=int(current_user["id"])
    )

@router.put(
    "/{user_id}",
    response_model=MembershipResponse,
    summary="Update member role"
)
async def update_member(
    group_id: int,
    user_id: int,
    membership_data: MembershipUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = MembershipController(db)
    return controller.update_member(
        group_id=group_id,
        user_id=user_id,
        membership_data=membership_data,
        # FIX: Change str(...) to int(...)
        updated_by=int(current_user["id"]) 
    )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member from group"
)
async def remove_member(
    group_id: int,  # <--- CHANGED
    user_id: int,   # <--- CHANGED
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = MembershipController(db)
    controller.remove_member(
        group_id=group_id,
        user_id=user_id,
        removed_by=int(current_user["id"])
    )
    return None