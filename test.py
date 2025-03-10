from fastapi import FastAPI, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import pyotp
import secrets

app = FastAPI()

# Serve static files (like CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# In-memory user storage for demonstration purposes
fake_users_db = {
    "user@example.com": {
        "username": "user@example.com",
        "full_name": "John Doe",
        "email": "user@example.com",
        "hashed_password": "fakehashedpassword",
        "totp_secret": pyotp.random_base32(),  # Generate a TOTP secret for the user
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str
    full_name: str

class UserInDB(User):
    hashed_password: str
    totp_secret: str

def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    print(user)
    # if not user or (fake_hash_password(form_data.password) != user.hashed_password):
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Generate TOTP token
    totp = pyotp.TOTP(user.totp_secret)
    return {"access_token": user.username, "token_type": "bearer", "totp_token": totp.now()}

@app.post("/verify-2fa")
async def verify_2fa(username: str = Form(...), token: str = Form(...)):
    user = get_user(fake_users_db, username)
    if not user:
        raise HTTPException(status_code=400, detail="User  not found")
    
    # Verify the TOTP token
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(token):
        raise HTTPException(status_code=400, detail="Invalid 2FA token")
    
    return {"message": "2FA verification successful!"}

@app.get("/users/me", response_model=User )
async def read_users_me(token: str = Depends(oauth2_scheme)):
    user = get_user(fake_users_db, token)
    if user is None:
        raise HTTPException(status_code=404, detail="User  not found")
    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)