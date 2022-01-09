from  rest_framework import fields, serializers
from django.conf import settings
from .models import InvoiceDetails
from .utils import shoten_url


class InvoiceSerializers(serializers.ModelSerializer):
    payment_link = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceDetails
        fields = 'invoice_number', 'client_name', 'client_email', 'project_name', 'amount', 'is_paid', 'payment_link'

    def get_payment_link(self, obj):
        shorten_url = shoten_url(settings.SITE_DOMAIN + '/payment-details/' + obj.invoice_number)
        return shorten_url