# tasks/forms.py
from django import forms
from django.contrib.auth.models import User
from staff.models import StaffProfile
from .models import Task, TaskComment


class TaskForm(forms.ModelForm):
    """فرم ایجاد و ویرایش وظیفه"""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'status',
            'start_date', 'due_date', 'assigned_to',
            'assigned_department', 'visibility', 'attachment', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'عنوان وظیفه را وارد کنید...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'توضیحات وظیفه...'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'datetime-local'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'datetime-local'
            }),
            'assigned_to': forms.SelectMultiple(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'multiple': True,
                'size': 4
            }),
            'assigned_department': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'visibility': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'attachment': forms.FileInput(attrs={
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
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].help_text = 'برای انتخاب چند نفر، کلید Ctrl را نگه دارید'
        self.fields['assigned_department'].choices = [('', 'اختصاص به دپارتمان (اختیاری)')] + list(StaffProfile.DEPARTMENT_CHOICES)
        self.fields['assigned_department'].required = False
        self.fields['assigned_to'].required = False


class TaskCommentForm(forms.ModelForm):
    """فرم نظر روی وظیفه"""

    class Meta:
        model = TaskComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 2,
                'placeholder': 'نظر خود را وارد کنید...'
            }),
        }