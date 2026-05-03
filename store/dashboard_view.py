from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta
import json
from decimal import Decimal

from store.models import Order, OrderItem


def get_income_dashboard_data():
    """
    Optimized Django ORM queries for income dashboard.
    All aggregations happen at database level - O(1) Python loops.
    Target: <200ms backend for 100k+ orders.
    
    Returns dict with Chart.js-ready arrays.
    """
    now = timezone.now()
    
    # === SHARED QUERYSETS (computed once) ===
    delivered_qs = Order.objects.filter(status='delivered')
    all_orders_qs = Order.objects.all()
    
    # === GENERAL STATS (2 queries) ===
    stats = delivered_qs.aggregate(
        total_revenue=Sum('total_price'),
        total_orders=Count('id'),
        delivered_count=Count('id')
    )
    total_revenue = float(stats['total_revenue'] or 0)
    total_orders = stats['total_orders'] or 0
    
    status_dist = list(
        all_orders_qs.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )
    
    cancelled_count = next(
        (s['count'] for s in status_dist if s['status'] == 'cancelled'),
        0
    )
    
    # === TIME-BASED SALES (4 DB hits, aggregated at DB level) ===
    # Daily: last 30 days - single query
    thirty_days_ago = now - timedelta(days=30)
    daily_data = list(
        delivered_qs.filter(created_at__gte=thirty_days_ago)
        .annotate(period=TruncDate('created_at'))
        .values('period')
        .annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        )
        .order_by('period')
    )
    
    # Weekly: last 12 weeks - single query
    twelve_weeks_ago = now - timedelta(weeks=12)
    weekly_data = list(
        delivered_qs.filter(created_at__gte=twelve_weeks_ago)
        .annotate(period=TruncWeek('created_at'))
        .values('period')
        .annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        )
        .order_by('period')
    )
    
    # Monthly: last 12 months - single
    twelve_months_ago = now - timedelta(days=365)
    monthly_data = list(
        delivered_qs.filter(created_at__gte=twelve_months_ago)
        .annotate(period=TruncMonth('created_at'))
        .values('period')
        .annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        )
        .order_by('period')
    )
    
    # Yearly: all time - single query
    yearly_data = list(
        delivered_qs
        .annotate(period=TruncYear('created_at'))
        .values('period')
        .annotate(
            revenue=Sum('total_price'),
            orders=Count('id')
        )
        .order_by('period')
    )
    
    # === TOP MEDICINES (1 DB hit, aggregated) ===
    top_medicines = list(
        OrderItem.objects
        .filter(order__status='delivered')
        .values('medicine__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('medicine__price'))
        )
        .order_by('-total_qty')[:10]
    )
    
    # === CATEGORY REVENUE (1 DB hit) ===
    category_revenue = list(
        OrderItem.objects
        .filter(order__status='delivered')
        .values('medicine__category__name')
        .annotate(
            total_revenue=Sum(F('quantity') * F('medicine__price'))
        )
        .order_by('-total_revenue')
    )
    
    # === FORMAT OUTPUT (minimal post-processing) ===
    def _format_time_series(qs_data):
        labels = []
        revenues = []
        orders = []
        for item in qs_data:
            period = item['period']
            labels.append(period.strftime('%Y-%m-%d'))
            revenues.append(float(item['revenue'] or 0))
            orders.append(item['orders'])
        return labels, revenues, orders
    
    daily_labels, daily_revenue, daily_orders = _format_time_series(daily_data)
    weekly_labels, weekly_revenue, weekly_orders = _format_time_series(weekly_data)
    monthly_labels, monthly_revenue, monthly_orders = _format_time_series(monthly_data)
    yearly_labels, yearly_revenue, yearly_orders = _format_time_series(yearly_data)
    
    top_med_names = [m['medicine__name'] for m in top_medicines]
    top_med_qty = [int(m['total_qty']) for m in top_medicines]
    top_med_revenue = [float(m['total_revenue'] or 0) for m in top_medicines]
    
    cat_names = [c['medicine__category__name'] for c in category_revenue]
    cat_revenue = [float(c['total_revenue'] or 0) for c in category_revenue]
    
    status_labels = [s['status'].capitalize() for s in status_dist]
    status_data = [s['count'] for s in status_dist]
    
    # === FINAL OUTPUT ===
    return {
        'stats': {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'delivered_count': stats['delivered_count'] or 0,
            'cancelled_count': cancelled_count,
        },
        'daily': {
            'labels': json.dumps(daily_labels),
            'revenue': json.dumps(daily_revenue),
            'orders': json.dumps(daily_orders),
        },
        'weekly': {
            'labels': json.dumps(weekly_labels),
            'revenue': json.dumps(weekly_revenue),
            'orders': json.dumps(weekly_orders),
        },
        'monthly': {
            'labels': json.dumps(monthly_labels),
            'revenue': json.dumps(monthly_revenue),
            'orders': json.dumps(monthly_orders),
        },
        'yearly': {
            'labels': json.dumps(yearly_labels),
            'revenue': json.dumps(yearly_revenue),
            'orders': json.dumps(yearly_orders),
        },
        'top_medicines': {
            'names': json.dumps(top_med_names),
            'quantities': json.dumps(top_med_qty),
            'revenues': json.dumps(top_med_revenue),
        },
        'category_revenue': {
            'names': json.dumps(cat_names),
            'revenues': json.dumps(cat_revenue),
        },
        'status_distribution': {
            'labels': json.dumps(status_labels),
            'data': json.dumps(status_data),
        },
    }