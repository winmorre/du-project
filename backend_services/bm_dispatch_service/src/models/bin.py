from dataclasses import dataclass
from dataclasses_json import dataclass_json
from sqlalchemy import Boolean, Column, Integer, DateTime, String, JSON

from src.helpers.postgres_helpers import Base

BIN_STATUS = (
    ("EMPTY", 0),
    ("PARTIALLY_FULL", 1),
    ("FULL", 2),
)


@dataclass
@dataclass_json
class Bin(Base):
    __tablename__ = "bins"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    rfid_tag = Column(String)
    barcode = Column(String)
    status = Column(Integer)
    location = Column(JSON)
    owner = Column(Integer)
    size = Column(Integer)  # this might represent the volume of the bin
    zone = Column(String)
    bin_id = Column(String)
