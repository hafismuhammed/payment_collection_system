from django.db import models

class InvoiceDetails(models.Model):
    invoice_number = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    project_name = models.CharField(max_length=100)
    amount = models.FloatField()
    is_paid = models.BooleanField(default=False)
