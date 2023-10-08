class ServiceFactory:
    @staticmethod
    def create_account_service():
        from factories.repository_factory import RepositoryFactory

        account_repo = RepositoryFactory.create_account_repository()

        from services.account_service import AccountService

        return AccountService(account_repository=account_repo)
