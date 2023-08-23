import difflib
import sys

import gspread
import pandas as pd
import numpy as np
from dotenv import dotenv_values

from data_load.db.database import engine

config = dotenv_values()


def get_table_from_dw(table_name: str, schema: str, db_engine):
    with db_engine.connect() as conn:
        table_df = pd.read_sql_table(table_name=table_name, con=conn, schema=schema)
        table_df = clean_df_headers(table_df)
        return table_df


def clean_df_headers(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataframe headers.
    :param dataframe: dataframe to clean
    :return: cleaned dataframe
    """
    dataframe.columns = (
        dataframe.columns.str.replace(" ", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.lower()
        .str.rstrip(".")
    )

    return dataframe


def remove_duplicates_in_string(fund_name) -> str:
    """
    if a fund name contains duplicate words eg. (Foord Foord Flexible Fund), this removes the duplicate words by making each word a dict key therefore eliminating duplicates.
    :param fund_name:
    :return string with deduplicated words:
    """
    string = " ".join(dict.fromkeys(fund_name.split()))

    return string


def get_fund_match(fund_name: str, fe_funds: pd.DataFrame, cutoff: float) -> str:
    """
    :param fund_name:
    :param cutoff: confidence level between 0 and 1. Defauly is 0.6
    :return:
    """
    # get_close_matches(word, possibilities, n, cutoff)
    try:
        match = difflib.get_close_matches(
            fund_name, fe_funds["clean_fund_name"], 1, cutoff
        )[0]
    except IndexError as e:
        match = "No Match Found"

    return match


# # Google Spreadsheet Access

# Using gspread with service account to connect to source sheet

def open_google_sheet_as_df(file_name: str, sheet_name: str) -> pd.DataFrame:
    """
    Authorisation is at a "service account" level, so the credentials are stored in a json file. In order to open the file, it needs to be shared with the service account email
    :param file_name:
    :param sheet_name:
    :return:
    """
    gc = gspread.service_account()
    sh = gc.open(file_name)
    ws = sh.worksheet(sheet_name)
    df = pd.DataFrame(ws.get_all_records())

    return df


def get_fund_analytics_local_fund_list() -> pd.DataFrame:
    """
    Get the fund list from the Fund Analytics Google Sheet
    :return: dataframe of fund list
    """
    fe_fund_pattern = "\s(?:TR.+|in.+)$"
    fe_funds = open_google_sheet_as_df("FE CGWM Fund List", "mrd_mutual_transform")
    fe_funds["clean_fund_name"] = (
        fe_funds["fund_name"]
        .str.replace(pat=fe_fund_pattern, repl="", regex=True)
        .apply(remove_duplicates_in_string)
    )
    fe_funds.to_csv(config.get("FE_LOCAL_SEED_OUTPUT"), index=False)

    return fe_funds


def get_fund_analytics_intl_fund_list() -> pd.DataFrame:
    """
    Get the fund list from the Fund Analytics Google Sheet
    :return: dataframe of fund list
    """
    fe_fund_pattern = "\s(?:TR.+|in.+)$"
    fe_intl_funds = open_google_sheet_as_df("FE CGWM Fund List", "mrd_intl_transform")
    fe_intl_funds["clean_fund_name"] = (
        fe_intl_funds["fund_name"]
        .str.replace(pat=fe_fund_pattern, repl="", regex=True)
        .apply(remove_duplicates_in_string)
    )
    fe_intl_funds.to_csv(config.get("FE_INTL_SEED_OUTPUT"), index=False)

    return fe_intl_funds


def get_fund_performance_monthly_data():
    """
    Get the fund performance data from the Fund Analytics Google Sheet
    :return: dataframe of fund performance data
    """
    fe_fund_performance = open_google_sheet_as_df(
        "FE CGWM Fund List", "master_funds_transform"
    )
    fe_fund_performance = fe_fund_performance.replace(r"^\s*$", np.nan, regex=True)
    fe_fund_performance.iloc[:, 3:-2] = fe_fund_performance.iloc[:, 3:-2].astype(
        "float64"
    )

    return fe_fund_performance


def get_fund_xref():
    """
    Get the fund xref data from the Fund Analytics Google Sheet
    :return: dataframe of fund xref data
    """
    fe_fund_xref = open_google_sheet_as_df("FE CGWM Fund List", "xref_funds")

    return fe_fund_xref


def save_ag_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.8
) -> None:
    """
    Load the ag_fund_matches dataframe to the database
    :return:
    """
    ag_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    ag_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "AG"
    ]
    ag_funds = (
        ag_funds_raw.copy()
        .drop_duplicates(subset="fund_name")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    ag_funds["clean_fund_name"] = (
        ag_funds["fund_name"]
        .str.replace(pat=ag_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    ag_funds["fe_fund_name"] = ag_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, cutoff)
    )
    matched_funds_ag = ag_funds[ag_funds.fe_fund_name != "No Match Found"]
    xref_matched_funds_ag = pd.merge(
        matched_funds_ag,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="left",
    )
    xref_seed_matched_ag_funds = xref_matched_funds_ag.loc[
        :, ["provider_code", "fund_code", "isin_code_y"]
    ].rename(columns={"isin_code_y": "fe_isin_code"})

    unmatched_funds_ag = ag_funds[ag_funds.fe_fund_name == "No Match Found"]
    xref_seed_unmatched_funds_ag = unmatched_funds_ag.copy().loc[
        :, ["provider_code", "fund_code", "fund_name", "clean_fund_name"]
    ]

    xref_seed_unmatched_funds_ag.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_ag_funds_unmatched.csv",
        index=False,
    )
    xref_seed_matched_ag_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_ag_funds_matched.csv",
        index=False,
    )

    return sys.stdout.write("\nAllan Gray (AG) Fund Matches saved to dbt seeds folder")


def save_mw_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.8
) -> None:
    mw_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    mw_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "MW"
    ]
    mw_funds = (
        mw_funds_raw.copy()
        .drop_duplicates(subset="fund_name")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    mw_funds["clean_fund_name"] = (
        mw_funds["fund_name"]
        .str.replace(pat=mw_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    mw_funds["fe_fund_name"] = mw_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, cutoff)
    )
    # step one: match funds by isin_code with master fe analytics feed
    matched_mw_isin_codes = pd.merge(
        mw_funds, fe_funds, left_on="isin_code", right_on="isin_code", how="inner"
    )
    matched_mw_isin_codes_final = (
        matched_mw_isin_codes.copy()
        .loc[:, ["provider_code", "fund_code", "isin_code"]]
        .rename(columns={"isin_code": "fe_isin_code"})
    )
    # step two: match funds not matched by isin_code by fund_name with master fe analytics feed
    unmatched_mw_isin_codes = mw_funds[
        ~mw_funds["fund_code"].isin(matched_mw_isin_codes["fund_code"])
    ]
    matched_mw_funds = unmatched_mw_isin_codes[
        unmatched_mw_isin_codes["fe_fund_name"] != "No Match Found"
    ]
    matched_mw_fund_name = pd.merge(
        matched_mw_funds,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="inner",
    )
    matched_mw_fund_name = matched_mw_fund_name.loc[
        :, ["provider_code", "fund_code", "isin_code_y"]
    ].rename(columns={"isin_code_y": "fe_isin_code"})
    xref_seed_matched_mw_funds = pd.concat(
        [matched_mw_isin_codes_final, matched_mw_fund_name]
    ).reset_index(drop=True)
    # step three: save unmatched funds to seeds folder
    unmatched_funds_mw = mw_funds[
        ~mw_funds["fund_code"].isin(xref_seed_matched_mw_funds["fund_code"])
    ]
    mw_psp_funds = unmatched_funds_mw[
        unmatched_funds_mw["clean_fund_name"].str.contains("(PSP)", regex=False)
    ]
    xref_mw_psp_funds = mw_psp_funds.loc[
        :, ["provider_code", "fund_code", "fund_name"]
    ].copy()

    unmatched_funds_mw = unmatched_funds_mw[
        ~unmatched_funds_mw["fund_code"].isin(mw_psp_funds["fund_code"])
    ].copy()
    xref_unmatched_funds_mw = unmatched_funds_mw.loc[
        :, ["provider_code", "fund_code", "fund_name", "clean_fund_name"]
    ].copy()
    # Final csv exports to seeds folder in dbt transform project
    xref_seed_matched_mw_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_mw_funds_matched.csv",
        index=False,
    )
    xref_mw_psp_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_mw_funds_psp.csv",
        index=False,
    )
    xref_unmatched_funds_mw.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_mw_funds_unmatched.csv",
        index=False,
    )

    return sys.stdout.write("\nMomentum (MW) Fund Matches saved to dbt seeds folder")


def save_gl_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.8
) -> None:
    gl_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    gl_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "GL"
    ]
    gl_funds = (
        gl_funds_raw.copy()
        .drop_duplicates(subset="fund_name")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    gl_funds["clean_fund_name"] = (
        gl_funds["fund_name"]
        .str.replace(pat=gl_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    gl_funds["fe_fund_name"] = gl_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, 0.775)
    )
    gl_funds

    matched_gl_isin_codes = pd.merge(
        gl_funds, fe_funds, left_on="isin_code", right_on="isin_code", how="inner"
    )
    matched_gl_isin_codes_final = (
        matched_gl_isin_codes.copy()
        .loc[:, ["provider_code", "fund_code", "isin_code"]]
        .rename(columns={"isin_code": "fe_isin_code"})
    )
    unmatched_gl_isin_codes = gl_funds[
        ~gl_funds["fund_code"].isin(matched_gl_isin_codes["fund_code"])
    ]

    matched_gl_funds = unmatched_gl_isin_codes[
        unmatched_gl_isin_codes["fe_fund_name"] != "No Match Found"
    ]
    matched_gl_fund_name = pd.merge(
        matched_gl_funds,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="inner",
    )
    matched_gl_fund_name = matched_gl_fund_name.loc[
        :, ["provider_code", "fund_code", "isin_code_y"]
    ].rename(columns={"isin_code_y": "fe_isin_code"})
    xref_seed_matched_gl_funds = pd.concat(
        [matched_gl_isin_codes_final, matched_gl_fund_name]
    ).reset_index(drop=True)

    unmatched_funds_gl = gl_funds[
        ~gl_funds["fund_code"].isin(xref_seed_matched_gl_funds["fund_code"])
    ]
    xref_unmatched_funds_gl = unmatched_funds_gl.loc[
        :, ["provider_code", "fund_code", "fund_name", "clean_fund_name"]
    ].copy()

    xref_seed_matched_gl_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_gl_funds_matched.csv",
        index=False,
    )
    xref_unmatched_funds_gl.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_gl_funds_unmatched.csv",
        index=False,
    )

    return sys.stdout.write(
        "\nGlacier Local (GL) Fund Matches saved to dbt seeds folder"
    )


def save_noip_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.85
) -> None:
    noip_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    noip_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "NOIP"
    ]
    noip_funds = (
        noip_funds_raw.copy()
        .drop_duplicates(subset="fund_code")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    noip_funds["clean_fund_name"] = (
        noip_funds["fund_name"]
        .str.replace(pat=noip_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    noip_funds["fe_fund_name"] = noip_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, cutoff)
    )

    matched_noip_funds = noip_funds[noip_funds.fe_fund_name != "No Match Found"]
    matched_noip_fund_name = pd.merge(
        matched_noip_funds,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="inner",
    )
    xref_seed_matched_noip_funds = matched_noip_fund_name.loc[
        :,
        ["provider_code", "fund_code", "isin_code_y", "fund_name_x"],
    ].rename(columns={"isin_code_y": "fe_isin_code"})
    xref_seed_matched_noip_funds = xref_seed_matched_noip_funds.reset_index(drop=True)

    unmatched_funds_noip = noip_funds[
        ~noip_funds["fund_code"].isin(xref_seed_matched_noip_funds["fund_code"])
    ]
    xref_unmatched_funds_noip = unmatched_funds_noip.loc[
        :,
        ["provider_code", "fund_code", "fund_name", "clean_fund_name", "fe_fund_name"],
    ].copy()

    xref_seed_matched_noip_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_noip_funds_matched"
        ".csv",
        index=False,
    )
    xref_unmatched_funds_noip.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_noip_funds_unmatched.csv",
        index=False,
    )

    return sys.stdout.write(
        "\nNinety One (NOIP) Fund Matches saved to dbt seeds folder"
    )


def save_gi_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.65
) -> None:
    gi_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    gi_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "GI"
    ]
    gi_funds = (
        gi_funds_raw.copy()
        .drop_duplicates(subset="fund_name")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    gi_funds["clean_fund_code"] = gi_funds["fund_code"].str.rstrip("N")
    gi_funds["clean_fund_name"] = (
        gi_funds["fund_name"]
        .str.replace(pat=gi_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    gi_funds["fe_fund_name"] = gi_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, cutoff)
    )

    matched_gi_isin_codes = pd.merge(
        gi_funds, fe_funds, left_on="isin_code", right_on="isin_code", how="inner"
    )
    matched_gi_isin_codes_final = (
        matched_gi_isin_codes.copy()
        .loc[:, ["provider_code", "fund_code", "clean_fund_code", "isin_code"]]
        .rename(columns={"isin_code": "fe_isin_code"})
    )
    unmatched_gi_isin_codes = gi_funds[
        ~gi_funds["fund_code"].isin(matched_gi_isin_codes["fund_code"])
    ]
    matched_gi_funds = unmatched_gi_isin_codes[
        unmatched_gi_isin_codes["fe_fund_name"] != "No Match Found"
    ]
    matched_gi_funds_name = pd.merge(
        matched_gi_funds,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="inner",
    )
    matched_gi_funds_name = (
        matched_gi_funds_name.copy()
        .loc[:, ["provider_code", "fund_code", "isin_code_y"]]
        .rename(columns={"isin_code_y": "fe_isin_code"})
    )
    xref_seed_matched_gi_funds = pd.concat(
        [matched_gi_isin_codes_final, matched_gi_funds_name]
    ).reset_index(drop=True)
    unmatched_funds_gi = gi_funds[
        ~gi_funds["fund_code"].isin(matched_gi_funds_name["fund_code"])
    ]
    xref_unmatched_funds_gi = unmatched_funds_gi.copy().loc[
        :, ["provider_code", "fund_code", "fund_name"]
    ]

    xref_seed_matched_gi_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_gi_funds_matched.csv",
        index=False,
    )
    xref_unmatched_funds_gi.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_gi_funds_unmatched.csv",
        index=False,
    )

    return sys.stdout.write(
        "\nGlacier International (GI) Fund Matches saved to dbt seeds folder"
    )


def save_mwi_fund_matches_to_seeds_folder(
    intermediate_fund_list: pd.DataFrame, fe_funds: pd.DataFrame, cutoff: float = 0.8
) -> None:
    mwi_fund_pattern = "\s(?:Funds\s.+|Fund\s.+|Fund)$"
    mwi_funds_raw = intermediate_fund_list[
        intermediate_fund_list["provider_code"] == "MWI"
    ]
    mwi_funds = (
        mwi_funds_raw.copy()
        .drop_duplicates(subset="fund_name")
        .reset_index(drop=True)
        .loc[
            :, ["provider_code", "isin_code", "fund_code", "fund_name", "fund_currency"]
        ]
    )
    mwi_funds["clean_fund_name"] = (
        mwi_funds["fund_name"]
        .str.replace(pat=mwi_fund_pattern, repl="", regex=True)
        .str.replace(" - ", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(" (end)", "", regex=False)
        .str.replace(" (End)", "", regex=False)
        .str.replace(" (END)", "", regex=False)
        .str.replace("(END)", "", regex=False)
        .str.replace(" (Parking)", "", regex=False)
        .str.replace(" {Exp} ", " ", regex=False)
        .str.replace(" {RF} ", " ", regex=False)
    )
    mwi_funds["fe_fund_name"] = mwi_funds["clean_fund_name"].apply(
        get_fund_match, args=(fe_funds, cutoff)
    )
    # step one: match funds by isin_code with master fe analytics feed
    matched_mwi_isin_codes = pd.merge(
        mwi_funds, fe_funds, left_on="isin_code", right_on="isin_code", how="inner"
    )
    matched_mwi_isin_codes_final = (
        matched_mwi_isin_codes.copy()
        .loc[:, ["provider_code", "fund_code", "isin_code"]]
        .rename(columns={"isin_code": "fe_isin_code"})
    )

    # step two: match funds not matched by isin_code by fund_name with master fe analytics feed
    unmatched_mwi_isin_codes = mwi_funds[
        ~mwi_funds["fund_code"].isin(matched_mwi_isin_codes["fund_code"])
    ]
    matched_mwi_funds = unmatched_mwi_isin_codes[
        unmatched_mwi_isin_codes["fe_fund_name"] != "No Match Found"
    ]
    matched_mwi_fund_name = pd.merge(
        matched_mwi_funds,
        fe_funds,
        left_on="fe_fund_name",
        right_on="clean_fund_name",
        how="inner",
    )
    matched_mwi_fund_name = matched_mwi_fund_name.loc[
        :, ["provider_code", "fund_code", "isin_code_y"]
    ].rename(columns={"isin_code_y": "fe_isin_code"})
    xref_seed_matched_mwi_funds = pd.concat(
        [matched_mwi_isin_codes_final, matched_mwi_fund_name]
    ).reset_index(drop=True)

    # step three: save unmatched funds to seeds folder
    unmatched_funds_mwi = mwi_funds[
        ~mwi_funds["fund_code"].isin(xref_seed_matched_mwi_funds["fund_code"])
    ]
    xref_unmatched_funds_mwi = unmatched_funds_mwi.loc[
        :, ["provider_code", "fund_code", "fund_name", "clean_fund_name"]
    ].copy()

    # Final csv exports to seeds folder in dbt transform project
    xref_seed_matched_mwi_funds.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_mwi_funds_matched.csv",
        index=False,
    )
    xref_unmatched_funds_mwi.to_csv(
        "/Users/azwerd/datadev/cgwm_dw_transform/seeds/seeds__xref_mwi_funds_unmatched.csv",
        index=False,
    )
    return sys.stdout.write(
        "\nMomentum Wealth International (MWI) Fund Matches saved to dbt seeds folder"
    )


if __name__ == "__main__":
    fund_xref = get_fund_xref()
    # combined_fund = get_table_from_dw(
    #     "intermediate__dfp_navs_rpt_combined", "dw_andrew_intermediate", engine
    # )
    # fe_local_funds = get_fund_analytics_local_fund_list()
    # fe_intl_funds = get_fund_analytics_intl_fund_list()
    # save_ag_fund_matches_to_seeds_folder(combined_fund, fe_local_funds)
    # save_mw_fund_matches_to_seeds_folder(combined_fund, fe_local_funds)
    # save_gl_fund_matches_to_seeds_folder(combined_fund, fe_local_funds)
    # save_noip_fund_matches_to_seeds_folder(combined_fund, fe_local_funds)
    # save_gi_fund_matches_to_seeds_folder(combined_fund, fe_intl_funds)
    # save_mwi_fund_matches_to_seeds_folder(combined_fund, fe_intl_funds)
