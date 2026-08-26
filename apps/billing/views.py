from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.orders.models import GuestOrder
from apps.settings.printer import PrinterManager
from apps.settings.receipt_builder import build_receipt

from .forms import BillForm
from .models import Bill, Customer, CreditLedgerEntry, CustomerPayment, Payment


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
                "preparing",
                "ready",
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

    # ======================================================
    # CREATE BILL IF NOT EXISTS
    # ======================================================

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

    # ======================================================
    # POST
    # ======================================================

    if request.method == "POST":

        action = request.POST.get("action")

        if form.is_valid():

            bill = form.save(commit=False)

            # Assign customer if selected in POS
            customer_id = request.POST.get("customer")
            if customer_id:
                customer_obj = Customer.objects.filter(id=customer_id, is_active=True).first()
                bill.customer = customer_obj
            else:
                bill.customer = None

            bill.calculate_totals()
            bill.save()

            # ==========================================
            # UPDATE BILL ONLY
            # ==========================================

            if action == "update_bill":

                messages.success(
                    request,
                    "Bill updated successfully."
                )

                return redirect(
                    "billing:billing-screen",
                    guest.id,
                )

            # ==========================================
            # COMPLETE PAYMENT
            # ==========================================

            if action == "complete_payment":

                payment_method = request.POST.get("payment_method", "cash").lower()
                amount_str = request.POST.get("amount")

                if not amount_str:
                    amount = bill.grand_total
                else:
                    amount = Decimal(amount_str)

                # --- VALIDATION FOR CREDIT PAYMENTS ---
                if payment_method == "credit":
                    if not bill.customer:
                        messages.error(
                            request,
                            "A valid Customer must be selected for Credit / Ledger transactions."
                        )
                        return redirect(
                            "billing:billing-screen",
                            guest.id
                        )

                    # Verify Credit Limit — warn but do NOT block the sale
                    if bill.customer.available_credit < amount:
                        messages.warning(
                            request,
                            f"Credit limit exceeded! Customer available credit: ₹{bill.customer.available_credit}. "
                            f"Proceeding with credit sale anyway."
                        )

                # Record Payment Entry
                payment = Payment.objects.create(
                    bill=bill,
                    payment_method=payment_method,
                    amount=amount,
                    reference_number=request.POST.get("reference_number", ""),
                    received_by=request.user,
                )

                # --- RECORD CREDIT LEDGER ENTRY (DEBIT) ---
                if payment_method == "credit" and bill.customer:
                    CreditLedgerEntry.objects.create(
                        customer=bill.customer,
                        transaction_type=CreditLedgerEntry.TransactionType.CREDIT_SALE,
                        entry_type=CreditLedgerEntry.EntryType.DEBIT,
                        amount=amount,
                        bill=bill,
                        reference_number=bill.bill_number,
                        description=f"Credit Sale - Bill #{bill.bill_number}",
                        created_by=request.user,
                    )

                # ======================================
                # MARK BILL AS PAID
                # ======================================
                bill.status = "paid"
                bill.paid_at = timezone.now()
                bill.save()

                # ======================================
                # MARK GUEST AS PAID
                # ======================================
                guest.status = "paid"
                guest.save()

                # ======================================
                # PRINT RECEIPT
                # ======================================
                try:
                    receipt = build_receipt(bill)
                    PrinterManager.print_bill(receipt)
                except Exception as e:
                    print("=" * 60)
                    print("Receipt Printing Failed")
                    print(e)
                    print("=" * 60)

                # ======================================
                # CLOSE SESSION IF NO ACTIVE GUESTS
                # ======================================
                session = guest.session

                active_guests = session.guest_orders.filter(
                    status__in=[
                        "open",
                        "preparing",
                        "ready",
                        "served",
                    ]
                ).exists()

                if not active_guests:

                    session.status = "closed"
                    session.closed_at = timezone.now()
                    session.save()

                    table = session.table
                    table.status = "available"
                    table.save()

                messages.success(
                    request,
                    "Payment completed successfully."
                )

                return redirect(
                    "billing:dashboard"
                )

    # Fetch all active customers for selection
    customers = Customer.objects.filter(is_active=True).order_by("name")

    context = {
        "guest": guest,
        "bill": bill,
        "form": form,
        "items": guest.items.all(),
        "customers": customers,
    }

    return render(
        request,
        "billing/billing_screen.html",
        context,
    )


# ==========================================================
# CUSTOMER LEDGER VIEWS
# ==========================================================

@login_required
def customer_list(request):
    """Handles both Customer Creation (POST) and Customer Listing (GET)."""
    
    # --- Handle Creation POST Request from Modal ---
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip() or None
        email = request.POST.get('email', '').strip() or None
        address = request.POST.get('address', '').strip() or None
        is_credit_customer = request.POST.get('is_credit_customer') == 'on'
        credit_limit = request.POST.get('credit_limit', '0.00')
        opening_balance_str = request.POST.get('opening_balance', '0.00')
        notes = request.POST.get('notes', '').strip() or None

        if not name:
            messages.error(request, "Customer name is required.")
            return redirect('billing:customer_list')

        try:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                address=address,
                credit_limit=Decimal(credit_limit) if is_credit_customer and credit_limit else Decimal('0.00'),
                notes=notes,
                is_active=True
            )

            # Record opening balance as a DEBIT entry if provided
            opening_balance = Decimal(opening_balance_str) if opening_balance_str else Decimal('0.00')
            if opening_balance > Decimal('0.00'):
                CreditLedgerEntry.objects.create(
                    customer=customer,
                    transaction_type=CreditLedgerEntry.TransactionType.ADJUSTMENT,
                    entry_type=CreditLedgerEntry.EntryType.DEBIT,
                    amount=opening_balance,
                    description=f"Opening balance - {customer.name}",
                    reference_number=customer.customer_number,
                    created_by=request.user,
                )

            if is_credit_customer:
                messages.success(request, f"Credit customer '{customer.name}' created successfully!")
            else:
                messages.success(request, f"Customer '{customer.name}' created successfully!")
        except IntegrityError:
            messages.error(request, f"Customer creation failed. Phone number '{phone}' is already registered.")
        except Exception as e:
            messages.error(request, f"Error creating customer: {str(e)}")

        return redirect('billing:customer_list')

    # --- Handle Customer Listing Search (GET) ---
    query = request.GET.get('q', '').strip()
    customers = Customer.objects.filter(is_active=True).order_by("name")

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(customer_number__icontains=query)
        )

    # FIXED: Compute total balance by summing properties across filtered customers in Python
    customer_list_objs = list(customers)
    total_balance = sum((c.current_outstanding for c in customer_list_objs), Decimal('0.00'))
    active_customers_count = len(customer_list_objs)

    return render(request, 'billing/customers/customer_list.html', {
        'customers': customer_list_objs,
        'total_balance': total_balance,
        'active_customers_count': active_customers_count,
        'query': query,
    })


@login_required
def customer_detail(request, pk):
    """Displays customer profile and running transaction history/ledger statement."""
    customer = get_object_or_404(Customer, pk=pk)
    entries = customer.ledger_entries.select_related('created_by', 'bill', 'customer_payment').all()

    # Build chronological running balance
    running_balance = Decimal('0.00')
    entries_with_balance = []

    for entry in reversed(list(entries)):
        if entry.entry_type == CreditLedgerEntry.EntryType.DEBIT:
            running_balance += entry.amount
        else:
            running_balance -= entry.amount
        entries_with_balance.append((entry, running_balance))

    entries_with_balance.reverse()  # Newest transactions first

    return render(request, 'billing/customers/customer_detail.html', {
        'customer': customer,
        'outstanding': customer.current_outstanding,
        'available_credit': customer.available_credit,
        'entries_with_balance': entries_with_balance,
    })


@login_required
@transaction.atomic
def receive_customer_payment(request, pk):
    """Processes repayments from credit customers and updates their ledger."""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', '0.00'))
        payment_method = request.POST.get('payment_method', 'CASH').upper()
        reference_number = request.POST.get('reference_number', '')
        notes = request.POST.get('notes', '')

        if amount <= Decimal('0.00'):
            messages.error(request, "Payment amount must be greater than zero.")
            return redirect('billing:receive_customer_payment', pk=customer.pk)

        # Record customer repayment
        cust_payment = CustomerPayment.objects.create(
            customer=customer,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            received_by=request.user,
        )

        # Create Credit entry in customer ledger
        CreditLedgerEntry.objects.create(
            customer=customer,
            transaction_type=CreditLedgerEntry.TransactionType.PAYMENT,
            entry_type=CreditLedgerEntry.EntryType.CREDIT,
            amount=amount,
            customer_payment=cust_payment,
            reference_number=reference_number or cust_payment.payment_number,
            description=f"Payment received via {payment_method}",
            created_by=request.user,
        )

        messages.success(request, f"Successfully recorded payment of ₹{amount} for {customer.name}.")
        return redirect('billing:customer_detail', pk=customer.pk)

    return render(request, 'billing/customers/receive_payment.html', {
        'customer': customer,
        'outstanding': customer.current_outstanding,
    })