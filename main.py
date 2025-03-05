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
import os

from pipeline import deployment_pipeline

from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=os.getenv("AUTHORIZATION_URL"),
    tokenUrl=os.getenv("TOKEN_URL"),
)
print(oauth2_scheme)

app = FastAPI()


@app.get("/login")
async def login():
    redirect_uri = os.getenv("REDIRECT_URI")
    scope = quote("https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email")
    authorization_url = f"{os.getenv('AUTHORIZATION_URL')}?redirect_uri={redirect_uri}&response_type=code&client_id={os.getenv('CLIENT_ID')}&scope={scope}"
    return RedirectResponse(url=authorization_url)

connection=pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='test_db',
        cursorclass=DictCursor
    )



app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/home')
def homepage(request:Request):

    with connection.cursor() as cursor:
        sql = "SELECT * FROM Architect.projects"
        cursor.execute(sql)
        data = cursor.fetchall()

    return templates.TemplateResponse('architecture.html', context={'request': request,'data':data})

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
    print(data)
    return data
    

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("logo.png")


