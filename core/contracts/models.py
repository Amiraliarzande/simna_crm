# contracts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from staff.models import StaffProfile


class Contract(models.Model):
    """مدل قراردادهای کارکنان"""

    # وضعیت‌های قرارداد
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('pending_admin', 'در انتظار امضای مدیر'),
        ('pending_employee', 'در انتظار امضای کارمند'),
        ('signed', 'امضا شده'),
        ('rejected', 'رد شده'),
        ('expired', 'منقضی شده'),
    ]

    # کارمند مربوطه
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name='کارمند'
    )

    # اطلاعات قرارداد
    title = models.CharField('عنوان قرارداد', max_length=200)
    contract_number = models.CharField('شماره قرارداد', max_length=50, unique=True, blank=True, null=True)
    description = models.TextField('توضیحات', blank=True, null=True)

    # تاریخ‌ها
    start_date = models.DateField('تاریخ شروع', null=True, blank=True)
    end_date = models.DateField('تاریخ پایان', null=True, blank=True)

    # فایل‌ها
    contract_file = models.FileField(
        'فایل قرارداد',
        upload_to='contracts/files/',
        blank=True,
        null=True
    )
    signed_file = models.FileField(
        'فایل امضا شده',
        upload_to='contracts/signed/',
        blank=True,
        null=True
    )

    # امضاها
    admin_signature = models.TextField('امضای مدیر', blank=True, null=True)
    admin_signed_at = models.DateTimeField('تاریخ امضای مدیر', null=True, blank=True)
    admin_signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='signed_contracts_as_admin',
        verbose_name='امضا کننده (مدیر)'
    )

    employee_signature = models.TextField('امضای کارمند', blank=True, null=True)
    employee_signed_at = models.DateTimeField('تاریخ امضای کارمند', null=True, blank=True)
    employee_signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='signed_contracts_as_employee',
        verbose_name='امضا کننده (کارمند)'
    )

    # وضعیت
    status = models.CharField(
        'وضعیت',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    notes = models.TextField('یادداشت‌ها', blank=True, null=True)

    # تاریخ‌های سیستمی
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts',
        verbose_name='ایجاد کننده'
    )

    class Meta:
        verbose_name = 'قرارداد'
        verbose_name_plural = 'قراردادها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.employee.get_full_name()} ({self.get_status_display()})"

    @property
    def employee_name(self):
        return self.employee.get_full_name() or self.employee.username

    @property
    def is_fully_signed(self):
        return self.status == 'signed'

    @property
    def is_pending(self):
        return self.status in ['pending_admin', 'pending_employee']

    def sign_by_admin(self, user, signature_text=None):
        """امضای قرارداد توسط مدیر"""
        if self.status == 'draft' or self.status == 'pending_admin':
            self.admin_signature = signature_text or f"امضای مدیر: {user.get_full_name()}"
            self.admin_signed_at = timezone.now()
            self.admin_signed_by = user
            self.status = 'pending_employee'
            self.save()
            return True
        return False

    def sign_by_employee(self, user, signature_text=None):
        """امضای قرارداد توسط کارمند"""
        if self.status == 'pending_employee':
            self.employee_signature = signature_text or f"امضای کارمند: {user.get_full_name()}"
            self.employee_signed_at = timezone.now()
            self.employee_signed_by = user
            self.status = 'signed'
            self.save()
            return True
        return False

    def reject(self, user, reason=None):
        """رد قرارداد"""
        if user == self.admin_signed_by or user == self.created_by:
            self.status = 'rejected'
            if reason:
                self.notes = reason
            self.save()
            return True
        return False

    def send_to_employee(self, user):
        """ارسال قرارداد برای امضای کارمند"""
        if user == self.created_by or user == self.admin_signed_by:
            self.status = 'pending_admin'
            self.save()
            return True
        return False


class ContractNotification(models.Model):
    """نوتیفیکیشن‌های قرارداد"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contract_notifications'
    )
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'نوتیفیکیشن قرارداد'
        verbose_name_plural = 'نوتیفیکیشن‌های قرارداد'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.contract.title}"