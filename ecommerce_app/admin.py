from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.db.models import Sum, F
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from openpyxl import Workbook
from import_export.admin import ExportMixin
from import_export.resources import ModelResource
from .models import Product, PurchaseOrder, PurchaseOrderLineItem, Invoice, InvoiceLineItem

class PurchaseOrderLineItemInline(admin.TabularInline):
    model = PurchaseOrderLineItem
    extra = 1

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1

# Export Invoices to XLSX
class InvoiceResource(ModelResource):
    class Meta:
        model = Invoice

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'order_date', 'status', 'total_cost')
    inlines = [PurchaseOrderLineItemInline]

    def total_cost(self, obj):
        total = obj.line_items.aggregate(total=Sum('cost'))['total']
        return f"${total:.2f}" if total else "$0.00"
    
    total_cost.short_description = "Total Cost"

@admin.register(Invoice)
class InvoiceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = InvoiceResource
    list_display = ('id', 'customer_name', 'invoice_date', 'due_date', 'status', 'total_price', 'overdue_highlight', 'print_link')
    inlines = [InvoiceLineItemInline]
    actions = ['mark_as_paid', 'export_xlsx']

    def total_price(self, obj):
        total = obj.line_items.aggregate(total=Sum(F('quantity') * F('price_each')))['total']
        return f"${total:.2f}" if total else "$0.00"

    total_price.short_description = "Total Price"

    def mark_as_paid(self, request, queryset):
        updated_count = queryset.update(status='paid')
        self.message_user(request, f"{updated_count} invoice(s) marked as Paid.")
    
    mark_as_paid.short_description = "Mark selected invoices as Paid"

    def get_readonly_fields(self, request, obj=None):
        return ('total_price', 'overdue_highlight')  # Read-only fields

    def overdue_highlight(self, obj):
        if obj.status == 'unpaid' and obj.due_date < now().date():
            return format_html('<span style="color: red; font-weight: bold;">OVERDUE</span>')
        return "On Time"
    def overdue_highlight(self, obj):
        if obj.status == 'unpaid' and obj.due_date and obj.due_date < now().date():
            return format_html('<span style="color: red; font-weight: bold;">OVERDUE</span>')
        return "On Time"


    overdue_highlight.short_description = "Status"

    # Custom Invoice Printing
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:invoice_id>/print/', self.admin_site.admin_view(self.print_invoice), name='invoice-print'),
        ]
        return custom_urls + urls

    def print_invoice(self, request, invoice_id):
        invoice = Invoice.objects.get(pk=invoice_id)
        return render(request, 'admin/invoice_print.html', {'invoice': invoice})

    def print_link(self, obj):
        return format_html('<a href="{}" target="_blank">Print</a>', f"/admin/app/invoice/{obj.id}/print/")
    
    print_link.short_description = "Print Invoice"

    # Export Invoices to XLSX
    def export_xlsx(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.append(["Invoice ID", "Customer", "Invoice Date", "Due Date", "Status", "Total Price"])

        for invoice in queryset:
            ws.append([
                invoice.id,
                invoice.customer_name,
                invoice.invoice_date,
                invoice.due_date,
                invoice.status,
                invoice.total_price(),
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="invoices.xlsx"'
        wb.save(response)
        return response

    export_xlsx.short_description = "Export selected invoices to XLSX"

admin.site.register(Product)
