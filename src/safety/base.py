"""Safety layer interface (PROJECT_CONTEXT §6.1, §6.3). Identity filter here;
the CBF-QP filter on the virtual vessels' acceleration Pi is src/safety/qp_filter.py (Mốc 7).
"""
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


@dataclass
class Environment:
    """Channel banks and obstacles. Empty in stage 1, but always passed through the runner."""
    banks: list = field(default_factory=list)
    obstacles: list = field(default_factory=list)


class SafetyFilter(Protocol):
    def filter(self, Pi_nom: dict, virtual_states: dict, env: Environment, t: float,
               others: dict | None = None) -> tuple[dict, dict]:
        """Return (Pi, info). Pi_nom, Pi: {follower id: (2,) earth-frame acceleration}.
        virtual_states: {follower id: (p_d (2,), p_d_dot (2,))} earth frame.
        others: {leader id: (p, p_dot, p_ddot)} kinematic agents (not decision variables)."""
        ...


class IdentityFilter:
    def filter(self, Pi_nom, virtual_states, env, t, others=None):
        return {i: np.array(v, float) for i, v in Pi_nom.items()}, {}
