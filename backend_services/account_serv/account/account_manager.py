from typing import Any

from django.contrib.auth.base_user import BaseUserManager


class AccountManager(BaseUserManager):
    user_in_migration = True

    def _create_account(
            self, username: str, email: str | None, phone: str | None, password: str | None, **extra_fields
    ) -> Any:
        """
        This is a base method to create accounts with the given credentials
        """

        if email is None and phone is None:
            raise ValueError("Either phone or email must be set")

        if not username:
            raise ValueError("Username must be set")

        if phone is not None and len(phone) < 10:
            raise ValueError("Invalid phone number")

        if phone is not None and not phone.startswith("+"):
            raise ValueError("Phone number should have country code")

        if email is not None and "@" not in email and len(email.split("@")) != 2:
            raise ValueError("Invalid email")

        account = self.model(username=username, phone=phone, email=email, **extra_fields)

        account.set_password(password)
        account.save(using=self._db)

        return account

    def create_account(
            self, username: str, email: str | None, phone: str | None, password: str | None = None, **extra_fields
    ) -> Any:
        """
        This method serves as the layer to set default fields when creating auth
        """

        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_phone_verified", False)
        extra_fields.setdefault("is_account_blocked", False)
        extra_fields.setdefault("is_suspended", False)

        return self._create_account(username, email, phone, password, **extra_fields)

    def create_superuser(
            self, username: str, email: str | None, phone: str | None, password: str, **extra_fields
    ) -> Any:
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_phone_verified", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_account(username, email, phone, password, **extra_fields)
