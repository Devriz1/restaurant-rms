from django.core.management.base import BaseCommand
from apps.registration.models import LicenseKey


class Command(BaseCommand):
    help = "Create a license key for software registration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--plan",
            type=str,
            default="lifetime",
            choices=["lifetime", "monthly", "yearly"],
            help="Plan type (default: lifetime).",
        )
        parser.add_argument(
            "--max-users",
            type=int,
            default=1,
            help="Maximum number of user accounts allowed (default: 1).",
        )
        parser.add_argument(
            "--expires",
            type=str,
            default=None,
            help="Expiration datetime, format YYYY-MM-DD HH:MM (optional).",
        )
        parser.add_argument(
            "--duration",
            type=str,
            default=None,
            help="Duration from now, e.g. 10s, 20s, 5m, 1h. Overrides --expires.",
        )
        parser.add_argument(
            "--note",
            type=str,
            default="",
            help="Optional note.",
        )

    def _generate_key(self):
        """Generate a random license key like RMS-XXXX-XXXX-XXXX."""
        import secrets
        import string
        while True:
            part = lambda n: "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(n)
            )
            key = "RMS-%s-%s-%s" % (part(4), part(4), part(4))
            if not LicenseKey.objects.filter(key=key).exists():
                return key

    def _parse_duration(self, value):
        """Parse a duration string like 10s, 20s, 5m, 1h into a timedelta."""
        import re
        from datetime import timedelta
        match = re.match(r"^(\d+)([smhd])$", value.strip().lower())
        if not match:
            raise ValueError("Invalid duration: %s. Use e.g. 10s, 5m, 1h." % value)
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "s":
            return timedelta(seconds=amount)
        if unit == "m":
            return timedelta(minutes=amount)
        if unit == "h":
            return timedelta(hours=amount)
        if unit == "d":
            return timedelta(days=amount)
        return timedelta(seconds=amount)

    def handle(self, *args, **options):
        key_code = self._generate_key()
        expires_at = None
        if options["duration"]:
            from django.utils import timezone
            expires_at = timezone.now() + self._parse_duration(options["duration"])
        elif options["expires"]:
            from django.utils import timezone
            from datetime import datetime
            expires_at = timezone.make_aware(
                datetime.strptime(options["expires"], "%Y-%m-%d %H:%M"),
                timezone.get_current_timezone(),
            )

        key = LicenseKey.objects.create(
            key=key_code,
            plan=options["plan"],
            max_users=options["max_users"],
            expires_at=expires_at,
            note=options["note"],
        )

        expires_str = (
            key.expires_at.strftime("%d %b %Y, %I:%M %p")
            if key.expires_at
            else "Never (Lifetime)"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "\n" + "=" * 50 + "\n"
                "LICENSE KEY CREATED\n"
                + "=" * 50 + "\n"
                "Key        : %s\n" % key.key
                + "Plan       : %s\n" % key.get_plan_display()
                + "Max Users  : %s\n" % key.max_users
                + "Expires    : %s\n" % expires_str
                + "Note       : %s\n" % (key.note or "-")
                + "=" * 50 + "\n"
                "Copy the Key value above and paste it into\n"
                "Registration -> Activate License Key on your site.\n"
            )
        )