from django.dispatch import Signal

# New auth is created. Args: auth, request

account_registered = Signal()

# Account has been activated, Args: auth, request
account_activated = Signal()

# Account has been updated. Args: auth, request
account_updated = Signal()
