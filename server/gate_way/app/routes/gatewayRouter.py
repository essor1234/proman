from fastapi import APIRouter, Request, Response
import httpx

router = APIRouter()

ACCOUNT_SERVICE_URL = "http://account_service:8000"
GROUP_SERVICE_URL = "http://group_service:8000"
PROJECT_SERVICE_URL = "http://project_service:8000"
FILE_SERVICE_URL = "http://file_service:8000"

### ACCOUNT SERVICE ###

### Login ###
@router.post("/login")
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

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Register ###
@router.post("/register")
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

### GROUP SERVICE ###

### Create Group ###
@router.post("/create/group")
async def create_group(request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
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

### List Groups ###
@router.get("/list/groups")
async def list_groups(request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
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

### Read Group ###
@router.get("/read/group/{group_id}")
async def read_group(group_id: int, request: Request):
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

### Update Group ###
@router.put("/update/group/{group_id}")
async def update_group(group_id: int, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(
                f"{GROUP_SERVICE_URL}/groups/{group_id}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Group Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Delete Group ###
@router.delete("/delete/group/{group_id}")
async def delete_group(group_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(
                f"{GROUP_SERVICE_URL}/groups/{group_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Group Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### PROJECT SERVICE ###

### Create Project ###
@router.post("/create/project")
async def create_project(request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
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

### List Projects ###
@router.get("/list/projects")
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

### Read Project ###
@router.get("/read/project/{project_id}")
async def read_project(project_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{PROJECT_SERVICE_URL}/projects/{project_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Project Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Update Project ###
@router.put("/update/project/{project_id}")
async def update_project(project_id: int, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.put(
                f"{PROJECT_SERVICE_URL}/projects/{project_id}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Project Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Delete Project ###
@router.delete("/delete/project/{project_id}")
async def delete_project(project_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(
                f"{PROJECT_SERVICE_URL}/projects/{project_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to Project Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### FILE SERVICE ###

### CREATE ###

### Create File ###
@router.post("/create/file/{projectid}")
async def create_file(projectid: str, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{FILE_SERVICE_URL}/api/v1/files/{projectid}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Create Folder ###
@router.post("/create/folder/{projectid}")
async def create_folder(projectid: str, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{FILE_SERVICE_URL}/api/v1/folders/project/{projectid}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### LIST ###

### List Files ###
@router.get("/list/files/")
async def list_files(request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{FILE_SERVICE_URL}/api/v1/files/",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### List Folders ###
@router.get("/list/folders/{projectid}")
async def list_folders(projectid: str, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{FILE_SERVICE_URL}/api/v1/folders/project/{projectid}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### UPDATE ###

### Update File ###
@router.patch("/update/file/{file_id}")
async def update_file(file_id: int, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.patch(
                f"{FILE_SERVICE_URL}/api/v1/files/file/{file_id}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Update Folder ###
@router.patch("/update/project/{projectid}/folder/{folder_id}")
async def update_folder(projectid: str, folder_id: int, request: Request):
    form_data = await request.json()

    forward_headers = {"Content-Type": "application/json"}
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.patch(
                f"{FILE_SERVICE_URL}/api/v1/folders/project/{projectid}/folder/{folder_id}",
                json=form_data,
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)

    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### DELETE ###

### Delete File ###
@router.delete("/delete/file/{file_id}")
async def delete_file(file_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(
                f"{FILE_SERVICE_URL}/api/v1/files/file/{file_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")

### Delete Folder ###
@router.delete("/delete/folder/project/{projectid}/folder/{folder_id}")
async def delete_folder(projectid: str, folder_id: int, request: Request):
    forward_headers = {"Content-Type": "application/json"}
    
    if "authorization" in request.headers:
        forward_headers["Authorization"] = request.headers["authorization"]
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(
                f"{FILE_SERVICE_URL}/api/v1/folders/project/{projectid}/folder/{folder_id}",
                headers=forward_headers,
                timeout=10.0,
            )
        except httpx.RequestError as e:
            return Response(content=f"❌ Cannot connect to File Service: {e}", status_code=502)
    
    return Response(content=resp.text, status_code=resp.status_code, media_type="application/json")