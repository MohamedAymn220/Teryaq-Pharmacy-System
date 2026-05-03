from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from urllib.parse import quote_plus


def build_avatar_url(name):
    """Generate a neutral CDN avatar based on a user's display name."""
    safe_name = quote_plus(name or 'Teryaq User')
    return (
        'https://ui-avatars.com/api/'
        f'?name={safe_name}&background=E2E8F0&color=475569&size=256&rounded=true&bold=true'
    )


class Profile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    profile_picture = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    @property
    def display_name(self):
        return self.user.get_full_name().strip() or self.user.username

    @property
    def avatar_url(self):
        return self.profile_picture or build_avatar_url(self.display_name)

    def sync_role_from_user(self):
        self.role = self.ROLE_ADMIN if (self.user.is_staff or self.user.is_superuser) else self.ROLE_USER

    def save(self, *args, **kwargs):
        self.sync_role_from_user()
        if not self.profile_picture:
            self.profile_picture = build_avatar_url(self.display_name)
        super().save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    def __str__(self): 
        return self.name
    

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='medicines')
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total(self):
        return sum(item.total_price() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.medicine.price

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"
    
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


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


@receiver(post_save, sender=User)
def create_or_sync_user_profile(sender, instance, created, **kwargs):
    profile, profile_created = Profile.objects.get_or_create(user=instance)

    needs_update = False
    synced_role = Profile.ROLE_ADMIN if (instance.is_staff or instance.is_superuser) else Profile.ROLE_USER
    if profile.role != synced_role:
        profile.role = synced_role
        needs_update = True

    if not profile.profile_picture:
        profile.profile_picture = build_avatar_url(profile.display_name)
        needs_update = True

    if created or profile_created or needs_update:
        profile.save()
