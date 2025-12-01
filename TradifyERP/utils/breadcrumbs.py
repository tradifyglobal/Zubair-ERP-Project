from django.urls import reverse

class BreadcrumbMixin:
    """
    Mixin to add breadcrumb support to Django class-based views.
    Override get_breadcrumbs() in your view to customize breadcrumbs.
    """
    
    def get_breadcrumbs(self):
        """
        Return a list of breadcrumb dictionaries.
        Each dictionary should have 'title' and optionally 'url' keys.
        """
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
