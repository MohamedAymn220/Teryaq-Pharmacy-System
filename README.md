# 🏥 Teryaq Pharmacy (ترياق فارما)

<div align="center">

![Django](https://img.shields.io/badge/Django-5.2+-092E1A?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D2?style=for-the-badge&logo=tailwind-css&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

> ### 🌐 English | Arabic

A full-featured online pharmacy management system built with Django 5.2 + Tailwind CSS. Manage medicines, categories, shopping cart, orders, and view detailed income analytics with interactive charts.

نظام إدارة صيدلية متكامل مبني باستخدام Django 5.2 + Tailwind CSS. إدارة الأدوية والفئات وسلة التسوق والطلبات مع رسوم بيانية تفاعلية.

---

## 📁 Project Structure | هيكل المشروع

```
Teryaq-Pharmacy-System/
├── TeryaqPharma/              # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Project configuration
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point
├── store/                    # Main application
│   ├── models.py             # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URLs
│   ├── forms.py             # Django forms
│   ├── admin.py            # Admin configuration
│   ├── apps.py             # App configuration
│   ├── tests.py            # Unit tests
│   ├── context_processors.py
│   ├── order_services.py   # Order business logic
│   ├── dashboard_service.py # Analytics data service
│   ├── dashboard_view.py  # Dashboard view
│   ├── templates/store/    # HTML templates
│   └── static/store/      # CSS/JS files
|
├── docs/                   # Documentation
│   ├── db_init.sql        # Database initialization
│   └── nginx.conf         # Nginx config
|
├── media/                  # User uploaded files
│   ├── medicines/         # Product images
│   └── category_images/   # Category images
|
├── staticfiles/           # Collected static files
├── requirements.txt     # Python dependencies
├── manage.py           # Django management CLI
├── seed_data.py        # Sample data seeder
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose
├── Procfile           # Heroku deployment
├── runtime.txt        # Python runtime
└── README.md         # This file
```

---

## 🗃️ Database Models | نماذج البيانات

### Profile | الملف الشخصي

| Field           | الحقل         | Type                | الوصف         |
| --------------- | ------------- | ------------------- | ------------- |
| user            | المستخدم      | OneToOneField(User) | User account  |
| role            | الدور         | CharField           | admin/user    |
| profile_picture | صورة الملف    | URLField            | Avatar URL    |
| created_at      | تاريخ الإنشاء | DateTimeField       | Creation date |
| updated_at      | تاريخ التحديث | DateTimeField       | Last update   |

### Category | الفئة

| Field       | الحقل  | Type           | الوصف          |
| ----------- | ------ | -------------- | -------------- |
| name        | الاسم  | CharField(100) | Category name  |
| description | الوصف  | TextField      | Description    |
| image       | الصورة | ImageField     | Category image |

### Medicine | الدواء

| Field       | الحقل   | Type                 | الوصف              |
| ----------- | ------- | -------------------- | ------------------ |
| name        | الاسم   | CharField(100)       | Medicine name      |
| description | الوصف   | TextField            | Description        |
| price       | السعر   | DecimalField         | Price in EGP       |
| stock       | المخزون | PositiveIntegerField | Available quantity |
| category    | الفئة   | ForeignKey(Category) | Category           |
| image       | الصورة  | ImageField           | Product image      |

### Order | الطلب

| Field       | الحقل          | Type             | الوصف                                                    |
| ----------- | -------------- | ---------------- | -------------------------------------------------------- |
| user        | المستخدم       | ForeignKey(User) | Customer                                                 |
| created_at  | تاريخ الإنشاء  | DateTimeField    | Order date                                               |
| completed   | مكتمل          | BooleanField     | Is completed                                             |
| status      | الحالة         | CharField        | pending/confirmed/processing/shipped/delivered/cancelled |
| total_price | السعر الإجمالي | DecimalField     | Total price                                              |

### OrderItem | عنصر الطلب

| Field    | الحقل  | Type                 | الوصف    |
| -------- | ------ | -------------------- | -------- |
| order    | الطلب  | ForeignKey(Order)    | Order    |
| medicine | الدواء | ForeignKey(Medicine) | Product  |
| quantity | الكمية | PositiveIntegerField | Quantity |

### Payment | الدفع

| Field          | الحقل       | Type              | الوصف          |
| -------------- | ----------- | ----------------- | -------------- |
| order          | الطلب       | ForeignKey(Order) | Order          |
| amount         | المبلغ      | DecimalField      | Amount paid    |
| status         | الحالة      | CharField         | Payment status |
| payment_method | طريقة الدفع | CharField         | Payment method |
| created_at     | تاريخ الدفع | DateTimeField     | Payment date   |

### Cart | السلة

| Field      | الحقل         | Type                | الوصف         |
| ---------- | ------------- | ------------------- | ------------- |
| user       | المستخدم      | OneToOneField(User) | Owner         |
| created_at | تاريخ الإنشاء | DateTimeField       | Creation date |
| updated_at | تاريخ التحديث | DateTimeField       | Last update   |

### CartItem | عنصر السلة

| Field    | الحقل         | Type                 | الوصف         |
| -------- | ------------- | -------------------- | ------------- |
| cart     | السلة         | ForeignKey(Cart)     | Cart          |
| medicine | الدواء        | ForeignKey(Medicine) | Product       |
| quantity | الكمية        | PositiveIntegerField | Quantity      |
| added_at | تاريخ الإضافة | DateTimeField        | Addition date |

---

## 📋 URL Routes | روابط الموقع

| URL                          | View                    | الوصف                               |
| ---------------------------- | ----------------------- | ----------------------------------- |
| `/`                          | `home`                  | Home page - الرئيسية                |
| `/medicines/`                | `medicine_list`         | All medicines - جميع الأدوية        |
| `/medicine/<id>/`            | `medicine_detail`       | Medicine details - تفاصيل الدواء    |
| `/category/<id>/`            | `category_detail`       | Category detail - تفاصيل الفئة      |
| `/category/<id>/medicines/`  | `medicines_by_category` | Medicines in category - أدوية الفئة |
| `/search/`                   | `search_medicines`      | Search results - نتائج البحث        |
| `/profile/`                  | `user_profile`          | User profile - الملف الشخصي         |
| `/orders/`                   | `order_history`         | Order history - سجل الطلبات         |
| `/orders/<id>/`              | `order_detail`          | Order details - تفاصيل الطلب        |
| `/dashboard/`                | `dashboard`             | Admin dashboard - لوحة الإدارة      |
| `/dashboard/income/`         | `income_dashboard`      | Income analytics - تحليل الإيرادات  |
| `/category/add/`             | `category_add`          | Add category - إضافة فئة            |
| `/category/edit/<id>/`       | `category_edit`         | Edit category - تعديل فئة           |
| `/category/delete/<id>/`     | `category_delete`       | Delete category - حذف فئة           |
| `/medicine/add/`             | `medicine_add`          | Add medicine - إضافة دواء           |
| `/medicine/edit/<id>/`       | `medicine_edit`         | Edit medicine - تعديل دواء          |
| `/medicine/delete/<id>/`     | `medicine_delete`       | Delete medicine - حذف دواء          |
| `/cart/`                     | `cart_view`             | Shopping cart - سلة التسوق          |
| `/cart/add/<id>/`            | `add_to_cart`           | Add to cart - إضافة للسلة           |
| `/cart/update/<id>/`         | `update_cart_quantity`  | Update quantity - تحديث الكمية      |
| `/cart/remove/<id>/`         | `remove_from_cart`      | Remove from cart - حذف من الس��ة    |
| `/checkout/`                 | `checkout`              | Checkout - الدفع                    |
| `/order-success/<id>/`       | `order_success`         | Order success - نجاح الطلب          |
| `/order/<id>/update-status/` | `update_order_status`   | Update status - تحديث الحالة        |
| `/ajax/search/`              | `ajax_search`           | AJAX search - بحث فوري              |
| `/auth/`                     | `auth_view`             | Login/Register - تسجيل الدخول       |
| `/logout/`                   | `logout_view`           | Logout - تسجيل الخروج               |

---

## ✨ Features | المميزات

| Feature                    | الوصف                               |
| -------------------------- | ----------------------------------- |
| 🔐 **User Authentication** | تسجيل الدخول/التسجيل مع دورات مخصصة |
| 💊 **Medicine Catalog**    | كتالوج الأدوية مع تصفية حسب الفئة   |
| 🏷️ **Categories**          | فئات المنتجات مع صور                |
| 🛒 **Shopping Cart**       | نظام سلة تسوق متكامل                |
| 📦 **Order Management**    | إدارة الطلبات مع تتبع الحالة        |
| 📊 **Admin Dashboard**     | لوحة تحكم_ADMIN مع عمليات CRUD      |
| 📈 **Income Analytics**    | تحليل الإيرادات مع Chart.js         |
| 🔍 **Live Search**         | بحث AJAX فوري                       |
| 📱 **Responsive Design**   | تصميم متجاوب مع Tailwind CSS        |
| 🎨 **Modern UI**           | واجهة مستخدم عصرية وأنيقة           |

---

## 🛠️ Tech Stack | التقنيات

| Category             | Technology   | الإصدار  |
| -------------------- | ------------ | -------- |
| **Backend**          | Django       | 5.2+     |
| **Backend**          | Python       | 3.13     |
| **Frontend**         | Tailwind CSS | 3.4      |
| **Frontend**         | Chart.js     | 4.4      |
| **Frontend**         | Vanilla JS   | ES6+     |
| **Database**         | SQLite       | 3        |
| **Image Processing** | Pillow       | 10+      |
| **Static Files**     | Whitenoise   | 6+       |
| **Authentication**   | Django Auth  | Built-in |

---

## 🚀 Installation & Setup | التثبيت والتشغيل

### 1. Clone the Repository | استنساخ المشروع

```bash
git clone https://github.com/MohamedAymn220/Teryaq-Pharmacy-System.git
cd Teryaq-Pharmacy-System
```

### 2. Create Virtual Environment | إنشاء بيئة افتراضية

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies | تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

### 4. Run Migrations | تشغيل الترحيلات

```bash
python manage.py migrate
```

### 5. Create Superuser | إنشاء مدير système

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 6. (Optional) Load Seed Data | (اختياري) تحميل بيانات تجريبية

```bash
python manage.py shell < seed_data.py
# Or run the seeder function
```

### 7. Run Server | تشغيل السيرفر

```bash
python manage.py runserver
```

### 8. Access the Application | الوصول للتطبيق

| URL                              | الوصف           |
| -------------------------------- | --------------- |
| http://127.0.0.1:8000/           | Main store      |
| http://127.0.0.1:8000/dashboard/ | Admin dashboard |
| http://127.0.0.1:8000/auth/      | Login/Register  |

---

## ⚙️ Environment Variables | متغيرات البيئة

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (optional - uses SQLite by default)
DATABASE_NAME=db.sqlite3

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=BASE_DIR / 'media'

# Static Files
STATIC_URL=/static/
STATIC_ROOT=BASE_DIR / 'staticfiles'
```
### 🗃️ Database ERD
![ERD](docs/screenshots/erd.png)
---

## 📸 Screenshots | لقطات الشاشة
![Home Page](docs/screenshots/home.png)
![Admin Dashboard](docs/screenshots/dashboard.png)
![Income Analytics](docs/screenshots/analytics.png)


| Page             | الصفحة           |
| ---------------- | ---------------- |
| Home             | الرئيسية         |
| Medicine List    | قائمة الأدوية    |
| Cart             | السلة            |
| Dashboard        | لوحة التحكم      |
| Income Analytics | تحليل الإيراد��ت |

---

## 📄 License | الترخيص

<div align="center">

**MIT License** - Feel free to use, modify, and distribute.

</div>

---

## 👤 Author | المؤلف

<div align="center">

**Mohamed Ayman**

[![GitHub](https://img.shields.io/badge/GitHub-MohamedAymn220-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MohamedAymn220)
[![Email](https://img.shields.io/badge/Email-mohamedayman_@outlook.com-D14836?style=for-the-badge&logo=microsoft-outlook&logoColor=white)](mailto:mohamedayman_@outlook.com)

</div>

---

<div align="center">

**Made with Mohamed Ayaman❤️ in Egypt**

</div>
