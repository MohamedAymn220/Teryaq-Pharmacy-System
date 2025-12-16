# store/forms.py
from django import forms
from .models import Category, Medicine

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']  

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2',
                'rows': 3
            }),
        }
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'price', 'category', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2'
            }),
        }
