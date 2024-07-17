import logging
import re
import traceback
from datetime import timedelta
from pathlib import Path
from typing import List

import requests
import sqlalchemy

from fastapi import FastAPI, Depends, HTTPException, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from starlette.requests import Request
from starlette.responses import JSONResponse

from sqlalchemy.orm import Session

from passlib.context import CryptContext

import secrets

from .api.router import router as api_router
from . import models, schemas, crud
from .auth import create_access_token, verify_token
from .calculations import calculate_decay_constant, calculate_halving_time
from .schemas import UserSignup
from .dependencies import get_db, oauth2_scheme
from .logging_config import setup_logging
from .dependencies import get_db, oauth2_scheme
from ..email_utils import send_reset_email

STATIC_PATH = Path(__file__).parents[1] / 'static'
TEMPLATES_PATH = Path(__file__).parents[1] / 'templates'

setup_logging()

logger = logging.getLogger("hem_tracker")

app = FastAPI(title="Hemophilia Tracker", version="0.0.1")

app.include_router(api_router)

app.mount("/static", StaticFiles(directory=str(STATIC_PATH)), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, you might use '*'; specify domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

templates = Jinja2Templates(directory=str(TEMPLATES_PATH))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username
    logger.debug(f"User attempt for username: {username}")
    db_user = crud.get_user_by_username(db, username=username)

    if db_user is None or not crud.verify_password(form_data.password, db_user.password):
        logger.warning(f"Failed login attempt: {username} not found.")
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not crud.verify_password(form_data.password, db_user.password):
        logger.warning(f"Failed login attempt: invalid password for username {form_data.username}")
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        if user.email:
            db_user = crud.get_user_by_email(db, email=user.email)
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")

        user.weekly_infusions = ", ".join(user.weekly_infusions)
        new_user = schemas.UserCreate(
            username=user.username,
            password=user.password,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            peak_level=user.peak_level,
            weekly_infusions=user.weekly_infusions,
        )
        crud.create_user(db=db, user=new_user)
        return {"detail": "Signup successful"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/request-password-reset")
def request_password_reset(request: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    identifier = request.identifier
    logger.debug(f"User attempt for password reset: {identifier}")

    if "@" in identifier:
        user = crud.get_user_by_email(db, email=identifier)
    else:
        user = crud.get_user_by_username(db, username=identifier)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = secrets.token_urlsafe(32)

    crud.save_reset_token(db, user.id, reset_token)

    logger.debug(f"Attempt to send link to user email: {user.email}")
    send_reset_email(user.email, reset_token)

    return {"detail": "Password reset instructions sent to your email"}


@app.get("/reset-password/{token}")
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_reset_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


@app.post("/reset-password")
def reset_password(request: schemas.PasswordReset, db: Session = Depends(get_db)):
    user = crud.get_user_by_reset_token(db, request.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    crud.update_user_password(db, user.id, request.new_password)
    crud.delete_reset_token(db, request.token)

    return {"detail": "Password reset successful"}


@app.delete("/users/")
def delete_user_by_email(email: str, db: Session = Depends(get_db)):
    logger.debug(f"Attempt to delete user: {email}")
    success = crud.delete_user_by_email(db, email)
    if not success:
        logger.debug(f"User not found: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted"}


@app.put("/users/{username}", response_model=schemas.User)
def update_user(username: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = crud.update_user(db, db_user, user)
    return db_user


@app.delete("/users/{username}", response_class=JSONResponse)
def delete_user_by_username(username: str, db: Session = Depends(get_db)):
    logger.debug(f"Attempt to delete user: {username}")
    success = crud.delete_user_and_measurements_by_username(db, username)
    if not success:
        logger.debug(f"User not found: {username}")
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content={"detail": "User deleted"})


@app.get("/users/{username}/data", response_model=schemas.User)
def read_user_json(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/user-data/{username}", response_model=schemas.UserPlotsData)
async def get_user_data(username: str, db: Session = Depends(get_db)):
    user_data = crud.get_user_plot_data(db, username)
    if user_data:
        return user_data
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{username}/measurements/", response_model=List[schemas.Measurement])
def read_measurements(username: str, db: Session = Depends(get_db)):
    logger.debug(f"Attempt to read user measurement for user: {username}")
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        logger.debug(f"User not found: {username}")
        raise HTTPException(status_code=404, detail="User not found")
    return db_user.measurements


@router.post("/users/{username}/measurements/", response_model=schemas.MeasurementCreate)
def create_measurement(username: str, measurement: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    logger.debug(f"Attempt to create measurement for user: {username}")
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        logger.debug(f"User not found: {username}")
        raise HTTPException(status_code=404, detail="User not found")

    decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                              measured_level=measurement.second_level_measurement,
                                              time_elapsed=measurement.time_elapsed)
    logger.debug(f"Calculate decay constant for measurement for user {username}: {decay_constant}")
    halving_time = calculate_halving_time(decay_constant=decay_constant)
    logger.debug(f"Calculate halving time for measurement for user {username}: {halving_time}")

    try:
        db_measurement = models.Measurement(
            user_id=db_user.id,
            peak_level=measurement.peak_level,
            time_elapsed=measurement.time_elapsed,
            second_level_measurement=measurement.second_level_measurement,
            decay_constant=decay_constant,
            halving_time=halving_time,
            comment=measurement.comment
        )
        db.add(db_measurement)
        db.commit()
        db.refresh(db_measurement)
        return db_measurement

    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()
        logger.debug(f"Integrity error: {e}")
    except sqlalchemy.exc.OperationalError as e:
        db.rollback()
        logger.debug(f"Operational error: {e}")
    except AttributeError as e:
        logger.debug(f"Attribute error: {e}")
    except Exception as e:
        db.rollback()
        logger.debug(f"Unexpected error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")


@app.post("/users/{username}/measurements", include_in_schema=False)
async def redirect_measurements(username: str):
    return RedirectResponse(url=f"/users/{username}/measurements/", status_code=307)


@app.delete("/users/{username}/measurements/{measurement_id}", response_model=schemas.Measurement)
def delete_measurement(username: str, measurement_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
    if db_measurement is None:
        raise HTTPException(status_code=404, detail="Measurement not found")

    db.delete(db_measurement)
    db.commit()
    return db_measurement


@app.post("/validate-token")
async def validate_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_token(token)
        return {"valid": True, "username": payload.get("sub")}
    except:
        return {"valid": False}


@app.post("/submit_contact_form")
async def submit_contact_form(
        email: str = Form(...),
        message: str = Form(...)
):
    url = "https://formspree.io/f/xanwnqyw"
    data = {"email": email, "message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return JSONResponse(
                content={"status": "success", "message": "Message sent. We will get back to you as soon as possible."})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to submit. Please try again later."})
    except requests.exceptions.ConnectionError:
        return JSONResponse(
            content={"status": "error", "message": "Failed to connect. Please check your network connection."})
    except requests.exceptions.Timeout:
        return JSONResponse(content={"status": "error", "message": "Request timed out. Please try again later."})
    except requests.exceptions.RequestException:
        return JSONResponse(content={"status": "error", "message": "A request error occurred. Please try again."})


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def show_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/disclaimer", response_class=HTMLResponse)
def show_disclaimer(request: Request):
    return templates.TemplateResponse("disclaimer.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
def get_signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def show_contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@app.get("/users/")
def read_user(email: str, request: Request, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("user.html", {"request": request, "user": db_user})


@app.get("/user/{username}", response_class=HTMLResponse)
def read_user_page(username: str, request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if username != payload.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Render the template to a string
    html_content = templates.TemplateResponse("user.html", {"request": request, "user": db_user}).body.decode('utf-8')
    return HTMLResponse(content=html_content)


app.include_router(router)
