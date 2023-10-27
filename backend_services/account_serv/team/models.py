from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Team(models.Model):
    id = models.IntegerField(_("id"), primary_key=True, editable=False, db_index=True)
    teamName = models.CharField(_("team name"), max_length=245, null=True, blank=True, db_index=True, unique=True)
    assignedZones = models.CharField(_("assigned zones"), max_length=245, null=True, blank=True)
    available = models.BooleanField(_("available"), default=True)
    createdAt = models.DateTimeField(_("created at"), auto_now_add=True, db_column="createdAt")

    class Meta:
        db_table = "team"
        verbose_name = _("teams")
        ordering = ["-createdAt"]
