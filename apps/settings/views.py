from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import PrinterSettingForm
from .models import PrinterSetting


@login_required
def printer_settings(request):

    settings = PrinterSetting.objects.first()

    if settings is None:

        settings = PrinterSetting.objects.create()

    if request.method == "POST":

        form = PrinterSettingForm(
            request.POST,
            instance=settings,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Printer settings saved successfully."
            )

            return redirect(
                "settings:printer-settings"
            )

    else:

        form = PrinterSettingForm(
            instance=settings,
        )

    context = {

        "form": form,
        "settings": settings,

    }

    return render(
        request,
        "settings/printer_settings.html",
        context,
    )


@login_required
def test_printer(request):

    from apps.settings.printer import PrinterManager

    settings = PrinterSetting.objects.first()

    if settings is None:

        return HttpResponse(
            "Printer settings are not configured.",
            content_type="text/plain",
        )

    test_output = """=========================================
      RMS PRINTER TEST
=========================================

This is a test print from Restaurant RMS.

Billing Printer
---------------
{ billing_printer }

Kitchen Printer
---------------
{ kitchen_printer }

Report Printer
--------------
{ report_printer }

=========================================
Printer communication test complete.
=========================================
""".format(
        billing_printer=settings.billing_printer or "Not Configured",
        kitchen_printer=settings.kitchen_printer or "Not Configured",
        report_printer=settings.report_printer or "Not Configured",
    )

    # Attempt to print test page
    result = None

    if settings.billing_printer:
        result = PrinterManager.print_text(settings.billing_printer, test_output)
        if result:
            return HttpResponse(
                f"Test page sent to billing printer '{settings.billing_printer}'.",
                content_type="text/plain",
            )
        else:
            return HttpResponse(
                f"Failed to print to '{settings.billing_printer}'. Check printer connection.",
                content_type="text/plain",
            )

    return HttpResponse(
        test_output,
        content_type="text/plain",
    )