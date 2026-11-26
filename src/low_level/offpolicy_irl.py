"""Off-policy IRL for H-infinity (tracking) control: Eqs. (43)-(45), (54)-(61), Algorithm 2
(phase 2) of Paper A = Algorithm 2 of [M15]. Knows NOTHING about vessels.

Off-policy Bellman equation (45) on interval [t_{j-1}, t_j], T = t_j - t_{j-1},
weights w(tau) = exp(-alpha (tau - t_{j-1})), behaviour data (X, u, d):

  [e^{-alpha T} sigma(X(t_j)) - sigma(X(t_{j-1}))]^T W_c
    + 2 int w (u - u_k)^T R W_a^T phi dtau  -  2 gamma^2 int w (d - d_k)^T W_d^T psi dtau
    = - int w ( X^T Q' X + u_k^T R u_k - gamma^2 d_k^T d_k ) dtau                  (*)

with u_k = W_a^(k)T phi(X), d_k = W_d^(k)T psi(X) the policies under evaluation and
(W_c, W_a, W_d) = (W_c^(k+1), W_a^(k+1), W_d^(k+1)) the unknowns. Stacking (*) over the M
intervals gives rho1 W = rho2 (Eq. (60)); note rho2 = -int(...) as in [M15] (77) — the sign
printed in (58)-(59) of Paper A is wrong (assumptions.md B-5).

vec(.) is column-major: phi^T W_a w = kron(w, phi)^T vec(W_a).
Integrals use the ZOH trapezoid rule on the n_sub sub-steps of each interval: u, d are
constant on a sub-step (value stored at its left sample), state functions vary linearly.
"""
import warnings
from dataclasses import dataclass, field

import numpy as np


class RankDeficientError(RuntimeError):
    """rho1 lacks full column rank: not enough excitation (PROJECT_CONTEXT §5.4.5)."""


@dataclass
class IRLResult:
    W_c: np.ndarray
    W_a: np.ndarray
    W_d: np.ndarray
    converged: bool
    history: list = field(default_factory=list)   # per iteration: dict(W_c, W_a, W_d, dW, bellman)
    rank: int = 0
    n_unknowns: int = 0
    cond: float = np.nan


def _zoh_trapezoid(w, h, left_const, smooth):
    """int over each interval of w(t) * left_const(t) (x) smooth(t), ZOH on left_const.
    w: (M, S+1); left_const: (M, S+1, a) (sample s holds on [s, s+1]); smooth: (M, S+1, b).
    Returns (M, a, b)."""
    g = w[..., None] * smooth                          # (M, S+1, b)
    seg = 0.5 * h * (g[:, :-1] + g[:, 1:])            # (M, S, b) int of w*smooth per sub-step
    return np.einsum("msa,msb->mab", left_const[:, :-1], seg)


def _trapezoid(w, h, f):
    """int over each interval of w(t) f(t) for smooth f: (M, S+1, ...) -> (M, ...)."""
    g = w.reshape(w.shape + (1,) * (f.ndim - 2)) * f
    return 0.5 * h * (g[:, :-1] + g[:, 1:]).sum(axis=1)


class OffPolicyHinf:
    """Phase 2 of Algorithm 2 on a fixed data set."""

    def __init__(self, sigma, phi, psi, Q_fn, R, gamma, alpha, rcond=None):
        """rcond: None -> plain least squares (exact problems, Mốc 4). A value such as 1e-6
        truncates singular directions below rcond * s_max of the column-scaled rho1, i.e. the
        weights of directions the data do not excite are set by the minimum-norm rule instead
        of being amplified (replication_report.md, Mốc 5)."""
        self.rcond = rcond
        self.sigma, self.phi, self.psi = sigma, phi, psi
        self.Q_fn = Q_fn                    # X (..., n) -> X^T Q' X  (...)
        self.R = np.atleast_2d(np.asarray(R, float))
        self.gamma, self.alpha = float(gamma), float(alpha)

    def precompute(self, data):
        """All integrals of (*) that do not depend on the iteration k."""
        t, X, U, D = data["t"], data["X"], data["U"], data["D"]
        T = t[:, -1] - t[:, 0]
        h = (t[0, 1] - t[0, 0])
        w = np.exp(-self.alpha * (t - t[:, :1]))
        sig = self.sigma(X)
        Ph, Ps = self.phi(X), self.psi(X)
        self.M = len(t)
        self.dsig = np.exp(-self.alpha * T)[:, None] * sig[:, -1] - sig[:, 0]     # (M, l1)
        self.Iq = _trapezoid(w, h, self.Q_fn(X)[..., None])[:, 0]                # (M,)
        self.Uphi = _zoh_trapezoid(w, h, U, Ph)                                   # (M, m, l2)
        self.PhiPhi = _trapezoid(w, h, Ph[..., :, None] * Ph[..., None, :])      # (M, l2, l2)
        self.Dpsi = _zoh_trapezoid(w, h, D, Ps)                                   # (M, q, l3)
        self.PsiPsi = _trapezoid(w, h, Ps[..., :, None] * Ps[..., None, :])      # (M, l3, l3)
        self.m, self.l2 = self.Uphi.shape[1:]
        self.q, self.l3 = self.Dpsi.shape[1:]
        self.l1 = self.dsig.shape[1]
        return self

    def regression(self, W_a, W_d, rows=slice(None)):
        """rho1 (M x (l1 + m l2 + q l3)) and rho2 (M,) of Eq. (60) for policies (W_a, W_d)."""
        R, g2 = self.R, self.gamma ** 2
        # int w (u - u_k) phi^T = Uphi - W_a^T PhiPhi ;  coefficient of vec(W_a): (R E)^T
        E_u = self.Uphi[rows] - np.einsum("lm,jlk->jmk", W_a, self.PhiPhi[rows])
        Cu = 2.0 * np.einsum("ab,jbk->jka", R, E_u)                 # (M, l2, m)
        E_d = self.Dpsi[rows] - np.einsum("lq,jlk->jqk", W_d, self.PsiPsi[rows])
        Cd = -2.0 * g2 * np.transpose(E_d, (0, 2, 1))               # (M, l3, q)
        Mj = len(E_u)
        rho1 = np.hstack([self.dsig[rows],
                          Cu.transpose(0, 2, 1).reshape(Mj, -1),     # column-major vec(W_a)
                          Cd.transpose(0, 2, 1).reshape(Mj, -1)])
        uRu = np.einsum("jkl,la,ab,kb->j", self.PhiPhi[rows], W_a, R, W_a)
        dd = np.einsum("jkl,la,ka->j", self.PsiPsi[rows], W_d, W_d)
        rho2 = -(self.Iq[rows] + uRu - g2 * dd)
        return rho1, rho2

    def unpack(self, W):
        l1, m, l2, q, l3 = self.l1, self.m, self.l2, self.q, self.l3
        W_c = W[:l1]
        W_a = W[l1:l1 + m * l2].reshape(m, l2).T                      # undo column-major vec
        W_d = W[l1 + m * l2:].reshape(q, l3).T
        return W_c, W_a, W_d

    def solve_ls(self, rho1, rho2, rank_tol=1e-10):
        """Least squares with column scaling (lstsq, not the normal equations of (61): same
        solution when rho1 has full column rank, without squaring the condition number)."""
        scale = np.linalg.norm(rho1, axis=0)
        scale[scale == 0] = 1.0
        A = rho1 / scale
        sv = np.linalg.svd(A, compute_uv=False)
        rank = int((sv > rank_tol * sv[0]).sum())
        cond = float(sv[0] / sv[-1]) if sv[-1] > 0 else np.inf
        W = np.linalg.lstsq(A, rho2, rcond=self.rcond)[0] / scale
        if self.rcond is not None:
            rank = int((sv > self.rcond * sv[0]).sum())
        return W, rank, cond

    def run(self, W_a0, W_d0, eps=1e-6, max_iter=50, allow_rank_deficient=False,
            validation_rows=None, relax=1.0):
        """Algorithm 2, phase 2: iterate until ||W^(k+1) - W^(k)|| <= eps max(1, ||W^(k)||)
        (stopping rule of Algorithms 1-2 with the inequality the right way round, item 7).
        `validation_rows`: intervals excluded from fitting and used to report a held-out
        Bellman residual. `relax` in (0, 1]: damped iteration
        W_(k+1) <- (1 - relax) W_k + relax W_LS (1.0 = Algorithm 2 as written)."""
        fit = slice(None)
        if validation_rows is not None:
            mask = np.ones(self.M, bool)
            mask[validation_rows] = False
            fit = np.nonzero(mask)[0]
        W_a, W_d = np.array(W_a0, float), np.array(W_d0, float)
        W_prev = None
        res = IRLResult(None, None, None, False)
        for k in range(max_iter):
            rho1, rho2 = self.regression(W_a, W_d, fit)
            W, rank, cond = self.solve_ls(rho1, rho2)
            res.rank, res.n_unknowns, res.cond = rank, rho1.shape[1], cond
            if rank < rho1.shape[1]:
                msg = (f"rho1 rank {rank} < {rho1.shape[1]} unknowns (cond {cond:.2e}): "
                       "insufficient excitation")
                if not allow_rank_deficient:
                    raise RankDeficientError(msg)
                warnings.warn(msg)
            if relax < 1.0 and W_prev is not None:
                W = (1.0 - relax) * W_prev + relax * W
            W_c, W_a_new, W_d_new = self.unpack(W)
            entry = dict(W_c=W_c, W_a=W_a_new, W_d=W_d_new, bellman=float(np.linalg.norm(rho1 @ W - rho2)),
                         norm_W=float(np.linalg.norm(W)), cond=cond, rank=rank)
            if validation_rows is not None:
                r1v, r2v = self.regression(W_a, W_d, validation_rows)
                entry["bellman_val"] = float(np.linalg.norm(r1v @ W - r2v) / np.sqrt(len(r2v)))
            dW = np.inf if W_prev is None else float(np.linalg.norm(W - W_prev))
            entry["dW"] = dW
            res.history.append(entry)
            W_a, W_d = W_a_new, W_d_new
            if W_prev is not None and dW <= eps * max(1.0, float(np.linalg.norm(W_prev))):
                res.converged = True
                W_prev = W
                break
            W_prev = W
        res.W_c, res.W_a, res.W_d = self.unpack(W_prev)
        return res
