from django.urls import path

from .views import (

    apps_horizontal_horizontal_view,

    apps_authentication_auth_login_view,
    apps_authentication_auth_register_view,
    apps_authentication_auth_recoverpassword_view,
    apps_authentication_auth_lockscreen_view,
    apps_authentication_auth_logout_view,
    apps_authentication_auth_confirm_mail_view,
    apps_authentication_auth_email_verification_view,
    apps_authentication_auth_two_step_verification_view
)

app_name = "apps"
urlpatterns = [
    
    #Horizontal
    path("horizontal", view=apps_horizontal_horizontal_view, name="horizontal"),

    #Authentication 
    path("authentication/auth-login", view=apps_authentication_auth_login_view, name="authentication.auth-login"),
    path("authentication/auth-register", view=apps_authentication_auth_register_view, name="authentication.auth-register"),
    path("authentication/auth-recoverpassword", view=apps_authentication_auth_recoverpassword_view, name="authentication.auth-recoverpassword"),
    path("authentication/auth-lockscreen", view=apps_authentication_auth_lockscreen_view, name="authentication.auth-lockscreen"),
    path("authentication/auth-logout", view=apps_authentication_auth_logout_view, name="authentication.auth-logout"),
    path("authentication/auth-confirm-mail", view=apps_authentication_auth_confirm_mail_view, name="authentication.auth-confirm-mail"),
    path("authentication/auth-email-verification", view=apps_authentication_auth_email_verification_view, name="authentication.auth-email-verification"),
    path("authentication/auth-two-step-verification", view=apps_authentication_auth_two_step_verification_view, name="authentication.auth-two-step-verification"),

]