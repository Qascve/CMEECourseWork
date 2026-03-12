#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import re

def find_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".gitignore").exists():
            return candidate
    raise FileNotFoundError("Could not find project root via .gitignore")


root_path = find_root(Path(__file__))
data_path = Path("MiniProject") / "data" / "logistic_growth_data.csv"
data_path = root_path / data_path
result_dir = root_path / "MiniProject" / "result" / "explore_dataset"
print(f"root path: {root_path}")
print(f"data path: {data_path}")


TOP_N = 10
TARGET_TEMPS = {8, 16, 25}


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
        "Rep",
        "Citation",
    ]
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
   
    return df[required_cols].copy()


def count_unique_species_medium(df: pd.DataFrame) -> int:
    return df[["Species", "Medium"]].drop_duplicates().shape[0]


def top_groups_by_unique_temperature(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    # Summarize each Species+Medium by total rows and temperature coverage.
    grouped = (
        df.groupby(["Species", "Medium"], as_index=False)
        .agg(
            n_rows_total=("Temp", "size"),
            n_unique_temps=("Temp", pd.Series.nunique),
            temperature_list=("Temp", lambda s: sorted(pd.unique(s.dropna()))),
        )
        .sort_values(by=["n_rows_total", "Species", "Medium"], ascending=[False, True, True])
        .head(top_n)
        .reset_index(drop=True)
    )
    return grouped


def format_temperature_list(temps: list[float]) -> str:
    return ", ".join(f"{t:g}" for t in temps)


def tetraselmis_tetrahele_esaw_by_temp(df: pd.DataFrame) -> pd.DataFrame:
    subset = df[
        (df["Species"] == "Tetraselmis tetrahele") & (df["Medium"] == "ESAW")
    ].copy()
    return (
        subset.groupby("Temp", as_index=False)
        .agg(n_rows=("Temp", "size"))
        .sort_values(by=["n_rows", "Temp"], ascending=[False, True])
        .reset_index(drop=True)
    )


def create_tetraselmis_tetrahele_dataset(
    df: pd.DataFrame, output_path: Path
) -> pd.DataFrame:
    subset = df[
        (df["Species"] == "Tetraselmis tetrahele") & (df["Medium"] == "ESAW")
    ].copy()
    subset = subset[subset["Temp"].isin(TARGET_TEMPS)].copy()
    subset = subset.rename(columns={"Rep": "rep"})
    ordered_cols = [
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
    subset = subset[ordered_cols]
    subset.to_csv(output_path, index=False)
    return subset


def summarize_created_dataset_by_temp(created_df: pd.DataFrame) -> pd.DataFrame:
    return (
        created_df.groupby(["Species", "Medium", "Temp"], as_index=False)
        .agg(n_rows=("Temp", "size"))
        .sort_values(by=["Species", "Medium", "Temp"], ascending=[True, True, True])
        .reset_index(drop=True)
    )


def safe_filename(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")


def plot_top_groups_summary(top_groups: pd.DataFrame, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = [
        f"{row['Species']} | {row['Medium']}" for _, row in top_groups.iterrows()
    ]
    values = top_groups["n_rows_total"].to_numpy(dtype=float)
    temps = top_groups["n_unique_temps"].to_numpy(dtype=int)

    plt.figure(figsize=(12, 6.5))
    bars = plt.barh(range(len(labels)), values, color="#4C78A8", alpha=0.9)
    plt.gca().invert_yaxis()
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.xlabel("n_rows_total")
    plt.title("Top groups by total rows (Species + Medium)")

    for bar, n_temp in zip(bars, temps):
        x = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        plt.text(x + max(values) * 0.01, y, f"n_unique_temps={n_temp}", va="center", fontsize=8)

    plt.tight_layout()
    out_path = out_dir / "top_groups_summary.pdf"
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path


def main() -> None:
    df = load_data(data_path)

    unique_combo_count = count_unique_species_medium(df)
    top_groups = top_groups_by_unique_temperature(df, top_n=TOP_N)
    tetraselmis_esaw = tetraselmis_tetrahele_esaw_by_temp(df)
    output_path = data_path.parent / "tetraselmis_tetrahele.csv"
    tetraselmis_subset = create_tetraselmis_tetrahele_dataset(df, output_path)
    created_summary = summarize_created_dataset_by_temp(tetraselmis_subset)
    summary_plot_path = plot_top_groups_summary(top_groups, result_dir)

    print(f"Dataset: {data_path}")
    print(f"Unique (Species, Medium) combinations: {unique_combo_count}")
    print("\n")
    print(
        f"Top {TOP_N} (Species, Medium) groups by total rows "
        "(with unique temperature count and temperature list):"
    )
    print("\n")
    
    for idx, row in top_groups.iterrows():
        # Print readable temperatures so the top groups are easy to check.
        temps = format_temperature_list(row["temperature_list"])
        print(
            f"{idx + 1}. Species={row['Species']} | Medium={row['Medium']} | "
            f"n_unique_temps={row['n_unique_temps']} | temps=[{temps}] | "
            f"n_rows_total={row['n_rows_total']}"
        )

    print("\n")
    print("Tetraselmis tetrahele | Medium=ESAW by temperature (sorted by n_rows desc):")
    for idx, row in tetraselmis_esaw.iterrows():
        print(f"{idx + 1}. Temp={row['Temp']:g} | n_rows={row['n_rows']}")
    print("\n")
    print(
        "Created filtered dataset: "
        f"{output_path} | n_rows={len(tetraselmis_subset)}"
    )
    for _, row in created_summary.iterrows():
        print(
            f"Species={row['Species']} | Medium={row['Medium']} | "
            f"Temp={row['Temp']:g} | n_rows={row['n_rows']}"
        )
    print("\n")
    print("Saved top-group summary plot:")
    print(summary_plot_path)


if __name__ == "__main__":
    main()
