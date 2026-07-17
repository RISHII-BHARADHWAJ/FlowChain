"""
Service layer for inventory operations - business logic separated from views
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from inventory.models import StockLevel, StockMovement, Batch

logger = logging.getLogger('scm')


class InventoryService:
    """Centralized inventory business logic"""

    @classmethod
    @transaction.atomic
    def receive_stock(cls, product, warehouse, quantity, unit_cost,
                      movement_type='receipt', reference_number='',
                      batch_number=None, expiry_date=None, performed_by=None):
        """Add stock to warehouse with movement tracking"""
        stock_level, created = StockLevel.objects.select_for_update().get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'average_cost': unit_cost},
        )

        quantity_before = stock_level.quantity_on_hand

        # Update weighted average cost
        if stock_level.quantity_on_hand > 0:
            total_value = (stock_level.quantity_on_hand * stock_level.average_cost) + (quantity * unit_cost)
            stock_level.average_cost = total_value / (stock_level.quantity_on_hand + quantity)
        else:
            stock_level.average_cost = unit_cost

        stock_level.quantity_on_hand += Decimal(str(quantity))
        stock_level.total_value = stock_level.quantity_on_hand * stock_level.average_cost
        stock_level.last_movement_at = timezone.now()
        stock_level.save()

        # Record movement
        movement = StockMovement.objects.create(
            product=product,
            warehouse=warehouse,
            movement_type=movement_type,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=stock_level.quantity_on_hand,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost,
            reference_number=reference_number,
            performed_by=performed_by,
        )

        # Create batch if batch tracking is enabled
        if product.is_batch_tracked and batch_number:
            Batch.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                batch_number=batch_number,
                defaults={
                    'quantity': quantity,
                    'unit_cost': unit_cost,
                    'expiry_date': expiry_date,
                }
            )

        logger.info(f"Stock received: {product.sku} | Qty: {quantity} | WH: {warehouse.code}")
        return movement

    @classmethod
    @transaction.atomic
    def deduct_stock(cls, product, warehouse, quantity, movement_type='sale',
                     reference_number='', performed_by=None):
        """Remove stock from warehouse"""
        stock_level = StockLevel.objects.select_for_update().get(
            product=product, warehouse=warehouse
        )

        if stock_level.quantity_available < quantity:
            raise ValueError(
                f"Insufficient stock. Available: {stock_level.quantity_available}, "
                f"Requested: {quantity}"
            )

        quantity_before = stock_level.quantity_on_hand
        stock_level.quantity_on_hand -= Decimal(str(quantity))
        stock_level.total_value = stock_level.quantity_on_hand * stock_level.average_cost
        stock_level.last_movement_at = timezone.now()
        stock_level.save()

        movement = StockMovement.objects.create(
            product=product,
            warehouse=warehouse,
            movement_type=movement_type,
            quantity=-quantity,
            quantity_before=quantity_before,
            quantity_after=stock_level.quantity_on_hand,
            unit_cost=stock_level.average_cost,
            total_cost=quantity * stock_level.average_cost,
            reference_number=reference_number,
            performed_by=performed_by,
        )

        logger.info(f"Stock deducted: {product.sku} | Qty: {quantity} | WH: {warehouse.code}")
        return movement

    @classmethod
    def get_stock_valuation(cls, warehouse=None):
        """Calculate total inventory value"""
        qs = StockLevel.objects.all()
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        from django.db.models import Sum
        result = qs.aggregate(
            total_value=Sum('total_value'),
            total_quantity=Sum('quantity_on_hand'),
        )
        return result

    @classmethod
    def get_low_stock_products(cls, warehouse=None):
        """Get all products at or below reorder point"""
        from django.db.models import F
        qs = StockLevel.objects.select_related('product', 'warehouse').filter(
            quantity_on_hand__lte=F('product__reorder_point'),
            quantity_on_hand__gt=0,
        )
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        return qs

    @classmethod
    def get_out_of_stock_products(cls, warehouse=None):
        """Get all out-of-stock products"""
        qs = StockLevel.objects.select_related('product', 'warehouse').filter(
            quantity_on_hand__lte=0
        )
        if warehouse:
            qs = qs.filter(warehouse=warehouse)
        return qs
