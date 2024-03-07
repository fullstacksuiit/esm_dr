from django.db import models


class Ledger(models.Model):
    """Model definition for Ledger."""

    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    debit = models.FloatField(null=True, blank=True, default=0.0)
    credit = models.FloatField(null=True, blank=True, default=0.0)
    name = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        """Meta definition for Ledger."""

        verbose_name = "Ledger"
        verbose_name_plural = "Ledgers"
