"""Mốc 7: HOCBF-QP filter on double integrators (src/safety/qp_filter.py)."""
import numpy as np

from src.safety.qp_filter import CBFFilter


def _simulate(filt, p, v, goal_acc, T=6.0, dt=1e-3, others=None):
    """Double integrators p_ddot = Pi with nominal accelerations goal_acc(p, v) filtered."""
    d_hist = []
    for k in range(int(T / dt)):
        Pi_nom = goal_acc(p, v)
        vs = {i: (p[i], v[i]) for i in p}
        oth = None if others is None else others(k * dt)
        Pi, _ = filt.filter(Pi_nom, vs, None, k * dt, others=oth)
        for i in p:
            p[i] = p[i] + dt * v[i] + 0.5 * dt ** 2 * Pi[i]
            v[i] = v[i] + dt * Pi[i]
        ids = list(p)
        d_hist.append(min(np.linalg.norm(p[a] - p[b]) for x, a in enumerate(ids) for b in ids[x + 1:])
                      if len(ids) > 1 else np.inf)
        if oth:
            d_hist[-1] = min(d_hist[-1], *(np.linalg.norm(p[i] - q[0]) for i in p for q in oth.values()))
    return np.array(d_hist)


def test_head_on_pair_keeps_margin():
    """Two vessels driven straight at each other (PD to the other's start) never get closer
    than D = d_min + 2 eps, while the acceleration bound holds."""
    filt = CBFFilter(d_min=2.0, eps=0.5, a1=1.0, a2=2.0, a_max=5.0)
    p = {3: np.array([-10.0, 0.1]), 4: np.array([10.0, -0.1])}
    v = {3: np.array([2.0, 0.0]), 4: np.array([-2.0, 0.0])}
    tgt = {3: np.array([10.0, 0.0]), 4: np.array([-10.0, 0.0])}
    acc = lambda p, v: {i: np.clip(2.0 * (tgt[i] - p[i]) - 2.0 * v[i], -3.5, 3.5) for i in p}
    d = _simulate(filt, p, v, acc)
    assert d.min() >= 3.0 - 1e-3
    assert filt.stats["infeasible"] == 0 and filt.stats["qp_solved"] > 0


def test_no_conflict_returns_nominal():
    filt = CBFFilter(d_min=2.0, eps=0.5, a_max=5.0)
    Pi_nom = {3: np.array([1.0, -2.0]), 4: np.array([0.5, 0.5])}
    vs = {3: (np.zeros(2), np.zeros(2)), 4: (np.array([20.0, 0.0]), np.zeros(2))}
    Pi, info = filt.filter(Pi_nom, vs, None, 0.0)
    assert not info["qp"] and all(np.array_equal(Pi[i], Pi_nom[i]) for i in Pi)


def test_leader_is_avoided_alone():
    """A kinematic leader moving through a parked follower: the follower gives way alone."""
    filt = CBFFilter(d_min=2.0, eps=0.3, a_max=5.0)
    p, v = {3: np.array([0.0, 0.0])}, {3: np.zeros(2)}
    lead = lambda t: {1: (np.array([-12.0 + 2.0 * t, 0.5]), np.array([2.0, 0.0]), np.zeros(2))}
    d = _simulate(filt, p, v, lambda p, v: {3: -2.0 * p[3] - 2.0 * v[3]}, T=12.0, others=lead)
    assert d.min() >= 2.3 - 1e-3
