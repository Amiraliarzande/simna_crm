# projects/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from customers.models import Customer
from staff.models import StaffProfile


class Project(models.Model):
    """مدل پروژه‌ها"""

    # نوع پروژه
    PROJECT_TYPE_CHOICES = [
        ('internal', 'داخلی'),
        ('external', 'خارجی'),
    ]

    # وضعیت پروژه
    STATUS_CHOICES = [
        ('not_started', 'شروع نشده'),
        ('in_progress', 'در حال پیشرفت'),
        ('pending', 'در حال انتظار'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تمام شده'),
    ]

    # اطلاعات پایه
    project_number = models.CharField('شماره پروژه', max_length=50, unique=True)
    title = models.CharField('عنوان پروژه', max_length=200)
    description = models.TextField('توضیحات', blank=True, null=True)

    # نوع پروژه
    project_type = models.CharField('نوع پروژه', max_length=20, choices=PROJECT_TYPE_CHOICES, default='internal')

    # مشتری اصلی (برای پروژه‌های خارجی)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name='مشتری اصلی'
    )

    # وضعیت
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='not_started')

    # تاریخ‌ها
    start_date = models.DateField('تاریخ شروع')
    end_date = models.DateField('تاریخ پایان', null=True, blank=True)
    actual_end_date = models.DateField('تاریخ اتمام واقعی', null=True, blank=True)

    # اعضای پروژه (کارمندان)
    members = models.ManyToManyField(
        User,
        blank=True,
        related_name='projects',
        verbose_name='اعضای پروژه (کارمندان)'
    )

    # مشتریان عضو پروژه (فقط برای پروژه‌های خارجی)
    customer_members = models.ManyToManyField(
        Customer,
        blank=True,
        related_name='project_members',
        verbose_name='مشتریان عضو پروژه'
    )

    # دسترسی
    VISIBILITY_CHOICES = [
        ('private', 'خودم'),
        ('assigned', 'اعضا'),
        ('department', 'دپارتمان'),
    ]
    visibility = models.CharField(
        'دسترسی',
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='assigned'
    )

    # دپارتمان‌های دسترسی (برای حالت department)
    assigned_departments = models.CharField(
        'دپارتمان‌های دسترسی',
        max_length=200,
        blank=True,
        null=True,
        help_text='برای انتخاب چند دپارتمان، با کاما جدا کنید'
    )

    # ایجاد کننده
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_projects',
        verbose_name='ایجاد کننده'
    )

    # تاریخ‌های سیستمی
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'پروژه'
        verbose_name_plural = 'پروژه‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project_number} - {self.title}"

    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            'not_started': 'bg-gray-100 text-gray-600',
            'in_progress': 'bg-blue-100 text-blue-700',
            'pending': 'bg-yellow-100 text-yellow-700',
            'cancelled': 'bg-rose-100 text-rose-700',
            'completed': 'bg-emerald-100 text-emerald-700',
        }
        return colors.get(self.status, 'bg-gray-100 text-gray-600')

    @property
    def project_type_display(self):
        return dict(self.PROJECT_TYPE_CHOICES).get(self.project_type, self.project_type)

    @property
    def visibility_display(self):
        return dict(self.VISIBILITY_CHOICES).get(self.visibility, self.visibility)

    @property
    def customer_name(self):
        if self.customer:
            return self.customer.full_name
        return '-'

    @property
    def member_names(self):
        members_list = []
        for m in self.members.all():
            members_list.append(m.get_full_name() or m.username)
        for c in self.customer_members.all():
            members_list.append(f"{c.full_name} (مشتری)")
        return ', '.join(members_list) if members_list else '-'

    @property
    def is_overdue(self):
        """بررسی آیا پروژه دیر شده است"""
        if self.end_date and self.status not in ['completed', 'cancelled']:
            return timezone.now().date() > self.end_date
        return False

    def is_visible_to(self, user):
        """بررسی دسترسی کاربر به پروژه"""
        # ایجاد کننده همیشه می‌بیند
        if user == self.created_by:
            return True

        # اگر دسترسی خصوصی (فقط خودم)
        if self.visibility == 'private':
            return False

        # اگر دسترسی اعضا
        if self.visibility == 'assigned' and self.members.filter(id=user.id).exists():
            return True

        # اگر دسترسی دپارتمان
        if self.visibility == 'department' and self.assigned_departments:
            profile = getattr(user, 'staff_profile', None)
            if profile and profile.department:
                dept_list = self.assigned_departments.split(',')
                if profile.department in dept_list:
                    return True

        return False


class ProjectComment(models.Model):
    """نظرات پروژه"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    comment = models.TextField('متن نظر')
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'نظر پروژه'
        verbose_name_plural = 'نظرات پروژه'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.project.title[:30]}"


class ProjectFile(models.Model):
    """فایل‌های پیوست پروژه"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_files')
    file = models.FileField('فایل', upload_to='projects/files/')
    description = models.CharField('توضیحات', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('تاریخ آپلود', auto_now_add=True)

    class Meta:
        verbose_name = 'فایل پروژه'
        verbose_name_plural = 'فایل‌های پروژه'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file.name} - {self.project.title[:30]}"

