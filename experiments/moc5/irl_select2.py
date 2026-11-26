import sys, numpy as np, time
exec(open("experiments/moc5/irl_select.py").read().split("for seed in (0, 2, 3, 4):")[0])
print("J(behaviour P part W0) =", f"{val_cost(W0):.3g}")
for seed in (0, 4):
    t0 = time.time(); W = {}; info = []
    for i in (3, 4):
        parts = []
        for batch in range(3):
            mk = lambda s, i=i, b=batch: SumOfSines(3, [600., 180., 18.], n_sines=20, w_min=0.05, w_max=20.0, seed=10000 * seed + 1000 * i + 100 * b + s)
            parts.append(collect_episodes(grid, 5.0, mk, Kb, Ki, [2, 2, 0.3, 1, 0.5, 0.3], seed=10000 * seed + 100 * i + 37 * batch))
            data = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
            irl = OffPolicyHinf(QuadraticBasis(idx), phi, LinearBasis(idx), Qf, R, 5.0, 0.1).precompute(data)
            res = irl.run(W0, np.zeros((9, 3)), eps=1e-5, max_iter=40, allow_rank_deficient=True)
            Js = [val_cost(h["W_a"]) for h in res.history]; k = int(np.argmin(Js))
            if Js[k] < val_cost(W0):
                break
        W[i] = res.history[k]["W_a"]
        info.append(f"SV{i}: batches {batch+1}, pick it {k+1} J={Js[k]:.3g} diag{np.diag(W[i][3:6]).round(0).tolist()}")
    try:
        L = run_closed_loop(cfg, IRLController(W, phi), t_end=40.0, log_every=100)
        F = L["formation"]; t = L["t"]; e = np.array([bearing_error(p, F.bearings) for p in L["p"]]); kk = t > 30
        out = f"OK RMSE {rmse(t, e):.4f} |z_ups|t>30 {np.abs(L['z_ups'][kk]).mean((0,1)).round(3).tolist()} max|tau| {np.abs(L['tau']).max():.0f}"
    except FloatingPointError as ex:
        out = f"DIVERGED {ex}"
    print(f"seed {seed}: {' | '.join(info)} -> {out} [{time.time()-t0:.0f}s]", flush=True)
