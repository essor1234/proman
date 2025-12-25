"""
Internal API Routes for Service-to-Service Communication
These endpoints are meant for other microservices (like project_management_service)
to query group data without requiring user authentication.

Security Note: In production, implement API key authentication or mTLS for these endpoints.
"""

from fastapi import APIRouter, Query, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.models.group import Group
from app.models.membership import Membership
from app.repositories.group_repository import GroupRepository
from app.repositories.membership_repository import MembershipRepository

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get(
    "/groups",
    summary="[Internal] List all groups"
)
async def list_all_groups(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=500, description="Page size"),
    visibility: Optional[str] = Query(None, description="Filter by visibility"),
    db: Session = Depends(get_db)
):
    """List all groups in the system (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    query = db.query(Group)
    if visibility:
        query = query.filter(Group.visibility == visibility)
    
    total = query.count()
    skip = (page - 1) * size
    groups = query.offset(skip).limit(size).all()
    
    result = []
    for group in groups:
        member_count = membership_repo.count_members(group.id)
        result.append({
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "visibility": group.visibility,
            "owner_id": group.owner_id,
            "member_count": member_count,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        })
    
    return {
        "groups": result,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }


@router.get(
    "/groups/search",
    summary="[Internal] Search groups"
)
async def search_groups(
    name: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search groups by name (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    groups = db.query(Group).filter(
        func.lower(Group.name).like(f"%{name.lower()}%")
    ).limit(limit).all()
    
    result = []
    for group in groups:
        member_count = membership_repo.count_members(group.id)
        result.append({
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "visibility": group.visibility,
            "owner_id": group.owner_id,
            "member_count": member_count,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        })
    
    return {
        "search_term": name,
        "result_count": len(result),
        "groups": result
    }


@router.get(
    "/groups/stats",
    summary="[Internal] Get group statistics"
)
async def get_group_stats(db: Session = Depends(get_db)):
    """Get group statistics (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    total_groups = db.query(Group).count()
    public_groups = db.query(Group).filter(Group.visibility == "public").count()
    private_groups = db.query(Group).filter(Group.visibility == "private").count()
    
    total_memberships = db.query(func.count(Membership.id)).scalar() or 0
    
    return {
        "total_groups": total_groups,
        "public_groups": public_groups,
        "private_groups": private_groups,
        "total_memberships": total_memberships,
        "avg_group_size": round(total_memberships / total_groups, 2) if total_groups > 0 else 0
    }


@router.get(
    "/groups/{group_id}",
    summary="[Internal] Get group by ID"
)
async def get_group_internal(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get group info by ID (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    member_count = membership_repo.count_members(group_id)
    
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "visibility": group.visibility,
        "owner_id": group.owner_id,
        "member_count": member_count,
        "created_at": group.created_at,
        "updated_at": group.updated_at,
    }


@router.get(
    "/groups/{group_id}/members",
    summary="[Internal] Get group members"
)
async def get_group_members_internal(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get list of members for a group (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    memberships = membership_repo.list_members(group_id)
    
    return {
        "group_id": str(group_id),
        "group_name": group.name,
        "member_count": len(memberships),
        "members": [
            {
                "user_id": m.user_id,
                "role": m.role.value if hasattr(m.role, 'value') else m.role,
                "status": m.status.value if hasattr(m.status, 'value') else m.status,
                "joined_at": m.joined_at
            }
            for m in memberships
        ]
    }


@router.get(
    "/groups/{group_id}/members-ids",
    summary="[Internal] Get member IDs only"
)
async def get_group_member_ids(
    group_id: UUID,
    db: Session = Depends(get_db)
):
    """Get member IDs for a group (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    memberships = membership_repo.list_members(group_id)
    
    return {
        "group_id": str(group_id),
        "member_ids": [m.user_id for m in memberships]
    }


@router.get(
    "/users/{user_id}/groups",
    summary="[Internal] Get groups for a user"
)
async def get_user_groups_internal(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all groups for a user (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    memberships = membership_repo.list_user_memberships(user_id)
    
    result = []
    for membership in memberships:
        group = group_repo.get_by_id(membership.group_id)
        if group:
            member_count = membership_repo.count_members(group.id)
            result.append({
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "visibility": group.visibility,
                "owner_id": group.owner_id,
                "member_count": member_count,
                "user_role": membership.role.value if hasattr(membership.role, 'value') else membership.role,
                "created_at": group.created_at,
                "updated_at": group.updated_at,
            })
    
    return {
        "user_id": str(user_id),
        "group_count": len(result),
        "groups": result
    }


@router.get(
    "/groups/{group_id}/check-member/{user_id}",
    summary="[Internal] Check if user is member"
)
async def check_group_member(
    group_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Check if user is member of group (internal endpoint)."""
    group_repo = GroupRepository(db)
    membership_repo = MembershipRepository(db)
    
    group = group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    is_member = membership_repo.is_member(group_id, user_id)
    membership = membership_repo.get_membership(group_id, user_id) if is_member else None
    
    return {
        "group_id": str(group_id),
        "user_id": str(user_id),
        "is_member": is_member,
        "role": membership.role.value if membership and hasattr(membership.role, 'value') else (membership.role if membership else None),
        "status": membership.status.value if membership and hasattr(membership.status, 'value') else (membership.status if membership else None),
    }
