"""Centralised CBF-QP safety filter on the virtual-vessel accelerations Pi (Mốc 7).

    Pi* = argmin sum_i ||Pi_i - Pi_nom,i||^2
          s.t.  HOCBF (*) of src/safety/cbf.py for every pair follower-follower and
                leader-follower (leaders are kinematic, not filtered: the follower takes
                the whole responsibility and the leader acceleration is known from Eq. (9)),
                ||Pi_i|| <= a_max as a 16-gon CIRCUMSCRIBING the disc (so a saturated Pi_nom
                stays feasible and is returned unchanged when no CBF is violated; the bound
                is then exceeded by at most 1/cos(pi/16) - 1 = 2 %).
Fast path: if Pi_nom satisfies every constraint it is the optimum and no QP is solved.
Infeasible QP: one shared slack s >= 0 on the CBF rows only (acceleration bound kept hard),
heavy penalty; the step is COUNTED as infeasible (an index of the paper, PLAN_phase2 §2).
Solver: quadprog (dense Goldfarb-Idnani active set; exact, a few variables).
"""
import numpy as np
import quadprog

from src.safety.cbf import pair_constraint


class CBFFilter:
    def __init__(self, d_min, eps, a1=1.0, a2=2.0, a_max=None, n_poly=16, rho=1e8):
        """eps: dict {follower id: tracking radius} or a float (same for all followers)."""
        self.d_min, self.eps, self.a1, self.a2 = d_min, eps, a1, a2
        self.a_max, self.rho = a_max, rho
        th = 2 * np.pi * np.arange(n_poly) / n_poly
        self.N = np.c_[np.cos(th), np.sin(th)]                 # outward normals of the polygon
        self.r_poly = None if a_max is None else a_max / np.cos(np.pi / n_poly)
        self.stats = {"steps": 0, "qp_solved": 0, "infeasible": 0}

    def _eps(self, i):
        return self.eps.get(i, 0.0) if isinstance(self.eps, dict) else self.eps

    def filter(self, Pi_nom, virtual_states, env, t, others=None):
        """virtual_states: {follower id: (p (2,), v (2,))} earth frame.
        others: {leader id: (p, v, a)} kinematic agents that are not decision variables."""
        fol = list(Pi_nom)
        nf = len(fol)
        x0 = np.concatenate([Pi_nom[i] for i in fol])
        rows, rhs, hs, psis = [], [], [], []
        for a, i in enumerate(fol):
            pi, vi = virtual_states[i]
            for b in range(a + 1, nf):                         # follower-follower
                j = fol[b]
                pj, vj = virtual_states[j]
                g, bb, h, ps = pair_constraint(pi - pj, vi - vj, self.d_min + self._eps(i) + self._eps(j),
                                               self.a1, self.a2)
                r = np.zeros(2 * nf)
                r[2 * a:2 * a + 2], r[2 * b:2 * b + 2] = g, -g
                rows.append(r), rhs.append(bb), hs.append(h), psis.append(ps)
            for j, (pj, vj, aj) in (others or {}).items():      # leader-follower
                g, bb, h, ps = pair_constraint(pi - pj, vi - vj, self.d_min + self._eps(i), self.a1, self.a2)
                r = np.zeros(2 * nf)
                r[2 * a:2 * a + 2] = g
                rows.append(r), rhs.append(bb + g @ aj), hs.append(h), psis.append(ps)
        A_cbf, b_cbf = np.array(rows).reshape(-1, 2 * nf), np.array(rhs)
        A_acc, b_acc = self._accel_rows(nf)
        self.stats["steps"] += 1
        info = {"h_min": min(hs) if hs else np.inf, "psi1_min": min(psis) if psis else np.inf,
                "active": 0, "infeasible": False, "qp": False}
        viol = A_cbf @ x0 - b_cbf
        if np.all(viol >= -1e-9) and (A_acc is None or np.all(A_acc @ x0 - b_acc >= -1e-9)):
            return dict(Pi_nom), info
        self.stats["qp_solved"] += 1
        info["qp"] = True
        A = A_cbf if A_acc is None else np.vstack([A_cbf, A_acc])
        b = b_cbf if A_acc is None else np.r_[b_cbf, b_acc]
        try:
            x = quadprog.solve_qp(np.eye(2 * nf), x0, A.T, b)[0]
        except ValueError:                                     # inconsistent constraints
            self.stats["infeasible"] += 1
            info["infeasible"] = True
            x = self._solve_slack(x0, A_cbf, b_cbf, A_acc, b_acc)
        info["active"] = int(np.sum(np.abs(A_cbf @ x - b_cbf) < 1e-6))
        return {i: x[2 * a:2 * a + 2].copy() for a, i in enumerate(fol)}, info

    def _accel_rows(self, nf):
        if self.a_max is None:
            return None, None
        A = np.zeros((len(self.N) * nf, 2 * nf))
        for a in range(nf):
            A[a * len(self.N):(a + 1) * len(self.N), 2 * a:2 * a + 2] = -self.N   # -n^T Pi >= -r
        return A, -self.r_poly * np.ones(len(self.N) * nf)

    def _solve_slack(self, x0, A_cbf, b_cbf, A_acc, b_acc):
        n = len(x0)
        G = np.diag(np.r_[np.ones(n), self.rho])
        a = np.r_[x0, 0.0]
        A = [np.c_[A_cbf, np.ones(len(b_cbf))], np.r_[np.zeros(n), 1.0][None]]
        b = [b_cbf, [0.0]]
        if A_acc is not None:
            A.append(np.c_[A_acc, np.zeros(len(b_acc))])
            b.append(b_acc)
        return quadprog.solve_qp(G, a, np.vstack(A).T, np.concatenate(b))[0][:n]
