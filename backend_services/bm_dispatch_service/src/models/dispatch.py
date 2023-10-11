from enum import Enum

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from sqlalchemy import Column, Integer, DateTime, String, Boolean, JSON
from sqlalchemy.sql import func

from src.helpers.postgres_helpers import Base


class DispatchType(Enum):
    SUBSCRIPTION = 0
    ONE_TIME = 1
    PAY_AS_YOU_GO = 2


@dataclass
@dataclass_json
class Dispatch(Base):
    __tablename__ = "dispatch"

    id = Column(Integer, primary_key=True)
    account = Column(Integer)
    waste_bins = Column(String, nullable=False, name="wasteBins")  # semicolon seperated string list of bins
    created_at = Column(DateTime, server_default=func.now(), name="createdAt")
    scheduled_for = Column(DateTime, nullable=True, name="scheduledFor")
    assigned_to = Column(Integer, name="assignedTo", nullable=True)
    fulfilled = Column(Boolean, default=False)
    location = Column(JSON, nullable=False)
    dispatch_type = Column(Integer, name="dispatchType")
    zone = Column(String, nullable=True)
    fulfilled_at = Column(DateTime, nullable=True,name="fulfilledAt")
    # The ID of client that confirms the dispatch has been successful
    # Dispatch the is fulfilled and not confirm will auto confirm after two days. auto-confirm id will be 0000
    confirmed_by = Column(Integer, name="confirmedBy")
    dispatch_confirmed = Column(Boolean,default=False,name="dispatchConfirmed")
    rescheduled = Column(Boolean, default=False)
    rescheduled_by = Column(Integer, nullable=True, name="rescheduledBy")
    rescheduled_reason = Column(String, nullable=True, name="rescheduledReason")
    cancelled = Column(Boolean, default=False)
    cancel_reason = Column(String, nullable=True,name="cancelReason")
    cancelled_at = Column(DateTime, nullable=True,name="cancelledAt")
    cancelled_by = Column(Integer, nullable=True,name="cancelledBy")
