import datetime
import traceback
from typing import List, Type, Any

import structlog
from fastapi import BackgroundTasks

from src.models.dispatch import Dispatch
from src.schemas.dispatch_schema import (
    DispatchSchema,
    DispatchCreate,
    FulfilDispatch,
    RescheduleDispatch,
    CancelDispatch,
)
from src.repositories.dispatch_repository import DispatchRepository
from src.repositories.redis_repository import RedisRepository
from src.schemas.error_response import ErrorResponse
from src.errors.dispatch_error import DispatchError
from src.schemas.place_schema import PlaceSchema
from libs.id_gen import id_gen

Logger = structlog.getLogger(__name__)


class DispatchService:
    def __init__(self, dispatch_repo: DispatchRepository, redis_repo: RedisRepository):
        self._dispatch_repo = dispatch_repo
        self._redis_repo = redis_repo

    def create_dispatch_request(self, payload: DispatchCreate) -> Dispatch | ErrorResponse:
        """
        create_dispatch_request
        :param payload
        :return: Dispatch | ErrorResponse
        """
        try:
            new_dispatch: DispatchSchema = DispatchSchema.from_dict(payload.asdict())
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            new_dispatch.createdAt = now
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
            now = self._get_current_time()
            return self._dispatch_repo.assign_dispatch(pk=pk, assignee=assignee, assigned_at=now)
        except DispatchError as de:
            return ErrorResponse(
                title="Couldn't assign dispatch request",
                detail=(
                    "An error occurred while trying to assign dispatch request",
                    f"\n {de.args[0]}"
                )
            )

    def fulfil_dispatch(self, pk: int, payload: FulfilDispatch) -> Dispatch | ErrorResponse:
        """
        fulfil_dispatch
        Fulfil dispatch. This is done by the picker (s)
        :param pk
        :param payload
        :return: Dispatch | ErrorResponse
        """
        try:
            if payload.fulfilledAt is None:
                payload.fulfilledAt = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            return self._dispatch_repo.fulfil_dispatch(
                pk=pk,
                fulfilled_at=payload.fulfilledAt,
                fulfilled_by=payload.fulfilledBy,
            )
        except DispatchError as de:
            Logger.error("fulfil dispatch error",
                         pk=pk,
                         fulfilled_by=payload.fulfilledBy,
                         fulfilled_at=payload.fulfilledAt,
                         traceback=traceback,
                         )
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

    def reschedule_dispatch(self, pk: int, payload: RescheduleDispatch) -> Dispatch | ErrorResponse:
        """
        reschedule_dispatch
        Reschedule dispatch request
        :param pk
        :param payload
        :return: Dispatch | ErrorResponse
        """
        try:
            now = self._get_current_time()
            return self._dispatch_repo.reschedule_dispatch(
                pk=pk, reschedule_by=payload.rescheduleBy,
                reschedule_reason=payload.rescheduleReason,
                rescheduled_at=now,
            )
        except DispatchError as de:
            Logger.error("reschedule dispatch error", pk=pk, reschedule_by=payload.rescheduleBy,
                         reschedule_reason=payload.rescheduleReason, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't reschedule dispatch request",
                detail=(
                    "Error occurred while rescheduling dispatch request"
                    f"\n {de.args[0]}"
                )

            )

    def cancel_dispatch_request(self, pk: int, payload: CancelDispatch) -> Dispatch | ErrorResponse:
        """
        cancel dispatch request
        :param pk
        :param payload
        :return Dispatch | ErrorResponse
        """
        try:
            now = self._get_current_time()
            return self._dispatch_repo.cancel_dispatch_request(
                pk=pk,
                cancelled_by=payload.cancelledBy,
                cancel_reason=payload.reason,
                cancelled_at=now,
            )
        except DispatchError as de:
            Logger.error("cancel dispatch error", pk=pk, reason=payload.reason, cancelled_by=payload.cancelledBy,
                         traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't cancel dispatch request",
                detail=(
                    "Error occurred while trying to cancel dispatch request"
                    f"\n {de.args[0]}"
                )
            )

    async def get_scheduled_dispatches_by_zone(
        self, zone: str, tasks: BackgroundTasks
    ) -> list[Any] | list[Type[Dispatch]] | ErrorResponse:
        try:
            scheduled_dispatches = await self._redis_repo.get_item(item_id=zone)
            if scheduled_dispatches is not None:
                return [Dispatch.from_dict(s) for s in scheduled_dispatches]
            scheduled_dispatches = self._dispatch_repo.fetch_scheduled_dispatch_for_zone(zone=zone)
            if len(list(scheduled_dispatches)) > 0:
                as_list = [a.asdict() for a in scheduled_dispatches]
                tasks.add_task(self._redis_repo.set_item, item_id=zone, item=as_list)
            return list(scheduled_dispatches)
        except DispatchError as de:
            Logger.error("get scheduled request by zone error", zone=zone, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Could not get scheduled requests",
                detail=(
                    "Please cross the check the Zone ID provided"
                    f"\n {de.args[0]}"
                )
            )

    # we can also get scheduled request for a radius of area
    # that will mean we will need to change how we store locations

    async def get_scheduled_dispatches_by_assignee(
        self, assignee: int, tasks: BackgroundTasks
    ) -> list[Any] | list[Type[Dispatch]] | ErrorResponse:
        """
        Get all dispatches assigned to the assignee id
        :param assignee
        :param tasks
        :return: List[Dispatch] | ErrorResponse
        """
        try:
            dispatches = await self._redis_repo.get_item(item_id=str(assignee))
            if dispatches is not None:
                return [Dispatch.from_dict(d) for d in dispatches]

            dispatches = self._dispatch_repo.fetch_scheduled_dispatch_by_assignee(assignee=assignee)

            if len(list(dispatches)) > 0:
                as_list = [Dispatch.from_dict(d) for d in dispatches]
                tasks.add_task(self._redis_repo.set_item, item_id=str(assignee), item=as_list)

            return list(dispatches)
        except DispatchError as de:
            Logger.error("get dispatches by assignee error", assignee=assignee, traceback=traceback.format_exc())
            return ErrorResponse(
                title=f"Couldn't get dispatches assigned to {assignee}",
                detail=(
                    "Please try again later"
                    f"\n {de.args[0]}"
                )
            )

    def get_all_dispatches_for_zone(self, zone: str):
        try:
            return self._dispatch_repo.fetch_all_dispatches_for_zone(zone=zone)
        except DispatchError as de:
            Logger.error("get all dispatches for zone error", zone=zone, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't get all zonal dispatches",
                detail=(
                    "Error fetching zonal dispatches"
                    f"\n {de.args[0]}"
                )
            )

    def get_all_scheduled_dispatch(self):
        try:
            return self._dispatch_repo.fetch_all_scheduled_dispatch()
        except DispatchError as de:
            Logger.error("get all scheduled dispatch error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't fetch all scheduled dispatches",
                detail=(
                    "Error fetching all scheduled dispatches",
                    f"\n {de.args[0]}"
                )
            )

    def get_all_scheduled_dispatch_by_date(self, date):
        try:
            return self._dispatch_repo.fetch_all_scheduled_dispatch_by_date(date=date)
        except DispatchError as de:
            Logger.error("get all scheduled dispatch by date error", dated=date, traceback=traceback.format_exc())
            return ErrorResponse(
                title="",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_scheduled_dispatches_for_date_range(self, start, end=None):

        try:
            if not end:
                end = self._get_current_time()

            dispatches = self._dispatch_repo.fetch_all_scheduled_dispatches_for_date_range(start=start, end=end)
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all scheduled dispatches for date range", start=start,
                         end=end,
                         traceback=traceback.format_exc()
                         )
            return ErrorResponse(
                title="Couldn't fetch all scheduled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_dispatches_for_date_range(self, start, end):
        if not end:
            end = self._get_current_time()
        try:
            dispatch = self._dispatch_repo.fetch_all_dispatches_for_date_range(start=start, end=end)
            return list(dispatch)
        except DispatchError as de:
            Logger.error("get all dispatches for date range", start=start, end=end)
            return ErrorResponse(
                title="Couldn't get all dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_assigned_dispatches(self):
        try:
            dispatch = self._dispatch_repo.fetch_all_assigned_dispatches()
            return list(dispatch)
        except DispatchError as de:
            Logger.error("get all assigned dispatches", traceback=traceback.format_exc())

            return ErrorResponse(
                title="Get all assigned dispatches Error",
                detail=(
                    "Error occurred while trying to get all assigned dispatches"
                    f"{de.args[0]}"
                )
            )

    def get_fulfilled_dispatches(self):
        try:
            return self._dispatch_repo.fetch_fulfilled_dispatches()
        except DispatchError as de:
            Logger.error("get fulfilled dispatches error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't get all fulfilled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_fulfilled_dispatches_for_date_range(self, start, end=None):
        if not end:
            end = self._get_current_time()
        try:
            dispatches = self._dispatch_repo.fetch_all_fulfilled_dispatches_for_date_range(start=start, end=end)
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all fulfilled dispatches for date range error", start=start,
                         end=end,
                         traceback=traceback.format_exc(),
                         )
            return ErrorResponse(
                title="Couldn't get all fulfilled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_confirmed_fulfilled_dispatches(self):
        try:
            dispatches = self._dispatch_repo.fetch_all_confirmed_fulfilled_dispatches()
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all confirmed fulfilled dispatches", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't get all fulfilled dispatches",
                detail=(
                    "Error"
                    f"{de.args[0]}"
                )
            )

    def get_all_confirmed_fulfilled_dispatches_for_date_range(self, start, end=None):
        if not end:
            end = self._get_current_time()
        try:
            dispatches = self._dispatch_repo.fetch_all_confirmed_fulfilled_dispatches_for_date_range(
                start=start,
                end=end,
            )
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all confirmed fulfilled dispatches for date range error", start=start, end=end)
            return ErrorResponse(
                title="Could not get confirmed fulfilled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_cancelled_dispatches(self):
        try:
            dispatches = self._dispatch_repo.fetch_all_cancelled_dispatches()
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all cancelled dispatches error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_all_cancelled_dispatches_for_date_range(self, start: datetime.datetime, end=None):
        try:
            if not end:
                end = self._get_current_time()

            dispatches = self._dispatch_repo.fetch_all_cancelled_dispatches_for_date_range(start=start, end=end)
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get all cancelled dispatches for date range error", start=start, end=end)
            return ErrorResponse(
                title="Couldn't get all cancelled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_cancelled_dispatches_by_zone(self, zone):
        try:
            dispatches = self._dispatch_repo.fetch_all_cancelled_dispatches_for_zone(zone=zone)
            return list(dispatches)
        except DispatchError as de:
            Logger.error("get cancelled dispatch by zone error", zone=zone, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Couldn't get all cancelled dispatches by zone",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def get_cancelled_dispatches_by_zone_for_date_range(self, zone, start, end=None):
        if not end:
            end = self._get_current_time()
        try:
            dispatches = self._dispatch_repo.fetch_all_cancelled_dispatches_by_zone_for_date_range(
                zone=zone, start=start, end=end,
            )
            return list(dispatches)
        except DispatchError as de:
            Logger.error("cancelled dispatches error", zone=zone, start=start, end=end)
            return ErrorResponse(
                title="Couldn't get cancelled dispatches",
                detail=(
                    f"{de.args[0]}"
                )
            )

    def _get_current_time(self) -> datetime.datetime:
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)

    # assign dispatch
    # fetch available stuffs
