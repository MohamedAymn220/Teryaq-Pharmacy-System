"""
store/dashboard_service.py
"""
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta

from store.models import Order, OrderItem


def get_income_dashboard_data():
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    twelve_weeks_ago = now - timedelta(weeks=12)
    one_year_ago = now - timedelta(days=365)

    delivered_qs = Order.objects.filter(status='delivered')
    all_orders_qs = Order.objects.all()

    stats = delivered_qs.aggregate(
        total_revenue=Sum('total_price'),
        delivered_count=Count('id'),
    )

    total_revenue = float(stats['total_revenue'] or 0)
    delivered_count = stats['delivered_count'] or 0
    total_orders = all_orders_qs.count()
    cancelled_count = all_orders_qs.filter(status='cancelled').count()

    def time_series(qs, trunc_fn, since):
        return list(
            qs.filter(created_at__gte=since)
            .annotate(period=trunc_fn('created_at'))
            .values('period')
            .annotate(revenue=Sum('total_price'), orders=Count('id'))
            .order_by('period')
        )

    monthly_data = list(
        Order.objects.all()
        .annotate(period=TruncMonth('created_at'))
        .values('period')
        .annotate(revenue=Sum('total_price'), orders=Count('id'))
        .order_by('period')
    )

    def fmt(data):
        labels = []
        revenues = []
        orders = []
        for row in data:
            if hasattr(row['period'], 'strftime'):
                labels.append(row['period'].strftime('%Y-%m-%d'))
            else:
                labels.append(str(row['period']))
            revenues.append(float(row['revenue'] or 0))
            orders.append(int(row['orders'] or 0))
        return {'labels': labels, 'revenue': revenues, 'orders': orders}

    daily = fmt(time_series(delivered_qs, TruncDate, thirty_days_ago))
    weekly = fmt(time_series(delivered_qs, TruncWeek, twelve_weeks_ago))
    monthly = fmt(monthly_data)

    yearly_data = list(
        delivered_qs
        .annotate(period=TruncYear('created_at'))
        .values('period')
        .annotate(revenue=Sum('total_price'), orders=Count('id'))
        .order_by('period')
    )
    yearly = fmt(yearly_data)

    top_meds_raw = list(
        OrderItem.objects
        .filter(order__status='delivered')
        .values('medicine__name')
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('medicine__price'))
        )
        .order_by('-total_qty')[:5]
    )

    top_meds = [
        {
            'medicine__name': m['medicine__name'],
            'total_qty': m['total_qty'],
            'total_revenue': float(m['total_revenue'] or 0)
        }
        for m in top_meds_raw
    ]

    cat_rev_raw = list(
        OrderItem.objects
        .filter(order__status='delivered')
        .values('medicine__category__name')
        .annotate(total_revenue=Sum(F('quantity') * F('medicine__price')))
        .order_by('-total_revenue')
    )

    cat_rev = [
        {
            'medicine__category__name': c['medicine__category__name'],
            'total_revenue': float(c['total_revenue'] or 0)
        }
        for c in cat_rev_raw
    ]

    status_dist = list(
        all_orders_qs.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'delivered_count': delivered_count,
        'cancelled_count': cancelled_count,
        'has_delivered_orders': delivered_count > 0,

        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'yearly': yearly,

        'top_meds': top_meds,
        'cat_rev': cat_rev,
        'status_dist': status_dist,
    }