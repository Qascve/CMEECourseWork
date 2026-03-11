#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lmfit import Parameters, minimize


def find_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".gitignore").exists():
            return candidate
    raise FileNotFoundError("Could not find project root via .gitignore")


root_path = find_root(Path(__file__))
data_path = Path("MiniProject") / "data" / "tetraselmis_tetrahele_log.csv"
data_path = root_path / data_path
result_dir = root_path / "MiniProject" / "result" / "three_phase_linear_fit"

three_phase_fixed_start_count = 16

print(f"root path: {root_path}")
print(f"data path: {data_path}")
print(f"result dir: {result_dir}")


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_cols = ["Time", "log_PopBio", "Species", "Medium", "Temp"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def filter_tetraselmis_esaw(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        (df["Species"] == "Tetraselmis tetrahele") & (df["Medium"] == "ESAW")
    ].copy()


def summarize_temp_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Species", "Medium", "Temp"], as_index=False)
        .agg(n_rows=("Temp", "size"))
        .sort_values(by=["Temp"], ascending=[True])
        .reset_index(drop=True)
    )


def get_temp_color(temp: float) -> str:
    color_map = {8.0: "tab:blue", 16.0: "tab:orange", 25.0: "tab:green"}
    return color_map.get(float(temp), "tab:gray")


def prepare_logged_temp_data(temp_df: pd.DataFrame) -> pd.DataFrame:
    return (
        temp_df[["Time", "log_PopBio", "Temp"]]
        .dropna()
        .sort_values(by="Time")
        .reset_index(drop=True)
    )


def unpack_theta(theta: np.ndarray) -> tuple[float, float, float, float]:
    n0 = float(theta[0])
    delta_n = float(np.exp(np.clip(theta[1], -20, 20)))
    t_lag = float(theta[2])
    delta_t = float(np.exp(np.clip(theta[3], -20, 20)))
    n_max = n0 + delta_n
    t_max = t_lag + delta_t
    return n0, n_max, t_lag, t_max


def three_phase_linear(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    n0, n_max, t_lag, t_max = unpack_theta(theta)
    duration = max(t_max - t_lag, 1e-12)
    mu = (n_max - n0) / duration
    growth = n0 + mu * (t - t_lag)
    return np.where(t <= t_lag, n0, np.where(t >= t_max, n_max, growth))


def residuals(theta: np.ndarray, t: np.ndarray, y: np.ndarray) -> np.ndarray:
    return y - three_phase_linear(t, theta)


def residuals_lmfit(params: Parameters, t: np.ndarray, y: np.ndarray) -> np.ndarray:
    theta = np.array(
        [
            params["theta_n0"].value,
            params["theta_log_delta_n"].value,
            params["theta_t_lag"].value,
            params["theta_log_delta_t"].value,
        ],
        dtype=float,
    )
    return residuals(theta, t, y)


def initial_theta(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    y_min = float(np.min(y))
    y_max = float(np.max(y))
    y_range = max(y_max - y_min, 0.25)

    low_threshold = y_min + 0.1 * y_range
    high_threshold = y_min + 0.9 * y_range

    first_growth_idx = int(np.argmax(y >= low_threshold))
    first_plateau_idx = int(np.argmax(y >= high_threshold))

    if not np.any(y >= low_threshold):
        first_growth_idx = 0
    if not np.any(y >= high_threshold):
        first_plateau_idx = len(t) - 1

    t_lag_guess = float(t[first_growth_idx])
    t_max_guess = float(t[first_plateau_idx])
    if t_max_guess <= t_lag_guess:
        t_max_guess = float(t_lag_guess + max(np.ptp(t) * 0.25, 1.0))

    delta_n_guess = max(y_max - y_min, 0.2)
    delta_t_guess = max(t_max_guess - t_lag_guess, 1.0)

    return np.array(
        [y_min, np.log(delta_n_guess), t_lag_guess, np.log(delta_t_guess)],
        dtype=float,
    )


def build_fixed_initial_thetas(t: np.ndarray, y: np.ndarray) -> list[np.ndarray]:
    base_theta = initial_theta(t, y)
    base_n0 = float(base_theta[0])
    base_delta_n = float(np.exp(base_theta[1]))
    base_t_lag = float(base_theta[2])
    base_delta_t = float(np.exp(base_theta[3]))
    time_span = max(float(np.ptp(t)), 1.0)

    fixed_start_specs = [
        (-0.20, 0.70, -0.15 * time_span, 0.70),
        (-0.20, 0.70, 0.00 * time_span, 1.00),
        (-0.20, 1.00, 0.10 * time_span, 1.40),
        (-0.20, 1.30, 0.20 * time_span, 1.80),
        (0.00, 0.70, -0.15 * time_span, 1.00),
        (0.00, 1.00, 0.00 * time_span, 0.70),
        (0.00, 1.00, 0.00 * time_span, 1.00),
        (0.00, 1.00, 0.10 * time_span, 1.40),
        (0.00, 1.30, 0.20 * time_span, 1.80),
        (0.15, 0.70, -0.10 * time_span, 1.40),
        (0.15, 1.00, 0.00 * time_span, 1.40),
        (0.15, 1.30, 0.10 * time_span, 0.70),
        (0.15, 1.30, 0.20 * time_span, 1.00),
        (0.30, 0.70, -0.05 * time_span, 1.80),
        (0.30, 1.00, 0.10 * time_span, 0.70),
        (0.30, 1.30, 0.20 * time_span, 1.80),
    ]

    theta_candidates = []
    for n0_shift, delta_n_scale, t_lag_shift, delta_t_scale in fixed_start_specs:
        n0_0 = base_n0 + n0_shift
        delta_n_0 = max(base_delta_n * delta_n_scale, 1e-8)
        t_lag_0 = base_t_lag + t_lag_shift
        delta_t_0 = max(base_delta_t * delta_t_scale, 1.0)
        theta_candidates.append(
            np.array(
                [n0_0, np.log(delta_n_0), t_lag_0, np.log(delta_t_0)],
                dtype=float,
            )
        )

    return theta_candidates


def compute_fit_metrics(y: np.ndarray, y_hat: np.ndarray) -> dict:
    resid = y - y_hat
    rss = float(np.nansum(resid**2))
    n = len(y)
    k = 4
    tss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else np.nan
    rmse = float(np.sqrt(rss / n))
    mae = float(np.mean(np.abs(resid)))
    rss_safe = max(rss, 1e-12)
    loglik = -0.5 * n * (np.log(2 * np.pi) + 1 + np.log(rss_safe / n))
    aic = 2 * k - 2 * loglik
    bic = np.log(n) * k - 2 * loglik
    return {
        "RSS": rss,
        "R2": float(r2),
        "RMSE": rmse,
        "MAE": mae,
        "AIC": float(aic),
        "BIC": float(bic),
    }


def fit_with_fixed_starts(t: np.ndarray, y: np.ndarray) -> tuple:
    theta_candidates = build_fixed_initial_thetas(t, y)
    time_span = max(float(np.ptp(t)), 1.0)

    best_fit = None
    best_theta = None
    best_metrics = None
    n_successful = 0

    for theta0 in theta_candidates:
        try:
            params = Parameters()
            params.add("theta_n0", value=float(theta0[0]), min=-20, max=20)
            params.add("theta_log_delta_n", value=float(theta0[1]), min=-20, max=20)
            params.add(
                "theta_t_lag",
                value=float(theta0[2]),
                min=float(np.min(t) - time_span),
                max=float(np.max(t) + time_span),
            )
            params.add("theta_log_delta_t", value=float(theta0[3]), min=-20, max=20)

            fit = minimize(
                residuals_lmfit,
                params,
                args=(t, y),
                method="leastsq",
                max_nfev=5000,
                nan_policy="omit",
            )

            theta_hat = np.array(
                [
                    fit.params["theta_n0"].value,
                    fit.params["theta_log_delta_n"].value,
                    fit.params["theta_t_lag"].value,
                    fit.params["theta_log_delta_t"].value,
                ],
                dtype=float,
            )
            y_hat = three_phase_linear(t, theta_hat)
            fit_metrics = compute_fit_metrics(y, y_hat)
            if not np.isfinite(fit_metrics["RSS"]):
                continue

            n_successful += 1
            if (
                best_metrics is None
                or fit_metrics["AIC"] < best_metrics["AIC"]
                or (
                    np.isclose(fit_metrics["AIC"], best_metrics["AIC"])
                    and fit_metrics["RSS"] < best_metrics["RSS"]
                )
            ):
                best_fit = fit
                best_theta = theta_hat
                best_metrics = fit_metrics
        except Exception:
            # Skip failed starts and continue looking for a usable solution.
            continue

    if best_fit is None or best_theta is None or best_metrics is None:
        raise RuntimeError("All multi-start three-phase linear fits failed.")

    return best_fit, best_theta, best_metrics, n_successful


def fit_single_temperature(temp_df: pd.DataFrame) -> dict:
    logged_df = prepare_logged_temp_data(temp_df)

    t = logged_df["Time"].to_numpy(dtype=float)
    y = logged_df["log_PopBio"].to_numpy(dtype=float)
    t_raw = logged_df["Time"].to_numpy(dtype=float)
    y_raw = logged_df["log_PopBio"].to_numpy(dtype=float)

    if len(y) < 4:
        raise ValueError(
            f"Not enough samples in logged dataset at Temp={temp_df['Temp'].iloc[0]}: "
            f"need >= 4, got {len(y)}"
        )

    fit, theta_hat, fit_metrics, n_successful = fit_with_fixed_starts(t, y)

    y_hat = three_phase_linear(t, theta_hat)
    t_grid = np.linspace(float(np.min(t_raw)), float(np.max(t_raw)), 400)
    y_hat_grid = three_phase_linear(t_grid, theta_hat)

    n0, n_max, t_lag, t_max = unpack_theta(theta_hat)
    mu = (n_max - n0) / max(t_max - t_lag, 1e-12)

    return {
        "temp": float(temp_df["Temp"].iloc[0]),
        "n_rows_raw": int(len(logged_df)),
        "n_rows": int(len(y)),
        "n_rows_removed_after_log_filter": 0,
        "selection_metric": "AIC",
        "n_starts": int(three_phase_fixed_start_count),
        "n_successful_starts": int(n_successful),
        "N0": float(n0),
        "NMAX": float(n_max),
        "tLAG": float(t_lag),
        "tMAX": float(t_max),
        "mu": float(mu),
        "RSS": float(fit_metrics["RSS"]),
        "R2": float(fit_metrics["R2"]),
        "RMSE": float(fit_metrics["RMSE"]),
        "MAE": float(fit_metrics["MAE"]),
        "AIC": float(fit_metrics["AIC"]),
        "BIC": float(fit_metrics["BIC"]),
        "success": bool(fit.success),
        "message": str(fit.message),
        "t": t,
        "y": y,
        "t_raw": t_raw,
        "y_raw": y_raw,
        "t_grid": t_grid,
        "y_hat": y_hat,
        "y_hat_grid": y_hat_grid,
    }


def save_fit_plot(fit_result: dict, out_dir: Path) -> None:
    temp = fit_result["temp"]
    t_raw = fit_result["t_raw"]
    y_raw = fit_result["y_raw"]
    t_grid = fit_result["t_grid"]
    y_hat_grid = fit_result["y_hat_grid"]
    color = get_temp_color(temp)

    plt.figure(figsize=(7, 4.5))
    plt.scatter(t_raw, y_raw, s=18, alpha=0.55, color=color, label="Observed data")
    plt.plot(t_grid, y_hat_grid, linewidth=2.0, color=color, label="Fit line")
    plt.title(f"Three-phase linear model fit at {temp:g} °C")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Population abundance(N)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(out_dir / f"three_phase_fit_temp{int(temp)}.svg")
    plt.close()


def save_combined_temperature_plot(fit_results: list, out_dir: Path) -> Path:
    plt.figure(figsize=(8, 5))
    for fit_result in fit_results:
        temp = fit_result["temp"]
        t_raw = fit_result["t_raw"]
        y_raw = fit_result["y_raw"]
        t_grid = fit_result["t_grid"]
        y_hat_grid = fit_result["y_hat_grid"]
        color = get_temp_color(temp)
        plt.scatter(
            t_raw,
            y_raw,
            s=10,
            alpha=0.25,
            color=color,
            label=f"Observed data ({temp:g} °C)",
        )
        plt.plot(
            t_grid,
            y_hat_grid,
            linewidth=2.0,
            color=color,
            label=f"Fit line ({temp:g} °C)",
        )

    plt.title("Three-phase linear model fits across temperatures")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Population abundance(N)")
    plt.legend(fontsize=8, ncol=2, loc="lower right")
    plt.tight_layout()
    out_path = out_dir / "three_phase_fit_all_temps.svg"
    plt.savefig(out_path)
    plt.close()
    return out_path


def fit_all_temperatures(subset: pd.DataFrame, out_dir: Path) -> tuple[pd.DataFrame, list]:
    out_dir.mkdir(parents=True, exist_ok=True)
    fit_rows = []
    fit_results = []

    for temp in sorted(subset["Temp"].unique().tolist()):
        temp_df = subset[subset["Temp"] == temp].copy()
        fit_result = fit_single_temperature(temp_df)
        save_fit_plot(fit_result, out_dir)
        fit_results.append(fit_result)
        fit_rows.append(
            {
                "Temp": fit_result["temp"],
                "n_rows_raw": fit_result["n_rows_raw"],
                "n_rows": fit_result["n_rows"],
                "n_rows_removed_after_log_filter": fit_result[
                    "n_rows_removed_after_log_filter"
                ],
                "selection_metric": fit_result["selection_metric"],
                "n_starts": fit_result["n_starts"],
                "n_successful_starts": fit_result["n_successful_starts"],
                "N0": fit_result["N0"],
                "NMAX": fit_result["NMAX"],
                "tLAG": fit_result["tLAG"],
                "tMAX": fit_result["tMAX"],
                "mu": fit_result["mu"],
                "RSS": fit_result["RSS"],
                "R2": fit_result["R2"],
                "RMSE": fit_result["RMSE"],
                "MAE": fit_result["MAE"],
                "AIC": fit_result["AIC"],
                "BIC": fit_result["BIC"],
                "success": fit_result["success"],
                "message": fit_result["message"],
            }
        )

    fit_table = pd.DataFrame(fit_rows).sort_values(by="Temp").reset_index(drop=True)
    return fit_table, fit_results


def print_fit_summary(fit_table: pd.DataFrame) -> None:
    print("\nTemperature-wise three-phase linear fit summary on ln(PopBio):")
    for _, row in fit_table.iterrows():
        print(
            f"Temp={row['Temp']:g} | n_rows_raw={int(row['n_rows_raw'])} | "
            f"n_rows_used={int(row['n_rows'])} | removed={int(row['n_rows_removed_after_log_filter'])} | "
            f"select_by={row['selection_metric']} | starts={int(row['n_starts'])} | "
            f"start_success={int(row['n_successful_starts'])} | "
            f"N0={row['N0']:.4f} | NMAX={row['NMAX']:.4f} | "
            f"tLAG={row['tLAG']:.4f} | tMAX={row['tMAX']:.4f} | mu={row['mu']:.4f} | "
            f"R2={row['R2']:.4f} | RMSE={row['RMSE']:.4f} | MAE={row['MAE']:.4f} | "
            f"AIC={row['AIC']:.2f} | BIC={row['BIC']:.2f} | success={row['success']}"
        )


def main() -> None:
    df = load_data(data_path)
    subset = filter_tetraselmis_esaw(df)
    summary = summarize_temp_counts(subset)

    print(f"Dataset: {data_path}")
    print("Tetraselmis tetrahele | ESAW | Temp + n_rows summary:")
    for idx, row in summary.iterrows():
        print(
            f"{idx + 1}. Species={row['Species']} | Medium={row['Medium']} | "
            f"Temp={row['Temp']:g} | n_rows={row['n_rows']}"
        )

    fit_table, fit_results = fit_all_temperatures(subset, result_dir)
    combined_plot_path = save_combined_temperature_plot(fit_results, result_dir)
    fit_table.to_csv(result_dir / "fit_metrics_by_temp.csv", index=False)
    print_fit_summary(fit_table)
    print(f"\nSaved metrics: {result_dir / 'fit_metrics_by_temp.csv'}")
    print(f"Saved plots to: {result_dir}")
    print(f"Saved combined plot: {combined_plot_path}")


if __name__ == "__main__":
    main()
