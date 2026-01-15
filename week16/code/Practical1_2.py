import importlib
import importlib.util
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp


# Simulate dn/dt = r*n*(K-n) with r=1 while K steps from 3 to -3.
r = 1.0
Ks = np.linspace(3.0, -3.0, 200)
n0 = 0.1  # non-zero initial condition
t_span = (0.0, 50.0)
t_eval = np.linspace(t_span[0], t_span[1], 2000)


def logistic_rhs(t, n, r_value, k_value):
    return r_value * n * (k_value - n)


stable_eq = []
for k_val in Ks:
    sol = solve_ivp(logistic_rhs, t_span, [n0], t_eval=t_eval, args=(r, k_val), rtol=1e-8, atol=1e-10)
    n_end = sol.y[0, -1]
    stable_eq.append(n_end)
    n0 = max(n_end, 1e-8)

stable_eq = np.array(stable_eq)

results_dir = Path(__file__).resolve().parents[1] / "results"
results_dir.mkdir(parents=True, exist_ok=True)

csv_path = results_dir / "week16_logistic_equilibria.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("k,equilibrium\n")
    for k_val, eq in zip(Ks, stable_eq):
        f.write(f"{k_val:.4f},{eq:.6f}\n")

# Plot bifurcation diagram (equilibrium vs K) if matplotlib is available
if importlib.util.find_spec("matplotlib") is not None:
    matplotlib = importlib.import_module("matplotlib")
    matplotlib.use("Agg")
    plt = importlib.import_module("matplotlib.pyplot")

    plt.figure(figsize=(6, 4))
    plt.plot(Ks, stable_eq, marker=".", linestyle="none", markersize=2)
    plt.xlabel("K")
    plt.ylabel("Stable equilibrium n")
    plt.title("Logistic ODE: stable equilibrium vs K")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(results_dir / "week16_logistic_bifurcation.png", dpi=150)
