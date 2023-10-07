import traceback
from typing import Dict

from django.core.exceptions import ObjectDoesNotExist
import structlog

from repositories.account_repository import AccountRepository
from helpers import validators_helpers as vh
from errors.account_error import AccountError
from models.error_response import ErrorResponse

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
                title="object does not exist",
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

    def delete_account(self, pk: int) -> bool | ErrorResponse:
        try:
            result = self._account_repo.delete_account(pk=pk)
            Logger.info("account deleted", account=result)
            return True
        except AccountError:
            Logger.error("delete account error", pk=pk, traceback=traceback.format_exc())
            return ErrorResponse(
                type="Invalid lookup",
                title="Couldn't delete account",
                detail=(
                    "Account you are trying to delete does not exist"
                    "Error occurred when trying to delete the account"
                )
            )
