class ViewFactory:
    @staticmethod
    def create_account_viewset():
        from factories.service_factory import ServiceFactory
        account_service = ServiceFactory.create_account_service()

        from account.views import AccountViewSet

        return AccountViewSet(account_service=account_service)


    @staticmethod
    def create_token_view():
        from account.views import TokenObtainPairView
        return TokenObtainPairView.as_view()
