"""Safety layer interface (PROJECT_CONTEXT §6.1, §6.3). Stage 1: identity only.

Stage 2 will add a CBF-QP filter on the virtual vessels' acceleration Pi (assumptions.md B-11).
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
    def filter(self, Pi_nom: dict, virtual_states: dict, env: Environment, t: float
               ) -> tuple[dict, dict]:
        """Return (Pi, info). Pi_nom, Pi: {follower id: (2,) earth-frame acceleration}."""
        ...


class IdentityFilter:
    def filter(self, Pi_nom, virtual_states, env, t):
        return {i: np.array(v, float) for i, v in Pi_nom.items()}, {}
