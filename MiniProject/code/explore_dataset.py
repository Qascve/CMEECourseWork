#!/usr/bin/env python3

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "logistic_growth_data.csv"
TOP_N = 10


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


def lactobaciulus_plantarum_mrs_by_temp(df: pd.DataFrame) -> pd.DataFrame:
    subset = df[
        (df["Species"] == "Lactobaciulus plantarum") & (df["Medium"] == "MRS")
    ].copy()
    return (
        subset.groupby("Temp", as_index=False)
        .agg(n_rows=("Temp", "size"))
        .sort_values(by=["n_rows", "Temp"], ascending=[False, True])
        .reset_index(drop=True)
    )


def create_lactobaciulus_plantarum_temp_dataset(
    df: pd.DataFrame, output_path: Path
) -> pd.DataFrame:
    subset = df[
        (df["Species"] == "Lactobaciulus plantarum") & (df["Temp"].isin([10, 20, 25]))
    ].copy()
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


def main() -> None:
    df = load_data(DATA_PATH)

    unique_combo_count = count_unique_species_medium(df)
    top_groups = top_groups_by_unique_temperature(df, top_n=TOP_N)
    plantarum_mrs = lactobaciulus_plantarum_mrs_by_temp(df)
    output_path = DATA_PATH.parent / "lactobaciulus_plantarum.csv"
    plantarum_temp_subset = create_lactobaciulus_plantarum_temp_dataset(df, output_path)

    print(f"Dataset: {DATA_PATH}")
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
    print("Lactobaciulus plantarum | Medium=MRS by temperature (sorted by n_rows desc):")
    for idx, row in plantarum_mrs.iterrows():
        print(f"{idx + 1}. Temp={row['Temp']:g} | n_rows={row['n_rows']}")
    print("\n")
    print(
        "Created filtered dataset: "
        f"{output_path} | n_rows={len(plantarum_temp_subset)}"
    )


if __name__ == "__main__":
    main()
