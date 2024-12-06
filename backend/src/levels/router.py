import traceback
from typing import Dict

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from backend.src.common.utils import calculate_decay_constant
from backend.src.database.dependencies import get_db
from backend.src.levels.schemas import FactorLevelSettings, DefaultValues, FactorLevels, DecayConstantParameters
from backend.src.levels.service import calculate_factor_levels, get_values_for_default_user

router = APIRouter(
    prefix="/api/levels",
    tags=["levels"],
    responses={404: {"description": "Could not compute"}},
)


@router.post(
    "/update-levels",
    response_model=FactorLevels,
    responses={
        403: {"description": "Operation forbidden"},
        500: {"description": "Could not compute. Server error."}
    },

)
def get_factor_levels(settings: FactorLevelSettings) -> Dict[str, str]:
    try:
        result = calculate_factor_levels(settings)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=403, detail=str(ve))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Could not compute. Server error.")


@router.get(
    "/default-values",
    response_model=DefaultValues,
    responses={
        403: {"description": "Operation forbidden"},
        404: {"description": "Not Found"},
        500: {"description": "Server error"},
    },
)
def get_default_values(db: Session = Depends(get_db)) -> DefaultValues:
    try:
        default_values = get_values_for_default_user(db)
        return default_values
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Could not compute. Server error.")


@router.post("/calculate-decay-constant", response_model=dict)
def get_factor_levels(measurement: DecayConstantParameters) -> dict:
    decay_constant = calculate_decay_constant(peak_level=measurement.peak_level,
                                              measured_level=measurement.second_level_measurement,
                                              time_elapsed=measurement.time_elapsed)

    return {
        "decay_constant": decay_constant,
    }
