import requests

import structlog

Logger = structlog.getLogger(__name__)


class AccountGateway:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_all_teams(self, endpoint: str) -> dict | None:
        url = self.base_url + endpoint
        response = requests.get(url=url)
        if response.status_code != 200:
            Logger.error("get all teams error", response=response.json())
            return
        return response.json()

    def get_all_accounts(self, endpoint: str):
        url = self.base_url + endpoint
        response = requests.get(url=url)

        if response.status_code != 200:
            Logger.error("get all accounts error", response=response.json())
            return
        return response.json()

    def get_account(self, endpoint, pk):
        url = self.base_url + endpoint + f"/{pk}"
        response = requests.get(url=url)

        if response.status_code != 200:
            Logger.error("get account error", response=response.json())
            return
        return response.json()
