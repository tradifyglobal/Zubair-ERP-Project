from django.http import request
from django.shortcuts import redirect, render
from django.views import View   
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import TemplateView


# Create your views here.
class AppsView(LoginRequiredMixin,TemplateView):
    pass

#horizontal
apps_horizontal_horizontal_view = AppsView.as_view(template_name="apps/horizontal/horizontal.html")

#Authentication
apps_authentication_auth_login_view = AppsView.as_view(template_name="apps/authentication/auth-login.html")
apps_authentication_auth_register_view = AppsView.as_view(template_name="apps/authentication/auth-register.html")
apps_authentication_auth_recoverpassword_view= AppsView.as_view(template_name="apps/authentication/auth-recoverpassword.html")
apps_authentication_auth_lockscreen_view= AppsView.as_view(template_name="apps/authentication/auth-lockscreen.html")
apps_authentication_auth_logout_view = AppsView.as_view(template_name="apps/authentication/auth-logout.html")
apps_authentication_auth_confirm_mail_view = AppsView.as_view(template_name="apps/authentication/auth-confirm-mail.html")
apps_authentication_auth_email_verification_view = AppsView.as_view(template_name="apps/authentication/auth-email-verification.html")
apps_authentication_auth_two_step_verification_view = AppsView.as_view(template_name="apps/authentication/auth-two-step-verification.html")