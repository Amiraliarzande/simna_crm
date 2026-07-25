# customers/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class CustomerGroup(models.Model):
    """گروه‌های مشتریان (قابل تعریف توسط کاربر)"""
    name = models.CharField('نام گروه', max_length=100)
    description = models.TextField('توضیحات', blank=True, null=True)

    # پاداش و تخفیف
    discount_percent = models.DecimalField('درصد تخفیف', max_digits=5, decimal_places=2, default=0)
    bonus_points = models.IntegerField('امتیاز پاداش', default=0)
    bonus_description = models.TextField('توضیحات پاداش', blank=True, null=True)

    # معیارهای عضویت
    min_purchase = models.DecimalField('حداقل خرید (تومان)', max_digits=15, decimal_places=0, default=0)
    min_visits = models.IntegerField('حداقل تعداد مراجعه', default=0)

    # دپارتمان
    department = models.CharField('دپارتمان', max_length=100, blank=True, null=True)

    # وضعیت
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='ایجاد کننده',
        related_name='created_groups'
    )

    class Meta:
        verbose_name = 'گروه مشتریان'
        verbose_name_plural = 'گروه‌های مشتریان'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """تعداد اعضای گروه"""
        return self.customers.count()


class Customer(models.Model):
    """مدل مشتریان"""

    # اطلاعات شخصی
    first_name = models.CharField('نام', max_length=50)
    last_name = models.CharField('نام خانوادگی', max_length=50)
    company = models.CharField('شرکت', max_length=100, blank=True, null=True)
    email = models.EmailField('ایمیل', blank=True, null=True)
    phone = models.CharField('تلفن', max_length=20, unique=True)
    address = models.TextField('آدرس', blank=True, null=True)

    # اطلاعات مالی
    credit_limit = models.DecimalField('سقف اعتبار', max_digits=15, decimal_places=0, default=0)
    total_purchases = models.DecimalField('کل خرید', max_digits=15, decimal_places=0, default=0)
    visit_count = models.IntegerField('تعداد مراجعه', default=0)
    last_visit = models.DateTimeField('آخرین مراجعه', null=True, blank=True)

    # وضعیت اصلی
    is_active = models.BooleanField('فعال', default=True)
    customer_type = models.CharField(
        'نوع مشتری',
        max_length=20,
        choices=[
            ('regular', 'عادی'),
            ('gold', 'طلایی'),
            ('platinum', 'پلاتینیوم'),
            ('vip', 'VIP'),
        ],
        default='regular'
    )

    # ============ مشتری بالقوه ============
    is_potential = models.BooleanField('مشتری بالقوه', default=False)

    POTENTIAL_STATUS_CHOICES = [
        ('new_lead', 'سرنخ جدید'),
        ('initial_intro', 'معرفی اولیه'),
        ('needs_assessment', 'نیاز سنجی'),
        ('proposal_sent', 'ارسال پروپزال'),
        ('follow_up', 'پیگیری'),
        ('clarification', 'رفع ابهامات'),
        ('sale', 'فروش'),
        ('archived', 'بایگانی'),
        ('other', 'سایر'),
    ]
    potential_status = models.CharField(
        'وضعیت بالقوه',
        max_length=20,
        choices=POTENTIAL_STATUS_CHOICES,
        blank=True,
        null=True,
        default='new_lead'
    )
    potential_status_other = models.CharField(
        'سایر وضعیت‌های بالقوه',
        max_length=100,
        blank=True,
        null=True
    )

    # ============ منبع آشنایی ============
    SOURCE_CHOICES = [
        ('google', 'گوگل'),
        ('telemarketing', 'بازاریابی تلفنی'),
        ('exhibition', 'نمایشگاه'),
        ('referral', 'معرفی'),
        ('social_media', 'شبکه‌های اجتماعی'),
        ('website', 'وب‌سایت'),
        ('other', 'سایر'),
    ]
    source = models.CharField(
        'منبع آشنایی',
        max_length=20,
        choices=SOURCE_CHOICES,
        blank=True,
        null=True
    )
    source_other = models.CharField('سایر منابع', max_length=100, blank=True, null=True)

    # ============ گروه و دپارتمان ============
    group = models.ForeignKey(
        CustomerGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='گروه مشتریان',
        related_name='customers'
    )
    department = models.CharField('دپارتمان', max_length=100, blank=True, null=True)

    # ============ بایگانی ============
    is_archived = models.BooleanField('بایگانی شده', default=False)
    archived_at = models.DateTimeField('تاریخ بایگانی', null=True, blank=True)
    archived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='بایگانی کننده',
        related_name='archived_customers'
    )
    archive_reason = models.TextField('دلیل بایگانی', blank=True, null=True)

    # ============ کارشناس مسئول ============
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='کارشناس مسئول',
        related_name='customers'
    )

    # ============ تاریخ‌ها ============
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)
    last_check_date = models.DateTimeField('آخرین بررسی', null=True, blank=True)

    class Meta:
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتریان'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    # ============ پراپرتی‌ها ============
    @property
    def full_name(self):
        """نام کامل مشتری"""
        return f"{self.first_name} {self.last_name}"

    @property
    def source_display(self):
        """نمایش منبع آشنایی"""
        if self.source == 'other' and self.source_other:
            return self.source_other
        return dict(self.SOURCE_CHOICES).get(self.source, '-')

    @property
    def potential_status_display(self):
        """نمایش وضعیت بالقوه"""
        if self.potential_status == 'other' and self.potential_status_other:
            return self.potential_status_other
        return dict(self.POTENTIAL_STATUS_CHOICES).get(self.potential_status, '-')

    @property
    def group_name(self):
        """نام گروه مشتری"""
        return self.group.name if self.group else '-'

    @property
    def is_in_club(self):
        """آیا مشتری در باشگاه عضو است؟"""
        return self.group is not None

    # ============ متدها ============
    def check_and_deactivate(self):
        """بررسی و غیرفعال کردن خودکار بعد از 2 ماه عدم بررسی"""
        if self.is_active and self.last_check_date:
            two_months_ago = timezone.now() - timedelta(days=60)
            if self.last_check_date < two_months_ago:
                self.is_active = False
                self.save()
                return True
        return False

    def archive(self, user, reason=None):
        """بایگانی کردن مشتری"""
        self.is_archived = True
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = user
        self.archive_reason = reason
        self.save()

    def unarchive(self):
        """بازگرداندن از بایگانی"""
        self.is_archived = False
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.archive_reason = None
        self.save()

    def add_visit(self):
        """افزایش تعداد مراجعه"""
        self.visit_count += 1
        self.last_visit = timezone.now()
        self.save()

    def add_purchase(self, amount):
        """افزایش کل خرید"""
        self.total_purchases += amount
        self.save()

    def can_join_group(self, group):
        """بررسی آیا مشتری می‌تواند به این گروه بپیوندد؟"""
        if not group.is_active:
            return False, 'گروه غیرفعال است'
        if self.total_purchases < group.min_purchase:
            return False, f'حداقل خرید مورد نیاز: {group.min_purchase:,} تومان'
        if self.visit_count < group.min_visits:
            return False, f'حداقل مراجعه مورد نیاز: {group.min_visits} بار'
        return True, 'مشتری واجد شرایط است'


class CustomerNote(models.Model):
    """یادداشت‌های مشتری"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='مشتری'
    )
    note = models.TextField('متن یادداشت')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='ایجاد کننده'
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ ویرایش', auto_now=True)
    is_edited = models.BooleanField('ویرایش شده', default=False)
    is_pinned = models.BooleanField('پین شده', default=False)

    class Meta:
        verbose_name = 'یادداشت'
        verbose_name_plural = 'یادداشت‌ها'
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"یادداشت {self.customer.full_name} - {self.created_at.strftime('%Y/%m/%d %H:%M')}"