<<<<<<< Updated upstream
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from core.database import get_db
from core.security import get_current_user
from controllers.membership_controller import MembershipController
from schemas.membership_schemas import (
    InvitationCreate,
    MembershipResponse
)

router = APIRouter(prefix="/groups/{group_id}", tags=["invitations"])


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
=======
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from .core.database import init_db
from .routes import group_routes, invitation_routes, membership_routes

# Define lifespan to run tasks on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up... creating database tables...")
    init_db()  # <--- This creates the tables based on your models
    yield
    print("🛑 Shutting down...")

app = FastAPI(title="Group Service API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers from the routes module
app.include_router(group_routes.router)
app.include_router(membership_routes.router)
app.include_router(invitation_routes.router)
>>>>>>> Stashed changes
