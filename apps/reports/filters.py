from datetime import date, timedelta

from django.db.models import Q


def apply_report_filters(
    request,
    queryset,
    date_field="created_at",
    search_fields=None,
):

    if search_fields is None:
        search_fields = []

    # ===========================
    # Quick Date Filters
    # ===========================

    today = date.today()

    report_range = request.GET.get("range")

    if report_range == "today":

        queryset = queryset.filter(
            **{f"{date_field}__date": today}
        )

    elif report_range == "yesterday":

        queryset = queryset.filter(
            **{
                f"{date_field}__date":
                today - timedelta(days=1)
            }
        )

    elif report_range == "week":

        queryset = queryset.filter(
            **{
                f"{date_field}__date__gte":
                today - timedelta(days=6)
            }
        )

    elif report_range == "month":

        queryset = queryset.filter(
            **{
                f"{date_field}__year": today.year,
                f"{date_field}__month": today.month,
            }
        )

    elif report_range == "last_month":

        if today.month == 1:

            month = 12
            year = today.year - 1

        else:

            month = today.month - 1
            year = today.year

        queryset = queryset.filter(
            **{
                f"{date_field}__year": year,
                f"{date_field}__month": month,
            }
        )

    elif report_range == "year":

        queryset = queryset.filter(
            **{
                f"{date_field}__year":
                today.year
            }
        )

    # ===========================
    # Custom Dates
    # ===========================

    from_date = request.GET.get("from_date")

    if from_date:

        queryset = queryset.filter(
            **{
                f"{date_field}__date__gte":
                from_date
            }
        )

    to_date = request.GET.get("to_date")

    if to_date:

        queryset = queryset.filter(
            **{
                f"{date_field}__date__lte":
                to_date
            }
        )

    # ===========================
    # Search
    # ===========================

    search = request.GET.get("search")

    if search and search_fields:

        query = Q()

        for field in search_fields:

            query |= Q(
                **{
                    f"{field}__icontains":
                    search
                }
            )

        queryset = queryset.filter(query)

    return queryset