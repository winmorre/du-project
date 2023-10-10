from dataclasses import dataclass
from dataclasses_json import dataclass_json
from sqlalchemy import Column, Integer, DateTime, String, JSON
from sqlalchemy.sql import func

from src.helpers.postgres_helpers import Base

BIN_STATUS = (
    ("EMPTY", 0),
    ("PARTIALLY_FULL", 1),
    ("FULL", 2),
)


@dataclass
@dataclass_json
class Bin(Base):
    __tablename__ = "bin"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    status = Column(Integer)
    location = Column(JSON)
    owners = Column(String)
    capacity = Column(Integer)  # this might represent the volume of the bin
    zone = Column(String)
    bin_id = Column(String)
