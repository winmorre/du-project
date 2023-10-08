import pytest

from factories.service_factory import ServiceFactory
from models.error_response import ErrorResponse


@pytest.fixture(scope="class")
def account_service():
    return ServiceFactory.create_account_service()


def test_create_account(account_service):
    data = {
        "phone": "+233200000000",
        "phone": "test-secret@",
    }

    account = account_service.create_account(data=data)

    assert account.get("id") is not None
    assert account.get("phone") == "+233200000000"


def test_create_account_with_existing_phone_number(account_service):
    data = {
        "phone": "+233200000000",
        "phone": "test-secret@",
    }
    result = account_service.create_account(data=data)

    assert "Couldn't create account" in result.title


def test_get_object_with_invalid_lookup(account_service):
    result = account_service.get_account(lookup_field="+2335000")

    assert "does not exist" in result.title


def test_get_account(account_service):
    result = account_service.get_account(lookup_field="+233200000000")

    assert result is not None
    assert not isinstance(result, ErrorResponse)
    assert result.phone == "+233200000000"


def test_set_password_with_invalid_account_id(account_service):
    result = account_service.set_password(data={}, account_id=123)

    assert "Couldn't set account password" in result.title


def test_set_password_without_account_id_and_account(account_service):
    result = account_service.set_password(data={})

    assert "Couldn't set account password" in result.title


def test_change_phone_number_with_invalid_data(account_service):
    result = account_service.change_phone_number(data={}, lookup_field="+233200000000")

    assert isinstance(result, ErrorResponse)
    assert "Couldn't change phone number" in result.title


def test_change_account_phone_number(account_service):
    data = {
        "currentPhone": "+233200000000",
        "currentPassword": "test-secret@",
        "phone": "+233200000001"
    }

    result = account_service.change_phone_number(data=data, lookup_field="+233200000000")

    assert not isinstance(result, ErrorResponse)
    assert result.get("phone") is not None
    assert result.get("phone") != "+233200000000"
    assert result.get("phone") == "+233200000001"


def test_change_email(account_service):
    data = {
        "email": "test.mail@pipa.com",
    }

    result = account_service.change_email(data=data, lookup_field="+233200000001")
    assert not isinstance(result, ErrorResponse)
    assert result.get("email") is not None
    assert result.get("email") == "test.mail@pipa.com"


def test_delete_account(account_service):
    result = account_service.delete_account(lookup_field="+233200000001")

    assert not isinstance(result, ErrorResponse)
