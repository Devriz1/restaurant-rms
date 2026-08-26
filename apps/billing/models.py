from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Q
from apps.orders.models import GuestOrder, TableSession


class Customer(models.Model):
    customer_number = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=150, db_index=True)
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        permissions = [
            ("view_customer_ledger", "Can view customer ledger"),
            ("adjust_credit_ledger", "Can adjust credit ledger entries"),
            ("override_credit_limit", "Can override customer credit limit"),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.customer_number:
            self.customer_number = f"CUST-{self.pk:05d}"
            super().save(update_fields=['customer_number'])

    @property
    def current_outstanding(self) -> Decimal:
        """
        Calculates authoritative outstanding balance directly from the immutable ledger.
        Debit entries increase balance (+), Credit entries decrease balance (-).
        """
        aggregates = self.ledger_entries.aggregate(
            debits=Sum('amount', filter=Q(entry_type=CreditLedgerEntry.EntryType.DEBIT)),
            credits=Sum('amount', filter=Q(entry_type=CreditLedgerEntry.EntryType.CREDIT))
        )
        debits = aggregates['debits'] or Decimal('0.00')
        credits = aggregates['credits'] or Decimal('0.00')
        return debits - credits

    @property
    def balance(self) -> Decimal:
        """Alias for current_outstanding — the amount this customer currently owes."""
        return self.current_outstanding

    @property
    def is_credit_customer(self) -> bool:
        """True if this customer has a credit limit or has any ledger activity."""
        return (
            self.credit_limit > Decimal('0.00')
            or self.ledger_entries.exists()
        )

    @property
    def available_credit(self) -> Decimal:
        return max(Decimal('0.00'), self.credit_limit - self.current_outstanding)


class Bill(models.Model):

    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("partially_paid", "Partially Paid"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    DISCOUNT_TYPE_CHOICES = [
        ("amount", "Amount"),
        ("percent", "Percentage"),
    ]

    bill_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    guest_order = models.OneToOneField(
        GuestOrder,
        on_delete=models.PROTECT,
        related_name="bill",
    )

    session = models.ForeignKey(
        TableSession,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default="amount",
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    service_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unpaid",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_bills",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # String reference 'Customer' resolves the forward declaration issue
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True, related_name='bills')

    class Meta:
        ordering = ["-id"]

    @property
    def subtotal(self):
        return self.guest_order.subtotal

    @property
    def discount_amount(self):
        subtotal = self.subtotal
        if self.discount_type == "percent":
            amount = (subtotal * self.discount) / Decimal("100")
        else:
            amount = self.discount

        if amount > subtotal:
            amount = subtotal

        return amount

    def calculate_totals(self):
        self.grand_total = (
            self.subtotal
            - self.discount_amount
            + self.service_charge
            + self.tax
        )

        if self.grand_total < Decimal("0.00"):
            self.grand_total = Decimal("0.00")

    def save(self, *args, **kwargs):
        self.calculate_totals()

        if not self.bill_number:
            last_bill = Bill.objects.order_by("-id").first()
            if last_bill:
                try:
                    number = int(
                        last_bill.bill_number.replace("BILL", "")
                    ) + 1
                except ValueError:
                    number = last_bill.id + 1
            else:
                number = 1

            while Bill.objects.filter(bill_number=f"BILL{number:06d}").exists():
                number += 1

            self.bill_number = f"BILL{number:06d}"

        super().save(*args, **kwargs)

    @property
    def unpaid_balance(self) -> Decimal:
        # Fixed reference to grand_total instead of total_amount
        total_allocated = self.payment_allocations.aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
        return max(Decimal('0.00'), self.grand_total - total_allocated)

    def __str__(self):
        return self.bill_number


class Payment(models.Model):

    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("card", "Card"),
        ("credit", "Credit Ledger"),
    ]

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    paid_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-paid_at"]

    def __str__(self):
        return f"{self.bill.bill_number} ({self.payment_method})"


class DailyClosing(models.Model):
    date = models.DateField(unique=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    cash_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    upi_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    card_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    credit_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    closing_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total_bills = models.PositiveIntegerField(
        default=0
    )

    total_transactions = models.PositiveIntegerField(
        default=0
    )

    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    closed_at = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date}"


class CustomerPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        UPI = 'UPI', 'UPI'
        CARD = 'CARD', 'Card'
        OTHER = 'OTHER', 'Other'

    payment_number = models.CharField(max_length=30, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='received_customer_payments')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.payment_number:
            self.payment_number = f"PAY-{self.pk:06d}"
            super().save(update_fields=['payment_number'])

    def __str__(self):
        return f"{self.payment_number} - {self.customer.name} - ₹{self.amount}"


class CreditLedgerEntry(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT_SALE = 'CREDIT_SALE', 'Credit Sale'
        PAYMENT = 'PAYMENT', 'Customer Payment'
        ADJUSTMENT = 'ADJUSTMENT', 'Ledger Adjustment'
        REFUND = 'REFUND', 'Credit Refund'

    class EntryType(models.TextChoices):
        DEBIT = 'DEBIT', 'Debit (+ Outstanding)'
        CREDIT = 'CREDIT', 'Credit (- Outstanding)'

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='ledger_entries', db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    entry_type = models.CharField(max_length=10, choices=EntryType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_ledger_entries')
    customer_payment = models.ForeignKey(CustomerPayment, on_delete=models.SET_NULL, null=True, blank=True, related_name='ledger_entries')

    reference_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_ledger_entries')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def clean(self):
        if self.amount <= Decimal('0.00'):
            raise ValidationError("Ledger transaction amount must be greater than zero.")

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_type} - ₹{self.amount}"


class BillPaymentAllocation(models.Model):
    """Tracks which customer repayments cover which unpaid bills."""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payment_allocations')
    customer_payment = models.ForeignKey(CustomerPayment, on_delete=models.CASCADE, related_name='allocations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocated_at = models.DateTimeField(auto_now_add=True)