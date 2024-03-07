from django.db import models
import datetime


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=10)

    def __str__(self):
        return str(self.name)


class Purchase(models.Model):
    date = models.DateField(default=datetime.date.today)
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.date)


class Item(models.Model):
    """Model definition for Item."""

    item = models.CharField(max_length=200)
    quantity = models.CharField(max_length=100)
    rate = models.FloatField()
    amount = models.FloatField()
    purchase = models.ForeignKey(
        Purchase, related_name="purchase", on_delete=models.CASCADE
    )

    class Meta:
        """Meta definition for Item."""

        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        """Unicode representation of Item."""
        return f"{self.item} | {self.quantity}"
