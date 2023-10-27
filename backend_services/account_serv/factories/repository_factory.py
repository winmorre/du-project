class RepositoryFactory:

    @staticmethod
    def create_account_repository():
        from account.models import Account
        from repositories.account_repository import AccountRepository
        from serializers.account_serializer import (AccountCreateSerializer,
                                                    AccountSerializer,
                                                    ChangePhoneSerializer,
                                                    EmailSerializer,
                                                    PasswordSerializer,
                                                    SetPasswordSerializer)

        return AccountRepository(
            account=Account,
            account_serializer=AccountSerializer,
            account_create_serializer=AccountCreateSerializer,
            email_serializer=EmailSerializer,
            password_serializer=PasswordSerializer,
            change_phone_serializer=ChangePhoneSerializer,
            set_password_serializer=SetPasswordSerializer,
        )

    @staticmethod
    def create_team_repository():
        from team.models import Team
        from repositories.team_repository import TeamRepository
        from serializers.team_serializer import TeamSerializer, TeamCreateSerializer

        return TeamRepository(
            team=Team,
            team_serializer=TeamSerializer,
            team_create_serializer=TeamCreateSerializer,
        )

    @staticmethod
    def create_redis_repository():
        from repositories.redis_repository import RedisRepository
        from helpers.redis_helpers import create_redis_connection

        redis_connection = create_redis_connection()

        return RedisRepository(redis=redis_connection)
