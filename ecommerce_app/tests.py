from django.test import TestCase
from django.db import models
from django.utils.timezone import now, timedelta
from .models import Product, PurchaseOrder, PurchaseOrderLineItem, Invoice, InvoiceLineItem

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

    def test_purchase_order_line_item_creation(self):
        """Test the creation of a purchase order line item."""
        self.assertEqual(self.purchase_line_item.product.name, "Laptop")
        self.assertEqual(self.purchase_line_item.quantity, 5)
        self.assertEqual(self.purchase_line_item.cost, 5000.00)

    def test_invoice_line_item_creation(self):
        """Test the creation of an invoice line item."""
        self.assertEqual(self.invoice_line_item.product.name, "Laptop")
        self.assertEqual(self.invoice_line_item.quantity, 2)
        self.assertEqual(self.invoice_line_item.price_each, 1200.00)

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

    def test_mark_invoice_as_paid(self):
        """Test the custom action to mark an invoice as paid."""
        self.invoice.mark_as_paid()  # Calls the custom method
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'paid')

    def test_filter_overdue_invoices_above_threshold(self):
        """Test filtering overdue invoices above a certain total."""
        overdue_invoices = Invoice.objects.filter(
            due_date__lt=now().date(),
            status="unpaid"
        ).annotate(
            total_price=models.Sum(models.F('line_items__quantity') * models.F('line_items__price_each'))
        )
        
        overdue_invoices_above_threshold = overdue_invoices.filter(total_price__gt=1000)
        
        # Test if the correct invoices are included
        self.assertTrue(self.invoice in overdue_invoices_above_threshold)
        
    def test_invoice_status_update_on_paid(self):
        """Test if invoice status updates correctly when marked as paid."""
        self.invoice.status = 'unpaid'
        self.invoice.save()

        # Initially should be unpaid
        self.assertEqual(self.invoice.status, 'unpaid')

        self.invoice.status = 'paid'
        self.invoice.save()

        # Should change to paid
        self.assertEqual(self.invoice.status, 'paid')

    def test_purchase_order_total_cost_multiple_items(self):
        """Test if the total cost of a purchase order with multiple items is calculated correctly."""
        product2 = Product.objects.create(name="Phone", sku="PH123", unit_price=500.00)
        purchase_line_item2 = PurchaseOrderLineItem.objects.create(
            purchase_order=self.purchase_order,
            product=product2,
            quantity=4,
            cost=2000.00
        )
        self.assertEqual(self.purchase_order.total_cost(), 7000.00)  # 5000 + 2000

    def test_invoice_line_item_price_each(self):
        """Test the correct calculation of the price each for an invoice line item."""
        self.assertEqual(self.invoice_line_item.price_each, 1200.00)

    def test_total_price_for_invoice_line_items(self):
        """Test if the total price for all invoice line items is correct."""
        self.assertEqual(self.invoice.total_price(), 2400.00)

    def test_purchase_order_status_update(self):
        """Test that the status of the purchase order updates correctly."""
        self.purchase_order.status = 'completed'  # Directly setting status
        self.purchase_order.save()
        self.assertEqual(self.purchase_order.status, 'completed')