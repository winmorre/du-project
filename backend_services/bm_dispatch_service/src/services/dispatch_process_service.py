from src.gateways.account_gateway import AccountGateway


class DispatchProcessService:
    def __init__(self, account_gateway: AccountGateway):
        self._account_gateway = account_gateway

    def assign_dispatch_request(self):
        ...

    def schedule_dispatch_request(self):
        ...

    def get_zone_for_dispatch_request(self):
        ...

    def calculate_route_for_dispatch(self):
        ...

    def process_new_dispatch_request(self):
        ...
