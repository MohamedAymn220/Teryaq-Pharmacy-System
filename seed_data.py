"""
seed_data.py — حطه جنب manage.py وشغّله بـ:
  python seed_data.py

سيعمل بيانات حقيقية من الأدوية والكاتيجوريز الموجودة عندك
"""
import os, sys, django, random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TeryaqPharma.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Medicine, Category, Order, OrderItem

# ── تأكد إن فيه أدوية موجودة ──────────────────────────────────────────────
medicines = list(Medicine.objects.all())
if not medicines:
    print("❌  مفيش أدوية في قاعدة البيانات! أضف أدوية الأول من الـ Dashboard.")
    sys.exit(1)

print(f"✅  لقيت {len(medicines)} دواء")

# ── User تجريبي ────────────────────────────────────────────────────────────
user, _ = User.objects.get_or_create(
    username='demo_customer',
    defaults={'email': 'demo@teryaq.com', 'first_name': 'Demo'}
)
if _:
    user.set_password('demo123')
    user.save()
    print("✅  تم إنشاء مستخدم تجريبي: demo_customer / demo123")

# ── إنشاء أوردرات ──────────────────────────────────────────────────────────
STATUSES = ['delivered', 'delivered', 'delivered', 'pending', 'confirmed', 'cancelled']
now = timezone.now()
created = 0

for i in range(80):
    # أوردرات موزعة على آخر 12 شهر
    days_ago = random.randint(1, 365)
    order_date = now - timedelta(days=days_ago)

    status = random.choice(STATUSES)
    
    # اختار 1-3 أدوية عشوائية
    num_items = random.randint(1, 3)
    selected = random.sample(medicines, min(num_items, len(medicines)))
    
    # احسب السعر الكلي
    total = sum(random.randint(1, 4) * med.price for med in selected)

    order = Order(
        user=user,
        status=status,
        completed=(status == 'delivered'),
        total_price=total,
    )
    order.save()
    # تعديل التاريخ بعد الحفظ (auto_now_add)
    Order.objects.filter(pk=order.pk).update(created_at=order_date)

    for med in selected:
        qty = random.randint(1, 4)
        OrderItem.objects.create(order=order, medicine=med, quantity=qty)

    created += 1

print(f"✅  تم إنشاء {created} أوردر تجريبي بأدوية حقيقية من قاعدة البيانات")
print("🚀  افتح http://127.0.0.1:8000/dashboard/income/ وشوف النتيجة!")
