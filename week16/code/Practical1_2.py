import importlib
import importlib.util
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root
import matplotlib.pyplot as plt

#1
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



plt.figure(figsize=(6, 4))
plt.plot(Ks, stable_eq, marker=".", linestyle="none", markersize=2)
plt.xlabel("K")
plt.ylabel("Stable equilibrium n")
plt.title("Logistic ODE: stable equilibrium vs K")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(results_dir / "week16_logistic_bifurcation.png", dpi=150)

#2
def equilibrium_root(K, guess, r=1.0):
    f = lambda n: r*n*(K - n)
    sol = root(lambda x: f(x[0]), x0=np.array([guess]))
    return sol.x[0], sol.success

Ks2 = np.linspace(3, -3, 200)

# Track n=K branch
eq_K = []
guess = 3.0
for K in Ks2:
    val, ok = equilibrium_root(K, guess, r=r)
    eq_K.append(val if ok else np.nan)
    guess = val

# Track n=0 branch
eq_0 = []
guess = 1e-6
for K in Ks2:
    val, ok = equilibrium_root(K, guess, r=r)
    eq_0.append(val if ok else np.nan)
    guess = val

eq_K = np.array(eq_K)
eq_0 = np.array(eq_0)

# Stability by linearization: f'(n)=r(K-2n)
def stability(K, n, r=1.0):
    fp = r*(K - 2*n)
    return fp < 0  # stable if derivative negative

stable_K = np.array([stability(K, n, r=r) for K, n in zip(Ks2, eq_K)])
stable_0 = np.array([stability(K, n, r=r) for K, n in zip(Ks2, eq_0)])

plt.figure()
# plot branches with stability styling
plt.plot(Ks2[stable_0], eq_0[stable_0], 'b.', markersize=3, label=r'$n^*=0$ (stable)')
plt.plot(Ks2[~stable_0], eq_0[~stable_0], 'r.', markersize=3, label=r'$n^*=0$ (unstable)')
plt.plot(Ks2[stable_K], eq_K[stable_K], 'b.', markersize=3, label=r'$n^*=K$ (stable)')
plt.plot(Ks2[~stable_K], eq_K[~stable_K], 'r.', markersize=3, label=r'$n^*=K$ (unstable)')
plt.axhline(0, linewidth=1)
plt.xlabel(r'$K$')
plt.ylabel(r'Equilibrium $n^*$')
plt.title("(1-2b,c) Logistic bifurcation diagram with stability (blue=stable, red=unstable)")
plt.legend()
plt.show()