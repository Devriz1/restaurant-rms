from django.urls import path

from . import views


app_name = "settings"


urlpatterns = [

    path(

        "printer-settings/",

        views.printer_settings,

        name="printer-settings",

    ),
    path(
    "printer-settings/test/",
    views.test_printer,
    name="test-printer",
),

]