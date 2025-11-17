from django.http import request
from django.shortcuts import redirect, render
from django.views import View   
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import TemplateView

User = get_user_model()

class PagesView(LoginRequiredMixin,TemplateView):
    pass
 
pages_starterpage_view = PagesView.as_view(template_name="pages/starterpage.html")
pages_maintenance_view = PagesView.as_view(template_name="pages/maintenance.html")
pages_comingsoon_view = PagesView.as_view(template_name="pages/comingsoon.html")
pages_timeline_view = PagesView.as_view(template_name="pages/timeline.html")
pages_faqs_view = PagesView.as_view(template_name="pages/faqs.html")
pages_pricing_view = PagesView.as_view(template_name="pages/pricing.html")
pages_404_error_view = PagesView.as_view(template_name="pages/404error.html")
pages_500_error_view = PagesView.as_view(template_name="pages/500error.html")