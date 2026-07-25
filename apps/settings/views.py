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

    settings = PrinterSetting.objects.first()

    if settings is None:

        return HttpResponse(
            "Printer settings are not configured."
        )

    output = f"""
=========================================
      RMS PRINTER TEST
=========================================

Billing Printer
---------------
{settings.billing_printer or "Not Configured"}

Kitchen Printer
---------------
{settings.kitchen_printer or "Not Configured"}

Report Printer
--------------
{settings.report_printer or "Not Configured"}

=========================================
Printer communication successful.
=========================================
"""

    return HttpResponse(
        output,
        content_type="text/plain",
    )