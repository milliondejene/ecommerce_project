from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.db.models import Sum, F
from .models import Product, PurchaseOrder, PurchaseOrderLineItem, Invoice, InvoiceLineItem

class PurchaseOrderLineItemInline(admin.TabularInline):
    model = PurchaseOrderLineItem
    extra = 1

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'order_date', 'status', 'total_cost')
    inlines = [PurchaseOrderLineItemInline]

    def total_cost(self, obj):
        total = obj.line_items.aggregate(total=Sum('cost'))['total']
        return f"${total:.2f}" if total else "$0.00"
    
    total_cost.short_description = "Total Cost"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'invoice_date', 'due_date', 'status', 'total_price', 'overdue_highlight')
    inlines = [InvoiceLineItemInline]
    actions = ['mark_as_paid']

    def total_price(self, obj):
        total = obj.line_items.aggregate(total=Sum(F('quantity') * F('price_each')))['total']
        return f"${total:.2f}" if total else "$0.00"

    total_price.short_description = "Total Price"

    def mark_as_paid(self, request, queryset):
        updated_count = queryset.update(status='paid')
        self.message_user(request, f"{updated_count} invoice(s) marked as Paid.")
    
    mark_as_paid.short_description = "Mark selected invoices as Paid"

    def overdue_highlight(self, obj):
        if obj.status == 'unpaid' and obj.due_date < now().date():
            return format_html('<span style="color: red; font-weight: bold;">OVERDUE</span>')
        return "On Time"

    overdue_highlight.short_description = "Status"

admin.site.register(Product)