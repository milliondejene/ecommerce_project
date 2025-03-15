from django.urls import path
from .views import print_invoice

urlpatterns = [
    path('invoice/<int:invoice_id>/print/', print_invoice, name='print_invoice'),
]
