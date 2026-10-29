import os
import tempfile
import subprocess
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

    @staticmethod
    def print_text(printer_name, text):
        """
        Send text to a Windows shared printer.

        Uses PowerShell's Out-Printer cmdlet to print to the specified
        Windows printer.  Falls back to a temporary file piped through
        notepad if the printer is unavailable.
        """

        if not printer_name:
            print("=" * 50)
            print("Printer : [NOT CONFIGURED]")
            print("=" * 50)
            print(text)
            print("=" * 50)
            return False

        try:
            # Write text to a temp file, then print it via PowerShell
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                delete=False,
                encoding="utf-8",
            ) as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            # Use PowerShell to write content to the printer
            # The printer name must match a Windows shared printer
            # Use a shorter timeout to avoid hanging on missing printers
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Get-Content -Path '{tmp_path}' | Out-Printer -Name '{printer_name}'",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            if result.returncode == 0:
                print(f"[PrinterManager] Printed to '{printer_name}' successfully.")
                return True
            else:
                print(f"[PrinterManager] Print failed for '{printer_name}': {result.stderr or 'Unknown error'}")
                return False

        except subprocess.TimeoutExpired:
            print(f"[PrinterManager] Print timed out for '{printer_name}'. Printer may not exist or be offline.")
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return False

        except Exception as e:
            print(f"[PrinterManager] Unexpected error printing to '{printer_name}': {e}")
            # Clean up temp file
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass
            return False

    @staticmethod
    def print_bill(receipt):
        printer = PrinterManager.get_settings().billing_printer

        if not printer:
            print("[PrinterManager] Billing printer not configured. Output to console:")
            print(receipt)
            return False

        return PrinterManager.print_text(printer, receipt)

    @staticmethod
    def print_kot(ticket):
        printer = PrinterManager.get_settings().kitchen_printer

        if not printer:
            print("[PrinterManager] Kitchen printer not configured. Output to console:")
            print(ticket)
            return False

        return PrinterManager.print_text(printer, ticket)

    @staticmethod
    def print_report(report):
        printer = PrinterManager.get_settings().report_printer

        if not printer:
            print("[PrinterManager] Report printer not configured. Output to console:")
            print(report)
            return False

        return PrinterManager.print_text(printer, report)