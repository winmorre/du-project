import datetime
from typing import Type, List
from sqlalchemy.orm import Session

from src.models.dispatch import Dispatch
from src.schemas.dispatch_schema import DispatchSchema
from src.errors.dispatch_error import DispatchError
from src.schemas.place_schema import PlaceSchema


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

            dispatch.scheduled_for = schedule_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Ooops!! could not set schedule date for dispatch with id {pk}")

    def assign_dispatch(self, pk, assignee: int) -> Dispatch:
        """
        assign_dispatch
        Assign someone to a dispatch
        :param pk
        :param assignee
        :return Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.assigned_to = assignee
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
            dispatch.fulfilled_at = fulfilled_at
            dispatch.fulfilled_by = fulfilled_by
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

            dispatch.confirmed_by = confirm_by
            dispatch.dispatch_confirmed = True
            dispatch.confirmed_at = confirmed_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Oooops!! Error occurred while confirming dispatch")

    def reschedule_dispatch(self, pk: int, reschedule_reason: str, reschedule_by: int,
                            rescheduled_at: datetime.datetime) -> Dispatch:
        """
        reschedule_dispatch
        Reschedule a dispatch request
        :param pk
        :param reschedule_reason
        :param reschedule_by
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._get_dispatch_by_id(pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.rescheduled = True
            dispatch.rescheduled_reason = reschedule_reason
            dispatch.rescheduled_by = reschedule_by
            dispatch.rescheduled_at = rescheduled_at
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
            dispatch.cancel_reason = cancel_reason
            dispatch.cancelled_by = cancelled_by
            dispatch.cancelled_at = cancelled_at

            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Error occurred while trying to cancel dispatch")

    def _get_dispatch_by_id(self, pk) -> Dispatch | None:
        return self._db.query(self._dispatch).get(self._dispatch.id == pk)
