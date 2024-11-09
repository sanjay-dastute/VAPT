from fastapi import APIRouter
from app.api.v1.scanners import web

api_router = APIRouter()
api_router.include_router(web.router, prefix="/scanners/web", tags=["web"])
