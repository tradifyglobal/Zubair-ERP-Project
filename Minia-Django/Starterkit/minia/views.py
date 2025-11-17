from django.http import request
from django.shortcuts import redirect, render
from django.views import View   
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,auth
from allauth.account.views import PasswordChangeView,PasswordSetView

class DashboardView(LoginRequiredMixin,View):
    def get(self, request):       
        return render(request, 'dashboard.html')
       
class PagesLockscreenView(View):
    def get(self, request):
        return render(request, 'account/lockscreen.html')

def logout(request):
    auth.logout(request)
    return render(request,'account/logout.html')



class MyPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    success_url = reverse_lazy('dashboard')        

class MyPasswordSetView(LoginRequiredMixin, PasswordSetView):
    success_url = reverse_lazy('dashboard')  
