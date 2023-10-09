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
            account=Account(),
            account_serializer=AccountSerializer,
            account_create_serializer=AccountCreateSerializer,
            email_serializer=EmailSerializer,
            password_serializer=PasswordSerializer,
            change_phone_serializer=ChangePhoneSerializer,
            set_password_serializer=SetPasswordSerializer,
        )