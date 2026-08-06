from django.db import models


class PrinterSetting(models.Model):

    billing_printer = models.CharField(
        max_length=150,
        blank=True,
    )

    kitchen_printer = models.CharField(
        max_length=150,
        blank=True,
    )

    report_printer = models.CharField(
        max_length=150,
        blank=True,
    )

    receipt_printer = models.CharField(
        max_length=150,
        blank=True,
    )

    auto_print_kot = models.BooleanField(
        default=True,
    )

    auto_print_bill = models.BooleanField(
        default=False,
    )

    bill_copies = models.PositiveIntegerField(
        default=1,
    )

    kot_copies = models.PositiveIntegerField(
        default=1,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Printer Setting"
        verbose_name_plural = "Printer Settings"

    def __str__(self):
        return "Restaurant Printer Settings"