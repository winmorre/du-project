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
            dispatch = self._db.query(self._dispatch).get(self._dispatch.id == pk)
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
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
            if dispatch is None:
                raise Dispatch("Dispatch object with ID {} does not exist".format(pk))

            dispatch.location = location.asdict()
            self._db.commit()

            return dispatch
        except Exception:
            raise ("Error occurred while updated dispatch location")

    def set_dispatch_zone(self, pk, zone: str) -> Dispatch:
        """
        set_dispatch_zone
        Set the zone area that a dispatch is scheduled for
        :param pk
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
            if dispatch is None:
                raise DispatchError(f"Oooops!! dispatch object with ID {pk} does not exist")

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
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
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
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.assigned_to = assignee
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError(f"Could not assign dispatch with ID {pk}  to {assignee}")

    def fulfil_dispatch(self, pk: int, fulfilled_at: datetime.datetime) -> Dispatch:
        """
        fulfil_dispatch
        Marks dispatch as fulfilled which means waste has been picked by assignee
        :param pk
        :param fulfilled_at
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.fulfilled = True
            dispatch.fulfilled_at = fulfilled_at
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Ooops could not mark dispatch as fulfilled, pls try again")

    def confirm_dispatch_fulfilled(self, pk: int, confirm_by: int) -> Dispatch:
        """
        confirm_dispatch_fulfilled
        Confirms that a dispatch is truely fulfilled
        :param pk
        :param confirm_by
        :return: Dispatch
        """
        try:
            dispatch: Dispatch | None = self._db.query(self._dispatch).get(self._dispatch.id == pk)
            if dispatch is None:
                raise DispatchError(f"Ooops!! dispatch object with ID {pk} does not exist")

            dispatch.confirmed_by = confirm_by
            dispatch.dispatch_confirmed = True
            self._db.commit()
            return dispatch
        except Exception:
            raise DispatchError("Oooops!! Error occurred while confirming dispatch")

    def reschedule_dispatch(self, pk: int, reschedule_reason: str) -> Dispatch:
        ...

    def cancel_dispatch_request(self, pk: int, cancelled_at: datetime.datetime, cancelled_by: int,
                                cancel_reason: str) -> Dispatch:
        ...
