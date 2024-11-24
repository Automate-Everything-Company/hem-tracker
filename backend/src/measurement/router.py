import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .schemas import MeasurementCreate, MeasurementResponse, MeasurementRequest
from .service import create_user_measurement
from ..database.dependencies import get_db
from ...app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/api/measurement",
    tags=["measurement"],
    responses={
        404: {"description": "Measurement not found"},
        500: {"description": "Internal server error"}
    },
)


@router.post("/{username}/measurements/", response_model=MeasurementCreate)
def create_measurement(username: str, measurement: MeasurementRequest, db: Session = Depends(get_db)):
    return create_user_measurement(db=db, username=username, measurement=measurement)

# @app.post("/users/{username}/measurements", include_in_schema=False)
# async def redirect_measurements(username: str):
#     return RedirectResponse(url=f"/users/{username}/measurements/", status_code=307)
#
#
# @app.delete("/users/{username}/measurements/{measurement_id}", response_model=schemas.Measurement)
# def delete_measurement(username: str, measurement_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.username == username).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db_measurement = db.query(models.Measurement).filter(models.Measurement.id == measurement_id).first()
#     if db_measurement is None:
#         raise HTTPException(status_code=404, detail="Measurement not found")
#
#     db.delete(db_measurement)
#     db.commit()
#     return db_measurement
#
#
# @app.get("/users/")
# def read_user(email: str, request: Request, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=email)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return templates.TemplateResponse("user.html", {"request": request, "user": db_user})
#
#
# @app.get("/user/{username}", response_class=HTMLResponse)
# def read_user_page(username: str, request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     payload = verify_token(token)
#     if username != payload.get("sub"):
#         raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
#     db_user = crud.get_user_by_username(db, username=username)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Render the template to a string
#     html_content = templates.TemplateResponse("user.html", {"request": request, "user": db_user}).body.decode('utf-8')
#     return HTMLResponse(content=html_content)
