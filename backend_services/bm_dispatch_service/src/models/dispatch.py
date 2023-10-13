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
    wasteBins = Column(String, nullable=False, name="wasteBins")  # semicolon seperated string list of bins
    createdAt = Column(DateTime, server_default=func.now(), name="createdAt")
    scheduledFor = Column(DateTime, nullable=True, name="scheduledFor")
    assignedTo = Column(Integer, name="assignedTo", nullable=True)
    fulfilled = Column(Boolean, default=False)
    location = Column(JSON, nullable=False)
    dispatchType = Column(Integer, name="dispatchType")
    zone = Column(String, nullable=True)
    fulfilledAt = Column(DateTime, nullable=True, name="fulfilledAt")
    # The ID of client that confirms the dispatch has been successful
    # Dispatch the is fulfilled and not confirm will auto confirm after two days. auto-confirm id will be 0000
    confirmedBy = Column(Integer, name="confirmedBy", nullable=True)
    confirmedAt = Column(DateTime, nullable=True, name="confirmedAt")
    dispatchConfirmed = Column(Boolean, default=False, name="dispatchConfirmed")
    rescheduled = Column(Boolean, default=False)
    rescheduledBy = Column(Integer, nullable=True, name="rescheduledBy")
    rescheduledReason = Column(String, nullable=True, name="rescheduledReason")
    rescheduledAt = Column(DateTime, nullable=True, name="rescheduledAt")
    cancelled = Column(Boolean, default=False)
    cancelledReason = Column(String, nullable=True, name="cancelReason")
    cancelledAt = Column(DateTime, nullable=True, name="cancelledAt")
    cancelledBy = Column(Integer, nullable=True, name="cancelledBy")
    fulfilledBy = Column(Integer, nullable=True, name="fulfilledBy")
    scheduled = Column(Boolean, default=False)
    assigned = Column(Boolean, default=False)
    assignedAt = Column(DateTime, nullable=True, name="assignedAt")
