"""Basis functions of the critic, actor and disturber NNs, Eqs. (51)-(56) and p. 18-19.

Paper A: sigma = the 45 products X(k) X(l), 1 <= k <= l <= 9; phi = psi = X(1), ..., X(9).
Written for an arbitrary index set so the same code serves the toy problems (Mốc 4).
All functions are vectorised: X has shape (..., n) and the output (..., l).
"""
import numpy as np


class QuadraticBasis:
    """sigma(X) = [X_k X_l for k <= l, k, l in idx] (row-major order, as on p. 18)."""

    def __init__(self, idx):
        self.idx = list(idx)
        self.pairs = [(a, b) for p, a in enumerate(self.idx) for b in self.idx[p:]]
        self.size = len(self.pairs)

    def __call__(self, X):
        X = np.asarray(X, float)
        return np.stack([X[..., a] * X[..., b] for a, b in self.pairs], axis=-1)

    def weights_from_P(self, P):
        """W_c such that W_c^T sigma(x) = x^T P x on the idx coordinates (P symmetric):
        coefficient P_kk on x_k^2 and 2 P_kl on x_k x_l (k < l)."""
        pos = {a: p for p, a in enumerate(self.idx)}
        return np.array([P[pos[a], pos[b]] * (1.0 if a == b else 2.0) for a, b in self.pairs])

    def P_from_weights(self, W):
        n = len(self.idx)
        pos = {a: p for p, a in enumerate(self.idx)}
        P = np.zeros((n, n))
        for w, (a, b) in zip(W, self.pairs):
            i, j = pos[a], pos[b]
            if i == j:
                P[i, i] = w
            else:
                P[i, j] = P[j, i] = w / 2
        return P


class LinearBasis:
    """phi(X) = [X_k, k in idx] (optionally with extra feature functions appended)."""

    def __init__(self, idx, extra=()):
        self.idx = list(idx)
        self.extra = list(extra)          # callables X -> (...,) for labelled variants
        self.size = len(self.idx) + len(self.extra)

    def __call__(self, X):
        X = np.asarray(X, float)
        cols = [X[..., k] for k in self.idx] + [f(X) for f in self.extra]
        return np.stack(cols, axis=-1)
