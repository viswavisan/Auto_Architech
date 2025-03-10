from fastapi import FastAPI
from fastapi import APIRouter,Request,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,HTMLResponse
templates = Jinja2Templates(directory="templates")
from fastapi.responses import JSONResponse
import pymysql,json
from pymysql.cursors import DictCursor
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Depends, HTTPException, Request, Cookie
import os
from httpx import AsyncClient
import pyotp,qrcode,io
from fastapi.responses import StreamingResponse

from pipeline import deployment_pipeline
from dateutil.tz import gettz
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import timedelta
import datetime
import geocoder,requests

def now():
    return str(datetime.datetime.now(tz=gettz('Asia/Kolkata'))).split('.')[0]

load_dotenv()


GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")


app = FastAPI()

@app.get("/login")
async def login(request:Request):
    return templates.TemplateResponse('login.html', context={'request': request})

@app.get("/login_with_git_hub")
async def login_git_hub():
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}"
    return RedirectResponse(url=redirect_uri)

@app.get("/github/callback")
async def auth_callback(code: str):
    async with AsyncClient(verify=False) as client:
        response = await client.post("https://github.com/login/oauth/access_token",
            data={"client_id": GITHUB_CLIENT_ID,"client_secret": GITHUB_CLIENT_SECRET,"code": code,},
            headers={"Accept": "application/json"},)
        if response.status_code != 200:raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        


        # Set a cookie with the access token (or user info)
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

@app.get("/logout")
async def logout(response: RedirectResponse):
    # Clear the cookies by setting their expiration time to the past
    response.set_cookie(key="access_token", value="", httponly=True, expires=0)
    response.set_cookie(key="expiry", value="", httponly=True, expires=0)
    return RedirectResponse(url='/login')

connection=pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='test_db',
        cursorclass=DictCursor
    )

def get_ip_info(ip_address):
    response = requests.get(f'https://ipinfo.io/{ip_address}/json',verify=False)
    return response.json()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/home")
@check_token_expiry
async def home(request: Request,access_token: str | None = Cookie(None),expiry: str | None = Cookie(None)):
    
    async with AsyncClient(verify=False) as client:
        if not access_token:raise HTTPException(status_code=400, detail="No access token received")

        user_response = await client.get("https://api.github.com/user",headers={"Authorization": f"Bearer {access_token}"},)
        if user_response.status_code != 200:raise HTTPException(status_code=400, detail="Failed to fetch user information")

        user_info = user_response.json()
        
    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM Architect.projects")
        data = cursor.fetchall()

        cursor.execute("SELECT * FROM Architect.users WHERE name = %s", (user_info['login'],))
        user = cursor.fetchone()

        # Insert or update user
        if not user:
            cursor.execute(
                "INSERT INTO Architect.users (name, password, image, last_login, created_date) VALUES (%s, %s, %s, %s, %s)",
                (user_info['login'], str(user_info['id']), user_info['avatar_url'], now(), now()))
        else:
            cursor.execute("UPDATE Architect.users SET last_login = %s WHERE name = %s",(now(), user_info['login']))
        
        connection.commit()

        ip=request.client.host
        print(ip)
        ip = geocoder.ip('10.11.27.30')
        latitude = ip.latlng[0] if ip.latlng else None
        longitude = ip.latlng[1] if ip.latlng else None
        print(latitude,longitude)
        location=get_ip_info('10.11.27.30')
        print(location)

    return templates.TemplateResponse('architecture.html', context={'request': request,'data':data,'user':user_info['login'],'profile':user_info['avatar_url']})

@app.post("/save_data")
def save(request:dict):
    data=json.dumps(request['value'])
    with connection.cursor() as cursor:
        sql = f"update Architect.projects set diagram='{data}' where project='{request['project']}'"
        cursor.execute(sql)
        connection.commit()

@app.post("/get_data")
def save(request:dict):
    connection=pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='test_db',
        cursorclass=DictCursor
    )
    cursor=connection.cursor()
    sql = f"select diagram from Architect.projects  where project='{request['project']}'"
    cursor.execute(sql)
    data = cursor.fetchall()
    data=json.loads(data[0]['diagram'])
    return data
    

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("logo.png")

fake_users_db = {
    "viswavisan": {
        "username": "viswavisan",
        "hashed_password": "fakehashedsecret",
        "totp_secret": pyotp.random_base32(),  # Generate a TOTP secret
        "is_verified": False,
    }
}

@app.get("/2fa/qr")
async def get_qr_code(username: str):
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")
    
    totp = pyotp.TOTP(user['totp_secret'])
    uri = totp.provisioning_uri(name=username)
    
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")

@app.post("/2fa/verify")
async def verify_2fa(username: str, token: str):
    user = fake_users_db.get(username)
    if not user:
        return {"message": "user not found"}
    
    totp = pyotp.TOTP(user['totp_secret'])
    if totp.verify(token):
        fake_users_db[username]['is_verified'] = True
        return {"message": "2FA verification successful"}
    else:
        return {"message": "Invalid token"}
