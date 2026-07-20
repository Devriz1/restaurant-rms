from django.contrib import admin

from .models import Bill, BillItem, Payment


admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(Payment)