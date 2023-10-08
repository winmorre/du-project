import traceback
from typing import Dict

import structlog
from django.core.exceptions import ObjectDoesNotExist
from errors.account_error import AccountError
from helpers import validators_helpers as vh
from models.error_response import ErrorResponse
from repositories.account_repository import AccountRepository

Logger = structlog.getLogger(__name__)


class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self._account_repo = account_repository

    def create_account(self, data: dict):
        try:
            validated_phone = self._validate_create_account_data(data=data)

            if validated_phone is not None:
                return validated_phone

            new_account = self._account_repo.create_account(data=data)

            return new_account
        except AccountError:
            Logger.error("create account error", phone=data.get("phone"), traceback=traceback.format_exc())
            _err = {
                "type": "create entity error",
                "title": "Couldn't create account",
                "detail": traceback.format_exc()
            }
            return ErrorResponse.from_dict(_err)

    def _validate_create_account_data(self, data) -> ErrorResponse | None:
        phone = data.get("phone")

        if not phone or not vh.is_phone_number(phone):
            err = {
                "type": "Incorrect field value",
                "title": "invalid field",
                "detail": (
                    "The phone number provided is not valid. Phone numbers should start with a country code i.e (+233)"
                    "Phone number should be at least 10 digits "
                )
            }

            return ErrorResponse.from_dict(err)

        return

    def get_account(self, lookup_field: int | str) -> Dict | ErrorResponse:
        try:
            _, account_serialized = self._account_repo.get_account(lookup_field=lookup_field)

            return account_serialized
        except ObjectDoesNotExist:
            Logger.error("get account error", lookup_field=lookup_field, traceback=traceback.format_exc())
            return ErrorResponse(
                title="Account object does not exist",
                type="invalid lookup",
                detail=(
                    "Account object does not exist"
                    f"Cross check the lookup field {lookup_field} and try again"
                )
            )

    def get_all_accounts(self, account):
        # check for right permission
        try:
            result = self._account_repo.get_all_accounts()
            return result
        except AccountError:
            Logger.error("get accounts error", traceback=traceback.format_exc())
            return ErrorResponse(
                title="Accounts data retrieval error",
                type="Invalid lookup",
                detail=(
                    "Could not retrieve account data"
                    "Suggest a way around"
                )
            )

    def delete_account(self, lookup_field: int) -> bool | ErrorResponse:
        try:
            result = self._account_repo.delete_account(lookup_field=lookup_field)
            Logger.info("account deleted", account=result)
            return True
        except AccountError:
            Logger.error("delete account error", pk=lookup_field, traceback=traceback.format_exc())
            return ErrorResponse(
                type="Invalid lookup",
                title="Couldn't delete account",
                detail=(
                    "Account you are trying to delete does not exist"
                    "Error occurred when trying to delete the account"
                )
            )

    def set_password(self, data, account_id=None, account=None):
        try:
            updated_account = self._account_repo.set_password(data, account_id, account)
            return updated_account
        except AccountError:
            Logger.error("set password error", data=data, account_id=account_id, traceback=traceback.format_exc())
            return ErrorResponse(
                type="account update",
                title="Couldn't set account password",
                detail=(),
            )

    def reset_password(self, data, lookup_field):
        try:
            updated_account = self._account_repo.reset_password(data=data, lookup_field=lookup_field)
            return updated_account
        except AccountError:
            Logger.error("reset password error", data=data, lookup_field=lookup_field, traceback=traceback.format_exc())
            return ErrorResponse(
                type="account update",
                title="Couldn't reset account password",
                detail=(),
            )

    def change_phone_number(self, data, lookup_field, instance=None):
        try:
            updated_account = self._account_repo.change_phone_number(data=data, lookup_field=lookup_field,
                                                                     instance=instance)
            return updated_account
        except AccountError as ac_err:
            Logger.error("change phone error", data=data, lookup_field=lookup_field, traceback=traceback.format_exc())
            return ErrorResponse(
                type="account update",
                title="Couldn't change phone number of this account",
                detail=(
                    str(ac_err.args[0])
                ),
            )

    def change_email(self, data, lookup_field):
        try:
            updated_account = self._account_repo.change_email(data=data, lookup_field=lookup_field)
            return updated_account
        except AccountError:
            Logger.error("change email error", data=data, lookup_field=lookup_field, traceback=traceback.format_exc())
            return ErrorResponse(
                type="account update",
                title="Couldn't change the email of this account",
                detail="",
            )
