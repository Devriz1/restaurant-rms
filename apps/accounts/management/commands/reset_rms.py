from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Delete operational RMS data without touching master data."

    @transaction.atomic
    def handle(self, *args, **options):

        # Import models here to avoid circular imports
        from apps.billing.models import (
            Bill,
            BillItem,
            Payment,
        )

        from apps.orders.models import (
            GuestOrder,
            TableSession,
        )

        self.stdout.write(self.style.WARNING(
            "Deleting RMS operational data..."
        ))

        Payment.objects.all().delete()
        BillItem.objects.all().delete()
        Bill.objects.all().delete()

        GuestOrder.objects.all().delete()
        TableSession.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                "RMS reset completed successfully."
            )
        )