"""Performance metrics (assumptions.md B-8) and the safety log of PROJECT_CONTEXT §5.5."""
import numpy as np

from src.graph.bearing import bearing


def bearing_error(p, bearings):
    """||e|| = sqrt( sum_{(i,j) in E} ||g_ij - g*_ij||^2 ), p: (n, 2) actual positions."""
    return float(np.sqrt(sum(np.sum((bearing(p[i - 1], p[j - 1]) - g) ** 2)
                             for (i, j), g in bearings.items())))


def pairwise_min_distance(p):
    """(d_min, (i, j)) over all vessel pairs, 1-based ids."""
    p = np.asarray(p, float)
    d = np.linalg.norm(p[:, None, :] - p[None, :, :], axis=-1)
    iu = np.triu_indices(len(p), 1)
    k = int(np.argmin(d[iu]))
    return float(d[iu][k]), (int(iu[0][k]) + 1, int(iu[1][k]) + 1)


def iae(t, e):
    return float(np.trapezoid(np.abs(e), t))


def itae(t, e):
    return float(np.trapezoid(t * np.abs(e), t))


def rmse(t, e):
    """sqrt( (1/T) int ||e||^2 dt ) over the horizon [t0, t_end]."""
    return float(np.sqrt(np.trapezoid(np.asarray(e) ** 2, t) / (t[-1] - t[0])))


def settling_time(t, e, tol):
    """First time after which |e| stays below tol (nan if never)."""
    above = np.nonzero(np.abs(e) > tol)[0]
    if len(above) == 0:
        return float(t[0])
    k = above[-1] + 1
    return float(t[k]) if k < len(t) else float("nan")
