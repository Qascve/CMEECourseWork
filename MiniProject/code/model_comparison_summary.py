#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import importlib
import io
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def find_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".gitignore").exists():
            return candidate
    raise FileNotFoundError("Could not find project root via .gitignore")


root_path = find_root(Path(__file__))
data_path = root_path / "MiniProject" / "data" / "tetraselmis_tetrahele_log.csv"
result_dir = root_path / "MiniProject" / "result" / "model_comparison_summary"
selected_temps = [8.0, 16.0, 25.0]


def load_logged_subset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_cols = ["Time", "log_PopBio", "Species", "Medium", "Temp"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    subset = df[
        (df["Species"] == "Tetraselmis tetrahele") & (df["Medium"] == "ESAW")
    ].copy()
    return subset.sort_values(by=["Temp", "Time"]).reset_index(drop=True)


def save_three_temperature_scatter_distribution(
    subset: pd.DataFrame, out_dir: Path
) -> Path:
    target_temps = [8.0, 16.0, 25.0]
    dist_df = subset[subset["Temp"].isin(target_temps)].copy()
    if dist_df.empty:
        raise ValueError("No data found for 8, 16, 25 °C.")

    summary_table = dist_df.groupby("Temp")["log_PopBio"].agg(["count", "mean"]).reset_index()

    print("\nObserved data summary at three temperatures:")
    for _, row in summary_table.sort_values(by="Temp").iterrows():
        print(
            f"Temp={row['Temp']:g} °C | n={int(row['count'])} | "
            f"mean(log_PopBio)={row['mean']:.4f}"
        )

    plt.figure(figsize=(8, 5))
    color_map = {8.0: "tab:blue", 16.0: "tab:orange", 25.0: "tab:green"}
    for temp in target_temps:
        temp_df = dist_df[dist_df["Temp"] == temp]
        plt.scatter(
            temp_df["Time"],
            temp_df["log_PopBio"],
            s=24,
            alpha=0.65,
            color=color_map[temp],
            label=f"Observed data ({int(temp)} °C)",
        )

    plt.title("Observed data across temperatures")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Population abundance(N)")
    plt.legend(loc="lower right")
    plt.tight_layout()

    out_path = out_dir / "three_temperature_distribution.pdf"
    plt.savefig(out_path)
    plt.close()
    return out_path


def import_model_modules() -> dict[str, object]:
    module_map = {
        "Logistic": "logistic_fit",
        "Baranyi": "baranyi_fit",
        "Three-phase linear": "three_phase_linear_fit",
    }
    imported = {}
    for model_name, module_name in module_map.items():
        with contextlib.redirect_stdout(io.StringIO()):
            imported[model_name] = importlib.import_module(module_name)
    return imported


def fit_models_at_temperature(
    modules: dict[str, object], subset: pd.DataFrame, selected_temp: float
) -> tuple[dict[str, dict], pd.DataFrame]:
    temp_df = subset[subset["Temp"] == selected_temp].copy()
    if temp_df.empty:
        raise ValueError(f"No data found for selected temperature {selected_temp:g}.")

    fit_results = {}
    for model_name, module in modules.items():
        fit_results[model_name] = module.fit_single_temperature(temp_df)

    return fit_results, temp_df.sort_values(by="Time").reset_index(drop=True)


def logistic_curve_from_fit(fit_result: dict, t_grid: np.ndarray) -> np.ndarray:
    k = float(fit_result["K"])
    r = float(fit_result["r"])
    n0 = float(fit_result["N0"])
    exp_arg = np.clip(-r * t_grid, -700, 700)
    denom = 1.0 + ((k - n0) / max(n0, 1e-12)) * np.exp(exp_arg)
    denom = np.clip(denom, 1e-12, None)
    return np.log(np.clip(k / denom, 1e-12, None))


def baranyi_curve_from_fit(fit_result: dict, t_grid: np.ndarray) -> np.ndarray:
    y0 = float(fit_result["N0"])
    ymax = float(fit_result["NMAX"])
    mu = float(fit_result["mumax"])
    lag = float(fit_result["lag"])
    h0 = mu * lag
    exp_neg_mut = np.exp(np.clip(-mu * t_grid, -700, 700))
    exp_neg_h0 = np.exp(np.clip(-h0, -700, 700))
    adjustment_core = exp_neg_mut + exp_neg_h0 - np.exp(np.clip(-mu * t_grid - h0, -700, 700))
    adjustment_core = np.clip(adjustment_core, 1e-12, None)
    at = t_grid + np.log(adjustment_core) / max(mu, 1e-12)
    exp_mu_at = np.exp(np.clip(mu * at, -700, 700))
    exp_capacity = np.exp(np.clip(ymax - y0, -700, 700))
    denom = 1.0 + (exp_mu_at - 1.0) / max(exp_capacity, 1e-12)
    denom = np.clip(denom, 1e-12, None)
    return y0 + mu * at - np.log(denom)


def three_phase_curve_from_fit(fit_result: dict, t_grid: np.ndarray) -> np.ndarray:
    n0 = float(fit_result["N0"])
    nmax = float(fit_result["NMAX"])
    tlag = float(fit_result["tLAG"])
    tmax = float(fit_result["tMAX"])
    duration = max(tmax - tlag, 1e-12)
    mu = (nmax - n0) / duration
    growth = n0 + mu * (t_grid - tlag)
    return np.where(t_grid <= tlag, n0, np.where(t_grid >= tmax, nmax, growth))


def save_model_comparison_plot(
    fit_results: dict[str, dict], observed_df: pd.DataFrame, selected_temp: float, out_dir: Path
) -> Path:
    t_obs = observed_df["Time"].to_numpy(dtype=float)
    y_obs = observed_df["log_PopBio"].to_numpy(dtype=float)
    t_grid = np.linspace(float(np.min(t_obs)), float(np.max(t_obs)), 500)

    curve_specs = [
        ("Logistic", "tab:blue", "-", logistic_curve_from_fit(fit_results["Logistic"], t_grid)),
        (
            "Baranyi",
            "tab:orange",
            "--",
            fit_results["Baranyi"]["y_hat_grid"],
        ),
        (
            "Three-phase linear",
            "tab:green",
            "-.",
            fit_results["Three-phase linear"]["y_hat_grid"],
        ),
    ]

    plt.figure(figsize=(8, 5))
    plt.scatter(t_obs, y_obs, s=18, alpha=0.45, color="black", label="Observed data")
    plt.plot(t_grid, curve_specs[0][3], color=curve_specs[0][1], linestyle=curve_specs[0][2], linewidth=2.1, label="Logistic fit")
    plt.plot(
        fit_results["Baranyi"]["t_grid"],
        curve_specs[1][3],
        color=curve_specs[1][1],
        linestyle=curve_specs[1][2],
        linewidth=2.1,
        label="Baranyi fit",
    )
    plt.plot(
        fit_results["Three-phase linear"]["t_grid"],
        curve_specs[2][3],
        color=curve_specs[2][1],
        linestyle=curve_specs[2][2],
        linewidth=2.1,
        label="Three-phase linear fit",
    )
    plt.title(f"Model comparison at {selected_temp:g} °C")
    plt.xlabel("Time (Hours)")
    plt.ylabel("Population abundance(N)")
    plt.legend(loc="lower right")
    plt.tight_layout()

    out_path = out_dir / f"model_comparison_temp{int(selected_temp)}.pdf"
    plt.savefig(out_path)
    plt.close()
    return out_path


def build_metrics_summary_table(fit_results: dict[str, dict], selected_temp: float) -> pd.DataFrame:
    summary_rows = []
    for model_name, fit_result in fit_results.items():
        summary_rows.append(
            {
                "Model": model_name,
                "Temp": float(selected_temp),
                "R2": float(fit_result["R2"]),
                "RMSE": float(fit_result["RMSE"]),
                "AIC": float(fit_result["AIC"]),
                "BIC": float(fit_result["BIC"]),
            }
        )

    return pd.DataFrame(summary_rows).sort_values(by="Model").reset_index(drop=True)


def print_metrics_summary(metrics_table: pd.DataFrame) -> None:
    print("\nModel metrics summary at selected temperature:")
    for _, row in metrics_table.iterrows():
        print(
            f"{row['Model']}: Temp={row['Temp']:g} | R2={row['R2']:.4f} | "
            f"RMSE={row['RMSE']:.4f} | AIC={row['AIC']:.2f} | BIC={row['BIC']:.2f}"
        )


def main() -> None:
    result_dir.mkdir(parents=True, exist_ok=True)

    print(f"root path: {root_path}")
    print(f"data path: {data_path}")
    print(f"result dir: {result_dir}")
    print(
        "selected temperatures: "
        + ", ".join(f"{temp:g}" for temp in selected_temps)
        + " °C"
    )

    subset = load_logged_subset(data_path)
    distribution_plot_path = save_three_temperature_scatter_distribution(subset, result_dir)

    modules = import_model_modules()
    all_metrics_tables: list[pd.DataFrame] = []
    for selected_temp in selected_temps:
        fit_results, observed_df = fit_models_at_temperature(modules, subset, selected_temp)
        metrics_table = build_metrics_summary_table(fit_results, selected_temp)
        all_metrics_tables.append(metrics_table)
        comparison_plot_path = save_model_comparison_plot(
            fit_results, observed_df, selected_temp, result_dir
        )

        print_metrics_summary(metrics_table)
        print(f"Saved comparison plot: {comparison_plot_path}")

    merged_metrics = (
        pd.concat(all_metrics_tables, ignore_index=True)
        .sort_values(by=["Temp", "Model"])
        .reset_index(drop=True)
    )
    merged_out_path = result_dir / "model_metrics_all_temps.csv"
    merged_metrics.to_csv(merged_out_path, index=False)
    print(f"Saved merged metrics table: {merged_out_path}")

    print(f"Saved distribution plot: {distribution_plot_path}")


if __name__ == "__main__":
    main()
