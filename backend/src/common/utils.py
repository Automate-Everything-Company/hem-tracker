import numpy as np


def calculate_decay_constant(peak_level: float, measured_level: float, time_elapsed: float) -> float:
    return float((np.log(measured_level) - np.log(peak_level)) / time_elapsed)


def calculate_halving_time(decay_constant: float) -> float:
    return float(f"{abs(np.log(2) / decay_constant):.1f}")
