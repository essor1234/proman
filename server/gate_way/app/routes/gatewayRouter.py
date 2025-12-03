from fastapi import APIRouter, Request, Response
import httpx

router = APIRouter()

ACCOUNT_SERVICE_URL = "http://account_service:8000"
GROUP_SERVICE_URL = "http://group_service:8000"
PROJECT_SERVICE_URL = "http://project_service:8000"
FILE_SERVICE_URL = "http://file_service:8000"

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

### Create Group ###
@router.post("/groups")
async def createGroup(request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    # ✅ Fixed: Check for lowercase "authorization" and forward with proper case
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{GROUP_SERVICE_URL}/groups",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Group Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Get User's Groups ###
@router.get("/groups")
async def list_groups(request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    # Get query parameters
    params = dict(request.query_params)
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{GROUP_SERVICE_URL}/groups",
                headers=forward_headers,
                params=params,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Group Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Get Specific Group Details ###
@router.get("/groups/{group_id}")
async def get_group(group_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{GROUP_SERVICE_URL}/groups/{group_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Group Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Create Project ###
@router.post("/projects/")
async def createGroup(request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    # ✅ Fixed: Check for lowercase "authorization" and forward with proper case
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{PROJECT_SERVICE_URL}/projects/",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Prject Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Get All Projects ###
@router.get("/projects/")
async def list_projects(request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    # Get query parameters
    params = dict(request.query_params)
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{PROJECT_SERVICE_URL}/projects/",
                headers=forward_headers,
                params=params,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Project Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")