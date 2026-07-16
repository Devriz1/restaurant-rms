from django.contrib.auth.views import LoginView
from .forms import LoginForm


class UserLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True