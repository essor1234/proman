from pydantic import BaseModel


class InviteLinkResponse(BaseModel):
    inviteLink: str
    token: str
