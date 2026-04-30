# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Medicine


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with additional fields for pharmacy registration."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    pharmacy_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pharmacy Name'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'pharmacy_name', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the widget classes for better styling
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3',
                'rows': 3
            }),
        }

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full border-2 border-gray-200 rounded-lg shadow-sm focus:ring-green-500 focus:border-green-500 p-3'
            }),
        }