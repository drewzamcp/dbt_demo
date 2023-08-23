import pandas as pd
import sys
from dotenv import dotenv_values
from pathlib import Path
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import DatabaseError
from sqlmodel import Session, select


from data_load.db.database import SQLModel, engine
from data_load.load_scripts.mrd_src_data import (
    load_fe_master_annualised_fund_performance,
)
from data_load.load_scripts.mrd_src_data import (
    load_fe_master_cumulative_fund_performance,
)
from data_load.load_scripts.mrd_src_data import (
    load_fe_master_cumulative_index_performance,
)
from data_load.load_scripts.mrd_src_data import load_fe_master_index_performance
from data_load.models import dfp_src_models
from data_load.models import mrd_src_models

config = dotenv_values()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# def select_portfolios():
#     with Session(engine) as session:
#         statement = select(Portfolio).where(Portfolio.is_active == True)
#         results = session.exec(statement)
#         for portfolio in results:
#             print(
#                 f"{portfolio.id}: {portfolio.portfolio_name} {portfolio.portfolio_code}"
#             )


def bulk_insert_model_rows(df: pd.DataFrame, model: SQLModel) -> None:
    """

    :rtype: None
    """
    try:
        import_dict = df.to_dict("records")
        session = Session(engine)
        session.bulk_insert_mappings(model, import_dict)
        session.commit()
        session.close()

    except (Exception, DatabaseError, UniqueViolation) as e:
        print(e)
        if UnboundLocalError:
            print(f"No data to insert {import_dict}")
        else:
            session.rollback()
            session.close()


def load_fund_performance_data():
    fund_perf_data = load_fe_master_annualised_fund_performance()
    if fund_perf_data.one_month_cumulative_performance.isna().sum() > 10:
        sys.stdout.write(
            f"Fund current month has {fund_perf_data.one_month_cumulative_performance.isna().sum()} "
            f"missing values\n"
        )
    else:
        bulk_insert_model_rows(fund_perf_data, mrd_src_models.MonthlyFundPerformance)


def load_cumulative_fund_performance_data():
    fund_perf_data = load_fe_master_cumulative_fund_performance()
    if fund_perf_data.one_month_cumulative_performance.isna().sum() > 10:
        sys.stdout.write(
            f"Fund current month has {fund_perf_data.one_month_cumulative_performance.isna().sum()} "
            f"missing values\n"
        )
    else:
        bulk_insert_model_rows(
            fund_perf_data, mrd_src_models.CumulativeMonthlyFundPerformance
        )


def load_index_performance_data():
    index_perf_data = load_fe_master_index_performance()
    if index_perf_data.one_month_cumulative_performance.isna().sum() > 1:
        sys.stdout.write(
            f"Index current month has {index_perf_data.one_month_cumulative_performance.isna().sum()} "
            f"missing values\n"
        )
    else:
        bulk_insert_model_rows(index_perf_data, mrd_src_models.MonthlyIndexPerformance)


def load_cumulative_index_performance_data():
    index_perf_data = load_fe_master_cumulative_index_performance()
    if index_perf_data.one_month_cumulative_performance.isna().sum() > 1:
        sys.stdout.write(
            f"Index current month has {index_perf_data.one_month_cumulative_performance.isna().sum()} "
            f"missing values\n"
        )
    else:
        bulk_insert_model_rows(
            index_perf_data, mrd_src_models.CumulativeMonthlyIndexPerformance
        )


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
