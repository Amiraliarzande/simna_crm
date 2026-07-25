# staff/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffCreateForm(forms.ModelForm):
    """فرم ایجاد کارمند جدید"""
    username = forms.CharField(
        label='نام کاربری',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )
    password_confirm = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
        })
    )

    class Meta:
        model = StaffProfile
        fields = [
            'phone', 'address', 'position', 'position_other', 'department', 'department_other', 'avatar'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثال: ۰۹۱۲۱۲۳۴۵۶۷'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'آدرس کامل را وارد کنید...'
            }),
            'position': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'position_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'نام سمت را وارد کنید...'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'department_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'نام دپارتمان را وارد کنید...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].label = 'سمت'
        self.fields['position_other'].label = 'نام سمت'
        self.fields['department'].label = 'دپارتمان'
        self.fields['department_other'].label = 'نام دپارتمان'
        self.fields['phone'].label = 'شماره تماس'
        self.fields['phone'].required = False
        self.fields['address'].label = 'آدرس'
        self.fields['avatar'].label = 'تصویر پروفایل'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('این نام کاربری قبلاً ثبت شده است.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.replace(' ', '').replace('-', '').replace('_', '')
            if not phone.isdigit():
                raise forms.ValidationError('شماره تماس باید فقط شامل اعداد باشد.')
            if len(phone) < 10:
                raise forms.ValidationError('شماره تماس باید حداقل ۱۰ رقم باشد.')
            if StaffProfile.objects.filter(phone=phone).exists():
                raise forms.ValidationError('این شماره تماس قبلاً ثبت شده است.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'رمز عبور و تکرار آن مطابقت ندارند.')

        position = cleaned_data.get('position')
        position_other = cleaned_data.get('position_other')
        if position == 'other' and not position_other:
            self.add_error('position_other', 'لطفاً نام سمت را وارد کنید.')

        department = cleaned_data.get('department')
        department_other = cleaned_data.get('department_other')
        if department == 'other' and not department_other:
            self.add_error('department_other', 'لطفاً نام دپارتمان را وارد کنید.')

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        profile, created = StaffProfile.objects.get_or_create(user=user)

        profile.phone = self.cleaned_data.get('phone', '') or None
        profile.address = self.cleaned_data.get('address', '')
        profile.position = self.cleaned_data.get('position', 'expert')
        profile.position_other = self.cleaned_data.get('position_other', '')
        profile.department = self.cleaned_data.get('department', 'other')
        profile.department_other = self.cleaned_data.get('department_other', '')

        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data.get('avatar')

        if commit:
            profile.save()
        return profile


class StaffEditForm(forms.ModelForm):
    """فرم ویرایش کارمند - ساده و بدون اعتبارسنجی اضافی"""

    class Meta:
        model = StaffProfile
        fields = [
            'phone', 'address', 'position', 'position_other',
            'department', 'department_other', 'avatar', 'is_active'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'مثال: ۰۹۱۲۱۲۳۴۵۶۷'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'rows': 3,
                'placeholder': 'آدرس کامل را وارد کنید...'
            }),
            'position': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'position_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'نام سمت را وارد کنید...'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'department_other': forms.TextInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition',
                'placeholder': 'نام دپارتمان را وارد کنید...'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # همه فیلدها را غیر اجباری کنید
        for field in self.fields.values():
            field.required = False

        # تنظیم لیبل‌ها
        self.fields['position'].label = 'سمت'
        self.fields['position_other'].label = 'نام سمت'
        self.fields['department'].label = 'دپارتمان'
        self.fields['department_other'].label = 'نام دپارتمان'
        self.fields['phone'].label = 'شماره تماس'
        self.fields['address'].label = 'آدرس'
        self.fields['avatar'].label = 'تصویر پروفایل'
        self.fields['is_active'].label = 'فعال'

        # اضافه کردن فیلد email
        if self.instance and self.instance.user:
            self.fields['email'] = forms.EmailField(
                label='ایمیل',
                initial=self.instance.user.email,
                required=False,
                widget=forms.EmailInput(attrs={
                    'class': 'w-full border border-gray-200 rounded-lg px-3.5 py-2.5 text-sm focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition'
                })
            )

    def clean_phone(self):
        """اعتبارسنجی شماره تماس - فقط در صورت وارد شدن"""
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = phone.replace(' ', '').replace('-', '').replace('_', '')
            if not phone.isdigit():
                raise forms.ValidationError('شماره تماس باید فقط شامل اعداد باشد.')
            if len(phone) < 10:
                raise forms.ValidationError('شماره تماس باید حداقل ۱۰ رقم باشد.')
            # فقط اگر شماره تکراری باشد و متعلق به کاربر دیگری باشد
            if StaffProfile.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('این شماره تماس قبلاً ثبت شده است.')
        # اگر خالی بود، بدون خطا برگردان
        return phone or None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean(self):
        cleaned_data = super().clean()

        position = cleaned_data.get('position')
        position_other = cleaned_data.get('position_other')
        if position == 'other' and not position_other:
            self.add_error('position_other', 'لطفاً نام سمت را وارد کنید.')

        department = cleaned_data.get('department')
        department_other = cleaned_data.get('department_other')
        if department == 'other' and not department_other:
            self.add_error('department_other', 'لطفاً نام دپارتمان را وارد کنید.')

        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)

        # اگر شماره تماس خالی بود، None بگذار
        if not profile.phone:
            profile.phone = None

        # به‌روزرسانی ایمیل کاربر
        if self.cleaned_data.get('email') and profile.user:
            profile.user.email = self.cleaned_data['email']
            profile.user.save()

        if commit:
            profile.save()
        return profile