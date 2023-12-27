from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT

page_router = APIRouter()

templates = Jinja2Templates(
    directory="app/front/templates"
)


@page_router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@page_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@page_router.get("/signin")
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})
