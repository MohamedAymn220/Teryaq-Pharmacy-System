from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicine/<int:id>/', views.medicine_detail, name='medicine_detail'),

    # Categories
    path('category/<int:id>/', views.category_detail, name='category_detail'),
    path('category/<int:category_id>/medicines/', views.medicines_by_category, name='category_medicines'),

    # Search
    path('search/', views.search_medicines, name='search'),

    # User Profile & Orders
    path('profile/', views.user_profile, name='profile'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # CRUD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/add/', views.category_add, name='add_category'),
    path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),

    path('medicine/add/', views.medicine_add, name='add_medicine'),
    path('medicine/edit/<int:id>/', views.medicine_edit, name='medicine_edit'),
    path('medicine/delete/<int:id>/', views.medicine_delete, name='medicine_delete'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/update-form/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('ajax/search/', views.ajax_search, name='ajax_search'),

    # Auth
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    # Admin Dashboard
    path('dashboard/income/', views.income_dashboard, name='income_dashboard'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]
