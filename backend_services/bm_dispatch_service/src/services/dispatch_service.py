import datetime
import traceback
from typing import List, Type

import structlog

from src.models.dispatch import Dispatch
from src.schemas.dispatch_schema import DispatchSchema, DispatchCreate
from src.repositories.dispatch_repository import DispatchRepository
from src.schemas.error_response import ErrorResponse
from src.errors.dispatch_error import DispatchError
from src.schemas.place_schema import PlaceSchema
from libs.id_gen import id_gen

Logger = structlog.getLogger(__name__)


class DispatchService:
    def __init__(self, dispatch_repo: DispatchRepository):
        self._dispatch_repo = dispatch_repo

    def create_dispatch_request(self, payload: DispatchCreate) -> Dispatch | ErrorResponse:
        """
        create_dispatch_request
        :param payload
        :return: Dispatch | ErrorResponse
        """
        try:
            new_dispatch: DispatchSchema = DispatchSchema.from_dict(payload.asdict())
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            new_dispatch.created_at = now
            new_dispatch.id = id_gen.get_id()

            return self._dispatch_repo.create_dispatch(payload=new_dispatch)
        except DispatchError as de:
            Logger.error("create dispatch error", payload=payload.asdict(), traceback=traceback.format_exc())
            return ErrorResponse(
                title="Create dispatch object error",
                detail=(
                    "Could not create dispatch request."
                    f"\n {de.args[0]}"
                )
            )

    def get_dispatch_request(self, pk: int) -> Dispatch | ErrorResponse:
        """
        get_dispatch_request
        Get dispatch request details
        :param pk
        :return: Dispatch | ErrorResponse
        """
        try:
            return self._dispatch_repo.fetch_dispatch(pk=pk)
        except DispatchError as de:
            Logger.error("get dispatch error", pk=pk, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Get dispatch request error",
                detail=(
                    "Could not get dispatch request detail"
                    f"\n {de.args[0]}"
                )
            )

    def get_all_dispatch_request(self) -> List[Type[Dispatch]] | ErrorResponse:
        """
        :return: List[Type[Dispatch]] | ErrorResponse
        """
        try:
            return self._dispatch_repo.fetch_all_dispatches()
        except DispatchError as de:
            Logger.error("get all dispatch error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Could not get all dispatch request",
                detail=(
                    "An error occurred while trying to fetch all dispatch requests"
                    f"\n {de.args[0]}"
                )
            )

    def update_dispatch_location(self, location: PlaceSchema, pk: int) -> Dispatch | ErrorResponse:
        """
        update_dispatch_location
        Update dispatch location
        :param location
        :param pk
        :return: Dispatch |  ErrorResponse
        """
        try:
            return self._dispatch_repo.update_dispatch_location(pk=pk, location=location)
        except DispatchError as de:
            Logger.error("update dispatch location error", pk=pk, location=location, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't update dispatch request's location",
                detail=(
                    "While trying to update the location of the dispatch request, an error occurred",
                    f"\n {de.args[0]}"
                )
            )

    def schedule_dispatch(self, pk: int) -> Dispatch | ErrorResponse:
        """
        schedule_dispatch
        Schedule dispatch
        :param pk
        :return Dispatch | ErrorResponse
        """
        try:
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            return self._dispatch_repo.schedule_dispatch(pk=pk, schedule_at=now)
        except DispatchError as de:
            Logger.error("schedule dispatch error", pk=pk, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't schedule dispatch request",
                detail=(
                    "While trying to schedule the dispatch, and Error Occurred",
                    f"\n {de.args[0]}"
                )
            )

    def assign_dispatch(self, pk: int, assignee: int) -> Dispatch | ErrorResponse:
        """
        assign_dispatch
        Assign dispatch request
        :param pk
        :param assignee
        :return: Dispatch | ErrorResponse
        """
        try:
            return self._dispatch_repo.assign_dispatch(pk=pk, assignee=assignee)
        except DispatchError as de:
            return ErrorResponse(
                title="Couldn't assign dispatch request",
                detail=(
                    "An error occurred while trying to assign dispatch request",
                    f"\n {de.args[0]}"
                )
            )

    def fulfil_dispatch(self, pk: int, fulfilled_by: int, fulfilled_at=None) -> Dispatch | ErrorResponse:
        """
        fulfil_dispatch
        Fulfil dispatch. This is done by the picker (s)
        :param pk
        :param fulfilled_at
        :param fulfilled_by
        :return: Dispatch | ErrorResponse
        """
        try:
            if fulfilled_at is None:
                fulfilled_at = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            return self._dispatch_repo.fulfil_dispatch(pk=pk, fulfilled_at=fulfilled_at, fulfilled_by=fulfilled_by)
        except DispatchError as de:
            Logger.error("fulfil dispatch error", pk=pk, fulfilled_by=fulfilled_by, fulfilled_at=fulfilled_at,
                         traceback=traceback)
            return ErrorResponse(
                title="Couldn't fulfil dispatch",
                detail=(
                    "Error occurred while trying to fulfil dispatch request",
                    f"\n {de.args[0]}"
                )
            )

    def confirm_dispatch_fulfilled(self, pk: int, confirmed_by: int) -> Dispatch | ErrorResponse:
        """
        confirm_dispatch_fulfilled
        Confirm that a dispatch request has truely been fulfilled
        :param pk
        :param confirmed_by
        :return: Dispatch | ErrorResponse
        """
        try:
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            return self._dispatch_repo.confirm_dispatch_fulfilled(pk=pk, confirm_by=confirmed_by, confirmed_at=now)
        except DispatchError as de:
            Logger.error("confirm dispatch error", pk=pk, confirmed_by=confirmed_by, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't confirm fulfilment of dispatch",
                detail=(
                    "Error occurred while trying to confirm dispatch fulfilment"
                    "Please try again"
                    f"\n {de.args[0]}"
                )
            )

    def reschedule_dispatch(self, pk: int, reschedule_reason: str, reschedule_by: int) -> Dispatch | ErrorResponse:
        """
        reschedule_dispatch
        Reschedule dispatch request
        :param pk
        :param reschedule_reason
        :param reschedule_by
        :return: Dispatch | ErrorResponse
        """
        try:
            now = self._get_current_time()
            return self._dispatch_repo.reschedule_dispatch(pk=pk, reschedule_by=reschedule_by,
                                                           reschedule_reason=reschedule_reason, rescheduled_at=now)
        except DispatchError as de:
            Logger.error("reschedule dispatch error", pk=pk, reschedule_by=reschedule_by,
                         reschedule_reason=reschedule_reason, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't reschedule dispatch request",
                detail=(
                    "Error occurred while rescheduling dispatch request"
                    f"\n {de.args[0]}"
                )

            )

    def cancel_dispatch_request(self, pk: int, reason: str, cancelled_by: int) -> Dispatch | ErrorResponse:
        """
        cancel dispatch request
        :param pk
        :param reason
        :param cancelled_by
        :return Dispatch | ErrorResponse
        """
        try:
            now = self._get_current_time()
            return self._dispatch_repo.cancel_dispatch_request(pk=pk, cancelled_by=cancelled_by, cancel_reason=reason,
                                                               cancelled_at=now)
        except DispatchError as de:
            Logger.error("cancel dispatch error", pk=pk, reason=reason, cancelled_by=cancelled_by,
                         traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't cancel dispatch request",
                detail=(
                    "Error occurred while trying to cancel dispatch request"
                    f"\n {de.args[0]}"
                )
            )

    def _get_current_time(self) -> datetime.datetime:
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
