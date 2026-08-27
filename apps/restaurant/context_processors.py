from apps.restaurant.models import Restaurant


def currency_context(request):
    restaurant = Restaurant.objects.first()
    return {
        "currency_symbol": restaurant.currency_symbol if restaurant else "₹",
        "currency_code": restaurant.currency if restaurant else "INR",
        "timezone": restaurant.timezone if restaurant else "Asia/Kolkata",
    }
