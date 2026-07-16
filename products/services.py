"""Product service layer: barcode/QR generation"""
import os
import io
import uuid
from django.conf import settings
import logging

logger = logging.getLogger('scm')


class BarcodeService:
    """Generates barcodes and QR codes for products"""

    @classmethod
    def generate_barcode(cls, product):
        """Generate EAN-13 / Code128 barcode and save to media"""
        try:
            import barcode
            from barcode.writer import ImageWriter

            barcode_value = product.barcode or product.sku
            code = barcode.get('code128', barcode_value, writer=ImageWriter())
            filename = f"barcodes/{product.sku}_barcode"
            filepath = os.path.join(settings.MEDIA_ROOT, f"{filename}.png")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            code.save(filepath.replace('.png', ''))

            url = f"{settings.MEDIA_URL}{filename}.png"
            if not product.barcode:
                product.barcode = barcode_value
                product.save(update_fields=['barcode'])
            return url
        except Exception as e:
            logger.error(f"Barcode generation failed for {product.sku}: {e}")
            return None

    @classmethod
    def generate_qr_code(cls, product):
        """Generate QR code containing product info"""
        try:
            import qrcode
            from qrcode.image.pure import PyPNGImage

            data = {
                'sku': product.sku,
                'name': product.name,
                'barcode': product.barcode or '',
            }
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(str(data))
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"qrcodes/{product.sku}_qr.png"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            img.save(filepath)

            url = f"{settings.MEDIA_URL}{filename}"
            product.qr_code = url
            product.save(update_fields=['qr_code'])
            return url
        except Exception as e:
            logger.error(f"QR generation failed for {product.sku}: {e}")
            return None
