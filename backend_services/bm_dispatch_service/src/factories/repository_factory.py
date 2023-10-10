class RepositoryFactory:

    @staticmethod
    def create_bin_repository(db_session=None):
        from src.models.bin import Bin
        from src.helpers import postgres_helpers
        from src.repositories.bin_repository import BinRepository

        if not db_session:
            db_session = postgres_helpers.get_db()
        return BinRepository(db_session=db_session, bin_model=Bin)
