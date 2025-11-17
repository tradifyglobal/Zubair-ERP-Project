from django.http import request
from django.shortcuts import redirect, render
from django.views import View   
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.generic import TemplateView

User = get_user_model()

class ElementsView(LoginRequiredMixin,TemplateView):
    pass

#Components 
elements_components_alerts_view = ElementsView.as_view(template_name="elements/components/alerts.html")
elements_components_buttons_view = ElementsView.as_view(template_name="elements/components/buttons.html")
elements_components_cards_view = ElementsView.as_view(template_name="elements/components/cards.html")
elements_components_carousel_view = ElementsView.as_view(template_name="elements/components/carousel.html")
elements_components_dropdowns_view = ElementsView.as_view(template_name="elements/components/dropdowns.html")
elements_components_grid_view = ElementsView.as_view(template_name="elements/components/grid.html")
elements_components_images_view = ElementsView.as_view(template_name="elements/components/images.html")
elements_components_modals_view = ElementsView.as_view(template_name="elements/components/modals.html")
elements_components_offcanvas_view = ElementsView.as_view(template_name="elements/components/offcanvas.html")
elements_components_progressbars_view = ElementsView.as_view(template_name="elements/components/progressbars.html")
elements_components_tabs_view = ElementsView.as_view(template_name="elements/components/tabs.html")
elements_components_typography_view = ElementsView.as_view(template_name="elements/components/typography.html")
elements_components_video_view = ElementsView.as_view(template_name="elements/components/video.html")
elements_components_general_view = ElementsView.as_view(template_name="elements/components/general.html")
elements_components_colors_view = ElementsView.as_view(template_name="elements/components/colors.html")
elements_components_toasts_view = ElementsView.as_view(template_name="elements/components/toasts.html")
elements_components_utilites_view = ElementsView.as_view(template_name="elements/components/utilites.html")

#Extended
elements_extended_lightbox_view = ElementsView.as_view(template_name="elements/extended/lightbox.html")
elements_extended_rangeslider_view = ElementsView.as_view(template_name="elements/extended/rangeslider.html")
elements_extended_sweetalerts2_view= ElementsView.as_view(template_name="elements/extended/sweetalerts2.html")
elements_extended_sessiontimeout_view= ElementsView.as_view(template_name="elements/extended/sessiontimeout.html")
elements_extended_rating_view= ElementsView.as_view(template_name="elements/extended/rating.html")
elements_extended_notifications_view= ElementsView.as_view(template_name="elements/extended/notifications.html")

#Forms
elements_forms_basic_elements_view= ElementsView.as_view(template_name="elements/forms/form_basic_elements.html")
elements_forms_validation_view= ElementsView.as_view(template_name="elements/forms/form_validation.html")
elements_forms_advanced_plugins_view = ElementsView.as_view(template_name="elements/forms/form_advanced_plugins.html")
elements_forms_editors_view = ElementsView.as_view(template_name="elements/forms/form_editors.html")
elements_forms_fileupload_view = ElementsView.as_view(template_name="elements/forms/form_fileupload.html")
elements_forms_wizard_view = ElementsView.as_view(template_name="elements/forms/form_wizard.html")
elements_forms_mask_view = ElementsView.as_view(template_name="elements/forms/form_mask.html")

#Tables
elements_tables_bootstrap_basic_view = ElementsView.as_view(template_name="elements/tables/bootstrap_basic.html")
elements_tables_datatables_view = ElementsView.as_view(template_name="elements/tables/datatables.html")
elements_tables_responsive_tables_view = ElementsView.as_view(template_name="elements/tables/responsive_tables.html")
elements_tables_editable_tables_view = ElementsView.as_view(template_name="elements/tables/editable_tables.html")

#Charts
elements_charts_apexcharts_view = ElementsView.as_view(template_name="elements/charts/apexcharts.html")
elements_charts_echarts_view = ElementsView.as_view(template_name="elements/charts/echarts.html")
elements_charts_chartjs_view = ElementsView.as_view(template_name="elements/charts/chartjs.html")
elements_charts_jqueryknob_view = ElementsView.as_view(template_name="elements/charts/jqueryknob.html")
elements_charts_sparkline_view =ElementsView.as_view(template_name="elements/charts/sparkline.html")

#Icons
elements_icons_boxicons_view =ElementsView.as_view(template_name="elements/icons/boxicons.html")
elements_icons_materialdesign_view = ElementsView.as_view(template_name="elements/icons/materialdesign.html")
elements_icons_dripicons_view = ElementsView.as_view(template_name="elements/icons/dripicons.html")
elements_icons_fontawesome_view = ElementsView.as_view(template_name="elements/icons/fontawesome.html")

#Maps
elements_maps_googlemaps_view = ElementsView.as_view(template_name="elements/maps/googlemaps.html")
elements_maps_vectormaps_view = ElementsView.as_view(template_name="elements/maps/vectormaps.html")
elements_maps_leaflet_view = ElementsView.as_view(template_name="elements/maps/leaflet.html")
