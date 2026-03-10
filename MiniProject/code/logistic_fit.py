#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
result_dir = root_path / "MiniProject" / "result" / "logistic_fit"
logistic_fixed_start_count = 12

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
    subset = df[
        (df["Species"] == "Tetraselmis tetrahele") & (df["Medium"] == "ESAW")
    ].copy()
    return subset


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


def logistic_3p(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    # theta is in log-space so parameters remain positive after exp.
    k, r, n0 = np.exp(np.clip(theta, -20, 20))
    exp_arg = np.clip(-r * t, -700, 700)
    with np.errstate(over="ignore", invalid="ignore"):
        denom = 1.0 + ((k - n0) / n0) * np.exp(exp_arg)
    denom = np.where(np.isfinite(denom), denom, 1e12)
    denom = np.where(np.abs(denom) < 1e-12, 1e-12, denom)
    return k / denom


def residuals(theta: np.ndarray, t: np.ndarray, y_log: np.ndarray) -> np.ndarray:
    y_pred = logistic_3p(t, theta)
    y_pred_safe = np.clip(y_pred, 1e-12, None)
    y_pred_log = np.log(y_pred_safe)
    return y_log - y_pred_log


def residuals_lmfit(params: Parameters, t: np.ndarray, y_log: np.ndarray) -> np.ndarray:
    theta = np.array(
        [
            params["theta_k"].value,
            params["theta_r"].value,
            params["theta_n0"].value,
        ],
        dtype=float,
    )
    return residuals(theta, t, y_log)


def initial_theta(t: np.ndarray, y_log: np.ndarray) -> np.ndarray:
    y_pos = np.clip(np.exp(y_log), 1e-8, None)
    n0_guess = float(np.percentile(y_pos, 5))
    k_guess = float(np.percentile(y_pos, 95))
    if k_guess <= n0_guess:
        k_guess = float(y_pos.max() * 1.2)
    r_guess = 0.1
    return np.log([k_guess, r_guess, n0_guess])


def build_fixed_initial_thetas(t: np.ndarray, y_log: np.ndarray) -> list[np.ndarray]:
    base_k, base_r, base_n0 = np.exp(initial_theta(t, y_log))
    fixed_start_specs = [
        (0.85, 0.30, 0.70),
        (0.85, 1.00, 1.00),
        (0.85, 2.50, 1.35),
        (1.00, 0.30, 0.70),
        (1.00, 0.60, 0.90),
        (1.00, 1.00, 1.00),
        (1.00, 1.80, 1.20),
        (1.00, 2.50, 1.35),
        (1.20, 0.30, 0.70),
        (1.20, 1.00, 1.00),
        (1.20, 1.80, 1.20),
        (1.40, 2.50, 1.35),
    ]

    theta_candidates = []
    for k_scale, r_scale, n0_scale in fixed_start_specs:
        k0 = max(base_k * k_scale, 1e-8)
        r0 = max(base_r * r_scale, 1e-8)
        n00 = max(base_n0 * n0_scale, 1e-8)
        if k0 <= n00:
            k0 = max(n00 * 1.2, 1e-8)
        theta_candidates.append(np.log([k0, r0, n00]))

    return theta_candidates


def prepare_logged_temp_data(temp_df: pd.DataFrame) -> pd.DataFrame:
    return (
        temp_df[["Time", "log_PopBio", "Temp"]]
        .dropna()
        .sort_values(by="Time")
        .reset_index(drop=True)
    )


def compute_fit_metrics(y_log: np.ndarray, y_hat_log: np.ndarray) -> dict:
    resid = y_log - y_hat_log
    rss = float(np.nansum(resid**2))
    n = len(y_log)
    k = 3
    tss = float(np.sum((y_log - np.mean(y_log)) ** 2))
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


def is_better_candidate(candidate: dict, current_best: dict | None) -> bool:
    if current_best is None:
        return True

    candidate_value = candidate["AIC"]
    best_value = current_best["AIC"]
    if not np.isfinite(candidate_value):
        return False
    if not np.isfinite(best_value):
        return True

    if candidate_value < best_value:
        return True
    if candidate_value > best_value:
        return False

    return candidate["RSS"] < current_best["RSS"]


def fit_with_fixed_starts(t: np.ndarray, y_log: np.ndarray) -> tuple:
    theta_candidates = build_fixed_initial_thetas(t, y_log)
    best_record = None
    n_successful = 0

    for theta0 in theta_candidates:
        try:
            params = Parameters()
            params.add("theta_k", value=float(theta0[0]), min=-20, max=20)
            params.add("theta_r", value=float(theta0[1]), min=-20, max=20)
            params.add("theta_n0", value=float(theta0[2]), min=-20, max=20)
            fit = minimize(
                residuals_lmfit,
                params,
                args=(t, y_log),
                method="leastsq",
                max_nfev=5000,
                nan_policy="omit",
            )
            theta_hat = np.array(
                [
                    fit.params["theta_k"].value,
                    fit.params["theta_r"].value,
                    fit.params["theta_n0"].value,
                ],
                dtype=float,
            )
            y_hat = logistic_3p(t, theta_hat)
            y_hat_log = np.log(np.clip(y_hat, 1e-12, None))
            fit_metrics = compute_fit_metrics(y_log, y_hat_log)
            if not np.isfinite(fit_metrics["RSS"]):
                continue
            record = {
                "success": bool(fit.success),
                "message": str(fit.message),
                "fit": fit,
                "y_hat_log": y_hat_log,
                **fit_metrics,
            }
            n_successful += 1
            if is_better_candidate(record, best_record):
                best_record = record
        except Exception:
            continue

    if best_record is None:
        raise RuntimeError("All multi-start LM fits failed.")

    return best_record, n_successful


def fit_single_temperature(temp_df: pd.DataFrame) -> dict:
    logged_df = prepare_logged_temp_data(temp_df)

    t = logged_df["Time"].to_numpy(dtype=float)
    y = logged_df["log_PopBio"].to_numpy(dtype=float)
    t_raw = logged_df["Time"].to_numpy(dtype=float)
    y_raw = logged_df["log_PopBio"].to_numpy(dtype=float)

    if len(y) < 3:
        raise ValueError(
            f"Not enough samples in logged dataset at Temp={temp_df['Temp'].iloc[0]}: "
            f"need >= 3, got {len(y)}"
        )

    best_record, n_successful = fit_with_fixed_starts(t, y)
    fit = best_record["fit"]
    n = len(y)

    theta_hat = np.array(
        [
            fit.params["theta_k"].value,
            fit.params["theta_r"].value,
            fit.params["theta_n0"].value,
        ],
        dtype=float,
    )
    params = np.exp(theta_hat)
    return {
        "temp": float(temp_df["Temp"].iloc[0]),
        "n_rows_raw": int(len(logged_df)),
        "n_rows": n,
        "n_rows_removed_after_log_filter": 0,
        "selection_metric": "AIC",
        "n_starts": int(logistic_fixed_start_count),
        "n_successful_starts": int(n_successful),
        "K": float(params[0]),
        "r": float(params[1]),
        "N0": float(params[2]),
        "RSS": float(best_record["RSS"]),
        "R2": float(best_record["R2"]),
        "RMSE": float(best_record["RMSE"]),
        "MAE": float(best_record["MAE"]),
        "AIC": float(best_record["AIC"]),
        "BIC": float(best_record["BIC"]),
        "success": bool(fit.success),
        "message": str(fit.message),
        "t": t,
        "y": y,
        "t_raw": t_raw,
        "y_raw": y_raw,
        "y_hat": best_record["y_hat_log"],
    }


def save_fit_plot(fit_result: dict, out_dir: Path) -> None:
    temp = fit_result["temp"]
    t_raw = fit_result["t_raw"]
    y_raw = fit_result["y_raw"]
    y_hat = fit_result["y_hat"]
    color = get_temp_color(temp)

    plt.figure(figsize=(7, 4.5))
    plt.scatter(t_raw, y_raw, s=18, alpha=0.55, color=color, label="Observed data")
    plt.plot(t_raw, y_hat, linewidth=2.0, color=color, label="Fit line")
    plt.title(f"Logistic model fit at {temp:g} °C")
    plt.xlabel("Time (Hours)")
    plt.ylabel("ln(population abundance, N)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(out_dir / f"logistic_fit_temp{int(temp)}.svg")
    plt.close()


def save_combined_temperature_plot(fit_results: list, out_dir: Path) -> Path:
    plt.figure(figsize=(8, 5))
    for fit_result in fit_results:
        temp = fit_result["temp"]
        y_hat = fit_result["y_hat"]
        t_raw = fit_result["t_raw"]
        y_raw = fit_result["y_raw"]
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
            t_raw,
            y_hat,
            linewidth=2.0,
            color=color,
            label=f"Fit line ({temp:g} °C)",
        )

    plt.title("Logistic model fits across temperatures")
    plt.xlabel("Time (Hours)")
    plt.ylabel("ln(population abundance, N)")
    plt.legend(fontsize=8, ncol=2, loc="lower right")
    plt.tight_layout()
    out_path = out_dir / "logistic_fit_all_temps.svg"
    plt.savefig(out_path)
    plt.close()
    return out_path


def fit_all_temperatures(
    subset: pd.DataFrame, out_dir: Path
) -> tuple[pd.DataFrame, list]:
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
                "K": fit_result["K"],
                "r": fit_result["r"],
                "N0": fit_result["N0"],
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
    print(
        "\nTemperature-wise logistic fit summary on ln(PopBio) "
        "(logistic 3-parameter):"
    )
    for _, row in fit_table.iterrows():
        print(
            f"Temp={row['Temp']:g} | n_rows_raw={int(row['n_rows_raw'])} | "
            f"n_rows_used={int(row['n_rows'])} | removed={int(row['n_rows_removed_after_log_filter'])} | "
            f"select_by={row['selection_metric']} | starts={int(row['n_starts'])} | "
            f"start_success={int(row['n_successful_starts'])} | "
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
