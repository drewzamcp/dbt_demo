# sourcery skip: aware-datetime-for-utc
from datetime import datetime, date
from pydantic import condecimal
from sqlalchemy import func, Column
from sqlmodel import Field, UniqueConstraint, DateTime
from typing import Optional

from data_load.db.database import SQLModel


class SrcBase(SQLModel):
    __table_args__ = {"schema": "dw_andrew_sources"}

    id: Optional[int] = Field(default=None, primary_key=True)
    modified: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


class AllanGrayNav(SrcBase, table=True):
    __tablename__ = "dfp_src_ag_navs"
    __table_args__ = (
        UniqueConstraint(
            "account_number", "price_date", "fund_name", name="ag_nav_unique_constraint"
        ),
        {"schema": "dw_andrew_sources"},
    )

    adviser_code: Optional[str]
    product: Optional[str]
    account_name: Optional[str]
    account_group: Optional[str]
    account_number: Optional[str]
    inception_date: Optional[date]
    fund_manager: Optional[str]
    fund_name: Optional[str]
    fund_code: Optional[str]
    initial_adviser_fees: Optional[condecimal(max_digits=22, decimal_places=4)] = Field(
        default=0
    )
    annual_adviser_fees: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    section_14_adviser_fee_renewal_date: Optional[date]
    monthly_debit_order: Optional[str]
    anuity_income_regular_withdrawal: Optional[str]
    anuity_income_regular_withdrawal_frequency: Optional[str]
    annuity_income_anniversary_date: Optional[date]
    account_fund_allocation: Optional[str]
    units: condecimal(max_digits=22, decimal_places=4) = Field(default=0, nullable=True)
    unit_price_cents_in_fund_currency: condecimal(
        max_digits=22, decimal_places=2
    ) = Field(default=0, nullable=True)
    price_date: Optional[date]
    fund_currency: Optional[str]
    market_value_in_fund_currency: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    exchange_rate: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    market_value_in_rands: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    annuity_revision_effective_month: Optional[str]
    net_capital_gain_or_loss: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    model_portfolio_name: Optional[str]
    dim_fee: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    ric_fee: condecimal(max_digits=22, decimal_places=4) = Field(
        default=0, nullable=True
    )
    group_ra_employer: Optional[str]


class GlacierLocalNav(SrcBase, table=True):
    __tablename__ = "dfp_src_gl_navs"
    __table_args__ = (
        UniqueConstraint(
            "contractnumber",
            "productcode",
            "jsecode",
            "amount",
            "holdingsdate",
            name="gl_nav_unique_constraint",
        ),
        {"schema": "dw_andrew_sources"},
    )

    housecode: Optional[str]
    brokercode: Optional[str]
    title: Optional[str]
    initials: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    id_number_or_registration_number: Optional[str]
    generatedatetime: Optional[date]
    contractnumber: Optional[str]
    product: Optional[str]
    productcode: Optional[str]
    aum: condecimal(max_digits=22, decimal_places=2) = Field(default=0, nullable=True)
    jsecode: Optional[str]
    fundname: Optional[str]
    currency: Optional[str]
    amount: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    units: condecimal(max_digits=22, decimal_places=2) = Field(default=0, nullable=True)
    unitprice: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    pricedate: Optional[date]
    exrate: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    model_portfolio_code: Optional[str]
    product_inception_date: Optional[date] = Field(default=None, nullable=True)
    unrealised_cgt_amount: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    holdingsdate: Optional[date]
    fund_type: Optional[str]
    bda_number: Optional[str]
    share_provider: Optional[str]
    producttype: Optional[str]
    housename: Optional[str]
    broker_first_name: Optional[str]
    broker_surname: Optional[str]
    contribution_amount: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    contribution_frequency: Optional[str]
    contribution_next_due_date: Optional[date] = Field(default=None, nullable=True)
    contribution_escalation_percentage: Optional[str]
    contribution_escalation_date: Optional[str]
    income_amount_gross: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    income_frequency: Optional[str]
    income_next_due_date: Optional[date] = Field(default=None, nullable=True)
    income_escalation_percentage: Optional[str]
    income_escalation_date: Optional[date] = Field(default=None, nullable=True)
    broker_fee: condecimal(max_digits=5, decimal_places=2) = Field(
        default=0, nullable=True
    )
    broker_fee_split_percentage: condecimal(max_digits=6, decimal_places=2) = Field(
        default=0, nullable=True
    )
    offshore_indicator: Optional[str]
    isin_code: Optional[str]
    rand_base_cost: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    currency_base_cost: condecimal(max_digits=22, decimal_places=2) = Field(
        default=0, nullable=True
    )
    model_description: Optional[str]
    primary_intermediary: Optional[str]
