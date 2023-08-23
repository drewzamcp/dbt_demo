from sqlmodel import SQLModel, create_engine
from dotenv import dotenv_values

from data_load.models import models
from data_load.models import dfp_src_models
from data_load.models import mrd_src_models
from data_load.models import xref_src_models

config = dotenv_values()

pg_dev_dsn = config.get("PG_DEV_DBT_DSN")

engine = create_engine(pg_dev_dsn, echo=False)
