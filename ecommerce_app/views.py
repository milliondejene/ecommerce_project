from django.shortcuts import render, get_object_or_404
from .models import Invoice

def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'ecommerce_project/invoice_print.html', {'invoice': invoice})
