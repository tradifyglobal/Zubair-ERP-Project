from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class MyAccountAdapter(DefaultAccountAdapter):
    """Custom adapter to control where users are redirected after login.

    This keeps the rest of allauth's behavior intact (including email
    verification), but ensures the login redirect goes to
    `settings.LOGIN_REDIRECT_URL` (set to `/dashboard/` in settings.py).
    """

    def get_login_redirect_url(self, request):
        return getattr(settings, 'LOGIN_REDIRECT_URL', '/')
