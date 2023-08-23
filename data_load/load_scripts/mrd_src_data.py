import os
import sys
from pathlib import Path

import pandas as pd

from data_load.db.database import config
from data_load.load_scripts.xref_funds_lookup import clean_df_headers

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)


def get_latest_file(folder_path: Path, pattern: str = "*.xlsx"):
    files = folder_path.glob(pattern)
    paths = [os.path.join(folder_path, file.name) for file in files]
    return Path(max(paths, key=os.path.getctime))


def load_fe_master_annualised_fund_performance() -> pd.DataFrame:
    """
    Monthly indices performance is extracted from Fund Analytics in csv format and dropped into the mrd fund index
    folder. Performance data is in the local currency of the fund (ZAR, USD, GBP etc...).

    :return:
        Dataframe: of monthly fund performance similar in structure to the morningstar report.
    """
    from data_load.load_scripts.date_utils import last_month
    fe_master_fund_performance = get_latest_file(Path(config.get("MRD_SRC_FUND_PERFORMANCE_ANU")), pattern="*.csv")
    match_cols = [
        "fe_fund_name",
        "isin_code",
        "fund_currency",
        "one_month_cumulative_performance",
        "three_month_cumulative_performance",
        "six_month_cumulative_performance",
        "one_year_cumulative_performance",
        "two_year_cumulative_performance",
        "three_year_cumulative_performance",
        "five_year_cumulative_performance",
        "seven_year_cumulative_performance",
        "three_year_cumulative_volatility",
        "fund_size_millions",
        "month_end",
    ]
    df = pd.read_csv(fe_master_fund_performance, skiprows=[0, 1], index_col=None)
    df['month_end'] = pd.to_datetime(last_month())
    df.columns = match_cols
    df['fund_currency'] = df['fund_currency'].str.replace('GBX', 'GBP')
    df['src_file'] = fe_master_fund_performance.name
    df = clean_df_headers(df)

    return df


def load_fe_master_cumulative_fund_performance() -> pd.DataFrame:
    """
    Monthly indices performance is extracted from Fund Analytics in csv format and dropped into the mrd fund index
    folder. Performance data is in the local currency of the fund (ZAR, USD, GBP etc...).

    :return:
        Dataframe: of monthly fund performance similar in structure to the morningstar report.
    """
    from data_load.load_scripts.date_utils import last_month
    fe_master_fund_performance = get_latest_file(Path(config.get("MRD_SRC_FUND_PERFORMANCE_CUM")), pattern="*.csv")
    match_cols = [
        "fe_fund_name",
        "isin_code",
        "fund_currency",
        "one_month_cumulative_performance",
        "three_month_cumulative_performance",
        "six_month_cumulative_performance",
        "ytd_month_cumulative_performance",
        "one_year_cumulative_performance",
        "two_year_cumulative_performance",
        "three_year_cumulative_performance",
        "five_year_cumulative_performance",
        "seven_year_cumulative_performance",
        "three_year_cumulative_volatility",
        "month_end",
    ]
    df = pd.read_csv(fe_master_fund_performance, skiprows=[0, 1], index_col=None)
    df['month_end'] = pd.to_datetime(last_month())
    df.columns = match_cols
    df['fund_currency'] = df['fund_currency'].str.replace('GBX', 'GBP')
    df['src_file'] = fe_master_fund_performance.name
    df = clean_df_headers(df)

    return df


def load_fe_master_index_performance():
    """
    Monthly fund performance is extracted from Fund Analytics in csv format and dropped into the mrd fund data folder.
    :return:
        Dataframe: of monthly index performance similar in structure to the morningstar report.
    """
    from data_load.load_scripts.date_utils import last_month
    fe_master_index_performance = get_latest_file(Path(config.get("MRD_SRC_INDEX_PERFORMANCE_ANU")), pattern="*.csv")
    match_cols = [
        "fe_index_name",
        "index_currency",
        "one_month_cumulative_performance",
        "three_month_cumulative_performance",
        "six_month_cumulative_performance",
        "one_year_cumulative_performance",
        "two_year_cumulative_performance",
        "three_year_cumulative_performance",
        "five_year_cumulative_performance",
        "seven_year_cumulative_performance",
        "three_year_cumulative_volatility",
        "month_end"
    ]
    df = pd.read_csv(fe_master_index_performance, skiprows=[0, 1], index_col=None)
    df['month_end'] = pd.to_datetime(last_month())
    df.drop(df.iloc[:, [1, 12]], inplace=True, axis=1)
    df.columns = match_cols
    df['index_currency'] = df['index_currency'].str.replace('GBX', 'GBP')
    df['src_file'] = fe_master_index_performance.name
    df = clean_df_headers(df)

    return df


def load_fe_master_cumulative_index_performance():
    """
    Monthly fund performance is extracted from Fund Analytics in csv format and dropped into the mrd fund data folder.
    :return:
        Dataframe: of monthly index performance similar in structure to the morningstar report.
    """
    from data_load.load_scripts.date_utils import last_month
    fe_master_index_performance = get_latest_file(Path(config.get("MRD_SRC_INDEX_PERFORMANCE_CUM")), pattern="*.csv")
    match_cols = [
        "fe_index_name",
        "index_currency",
        "one_month_cumulative_performance",
        "three_month_cumulative_performance",
        "six_month_cumulative_performance",
        "ytd_cumulative_performance",
        "one_year_cumulative_performance",
        "two_year_cumulative_performance",
        "three_year_cumulative_performance",
        "five_year_cumulative_performance",
        "seven_year_cumulative_performance",
        "three_year_cumulative_volatility",
        "month_end"
    ]
    df = pd.read_csv(fe_master_index_performance, skiprows=[0, 1], index_col=None)
    df['month_end'] = pd.to_datetime(last_month())
    df.drop('ISIN Code', inplace=True, axis=1)
    df.columns = match_cols
    df['index_currency'] = df['index_currency'].str.replace('GBX', 'GBP')
    df['src_file'] = fe_master_index_performance.name
    df = clean_df_headers(df)

    return df


def load_gi_fund_list():
    gi_fund_list = get_latest_file(Path(config.get("GI_FUNDLIST")))
    df = pd.read_excel(
        gi_fund_list,
        sheet_name="Sheet1",
        header=1,
        index_col=None,
        engine="openpyxl",
        usecols="A:J",
    )
    df = clean_df_headers(df)
    df = df.rename(columns={"investment_option_name": "fund_name"})
    df["fund_code"] = df["fund_code"].astype(str)
    final_df = df.iloc[:-1, :].copy()
    # df = df.loc[:, ["fund_name", "fund_code"]]
    final_df.to_csv(config.get("GI_FUNDLIST_SEED_OUTPUT"), index=False)
    sys.stdout.write("\nGI Fund List loaded successfully")

    return final_df


def load_fe_asset_allocations():
    """
    Extracts the asset allocation data from the FE Master Fund List and drops it into the mrd fund data folder.
    :return:
        Dataframe: of asset allocation data similar in structure to the morningstar report.
    """
    match_cols = [
        "fe_fund_name",
        "isin_code",
        "fund_currency",
        "asset_class",
        "domicile",
        'alternative_investment_strategies',
        'alternative_assets',
        'commodity_&_energy',
        'convertibles',
        'equities',
        'north_american_equities',
        'asia_pacific_equities',
        'european_equities',
        'uk_equities',
        'global_emerging_market_equities',
        'international_equities',
        'gcc_equities',
        'south_african_equities',
        'fixed_interest',
        'uk_fixed_interest',
        'global_fixed_interest',
        'south_african_fixed_interest',
        'islamic_instruments',
        'mixed_assets',
        'money_market',
        'mutual_funds',
        'others',
        'property',
        'unknown',
        'with_profits'
    ]

    fe_asset_allocation_file = get_latest_file(Path(config.get("MRD_SRC_ASSET_ALLOCATION")), pattern="*.csv")
    initial_df = pd.read_csv(fe_asset_allocation_file, skiprows=[0, 1], index_col=None)
    df = initial_df.copy()
    df = clean_df_headers(df)
    df.iloc[:, 5:] = df.iloc[:, 5:].fillna(0)
    df.columns = match_cols
    df['fund_currency'] = df['fund_currency'].str.replace('GBX', 'GBP')
    long_df = pd.melt(df, id_vars=['fe_fund_name', 'isin_code', 'domicile'], value_vars=df.columns[5:])
    final_df = long_df.copy().drop(long_df[long_df.value.eq(0)].index)
    final_df['variable'] = final_df['variable'].str.replace('_&_', '_').str.title()
    final_df.columns = ['fe_fund_name', 'master_isin_code', 'domicile', 'asset_class_sub', 'allocation']

    return final_df.reset_index(drop=True)
