from account.account_manager import AccountManager
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Account(models.Model):
    """
    Account Model
    This model can be used to modify Account data. retrieving, creating, updating, and deletion of data
    """

    id = models.IntegerField(_("id"), primary_key=True, editable=False, db_index=True)
    dateJoined = models.DateTimeField(_("date joined"), auto_now_add=True, db_column="dateJoined")
    phoneVerified = models.BooleanField(_("phone verified"), default=False, db_column="phoneVerified")
    roles = models.CharField(_("roles"), max_length=255, )
    phone = models.CharField(_("phone number"), max_length=25, unique=True, null=True, blank=True, db_index=True)
    email = models.EmailField(_("email"), max_length=255, unique=True, db_index=True, blank=True, null=True)
    isDeleted = models.BooleanField(_("is deleted"), default=False, db_column="isDeleted")
    timezone = models.CharField(_("account's timezone"), null=True, blank=True, max_length=50)
    geoEnabled = models.BooleanField(_("geo enabled"), db_column="geoEnabled", default=False)
    lang = models.CharField(_("account's lang"), max_length=5)
    displayName = models.CharField(_("display name"), max_length=75, db_column="displayName")
    location = models.CharField(_("location"), max_length=70, null=True, blank=True)
    entities = JSONField(_("entities"), default=dict)
    lastUpdated = models.DateTimeField(_("date joined"), auto_now_add=True, db_column="lastUpdated")

    objects = AccountManager()

    USERNAME_FIELD = "phone"
    EMAIL_FIELD = "email"
    PHONE_FIELD = "phone"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "accounts"
        verbose_name = _("accounts")
        ordering = ["-dateJoined"]

    def __str__(self) -> str:
        return f"{self.id}"
