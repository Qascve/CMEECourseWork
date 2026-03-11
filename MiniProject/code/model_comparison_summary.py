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
selected_temp = 8


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
    plt.legend(loc="lower left")
    plt.tight_layout()

    out_path = out_dir / f"model_comparison_temp{int(selected_temp)}.svg"
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
    print(f"selected temperature: {selected_temp:g} °C")

    subset = load_logged_subset(data_path)
    modules = import_model_modules()
    fit_results, observed_df = fit_models_at_temperature(modules, subset, selected_temp)
    metrics_table = build_metrics_summary_table(fit_results, selected_temp)
    comparison_plot_path = save_model_comparison_plot(
        fit_results, observed_df, selected_temp, result_dir
    )

    metrics_table.to_csv(result_dir / "model_metrics_at_selected_temp.csv", index=False)

    print_metrics_summary(metrics_table)
    print(f"Saved metrics table: {result_dir / 'model_metrics_at_selected_temp.csv'}")
    print(f"Saved comparison plot: {comparison_plot_path}")


if __name__ == "__main__":
    main()
