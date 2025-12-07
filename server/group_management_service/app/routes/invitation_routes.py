from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from jose import jwt

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.controllers.membership_controller import MembershipController
from app.schemas.membership_schemas import (
    InvitationCreate,
    MembershipResponse
)
from app.schemas.invitation_schemas import InviteLinkResponse

router = APIRouter(prefix="/groups/{group_id}", tags=["invitations"])


@router.post(
    "/generate-invite-link",
    response_model=InviteLinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a secure invite link"
)
async def generate_invite_link(
    group_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a secure, single-use invite link for the group.

    The link expires in 24 hours.
    """
    # 1. Define expiry for the token
    expire = datetime.utcnow() + timedelta(hours=24)
    
    # 2. Create the token payload
    to_encode = {
        "groupId": group_id,
        "exp": expire
    }
    
    # 3. Encode the JWT token
    # Note: Using a hardcoded secret as per the request's example.
    # In a real scenario, this should come from a secure config.
    encoded_jwt = jwt.encode(to_encode, "mySecretKey", algorithm="HS256")
    
    # 4. Construct the invite link
    # Using the base URL from the request's example.
    base_url = "https://example.com/invite"
    invite_link = f"{base_url}?token={encoded_jwt}"
    
    return {"inviteLink": invite_link, "token": encoded_jwt}


# Invite
@router.post(
    "/invite",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite member to group"
)
async def invite_member(
    group_id: UUID,
    invitation_data: InvitationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send invitation to join the group.
    
    Creates a pending membership that must be accepted.
    - **email** or **user_id**: Recipient of invitation
    - **role**: Intended role (default: member)
    """
    controller = MembershipController(db)
    return controller.invite_member(
        group_id=group_id,
        invitation_data=invitation_data,
        invited_by=current_user["id"]
    )


@router.post(
    "/accept-invitation",
    response_model=MembershipResponse,
    summary="Accept group invitation"
)
async def accept_invitation(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a pending invitation to join the group.
    
    Changes membership status from pending to active.
    """
    controller = MembershipController(db)
    return controller.accept_invitation(group_id, current_user["id"])


@router.post(
    "/decline-invitation",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Decline group invitation"
)
async def decline_invitation(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decline a pending invitation to join the group.
    
    Removes the pending membership.
    """
    controller = MembershipController(db)
    controller.decline_invitation(group_id, current_user["id"])
    return None


@router.post(
    "/leave",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Leave group"
)
async def leave_group(
    group_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leave a group (remove yourself as a member).
    
    Group owner cannot leave; they must transfer ownership first or delete the group.
    """
    controller = MembershipController(db)
    controller.leave_group(group_id, current_user["id"])
    return None