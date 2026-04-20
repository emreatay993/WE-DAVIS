from dataclasses import dataclass

import numpy as np


DEFAULT_RESIDUAL_FRACTIONS = np.array([0.10, 0.05, 0.02, 0.01, 0.001], dtype=float)


@dataclass(frozen=True)
class SteadyStateEstimate:
    damping_ratio: float
    excitation_frequency_hz: float
    mode_frequency_hz: float
    residual_fraction: float
    decay_rate_per_s: float
    time_constant_s: float
    estimated_time_s: float
    estimated_cycles: float
    rounded_cycle_count: int

    @property
    def settled_fraction(self) -> float:
        return 1.0 - self.residual_fraction


@dataclass(frozen=True)
class SteadyStateEstimateSnapshot:
    estimate: SteadyStateEstimate
    assume_resonance: bool


def estimate_cycles_to_steady_state(
    damping_ratio: float,
    excitation_frequency_hz: float,
    mode_frequency_hz: float | None = None,
    residual_fraction: float = 0.01,
) -> SteadyStateEstimate:
    """
    Estimate the transient run length required for the startup transient envelope
    to decay below a chosen residual fraction.

    The estimator follows the classical damped modal envelope:

        q_tr(t) ~ exp(-zeta * omega_n * t)

    so that, for a residual transient fraction ``r``,

        t_required = ln(1 / r) / (zeta * omega_n)
        N_cycles = f_exc * t_required

    When ``mode_frequency_hz`` is omitted, the estimator assumes the excitation is
    applied at the same dominant resonant frequency used for the transient run.
    """
    mode_frequency_hz = excitation_frequency_hz if mode_frequency_hz is None else mode_frequency_hz

    if not 0.0 < damping_ratio < 1.0:
        raise ValueError("Damping ratio must be between 0 and 1 for the underdamped estimate.")
    if excitation_frequency_hz <= 0.0:
        raise ValueError("Excitation frequency must be positive.")
    if mode_frequency_hz <= 0.0:
        raise ValueError("Mode frequency must be positive.")
    if not 0.0 < residual_fraction < 1.0:
        raise ValueError("Residual transient fraction must be between 0 and 1.")

    omega_n = 2.0 * np.pi * mode_frequency_hz
    decay_rate = damping_ratio * omega_n
    time_constant = 1.0 / decay_rate
    estimated_time = float(np.log(1.0 / residual_fraction) / decay_rate)
    estimated_cycles = float(excitation_frequency_hz * estimated_time)

    return SteadyStateEstimate(
        damping_ratio=float(damping_ratio),
        excitation_frequency_hz=float(excitation_frequency_hz),
        mode_frequency_hz=float(mode_frequency_hz),
        residual_fraction=float(residual_fraction),
        decay_rate_per_s=float(decay_rate),
        time_constant_s=float(time_constant),
        estimated_time_s=estimated_time,
        estimated_cycles=estimated_cycles,
        rounded_cycle_count=int(np.ceil(estimated_cycles)),
    )


def build_estimate_table(
    damping_ratio: float,
    excitation_frequency_hz: float,
    mode_frequency_hz: float | None = None,
    residual_fractions=None,
) -> list[SteadyStateEstimate]:
    residual_values = (
        DEFAULT_RESIDUAL_FRACTIONS
        if residual_fractions is None
        else np.asarray(residual_fractions, dtype=float)
    )
    return [
        estimate_cycles_to_steady_state(
            damping_ratio=damping_ratio,
            excitation_frequency_hz=excitation_frequency_hz,
            mode_frequency_hz=mode_frequency_hz,
            residual_fraction=float(residual_fraction),
        )
        for residual_fraction in residual_values
    ]
