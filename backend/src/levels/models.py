from dataclasses import dataclass
from typing import List


@dataclass
class FactorCalculationParameters:
    initial_factor_level: float
    decay_constant: float
    refill_hours: List[float]
    week_duration: int
