import datetime

from pydantic import BaseModel
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from .place_schema import PlaceSchema


class BinBase(BaseModel):
    location: PlaceSchema
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
    createdAt: datetime.datetime
    status: int
    zone: dict
    binId: str

    class Config:
        orm_mode = True
