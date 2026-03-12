#!/usr/bin/env python3

from pathlib import Path

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
source_data_path = root_path / "MiniProject" / "data" / "tetraselmis_tetrahele.csv"
output_data_path = root_path / "MiniProject" / "data" / "tetraselmis_tetrahele_log.csv"

print(f"root path: {root_path}")
print(f"source data path: {source_data_path}")
print(f"output data path: {output_data_path}")


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required_cols = [
        "Time",
        "PopBio",
        "Temp",
        "Time_units",
        "PopBio_units",
        "Species",
        "Medium",
        "rep",
        "Citation",
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def create_logged_dataset(df: pd.DataFrame) -> pd.DataFrame:
    logged_df = df.copy()
    with np.errstate(divide="ignore", invalid="ignore"):
        logged_df["log_PopBio"] = np.log(logged_df["PopBio"].to_numpy(dtype=float))

    logged_df = logged_df[np.isfinite(logged_df["log_PopBio"])].copy()
    logged_df = logged_df[logged_df["log_PopBio"] >= 0].copy()
    logged_df["log_PopBio_units"] = "ln(N)"

    ordered_cols = [
        "Time",
        "PopBio",
        "log_PopBio",
        "Temp",
        "Time_units",
        "PopBio_units",
        "log_PopBio_units",
        "Species",
        "Medium",
        "rep",
        "Citation",
    ]
    return logged_df[ordered_cols].sort_values(by=["Temp", "rep", "Time"]).reset_index(
        drop=True
    )


def summarize_by_temp(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Species", "Medium", "Temp"], as_index=False)
        .agg(n_rows=("Temp", "size"))
        .sort_values(by=["Temp"], ascending=[True])
        .reset_index(drop=True)
    )


def main() -> None:
    df = load_data(source_data_path)
    logged_df = create_logged_dataset(df)
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    logged_df.to_csv(output_data_path, index=False)

    summary = summarize_by_temp(logged_df)
    print(f"Saved logged dataset: {output_data_path}")
    print(f"Rows in source dataset: {len(df)}")
    print(f"Rows in logged dataset: {len(logged_df)}")
    print("\nLogged dataset summary by temperature:")
    for _, row in summary.iterrows():
        print(
            f"Species={row['Species']} | Medium={row['Medium']} | "
            f"Temp={row['Temp']:g} | n_rows={row['n_rows']}"
        )


if __name__ == "__main__":
    main()
