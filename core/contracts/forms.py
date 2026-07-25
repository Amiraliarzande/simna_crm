from django import forms
from django.contrib.auth.models import User
from .models import Contract


class ContractForm(forms.ModelForm):
    """فرم ایجاد قرارداد"""

    class Meta:
        model = Contract
        fields = [
            'employee', 'title', 'contract_number', 'description',
            'start_date', 'end_date', 'contract_file', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'عنوان قرارداد را وارد کنید...'
            }),
            'contract_number': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثال: CON-1404-001'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'توضیحات قرارداد...'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'date'
            }),
            'contract_file': forms.FileInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 2,
                'placeholder': 'یادداشت‌ها...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(is_active=True)
        self.fields['employee'].label = 'کارمند'
        self.fields['employee'].empty_label = 'انتخاب کارمند'


class ContractSignForm(forms.Form):
    """فرم امضای قرارداد"""
    signature = forms.CharField(
        label='امضای الکترونیک',
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
            'placeholder': 'امضای خود را وارد کنید...'
        }),
        required=False
    )