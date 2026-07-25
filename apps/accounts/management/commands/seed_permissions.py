from django.core.management.base import BaseCommand

from apps.accounts.models import Permission


PERMISSIONS = [

    # Dashboard
    ("dashboard.view", "View Dashboard", "Dashboard"),

    # Restaurant
    ("restaurant.view", "View Restaurant", "Restaurant"),
    ("restaurant.add", "Add Restaurant", "Restaurant"),
    ("restaurant.edit", "Edit Restaurant", "Restaurant"),

    # Dining Areas
    ("areas.view", "View Dining Areas", "Tables"),
    ("areas.add", "Add Dining Areas", "Tables"),
    ("areas.edit", "Edit Dining Areas", "Tables"),
    ("areas.delete", "Delete Dining Areas", "Tables"),

    # Restaurant Tables
    ("tables.view", "View Tables", "Tables"),
    ("tables.add", "Add Tables", "Tables"),
    ("tables.edit", "Edit Tables", "Tables"),
    ("tables.delete", "Delete Tables", "Tables"),

    # Menu Categories
    ("categories.view", "View Categories", "Menu"),
    ("categories.add", "Add Categories", "Menu"),
    ("categories.edit", "Edit Categories", "Menu"),
    ("categories.delete", "Delete Categories", "Menu"),

    # Menu Items
    ("menu.view", "View Menu Items", "Menu"),
    ("menu.add", "Add Menu Items", "Menu"),
    ("menu.edit", "Edit Menu Items", "Menu"),
    ("menu.delete", "Delete Menu Items", "Menu"),

    # Orders
    ("orders.view", "View Orders", "Orders"),
    ("orders.add", "Create Orders", "Orders"),
    ("orders.edit", "Edit Orders", "Orders"),
    ("orders.delete", "Delete Orders", "Orders"),

    # Billing
    ("billing.view", "View Billing", "Billing"),
    ("billing.payment", "Receive Payment", "Billing"),
    ("billing.print", "Print Bills", "Billing"),
    ("billing.refund", "Refund Bills", "Billing"),

    # Reports
    ("reports.view", "View Reports", "Reports"),
    ("reports.export", "Export Reports", "Reports"),
    ("reports.print", "Print Reports", "Reports"),

    # Printer
    ("printer.view", "Printer Settings", "Settings"),

    # Users
    ("users.view", "View Users", "Users"),
    ("users.add", "Add Users", "Users"),
    ("users.edit", "Edit Users", "Users"),
    ("users.delete", "Delete Users", "Users"),

    # Backup
    ("backup.view", "Backup Database", "System"),
    ("restore.view", "Restore Database", "System"),
]


class Command(BaseCommand):

    help = "Create RMS permissions"

    def handle(self, *args, **kwargs):

        for code, name, category in PERMISSIONS:

            Permission.objects.get_or_create(

                code=code,

                defaults={

                    "name": name,

                    "category": category,

                },

            )

        self.stdout.write(

            self.style.SUCCESS(

                "Permissions created successfully."

            )

        )