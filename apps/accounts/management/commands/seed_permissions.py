from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Permission, UserPermission


User = get_user_model()


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
    ("kitchen.view", "View Kitchen Display", "Orders"),
    ("kitchen.manage", "Manage Kitchen Items", "Orders"),


    # ==========================================================
    # BILLING
    # ==========================================================

    ("billing.view", "View Billing", "Billing"),
    ("billing.payment", "Receive Payment", "Billing"),
    ("billing.print", "Print Bills", "Billing"),
    ("billing.refund", "Refund Bills", "Billing"),
    ("billing.add", "Add Financial Period", "Billing"),
    ("billing.edit", "Edit Financial Period", "Billing"),
    ("billing.delete", "Delete Financial Period", "Billing"),


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
    ("audit.view", "View Audit Trail", "System"),

    # ==========================================================
    # REGISTRATION / LICENSE
    # ==========================================================

    ("registration.view", "View Registration", "System"),
    ("registration.add", "Add License Key", "System"),
    ("registration.edit", "Edit License Key", "System"),
    ("registration.delete", "Delete License Key", "System"),
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

        # Grant all permissions to OWNER users
        owner_users = User.objects.filter(role="OWNER")
        all_permissions = Permission.objects.all()

        for owner in owner_users:
            for perm in all_permissions:
                UserPermission.objects.get_or_create(
                    user=owner,
                    permission=perm,
                )

        # If no OWNER exists, grant all permissions to the first admin user
        if not owner_users.exists():
            fallback = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if fallback:
                for perm in all_permissions:
                    UserPermission.objects.get_or_create(
                        user=fallback,
                        permission=perm,
                    )
                self.stdout.write(
                    self.style.WARNING(
                        f"No OWNER user found — granted all permissions to '{fallback.username}' instead."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Permissions seeded successfully.")
        )