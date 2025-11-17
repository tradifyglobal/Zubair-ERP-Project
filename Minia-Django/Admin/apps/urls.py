from django.urls import path

from .views import (
    apps_calendar_calendar_view,

    apps_chat_chat_view,

    apps_email_inbox_view,
    apps_email_read_view,

    apps_invoice_list_view,
    apps_invoice_details_view,

    apps_contacts_usergrid_view,
    apps_contacts_userlist_view,
    apps_contacts_profile_view,
    apps_horizontal_horizontal_view,

    apps_blogs_grid_view,
    apps_blogs_list_view,
    apps_blogs_details_view,

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
    # calendar
    path("calendar", view=apps_calendar_calendar_view, name="calendar"),
    #chat
    path("chat",view=apps_chat_chat_view,name="chat"),

    #Email
    path("email/inbox", view=apps_email_inbox_view, name="email.inbox"),
    path("emial/read_email", view=apps_email_read_view ,name="email.read"),

    #Invoice
    path("invoice/invoice_list", view=apps_invoice_list_view, name="invoice.list"),
    path("invoice/invoice_details", view=apps_invoice_details_view, name="invoice.details"),

    #Contacts
    path("contacts/user_grid", view=apps_contacts_usergrid_view, name="contacts.usergrid"),
    path("contacts/user_list", view=apps_contacts_userlist_view, name="contacts.userlist"),
    path("contacts/profile", view=apps_contacts_profile_view, name="contacts.profile"),

    #Blogs
    path("blogs/grid", view=apps_blogs_grid_view, name="blogs.grid"),
    path("blogs/list", view=apps_blogs_list_view, name="blogs.list"),
    path("blogs/details", view=apps_blogs_details_view, name="blogs.details"),


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