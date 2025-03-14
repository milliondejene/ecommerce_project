from django.test import TestCase
from .models import Product, PurchaseOrder, PurchaseOrderLineItem, Invoice, InvoiceLineItem
from django.utils.timezone import now, timedelta

class ECommerceTestCase(TestCase):
    def setUp(self):
        """Set up test data before each test."""
        self.product = Product.objects.create(name="Laptop", sku="LAP123", unit_price=1000.00)
        self.purchase_order = PurchaseOrder.objects.create(vendor="TechSupplier")
        self.purchase_line_item = PurchaseOrderLineItem.objects.create(
            purchase_order=self.purchase_order,
            product=self.product,
            quantity=5,
            cost=5000.00
        )
        self.invoice = Invoice.objects.create(
            customer_name="John Doe",
            invoice_date=now().date(),
            due_date=now().date() - timedelta(days=1),  # Overdue
            status="unpaid"
        )
        self.invoice_line_item = InvoiceLineItem.objects.create(
            invoice=self.invoice,
            product=self.product,
            quantity=2,
            price_each=1200.00
        )

    def test_product_creation(self):
        """Test if the product is created correctly."""
        self.assertEqual(str(self.product), "Laptop (LAP123)")

    def test_purchase_order_total_cost(self):
        """Test if the purchase order total cost is calculated correctly."""
        self.assertEqual(self.purchase_order.total_cost(), 5000.00)

    def test_invoice_total_price(self):
        """Test if the invoice total price is calculated correctly."""
        self.assertEqual(self.invoice.total_price(), 2400.00)

    def test_invoice_overdue_query(self):
        """Test the overdue invoice query."""
        overdue_invoices = Invoice.objects.overdue_and_above(1000)
        self.assertTrue(self.invoice in overdue_invoices)
