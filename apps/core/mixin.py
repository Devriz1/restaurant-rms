from django.contrib.auth.mixins import LoginRequiredMixin


class BaseLoginRequiredMixin(LoginRequiredMixin):
    login_url = "login"