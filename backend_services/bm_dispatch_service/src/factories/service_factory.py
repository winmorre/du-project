class ServiceFactory:
    @staticmethod
    def create_bin_service():
        from src.services.bin_service import BinService
        from .repository_factory import RepositoryFactory

        bin_repo = RepositoryFactory.create_bin_repository()
        return BinService(bin_repo=bin_repo)
