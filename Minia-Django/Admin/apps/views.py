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
#calendar    
apps_calendar_calendar_view = AppsView.as_view(template_name="apps/calendar/calendar.html")
#chat
apps_chat_chat_view = AppsView.as_view(template_name="apps/chat/chat.html")

#Email
apps_email_inbox_view=AppsView.as_view(template_name="apps/email/inbox.html")
apps_email_read_view=AppsView.as_view(template_name="apps/email/read_email.html")

#Invoices
apps_invoice_list_view=AppsView.as_view(template_name="apps/invoices/invoice_list.html")
apps_invoice_details_view=AppsView.as_view(template_name="apps/invoices/invoice_details.html")

#Contacts
apps_contacts_usergrid_view = AppsView.as_view(template_name="apps/contacts/usergrid.html")
apps_contacts_userlist_view = AppsView.as_view(template_name="apps/contacts/userlist.html")
apps_contacts_profile_view = AppsView.as_view(template_name="apps/contacts/profile.html")

#Blogs
apps_blogs_grid_view = AppsView.as_view(template_name="apps/blogs/grid.html")
apps_blogs_list_view = AppsView.as_view(template_name="apps/blogs/list.html")
apps_blogs_details_view = AppsView.as_view(template_name="apps/blogs/details.html")


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