import datetime

from fastapi import APIRouter, status

from src.factories.service_factory import ServiceFactory
from src.schemas.error_response import ErrorResponse
from src.helpers import route_helpers as rh
from src.schemas.dispatch_schema import DispatchCreate, FulfilDispatch, RescheduleDispatch
from src.schemas.place_schema import PlaceSchema
from src.models.dispatch import Dispatch

DISPATCH_SERVICE = ServiceFactory.create_dispatch_service()

dispatch_router = APIRouter(prefix="/dispatch")


@dispatch_router.post("/")
def create_dispatch_request(payload: DispatchCreate):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.create_dispatch_request(payload=payload)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict(), status_code=status.HTTP_201_CREATED)


@dispatch_router.get("/{pk}")
def get_dispatch_detail(pk: int):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.get_dispatch_request(pk=pk)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/")
def get_all_dispatch_requests():
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.get_all_dispatch_request()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.patch("/{pk}")
def update_dispatch_location(pk: int, location: PlaceSchema):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.update_dispatch_location(pk=pk, location=location)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("/schedule/{pk}")
def schedule_dispatch(pk: int):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.schedule_dispatch(pk=pk)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("{pk}/assign/{assignee}")
def assign_dispatch(pk: int, assignee: int):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.assign_dispatch(pk=pk, assignee=assignee)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("/fulfil/{pk}")
def fulfil_dispatch_request(pk: int, payload: FulfilDispatch):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.fulfil_dispatch(pk=pk, payload=payload)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("{pk}/confirm-fulfilled/{confirmed_by}")
def confirm_dispatch_fulfilled(pk: int, confirmed_by: int):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.confirm_dispatch_fulfilled(pk=pk, confirmed_by=confirmed_by)

    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("/reschedule/{pk}")
def reschedule_dispatch(pk: int, payload: RescheduleDispatch):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.reschedule_dispatch(pk=pk, payload=payload)

    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.post("/cancel/{pk}")
def cancel_dispatch_request(pk: int):
    result: Dispatch | ErrorResponse = DISPATCH_SERVICE.cancel_dispatch_request(pk=pk)

    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/scheduled-by-zone/{zone}")
async def get_scheduled_dispatches_by_zone(zone: str):
    result = await DISPATCH_SERVICE.get_scheduled_dispatches_by_zone(zone=zone)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/scheduled-by-assignee/{assignee}")
async def get_scheduled_dispatches_by_assignee(assignee: int):
    result = await DISPATCH_SERVICE.get_scheduled_dispatches_by_assignee(assignee=assignee)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/by-zone/{zone}")
def get_all_dispatches_for_zone(zone: str):
    result = DISPATCH_SERVICE.get_all_dispatches_for_zone(zone=zone)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/scheduled/")
def get_all_scheduled_dispatch():
    result = DISPATCH_SERVICE.get_all_scheduled_dispatch()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/by-date/{date}")
def get_all_scheduled_dispatch_by_date(date: datetime.datetime):
    result = DISPATCH_SERVICE.get_all_scheduled_dispatch_by_date(date=date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/scheduled/{start_date}")
def get_all_scheduled_dispatches_for_date_range(start_date: datetime.datetime, end_date: datetime.datetime | None):
    result = DISPATCH_SERVICE.get_all_scheduled_dispatches_for_date_range(start=start_date, end=end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/{start_date}")
def get_all_dispatches_for_date_range(start_date: datetime.datetime, end_date: datetime.datetime | None):
    result = DISPATCH_SERVICE.get_all_dispatches_for_date_range(start=start_date, end=end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/assigned/")
def get_all_assigned_dispatches():
    result = DISPATCH_SERVICE.get_all_assigned_dispatches()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/fulfilled/")
def get_fulfilled_dispatches():
    result = DISPATCH_SERVICE.get_fulfilled_dispatches()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/fulfilled/{start_date}")
def get_all_fulfilled_dispatches_for_date_range(start_date: datetime.datetime, end_date: datetime.datetime | None):
    result = DISPATCH_SERVICE.get_all_fulfilled_dispatches_for_date_range(start=start_date, end=end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/confirmed/")
def get_all_confirmed_fulfilled_dispatches():
    result = DISPATCH_SERVICE.get_all_confirmed_fulfilled_dispatches()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/confirmed/{start_date}")
def get_all_confirmed_fulfilled_dispatches_for_date_range(
    start_date: datetime.datetime, end_date: datetime.datetime | None
):
    result = DISPATCH_SERVICE.get_all_confirmed_fulfilled_dispatches_for_date_range(start=start_date, end=end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/cancelled/")
def get_all_cancelled_dispatches():
    result = DISPATCH_SERVICE.get_all_cancelled_dispatches()
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/cancelled/{start_date}")
def get_all_cancelled_dispatches_for_date_range(start_date: datetime.datetime,
                                                end_date: datetime.datetime | None = None):
    result = DISPATCH_SERVICE.get_all_cancelled_dispatches_for_date_range(start_date, end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/cancelled/{zone}/")
def get_cancelled_dispatches_by_zone(zone: str):
    result = DISPATCH_SERVICE.get_cancelled_dispatches_by_zone(zone=zone)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())


@dispatch_router.get("/cancelled/{zone}/{start_date}")
def get_cancelled_dispatches_by_zone_for_date_range(zone: str, start_date: datetime.datetime, end_date=None):
    result = DISPATCH_SERVICE.get_cancelled_dispatches_by_zone_for_date_range(zone=zone, start=start_date, end=end_date)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())
    return rh.route_success_response(content=result.asdict())
