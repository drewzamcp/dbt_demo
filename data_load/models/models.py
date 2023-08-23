from typing import List, Optional
import uuid
from datetime import datetime, date

from sqlmodel import Field, Relationship, Date

from data_load.db.database import SQLModel


class Portfolio(SQLModel, table=True):
    __table_args__ = {'schema': 'dw_andrew_oltp'}

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: uuid.UUID = Field(default_factory=uuid.uuid4, index=True, unique=True, nullable=False)
    portfolio_code: str = Field(index=True, unique=True, max_length=10)
    portfolio_name: str = Field(index=True)
    description: str
    last_updated: Optional[date] = Field(default_factory=datetime.utcnow, nullable=False)
    is_active: bool = Field(default=True)

    investors: List['Investor'] = Relationship(back_populates="portfolio")


class Investor(SQLModel, table=True):
    __table_args__ = {'schema': 'dw_andrew_oltp'}

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: uuid.UUID = Field(default_factory=uuid.uuid4, index=True, unique=True, nullable=False)
    investor_name: str = Field(index=True)
    investor_lastname: Optional[str] = Field(index=True)
    investor_type: str
    id_ref: str = Field(index=True, unique=True, max_length=40)
    tax_ref: Optional[str]
    contact_no: Optional[str]
    email: Optional[str]
    occupation: Optional[str]
    region: Optional[str]
    is_active: bool = Field(default=True)
    last_updated: Optional[date] = Field(default_factory=datetime.utcnow, nullable=False)
    portfolio_id: Optional[int] = Field(default=None, foreign_key="dw_andrew_oltp.portfolio.id")

    portfolio: Optional[Portfolio] = Relationship(back_populates="investors")
