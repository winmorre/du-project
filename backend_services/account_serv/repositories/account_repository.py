import traceback
from typing import Type, Tuple, Dict

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.core.paginator import Paginator

from account.models import Account
from serializers.account_serializer import AccountSerializer, AccountCreateSerializer
from helpers import validators_helpers as vh
from libs.id_gen import id_gen
from errors.account_error import AccountError


class AccountRepository:
    def __init__(self, account: Account, account_serializer: Type[AccountSerializer],
                 account_create_serializer: Type[AccountCreateSerializer]):
        self._account = account
        self._account_serializer = account_serializer
        self._account_create_serializer = account_create_serializer

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

    def delete_account(self, pk):
        try:
            obj = self._account.objects.get(id=pk)

            if obj is not None:
                obj.delete()

            serializer = self._account_serializer(obj)
            return serializer.data
        except Exception:
            raise AccountError(traceback.format_exc())

    def change_phone(self):
        pass

    def change_password(self):
        pass

    def change_email(self):
        pass

    def update_location(self):
        pass

    def update_account(self, data):
        # check if any field is restricted/unique and has specific api
        # if so divert that to those apis
        pass
