from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from backend.src.authentication.domain import verify_token
from backend.src.core.config import TEMPLATES
from backend.src.database.crud import get_user_by_username
from backend.src.database.dependencies import get_db
from backend.src.users.router import oauth2_scheme

router = APIRouter(
    tags=["frontend"],
    responses={404: {"description": "Could not compute"}},
)


@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


@router.get("/about", response_class=HTMLResponse)
def show_about(request: Request):
    return TEMPLATES.TemplateResponse("about.html", {"request": request})


@router.get("/disclaimer", response_class=HTMLResponse)
def show_disclaimer(request: Request):
    return TEMPLATES.TemplateResponse("disclaimer.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def get_login_form(request: Request):
    return TEMPLATES.TemplateResponse("login.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
def get_signup_form(request: Request):
    return TEMPLATES.TemplateResponse("signup.html", {"request": request})


@router.get("/contact", response_class=HTMLResponse)
def show_contact_form(request: Request):
    return TEMPLATES.TemplateResponse("contact.html", {"request": request})