class RepositoryFactory:

    @staticmethod
    def create_bin_repository(db_session=None):
        from src.models.bin import Bin
        from src.helpers import postgres_helpers
        from src.repositories.bin_repository import BinRepository

        if not db_session:
            db_session = postgres_helpers.get_db()
        return BinRepository(db_session=db_session, bin_model=Bin)

    @staticmethod
    def create_dispatch_repository(db_session=None):
        from src.helpers import postgres_helpers
        if not db_session:
            db_session = postgres_helpers.get_db()

        from src.models.dispatch import Dispatch
        from src.repositories.dispatch_repository import DispatchRepository

        return DispatchRepository(db_session=db_session, dispatch_model=Dispatch)

    @staticmethod
    def create_redis_repository():
        from src.helpers.redis_helpers import create_redis_connection
        from src.repositories.redis_repository import RedisRepository
        connection = create_redis_connection()

        return RedisRepository(redis=connection)
