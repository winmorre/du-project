from typing import Type

from sqlalchemy.orm import Session

from src.errors.bin_error import BinError
from src.models.bin import Bin
from src.schemas.bin_schema import BinSchema


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

    def update_bin_location(self, location: dict, bin_id: int) -> Bin:
        """
        Update bin location
        :param location
        :param bin_id
        :return Bin
        """
        try:
            waste_bin = self.db.query(self.bin).get(self.bin.id == bin_id)
            waste_bin.location = location
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
