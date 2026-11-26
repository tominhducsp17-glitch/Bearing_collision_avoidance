import numpy as np

from src.sim.integrators import rk4_step


def _err(dt):
    x, t = np.array([1.0]), 0.0
    for _ in range(int(round(1.0 / dt))):
        x = rk4_step(lambda t, x: -x, t, x, dt)
        t += dt
    return abs(x[0] - np.exp(-1.0))


def test_rk4_is_fourth_order():
    ratio = _err(0.1) / _err(0.05)
    assert 14 < ratio < 18          # 2^4 = 16
