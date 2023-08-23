from pathlib import Path

import pandas as pd
from dotenv import dotenv_values

config = dotenv_values()


def update_monthly_performance_data_seed():
    perf_file = Path(config.get("PERF_DATA_FILE"))
    output_file = config.get("PERF_DATA__INDEX_SEED_OUTPUT")

    df = pd.read_excel(
        perf_file, sheet_name="main", header=0, index_col=None, usecols="A:Z"
    )
    df = df.copy().dropna(axis='columns', thresh=4).dropna(axis="rows", how="all")
    df = df.iloc[:-8, :]
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.rename(
        columns={
            "unnamed:_0": "month_end",
            "us_cpi_(cpi-u)": "us_cpi",
            "zar_aud": "zaraud",
        }
    )
    df["month_end"] = pd.to_datetime(df["month_end"])
    df = df.loc[
        :,
        [
            "month_end",
            "jse_allshare",
            "all_share_total_return",
            "cpi",
            "us_cpi",
            "msci_world",
            "msci_acwi",
        ],
    ]
    df.to_csv(output_file, index=False)


def update_monthly_performance_data_currencies_seed():
    perf_file = Path(config.get("PERF_DATA_FILE"))
    output_file = config.get("PERF_DATA_CURRENCY_SEED_OUTPUT")

    df = pd.read_excel(
        perf_file, sheet_name="currencies", header=0, index_col=None, usecols="A:M"
    )
    df = df.copy().dropna(axis="columns", thresh=4).dropna(axis="rows", how="all")
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df["month_end"] = pd.to_datetime(df["month_end"])

    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    update_monthly_performance_data_currencies_seed()
    update_monthly_performance_data_seed()
