from typing import Type
from unittest.mock import Mock

import pytest
from account.models import Account
from errors.account_error import AccountError
from repositories.account_repository import AccountRepository
from serializers.account_serializer import (AccountCreateSerializer,
                                            AccountSerializer,
                                            ChangePhoneSerializer,
                                            EmailSerializer,
                                            PasswordSerializer,
                                            SetPasswordSerializer)


@pytest.fixture
def mock_account():
    return Mock(spec=Account)


@pytest.fixture
def mock_account_serializer():
    return Mock(spec=Type[AccountSerializer])


@pytest.fixture
def account_repository(mock_account):
    return AccountRepository(
        account=mock_account,
        account_serializer=AccountSerializer,
        account_create_serializer=AccountCreateSerializer,
        email_serializer=EmailSerializer,
        password_serializer=PasswordSerializer,
        change_phone_serializer=ChangePhoneSerializer,
        set_password_serializer=SetPasswordSerializer,
    )


@pytest.fixture(scope="module")
def pk():
    return 7095354049319022592


@pytest.fixture
def fake_account(pk):
    return {
        "id": pk,
        "dateJoined": "2023-08-10 09:23:23.336561",
        "isActive": True,
        "isSuperuser": False,
        "phoneVerified": True,
        "phone": "+233200000000",
        "email": "test.email@pluug.io",
        "lastUpdated": "2023-08-10 09:23:23.336561",
        "entities": {},
    }


@pytest.fixture
def account(fake_account):
    return Account(**fake_account)


def test_create_account_failed_invalid_data(account_repository):
    data = {"phone": "+233506453"}
    with pytest.raises(AccountError) as ac_err:
        account_repository.create_account(data=data)

    assert "invalid" in ac_err.value.args[0]


def test_change_phone_number_with_invalid_lookup_field(account_repository, mock_account):
    mock_account.objects.filter.return_value = None

    with pytest.raises(AccountError) as acc_err:
        account_repository.change_phone_number(data={}, lookup_field=1)

    assert "not found" in acc_err.value.args[0]


def test_change_email_with_invalid_lookup_field(account_repository, mock_account):
    mock_account.objects.filter.return_value = None
    with pytest.raises(AccountError) as ac_err:
        account_repository.change_email(data={}, lookup_field=1)
    assert "not found" in ac_err.value.args[0]
