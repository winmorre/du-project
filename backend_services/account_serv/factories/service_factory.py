class ServiceFactory:
    @staticmethod
    def create_account_service():
        from factories.repository_factory import RepositoryFactory

        account_repo = RepositoryFactory.create_account_repository()
        redis_repo = RepositoryFactory.create_redis_repository()

        from services.account_service import AccountService

        return AccountService(account_repository=account_repo,redis_repository=redis_repo)

    @staticmethod
    def create_team_service():
        from factories.repository_factory import RepositoryFactory
        from services.team_service import TeamService
        team_repo = RepositoryFactory.create_team_repository()
        return TeamService(team_repo=team_repo)
