from datetime import datetime, date
from typing import Optional

from sqlmodel import Field, UniqueConstraint

from data_load.db.database import SQLModel


class XrefFundCodes(SQLModel, table=True):
    __tablename__ = "xref_src_fund_code_to_master_isin"
    __table_args__ = (
        UniqueConstraint(
            "provider_code",
            "fund_code",
            "master_isin",
            name="xref_funds_unique_constraint",
        ),
        {"schema": "dw_andrew_sources"},
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    provider_code: Optional[str]
    fund_code: Optional[str]
    master_isin: Optional[str]
    master_fund_name: Optional[str]
    last_updated: Optional[date] = Field(
        default_factory=datetime.utcnow, nullable=False
    )
