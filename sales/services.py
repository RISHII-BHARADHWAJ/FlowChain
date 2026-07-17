"""Sales service layer: invoice PDF generation"""
import os
import logging
from django.conf import settings

logger = logging.getLogger('scm')


class InvoiceService:
    """Invoice generation and PDF rendering"""

    @classmethod
    def generate_pdf(cls, invoice):
        """Generate a PDF invoice using WeasyPrint"""
        try:
            from django.template.loader import render_to_string
            from weasyprint import HTML
            html_string = render_to_string('sales/invoice_pdf.html', {
                'invoice': invoice,
                'COMPANY_NAME': settings.COMPANY_NAME,
                'CURRENCY_SYMBOL': settings.CURRENCY_SYMBOL,
            })
            output_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
            os.makedirs(output_dir, exist_ok=True)
            pdf_path = os.path.join(output_dir, f"invoice-{invoice.invoice_number}.pdf")
            HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(pdf_path)

            # Save path to invoice model
            rel_path = f"invoices/invoice-{invoice.invoice_number}.pdf"
            invoice.pdf_file = rel_path
            invoice.save(update_fields=['pdf_file'])
            logger.info(f"PDF generated: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"PDF generation failed for INV-{invoice.invoice_number}: {e}")
            raise


class SalesService:
    """Sales order business logic"""

    @classmethod
    def create_invoice_from_order(cls, sales_order, created_by):
        """Auto-create invoice from a sales order"""
        import datetime
        from sales.models import Invoice, SalesOrderItem
        from core.utils import generate_unique_id

        invoice = Invoice.objects.create(
            invoice_number=generate_unique_id('INV', 8),
            sales_order=sales_order,
            customer=sales_order.customer,
            invoice_date=datetime.date.today(),
            due_date=datetime.date.today() + datetime.timedelta(
                days=sales_order.customer.payment_terms_days
            ),
            subtotal=sales_order.subtotal,
            cgst_amount=sales_order.tax_amount / 2,
            sgst_amount=sales_order.tax_amount / 2,
            discount_amount=sales_order.discount_amount,
            total_amount=sales_order.total_amount,
            created_by=created_by,
        )
        return invoice
