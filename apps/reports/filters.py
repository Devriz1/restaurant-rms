from datetime import timedelta

from django.db.models import Q
from django.utils import timezone


def apply_report_filters(request, queryset):

    today = timezone.localdate()

    # Default to Today
    range_filter = request.GET.get("range", "today")

    from_date = request.GET.get("from_date")

    to_date = request.GET.get("to_date")

    search = request.GET.get("search")

    # ----------------------------------
    # QUICK FILTERS
    # ----------------------------------
# TODAY
    if range_filter == "today":

        queryset = queryset.filter(
        created_at__date=today
    )

# YESTERDAY
    elif range_filter == "yesterday":

        queryset = queryset.filter(
        created_at__date=today - timedelta(days=1)
    )

# LAST 7 DAYS
    elif range_filter == "week":

        queryset = queryset.filter(
        created_at__date__gte=today - timedelta(days=6)
    )

# THIS MONTH
    elif range_filter == "month":

        queryset = queryset.filter(
        created_at__year=today.year,
        created_at__month=today.month,
    )

# LAST MONTH
    elif range_filter == "last_month":

        first_day = today.replace(day=1)

        last_month = first_day - timedelta(days=1)

        queryset = queryset.filter(
            created_at__year=last_month.year,
            created_at__month=last_month.month,
        )

# THIS YEAR
    elif range_filter == "year":

        queryset = queryset.filter(
        created_at__year=today.year
    )

# ALL
    elif range_filter == "all":

        pass
    # ----------------------------------
    # CUSTOM DATE
    # ----------------------------------

    if from_date:

        queryset = queryset.filter(
            created_at__date__gte=from_date
        )

    if to_date:

        queryset = queryset.filter(
            created_at__date__lte=to_date
        )


    # ----------------------------------
    # SEARCH
    # ----------------------------------

    if search:

        queryset = queryset.filter(

            Q(bill_number__icontains=search)

            |

            Q(session__table__display_name__icontains=search)

            |

            Q(guest_order__guest_number__icontains=search)

        )


    return queryset