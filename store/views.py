from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count
from django.db import transaction
import json

from .models import Medicine, Category, Order, OrderItem, Cart, CartItem
from .forms import CategoryForm, MedicineForm, CustomUserCreationForm


def get_or_create_cart(user):
    """Helper function to get or create a cart for a user."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# =============================
# AUTH (LOGIN + REGISTER)
# =============================
def auth_view(request):
    """Handle user authentication (login and signup)."""
    # Redirect authenticated users away from auth page
    if request.user.is_authenticated:
        return redirect('store:home')

    form = CustomUserCreationForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        # ---------- LOGIN ----------
        if action == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            # Validate inputs
            if not username or not password:
                messages.error(request, 'Please enter both username and password.')
            else:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Welcome back, ' + username + '!')
                    return redirect('store:home')
                else:
                    messages.error(request, 'Invalid username or password. Please try again.')

        # ---------- SIGNUP ----------
        elif action == 'signup':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                try:
                    # Get cleaned data
                    username = form.cleaned_data.get('username')
                    email = form.cleaned_data.get('email')
                    password = form.cleaned_data.get('password1')
                    pharmacy_name = form.cleaned_data.get('pharmacy_name', '')
                    phone = form.cleaned_data.get('phone', '')
                    
                    # Additional validation
                    if User.objects.filter(username=username).exists():
                        messages.error(request, 'This username is already taken. Please choose another.')
                        return render(request, 'store/auth_complete.html', {'form': form})
                    
                    if User.objects.filter(email=email).exists():
                        messages.error(request, 'This email is already registered. Please use another.')
                        return render(request, 'store/auth_complete.html', {'form': form})
                    
                    # Create user with extra fields
                    user = form.save(commit=False)
                    user.first_name = pharmacy_name[:30]  # max 30 chars for first_name
                    user.email = email
                    user.save()
                    
                    # Log the user in after signup
                    login(request, user)
                    messages.success(request, f'Welcome to Teryaq Pharmacy, {username}! Your account has been created.')
                    return redirect('store:home')
                except Exception as e:
                    messages.error(request, 'An error occurred during registration. Please try again.')
            else:
                # Collect all form errors for display
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(error)
                if error_messages:
                    messages.error(request, 'Please correct the errors below: ' + '; '.join(error_messages[:3]))
                else:
                    messages.error(request, 'Please correct the errors below.')

    return render(request, 'store/auth_complete.html', {'form': form})


# =============================
# PROTECTED PAGES
# =============================
@login_required(login_url='store:auth')
def home(request):
    categories = Category.objects.all()
    medicines = Medicine.objects.all().select_related('category')
    
    # Add pagination to avoid loading all medicines at once
    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'medicines': page_obj,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    return render(request, 'store/home.html', context)


@login_required(login_url='store:auth')
def medicine_list(request):
    """Paginated list of all medicines with category filtering."""
    categories = Category.objects.all()
    medicines = Medicine.objects.all().select_related('category')
    
    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        medicines = medicines.filter(category_id=category_id)
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/medicine_list.html', {
        'medicines': page_obj,
        'categories': categories,
        'current_category': category_id,
        'query': query,
    })


@login_required(login_url='store:auth')
def medicine_detail(request, id):
    medicine = get_object_or_404(Medicine.objects.select_related('category'), id=id)
    return render(request, 'store/medicine_detail.html', {'medicine': medicine})


@login_required(login_url='store:auth')
def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    medicines = Medicine.objects.filter(category=category).select_related('category')
    return render(request, 'store/category_detail.html', {
        'category': category,
        'medicines': medicines
    })


# =============================
# DATABASE-BACKED CART
# =============================
@login_required(login_url='store:auth')
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if medicine.stock <= 0:
        messages.error(request, f"{medicine.name} is out of stock.")
        return redirect('store:medicine_detail', id=medicine_id)  # Fixed: was pk=medicine_id

    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < medicine.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{medicine.name} quantity updated.")
        else:
            messages.warning(request, f"Cannot add more — only {medicine.stock} in stock.")
    else:
        messages.success(request, f"{medicine.name} added to cart.")
    
    return redirect('store:cart')


@login_required(login_url='store:auth')
def cart_view(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('medicine').all()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
    })


@login_required(login_url='store:auth')
def update_cart(request, item_id):
    """Update cart item quantity via POST form submission."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        if cart_item.quantity < cart_item.medicine.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Quantity increased.")
        else:
            messages.warning(request, f"Cannot add more — only {cart_item.medicine.stock} in stock.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Quantity decreased.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect('store:cart')


@login_required(login_url='store:auth')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('store:cart')


@login_required(login_url='store:auth')
def update_cart_quantity(request, item_id):
    """Update cart item quantity via AJAX."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qty = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid data'}, status=400)

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if qty <= 0:
            cart_item.delete()
            return JsonResponse({'deleted': True})

        if qty > cart_item.medicine.stock:
            return JsonResponse({'error': f'Only {cart_item.medicine.stock} in stock'}, status=400)

        cart_item.quantity = qty
        cart_item.save()

        return JsonResponse({
            'quantity': cart_item.quantity,
            'subtotal': str(cart_item.get_subtotal()),
            'total': str(cart_item.cart.get_total())
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='store:auth')
@transaction.atomic
def checkout(request):
    """Process checkout with atomic transaction for data integrity."""
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('medicine').all()

    # Validate cart is not empty
    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('store:cart')

    # Validate stock for all items
    for item in items:
        if item.quantity > item.medicine.stock:
            messages.error(request, f"Not enough stock for {item.medicine.name}.")
            return redirect('store:cart')

    # Calculate total
    total = cart.get_total()
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        completed=True,
        total_price=total,
        status='pending'
    )

    # Create order items and update stock
    for item in items:
        OrderItem.objects.create(
            order=order,
            medicine=item.medicine,
            quantity=item.quantity,
            # Store price at time of order (optional enhancement)
        )
        # Update stock
        item.medicine.stock -= item.quantity
        item.medicine.save()

    # Clear cart
    items.delete()

    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('store:order_success', order_id=order.id)


@login_required(login_url='store:auth')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {
        'order': order,
        'total': order.total_price
    })


@login_required(login_url='store:auth')
def logout_view(request):
    logout(request)
    return redirect('store:auth')


# =============================
# DASHBOARD + CRUD
# =============================
@login_required(login_url='store:auth')
def dashboard(request):
    categories = Category.objects.annotate(medicine_count=Count('medicines'))
    medicines = Medicine.objects.select_related('category').all()

    category_form = None
    category_form_title = ''
    medicine_form = None
    medicine_form_title = ''

    # Forms logic if called with GET params
    if request.GET.get('add_category'):
        category_form = CategoryForm()
        category_form_title = 'Add Category'
    elif request.GET.get('add_medicine'):
        medicine_form = MedicineForm()
        medicine_form_title = 'Add Medicine'

    return render(request, 'store/dashboard.html', {
        'categories': categories,
        'medicines': medicines,
        'category_form': category_form,
        'category_form_title': category_form_title,
        'medicine_form': medicine_form,
        'medicine_form_title': medicine_form_title
    })


# ---------- Category CRUD ----------
@login_required(login_url='store:auth')
def category_add(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category added successfully.')
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Add Category'})


@login_required(login_url='store:auth')
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Edit Category'})


@login_required(login_url='store:auth')
def category_delete(request, id):
    """Delete category with protection for categories that have medicines."""
    category = get_object_or_404(Category, id=id)
    
    # Check if category has medicines
    if category.medicines.exists():
        messages.error(request, f"Cannot delete '{category.name}' - it contains medicines. Please remove or reassign them first.")
        return redirect('store:dashboard')
    
    category_name = category.name
    category.delete()
    messages.success(request, f"Category '{category_name}' deleted successfully.")
    return redirect('store:dashboard')


# ---------- Medicine CRUD ----------
@login_required(login_url='store:auth')
def medicine_add(request):
    form = MedicineForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Medicine added successfully.')
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Add Medicine'})


@login_required(login_url='store:auth')
def medicine_edit(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    form = MedicineForm(request.POST or None, request.FILES or None, instance=medicine)
    if form.is_valid():
        form.save()
        messages.success(request, 'Medicine updated successfully.')
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Edit Medicine'})


@login_required(login_url='store:auth')
def medicine_delete(request, id):
    """Delete medicine with protection for medicines that are in active orders."""
    medicine = get_object_or_404(Medicine, id=id)
    
    # Check if medicine is in any active orders
    if medicine.orderitem_set.filter(order__status__in=['pending', 'confirmed', 'processing', 'shipped']).exists():
        messages.error(request, f"Cannot delete '{medicine.name}' - it is part of active orders.")
        return redirect('store:dashboard')
    
    medicine_name = medicine.name
    medicine.delete()
    messages.success(request, f"Medicine '{medicine_name}' deleted successfully.")
    return redirect('store:dashboard')


# =============================
# SEARCH
# =============================
@login_required(login_url='store:auth')
def ajax_search(request):
    """AJAX endpoint for live search."""
    query = request.GET.get('q', '')
    if query:
        qs = Medicine.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]  # Limit results for performance
    else:
        qs = Medicine.objects.none()

    results = []
    for med in qs:
        results.append({
            'id': med.id,
            'name': med.name,
            'price': str(med.price),
            'stock': med.stock,
            'category': med.category.name if med.category else '',
        })

    return JsonResponse({'results': results})


@login_required(login_url='store:auth')
def search_medicines(request):
    """Full-page search with pagination."""
    query = request.GET.get('q', '')
    medicines = Medicine.objects.none()
    
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).select_related('category')

    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/search_results.html', {
        'medicines': page_obj,
        'query': query
    })


# =============================
# USER PROFILE & ORDERS
# =============================
@login_required(login_url='store:auth')
def user_profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_orders = orders.count()

    return render(request, 'store/profile.html', {
        'user': request.user,
        'total_orders': total_orders,
        'orders': orders
    })


@login_required(login_url='store:auth')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/order_history.html', {
        'orders': page_obj
    })


@login_required(login_url='store:auth')
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__medicine'), id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {
        'order': order
    })


@login_required(login_url='store:auth')
def medicines_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    medicines = Medicine.objects.filter(category=category).select_related('category')
    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/category_medicines.html', {
        'category': category,
        'medicines': page_obj
    })