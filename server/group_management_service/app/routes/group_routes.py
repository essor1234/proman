from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers.group_controller import GroupController
from app.schemas.group_schemas import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupListResponse
)
from app.schemas.group_schemas import GroupWithMembersResponse

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
    """
    Create a new group with the current user as owner.
    
    - **name**: Group name (required)
    - **description**: Group description (optional)
    - **visibility**: public, private, or invite-only (default: private)
    """
    controller = GroupController(db)
    return controller.create_group(group_data, current_user["id"])


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
    """
    List all groups the current user is a member of or owns.
    
    Supports pagination and search.
    """
    controller = GroupController(db)
    return controller.list_user_groups(
        user_id=current_user["id"],
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
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific group.
    
    User must be a member of the group or the group must be public.
    """
    controller = GroupController(db)
    return controller.get_group(group_id, current_user["id"])


@router.get(
    "/{group_id}/members",
    response_model=GroupWithMembersResponse,
    summary="Get group details with member profiles"
)
async def get_group_with_members(
    group_id: UUID,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns group details plus members enriched with user profiles fetched
    from the Account Management Service. For performance consider adding a
    batch user endpoint on the account service.
    """
    controller = GroupController(db)
    # Extract the JWT token from the Authorization header for forwarding to account service
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None
    return controller.get_group_with_members(group_id, current_user["id"], token=token)


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group information"
)
async def update_group(
    group_id: UUID,
    group_data: GroupUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update group information.
    
    Only group owner or admins can update group details.
    """
    controller = GroupController(db)
    return controller.update_group(group_id, group_data, current_user["id"])


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group"
)
async def delete_group(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a group permanently.
    
    Only the group owner can delete the group.
    All memberships will be removed.
    """
    controller = GroupController(db)
    controller.delete_group(group_id, current_user["id"])
    return None


@router.post(
    "/{group_id}/transfer-ownership/{new_owner_id}",
    response_model=GroupResponse,
    summary="Transfer group ownership"
)
async def transfer_ownership(
    group_id: UUID,
    new_owner_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transfer group ownership to another member.
    
    Only the current owner can transfer ownership.
    The new owner must be an existing member of the group.
    """
    controller = GroupController(db)
    return controller.transfer_ownership(
        group_id=group_id,
        new_owner_id=new_owner_id,
        current_owner_id=current_user["id"]
    )