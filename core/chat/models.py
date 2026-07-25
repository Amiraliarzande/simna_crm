# chat/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from staff.models import StaffProfile


class ChatRoom(models.Model):
    """اتاق‌های چت (فردی یا گروهی)"""
    ROOM_TYPES = [
        ('direct', 'فردی'),
        ('group', 'گروهی'),
        ('department', 'دپارتمانی'),
    ]

    room_type = models.CharField('نوع اتاق', max_length=20, choices=ROOM_TYPES, default='direct')
    name = models.CharField('نام اتاق', max_length=100, blank=True, null=True)
    department = models.CharField('دپارتمان', max_length=50, blank=True, null=True)
    participants = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        verbose_name='شرکت‌کنندگان'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rooms',
        verbose_name='ایجاد کننده'
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین فعالیت', auto_now=True)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'اتاق چت'
        verbose_name_plural = 'اتاق‌های چت'
        ordering = ['-updated_at']

    def __str__(self):
        if self.room_type == 'direct':
            users = self.participants.all()
            if users.count() == 2:
                return f"چت {users.first().get_full_name()} و {users.last().get_full_name()}"
            return f"چت گروهی {self.id}"
        return self.name or f"اتاق {self.id}"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    @property
    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class ChatMessage(models.Model):
    """پیام‌های چت"""
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='اتاق چت'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='فرستنده'
    )
    message = models.TextField('متن پیام')
    file = models.FileField('فایل پیوست', upload_to='chat/files/', blank=True, null=True)
    is_read = models.BooleanField('خوانده شده', default=False)
    read_at = models.DateTimeField('زمان خوانده شدن', null=True, blank=True)
    created_at = models.DateTimeField('زمان ارسال', auto_now_add=True)
    edited_at = models.DateTimeField('زمان ویرایش', null=True, blank=True)
    is_edited = models.BooleanField('ویرایش شده', default=False)
    is_deleted = models.BooleanField('حذف شده', default=False)

    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.message[:30]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class SavedMessage(models.Model):
    """پیام‌های ذخیره شده توسط کاربران"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_messages',
        verbose_name='کاربر'
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='saved_by',
        verbose_name='پیام'
    )
    saved_at = models.DateTimeField('زمان ذخیره', auto_now_add=True)
    note = models.TextField('یادداشت', blank=True, null=True)

    class Meta:
        verbose_name = 'پیام ذخیره شده'
        verbose_name_plural = 'پیام‌های ذخیره شده'
        ordering = ['-saved_at']
        unique_together = ['user', 'message']

    def __str__(self):
        return f"{self.user.username} - {self.message.message[:30]}"


class PinnedChat(models.Model):
    """چت‌های پین شده توسط کاربران"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pinned_chats',
        verbose_name='کاربر'
    )
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='pinned_by',
        verbose_name='اتاق چت'
    )
    pinned_at = models.DateTimeField('زمان پین', auto_now_add=True)

    class Meta:
        verbose_name = 'چت پین شده'
        verbose_name_plural = 'چت‌های پین شده'
        ordering = ['-pinned_at']
        unique_together = ['user', 'room']

    def __str__(self):
        return f"{self.user.username} - {self.room}"


class ChatNotification(models.Model):
    """نوتیفیکیشن‌های چت"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_notifications'
    )
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    is_seen = models.BooleanField('دیده شده', default=False)
    created_at = models.DateTimeField('زمان ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'نوتیفیکیشن چت'
        verbose_name_plural = 'نوتیفیکیشن‌های چت'
        ordering = ['-created_at']


# ============================================
# مدل یادداشت‌ها
# ============================================

class Note(models.Model):
    """یادداشت‌های کاربران"""
    COLOR_CHOICES = [
        ('white', 'سفید'),
        ('yellow', 'زرد'),
        ('blue', 'آبی'),
        ('green', 'سبز'),
        ('pink', 'صورتی'),
        ('purple', 'بنفش'),
        ('red', 'قرمز'),
    ]
    color = models.CharField('رنگ', max_length=20, choices=COLOR_CHOICES, default='white')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_notes',  # <-- این را تغییر دهید
        verbose_name='کاربر'
    )
    title = models.CharField('عنوان', max_length=200)
    content = models.TextField('متن یادداشت')
    color = models.CharField('رنگ', max_length=20, choices=COLOR_CHOICES, default='white')
    is_pinned = models.BooleanField('پین شده', default=False)
    is_archived = models.BooleanField('بایگانی شده', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'یادداشت'
        verbose_name_plural = 'یادداشت‌ها'
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title[:30]}"

    @property
    def preview(self):
        """پیش‌نمایش متن یادداشت"""
        return self.content[:100] + ('...' if len(self.content) > 100 else '')

    @property
    def preview(self):
        """پیش‌نمایش متن یادداشت"""
        return self.content[:100] + ('...' if len(self.content) > 100 else '')



class CalendarEvent(models.Model):
    """رویدادهای تقویم"""
    COLOR_CHOICES = [
        ('blue', 'آبی'),
        ('green', 'سبز'),
        ('red', 'قرمز'),
        ('yellow', 'زرد'),
        ('purple', 'بنفش'),
        ('pink', 'صورتی'),
        ('orange', 'نارنجی'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'فوری'),
        ('urgent', 'ضروری'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name='کاربر'
    )
    title = models.CharField('عنوان', max_length=200)
    description = models.TextField('توضیحات', blank=True, null=True)
    date = models.DateField('تاریخ')
    time = models.TimeField('ساعت', null=True, blank=True)
    color = models.CharField('رنگ', max_length=20, choices=COLOR_CHOICES, default='blue')
    priority = models.CharField('اولویت', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_important = models.BooleanField('مهم', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین ویرایش', auto_now=True)

    class Meta:
        verbose_name = 'رویداد تقویم'
        verbose_name_plural = 'رویدادهای تقویم'
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} - {self.date}"

    @property
    def priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'متوسط')

    @property
    def priority_color(self):
        colors = {
            'low': 'bg-gray-100 text-gray-600',
            'medium': 'bg-blue-100 text-blue-700',
            'high': 'bg-orange-100 text-orange-700',
            'urgent': 'bg-rose-100 text-rose-700',
        }
        return colors.get(self.priority, 'bg-blue-100 text-blue-700')

    @property
    def priority_icon(self):
        icons = {
            'low': '⬇️',
            'medium': '➡️',
            'high': '⬆️',
            'urgent': '🔴',
        }
        return icons.get(self.priority, '➡️')