"""minia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
#from django.conf.urls import url
from minia import views
#from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
#from . import MyPasswordChangeView
from .views import MyPasswordChangeView ,MyPasswordSetView


urlpatterns = [
    path('admin/', admin.site.urls),
    #Dashboard
    path('',views.DashboardView.as_view(),name='dashboard'),
    #Apps
    path('apps/',include('apps.urls')),
    #Pages
    path('pages/',include('pages.urls')),
    #Elements
    path('elements/',include('elements.urls')),
    #Accounts    
    path("account/", include("allauth.urls")),

    path('logout',views.logout,name ='logout'),
    
    path('accounts/password/change/', login_required(MyPasswordChangeView.as_view()), name="account_change_password"),
    path('accounts/password/set/', login_required(MyPasswordSetView.as_view()), name="account_set_password"),

    path('lockscreen', views.PagesLockscreenView.as_view(), name="lockscreen"),

    path('social-auth/',include('social_django.urls', namespace='social')),

    
]
