def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            from .models import Cart
            if hasattr(request.user, 'cart'):
                count = request.user.cart.get_total_items()
        except Exception:
            count = 0
    return {'cart_count': count}