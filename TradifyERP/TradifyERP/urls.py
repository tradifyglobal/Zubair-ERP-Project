"""
URL configuration for TradifyERP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Customize admin site title
admin.site.site_header = "Tradify Global Administration"
admin.site.site_title = "Tradify Global Admin"
admin.site.index_title = "Welcome to Tradify Global Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root dashboard redirect to accounting dashboard
    path('', RedirectView.as_view(url='/accounting/dashboard/', permanent=False), name='home'),
    path('dashboard/', RedirectView.as_view(url='/accounting/dashboard/', permanent=False), name='dashboard'),
    # Accounting module - includes /dashboard/ route
    path('accounting/', include('accounting.urls')),
    # Shareholder management module
    path('shareholder/', include('shareholder.urls')),
    # HR Management module
    path('hr/', include('hr.urls')),
    # Manufacturing module
    path('manufacturing/', include('manufacturing.urls')),
    # Sales module
    path('sales/', include('sales.urls')),
    # Inventory module
    path('inventory/', include('inventory.urls')),
    # Accounts Payable module
    path('ap/', include('ap.urls')),
    # Procurement module
    path('procurement/', include('procurement.urls')),
    # Cash Management module
    path('cash/', include('cash_management.urls')),
    # Project Management module
    path('projects/', include('projects.urls')),
    # CRM module
    path('crm/', include('crm.urls')),
    # Accounts Receivable module
    path('ar/', include('ar.urls')),
    # Site Maintenance module
    path('maintenance/', include('maintenance.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
