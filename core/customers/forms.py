from django import forms
from .models import Customer, CustomerNote, CustomerGroup
from django.contrib.auth.models import User


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'company', 'email', 'phone',
            'address', 'credit_limit', 'customer_type',
            'is_active', 'is_potential', 'potential_status', 'potential_status_other',
            'source', 'source_other', 'owner', 'group', 'department'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'company': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
            'is_potential': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
            'potential_status': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'potential_status_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'وضعیت دیگر را وارد کنید...'
            }),
            'source': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'source_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'منبع را وارد کنید...'
            }),
            'group': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'department': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثلاً فروش، بازاریابی، پشتیبانی...'
            }),
            'owner': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(is_active=True)
        self.fields['owner'].empty_label = 'انتخاب کارشناس'
        self.fields['potential_status'].empty_label = 'انتخاب وضعیت'
        self.fields['group'].empty_label = 'بدون گروه'


class CustomerNoteForm(forms.ModelForm):
    class Meta:
        model = CustomerNote
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 4,
                'placeholder': 'متن یادداشت را وارد کنید...'
            }),
        }


class CustomerGroupForm(forms.ModelForm):
    class Meta:
        model = CustomerGroup
        fields = ['name', 'description', 'discount_percent', 'bonus_points',
                  'bonus_description', 'min_purchase', 'min_visits', 'department', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'bonus_points': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'min': '0'
            }),
            'bonus_description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 2,
                'placeholder': 'توضیحات پاداش و تخفیف...'
            }),
            'min_purchase': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'min': '0'
            }),
            'min_visits': forms.NumberInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'min': '0'
            }),
            'department': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثلاً فروش، بازاریابی، پشتیبانی...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
        }