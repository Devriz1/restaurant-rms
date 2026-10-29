from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from apps.accounts.views import UserLoginView

view = UserLoginView()
view.request = RequestFactory().get('/accounts/login/')
SessionMiddleware(lambda x: None).process_request(view.request)
MessageMiddleware(lambda x: None).process_request(view.request)
form = view.get_form()
html = form['period'].as_widget()
print('has FY 2025-26:', 'FY 2025-26' in html)
print('has selected:', 'selected' in html)
print('has Active:', 'Active' in html)
print('length:', len(html))