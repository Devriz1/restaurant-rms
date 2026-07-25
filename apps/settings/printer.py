from .models import PrinterSetting


class PrinterManager:

    @staticmethod
    def get_settings():

        settings = PrinterSetting.objects.first()

        if settings is None:
            raise Exception("Printer settings not configured.")

        return settings


    @staticmethod
    def get_billing_printer():

        return PrinterManager.get_settings().billing_printer


    @staticmethod
    def get_kitchen_printer():

        return PrinterManager.get_settings().kitchen_printer


    @staticmethod
    def get_report_printer():

        return PrinterManager.get_settings().report_printer

class PrinterManager:

    # existing methods above...

    @staticmethod
    def print_text(printer_name, text):

        """
        Generic printer function.

        This will later send data directly
        to the Windows shared printer.
        """

        print("=" * 50)
        print("Printer :", printer_name)
        print("=" * 50)
        print(text)
        print("=" * 50)

        return True

class PrinterManager:

    # previous methods...

    @staticmethod
    def print_bill(receipt):

        printer = PrinterManager.get_billing_printer()

        return PrinterManager.print_text(
            printer,
            receipt,
        )


    @staticmethod
    def print_kot(ticket):

        printer = PrinterManager.get_kitchen_printer()

        return PrinterManager.print_text(
            printer,
            ticket,
        )


    @staticmethod
    def print_report(report):

        printer = PrinterManager.get_report_printer()

        return PrinterManager.print_text(
            printer,
            report,
        )