from django.db import models


class Dish(models.Model):
    """Model definition for Dish."""

    class Category(models.Choices):
        STARTERS = "Starters"
        DESSERTS = "Desserts"
        BREAKFAST = "Breakfast"
        LUNCH = "Lunch"
        DINNER = "Dinner"

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=100)

    restaurant_half_price = models.FloatField()
    restaurant_full_price = models.FloatField()

    zomato_half_price = models.FloatField()
    zomato_full_price = models.FloatField()

    swiggy_full_price = models.FloatField()
    swiggy_half_price = models.FloatField()

    class Meta:
        """Meta definition for Dish."""

        verbose_name = "Dish"
        verbose_name_plural = "Dishes"

    def __str__(self):
        """Unicode representation of Dish."""
        return f"{self.name} : {self.category}"


class Staff(models.Model):
    """Model definition for Staff."""

    name = models.CharField(max_length=100)
    contact = models.BigIntegerField()

    class Meta:
        """Meta definition for Staff."""

        verbose_name = "Staff"
        verbose_name_plural = "Staffs"

    def __str__(self):
        """Unicode representation of Staff."""
        return self.name


class Bill(models.Model):
    """Model definition for Bill."""

    class OrderType(models.TextChoices):
        RESTAURANT = "RESTAURANT"
        SWIGGY = "SWIGGY"
        ZOMATO = "ZOMATO"

    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    generated_at = models.DateTimeField(null=True)
    ref_no = models.CharField(max_length=50, null=True)

    discount = models.FloatField(null=True)
    sub_total = models.FloatField(null=True, default=0.0)
    net = models.FloatField(null=True, default=0.0)
    amount = models.FloatField(null=True)

    cgst = models.FloatField(null=True)
    sgst = models.FloatField(null=True)

    payment_type = models.CharField(max_length=100, default="Cash")

    order_type = models.CharField(choices=OrderType.choices, max_length=100, null=True)
    table_no = models.CharField(null=True, max_length=20)

    staff_name = models.ForeignKey("Staff", on_delete=models.CASCADE, null=True)
    cust_name = models.CharField(max_length=100, null=True)
    contact = models.CharField(max_length=100, null=True)

    amount_due = models.FloatField(default=0.0)

    kot_status = models.BooleanField(default=True)

    class Meta:
        """Meta definition for Bill."""

        verbose_name = "Bill"
        verbose_name_plural = "Bills"

    def __str__(self):
        """Unicode representation of Bill."""
        return f"{self.ref_no} : {self.table_no}"


class UdharKhata(models.Model):
    """Model definition for UdharKhata."""

    customer = models.CharField(max_length=255)
    contact = models.CharField(max_length=100)
    amount_due = models.FloatField(default=0.0)

    class Meta:
        """Meta definition for UdharKhata."""

        verbose_name = "UdharKhata"
        verbose_name_plural = "UdharKhatas"

    def __str__(self):
        """Unicode representation of UdharKhata."""
        return self.customer


class Order(models.Model):
    """Model definition for Order."""

    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    size = models.CharField(max_length=50)

    bill_id = models.ForeignKey(Bill, related_name="order", on_delete=models.CASCADE)

    class Meta:
        """Meta definition for Order."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        """Unicode representation of Order."""
        return self.dish.name


class KOT(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    details = models.JSONField(default=[])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.bill.table_no}"

class Feedback(models.Model):
    name = models.CharField(max_length=50)
    contact_no = models.BigIntegerField()
    bday = models.CharField(max_length=20)
    ambience = models.CharField(max_length=20)
    staff = models.CharField(max_length=20)
    food_quality = models.CharField(max_length=20)
