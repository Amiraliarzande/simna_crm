# projects/forms.py
from django import forms
from django.contrib.auth.models import User
from customers.models import Customer
from staff.models import StaffProfile
from .models import Project, ProjectComment, ProjectFile


class ProjectForm(forms.ModelForm):
    """فرم ایجاد پروژه"""

    # فیلد برای انتخاب دپارتمان‌ها (چند انتخابی)
    departments = forms.MultipleChoiceField(
        label='دپارتمان‌های دسترسی',
        choices=StaffProfile.DEPARTMENT_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
            'size': 4
        })
    )

    def __init__(self, *args, **kwargs):
        project_type = kwargs.pop('project_type', None)
        super().__init__(*args, **kwargs)

        # مشتری اصلی
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['customer'].empty_label = 'انتخاب مشتری اصلی (برای پروژه‌های خارجی)'

        # اعضای پروژه (کارمندان)
        self.fields['members'].queryset = User.objects.filter(is_active=True)
        self.fields['members'].help_text = 'برای انتخاب چند نفر، کلید Ctrl را نگه دارید'
        self.fields['members'].required = False

        # مشتریان عضو پروژه
        self.fields['customer_members'].queryset = Customer.objects.filter(is_active=True)
        self.fields['customer_members'].help_text = 'برای انتخاب چند مشتری، کلید Ctrl را نگه دارید'
        self.fields['customer_members'].required = False
        self.fields['customer_members'].label = 'مشتریان عضو پروژه'

        # تغییر گزینه‌های دسترسی
        self.fields['visibility'].choices = [
            ('private', 'خودم'),
            ('department', 'دپارتمان'),
            ('assigned', 'اعضا'),
        ]

        # اگر نوع پروژه مشخص است، فیلدهای مربوطه را تنظیم کن
        if project_type == 'internal':
            self.fields['customer'].required = False
            self.fields['customer'].widget = forms.HiddenInput()
            self.fields['customer_members'].widget = forms.HiddenInput()
            self.fields['visibility'].initial = 'assigned'
        elif project_type == 'external':
            self.fields['customer'].required = True
            self.fields['customer_members'].required = False

        # تنظیم initial برای departments
        if self.instance and self.instance.pk and self.instance.assigned_departments:
            self.fields['departments'].initial = self.instance.assigned_departments.split(',')

    class Meta:
        model = Project
        fields = [
            'project_number', 'title', 'description',
            'customer', 'status', 'start_date', 'end_date',
            'members', 'customer_members', 'visibility'
        ]
        widgets = {
            'project_number': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثال: PRJ-1404-001'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'عنوان پروژه را وارد کنید...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'توضیحات پروژه...'
            }),
            'customer': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'type': 'date'
            }),
            'members': forms.SelectMultiple(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'multiple': True,
                'size': 4
            }),
            'customer_members': forms.SelectMultiple(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'multiple': True,
                'size': 4
            }),
            'visibility': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
        }

    def save(self, commit=True):
        project = super().save(commit=False)

        # ذخیره دپارتمان‌های انتخاب شده
        departments = self.cleaned_data.get('departments', [])
        project.assigned_departments = ','.join(departments) if departments else None

        if commit:
            project.save()
            self.save_m2m()  # ذخیره members و customer_members
        return project


class ProjectCommentForm(forms.ModelForm):
    """فرم نظر پروژه"""

    class Meta:
        model = ProjectComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 2,
                'placeholder': 'نظر خود را وارد کنید...'
            }),
        }


class ProjectFileForm(forms.ModelForm):
    """فرم آپلود فایل پروژه"""

    class Meta:
        model = ProjectFile
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'توضیحات فایل...'
            }),
        }