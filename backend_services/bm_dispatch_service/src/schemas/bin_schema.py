import datetime

from pydantic import BaseModel
from dataclasses_json import dataclass_json
from dataclasses import dataclass


class BinBase(BaseModel):
    location: dict
    owner: str
    capacity: int


@dataclass
@dataclass_json
class BinCreate(BinBase):
    pass


@dataclass
@dataclass_json
class BinSchema(BinBase):
    id: int
    created_at: datetime.datetime
    status: int
    zone: dict
    bin_id: str

    class Config:
        orm_mode = True
