from django.core.management.base import BaseCommand
from apps.accounts.models import Permission


PERMISSIONS = [

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    ("dashboard.view", "View Dashboard", "Dashboard"),


    # ==========================================================
    # RESTAURANT
    # ==========================================================

    ("restaurant.view", "View Restaurant", "Restaurant"),
    ("restaurant.add", "Add Restaurant", "Restaurant"),
    ("restaurant.edit", "Edit Restaurant", "Restaurant"),


    # ==========================================================
    # DINING AREAS
    # ==========================================================

    ("areas.view", "View Dining Areas", "Tables"),
    ("areas.add", "Add Dining Areas", "Tables"),
    ("areas.edit", "Edit Dining Areas", "Tables"),
    ("areas.delete", "Delete Dining Areas", "Tables"),


    # ==========================================================
    # TABLES
    # ==========================================================

    ("tables.view", "View Tables", "Tables"),
    ("tables.add", "Add Tables", "Tables"),
    ("tables.edit", "Edit Tables", "Tables"),
    ("tables.delete", "Delete Tables", "Tables"),


    # ==========================================================
    # MENU
    # ==========================================================

    ("categories.view", "View Categories", "Menu"),
    ("categories.add", "Add Categories", "Menu"),
    ("categories.edit", "Edit Categories", "Menu"),
    ("categories.delete", "Delete Categories", "Menu"),

    ("menu.view", "View Menu Items", "Menu"),
    ("menu.add", "Add Menu Items", "Menu"),
    ("menu.edit", "Edit Menu Items", "Menu"),
    ("menu.delete", "Delete Menu Items", "Menu"),


    # ==========================================================
    # ORDERS
    # ==========================================================

    ("orders.view", "View Orders", "Orders"),
    ("orders.add", "Create Orders", "Orders"),
    ("orders.edit", "Edit Orders", "Orders"),
    ("orders.delete", "Delete Orders", "Orders"),

    # Waiter Screens
    ("floor.view", "Floor View", "Orders"),
    ("session.view", "Table Session", "Orders"),
    ("guest.view", "Guest Order", "Orders"),
    ("kot.send", "Send To Kitchen", "Orders"),
    ("kot.print", "Print KOT", "Orders"),


    # ==========================================================
    # BILLING
    # ==========================================================

    ("billing.view", "View Billing", "Billing"),
    ("billing.payment", "Receive Payment", "Billing"),
    ("billing.print", "Print Bills", "Billing"),
    ("billing.refund", "Refund Bills", "Billing"),


    # ==========================================================
    # REPORTS
    # ==========================================================

    ("reports.view", "View Reports", "Reports"),
    ("reports.export", "Export Reports", "Reports"),
    ("reports.print", "Print Reports", "Reports"),


    # ==========================================================
    # SETTINGS
    # ==========================================================

    ("printer.view", "Printer Settings", "Settings"),


    # ==========================================================
    # USERS
    # ==========================================================

    ("users.view", "View Users", "Users"),
    ("users.add", "Add Users", "Users"),
    ("users.edit", "Edit Users", "Users"),
    ("users.delete", "Delete Users", "Users"),


    # ==========================================================
    # SYSTEM
    # ==========================================================

    ("backup.view", "Backup Database", "System"),
    ("restore.view", "Restore Database", "System"),
]


class Command(BaseCommand):

    help = "Create RMS permissions"

    def handle(self, *args, **kwargs):

        for code, name, category in PERMISSIONS:

            Permission.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "category": category,
                },
            )

        self.stdout.write(
            self.style.SUCCESS("Permissions seeded successfully.")
        )