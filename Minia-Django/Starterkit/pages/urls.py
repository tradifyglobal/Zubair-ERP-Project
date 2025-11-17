from django.urls import path

from .views import (
    pages_starterpage_view,
    pages_maintenance_view,
    pages_comingsoon_view,
    pages_timeline_view,
    pages_faqs_view,
    pages_pricing_view,
    pages_404_error_view,
    pages_500_error_view,
)

app_name = "pages"

urlpatterns=[
    path("starterpage", pages_starterpage_view, name="pages.starterpage"),
    path("maintenance", pages_maintenance_view, name="pages.maintenance"),
    path("comingsoon", pages_comingsoon_view, name="pages.comingsoon"),
    path("timeline", pages_timeline_view, name="pages.timeline"),
    path("faqs", pages_faqs_view, name="pages.faqs"),
    path("pricing", pages_pricing_view, name="pages.pricing"),
    path("404error", pages_404_error_view, name="pages.404error"),
    path("500error", pages_500_error_view, name="pages.500error"),
]