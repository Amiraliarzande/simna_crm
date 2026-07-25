# staff/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class StaffProfile(models.Model):
    """پروفایل کارکنان"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        verbose_name='کاربر'
    )

    # اطلاعات شخصی
    phone = models.CharField('شماره تماس', max_length=20, blank=True, null=True)  # <-- اختیاری
    avatar = models.ImageField('تصویر پروفایل', upload_to='staff/avatars/', blank=True, null=True)
    address = models.TextField('آدرس', blank=True, null=True)
    hire_date = models.DateField('تاریخ استخدام', auto_now_add=True)

    # وضعیت
    is_active = models.BooleanField('فعال', default=True)

    # سمت/نقش
    POSITION_CHOICES = [
        ('ceo', 'مدیرعامل'),
        ('manager', 'مدیر'),
        ('supervisor', 'سرپرست'),
        ('senior', 'کارشناس ارشد'),
        ('expert', 'کارشناس'),
        ('junior', 'کارشناس تازه‌کار'),
        ('intern', 'کارآموز'),
        ('other', 'سایر'),
    ]
    position = models.CharField(
        'سمت',
        max_length=20,
        choices=POSITION_CHOICES,
        default='expert'
    )
    position_other = models.CharField('سایر سمت‌ها', max_length=100, blank=True, null=True)

    # دپارتمان
    DEPARTMENT_CHOICES = [
        ('management', 'مدیریت'),
        ('sales', 'فروش'),
        ('marketing', 'بازاریابی'),
        ('support', 'پشتیبانی'),
        ('warehouse', 'انبارداری'),
        ('accounting', 'حسابداری'),
        ('it', 'فناوری اطلاعات'),
        ('hr', 'منابع انسانی'),
        ('other', 'سایر'),
    ]
    department = models.CharField(
        'دپارتمان',
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        default='other'
    )
    department_other = models.CharField('سایر دپارتمان‌ها', max_length=100, blank=True, null=True)

    # دسترسی‌ها
    can_manage_staff = models.BooleanField('مدیریت کارکنان', default=False)
    can_manage_customers = models.BooleanField('مدیریت مشتریان', default=False)
    can_manage_sales = models.BooleanField('مدیریت فروش', default=False)
    can_manage_warehouse = models.BooleanField('مدیریت انبار', default=False)
    can_manage_accounting = models.BooleanField('مدیریت حسابداری', default=False)
    can_manage_support = models.BooleanField('مدیریت پشتیبانی', default=False)
    can_view_reports = models.BooleanField('مشاهده گزارشات', default=False)

    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_staff',
        verbose_name='ثبت کننده'
    )

    class Meta:
        verbose_name = 'کارمند'
        verbose_name_plural = 'کارکنان'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def position_display(self):
        if self.position == 'other' and self.position_other:
            return self.position_other
        return dict(self.POSITION_CHOICES).get(self.position, '-')

    @property
    def department_display(self):
        if self.department == 'other' and self.department_other:
            return self.department_other
        return dict(self.DEPARTMENT_CHOICES).get(self.department, '-')

    def save(self, *args, **kwargs):
        # تنظیم خودکار دسترسی‌ها بر اساس دپارتمان
        if self.department == 'management':
            self.can_manage_staff = True
            self.can_manage_customers = True
            self.can_manage_sales = True
            self.can_manage_warehouse = True
            self.can_manage_accounting = True
            self.can_manage_support = True
            self.can_view_reports = True
        elif self.department == 'sales':
            self.can_manage_customers = True
            self.can_manage_sales = True
            self.can_view_reports = True
        elif self.department == 'support':
            self.can_manage_support = True
            self.can_manage_customers = True
        elif self.department == 'warehouse':
            self.can_manage_warehouse = True
        elif self.department == 'accounting':
            self.can_manage_accounting = True
            self.can_view_reports = True
        elif self.department == 'marketing':
            self.can_manage_customers = True
            self.can_view_reports = True
        elif self.department == 'it':
            self.can_view_reports = True

        super().save(*args, **kwargs)

    def has_permission(self, permission):
        permissions = {
            'manage_staff': self.can_manage_staff,
            'manage_customers': self.can_manage_customers,
            'manage_sales': self.can_manage_sales,
            'manage_warehouse': self.can_manage_warehouse,
            'manage_accounting': self.can_manage_accounting,
            'manage_support': self.can_manage_support,
            'view_reports': self.can_view_reports,
        }
        return permissions.get(permission, False)


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created:
        StaffProfile.objects.create(user=instance)