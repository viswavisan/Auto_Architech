from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import  Request
import backend,frontend
app = FastAPI()
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

#disabled for testing purpose
# @app.middleware("http")
# async def enforce_https(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
#     response.headers["X-Frame-Options"] = "DENY"
#     response.headers['X-Content-Type-Options']= "nosniff"
#     response.headers["Content-Security-Policy"] = "default-src 'self'"
#     response.headers["X-XSS-Protection"] = "1; mode=block"
#     return response

# Allow all origins (for development purposes only)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
app.include_router(backend.app)
app.include_router(frontend.app)
