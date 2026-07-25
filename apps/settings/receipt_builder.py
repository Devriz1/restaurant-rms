from decimal import Decimal


LINE_WIDTH = 42


def separator():
    return "-" * LINE_WIDTH


def center(text):
    return text.center(LINE_WIDTH)


def money(value):

    if value is None:
        value = Decimal("0.00")

    return f"₹ {value:.2f}"


def build_receipt(bill):

    lines = []

    # ======================================
    # HEADER
    # ======================================

    lines.append(center("YOUR RESTAURANT"))
    lines.append(center("Restaurant Management System"))
    lines.append(separator())

    lines.append(f"Bill No : {bill.bill_number}")
    lines.append(
        f"Date    : {bill.created_at.strftime('%d-%m-%Y %I:%M %p')}"
    )

    lines.append(
        f"Table   : {bill.session.table.display_name}"
    )

    lines.append(
        f"Guest   : {bill.guest_order.guest_number}"
    )

    lines.append(
        f"Cashier : {bill.created_by.get_username()}"
    )

    lines.append(separator())

    # ======================================
    # ITEMS
    # ======================================

    order_items = bill.guest_order.items.select_related(
        "menu_item"
    )

    for item in order_items:

        name = item.menu_item.name

        qty = item.quantity

        price = item.unit_price

        total = item.line_total

        lines.append(name[:30])

        lines.append(
            f"{qty} x {price:.2f}".ljust(22)
            + f"{total:.2f}".rjust(20)
        )

    lines.append(separator())

    # ======================================
    # TOTALS
    # ======================================

    lines.append(
        "Subtotal".ljust(22)
        + money(bill.subtotal).rjust(20)
    )

    lines.append(
        "Discount".ljust(22)
        + money(bill.discount_amount).rjust(20)
    )

    lines.append(
        "Service".ljust(22)
        + money(bill.service_charge).rjust(20)
    )

    lines.append(
        "Tax".ljust(22)
        + money(bill.tax).rjust(20)
    )

    lines.append(separator())

    lines.append(
        "GRAND TOTAL".ljust(22)
        + money(bill.grand_total).rjust(20)
    )

    lines.append(separator())

    # ======================================
    # PAYMENT
    # ======================================

    payment = bill.payments.first()

    if payment:

        lines.append(
            f"Payment : {payment.get_payment_method_display()}"
        )

        if payment.reference_number:

            lines.append(
                f"Ref No  : {payment.reference_number}"
            )

    lines.append("")
    lines.append(center("THANK YOU"))
    lines.append(center("VISIT AGAIN"))
    lines.append(separator())

    return "\n".join(lines)