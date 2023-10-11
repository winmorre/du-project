from typing import Type, List

from sqlalchemy.orm import Session

from src.errors.bin_error import BinError
from src.models.bin import Bin
from src.schemas.bin_schema import BinSchema
from src.schemas.place_schema import PlaceSchema


class BinRepository:
    def __init__(self, db_session: Session, bin_model: Type[Bin]):
        self.db = db_session
        self.bin = bin_model

    def add_bin(self, payload: BinSchema) -> Bin:
        """
        Add a new bin
        :param payload
        :return:
        """
        try:
            new_bin = self.bin.from_dict(payload.asdict())
            self.db.add(new_bin)
            self.db.commit()
            self.db.refresh(new_bin)

            return new_bin

        except Exception:
            raise BinError("Error occurred while adding new bin")

    def update_bin_location(self, location: PlaceSchema, bin_id: int) -> Bin:
        """
        Update bin location
        :param location
        :param bin_id
        :return: Bin
        """
        try:
            waste_bin = self.db.query(self.bin).get(self.bin.id == bin_id)
            waste_bin.location = location.asdict()
            self.db.commit()

            return waste_bin
        except Exception:
            raise BinError("Error occurred while updating location of bin")

    def remove_bin(self, bin_id: int) -> Bin:
        """
        Use to delete waste bin
        :param bin_id
        :return Bin
        """
        try:
            waste_bin = self.db.query(self.bin).filter(self.bin.id == bin_id).delete(synchronize_session='auto')
            self.db.commit()
            return waste_bin
        except Exception:
            raise BinError(f"Oops!! error occurred while deleting bin with id: {bin_id}")

    def update_bin(self):
        ...

    def fetch_bin_detail(self, pk=None, bin_id=None) -> Bin:
        """
        Get bin details
        :param pk
        :param bin_id
        :return: Bin
        """
        try:
            if pk is None and bin_id is None:
                raise BinError("Specify any of pk or bin_id")

            if pk:
                return self.db.query(self.bin).get(self.bin.id == pk)
            elif bin_id:
                return self.db.query(self.bin).get(self.bin.bin_id == bin_id)

        except Exception:
            raise BinError("Could not fetch bin object")

    def fetch_all_bins(self) -> List[Type[Bin]]:
        """
        Fetch all Bins from db
        :return: List[Bin]
        """
        try:
            waste_bins = self.db.query(self.bin).all()
            return waste_bins
        except Exception:
            raise BinError("Error occurred while fetching all bin objects")

    def remove_bin_owner(self, bin_id: int, owner: int) -> Bin:
        """
        remove_bin_owner
        To un-assign an account ID associated with a bin
        :param bin_id
        :param owner
        :return: Bin
        """
        try:
            waste_bin: Bin | None = self.db.query(self.bin).get(self.bin.id == bin_id)
            if waste_bin is None:
                raise BinError("Bin object with id {} does not exist".format(bin_id))
            owners = waste_bin.owners.split(";")
            new_owners = list(filter(lambda n: int(n) != owner, owners))
            # remove bin if bin doesn't have any owner
            if len(new_owners) == 0:
                waste_bin.delete(synchronize_session='auto')
                self.db.commit()
                return waste_bin

            waste_bin.owners = new_owners
            self.db.commit()
            return waste_bin
        except Exception:
            raise BinError("Error occurred while removing bin owner")
