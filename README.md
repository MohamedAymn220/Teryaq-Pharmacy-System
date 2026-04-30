# 🏥 Teryaq-Pharmacy-System

## 📌 Project Overview

A **full-featured Pharmacy Management System** built using **Django**, designed and implemented with a **real-world software engineering mindset**. This project simulates an actual pharmacy workflow, focusing on scalability, clean architecture, and clear separation of concerns.

This is **not a tutorial project** — it is a practical system suitable for portfolios, academic submission, and real deployment after minor extensions.

---

## 🎯 Project Goals

- Build a real e-commerce–like pharmacy system
- Apply Django Authentication & Authorization correctly
- Practice clean backend architecture
- Deliver a responsive and user-friendly UI
- Create a solid base for future expansion

---

## 👥 User Roles

### 👤 Client (User)

- Register / Login
- Browse medicines by category
- View medicine details
- Add medicines to cart
- Update quantities in cart
- Place orders

### 🛠️ Admin (Dashboard)

- Secure admin dashboard
- Manage categories (CRUD)
- Manage medicines (CRUD + images)
- View and manage orders
- Restricted access using authorization

---

## 🔐 Authentication & Authorization

| Concept        | Implementation                          |
| -------------- | --------------------------------------- |
| Authentication | Django Built-in Auth (Login / Register) |
| Authorization  | `login_required`, staff checks          |
| Cart Security  | Django Sessions                         |

Only authorized users can access sensitive pages such as the dashboard.

---

## 🛒 Cart System (Session-Based)

- Cart stored using Django sessions
- Each item stored as: `{medicine_id: quantity}`
- Supports:
  - Add to cart
  - Increase / decrease quantity
  - Remove item

Efficient, simple, and scalable for small to medium systems.

---

## 📦 Orders System

- Each Order belongs to one User
- Each Order contains multiple OrderItems
- Total price calculated dynamically
- Easily extendable to payment gateways

---

## 🏗️ System Architecture

![System Architecture](docs/images/architecture.png)

```
Client (Browser)
     ↓ HTTP Requests
Django Views (Controller Logic)
     ↓
Django Models (Business Logic)
     ↓
Database (SQLite → PostgreSQL Ready)
```

This architecture follows Django MVT with clear separation between presentation, logic, and data layers.

---

## 📐 UML Diagrams

### Client & Admin Use Case Diagram

![Use Case Diagram](docs/images/usecase.png)

### Class Diagram

![Class Diagram](docs/images/class-diagram.png)

---

## 📐 UML – Use Case Diagram (Textual)

### Client Use Cases

- Register / Login
- Browse Medicines
- Manage Cart
- Place Order

### Admin Use Cases

- Login
- Manage Medicines
- Manage Categories
- View Orders

---

## 🧩 UML – Class Diagram (Core Models)

- **Category**

  - name
  - image

- **Medicine**

  - name
  - price
  - image
  - category

- **Order**

  - user
  - created_at
  - total_price

- **OrderItem**
  - order
  - medicine
  - quantity

---

## 🧪 Engineering Principles Applied

- Separation of Concerns
- Reusability
- Clean URLs
- Secure Access Control
- Scalable Structure

---

## 🧰 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **Database:** SQLite (development), PostgreSQL (production)
- **Auth:** Django Authentication System with custom registration form
- **Containerization:** Docker, Docker Compose
- **Web Server:** Gunicorn, Nginx
- **Caching:** Redis
- **Version Control:** Git & GitHub

---

## 📂 Project Structure

```
Teryaq-Pharmacy-System/
│
├── TeryaqPharma/              # Django Project Settings
│   ├── settings.py            # Configuration (PostgreSQL, Redis, Security)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── store/                     # Main Application
│   ├── migrations/
│   ├── static/store/          # Static files (CSS, JS, Images)
│   ├── templates/store/       # HTML Templates
│   │   └── auth_complete.html # Sign In / Create Account page
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py               # CustomUserCreationForm with Pharmacy fields
│   ├── models.py              # Category, Medicine, Order, OrderItem, Cart
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── docs/                      # Documentation & Configs
│   ├── nginx.conf             # Nginx reverse proxy configuration
│   └── db_init.sql            # PostgreSQL initialization script
│
├── media/                     # Uploaded media files
│   ├── category_images/
│   └── medicines/
│
├── .env.example               # Environment variables template
├── .dockerignore              # Docker ignore rules
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Full stack orchestration
├── db.sqlite3                 # Development database
├── manage.py
├── README.md
├── requirements.txt           # Python dependencies
└── runtime.txt                # Python version specification
```

---

## 🎓 Academic Value

This project demonstrates:

- Practical backend development
- Correct use of MVC/MVT concepts
- Secure web application design
- Database relationships

Suitable for:

- Faculty submission
- Software Engineering courses
- Django practical exams

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (for production)
- Docker & Docker Compose (for containerized deployment)

### Local Development (Without Docker)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TeryaqPharma
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Production Deployment (With Docker)

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

2. **Build and start containers**
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**
   - Web: http://localhost:8000
   - Admin: http://localhost:8000/admin/

4. **Stop containers**
   ```bash
   docker-compose down
   ```

### Key Features

- **Custom Registration Form**: Includes Pharmacy Name and Phone fields
- **PostgreSQL Support**: Production-ready database configuration
- **Redis Caching**: Improved performance with Redis cache
- **Nginx Reverse Proxy**: Static file serving and rate limiting
- **Security Headers**: CSP, HSTS, X-Frame-Options configured

## 🚀 Future Enhancements

- Online Payment Integration
- Order Status Tracking
- REST API (DRF)
- Mobile App Support
- Advanced User Profiles with pharmacy-specific data
- Email verification for new accounts
- Password reset functionality

---

## 👨‍💻 Developer Statement

> This project reflects my mindset as a Computer Engineering student who believes that **real learning happens when software solves real problems**. Every feature was implemented intentionally — not copied — and designed to be clean, scalable, and production-ready.

---

## 👨‍💻 Developer

**Mohamed Ayman**  
Computer Engineering – Systems & Computers  
Focused on building scalable, real-world systems using Django and modern web technologies.

---

## ✅ Final Notes

This system is not the end — it is a **strong foundation**.

Built to grow. Built to matter.
