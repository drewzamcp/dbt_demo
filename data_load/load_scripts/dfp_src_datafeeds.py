import datetime as dt
import io
import sys
from pathlib import Path

import msoffcrypto
import pandas as pd
from dotenv import dotenv_values

from data_load.db.database import engine
from data_load.load_scripts import mrd_src_data

config = dotenv_values()

DSN = config.get("PG_DEV_DBT_DSN")


def connect_to_db():
    try:
        return engine
    except Exception as e:
        print(e)
        return sys.stdout.write(f"Error Code {e}")


def get_raw_files(folder_path: Path, file_extension: str = "*.csv") -> list:
    if not any(folder_path.iterdir()):
        print("nothing here.")
        return sys.stdout.write("No raw_files to process")

    file_list: list = list(folder_path.glob(file_extension))
    return file_list


def open_excel_file(
    file: str, password: str = None, sheet: str | int | list = 0
) -> pd.DataFrame:
    temp = io.BytesIO()

    with open(file, "rb") as f:
        excel = msoffcrypto.OfficeFile(f)
        excel.load_key(password=password)
        excel.decrypt(temp)

    return pd.read_excel(temp, engine="openpyxl", parse_dates=True, sheet_name=sheet)


def clean_df_headers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataframe headers.
    :param df: dataframe to clean
    :return: cleaned dataframe
    """
    df.columns = df.columns.str.replace(" / ", "_", regex=False)
    df.columns = df.columns.str.replace(" ", "_", regex=False)
    df.columns = df.columns.str.replace("/", "_", regex=False)
    df.columns = df.columns.str.replace("(", "", regex=False)
    df.columns = df.columns.str.replace(")", "", regex=False)
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.rstrip(".")
    return df


def read_csv_to_pandas(
    file: str, sep="\t", threshold: int = 0, day_first=False
) -> pd.DataFrame:
    # sourcery skip: extract-method
    try:
        df = pd.read_csv(file, sep=sep, infer_datetime_format=True, dayfirst=day_first)
        # removed , engine="python" from pd.read_csv
        df = clean_df_headers(df)
        df = df.dropna(thresh=threshold)
        return df
    except UnicodeDecodeError as e:
        sys.stdout.write(f"Error Code {e}\n trying different encoding")
        df = pd.read_csv(file, sep=sep, infer_datetime_format=True, encoding="Latin-1")
        df = clean_df_headers(df)
        df = df.dropna(thresh=threshold)
        sys.stdout.write(f"File {file} read successfully")
        return df


def concat_files_to_dataframe(
    file_list: list, sep="\t", threshold: int = 0, day_first=False
) -> pd.DataFrame:
    """
    Concatenate a list of csv or xlsx files into a single dataframe.
    :param day_first: checks if day is first in date format
    :param file_list: list of csv files with full path
    :param sep: default is tab add "," for comma separated files etc...
    :param threshold: default 0 used to drop rows with missing column data above the threshold
    :return: DataFrame of concatenated csv files.
    """
    df_list = []
    for file in file_list:
        if file.suffix in [".csv", ".txt"]:
            df = read_csv_to_pandas(file, sep=sep, day_first=day_first)
            clean_df_headers(df)
        elif file.suffix == ".xlsx":
            # TODO: this section should maybe be split out
            if file.parent.parts[-3] == "gi":
                date_str = file.name.split(" ")[0]
                date = dt.datetime.strptime(date_str, "%Y%m%d")
                df = open_excel_file(file, password="CGWM001")
                df["nav_date"] = date
            else:
                df = pd.read_excel(file, parse_dates=True, engine="openpyxl")

        clean_df_headers(df)
        df = df.dropna(thresh=threshold)
        # df['src_file'] = file.name
        df_list.append(df)

    return pd.concat(df_list).reset_index(drop=True)


def clean_ag_navs(raw_files: list, sep=","):
    """
    Clean the AG Navs data prior to loading into DW. Loads raw cvs files into Dataframe
    for cleaning date formats, replacing nulls, etc.

    :param sep: standard csv separator
    :param raw_files: List of files to clean
    :return:
        Dataframe: ready for bulk insert into DW.
    """
    main_df = concat_files_to_dataframe(raw_files, sep=sep)
    date_cols = main_df.columns[[8, 14, 18, 22]]
    main_df[date_cols] = main_df[date_cols].apply(
        pd.to_datetime, infer_datetime_format=True, errors="coerce"
    )
    main_df[date_cols] = (
        main_df[date_cols].astype(object).where(main_df[date_cols].notnull(), None)
    )

    return main_df


def clean_ag_navs_single(file: Path, sep=","):
    """
    Clean the AG Navs data prior to loading into DW. Loads raw cvs files into Dataframe
    for cleaning date formats, replacing nulls, etc.

    :param file:
    :param sep: standard csv separator
    :param threshold: default 0 used to drop rows with missing column data above the threshold
    :return:
        Dataframe: ready for bulk insert into DW.
    """
    main_df = read_csv_to_pandas(file, sep=sep)
    date_cols = main_df.columns[[8, 14, 18, 22]]
    main_df[date_cols] = main_df[date_cols].apply(
        pd.to_datetime, infer_datetime_format=True, errors="coerce"
    )
    main_df[date_cols] = (
        main_df[date_cols].astype(object).where(main_df[date_cols].notnull(), None)
    )

    return main_df


def clean_gl_navs(raw_files: list, sep=","):
    """
    Clean the GL Navs data prior to loading into DW. Loads raw cvs files into Dataframe
    for cleaning date formats, replacing nulls, etc.

    :param sep: default is tab ','
    :param raw_files: List of files to clean
    :return: Dataframe: ready for bulk insert into DW.
    """
    main_df = concat_files_to_dataframe(raw_files, sep=sep)
    date_cols = main_df.columns[[7, 18, 21, 23, 33, 35, 38, 40]]
    main_df[date_cols] = main_df[date_cols].apply(
        pd.to_datetime, infer_datetime_format=True, errors="coerce"
    )
    main_df[date_cols] = (
        main_df[date_cols].astype(object).where(main_df[date_cols].notnull(), None)
    )

    return main_df


if __name__ == "__main__":
    conn = connect_to_db()
