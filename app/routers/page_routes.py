from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT

page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@page_router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@page_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
