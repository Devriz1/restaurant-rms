import shutil
from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from apps.accounts.decorators import permission_required

@login_required
@permission_required("backup.view")
def dashboard(request):

    backup_folder = Path(settings.BASE_DIR) / "backups"

    backup_folder.mkdir(
        exist_ok=True,
    )

    backups = []

    total_size = 0

    for file in sorted(
        backup_folder.glob("*.sqlite3"),
        reverse=True,
    ):

        size = file.stat().st_size

        total_size += size

        # Default to file modified time
        created = timezone.localtime(
            timezone.datetime.fromtimestamp(
                file.stat().st_mtime,
                tz=timezone.get_current_timezone(),
            )
        )

        # If this is a normal backup file, use the timestamp in its filename
        if file.stem.startswith("backup_"):

            try:

                timestamp = file.stem.replace(
                    "backup_",
                    "",
                )

                created = timezone.make_aware(
                    datetime.strptime(
                        timestamp,
                        "%Y%m%d_%H%M%S",
                    ),
                    timezone.get_current_timezone(),
                )

            except ValueError:

                pass

        backups.append({

            "name": file.name,

            "size": round(
                size / (1024 * 1024),
                2,
            ),

            "created": timezone.localtime(
                created,
            ),

        })

    context = {

        "backups": backups,

        "backup_count": len(backups),

        "total_size": round(
            total_size / (1024 * 1024),
            2,
        ),

        "latest_backup": backups[0] if backups else None,

    }

    return render(
        request,
        "backup/dashboard.html",
        context,
    )
@login_required
@permission_required("backup.create")
def create_backup(request):

    database_file = Path(settings.BASE_DIR) / "db.sqlite3"

    backup_folder = Path(settings.BASE_DIR) / "backups"

    backup_folder.mkdir(
        exist_ok=True,
    )

    timestamp = timezone.localtime().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = backup_folder / (
        f"backup_{timestamp}.sqlite3"
    )

    shutil.copy2(
        database_file,
        backup_file,
    )

    messages.success(
        request,
        f"Backup created successfully: {backup_file.name}"
    )

    return redirect(
        "backup:dashboard",
    )


@login_required
def download_backup(request, filename):

    backup_file = (
        Path(settings.BASE_DIR)
        / "backups"
        / filename
    )

    if not backup_file.exists():

        raise Http404()

    return FileResponse(

        open(backup_file, "rb"),

        as_attachment=True,

        filename=filename,

    )


@login_required
@require_POST
def delete_backup(request, filename):

    backup_file = (
        Path(settings.BASE_DIR)
        / "backups"
        / filename
    )

    if backup_file.exists():

        backup_file.unlink()

        messages.success(

            request,

            "Backup deleted successfully.",

        )

    else:

        messages.error(

            request,

            "Backup not found.",

        )

    return redirect(
        "backup:dashboard"
    )


@login_required
@permission_required("backup.restore")
def restore_backup(request, filename):
    backup_folder = Path(settings.BASE_DIR) / "backups"

    backup_file = backup_folder / filename

    if not backup_file.exists():

        messages.error(
            request,
            "Backup not found.",
        )

        return redirect("backup:dashboard")

    if request.method == "POST":

        database = Path(settings.BASE_DIR) / "db.sqlite3"

        safety_name = (
            "before_restore_"
            + timezone.localtime().strftime("%Y%m%d_%H%M%S")
            + ".sqlite3"
        )

        shutil.copy2(
            database,
            backup_folder / safety_name,
        )

        shutil.copy2(
            backup_file,
            database,
        )

        messages.success(

            request,

            "Database restored successfully. Restart the server."

        )

        return redirect(
            "backup:dashboard"
        )

    return render(

        request,

        "backup/restore_confirm.html",

        {

            "filename": filename,

        },

    )