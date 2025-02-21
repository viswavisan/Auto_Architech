from fastapi import FastAPI
from fastapi import APIRouter,Request,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,HTMLResponse
templates = Jinja2Templates(directory="")
from fastapi.responses import JSONResponse
import pymysql
from pymysql.cursors import DictCursor
from fastapi.staticfiles import StaticFiles


connection=pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='test_db',
        cursorclass=DictCursor
    )

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/home')
def homepage(request:Request):

    with connection.cursor() as cursor:
        sql = "SELECT * FROM projects.projects"
        cursor.execute(sql)
        data = cursor.fetchall()



    return templates.TemplateResponse('architecture.html', context={'request': request,'data':data})



@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("logo.png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)