from typing import Any, Dict

from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
import structlog
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, as_serializer_error
from rest_framework.settings import api_settings

from account.models import Account

Logger = structlog.getLogger(__name__)


class AccountCreateMixin:
    def create(self, validated_data):
        try:
            account = AccountCreateMixin.perform_create(validated_data)

        except IntegrityError:
            self.fail("cannot_create_account")
            return

        return account

    @staticmethod
    def perform_create(validated_data):
        with transaction.atomic():
            account = Account.objects.create_account(**validated_data)

        return account


class AccountCreateSerializer(AccountCreateMixin, serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    default_error_messages = {
        "cannot_create_user": "Error occurred while creating account"
    }

    class Meta:
        model = Account
        fields = tuple(Account.REQUIRED_FIELDS) + (
            "password",
            Account.PHONE_FIELD,
        )

    def validate(self, attrs: Dict[str, Any]):
        account = Account(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, account)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs


class AccountSerializer(ModelSerializer):
    """
    AccountSerializer:
    For serialization and de-serialization of account records.
    """

    class Meta:
        model = Account
        fields = "__all__"

    def validate(self, attrs):
        account = Account(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, account)
        except django_exceptions.ValidationError as e:
            serializer_error = as_serializer_error(e)
            Logger.error(
                "validation error", pasword=serializer_error[api_settings.NON_FIELD_ERRORS_KEY], error=e.messages
            )
            raise serializers.ValidationError({"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}) from e

        return attrs


class AccountFunctionsMixin:
    """
    This Mixin is to be used to get account detai.
    In the instance of sending email to reset password, phone,
    """

    def get_account(self, is_active=True):
        try:
            account = Account._default_manager.get(
                is_active=is_active,
                **{self.phone: self.data.get("phone", ""),
                   self.email: self.data.get("email", "")},
            )

            if account.has_usable_password():
                return account
        except Account.DoesNotExist:
            return None


class PasswordSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        super().update(instance, validated_data)

    def create(self, validated_data):
        super().create(validated_data)

    newPassword = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        account = getattr(self, "auth", None) or self.context["request"].user

        assert account is not None

        try:
            validate_password(attrs["newPassword"], account)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({"newPassword": e.messages}) from e
        return super().validate(attrs)


class CurrentPasswordSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        super().update(instance, validated_data)

    def create(self, validated_data):
        super().create(validated_data)

    currentPassword = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {"invalid_password": "Invalid password"}

    def validate_current_password(self, value):
        is_password_valid = self.context["request"].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail("invalid_password")


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["phone"]

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phone = "phone"
        self._default_username_field = Account.USERNAME_FIELD

        self.fields[f"new_{self.phone}"] = self.fields.pop(self.phone)

    def save(self, **kwargs):
        if self.phone != self._default_username_field:
            kwargs[Account.USERNAME_FIELD] = self.validated_data.get(f"new_{self.phone}")

        return super(PhoneSerializer, self).save(**kwargs)


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["email"]

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.email = "email"
        self._default_email_field = Account.EMAIL_FIELD

        self.fields[f"new{str(self.email).capitalize()}"] = self.fields.pop(self.email)

    def save(self, **kwargs):
        if self.email != self._default_email_field:
            kwargs[Account.EMAIL_FIELD] = self.validated_data.get(f"new{str(self.email).capitalize()}")

        return super(EmailSerializer, self).save(**kwargs)


"""
We are not supporting Usernames at the moment. 
But UsernameSerializer can be here, just incase we need it
"""


# class UsernameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         fields = ["username"]
#
#     def __int__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.username = "username"
#         self._default_username_field = Account.USERNAME_FIELD
#
#         self.fields[f"new{self.username.capitalize()}"] = self.fields.pop(self.username)
#
#     def save(self, **kwargs):
#         if self.username != self._default_username_field:
#             kwargs[Account.EMAIL_FIELD] = self.validated_data.get(f"new{self.username.capitalize()}")
#
#         return super(UsernameSerializer, self).save(**kwargs)


class SetPasswordSerializer(PasswordSerializer, CurrentPasswordSerializer):
    pass


class UserDeleteSerializer(CurrentPasswordSerializer):
    pass


class ChangePhoneSerializer(PhoneSerializer, CurrentPasswordSerializer):
    currentPhone = serializers.CharField(required=True, max_length=25)

    class Meta:
        model = Account
        fields = ("currentPhone", "phone", "currentPassword")

