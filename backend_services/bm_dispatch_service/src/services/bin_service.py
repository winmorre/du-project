import datetime
import traceback
from typing import List, Type

import structlog

from src.repositories.bin_repository import BinRepository
from src.schemas.bin_schema import BinCreate, BinSchema
from src.schemas.error_response import ErrorResponse
from src.schemas.place_schema import PlaceSchema
from src.models.bin import BinStatus, Bin
from src.errors.bin_error import BinError
from libs.id_gen import id_gen

Logger = structlog.getLogger(__name__)


class BinService:
    def __init__(self, bin_repo: BinRepository):
        self._bin_repo = bin_repo

    def add_waste_bin(self, data: BinCreate) -> Bin | ErrorResponse:
        """
        Validate and add new bin
        :param data
        :return: Bin | ErrorResponse
        """
        try:
            validated_msgs = BinService._validate_add_bin_payload(data)
            if len(validated_msgs) > 0:
                return ErrorResponse(
                    title="validation failed",
                    detail="\n".join(validated_msgs)
                )

            payload: BinSchema = BinSchema.from_dict(data.asdict())
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc, microsecond=0)
            payload.id = id_gen.get_id()
            payload.created_at = now
            payload.status = BinStatus.EMPTY

            # determine the bin zone from the location. first need to determine
            # what we mean by zone and how we create them
            # Also need to determine the bin ID. rough ID is, we use the Zone(Which could be some letter) +
            # Some(generated unique number)
            new_waste_bin = self._bin_repo.add_bin(payload=payload)
            return new_waste_bin
        except BinError as be:
            Logger.error("create bin error", data=data.asdict(), traceback=traceback.format_exc())
            return ErrorResponse(
                title="create object error",
                detail=(
                    f"{be.args[0]}"
                )
            )

    def remove_bin(self, bin_id: int) -> bool | ErrorResponse:
        """
         Remove a bin from the db
        :param bin_id
        :return: bool | ErrorResponse
        """

        try:
            result = self._bin_repo.remove_bin(bin_id=bin_id)

            return result is not None
        except BinError as be:
            Logger.error("delete bin object error", bin_id=bin_id, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Delete object error",
                detail=(
                    f"Couldn't delete waste bin with ID: {bin_id}"
                    f"{be.args[0]}"
                )
            )

    def remove_bin_owner(self, bin_id, owner_id) -> bool | ErrorResponse:
        """
        Remove Owner from bin_owners list
        :param bin_id
        :param owner_id
        :return: bool | ErrorResponse
        """
        try:
            result = self._bin_repo.remove_bin_owner(bin_id=int(bin_id), owner=int(owner_id))
            return result is not None
        except BinError as be:
            Logger.error("remove bin owner error", bin_id=bin_id, owner_id=owner_id, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Partial object update error",
                detail=(
                    f"{be.args[0]}"
                )
            )

    def update_bin_location(self, bin_id, location: PlaceSchema):
        """
        Update the bin location
        :param bin_id
        :param location
        :return:
        """
        try:
            result: Bin = self._bin_repo.update_bin_location(bin_id=bin_id, location=location)
            return result
        except BinError as be:
            Logger.error("update bin location error", bin_id=bin_id, location=location,
                         traceback=traceback.format_exc())
            return ErrorResponse(
                title="Partial update object error",
                detail=(
                    "Could not update the location of this bin"
                    f"{be.args[0]}"
                )
            )

    def get_bin_detail(self, pk: int = None, bin_id: int = None) -> Bin | ErrorResponse:
        """
        Get bin detail with either primary key (pk) or the bin identifier (bin_id)
        :param pk
        :param bin_id
        :return: Bin | ErrorResponse
        """
        try:
            result = self._bin_repo.fetch_bin_detail(pk=pk, bin_id=bin_id)
            return result
        except BinError as be:
            Logger.error("get bin object error", bin_id=bin_id, pk=pk, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Get object error",
                detail=(
                    "Error getting the bin detail "
                    "Cross check the BinId specified" if bin_id is not None else ""
                                                                                 f"\n {be.args[0]}"
                )
            )

    def get_all_bins(self) -> List[Type[Bin]] | ErrorResponse:
        """
        Get all bin objects
        :return: List[Type[Bin]] | ErrorResponse
        """
        try:
            waste_bins = self._bin_repo.fetch_all_bins()
            return waste_bins
        except BinError as be:
            Logger.error("Get bin objects error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Get bin objects error",
                detail=(
                    "Error occurred while getting all waste bin data"
                    f"\n {be.args[0]}"
                )
            )

    @staticmethod
    def _validate_add_bin_payload(data: BinCreate):
        msgs = []
        if data.location is None or data.location.id is None:
            msg = (
                "You need to provide location of the bin."
                "Please, turn on the location on the location service on your device before registering a waste bin"
            )
            msgs.append(msg)

        if data.capacity is None or data.capacity == 0:
            msg = (
                "Please specify the capacity of your waste bin."
            )
            msgs.append(msg)

        return msgs
