import datetime
import traceback
from typing import Dict, Tuple, Type

from account.models import Account
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from errors.account_error import AccountError
from helpers import validators_helpers as vh
from libs.id_gen import id_gen
from serializers.account_serializer import (AccountCreateSerializer,
                                            AccountSerializer,
                                            ChangePhoneSerializer,
                                            EmailSerializer,
                                            PasswordSerializer,
                                            SetPasswordSerializer)


class AccountRepository:
    def __init__(self, account: Account, account_serializer: Type[AccountSerializer],
                 account_create_serializer: Type[AccountCreateSerializer],
                 set_password_serializer: Type[SetPasswordSerializer], email_serializer: Type[EmailSerializer],
                 password_serializer: Type[PasswordSerializer], change_phone_serializer: Type[ChangePhoneSerializer]):
        self._account = account
        self._account_serializer = account_serializer
        self._account_create_serializer = account_create_serializer
        self._set_password_serializer = set_password_serializer
        self._password_serializer = password_serializer
        self._change_phone_serializer = change_phone_serializer
        self._email_serializer = email_serializer

    def create_account(self, data: dict):
        serializer = self._account_create_serializer(data=data)

        try:
            if not vh.is_valid_serializer(serializer):
                raise AccountError(str(serializer.errors))

            pk = id_gen.get_id()
            serializer.save(id=pk)

            return serializer.data
        except Exception:
            raise AccountError(traceback.format_exc())

    def get_account(self, lookup_field) -> Tuple[Account, Dict]:
        try:
            filter_query = Q(email=lookup_field) | Q(phone=lookup_field) | Q(id=lookup_field)

            account_instance = self._account.objects.filter(filter_query).first()
            serialized = self._account_serializer(account_instance)
            return account_instance, serialized.data
        except Exception:
            raise ObjectDoesNotExist()

    def get_account_by_id(self, account_id):
        try:
            account = self._account.objects.get(id=account_id)
            return account
        except Exception:
            raise AccountError(traceback.format_exc())

    def get_all_accounts(self, page=0, limit=500):
        try:
            accounts = self._account.objects.all()
            _paginator = Paginator(accounts, limit)

            page_obj = _paginator.get_page(page)
            serializer = self._account_serializer(page_obj, many=True)

            return {
                "page": page,
                "has_next_page": page_obj.has_next(),
                "accounts": serializer.data
            }
        except Exception:
            raise AccountError(traceback.format_exc())

    def delete_account(self, lookup_field):
        try:
            obj, _ = self.get_account(lookup_field=lookup_field)

            if obj is not None:
                obj.delete()

            serializer = self._account_serializer(obj)
            return serializer.data
        except Exception:
            raise AccountError(traceback.format_exc())

    def change_phone_number(self, data, lookup_field, instance=None):
        try:
            account, _ = self.get_account(lookup_field=lookup_field)

            if account is None:
                raise AccountError(f"Account object not found: lookup_field-> {lookup_field}")

            if instance is not None and account != instance:
                raise AccountError("Not authorized to change phone number of this account")
            serializer = self._change_phone_serializer(account, data=data)

            if not vh.is_valid_serializer(serializer):
                raise AccountError(str(serializer.errors))

            setattr(account, Account.PHONE_FIELD, serializer.data["phone"])

            return serializer.data
        except Exception:
            raise AccountError("Error occurred changing phone number")

    def reset_password(self, data, lookup_field: int | str):
        try:
            account, _ = self.get_account(lookup_field=lookup_field)
            if account is None:
                raise AccountError(f"Account object not found: lookup_field->{lookup_field}")

            serializer = self._password_serializer(data=data)
            if not vh.is_valid_serializer(serializer):
                raise AccountError(str(serializer.errors))

            account.set_password(serializer.data["newPassword"])
            now = datetime.datetime.now()
            account.save(lastUpdated=now)

            return self._account_serializer(account).data
        except Exception:
            raise AccountError(f"Error occurred resetting password: lookup_field-> {lookup_field}")

    def set_password(self, data, account_id=None, account=None):
        if not account_id or not account:
            raise AccountError("Either account Id or Account data is required")

        try:
            serializer = self._set_password_serializer(data=data)

            if not vh.is_valid_serializer(serializer):
                raise AccountError(str(serializer.errors))

            if account is not None and isinstance(account, Account):
                account.set_password(serializer.data['newPassword'])
                now = datetime.datetime.now()
                account.save(lastUpdated=now)

                return self._account_serializer(account).data

            if account_id is not None:
                account, _ = self.get_account_by_id(account_id)

                if account is None:
                    raise AccountError("Account with id {} not found!!".format(account_id))

                account.set_password(serializer.data['newPassword'])
                now = datetime.datetime.now()
                account.save(lastUpdated=now)

                return self._account_serializer(account).data
        except Exception:
            raise AccountError("Error occurred setting password")

    def change_email(self, data, lookup_field):
        try:
            account, _ = self.get_account(lookup_field=lookup_field)

            if account is None:
                raise AccountError(f"Account object not found: lookup_field->{lookup_field}")

            serializer = self._email_serializer(data=data)
            if not vh.is_valid_serializer(serializer):
                raise AccountError(str(serializer.errors))

            setattr(account, Account.EMAIL_FIELD, serializer.data["newEmail"])
            now = datetime.datetime.now()
            account.save(lastUpdated=now)
            return self._account_serializer(account).data
        except Exception:
            raise AccountError(f"Error occurred changing email on account: lookup_field->{lookup_field}")

    def update_location(self):
        pass

    def update_account(self, data):
        # check if any field is restricted/unique and has specific api
        # if so divert that to those apis
        pass
