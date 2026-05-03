# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Category, Medicine

egyptian_phone_regex = RegexValidator(
    regex=r'^01[0125][0-9]{8}$',
    message="Phone number must be 11 digits and start with 010, 011, 012, or 015."
)


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
        max_length=11,
        required=True,
        validators=[egyptian_phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Egyptian Phone (e.g., 01012345678)',
            'pattern': r'^01[0125][0-9]{8}$',
            'maxlength': '11',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '').slice(0, 11);",
            'oninvalid': "this.setCustomValidity('Please enter a valid Egyptian phone number (e.g., 010...)')"
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

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            if not re.match(r'^01[0125][0-9]{8}$', phone):
                raise forms.ValidationError(
                    "Phone number must be 11 digits and start with 010, 011, 012, or 015."
                )
        return phone


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