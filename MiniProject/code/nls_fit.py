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
data_path = Path("MiniProject") / "data" / "tetraselmis_tetrahele.csv"
data_path = root_path / data_path
result_dir = root_path / "MiniProject" / "result" / "nls_fit"

nls_fit_n_starts = 50
seed = 0

print(f"root path: {root_path}")
print(f"data path: {data_path}")
print(f"result dir: {result_dir}")


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_cols = ["Time", "PopBio", "Species", "Medium", "Temp"]
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


def logistic_3p(t: np.ndarray, theta: np.ndarray) -> np.ndarray:
    # theta is in log-space so parameters remain positive after exp.
    k, r, n0 = np.exp(np.clip(theta, -20, 20))
    exp_arg = np.clip(-r * t, -700, 700)
    with np.errstate(over="ignore", invalid="ignore"):
        denom = 1.0 + ((k - n0) / n0) * np.exp(exp_arg)
    denom = np.where(np.isfinite(denom), denom, 1e12)
    denom = np.where(np.abs(denom) < 1e-12, 1e-12, denom)
    return k / denom


def residuals(theta: np.ndarray, t: np.ndarray, y: np.ndarray) -> np.ndarray:
    return y - logistic_3p(t, theta)


def residuals_lmfit(params: Parameters, t: np.ndarray, y: np.ndarray) -> np.ndarray:
    theta = np.array(
        [
            params["theta_k"].value,
            params["theta_r"].value,
            params["theta_n0"].value,
        ],
        dtype=float,
    )
    return residuals(theta, t, y)


def initial_theta(t: np.ndarray, y: np.ndarray) -> np.ndarray:
    y_pos = np.clip(y, 1e-8, None)
    n0_guess = float(np.percentile(y_pos, 5))
    k_guess = float(np.percentile(y_pos, 95))
    if k_guess <= n0_guess:
        k_guess = float(y_pos.max() * 1.2)
    r_guess = 0.1
    return np.log([k_guess, r_guess, n0_guess])


def remove_outliers_iqr(data: np.ndarray) -> tuple[np.ndarray, float, float]:
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    filtered = data[(data >= lower) & (data <= upper)]
    return filtered, lower, upper


def remove_extreme_values(temp_df: pd.DataFrame) -> pd.DataFrame:
    y = temp_df["PopBio"].to_numpy(dtype=float)
    _, lower, upper = remove_outliers_iqr(y)
    keep_mask = (y >= lower) & (y <= upper)
    cleaned = temp_df.loc[keep_mask].copy()
    # Keep at least a minimal sample size for fitting.
    if len(cleaned) < 8:
        return temp_df.copy()
    return cleaned


def fit_with_multistart(
    t: np.ndarray, y: np.ndarray, n_starts: int, rng: np.random.Generator
) -> tuple:
    base_theta = initial_theta(t, y)
    theta_candidates = [base_theta]
    for _ in range(n_starts - 1):
        noise = rng.normal(loc=0.0, scale=[0.35, 0.8, 0.35], size=3)
        theta_candidates.append(base_theta + noise)

    best_fit = None
    best_y_hat = None
    best_rss = np.inf
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
                args=(t, y),
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
            resid = y - y_hat
            rss = float(np.nansum(resid**2))
            if not np.isfinite(rss):
                continue
            n_successful += 1
            if rss < best_rss:
                best_fit = fit
                best_y_hat = y_hat
                best_rss = rss
        except Exception:
            # Try-like behavior: skip failed starts and continue searching.
            continue

    if best_fit is None:
        raise RuntimeError("All multi-start LM fits failed.")

    return best_fit, best_y_hat, best_rss, n_successful


def fit_single_temperature(temp_df: pd.DataFrame) -> dict:
    raw_df = temp_df[["Time", "PopBio", "Temp"]].dropna().copy()
    raw_df = raw_df.sort_values(by="Time").reset_index(drop=True)
    cleaned_df = remove_extreme_values(raw_df)
    cleaned_df = cleaned_df.sort_values(by="Time").reset_index(drop=True)

    t = cleaned_df["Time"].to_numpy(dtype=float)
    y = cleaned_df["PopBio"].to_numpy(dtype=float)
    t_raw = raw_df["Time"].to_numpy(dtype=float)
    y_raw = raw_df["PopBio"].to_numpy(dtype=float)

    rng = np.random.default_rng(seed + int(cleaned_df["Temp"].iloc[0]))
    fit, y_hat, rss, n_successful = fit_with_multistart(t, y, nls_fit_n_starts, rng)

    resid = y - y_hat
    n = len(y)
    k = 3
    tss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - rss / tss if tss > 0 else np.nan
    rmse = float(np.sqrt(rss / n))
    mae = float(np.mean(np.abs(resid)))
    rss_safe = max(rss, 1e-12)
    loglik = -0.5 * n * (np.log(2 * np.pi) + 1 + np.log(rss_safe / n))
    aic = 2 * k - 2 * loglik
    bic = np.log(n) * k - 2 * loglik

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
        "n_rows_raw": int(len(raw_df)),
        "n_rows": n,
        "n_outliers_removed": int(len(raw_df) - len(cleaned_df)),
        "n_starts": int(nls_fit_n_starts),
        "n_successful_starts": int(n_successful),
        "K": float(params[0]),
        "r": float(params[1]),
        "N0": float(params[2]),
        "RSS": rss,
        "R2": float(r2),
        "RMSE": rmse,
        "MAE": mae,
        "AIC": float(aic),
        "BIC": float(bic),
        "success": bool(fit.success),
        "message": str(fit.message),
        "t": t,
        "y": y,
        "t_raw": t_raw,
        "y_raw": y_raw,
        "y_hat": y_hat,
    }


def save_fit_plot(fit_result: dict, out_dir: Path) -> None:
    temp = fit_result["temp"]
    t = fit_result["t"]
    y = fit_result["y"]
    t_raw = fit_result["t_raw"]
    y_raw = fit_result["y_raw"]
    y_hat = fit_result["y_hat"]

    plt.figure(figsize=(7, 4.5))
    plt.scatter(t_raw, y_raw, s=16, alpha=0.35, label="Observed (raw)")
    plt.scatter(t, y, s=18, alpha=0.75, label="Used after outlier filter")
    plt.plot(t, y_hat, linewidth=2.0, label="nls fit")
    plt.title(f"Growth of Tetraselmis tetrahele at {temp:g} C")
    plt.xlabel("Time (Hours)")
    plt.ylabel("PopBio (N)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(out_dir / f"nls_fit_temp{int(temp)}.svg")
    plt.close()


def save_combined_temperature_plot(fit_results: list, out_dir: Path) -> Path:
    plt.figure(figsize=(8, 5))
    for fit_result in fit_results:
        temp = fit_result["temp"]
        t = fit_result["t"]
        y_hat = fit_result["y_hat"]
        t_raw = fit_result["t_raw"]
        y_raw = fit_result["y_raw"]
        plt.scatter(t_raw, y_raw, s=10, alpha=0.25, label=f"Raw Temp={temp:g}")
        plt.plot(t, y_hat, linewidth=2.0, label=f"Fit Temp={temp:g}")

    plt.title("Growth of Tetraselmis tetrahele across temperatures")
    plt.xlabel("Time (Hours)")
    plt.ylabel("PopBio (N)")
    plt.legend(fontsize=8, ncol=2, loc="upper left")
    plt.tight_layout()
    out_path = out_dir / "logistic_fit_all_temps.svg"
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
                "n_outliers_removed": fit_result["n_outliers_removed"],
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
    print("\nTemperature-wise nls fit summary (logistic 3-parameter):")
    for _, row in fit_table.iterrows():
        print(
            f"Temp={row['Temp']:g} | n_rows_raw={int(row['n_rows_raw'])} | "
            f"n_rows_used={int(row['n_rows'])} | removed={int(row['n_outliers_removed'])} | "
            f"starts={int(row['n_starts'])} | start_success={int(row['n_successful_starts'])} | "
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
