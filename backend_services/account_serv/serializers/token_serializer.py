from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import CharField
from rest_framework import serializers, exceptions
from rest_framework.settings import api_settings
from rest_framework_simplejwt.serializers import PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import Account
from helpers import validators_helpers as vh
from serializers.account_serializer import AccountSerializer


class TokenCreateSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(TokenCreateSerializer, self).__init__(*args, **kwargs)
        self.account = None
        self.fields["phone"] = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    password = CharField(style={"input_type": "password"}, write_only=True)
    default_error_messages = {
        "invalid_credentials": "Invalid credentials",
        "inactive_account": "Account is inactive",
        "account_blocked": "Account is blocked",
        "inactive_phone": "Phone number is inactive",
        "account_suspended": "Account suspended",
    }

    def validate(self, attrs) -> Any:
        password = attrs.get("password")
        params = {"phone": attrs.get("phone")}
        self.account = authenticate(request=self.context.get("request"), **params, password=password)

        if not self.account:
            self.account = Account.objects.filter(**params).first()
        if self.account and not self.account.check_password(password):
            self.fail("invalid_credentials")

        if self.account and not self.account.is_account_blocked:
            self.fail("account_blocked")

        if self.account and not self.account.is_phone_verified:
            self.fail("inactive_phone")

        if self.account and not self.account.is_active:
            self.fail("inactive_account")

        if self.account and not self.account.is_suspended:
            self.fail("account_suspended")

        return attrs


class TokenObtainSerializer(serializers.Serializer):
    username_field = Account.USERNAME_FIELD
    email_field = Account.EMAIL_FIELD
    phone_field = Account.PHONE_FIELD
    login_field = "loginField"

    token_class = None

    default_error_messages = {"no_active_account": _("No active auth found with the given credentials")}

    def __init__(self, *args, **kwargs):
        super(TokenObtainSerializer, self).__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields[self.email_field] = serializers.EmailField()
        self.fields[self.phone_field] = serializers.CharField()
        self.fields["password"] = PasswordField()

        self.account = None

    def validate(self, attrs):
        authenticate_kwargs = {self.fields["password"]: attrs["password"]}

        try:
            authenticate_kwargs["request"] = self.context["request"]

            if vh.is_phone_number(attrs[self.login_field]):
                authenticate_kwargs[self.phone_field] = attrs[self.login_field]
            elif vh.is_email(value=attrs[self.login_field]):
                authenticate_kwargs[self.email_field] = attrs[self.login_field]
            else:
                authenticate_kwargs[self.username_field] = attrs[self.login_field]
        except KeyError:
            pass

        self.account = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.account):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, account):
        return cls.token_class.for_user(account)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)

        refresh = self.get_token(self.account)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        account = AccountSerializer(self.account)

        data["auth"] = account

        update_last_login(None, self.account)

        return data
