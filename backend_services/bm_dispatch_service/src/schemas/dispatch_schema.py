import datetime

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pydantic import BaseModel

from .place_schema import PlaceSchema


class DispatchBase(BaseModel):
    account: int
    waste_bins: str
    location: PlaceSchema
    dispatch_type: int


@dataclass
@dataclass_json
class DispatchCreate(DispatchBase):
    ...


@dataclass
@dataclass_json
class DispatchSchema(DispatchBase):
    id: int
    created_at: datetime.datetime
    scheduled_for: datetime.datetime | None
    assigned_to: int | None
    fulfilled: bool
    zone: str
    fulfilled_at: datetime.datetime | None
    confirmed_by: int | None
    rescheduled: bool
    rescheduled_by: int | None
    rescheduled_reason: str | None
    fulfilled_by: int | None
    confirmed_at: datetime.datetime | None
    dispatch_confirmed: bool
    rescheduled_at: datetime.datetime | None
    cancelled: bool
    cancelled_at: datetime.datetime | None
    cancelled_by: int | None
    cancelled_reason: str | None
