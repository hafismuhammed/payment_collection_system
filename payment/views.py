import stripe
import uuid
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import InvoiceDetails
from .utils import shoten_url
from .serializers import InvoiceSerializers

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentDetailsAPI(APIView):

    def get(self, request, *args, **kwargs):
        invoice_number = self.kwargs["invoice_number"]
        invoice_details = InvoiceDetails.objects.get(invoice_number=invoice_number)
        if invoice_details.is_paid:
            return Response({
                "message": "Invoice already paid",
                "status": "fail",
            }, status=400)
        else:
            context = {
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                'invoice_details': invoice_details,
            }
            return render(request, 'checkout.html', context)

class InvoiceAPI(APIView):
    def get(self, request):
        invoices_details = InvoiceDetails.objects.all()
        data = InvoiceSerializers(invoices_details, many=True).data
        return Response(data, status=200)


    def post(self, request):
        data = {}
        client_name = request.data['client_name']
        client_email = request.data['client_email']
        project_name = request.data['project_name']
        amount = request.data['amount']

        invoice_number = uuid.uuid4().hex[:12].upper()
        uniqe_confirm = InvoiceDetails.objects.filter(invoice_number=invoice_number).exists()
        while uniqe_confirm:
            invoice_number = uuid.uuid4().hex[:12].upper()
            if not uniqe_confirm:
                break

        invoice_details = InvoiceDetails(
            invoice_number=invoice_number, 
            client_name=client_name, 
            client_email=client_email, 
            project_name=project_name, 
            amount=amount)
        invoice_details.save()
        
        shorten_url = shoten_url(settings.SITE_DOMAIN + '/payment-details/' + invoice_details.invoice_number)

        data['invoice_number'] = invoice_details.invoice_number
        data['client_name'] = invoice_details.client_name
        data['client_email'] = invoice_details.client_email
        data['project_name'] = invoice_details.project_name
        data['amount'] = invoice_details.amount
        data['payment_link'] = shorten_url

        return Response(data, status=200)



class PaymentSuccessAPI(APIView):
    def get(self, request, *args, **kwargs):
        invoice_number = self.kwargs["invoice_number"]
        invoice_details = InvoiceDetails.objects.get(invoice_number=invoice_number)
        invoice_details.is_paid = True
        invoice_details.save()
        data = {
            "invoice_id": invoice_details.id,
            "invoice_number": invoice_details.invoice_number,
            "client_name": invoice_details.client_name,
            "client_email": invoice_details.client_email,
            "project_name": invoice_details.project_name,
            "amount": invoice_details.amount,
            "message": "payment success",
            "status": "success"
        }
        return Response(data, status=200)

class PaymentCancelAPI(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
                "message": "Payment cancelled",
                "status": "fail",
            }, status=400)


class CheckoutAPI(APIView):
    def post(self, request, *args, **kwargs):
        invoice_number = self.kwargs["invoice_number"]
        invoice_details = InvoiceDetails.objects.get(invoice_number=invoice_number)
        if not invoice_details.is_paid:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                        'currency': 'inr',
                        'unit_amount': int(invoice_details.amount * 100),
                        'product_data': {
                            'name': invoice_details.client_name,
                        },
                    },
                    'quantity': 1,  
                    },
                ],
                mode='payment',
                success_url= settings.SITE_DOMAIN + '/payment-success/'+ invoice_details.invoice_number,
                cancel_url= settings.SITE_DOMAIN + '/payment-cancel',
            )
            return redirect(checkout_session.url, code=303)
        else:
            return Response({
                "message": "Invoice already paid",
                "status": "fail",
            }, status=400)


