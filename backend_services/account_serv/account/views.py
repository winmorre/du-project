from http import HTTPStatus
from typing import Any

import structlog
from account.models import Account
from django.contrib.auth.tokens import default_token_generator
from helpers import signals
from models.error_response import ErrorResponse
from opentelemetry import trace
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenViewBase
from serializers.account_serializer import AccountSerializer
from serializers.token_serializer import TokenObtainPairSerializer
from services.account_service import AccountService

Logger = structlog.getLogger(__name__)
tracer = trace.get_tracer(__name__)


# Create your views here.


class AccountViewSet(ModelViewSet):
    def __init__(self, account_service: AccountService):
        super().__init__()
        self.account_service = account_service

    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    token_generator = default_token_generator
    lookup_field = "id"
    http_allowed_methods = ["options", "head", "delete", "get", "post"]
    http_method_names = ["options", "head", "delete", "get", "post"]

    def get_instance(self) -> Any:
        return self.request.user

    def perform_update(self, serializer, *args, **kwargs):
        super(AccountViewSet, self).perform_update(serializer)

        account = serializer.instance
        signals.account_updated.send(sender=self.__class__, account=account, request=self.request)

    def perform_create(self, serializer, *args, **kwargs):
        account = serializer.save(*args, **kwargs)
        signals.account_registered.send(sender=self.__class__, account=account, request=self.request)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            # log user out Or delete any active tokens
            pass
        self.perform_destroy(instance)
        return Response(status=HTTPStatus.NO_CONTENT)

    def get_permissions(self):
        match self.action:
            case "create":
                self.permission_classes = [AllowAny]
            case "me":
                if self.request and self.request.method == "DELETE":
                    self.permission_classes = [IsAuthenticated]
                if self.request and self.request.method == "POST":
                    self.permission_classes = [AllowAny]
            case "set_password":
                self.permission_classes = [IsAuthenticated]
            case "reset_password":
                self.permission_classes = [AllowAny]
            case "change_phone_number":
                self.permission_classes = [IsAuthenticated]
            case "change_account_email":
                self.permission_classes = [IsAuthenticated]
            case "change_username":
                self.permission_classes = [IsAuthenticated]

            case _:
                self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    @action(methods=["get", "delete", "post"], detail=False, url_path="me", url_name="me")
    def me(self, request: Request, *args, **kwargs):
        match request.method:
            case "GET":
                result = self.account_service.get_account(lookup_field=request.user.id)
                if isinstance(result, ErrorResponse):
                    return Response(
                        status=HTTPStatus.BAD_REQUEST,
                        data=result.asdict()
                    )
                return Response(status=HTTPStatus.OK, data=result)

            case "DELETE":
                result = self.account_service.delete_account(
                    lookup_field=request.user.id
                )
                if isinstance(result, ErrorResponse):
                    Response(status=HTTPStatus.BAD_REQUEST, exception=True, data=result.asdict())
                return Response(status=HTTPStatus.OK, data=True)

            case "POST":
                result = self.account_service.create_account(request.data)
                if isinstance(result, ErrorResponse):
                    return Response(status=HTTPStatus.BAD_REQUEST, data=result.asdict())

                return Response(status=HTTPStatus.CREATED, exception=True, data=result)

    @action(methods=["post"], detail=False, url_path="set-password", url_name="set-password")
    def set_password(self, request: Request):
        result = self.account_service.set_password(
            data=request.data,
            account_id=request.user.id,
            account=request.user
        )

        if isinstance(result, ErrorResponse):
            return Response(status=HTTPStatus.BAD_REQUEST, data=result.asdict(), exception=True, )

        return Response(data=True, status=HTTPStatus.OK)

    @action(methods=["post"], detail=False, url_path="reset-password/", url_name="reset-password")
    def reset_password(self, request: Request):
        login_field = request.query_params.get("loginField")
        result = self.account_service.reset_password(data=request.data, lookup_field=login_field)

        if isinstance(result, ErrorResponse):
            return Response(status=HTTPStatus.BAD_REQUEST, exception=True, data=result.asdict())
        return Response(
            status=HTTPStatus.CREATED,
            data=True
        )

    @action(methods=["post"], detail=False, url_name="change-phone", url_path="change-phone/")
    def change_phone_number(self, request: Request) -> Response | None:
        login_field = request.query_params.get("loginField")
        result = self.account_service.change_phone_number(
            data=request.data,
            instance=request.user,
            lookup_field=login_field
        )

        if isinstance(result, ErrorResponse):
            return Response(status=HTTPStatus.BAD_REQUEST, exception=True, data=result.asdict())

        Response(status=HTTPStatus.CREATED, data=result)

    @action(methods=["post"], detail=False, url_name="change-account-email", url_path="change-account-email/")
    def change_account_email(self, request: Request) -> Response | None:
        login_field = request.query_params.get("loginField")
        result = self.account_service.change_email(
            data=request.data,
            lookup_field=login_field
        )

        if isinstance(result, ErrorResponse):
            return Response(status=HTTPStatus.BAD_REQUEST, exception=True, data=result.asdict())

        return Response(status=HTTPStatus.CREATED, data=result)


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """

    _serializer_class = TokenObtainPairSerializer
