from datetime import datetime, date
from pydantic import condecimal
from sqlmodel import Field
from typing import Optional

from data_load.db.database import SQLModel


class MonthlyFundPerformance(SQLModel, table=True):
    __tablename__ = "mrd_src_monthly_fund_performance"
    __table_args__ = ({"schema": "dw_andrew_sources"},)
    id: Optional[int] = Field(default=None, primary_key=True)
    isin_code: Optional[str]
    fe_fund_name: Optional[str]
    fund_currency: Optional[str]
    one_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    six_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    one_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    two_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    five_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    seven_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_volatility: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    fund_size_millions: condecimal(max_digits=22, decimal_places=0) = Field(
        default=0, nullable=True
    )
    month_end: Optional[date]
    last_updated: Optional[date] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    src_file: Optional[str]


class CumulativeMonthlyFundPerformance(SQLModel, table=True):
    __tablename__ = "mrd_src_monthly_cumulative_fund_performance"
    __table_args__ = ({"schema": "dw_andrew_sources"},)
    id: Optional[int] = Field(default=None, primary_key=True)
    isin_code: Optional[str]
    fe_fund_name: Optional[str]
    fund_currency: Optional[str]
    one_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    six_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    ytd_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    one_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    two_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    five_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    seven_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_volatility: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    month_end: Optional[date]
    last_updated: Optional[date] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    src_file: Optional[str]


class MonthlyIndexPerformance(SQLModel, table=True):
    __tablename__ = "mrd_src_monthly_index_performance"
    __table_args__ = ({"schema": "dw_andrew_sources"},)
    id: Optional[int] = Field(default=None, primary_key=True)
    fe_index_name: Optional[str]
    index_currency: Optional[str]
    one_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    six_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    one_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    two_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    five_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    seven_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_volatility: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    month_end: Optional[date]
    last_updated: Optional[date] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    src_file: Optional[str]


class CumulativeMonthlyIndexPerformance(SQLModel, table=True):
    __tablename__ = "mrd_src_monthly_cumulative_index_performance"
    __table_args__ = ({"schema": "dw_andrew_sources"},)
    id: Optional[int] = Field(default=None, primary_key=True)
    fe_index_name: Optional[str]
    index_currency: Optional[str]
    one_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    six_month_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    ytd_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    one_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    two_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    five_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    seven_year_cumulative_performance: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    three_year_cumulative_volatility: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    month_end: Optional[date]
    last_updated: Optional[date] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
    src_file: Optional[str]
