from decimal import Decimal

from .models import StockLedger
from apps.inventory.models import Material


def add_stock(
    material,
    quantity,
    movement_type,
    reference="",
    remarks="",
):

    material.current_stock += Decimal(quantity)

    material.save(
        update_fields=["current_stock"],
    )

    StockLedger.objects.create(

        material=material,

        movement_type=movement_type,

        reference_number=reference,

        quantity_in=quantity,

        quantity_out=0,

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

    material.current_stock -= Decimal(quantity)

    material.save(
        update_fields=["current_stock"],
    )

    StockLedger.objects.create(

        material=material,

        movement_type=movement_type,

        reference_number=reference,

        quantity_in=0,

        quantity_out=quantity,

        balance=material.current_stock,

        remarks=remarks,

    )