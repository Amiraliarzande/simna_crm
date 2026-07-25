# tasks/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from staff.models import StaffProfile


class Task(models.Model):
    """مدل وظایف"""

    # اولویت‌ها
    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    ]

    # وضعیت‌ها
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'انجام شده'),
        ('cancelled', 'لغو شده'),
        ('deferred', 'به تعویق افتاده'),
    ]

    # اطلاعات پایه
    title = models.CharField('عنوان وظیفه', max_length=200)
    description = models.TextField('توضیحات', blank=True, null=True)

    # اولویت و وضعیت
    priority = models.CharField('اولویت', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')

    # تاریخ‌ها
    start_date = models.DateTimeField('تاریخ شروع', null=True, blank=True)
    due_date = models.DateTimeField('تاریخ سررسید', null=True, blank=True)
    completed_at = models.DateTimeField('تاریخ اتمام', null=True, blank=True)

    # ایجاد کننده
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='ایجاد کننده'
    )

    # مسئولین وظیفه (چند نفر)
    assigned_to = models.ManyToManyField(
        User,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='اختصاص به افراد'
    )

    # دپارتمان (اختصاص به دپارتمان)
    assigned_department = models.CharField(
        'اختصاص به دپارتمان',
        max_length=20,
        choices=StaffProfile.DEPARTMENT_CHOICES,
        blank=True,
        null=True
    )

    # سطح دسترسی
    VISIBILITY_CHOICES = [
        ('private', 'فقط من'),
        ('assigned', 'فقط افراد اختصاص داده شده'),
        ('department', 'دپارتمان'),
        ('public', 'همه'),
    ]
    visibility = models.CharField(
        'دسترسی',
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='assigned'
    )

    # فایل پیوست
    attachment = models.FileField('فایل پیوست', upload_to='tasks/attachments/', blank=True, null=True)

    # یادداشت‌ها
    notes = models.TextField('یادداشت‌ها', blank=True, null=True)

    # تاریخ‌های سیستمی
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'وظیفه'
        verbose_name_plural = 'وظایف'
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"

    @property
    def is_overdue(self):
        """بررسی آیا وظیفه دیر شده است"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

    @property
    def assigned_to_display(self):
        """نمایش افراد یا دپارتمان مسئول"""
        users = self.assigned_to.all()
        if users.exists():
            names = [u.get_full_name() or u.username for u in users]
            return ', '.join(names)
        if self.assigned_department:
            return dict(StaffProfile.DEPARTMENT_CHOICES).get(self.assigned_department, self.assigned_department)
        return 'تعیین نشده'

    @property
    def priority_color(self):
        """رنگ اولویت برای نمایش"""
        colors = {
            'low': 'bg-gray-100 text-gray-600',
            'medium': 'bg-blue-100 text-blue-700',
            'high': 'bg-orange-100 text-orange-700',
            'urgent': 'bg-rose-100 text-rose-700',
        }
        return colors.get(self.priority, 'bg-gray-100 text-gray-600')

    @property
    def visibility_display(self):
        return dict(self.VISIBILITY_CHOICES).get(self.visibility, self.visibility)

    def complete(self):
        """علامت‌گذاری به عنوان انجام شده"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def cancel(self):
        """لغو وظیفه"""
        self.status = 'cancelled'
        self.save()

    # tasks/models.py
    def is_visible_to(self, user):
        """بررسی اینکه آیا وظیفه برای کاربر قابل مشاهده است"""
        # ایجاد کننده همیشه می‌بیند
        if user == self.created_by:
            return True

        # اگر عمومی است
        if self.visibility == 'public':
            return True

        # اگر اختصاص داده شده به فرد
        if self.visibility == 'assigned' and self.assigned_to.filter(id=user.id).exists():
            return True

        # اگر دپارتمان
        if self.visibility == 'department' and self.assigned_department:
            profile = getattr(user, 'staff_profile', None)
            if profile and profile.department == self.assigned_department:
                return True

        return False


class TaskComment(models.Model):
    """نظرات روی وظایف"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    comment = models.TextField('متن نظر')
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'نظر وظیفه'
        verbose_name_plural = 'نظرات وظایف'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.task.title[:30]}"


class TaskNotification(models.Model):
    """نوتیفیکیشن‌های وظایف"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'نوتیفیکیشن وظیفه'
        verbose_name_plural = 'نوتیفیکیشن‌های وظایف'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.task.title[:30]}"