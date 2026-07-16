from django.db import models


class Restaurant(models.Model):

    name = models.CharField(max_length=150)

    logo = models.ImageField(
        upload_to="restaurant/logo/",
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)

    city = models.CharField(max_length=100, blank=True)

    state = models.CharField(max_length=100, blank=True)

    country = models.CharField(
        max_length=100,
        default="India"
    )

    pincode = models.CharField(max_length=15, blank=True)

    gst_number = models.CharField(
        max_length=25,
        blank=True
    )

    currency = models.CharField(
        max_length=10,
        default="INR"
    )

    currency_symbol = models.CharField(
        max_length=5,
        default="₹"
    )

    timezone = models.CharField(
        max_length=100,
        default="Asia/Kolkata"
    )

    opening_time = models.TimeField(
        blank=True,
        null=True
    )

    closing_time = models.TimeField(
        blank=True,
        null=True
    )

    receipt_header = models.TextField(blank=True)

    receipt_footer = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name