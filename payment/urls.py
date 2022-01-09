from django.urls import path
from . import views

urlpatterns = [
    path('all-invoices', views.InvoiceAPI.as_view(), name='all-invoices'),
    path('payment-details/<str:invoice_number>', views.PaymentDetailsAPI.as_view(), name='payment_details'),
    path('add_invoice', views.InvoiceAPI.as_view(), name='add_invoice'),
    path('checkout/<str:invoice_number>', views.CheckoutAPI.as_view(), name='checkout'),
    path('payment-success/<str:invoice_number>', views.PaymentSuccessAPI.as_view(), name='payment-success'),
    path('payment-cancel', views.PaymentCancelAPI.as_view(), name='payment_cancel'),
]