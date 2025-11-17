from django.urls import path

from .views import (
    elements_components_alerts_view,
    elements_components_buttons_view,
    elements_components_cards_view,
    elements_components_carousel_view,
    elements_components_dropdowns_view,
    elements_components_grid_view,
    elements_components_images_view,
    elements_components_modals_view,
    elements_components_offcanvas_view,
    elements_components_progressbars_view,
    elements_components_tabs_view,
    elements_components_typography_view,
    elements_components_video_view,
    elements_components_general_view,
    elements_components_colors_view,
    elements_components_toasts_view,
    elements_components_utilites_view,

    elements_extended_lightbox_view,
    elements_extended_rangeslider_view,
    elements_extended_sweetalerts2_view,
    elements_extended_sessiontimeout_view,
    elements_extended_rating_view,
    elements_extended_notifications_view,

    elements_forms_basic_elements_view,
    elements_forms_validation_view,
    elements_forms_advanced_plugins_view,
    elements_forms_editors_view,
    elements_forms_fileupload_view,
    elements_forms_wizard_view,
    elements_forms_mask_view,

    elements_tables_bootstrap_basic_view,
    elements_tables_datatables_view,
    elements_tables_responsive_tables_view,
    elements_tables_editable_tables_view,

    elements_charts_apexcharts_view,
    elements_charts_echarts_view,
    elements_charts_chartjs_view,
    elements_charts_jqueryknob_view,
    elements_charts_sparkline_view,

    elements_icons_boxicons_view,
    elements_icons_materialdesign_view,
    elements_icons_dripicons_view,
    elements_icons_fontawesome_view,

    elements_maps_googlemaps_view,
    elements_maps_vectormaps_view,
    elements_maps_leaflet_view,
    
)

app_name = "elements"

urlpatterns=[

    #Components
    path("components/alerts", view=elements_components_alerts_view, name="elements.components.alerts"),
    path("components/buttons", view=elements_components_buttons_view, name="elements.components.buttons"),
    path("components/cards", view=elements_components_cards_view, name="elements.components.cards"),
    path("components/carousel", view=elements_components_carousel_view, name="elements.components.carousel"),
    path("components/dropdowns", view=elements_components_dropdowns_view, name="elements.components.dropdowns"),
    path("components/grid", view=elements_components_grid_view, name="elements.components.grid"),
    path("components/images", view=elements_components_images_view, name="elements.components.images"),
    path("components/modals", view=elements_components_modals_view, name="elements.components.modals"),
    path("components/offcanvas", view=elements_components_offcanvas_view, name="elements.components.offcanvas"),
    path("components/progressbars", view=elements_components_progressbars_view, name="elements.components.progressbars"),
    path("components/tabs", view=elements_components_tabs_view, name="elements.components.tabs"),
    path("components/typography", view=elements_components_typography_view, name="elements.components.typography"),
    path("components/video", view=elements_components_video_view, name="elements.components.video"),
    path("components/general", view=elements_components_general_view, name="elements.components.general"),
    path("components/colors", view=elements_components_colors_view, name="elements.components.colors"),
    path("components/toasts", view=elements_components_toasts_view, name="elements.components.toasts"),
    path("components/utilites", view=elements_components_utilites_view, name="elements.components.utilities"),

    #Extended
    path("extended/lightbox", view=elements_extended_lightbox_view, name="elements.extended.lightbox"),
    path("extended/rangeslider", view=elements_extended_rangeslider_view, name="elements.extended.rangeslider"),
    path("extended/sweetalerts2", view=elements_extended_sweetalerts2_view, name="elements.extended.sweetalerts2"),
    path("extended/session-timeout", view=elements_extended_sessiontimeout_view, name="elements.extended.sessiontimeout"),
    path("extended/rating", view=elements_extended_rating_view, name="elements.extended.rating"),
    path("extended/notifications", view=elements_extended_notifications_view, name="elements.extended.notifications"),

    #Forms
    path("forms/basic_elements", view=elements_forms_basic_elements_view, name="elements.forms.basic_elements"),
    path("forms/validation", view=elements_forms_validation_view, name="elements.forms.validation"),
    path("forms/advancedplugins", view=elements_forms_advanced_plugins_view, name="elements.forms.advancedplugins"),
    path("forms/editors", view=elements_forms_editors_view, name="elements.forms.editors"),
    path("forms/fileupload", view=elements_forms_fileupload_view, name="elements.forms.fileupload"),
    path("forms/wizard", view=elements_forms_wizard_view, name="elements.forms.wizard"),
    path("forms/mask", view=elements_forms_mask_view, name="elements.forms.mask"),

    #Tables
    path("tables/bootstrapbasic", view=elements_tables_bootstrap_basic_view, name="elements.tables.bootstrap_basic"),
    path("tables/datatables", view=elements_tables_datatables_view, name="elements.tables.datatables"),
    path("tables/responsive_tables", view=elements_tables_responsive_tables_view, name="elements.tables.responsive_tables"),
    path("tables/editable_tables", view=elements_tables_editable_tables_view, name="elements.tables.editable_tables"),

    #Charts
    path("charts/apexcharts", view=elements_charts_apexcharts_view, name="elements.charts.apexcharts"),
    path("charts/echarts", view=elements_charts_echarts_view, name="elements.charts.echarts"),
    path("charts/chartjs", view=elements_charts_chartjs_view, name="elements.charts.chartjs"),
    path("charts/jqueryknob", view=elements_charts_jqueryknob_view, name="elements.charts.jqueryknob"),
    path("charts/sparkline", view=elements_charts_sparkline_view, name="elements.charts.sparkline"),

    #Icons
    path("icons/boxicons", view=elements_icons_boxicons_view, name="elements.icons.boxicons"),
    path("icons/materialdesign", view=elements_icons_materialdesign_view, name="elements.icons.materialdesign"),
    path("icons/dripicons", view=elements_icons_dripicons_view, name="elements.icons.dripicons"),
    path("icons/fontawesome", view=elements_icons_fontawesome_view, name="elements.icons.fontawesome"),

    #Maps
    path("maps/googlemaps", view = elements_maps_googlemaps_view, name="elements.maps.googlemaps"),
    path("maps/vectormaps", view = elements_maps_vectormaps_view, name="elements.maps.vectormaps"),
    path("maps/leaflet", view = elements_maps_leaflet_view, name="elements.maps.leaflet"),
]