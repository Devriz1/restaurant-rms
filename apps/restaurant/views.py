from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import Restaurant
from .forms import RestaurantForm


class RestaurantSettingsView(UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurant/settings.html"
    success_url = reverse_lazy("restaurant:settings")

    def get_object(self, queryset=None):
        obj, created = Restaurant.objects.get_or_create(
            pk=1,
            defaults={
                "name": "My Restaurant"
            }
        )
        return obj