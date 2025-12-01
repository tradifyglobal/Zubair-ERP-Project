
from .forms import InvoiceForm
from .models import Invoice

class AppsView(LoginRequiredMixin,TemplateView):
    pass

# Invoice List View with Vendor Dropdown
from django.views import View
class InvoiceListView(LoginRequiredMixin, View):
    def get(self, request):
        form = InvoiceForm()
        invoices = Invoice.objects.select_related('vendor').all()
        return render(request, "apps/invoices/invoice_list.html", {"form": form, "invoices": invoices})
    def post(self, request):
        form = InvoiceForm(request.POST)
        invoices = Invoice.objects.select_related('vendor').all()
        if form.is_valid():
            form.save()
            form = InvoiceForm()  # reset form after save
        return render(request, "apps/invoices/invoice_list.html", {"form": form, "invoices": invoices})

apps_invoice_list_view = InvoiceListView.as_view()
apps_invoice_details_view = AppsView.as_view(template_name="apps/invoices/invoice_details.html")

# ...existing code for other views...