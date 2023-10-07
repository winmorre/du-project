class RepositoryFactory:

    @staticmethod
    def create_account_repository():
        from account.models import Account
        from serializers.account_serializer import AccountSerializer,AccountCreateSerializer
        from repositories.account_repository import AccountRepository

        return AccountRepository(
            account=Account(),
            account_serializer=AccountSerializer,
            account_create_serializer=AccountCreateSerializer,
        )