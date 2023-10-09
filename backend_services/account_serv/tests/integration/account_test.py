import json
from http import HTTPStatus

import pytest
from account.models import Account
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def content_type():
    return "application/json"


@pytest.fixture
def token():
    url = reverse("/token/access/")
    data = {
        "loginField": "test-username",
        "password": "test-secret"
    }
    result = api_client.post(url, data=data, format='json')
    assert result.status_code == HTTPStatus.OK
    body = json.loads(result.body)
    return body["access"]


@pytest.fixture
def teardown(api_client, request):
    # token = Token.objects.get(account__username="test-username")
    # api_client.credentials(HTTP_AUTHORIZATION="Bearer " + token.key)

    account = Account.objects.get(username="test-username")

    # api_client.force_authenticate(user=account)

    def clean_up():
        # token.delete()
        account.clean()

    request.addfinalizer(clean_up)
    return account


def test_create_account():
    url = reverse("/account/me/")
    data = {
        "password": "test-secret@",
        "phone": "+233200000000"
    }

    response = api_client.post(url, data=json.dumps(data), format="json")

    body = json.loads(response.body)

    assert response.status_code == HTTPStatus.CREATED
    assert body["email"] == "test.email@gmail.com"
    assert body["id"] is not None


def test_create_account_error_without_phone_number():
    url = reverse("/account/me/")
    data = {"email": "test.email2@gmail.com", "password": "test-secret"}

    response = api_client.post(url, data=json.dumps(data), format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_error_without_password():
    url = reverse("/account/me/")
    data = {"username": "test-username-error", "email": "test.email@gmail.com"}

    response = api_client.post(url, data=json.dumps(data), format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_account(token):
    account = Account.objects.get(username="test-username")
    url = reverse("/account/me/")
    api_client.force_authenticate(user=account, token=token)
    headers = {"Authorization": f"Bearer {token}"}
    response = api_client.get(url, format="json", headers=headers)
    assert response.body.data is not None
    assert response.status_code == HTTPStatus.OK


def test_set_password():
    account = Account.objects.get(phone="+233200000000")
    url = "/account/set-password/"

    data = {"currentPassword": "test-secret", "newPassword": "new-test-password"}
    api_client.force_authenticate(user=account)

    response = api_client.post(url, data=json.dumps(data), format="json")
    body = json.loads(response.body)

    assert response.status_code == HTTPStatus.CREATED
    # assert body.data["data"]["lastPassword"] == account.lastUpdated
    assert body.data["status"] is True


def test_reset_password():
    url = "/account/reset-password/"
    data = {"newPassword": "new-test-secret", "loginField": "+233200000000"}

    response = api_client.post(url, data=json.dumps(data), format="json")
    body = json.loads(response.body)
    assert response.status_code == HTTPStatus.CREATED
    assert body["data"]["status"] is True


def test_reset_password_error_without_new_password():
    url = reverse("/account/reset-password/?loginField=+233200000000")
    response = api_client.post(url, data=json.dumps({}), format="json")

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_change_account_email():
    url = "/account/change-auth-email/?loginField=+233200000000"

    account = Account.objects.get(username="test-username")
    data = {"newEmail": "new-test.email@gmail.com"}

    api_client.force_authenticate(user=account)

    response = api_client.post(url, data=json.dumps(data), format="json")

    assert response.status_code == HTTPStatus.CREATED
    assert "successful" in response.body.data["msg"]


def test_change_phone_number(api_client):
    url = "/account/change-phone/?loginField=+233200000000"
    data = {
        "newPhone": "+2335555555500",
    }
    account = Account.objects.get(username="test-username")
    api_client.force_authenticate(user=account)

    response = api_client.post(url, data=json.dumps(data), format="json")

    assert response.status_code == HTTPStatus.CREATED
    assert "successful" in response.body.data["msg"]
