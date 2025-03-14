import datetime
from django.db import models
from django.db.models import F, Sum

class Product(models.Model):
    """Represents a product available for purchase."""
    name = models.CharField(max_length=255, unique=True, help_text="The name of the product.")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit (SKU) for the product.")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit of the product.")

    def __str__(self):
        return f"{self.name} ({self.sku})"


class PurchaseOrder(models.Model):
    """Represents a purchase order made to a vendor."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    
    vendor = models.CharField(max_length=255, help_text="Name of the vendor.")
    order_date = models.DateField(auto_now_add=True, help_text="The date when the order was placed.")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending', 
        help_text="The current status of the purchase order."
    )

    def __str__(self):
        return f"PO-{self.id} ({self.vendor}) - {self.get_status_display()}"
    
    def total_cost(self):
        """Calculate total cost of all line items in this purchase order."""
        return self.line_items.aggregate(total=Sum('cost'))['total'] or 0.00


class PurchaseOrderLineItem(models.Model):
    """Represents a line item in a purchase order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="line_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="The number of units ordered.")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="The total cost for this line item.")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in PO-{self.purchase_order.id}"


class InvoiceManager(models.Manager):
    """Custom manager to handle queries for invoices."""
    
    def overdue_and_above(self, threshold):
        """Returns invoices that are overdue and total price is above the given threshold."""
        return self.filter(
            due_date__lt=datetime.date.today(),  # Overdue invoices
            line_items__quantity__gt=0,  # Ensure line items exist
        ).annotate(
            total_price=Sum(F('line_items__quantity') * F('line_items__price_each'))
        ).filter(total_price__gt=threshold)  # Invoices with total price above the threshold


class Invoice(models.Model):
    """Represents an invoice sent to a customer."""
    
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    customer_name = models.CharField(max_length=255, help_text="Full name of the customer.")
    invoice_date = models.DateField(auto_now_add=True, help_text="The date when the invoice was created.")
    due_date = models.DateField(help_text="The due date by which payment should be made.")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='unpaid', 
        help_text="The current status of the invoice."
    )
    
    # Link custom manager
    objects = InvoiceManager()

    def __str__(self):
        return f"Invoice-{self.id} for {self.customer_name} ({self.get_status_display()})"
    
    def total_price(self):
        """Calculate total price of all line items in this invoice."""
        return self.line_items.aggregate(
            total=Sum(F('quantity') * F('price_each'))
        )['total'] or 0.00
    def mark_as_paid(self):
        """Custom method to mark the invoice as paid."""
        self.status = 'paid'
        self.save()  # Save the updated status to the database


class InvoiceLineItem(models.Model):
    """Represents a line item in an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="The number of units purchased.")
    price_each = models.DecimalField(max_digits=10, decimal_places=2, help_text="The price per unit for the product.")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Invoice-{self.invoice.id}"
