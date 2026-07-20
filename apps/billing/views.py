from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.orders.models import GuestOrder

from .forms import BillForm
from .models import Bill, BillItem, Payment


@login_required
def dashboard(request):

    guests = (
        GuestOrder.objects.filter(
            status="open",
            kots__isnull=False,
        )
        .distinct()
        .select_related(
            "session",
            "session__table",
        )
    )

    return render(
        request,
        "billing/dashboard.html",
        {
            "guests": guests,
        },
    )


@login_required
@transaction.atomic
def billing_screen(request, guest_id):

    guest = get_object_or_404(
        GuestOrder.objects.select_related(
            "session",
            "session__table",
        ),
        pk=guest_id,
    )

    bill, created = Bill.objects.get_or_create(
        guest_order=guest,
        defaults={
            "session": guest.session,
            "created_by": request.user,
        },
    )

    # -----------------------------------------
    # Rebuild Bill Items
    # -----------------------------------------

    bill.items.all().delete()

    for item in guest.items.select_related(
        "menu_item",
    ):

        BillItem.objects.create(
            bill=bill,
            menu_item_name=item.menu_item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
            notes=item.notes,
        )

    # -----------------------------------------
    # Calculate Totals
    # -----------------------------------------

    bill.calculate_totals()
    bill.save()

    # -----------------------------------------
    # Handle POST
    # -----------------------------------------

    if request.method == "POST":

        action = request.POST.get("action")

        form = BillForm(
            request.POST,
            instance=bill,
        )

        if form.is_valid():

            bill = form.save(
                commit=False,
            )

            bill.calculate_totals()

            if action == "update_bill":

                bill.save()

                messages.success(
                    request,
                    "Bill updated successfully.",
                )

                return redirect(
                    "billing:billing-screen",
                    guest_id=guest.id,
                )

            elif action == "complete_payment":

                bill.status = "paid"
                bill.paid_at = timezone.now()
                bill.save()

                Payment.objects.create(
                    bill=bill,
                    payment_method=request.POST.get(
                        "payment_method",
                        "cash",
                    ),
                    amount=request.POST.get(
                        "amount",
                        bill.grand_total,
                    ),
                    reference_number=request.POST.get(
                        "reference_number",
                        "",
                    ),
                    received_by=request.user,
                )

                guest.status = "paid"
                guest.save()

                remaining = guest.session.guest_orders.exclude(
                    status="paid",
                ).exists()

                if not remaining:

                    guest.session.status = "closed"
                    guest.session.closed_at = timezone.now()
                    guest.session.save()

                    table = guest.session.table
                    table.status = "available"
                    table.save()

                messages.success(
                    request,
                    "Payment completed successfully.",
                )

                return redirect(
                    "billing:dashboard",
                )

    else:

        form = BillForm(
            instance=bill,
        )

    return render(
        request,
        "billing/billing_screen.html",
        {
            "guest": guest,
            "bill": bill,
            "form": form,
            "items": bill.items.all(),
        },
    )