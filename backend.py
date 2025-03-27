from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import pyotp,qrcode,io
from dateutil.tz import gettz
import datetime
from database import sql

def now():return str(datetime.datetime.now(tz=gettz('Asia/Kolkata'))).split('.')[0]


app = APIRouter()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/get_datas")
def get_datas(request:dict={}):
    data=sql.getdatas('select * from test_db.users limit 10')
    return {"status":"success",'data':data}

@app.post('/get_count')
def get_count(request:dict)-> int:
    try:
        data=sql.getdata('select count(1) from test_db.users limit 10')
        return data['count(1)']
    except Exception as e:print(e);return 0

@app.post("/save_data")
def save(request:dict):
    data=json.dumps(request['value'])
    sql.update('Architect.projects',{'diagram':data},f"where project='{request['project']}'")


@app.post("/get_data")
def get_data(request:dict):
    data = sql.getdatas(f"select diagram from Architect.projects  where project='{request['project']}'")
    data=json.loads(data[0]['diagram'])
    return data

fake_users_db = { "viswavisan": { "username": "viswavisan", "hashed_password": "fakehashedsecret", "totp_secret": pyotp.random_base32(), "is_verified": False, } }

@app.get("/2fa/qr")
async def get_qr_code(username: str):
    user = fake_users_db.get(username)
    if not user:raise HTTPException(status_code=404, detail="User not found")
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
    if not user:return {"message": "user not found"}  
    totp = pyotp.TOTP(user['totp_secret'])
    if totp.verify(token):
        fake_users_db[username]['is_verified'] = True
        return {"message": "2FA verification successful"}
    else:return {"message": "Invalid token"}
