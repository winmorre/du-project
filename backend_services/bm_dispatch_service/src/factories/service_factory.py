class ServiceFactory:
    @staticmethod
    def create_bin_service():
        from src.services.bin_service import BinService
        from .repository_factory import RepositoryFactory

        bin_repo = RepositoryFactory.create_bin_repository()
        return BinService(bin_repo=bin_repo)

    @staticmethod
    def create_dispatch_service():
        from .repository_factory import RepositoryFactory
        from src.services.dispatch_service import DispatchService
        dispatch_repo = RepositoryFactory.create_dispatch_repository()
        redis_repo = RepositoryFactory.create_redis_repository()

        return DispatchService(dispatch_repo=dispatch_repo, redis_repo=redis_repo)
