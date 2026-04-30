# 🤖 AI Agent Prompt — Teryaq Pharmacy System (Production-Ready)

---

## 🎯 ROLE & MISSION

You are a **Senior Full-Stack Django Engineer** tasked with completing and hardening the **Teryaq Pharmacy System** for production deployment.

Your job is to:
1. **Analyze** the existing codebase thoroughly before touching anything
2. **Complete** missing pages and backend logic
3. **Harden** the system for production
4. **Never** break existing data, existing pages, or the existing design

---

## 📋 PROJECT CONTEXT

**Repository:** `https://github.com/MohamedAymn220/Teryaq-Pharmacy-System`

**Tech Stack (MUST NOT CHANGE):**
- Backend: **Django (Python)**
- Frontend: **HTML + Tailwind CSS** (same classes, same structure as existing templates)
- Database: **SQLite → PostgreSQL-ready** (do NOT change models that affect existing data)
- Auth: **Django Built-in Auth**
- Cart: **Database-backed Cart models** (Cart + CartItem) — NOT browser sessions or localStorage

**Existing App Structure:**
```
store/
├── models.py       → Category, Medicine, Order, OrderItem
├── views.py        → existing views
├── urls.py         → existing URL patterns
├── forms.py        → existing forms
├── templates/store/→ existing HTML templates (Tailwind CSS)
├── static/store/   → CSS, JS, images
TeryaqPharma/
├── settings.py
├── urls.py
```

---

## 🔒 ABSOLUTE CONSTRAINTS — READ BEFORE EVERY ACTION

```
❌ DO NOT modify any existing migration files
❌ DO NOT alter or delete any existing model fields (Category, Medicine, Order, OrderItem)
❌ DO NOT touch the database records or seed data
❌ DO NOT change any existing template's visual design, color scheme, or layout
❌ DO NOT change any existing URL that already works
❌ DO NOT switch the tech stack (no DRF, no Vue, no React)
❌ DO NOT use browser localStorage or sessionStorage for cart data
❌ DO NOT keep the old session-based cart logic — it must be fully replaced with DB Cart
❌ DO NOT remove any existing view or URL pattern
```

```
✅ ADD new pages using the EXACT same Tailwind CSS design pattern as existing pages
✅ EXTEND models only via new migrations (additive only, no breaking changes)
✅ FOLLOW the same Django MVT pattern used in the existing codebase
✅ USE the same base template ({% extends 'store/base.html' %}) for all new pages
✅ APPLY the same navbar, footer, cards, and button styles already in the project
```

---

## 🔍 STEP 1 — ANALYZE FIRST (Do this before writing any code)

Run these commands and read the output carefully:

```bash
# 1. Read ALL existing code
cat store/models.py
cat store/views.py
cat store/urls.py
cat store/forms.py

# 2. List ALL existing templates
find store/templates -name "*.html" | sort

# 3. Read each template to understand the design system
# Pay attention to: base.html, navbar, card components, button classes, color palette

# 4. Check settings
cat TeryaqPharma/settings.py

# 5. Check requirements
cat requirements.txt

# 6. Check existing migrations
ls store/migrations/
```

**After reading, document:**
- What URL patterns exist
- What templates exist
- What the base template structure is (nav, footer, CSS classes used)
- What design tokens are used (Tailwind color classes, spacing, etc.)

---

## 🏗️ STEP 2 — WHAT TO BUILD (Missing Features)

Build the following features **in this exact priority order**:

---

### 📄 A. Missing User-Facing Pages

#### A1. Medicine Search Page
- URL: `/search/`
- View: `search_medicines(request)` — GET param `q`, filter `Medicine.objects.filter(name__icontains=q)`
- Template: `store/search_results.html` — same medicine card design as existing listing page
- Add search bar to navbar (if not already present) using existing Tailwind input styles

#### A2. User Profile Page
- URL: `/profile/`
- View: `user_profile(request)` — `@login_required`
- Shows: username, email, join date, total orders count
- Template: `store/profile.html`
- No new model needed — use `request.user` and related `Order` objects

#### A3. Order Detail Page
- URL: `/orders/<int:order_id>/`
- View: `order_detail(request, order_id)` — `@login_required`, verify `order.user == request.user`
- Shows: order items, quantities, individual prices, total, order date, status badge
- Template: `store/order_detail.html`

#### A4. Order History Page (My Orders)
- URL: `/orders/`
- View: `order_history(request)` — `@login_required`
- Shows: all orders for `request.user`, paginated (10 per page)
- Template: `store/order_history.html`
- Add "My Orders" link to navbar for authenticated users

#### A5. Medicine Category Filter Page
- URL: `/category/<int:category_id>/`
- View: `medicines_by_category(request, category_id)`
- Filters medicines by category, paginated
- Template: `store/category_medicines.html` — reuse the same medicine card component

#### A6. Empty Cart Page / Checkout Confirmation
- Improve existing cart: if cart is empty, show a styled empty state (icon + message + "Browse Medicines" button)
- After order is placed: redirect to a success page `store/order_success.html` with order summary

---

### ⚙️ B. Backend Logic Improvements (No new pages, just fix/add logic)

#### B0. 🛒 DATABASE CART — Replace Session Cart (CRITICAL — Do This First)

The existing cart uses Django sessions (`request.session`). This must be **fully replaced** with a proper database-backed cart. This is the most important backend change.

**Why:** Session carts are lost on logout, can't be recovered across devices, and are not production-grade.

**Step 1 — Add Cart & CartItem models to `store/models.py`:**

```python
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_subtotal(self):
        return self.medicine.price * self.quantity

    class Meta:
        unique_together = ('cart', 'medicine')

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name}"
```

**Step 2 — Create migration:**
```bash
python manage.py makemigrations store --name="add_db_cart"
```

**Step 3 — Cart helper function (add to `views.py` or a new `utils.py`):**
```python
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart
```

**Step 4 — Rewrite all cart views to use DB Cart:**

Replace every `request.session['cart']` reference with DB queries:

```python
# ADD TO CART
@login_required
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    if medicine.stock <= 0:
        messages.error(request, f"{medicine.name} is out of stock.")
        return redirect('medicine_detail', pk=medicine_id)
    
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
    return redirect('view_cart')


# VIEW CART
@login_required
def view_cart(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('medicine').all()
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'total': cart.get_total(),
    })


# UPDATE QUANTITY
@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')
    if action == 'increase':
        if cart_item.quantity < cart_item.medicine.stock:
            cart_item.quantity += 1
            cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()
    return redirect('view_cart')


# REMOVE FROM CART
@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')


# PLACE ORDER (checkout)
@login_required
def place_order(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('medicine').all()
    
    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')
    
    # Validate stock before placing
    for item in items:
        if item.quantity > item.medicine.stock:
            messages.error(request, f"Not enough stock for {item.medicine.name}.")
            return redirect('view_cart')
    
    # Create Order
    total = cart.get_total()
    order = Order.objects.create(user=request.user, total_price=total)
    
    for item in items:
        OrderItem.objects.create(
            order=order,
            medicine=item.medicine,
            quantity=item.quantity
        )
        # Deduct stock
        item.medicine.stock -= item.quantity
        item.medicine.save()
    
    # Clear cart after order
    items.delete()
    
    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('order_detail', order_id=order.id)
```

**Step 5 — Update cart template (`store/cart.html`) to use DB Cart:**
- Loop over `items` (CartItem objects) instead of session dict
- Use `{% url 'update_cart' item.id %}` for quantity controls
- Show `item.medicine.name`, `item.medicine.price`, `item.quantity`, `item.get_subtotal`
- Show cart total from `cart.get_total`
- Use `@login_required` redirect — unauthenticated users go to login page

**Step 6 — Show cart item count in navbar:**
```python
# In context_processors.py (create if not exists):
def cart_count(request):
    if request.user.is_authenticated:
        try:
            count = request.user.cart.get_total_items()
        except Exception:
            count = 0
    else:
        count = 0
    return {'cart_count': count}
```
Register in `settings.py` under `TEMPLATES → OPTIONS → context_processors`:
```python
'store.context_processors.cart_count',
```
Then in `base.html` navbar, show `{{ cart_count }}` badge on the cart icon.

**Step 7 — URL patterns to add/update:**
```python
path('cart/', views.view_cart, name='view_cart'),
path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('cart/checkout/', views.place_order, name='place_order'),
```

**⚠️ Migration note:** After adding Cart + CartItem models, existing users will have no cart. That is fine — `get_or_create_cart()` creates one lazily on first use. Do NOT seed or migrate old session data.

#### B1. Order Status Field
Add `status` field to `Order` model:
```python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
```
- Create new migration: `python manage.py makemigrations store --name="add_order_status"`
- Show status as a colored badge in Order History and Order Detail pages
- Add status management to Admin Dashboard

#### B2. Stock Management
Add `stock` field to `Medicine` model:
```python
stock = models.PositiveIntegerField(default=0)
```
- Create new migration: `python manage.py makemigrations store --name="add_medicine_stock"`
- When an order is placed: deduct stock (`medicine.stock -= quantity`)
- If stock is 0: show "Out of Stock" badge on medicine card, disable "Add to Cart" button
- Restore stock if order is cancelled (admin action)

#### B3. Input Validation & Error Handling
- Validate cart quantities: if `quantity > medicine.stock`, show error message
- Add `messages` framework feedback for: add to cart, order placed, login required
- Handle 404 gracefully for invalid medicine/category IDs (use `get_object_or_404`)
- Protect against negative quantities in cart session

#### B4. Pagination
- Add `Paginator` to: medicine listing, order history, admin medicine list
- Use 12 items per page for medicines, 10 for orders
- Add pagination controls in the same Tailwind style as the rest of the site

#### B5. Admin Dashboard Enhancements
- Add order status update form in admin order detail view
- Add stock field display in admin medicine management
- Add simple dashboard stats: total orders, total revenue, low stock medicines (< 10 units)

---

### 🚀 C. Production Readiness

#### C1. Settings Configuration
Restructure `TeryaqPharma/settings.py`:

```python
import os
from pathlib import Path

# Read from environment variables with safe defaults
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database — keep SQLite as default, support PostgreSQL via env
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security (only in production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

#### C2. Update requirements.txt
Add these packages (keep all existing ones):
```
dj-database-url>=2.1.0
gunicorn>=21.2.0
whitenoise>=6.6.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
Pillow>=10.0.0
```

#### C3. Whitenoise for Static Files
In `settings.py` MIDDLEWARE, add after `SecurityMiddleware`:
```python
'whitenoise.middleware.WhiteNoiseMiddleware',
```

#### C4. Create `.env.example`
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/teryaq_db
```

#### C5. Create `Procfile` for deployment:
```
web: gunicorn TeryaqPharma.wsgi:application
```

#### C6. Create `runtime.txt`:
```
python-3.11.x
```

---

## 🎨 STEP 3 — DESIGN RULES (Mandatory)

Before writing any template, read `store/templates/store/base.html` carefully. Then:

```
✅ Use {% extends 'store/base.html' %} on EVERY new template
✅ Use {% block content %} ... {% endblock %} for page content
✅ Copy the exact card structure from medicine_list.html for medicine cards
✅ Use the same Tailwind color classes (look at existing buttons, headings, backgrounds)
✅ Use {% load static %} when needed, following the same pattern
✅ Use {% url 'view_name' %} for all links — no hardcoded URLs
✅ Use {% if messages %} block from base.html for flash messages
✅ Make all new pages fully responsive (mobile-first, same as existing pages)
```

**Status badge color convention (use for order status):**
```
pending    → yellow-100 text-yellow-800
confirmed  → blue-100 text-blue-800
processing → purple-100 text-purple-800
shipped    → indigo-100 text-indigo-800
delivered  → green-100 text-green-800
cancelled  → red-100 text-red-800
```

---

## 📋 STEP 4 — EXECUTION ORDER

Execute in this exact order to avoid breaking things:

```
1.  Read all existing code (STEP 1)
2.  Add Cart + CartItem models to models.py
3.  Create DB cart migration: makemigrations store --name="add_db_cart"
4.  Create new migrations (B1: status, B2: stock) → makemigrations only, DO NOT migrate yet
5.  Rewrite all cart views to use DB Cart (remove all request.session cart logic)
6.  Create context_processors.py with cart_count, register in settings.py
7.  Update views.py — add remaining new views at the bottom
8.  Update urls.py — add new URL patterns, do NOT modify existing ones
9.  Update forms.py — add new forms if needed
10. Create new templates — update cart.html, do NOT modify other existing templates
11. Update requirements.txt
12. Update settings.py — add production settings at the bottom
13. Create Procfile, .env.example, runtime.txt
14. Run: python manage.py migrate
15. Run: python manage.py collectstatic --noinput
16. Test every existing URL still works
17. Test every new URL works
18. Test: add to cart → view cart → place order → order detail
```

---

## ✅ DEFINITION OF DONE

Before finishing, verify:

```bash
# All existing pages still load
curl -s http://localhost:8000/ | grep -i "teryaq"
curl -s http://localhost:8000/medicines/ | grep -i "medicine"

# New pages load
curl -s http://localhost:8000/search/?q=panadol
curl -s http://localhost:8000/profile/   # Should redirect to login
curl -s http://localhost:8000/orders/

# No broken migrations
python manage.py showmigrations

# Static files collected
python manage.py collectstatic --dry-run

# No import errors
python manage.py check --deploy
```

**The system is done when:**
- [ ] All existing URLs work exactly as before
- [ ] Cart is fully database-backed (Cart + CartItem models exist in DB)
- [ ] Zero `request.session` cart references remain in views.py
- [ ] Cart persists after logout/login
- [ ] Cart count badge shows in navbar
- [ ] All 6 new pages exist and follow the same design
- [ ] Order status field exists and shows in UI
- [ ] Stock field exists and "Out of Stock" badge shows
- [ ] Pagination works on medicine listing and orders
- [ ] `python manage.py check --deploy` passes with no critical errors
- [ ] `requirements.txt` is updated
- [ ] `Procfile` and `.env.example` exist
- [ ] No hardcoded `DEBUG=True` or `SECRET_KEY` in production settings

---

## 🚫 WHAT NOT TO DO (Repeat Constraints)

```
🚫 Don't change Category/Medicine/Order/OrderItem field names (breaks existing data)
🚫 Don't redesign any existing page
🚫 Don't add JavaScript frameworks (Vue, React, Alpine) — vanilla JS only if needed
🚫 Don't add Django REST Framework
🚫 Don't use browser localStorage or sessionStorage for cart — DB only
🚫 Don't leave any request.session cart logic in the codebase
🚫 Don't rename existing views or URL names
🚫 Don't add fixtures or seed data
🚫 Don't run migrate before reading all existing migrations
🚫 Don't squash migrations
```

---

*Prompt engineered for Teryaq Pharmacy System — Django + Tailwind CSS — Production Hardening Agent*
