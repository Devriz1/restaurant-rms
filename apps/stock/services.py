from decimal import Decimal

from .models import StockLedger


def add_stock(
    material,
    quantity,
    movement_type,
    reference="",
    remarks="",
):

    quantity = Decimal(str(quantity))

    material.current_stock += quantity

    material.save(
        update_fields=[
            "current_stock",
            "updated_at",
        ]
    )

    StockLedger.objects.create(
        material=material,
        movement_type=movement_type,
        reference_number=reference,
        quantity_in=quantity,
        quantity_out=Decimal("0.00"),
        balance=material.current_stock,
        remarks=remarks,
    )


def remove_stock(
    material,
    quantity,
    movement_type,
    reference="",
    remarks="",
):

    quantity = Decimal(str(quantity))

    if quantity > material.current_stock:

        raise ValueError(
            "Insufficient stock."
        )

    material.current_stock -= quantity

    material.save(
        update_fields=[
            "current_stock",
            "updated_at",
        ]
    )

    StockLedger.objects.create(
        material=material,
        movement_type=movement_type,
        reference_number=reference,
        quantity_in=Decimal("0.00"),
        quantity_out=quantity,
        balance=material.current_stock,
        remarks=remarks,
    )


# ==========================================================
# STOCK ADJUSTMENT
# ==========================================================

def adjust_stock(
    material,
    quantity,
    adjustment_type,
    reason="",
    remarks="",
):

    quantity = Decimal(str(quantity))

    if quantity <= 0:

        raise ValueError(
            "Adjustment quantity must be greater than zero."
        )

    # ======================================================
    # INCREASE STOCK
    # ======================================================

    if adjustment_type == "INCREASE":

        material.current_stock += quantity

        material.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        StockLedger.objects.create(
            material=material,
            movement_type="ADJUSTMENT",
            reference_number="",
            quantity_in=quantity,
            quantity_out=Decimal("0.00"),
            balance=material.current_stock,
            remarks=(
                f"{reason}"
                + (
                    f" - {remarks}"
                    if remarks
                    else ""
                )
            ),
        )

        return material


    # ======================================================
    # DECREASE STOCK
    # ======================================================

    if adjustment_type == "DECREASE":

        if quantity > material.current_stock:

            raise ValueError(
                "Cannot decrease stock below zero."
            )

        material.current_stock -= quantity

        material.save(
            update_fields=[
                "current_stock",
                "updated_at",
            ]
        )

        StockLedger.objects.create(
            material=material,
            movement_type="ADJUSTMENT",
            reference_number="",
            quantity_in=Decimal("0.00"),
            quantity_out=quantity,
            balance=material.current_stock,
            remarks=(
                f"{reason}"
                + (
                    f" - {remarks}"
                    if remarks
                    else ""
                )
            ),
        )

        return material


    raise ValueError(
        "Invalid stock adjustment type."
    )