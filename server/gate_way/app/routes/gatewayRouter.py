from fastapi import APIRouter, Request, Response
import httpx

router = APIRouter()

ACCOUNT_SERVICE_URL = "http://account_service:8000"

### Login ###
@router.post("/auth/login")
async def login(request: Request):
    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ACCOUNT_SERVICE_URL}/auth/login",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Account Service: {e}", status_code=502)

    # Relay the account_service response to the frontend — including the correct status
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Register ###
@router.post("/auth/register")
async def register(request: Request):
    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{ACCOUNT_SERVICE_URL}/auth/register",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Account Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")