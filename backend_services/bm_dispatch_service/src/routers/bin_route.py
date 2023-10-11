from fastapi import APIRouter, status

from src.factories.service_factory import ServiceFactory
from src.schemas.bin_schema import BinCreate
from src.schemas.place_schema import PlaceSchema
from src.models.bin import Bin
from src.schemas.error_response import ErrorResponse
from src.helpers import route_helpers as rh

BIN_SERVICE = ServiceFactory.create_bin_service()

bin_router = APIRouter(prefix="/bin")


@bin_router.post("/")
async def add_bin(payload: BinCreate):
    result: Bin | ErrorResponse = BIN_SERVICE.add_waste_bin(data=payload)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())

    return rh.route_success_response(content=result.asdict(), status_code=status.HTTP_201_CREATED)


@bin_router.get("")
def get_bin(pk=None, bin_id=None):
    result = BIN_SERVICE.get_bin_detail(pk=pk, bin_id=bin_id)

    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict(), status_code=status.HTTP_404_NOT_FOUND)

    return rh.route_success_response(content=result.asdict())


@bin_router.get("/")
def get_all_bins():
    results = BIN_SERVICE.get_all_bins()

    if rh.check_error_response_instance(results):
        return rh.route_error_response(detail=results.asdict())

    return rh.route_success_response(content=results.asdict())


@bin_router.delete("/{bin_id}")
def remove_bin(bin_id: int):
    result = BIN_SERVICE.remove_bin(bin_id=id)

    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())

    return rh.route_success_response(content=result.asdict())


@bin_router.patch("/{bin_id}")
def update_bin_location(bin_id: int, location: PlaceSchema):
    result = BIN_SERVICE.update_bin_location(bin_id=bin_id, location=location)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())

    return rh.route_success_response(content=result.asdict(), status_code=status.HTTP_201_CREATED)


@bin_router.post("/remove-bin-owner")
def remove_waste_bin_owner(bin_id=None, owner_id=None):
    result = BIN_SERVICE.remove_bin_owner(bin_id=bin_id, owner_id=owner_id)
    if rh.check_error_response_instance(result):
        return rh.route_error_response(detail=result.asdict())

    return rh.route_success_response(content=result.asdict())
