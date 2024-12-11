import logging
import traceback
from typing import Dict

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from backend.src.common.utils import calculate_decay_constant
from backend.src.database.dependencies import get_db
from backend.src.levels.schemas import FactorLevelSettings, DefaultValues, FactorLevels, DecayConstantParameters, \
    DecayConstant
from backend.src.levels.service import calculate_factor_levels, get_values_for_default_user

logger = logging.getLogger("hem_tracker")

router = APIRouter(
    prefix="/api/levels",
    tags=["levels"],
    responses={
        200: {"decription": "Successfully retrieved default values"},
        400: {"description": "Bad Request"},
        403: {"description": "Operation forbidden"},
        422: {"description": "Validation Error - Invalid request format"},
        500: {"description": "Internal Server Error - Calculating levels service error"},
    },
)


@router.post(
    "/update-levels",
    response_model=FactorLevels,
    responses={403: {"description": "Operation forbidden"}, 500: {"description": "Could not compute. Server error."}},
)
def get_factor_levels(settings: FactorLevelSettings) -> Dict[str, str]:
    try:
        result = calculate_factor_levels(settings)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Could not compute. Server error.")


@router.get(
    "/default-values",
    response_model=DefaultValues,

)
def get_default_values(db: Session = Depends(get_db)) -> DefaultValues:
    try:
        default_values = get_values_for_default_user(db)
        return default_values
    except ValueError as exc:
        logger.error(f"Error getting default values: {str(exc)}")
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error(f"Internal server error: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/calculate-decay-constant", response_model=DecayConstant)
def calculate_constant(measurement: DecayConstantParameters) -> DecayConstant:
    decay_constant = calculate_decay_constant(
        peak_level=measurement.peak_level,
        measured_level=measurement.second_level_measurement,
        time_elapsed=measurement.time_elapsed,
    )
    return DecayConstant(decay_constant=decay_constant)