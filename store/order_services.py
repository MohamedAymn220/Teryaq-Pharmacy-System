from django.db import transaction
from django.utils import timezone
from .models import Order

class OrderStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

VALID_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['shipped', 'cancelled'],
    'shipped': ['delivered'],
    'delivered': [],
    'cancelled': [],
}

def is_valid_transition(current_status, new_status):
    """Check if status transition is valid."""
    return new_status in VALID_TRANSITIONS.get(current_status, [])

def calculate_total_price(order):
    """Calculate total price from order items."""
    return sum(item.quantity * item.medicine.price for item in order.items.all())

@transaction.atomic
def accept_order(order_id):
    """
    Accept an order (Pending -> Confirmed).
    Returns (success: bool, message: str, order: Order or None)
    """
    try:
        order = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        return False, "Order not found", None

    if not is_valid_transition(order.status, 'confirmed'):
        return False, f"Cannot accept order with status: {order.status}", None

    order.status = 'confirmed'
    order.save()

    return True, "Order accepted successfully", order

@transaction.atomic
def reject_order(order_id):
    """
    Reject an order (Pending/Confirmed/Processing -> Cancelled).
    Returns (success: bool, message: str, order: Order or None)
    """
    try:
        order = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        return False, "Order not found", None

    if not is_valid_transition(order.status, 'cancelled'):
        return False, f"Cannot reject order with status: {order.status}", None

    order.status = 'cancelled'
    order.save()

    return True, "Order rejected successfully", order

@transaction.atomic
def process_order(order_id):
    """
    Mark order as processing (Pending/Confirmed -> Processing).
    Returns (success: bool, message: str, order: Order or None)
    """
    try:
        order = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        return False, "Order not found", None

    if not is_valid_transition(order.status, 'processing'):
        return False, f"Cannot process order with status: {order.status}", None

    order.status = 'processing'
    order.save()

    return True, "Order marked as processing", order

@transaction.atomic
def deliver_order(order_id):
    """
    Mark order as delivered (Shipped -> Delivered).
    Also calculates total_price if it's 0.
    Returns (success: bool, message: str, order: Order or None)
    """
    try:
        order = Order.objects.select_for_update().prefetch_related('items__medicine').get(id=order_id)
    except Order.DoesNotExist:
        return False, "Order not found", None

    if not is_valid_transition(order.status, 'delivered'):
        return False, f"Cannot deliver order with status: {order.status}", None

    order.status = 'delivered'
    order.completed = True

    if order.total_price == 0:
        order.total_price = calculate_total_price(order)

    order.save()

    return True, "Order marked as delivered", order

@transaction.atomic
def ship_order(order_id):
    """
    Mark order as shipped (Processing -> Shipped).
    Returns (success: bool, message: str, order: Order or None)
    """
    try:
        order = Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        return False, "Order not found", None

    if not is_valid_transition(order.status, 'shipped'):
        return False, f"Cannot ship order with status: {order.status}", None

    order.status = 'shipped'
    order.save()

    return True, "Order marked as shipped", order