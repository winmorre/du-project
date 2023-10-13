import datetime

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pydantic import BaseModel

from .place_schema import PlaceSchema


class DispatchBase(BaseModel):
    account: int
    wasteBins: str
    location: PlaceSchema
    dispatchType: int


@dataclass
@dataclass_json
class DispatchCreate(DispatchBase):
    ...


@dataclass
@dataclass_json
class DispatchSchema(DispatchBase):
    id: int
    createdAt: datetime.datetime
    scheduledFor: datetime.datetime | None
    assignedTo: int | None
    fulfilled: bool
    zone: str
    fulfilledAt: datetime.datetime | None
    confirmedBy: int | None
    confirmedAt: datetime.datetime
    rescheduled: bool
    rescheduledBy: int | None
    rescheduledReason: str | None
    rescheduledAt: datetime.datetime
    fulfilledBy: int | None
    confirmedAt: datetime.datetime | None
    dispatchConfirmed: bool
    rescheduledAt: datetime.datetime | None
    cancelled: bool
    cancelledAt: datetime.datetime | None
    cancelledBy: int | None
    cancelledReason: str | None
    scheduled: bool
    assignedAt: datetime.datetime | None
    assigned: bool


@dataclass
@dataclass_json
class FulfilDispatch(BaseModel):
    fulfilledBy: int
    fulfilledAt: datetime.datetime | None


@dataclass
@dataclass_json
class RescheduleDispatch(BaseModel):
    rescheduleReason: str
    rescheduleBy: int


@dataclass
@dataclass_json
class CancelDispatch(BaseModel):
    reason: str
    cancelledBy: int
