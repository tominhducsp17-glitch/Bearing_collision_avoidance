"""Single vessel, exogenous excited reference: does off-policy IRL approach the oracle?"""
import sys, numpy as np
sys.path.insert(0, "/home/d/projects/Paper_1"); sys.path.insert(0, "/home/d/projects/Paper_1/scripts")
from irl_reference import linear_model
from src.analysis.hinf_reference import game_are, gains
from src.models.vessel import vessel_rhs, Disturbance
from src.sim.integrators import rk4_step
from src.high_level.followers import rot2, virtual_vessel_rhs
from src.low_level.augmented_state import build_X, BASIS, Q_prime_fn
from src.low_level.basis import QuadraticBasis, LinearBasis
from src.low_level.offpolicy_irl import OffPolicyHinf
from src.low_level.data_collection import SumOfSines
np.set_printoptions(precision=1, suppress=True, linewidth=150)
tn = np.array([1100., 300., 30.]); R = np.diag(1 / tn ** 2)
A, B, E, u0v = linear_model(); Q = np.diag([100.] * 6 + [0.] * 3)
P = game_are(A, B, E, Q, R, 5.0, 0.1); K, Lg = gains(P, B, E, R, 5.0); Wref = -K.T
u0 = u0v[0]; psi0 = np.pi / 4
def ref(t, a):   # theta_d, omega_d and their derivatives (exogenous reference)
    th = np.array([u0 + a[0] * np.sin(0.7 * t) + a[0] * 0.5 * np.sin(2.3 * t), a[1] * np.sin(1.1 * t)])
    thd = np.array([a[0] * 0.7 * np.cos(0.7 * t) + a[0] * 0.5 * 2.3 * np.cos(2.3 * t), a[1] * 1.1 * np.cos(1.1 * t)])
    om, omd = a[2] * np.sin(0.9 * t), a[2] * 0.9 * np.cos(0.9 * t)
    return th, om, thd, omd
PLANT = [vessel_rhs]
def simulate(policy, t_end, a, dt=1e-3, seed=0, record=False, x_err0=np.zeros(6)):
    dist = Disturbance(t_end, dt, seed)
    th, om, _, _ = ref(0, a)
    xd = np.r_[0, 0, psi0, th]
    xs = np.r_[xd[:3] + x_err0[:3], np.r_[th, om] + x_err0[3:]]
    rec = {"t": [], "X": [], "U": [], "D": []}
    for k in range(int(t_end / dt)):
        t = k * dt
        th, om, thd, omd = ref(t, a)
        eta_d, ups_d, ups_dd = xd[:3], np.r_[xd[3:5], om], np.r_[thd, omd]
        X = build_X(xs[:3], xs[3:], eta_d, ups_d, ups_dd, 2.0)
        tau = policy(t, X); d = dist(t)
        if record:
            rec["t"].append(t); rec["X"].append(X); rec["U"].append(tau); rec["D"].append(d)
        def f(tt, xx):
            th_, om_, thd_, omd_ = ref(tt, a)
            return np.r_[PLANT[0](xx[:6], tau, d), np.r_[rot2(xx[8]) @ xx[9:11], om_, thd_]]
        xx = rk4_step(f, t, np.r_[xs, xd], dt); xs, xd = xx[:6], xx[6:]
        if not np.all(np.isfinite(xx)) or np.abs(xx).max() > 1e6: return None, k * dt
    return {k_: np.array(v) for k_, v in rec.items()}, xs
def dataset(rec):
    pair = lambda Y: np.stack([Y[:-1], Y[1:]], axis=1)
    U, D = pair(rec["U"]), pair(rec["D"]); U[:, 1] = U[:, 0]; D[:, 1] = D[:, 0]
    return {"t": pair(rec["t"]), "X": pair(rec["X"]), "U": U, "D": D}
Kb = np.array([2000., 2000., 200.]); idx = BASIS["main"]; phi = LinearBasis(idx)
if __name__ == '__main__':
 for a in ((0.0, 0.0, 0.0), (0.5, 0.5, 0.2), (1.0, 1.0, 0.5)):
     for ampf in (1.0, 3.0):
         e = SumOfSines(3, ampf * np.array([200., 60., 6.]), seed=3)
         rec, _ = simulate(lambda t, X: -Kb * X[3:6] + e(t), 20.0, a, record=True)
         irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Q_prime_fn(), R, 5.0, 0.1).precompute(dataset(rec))
         res = irl.run(np.zeros((9, 3)), np.zeros((9, 3)), eps=1e-6, max_iter=60, allow_rank_deficient=True)
         ez = np.abs(res.W_a[:6] - Wref[:6]).max() / np.abs(Wref[:6]).max()
         eu = np.abs(res.W_a[6:] - Wref[6:]).max() / np.abs(Wref[6:]).max()
         r2, xs = simulate(lambda t, X: res.W_a.T @ phi(X), 20.0, (0.5, 0.5, 0.2), seed=1, record=True)
         dep = "DIVERGED at %.2f" % xs if r2 is None else "|z| last 5s = %s" % np.abs(r2["X"][-5000:, :6]).mean(0).round(3)
         print(f"ref excitation a={a} amp×{ampf}: rank {res.rank} cond {res.cond:.0e} it {len(res.history)} conv {res.converged} errZ {ez:.3f} errUpsd {eu:.3f} -> deploy {dep}")
         if a == (0.5, 0.5, 0.2) and ampf == 1.0:
             print(" learned z_ups rows\n", res.W_a[3:6], "\n ref\n", Wref[3:6], "\n learned z_eta rows\n", res.W_a[:3], "\n ref\n", Wref[:3], "\n learned ups rows\n", res.W_a[6:], "\n ref\n", Wref[6:])
 r_or, _ = simulate(lambda t, X: Wref.T @ phi(X), 20.0, (0.5, 0.5, 0.2), seed=1, record=True)
 print("oracle deploy |z| last 5s", np.abs(r_or["X"][-5000:, :6]).mean(0).round(3))
