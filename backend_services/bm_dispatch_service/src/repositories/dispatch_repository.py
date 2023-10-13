import datetime
from typing import Type, List
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_

from src.models.dispatch import Dispatch
from src.schemas.dispatch_schema import DispatchSchema
from src.errors.dispatch_error import DispatchError
from src.schemas.place_schema import PlaceSchema

TRUTHY = True


class DispatchRepository:
    def __init__(self, db_session: Session, dispatch_model: Type[Dispatch]):
        self._db = db_session
        self._dispatch = dispatch_model

    def create_dispatch(self, payload: DispatchSchema) -> Dispatch:
        """
        create_dispatch
        Add dispatch to db
        :param payload
        :return: Dispatch
        """
        try:
            new_dispatch = self._dispatch.from_dict(payload.asdict())
            self._db.add(new_dispatch)
            self._db.commit()
            self._db.refresh(new_dispatch)

            return new_dispatch
        except Exception:
            raise DispatchError("Error occurred while creating dispatch")

    def fetch_dispatch(self, pk: int) -> Dispatch:
        """
        fetch_dispatch
        Fetch dispatch by dispatch id
        :param pk
        :return: Dispatch
        """
        try:
            dispatch = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise Dispatch("Dispatch object with ID {} does not exist".format(pk))
            return dispatch
        except Exception:
            raise DispatchError("Error occurred fetching dispatch with ID: {}".format(pk))

    def fetch_all_dispatches(self) -> List[Type[Dispatch]]:
        """
        fetch_all_dispatches
        Fetch all dispatch from db. Paginate the fetch and sets a limit on returned data
        :return: List[Type[Dispatch]]
        """
        try:
            dispatches = self._db.query(self._dispatch).all()
            return dispatches
        except Exception:
            raise DispatchError("Ooops!! Error occurred while fetching all dispatches")

    def update_dispatch(self, pk: int, payload):
        ...

    def update_dispatch_location(self, pk, location: PlaceSchema) -> Dispatch:
        """
        update_dispatch_location
        Updates the location of the dispatch request
        :param pk
        :param location
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise Dispatch("Dispatch object with ID {} does not exist".format(pk))

            dispatch.location = location.asdict()
            self._db.commit()

            return dispatch
        except Exception:
            raise DispatchError("Error occurred while updated dispatch location")

    def set_dispatch_zone(self, pk, zone: str) -> Dispatch:
        """
        set_dispatch_zone
        Set the zone area that a dispatch is scheduled for
        :param pk
        :param zone
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.zone = zone
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Error occurred while setting zone for dispatch with ID {pk}")

    def schedule_dispatch(self, pk: int, schedule_at: datetime.datetime) -> Dispatch:
        """
        schedule_dispatch
        Set the date and time that a dispatch is schedule for
        :param pk
        :param schedule_at
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.scheduledFor = schedule_at
            dispatch.scheduled = True
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Ooops!! could not set schedule date for dispatch with id {pk}")

    def assign_dispatch(self, pk, assignee: int, assigned_at: datetime.datetime) -> Dispatch:
        """
        assign_dispatch
        Assign someone to a dispatch
        :param pk
        :param assignee
        :param assigned_at
        :return Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.assignedTo = assignee
            dispatch.assignedAt = assigned_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Could not assign dispatch with ID {pk}  to {assignee}")

    def fulfil_dispatch(self, pk: int, fulfilled_at: datetime.datetime, fulfilled_by: int) -> Dispatch:
        """
        fulfil_dispatch
        Marks dispatch as fulfilled which means waste has been picked by assignee
        :param pk
        :param fulfilled_at
        :param fulfilled_by
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.fulfilled = True
            dispatch.fulfilledAt = fulfilled_at
            dispatch.fulfilledBy = fulfilled_by
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Ooops could not mark dispatch as fulfilled, pls try again")

    def confirm_dispatch_fulfilled(self, pk: int, confirm_by: int, confirmed_at: datetime.datetime) -> Dispatch:
        """
        confirm_dispatch_fulfilled
        Confirms that a dispatch is truely fulfilled
        :param pk
        :param confirm_by
        :param confirmed_at
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.confirmedBy = confirm_by
            dispatch.dispatchConfirmed = True
            dispatch.confirmedAt = confirmed_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Oooops!! Error occurred while confirming dispatch")

    def reschedule_dispatch(
        self, pk: int, reschedule_reason: str, reschedule_by: int, rescheduled_at: datetime.datetime,
    ) -> Dispatch:
        """
        reschedule_dispatch
        Reschedule a dispatch request
        :param pk
        :param reschedule_reason
        :param reschedule_by
        :param rescheduled_at
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.rescheduled = True
            dispatch.rescheduledReason = reschedule_reason
            dispatch.rescheduledBy = reschedule_by
            dispatch.rescheduledAt = rescheduled_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Error occurred while rescheduling dispatch with ID {pk}")

    def cancel_dispatch_request(self, pk: int, cancelled_at: datetime.datetime, cancelled_by: int,
                                cancel_reason: str) -> Dispatch:
        """
        cancel_dispatch_request
        Cancel a dispatch request
        :param pk
        :param cancelled_at
        :param cancel_reason
        :param cancelled_by
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.cancelled = True
            dispatch.cancelledReason = cancel_reason
            dispatch.cancelledBy = cancelled_by
            dispatch.cancelledAt = cancelled_at

            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Error occurred while trying to cancel dispatch")

    def fetch_scheduled_dispatch_for_zone(self, zone: str) -> Query[Type[Dispatch]]:
        """
        Fetch all scheduled request that has not been fulfilled or cancelled for a zone
        :param zone
        :return: filter
        """
        try:
            dispatches = self._db.query(self._dispatch).filter(
                and_(
                    self._dispatch.zone == zone,
                    self._dispatch.scheduled == TRUTHY,
                )
            )
            return dispatches
        except Exception:
            raise DispatchError(f"Error occurred fetching dispatches for zone {zone}")

    def fetch_scheduled_dispatch_by_assignee(self, assignee: int) -> Query[Type[Dispatch]]:
        try:
            return self._db.query(self._dispatch).filter(
                and_(self._dispatch.assignedTo == assignee,
                     self._dispatch.scheduled == TRUTHY),
            )
        except Exception:
            raise DispatchError(f"Could not fetch dispatches assigned to {assignee}")

    def fetch_all_dispatches_for_zone(self, zone: str):
        try:
            return self._db.query(self._dispatch).get(self._dispatch.zone == zone)
        except Exception:
            raise DispatchError(f"Could fetch all dispatches for zone {zone}")

    def fetch_all_scheduled_dispatch(self) -> List[Type[Dispatch]]:
        try:
            return self._db.query(self._dispatch).get(self._dispatch.scheduled == TRUTHY)
        except Exception:
            raise DispatchError("Couldn't fetch all scheduled dispatches")

    def fetch_all_scheduled_dispatch_by_date(self, date: datetime.datetime):
        try:
            return self._db.query(self._dispatch).filter(
                and_(
                    self._dispatch.scheduled == TRUTHY,
                    self._dispatch.scheduledFor == date,
                )
            )
        except Exception:
            raise DispatchError(f"Couldn't fetch all scheduled dispatches for {date}")

    def fetch_all_scheduled_dispatches_for_date_range(self, start: datetime.datetime, end: datetime.datetime):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.scheduled == TRUTHY,
                and_(self._dispatch.scheduledFor >= start, self._dispatch.scheduledFor <= end)
            ))
        except Exception:
            raise DispatchError(f"Couldn't fetch all dispatches for specified date range {start} to {end}")

    def fetch_all_dispatches_for_date_range(self, start: datetime.datetime, end: datetime.datetime):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.createdAt >= start,
                self._dispatch.createdAt <= end,
            ))
        except Exception:
            raise DispatchError(f"Couldn't fetch dispatches for specified date range {start} to {end}")

    def fetch_all_assigned_dispatches(self):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.assigned == TRUTHY
            ))
        except Exception:
            raise DispatchError("Couldn't fetch all assigned dispatches")

    def fetch_fulfilled_dispatches(self):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.fulfilled == TRUTHY
            ))
        except Exception:
            raise DispatchError("Couldn't fetch all fulfilled dispatches")

    def fetch_all_fulfilled_dispatches_for_date_range(self, start: datetime.datetime, end: datetime.datetime):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.fulfilled == TRUTHY,
                and_(
                    self._dispatch.fulfilledAt >= start,
                    self._dispatch.fulfilledAt <= end,
                )
            ))
        except Exception:
            raise DispatchError(f"Couldn't fetch all fulfilled dispatches for date range {start} to {end}")

    def fetch_all_confirmed_fulfilled_dispatches(self):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.dispatchConfirmed == TRUTHY
            ))
        except Exception:
            raise DispatchError("Couldn't fetch all confirmed fulfilled dispatches")

    def fetch_all_confirmed_fulfilled_dispatches_for_date_range(self, start: datetime.datetime, end: datetime.datetime):
        try:
            return self._db.query(self._dispatch).filter(and_(
                self._dispatch.dispatchConfirmed == TRUTHY,
                and_(
                    self._dispatch.confirmedAt >= start,
                    self._dispatch.confirmedAt <= end,
                )
            ))
        except Exception:
            raise DispatchError(f"Couldn't fetch all confirmed fulfilled dispatches for date range {start} to {end}")

    def fetch_all_cancelled_dispatches(self):
        try:
            return self._db.query(self._dispatch).filter(
                and_(self._dispatch.cancelled == TRUTHY)
            )
        except Exception:
            raise DispatchError("Couldn't fetch all cancelled dispatches")

    def fetch_all_cancelled_dispatches_for_zone(self, zone: str):
        try:
            return self._db.query(self._dispatch).filter(
                and_(self._dispatch.zone == zone, self._dispatch.cancelled == TRUTHY)
            )
        except Exception:
            raise DispatchError("Couldn't get all cancelled dispatches")

    def fetch_all_cancelled_dispatches_by_zone_for_date_range(self, zone: str, start, end):
        try:
            return self._db.query(self._dispatch).filter(
                and_(
                    self._dispatch.cancelled == TRUTHY,
                    self._dispatch.zone == zone,
                    and_(
                        self._dispatch.cancelledAt >= start,
                        self._dispatch.cancelledAt <= end,
                    )
                )
            )
        except Exception:
            raise DispatchError("Couldn't fetch all cancelled dispatches")

    def fetch_all_cancelled_dispatches_for_date_range(self, start, end):
        try:
            return self._db.query(self._dispatch).filter(
                and_(self._dispatch.cancelled == TRUTHY, and_(
                    self._dispatch.cancelledAt >= start,
                    self._dispatch.cancelledAt <= end,
                ))
            )
        except Exception:
            raise DispatchError("Couldn't fetch dispatches")

    def _get_dispatch_by_id(self, pk) -> Dispatch | None:
        return self._db.query(self._dispatch).get(self._dispatch.id == pk)
