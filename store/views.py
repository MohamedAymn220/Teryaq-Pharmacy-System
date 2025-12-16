from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .models import Medicine, Category, Order, OrderItem
from .forms import CategoryForm, MedicineForm


# =============================
# AUTH (LOGIN + REGISTER)
# =============================
def auth_view(request):
    if request.user.is_authenticated:
        return redirect('store:home')

    form = UserCreationForm()

    if request.method == 'POST':
        action = request.GET.get('action')

        # ---------- LOGIN ----------
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('store:home')
            else:
                messages.error(request, 'Username or password is incorrect')

        # ---------- SIGNUP ----------
        elif action == 'signup':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('store:home')
            else:
                messages.error(request, 'Please fix the errors below')

    return render(request, 'store/auth.html', {'form': form})


# =============================
# PROTECTED PAGES
# =============================
@login_required(login_url='store:auth')
def home(request):
    categories = Category.objects.all()
    medicines = Medicine.objects.all()
    
    context = {
        'categories': categories,
        'medicines': medicines,
        'MEDIA_URL': settings.MEDIA_URL,  # إضافة MEDIA_URL للقالب
    }
    
    return render(request, 'store/home.html', context)

@login_required(login_url='store:auth')
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'store/medicine_list.html', {'medicines': medicines})


@login_required(login_url='store:auth')
def medicine_detail(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    return render(request, 'store/medicine_detail.html', {'medicine': medicine})


@login_required(login_url='store:auth')
def category_detail(request, id):
    category = get_object_or_404(Category, id=id)
    medicines = Medicine.objects.filter(category=category)
    return render(request, 'store/category_detail.html', {
        'category': category,
        'medicines': medicines
    })


# =============================
# CART USING SESSION
# =============================
@login_required(login_url='store:auth')
def add_to_cart(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart
    return redirect('store:medicine_list')

@login_required(login_url='store:auth')
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    cart.pop(str(id), None)
    request.session['cart'] = cart
    return redirect('store:cart')

@login_required(login_url='store:auth')
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for med_id, qty in cart.items():
        medicine = get_object_or_404(Medicine, id=med_id)
        subtotal = medicine.price * qty
        cart_items.append({
            'id': med_id,
            'medicine': medicine,
            'quantity': qty,
            'subtotal': subtotal
        })
        total += subtotal

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required(login_url='store:auth')
def update_cart_quantity(request, id):
    import json
    from django.http import JsonResponse

    if request.method == 'POST':
        data = json.loads(request.body)
        qty = int(data.get('quantity', 1))

        cart = request.session.get('cart', {})
        if str(id) in cart:
            cart[str(id)] = qty
        request.session['cart'] = cart

        # حساب الإجمالي
        total = 0
        subtotal = 0
        for med_id, q in cart.items():
            med = Medicine.objects.get(id=med_id)
            line_total = med.price * q
            total += line_total
            if str(id) == med_id:
                subtotal = line_total

        return JsonResponse({'quantity': qty, 'subtotal': subtotal, 'total': total})
    return JsonResponse({'error': 'Invalid request'}, status=400)


    

@login_required(login_url='store:auth')
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('store:cart')  # لو العربة فاضية

    # إنشاء الطلب
    order = Order.objects.create(user=request.user, completed=True)

    total = 0  # لحساب الإجمالي

    for medicine_id, quantity in cart.items():
        medicine = Medicine.objects.get(id=medicine_id)

        # إنشاء OrderItem
        OrderItem.objects.create(
            order=order,
            medicine=medicine,
            quantity=quantity
        )

        # تقليل الكمية من المخزن
        medicine.stock -= quantity
        medicine.save()

        total += medicine.price * quantity

    # مسح العربة بعد الشراء
    request.session['cart'] = {}

    # إعادة التوجيه لصفحة النجاح
    return redirect('store:order_success', order_id=order.id)
    

@login_required(login_url='store:auth')
def order_success(request, order_id):
    # جلب الطلب الخاص بالمستخدم
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # حساب الإجمالي من عناصر الطلب
    total = sum(item.total_price() for item in order.items.all())
    
    # تمرير البيانات للتمبلت
    return render(request, 'store/order_success.html', {
        'order': order,
        'total': total
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
    categories = Category.objects.all()
    medicines = Medicine.objects.all()

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
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Add Category'})


@login_required(login_url='store:auth')
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Edit Category'})


@login_required(login_url='store:auth')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('store:dashboard')


# ---------- Medicine CRUD ----------
@login_required(login_url='store:auth')
def medicine_add(request):
    form = MedicineForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Add Medicine'})


@login_required(login_url='store:auth')
def medicine_edit(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    form = MedicineForm(request.POST or None, request.FILES or None, instance=medicine)
    if form.is_valid():
        form.save()
        return redirect('store:dashboard')
    return render(request, 'store/dashboard_form.html', {'form': form, 'title': 'Edit Medicine'})


@login_required(login_url='store:auth')
def medicine_delete(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    medicine.delete()
    return redirect('store:dashboard')

from django.http import HttpResponseRedirect

@login_required(login_url='store:auth')
def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    cart.pop(str(id), None)  # نحذف المنتج من العربة
    request.session['cart'] = cart
    return redirect('store:cart')


def medicine_list(request):
    query = request.GET.get('q', '')  # يجيب قيمة البحث من الـ form
    if query:
        # البحث في الاسم بالعربي أو بالانجليزي أو أي حقل إضافي
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) | Q(name_en__icontains=query)
        )
    else:
        medicines = Medicine.objects.all()
    
    context = {
        'medicines': medicines,
        'categories': Category.objects.all(),
        'query': query
    }
    return render(request, 'store/medicine_list.html', context)

from django.http import JsonResponse
from django.db.models import Q

from .models import Order
@login_required(login_url='store:auth')
def ajax_search(request):
    query = request.GET.get('q', '')
    if query:
        # البحث بالعربي فقط
        qs = Medicine.objects.filter(name__icontains=query)
    else:
        qs = Medicine.objects.all()

    results = []
    for med in qs:
        results.append({
            'id': med.id,
            'name': med.name,
            'price': str(med.price),
            'stock': med.stock,
        })

    return JsonResponse({'results': results})
