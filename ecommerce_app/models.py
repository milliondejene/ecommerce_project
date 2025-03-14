from django.db import models

class Product(models.Model):
    """Model representing a product."""
    name = models.CharField(max_length=255, unique=True, help_text="Name of the product")
    sku = models.CharField(max_length=50, unique=True, help_text="Stock Keeping Unit (SKU)")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")

    def __str__(self):
        return f"{self.name} ({self.sku})"


class PurchaseOrder(models.Model):
    """Model representing a purchase order from a vendor."""
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    vendor = models.CharField(max_length=255, help_text="Vendor name")
    order_date = models.DateField(auto_now_add=True, help_text="Date when the order was placed")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"PO-{self.id} ({self.vendor}) - {self.get_status_display()}"


class PurchaseOrderLineItem(models.Model):
    """Model representing an item in a purchase order."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="line_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="Number of units ordered")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total cost for this item")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.purchase_order}"


class Invoice(models.Model):
    """Model representing a customer invoice."""
    STATUS_UNPAID = 'unpaid'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = [
        (STATUS_UNPAID, 'Unpaid'),
        (STATUS_PAID, 'Paid'),
    ]

    customer_name = models.CharField(max_length=255, help_text="Customer's full name")
    invoice_date = models.DateField(auto_now_add=True, help_text="Date of invoice creation")
    due_date = models.DateField(help_text="Due date for payment")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNPAID)

    def __str__(self):
        return f"Invoice-{self.id} for {self.customer_name} ({self.get_status_display()})"
