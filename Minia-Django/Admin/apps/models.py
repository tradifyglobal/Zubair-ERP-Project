
from django.db import models

class Vendor(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField(blank=True, null=True)
	phone = models.CharField(max_length=50, blank=True, null=True)
	address = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.name

class Invoice(models.Model):
	vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='invoices')
	invoice_number = models.CharField(max_length=100)
	date = models.DateField()
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Invoice {self.invoice_number} - {self.vendor.name}"
