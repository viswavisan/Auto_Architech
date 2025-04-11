from fastapi import APIRouter,Request,HTTPException,Cookie
from fastapi.responses import RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")
from datetime import timedelta
import datetime,os
from dotenv import load_dotenv
from httpx import AsyncClient
from dateutil.tz import gettz
from log_function import log_user



app = APIRouter()
load_dotenv()
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

def now():return str(datetime.datetime.now(tz=gettz('Asia/Kolkata'))).split('.')[0]

@app.get("/login")
async def login(request:Request):
    return templates.TemplateResponse('login.html', context={'request': request})


@app.get("/login_with_git_hub")
async def login_git_hub():
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}"
    return RedirectResponse(url=redirect_uri)

@app.get("/logout")
async def logout(response: RedirectResponse):
    response.set_cookie(key="access_token", value="", httponly=True, expires=0)
    response.set_cookie(key="expiry", value="", httponly=True, expires=0)
    return RedirectResponse(url='/login')

@app.get("/github/callback")
async def auth_callback(code: str):
    async with AsyncClient(verify=False) as client:
        response = await client.post("https://github.com/login/oauth/access_token", data={"client_id": GITHUB_CLIENT_ID,"client_secret": GITHUB_CLIENT_SECRET,"code": code,}, headers={"Accept": "application/json"},)
        if response.status_code != 200:raise HTTPException(status_code=400, detail="Failed to obtain access token")
        token_data = response.json()
        access_token = token_data.get("access_token")
        response = RedirectResponse(url='/home')
        expiry = datetime.datetime.now() + timedelta(minutes=20)
        expiry_timestamp = int(expiry.timestamp())
        response.set_cookie(key="access_token", value=access_token, httponly=True, path="/",expires=expiry_timestamp)
        response.set_cookie(key="expiry", value=str(expiry_timestamp), httponly=True, path="/",expires=expiry_timestamp)
        return response

def check_token_expiry(func):
    async def wrapper(request: Request, access_token: str | None = Cookie(None), expiry: str | None = Cookie(None)):
        if access_token is None:return RedirectResponse(url='/login')
        if expiry is not None:
            current_time = int(datetime.datetime.now().timestamp())
            if current_time > int(expiry):return RedirectResponse(url='/login')
        return await func(request, access_token, expiry)
    return wrapper


@app.get("/home")
@check_token_expiry
async def home(request: Request,access_token: str | None = Cookie(None),expiry: str | None = Cookie(None)):
    
    async with AsyncClient(verify=False) as client:
        if not access_token:raise HTTPException(status_code=400, detail="No access token received")

        user_response = await client.get("https://api.github.com/user",headers={"Authorization": f"Bearer {access_token}"},)
        if user_response.status_code != 200:raise HTTPException(status_code=400, detail="Failed to fetch user information")
        user_info = user_response.json()
        # log_user(user_info,request)
        
    return templates.TemplateResponse('architecture.html', context={'request': request,'user':user_info['login'],'profile':user_info['avatar_url']})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("logo.png")