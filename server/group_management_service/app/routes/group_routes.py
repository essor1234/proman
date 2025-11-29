from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
# removed UUID import

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers.group_controller import GroupController
from app.schemas.group_schemas import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupListResponse
)

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new group"
)
async def create_group(
    group_data: GroupCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    # Ensure user_id is passed as int
    return controller.create_group(group_data, int(current_user["id"]))


@router.get(
    "",
    response_model=GroupListResponse,
    summary="List all groups for current user"
)
async def list_groups(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: str = Query(None, description="Search by group name"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    return controller.list_user_groups(
        user_id=int(current_user["id"]),
        page=page,
        size=size,
        search=search
    )


@router.get(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Get group details"
)
async def get_group(
    group_id: int,  # <--- CHANGED FROM UUID TO int
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    return controller.get_group(group_id, int(current_user["id"]))


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group information"
)
async def update_group(
    group_id: int,  # <--- CHANGED FROM UUID TO int
    group_data: GroupUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    return controller.update_group(group_id, group_data, int(current_user["id"]))


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group"
)
async def delete_group(
    group_id: int,  # <--- CHANGED FROM UUID TO int
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    controller.delete_group(group_id, int(current_user["id"]))
    return None


@router.post(
    "/{group_id}/transfer-ownership/{new_owner_id}",
    response_model=GroupResponse,
    summary="Transfer group ownership"
)
async def transfer_ownership(
    group_id: int,      # <--- CHANGED FROM UUID TO int
    new_owner_id: int,  # <--- CHANGED FROM UUID TO int
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    controller = GroupController(db)
    return controller.transfer_ownership(
        group_id=group_id,
        new_owner_id=new_owner_id,
        current_owner_id=int(current_user["id"])
    )