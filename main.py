from fastapi import FastAPI
from fastapi import APIRouter,Request,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
templates = Jinja2Templates(directory="")
from fastapi.responses import JSONResponse



app = FastAPI()
@app.get('/home')
def homepage(request:Request):
    return templates.TemplateResponse('home.html', context={'request': request})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("logo.png")

@app.middleware("http")
async def enforce_https(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers['X-Content-Type-Options']= "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
