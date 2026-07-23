from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.orders.models import GuestOrder

from .forms import BillForm
from .models import Bill, Payment


# ==========================================================
# BILLING DASHBOARD
# ==========================================================

@login_required
def dashboard(request):

    guests = (
    GuestOrder.objects
    .filter(
        status__in=[
            "open",
            "served",
        ],
        items__isnull=False,
    )
    .distinct()
        .select_related(
            "session",
            "session__table",
        )
        .prefetch_related(
            "items",
        )
        .order_by(
            "session__table__area",
            "session__table__table_number",
            "guest_number",
        )
    )

    return render(
        request,
        "billing/dashboard.html",
        {
            "guests": guests,
        },
    )



# ==========================================================
# BILLING SCREEN
# ==========================================================

@login_required
@transaction.atomic
def billing_screen(request, guest_id):

    guest = get_object_or_404(
        GuestOrder.objects
        .select_related(
            "session",
            "session__table",
            "session__table__area",
        )
        .prefetch_related(
            "items",
            "items__menu_item",
        ),
        id=guest_id,
    )


    # ------------------------------------------
    # CREATE BILL IF NOT EXISTS
    # ------------------------------------------

    bill, created = Bill.objects.get_or_create(

        guest_order=guest,

        defaults={

            "session": guest.session,

            "created_by": request.user,

        },

    )


    form = BillForm(
        request.POST or None,
        instance=bill,
    )


    # ------------------------------------------
    # POST ACTIONS
    # ------------------------------------------

    if request.method == "POST":


        action = request.POST.get(
            "action"
        )


        if form.is_valid():


            bill = form.save(
                commit=False
            )


            bill.calculate_totals()

            bill.save()



            # ===============================
            # UPDATE BILL
            # ===============================

            if action == "update_bill":


                messages.success(
                    request,
                    "Bill updated successfully.",
                )


                return redirect(
                    "billing:billing-screen",
                    guest.id,
                )



            # ===============================
            # COMPLETE PAYMENT
            # ===============================

            if action == "complete_payment":


                amount = request.POST.get(
                    "amount"
                )


                if not amount:

                    amount = bill.grand_total


                amount = Decimal(
                    amount
                )


                Payment.objects.create(

                    bill=bill,

                    payment_method=request.POST.get(
                        "payment_method",
                        "cash",
                    ),

                    amount=amount,

                    reference_number=request.POST.get(
                        "reference_number",
                        "",
                    ),

                    received_by=request.user,

                )



                bill.status = "paid"

                bill.paid_at = timezone.now()

                bill.save()



                guest.status = "paid"

                guest.save()



                # --------------------------------
                # CLOSE TABLE SESSION
                # --------------------------------

                remaining = (
                    guest.session
                    .guest_orders
                    .exclude(
                        status="paid"
                    )
                    .exists()
                )


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
                    "billing:dashboard"
                )



    # ------------------------------------------
    # DISPLAY
    # ------------------------------------------

    context = {


        "guest": guest,


        "bill": bill,


        "form": form,


        "items": guest.items.all(),


    }


    return render(

        request,

        "billing/billing_screen.html",

        context,

    )