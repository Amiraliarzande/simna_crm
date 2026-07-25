# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from staff.models import StaffProfile
from .models import ChatRoom, ChatMessage, ChatNotification, SavedMessage, PinnedChat, Note
from .forms import ChatMessageForm, ChatRoomForm, NoteForm


@login_required
def chat_list(request):
    """لیست چت‌های کاربر"""
    user = request.user
    rooms = ChatRoom.objects.filter(
        participants=user,
        is_active=True
    ).order_by('-updated_at')

    # دریافت چت‌های پین شده
    pinned_room_ids = PinnedChat.objects.filter(user=user).values_list('room_id', flat=True)
    pinned_rooms = rooms.filter(id__in=pinned_room_ids)
    other_rooms = rooms.exclude(id__in=pinned_room_ids)

    # دریافت آخرین پیام و تعداد پیام‌های خوانده نشده هر اتاق
    room_list = []

    # چت‌های پین شده
    for room in pinned_rooms:
        last_msg = room.messages.order_by('-created_at').first()
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()

        room_list.append({
            'id': room.id,
            'room': room,
            'last_msg': last_msg,
            'unread_count': unread_count,
            'is_pinned': True,
        })

    # چت‌های دیگر
    for room in other_rooms:
        last_msg = room.messages.order_by('-created_at').first()
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()

        room_list.append({
            'id': room.id,
            'room': room,
            'last_msg': last_msg,
            'unread_count': unread_count,
            'is_pinned': False,
        })

    context = {
        'room_list': room_list,
        'has_pinned': pinned_rooms.exists(),
    }
    return render(request, 'chat/chat_list.html', context)


@login_required
def chat_room(request, room_id):
    """نمایش یک اتاق چت"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id, participants=user)

    # علامت‌گذاری پیام‌ها به عنوان خوانده شده
    unread_messages = room.messages.filter(is_read=False).exclude(sender=user)
    for msg in unread_messages:
        msg.mark_as_read()

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = room
            message.sender = user
            message.save()

            # به‌روزرسانی زمان آخرین فعالیت
            room.updated_at = timezone.now()
            room.save()

            # ایجاد نوتیفیکیشن برای سایر شرکت‌کنندگان
            for participant in room.participants.exclude(id=user.id):
                ChatNotification.objects.create(
                    user=participant,
                    message=message,
                )

            # اگر درخواست Ajax باشد
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': message.message,
                    'sender': user.get_full_name() or user.username,
                    'time': message.created_at.strftime('%H:%M'),
                    'message_id': message.id,
                })

            return redirect('chat:chat-room', room_id=room.id)
    else:
        form = ChatMessageForm()

    # دریافت لیست پیام‌های ذخیره شده توسط کاربر
    saved_message_ids = SavedMessage.objects.filter(user=user).values_list('message_id', flat=True)

    # دریافت وضعیت پین شدن چت
    is_pinned = PinnedChat.objects.filter(user=user, room=room).exists()

    context = {
        'room': room,
        'messages': room.messages.filter(is_deleted=False),
        'form': form,
        'saved_message_ids': list(saved_message_ids),
        'is_pinned': is_pinned,
    }
    return render(request, 'chat/chat_room.html', context)


@login_required
def chat_start(request):
    """شروع چت جدید"""
    user = request.user

    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            room_type = form.cleaned_data.get('room_type')

            if room_type == 'direct':
                # چت فردی
                target_user_id = request.POST.get('target_user')
                if target_user_id:
                    target_user = get_object_or_404(User, id=target_user_id)
                    # بررسی چت موجود
                    existing_room = ChatRoom.objects.filter(
                        room_type='direct',
                        participants=user
                    ).filter(participants=target_user).first()

                    if existing_room:
                        return redirect('chat:chat-room', room_id=existing_room.id)

                    room = ChatRoom.objects.create(
                        room_type='direct',
                        created_by=user
                    )
                    room.participants.add(user, target_user)
                    return redirect('chat:chat-room', room_id=room.id)

            elif room_type == 'department':
                # چت دپارتمانی
                department = form.cleaned_data.get('department')
                if department:
                    # پیدا کردن کاربران همان دپارتمان
                    staff_users = StaffProfile.objects.filter(department=department)
                    users_in_dept = [s.user for s in staff_users if s.user.is_active]

                    if users_in_dept:
                        # بررسی چت دپارتمانی موجود
                        existing_room = ChatRoom.objects.filter(
                            room_type='department',
                            department=department
                        ).first()

                        if existing_room:
                            return redirect('chat:chat-room', room_id=existing_room.id)

                        room = ChatRoom.objects.create(
                            room_type='department',
                            name=f'دپارتمان {department}',
                            department=department,
                            created_by=user
                        )
                        for u in users_in_dept:
                            room.participants.add(u)
                        return redirect('chat:chat-room', room_id=room.id)
                    else:
                        messages.error(request, 'هیچ کاربری در این دپارتمان وجود ندارد.')

            elif room_type == 'group':
                # چت گروهی
                name = form.cleaned_data.get('name')
                participants_ids = request.POST.getlist('participants')
                if name and participants_ids:
                    room = ChatRoom.objects.create(
                        room_type='group',
                        name=name,
                        created_by=user
                    )
                    room.participants.add(user)
                    for pid in participants_ids:
                        try:
                            p_user = User.objects.get(id=pid)
                            room.participants.add(p_user)
                        except User.DoesNotExist:
                            pass
                    return redirect('chat:chat-room', room_id=room.id)
                else:
                    messages.error(request, 'لطفاً نام گروه و شرکت‌کنندگان را انتخاب کنید.')
    else:
        form = ChatRoomForm()

    # لیست کاربران برای چت فردی
    users = User.objects.filter(is_active=True).exclude(id=user.id)

    # لیست دپارتمان‌ها
    departments = StaffProfile.DEPARTMENT_CHOICES

    context = {
        'form': form,
        'users': users,
        'departments': departments,
    }
    return render(request, 'chat/chat_start.html', context)


@login_required
def chat_save_message(request, message_id):
    """ذخیره پیام"""
    message = get_object_or_404(ChatMessage, id=message_id)
    user = request.user

    # بررسی اینکه آیا کاربر در این چت شرکت دارد
    if not message.room.participants.filter(id=user.id).exists():
        messages.error(request, 'شما دسترسی به این پیام را ندارید.')
        return redirect('chat:chat-list')

    # ذخیره یا حذف از ذخیره‌ها
    saved, created = SavedMessage.objects.get_or_create(
        user=user,
        message=message
    )

    if created:
        messages.success(request, 'پیام با موفقیت ذخیره شد.')
    else:
        saved.delete()
        messages.success(request, 'پیام از لیست ذخیره‌ها حذف شد.')

    return redirect('chat:chat-room', room_id=message.room.id)


@login_required
def chat_toggle_pin(request, room_id):
    """پین/آنپین کردن چت"""
    room = get_object_or_404(ChatRoom, id=room_id)
    user = request.user

    # بررسی اینکه آیا کاربر در این چت شرکت دارد
    if not room.participants.filter(id=user.id).exists():
        messages.error(request, 'شما دسترسی به این چت را ندارید.')
        return redirect('chat:chat-list')

    # پین یا آنپین
    pinned, created = PinnedChat.objects.get_or_create(
        user=user,
        room=room
    )

    if created:
        messages.success(request, 'چت با موفقیت پین شد.')
    else:
        pinned.delete()
        messages.success(request, 'چت از لیست پین‌ها حذف شد.')

    return redirect('chat:chat-list')


@login_required
def chat_saved_messages(request):
    """نمایش پیام‌های ذخیره شده"""
    user = request.user
    saved_messages = SavedMessage.objects.filter(user=user).select_related('message', 'message__room')

    context = {
        'saved_messages': saved_messages,
    }
    return render(request, 'chat/chat_saved_messages.html', context)


@login_required
def chat_delete_message(request, message_id):
    """حذف پیام"""
    message = get_object_or_404(ChatMessage, id=message_id)
    if message.sender == request.user:
        message.is_deleted = True
        message.save()
        messages.success(request, 'پیام حذف شد.')
    else:
        messages.error(request, 'شما اجازه حذف این پیام را ندارید.')
    return redirect('chat:chat-room', room_id=message.room.id)


@login_required
def chat_edit_message(request, message_id):
    """ویرایش پیام"""
    message = get_object_or_404(ChatMessage, id=message_id)
    if message.sender != request.user:
        messages.error(request, 'شما اجازه ویرایش این پیام را ندارید.')
        return redirect('chat:chat-room', room_id=message.room.id)

    if request.method == 'POST':
        new_message = request.POST.get('message')
        if new_message:
            message.message = new_message
            message.is_edited = True
            message.edited_at = timezone.now()
            message.save()
            messages.success(request, 'پیام ویرایش شد.')
        return redirect('chat:chat-room', room_id=message.room.id)

    context = {
        'message': message,
    }
    return render(request, 'chat/chat_edit_message.html', context)


@login_required
def chat_notifications(request):
    """نمایش نوتیفیکیشن‌های چت"""
    notifications = ChatNotification.objects.filter(
        user=request.user,
        is_seen=False
    ).order_by('-created_at')

    # علامت‌گذاری به عنوان دیده شده
    for notif in notifications:
        notif.is_seen = True
        notif.save()

    return JsonResponse({
        'count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'message': n.message.message[:50],
                'sender': n.message.sender.get_full_name() or n.message.sender.username,
                'time': n.created_at.strftime('%H:%M'),
                'room_id': n.message.room.id,
            } for n in notifications[:10]
        ]
    })


# ============================================
# ویوهای یادداشت‌ها
# ============================================

@login_required
def note_list(request):
    """لیست یادداشت‌های کاربر"""
    user = request.user
    notes = Note.objects.filter(user=user, is_archived=False)

    pinned_notes = notes.filter(is_pinned=True)
    other_notes = notes.filter(is_pinned=False)

    context = {
        'pinned_notes': pinned_notes,
        'other_notes': other_notes,
        'total_notes': notes.count(),
    }
    return render(request, 'chat/note_list.html', context)


@login_required
def note_create(request):
    """ایجاد یادداشت جدید"""
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'یادداشت با موفقیت ایجاد شد.')
            return redirect('chat:note-list')
    else:
        form = NoteForm()

    context = {
        'form': form,
        'title': 'یادداشت جدید',
    }
    return render(request, 'chat/note_form.html', context)


@login_required
def note_edit(request, pk):
    """ویرایش یادداشت"""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'یادداشت با موفقیت ویرایش شد.')
            return redirect('chat:note-list')
    else:
        form = NoteForm(instance=note)

    context = {
        'form': form,
        'note': note,
        'title': f'ویرایش: {note.title}',
    }
    return render(request, 'chat/note_form.html', context)


@login_required
def note_delete(request, pk):
    """حذف یادداشت"""
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        note.delete()
        messages.success(request, 'یادداشت با موفقیت حذف شد.')
        return redirect('chat:note-list')

    context = {
        'note': note,
    }
    return render(request, 'chat/note_confirm_delete.html', context)


@login_required
def note_toggle_pin(request, pk):
    """پین/آنپین کردن یادداشت"""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_pinned = not note.is_pinned
    note.save()

    status = 'پین شد' if note.is_pinned else 'آنپین شد'
    messages.success(request, f'یادداشت {status}.')
    return redirect('chat:note-list')


@login_required
def note_archive(request, pk):
    """بایگانی کردن یادداشت"""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_archived = True
    note.save()
    messages.success(request, 'یادداشت بایگانی شد.')
    return redirect('chat:note-list')


@login_required
def note_archived_list(request):
    """لیست یادداشت‌های بایگانی شده"""
    user = request.user
    notes = Note.objects.filter(user=user, is_archived=True)

    context = {
        'notes': notes,
        'total_notes': notes.count(),
    }
    return render(request, 'chat/note_archived_list.html', context)


@login_required
def note_unarchive(request, pk):
    """بازگرداندن از بایگانی"""
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_archived = False
    note.save()
    messages.success(request, 'یادداشت از بایگانی بازگردانده شد.')
    return redirect('chat:note-archived-list')


# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from staff.models import StaffProfile
from .models import ChatRoom, ChatMessage, ChatNotification, SavedMessage, PinnedChat, Note, CalendarEvent
from .forms import ChatMessageForm, ChatRoomForm, NoteForm, CalendarEventForm
import calendar
from datetime import datetime, timedelta, date




@login_required
def calendar_view(request, year=None, month=None):
    """نمایش تقویم"""
    user = request.user

    # تنظیم سال و ماه
    today = timezone.now().date()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # دریافت رویدادهای ماه
    events = CalendarEvent.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    )

    # ساخت دیکشنری رویدادها بر اساس روز
    events_by_day = {}
    for event in events:
        day = event.date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    # اطلاعات تقویم
    cal = calendar.monthcalendar(year, month)

    # نام ماه‌ها به فارسی
    month_names = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
        4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر',
        10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }

    # نام روزهای هفته به فارسی
    weekdays = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']

    context = {
        'calendar': cal,
        'month_name': month_names.get(month, ''),
        'year': year,
        'month': month,
        'weekdays': weekdays,
        'events_by_day': events_by_day,
        'today': today,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'today_day': today.day,
        'today_month': today.month,
        'today_year': today.year,
    }
    return render(request, 'chat/calendar_view.html', context)


@login_required
def calendar_event_create(request):
    """ایجاد رویداد جدید"""
    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, 'رویداد با موفقیت ایجاد شد.')
            return redirect('chat:calendar-view')
    else:
        # دریافت تاریخ از پارامتر GET
        date_param = request.GET.get('date')
        form = CalendarEventForm()
        if date_param:
            try:
                form.fields['date'].initial = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                pass

    context = {
        'form': form,
        'title': 'ایجاد رویداد جدید',
    }
    return render(request, 'chat/calendar_event_form.html', context)


@login_required
def calendar_event_edit(request, pk):
    """ویرایش رویداد"""
    event = get_object_or_404(CalendarEvent, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'رویداد با موفقیت ویرایش شد.')
            return redirect('chat:calendar-view')
    else:
        form = CalendarEventForm(instance=event)

    context = {
        'form': form,
        'event': event,
        'title': f'ویرایش: {event.title}',
    }
    return render(request, 'chat/calendar_event_form.html', context)


@login_required
def calendar_event_delete(request, pk):
    """حذف رویداد"""
    event = get_object_or_404(CalendarEvent, pk=pk, user=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'رویداد با موفقیت حذف شد.')
        return redirect('chat:calendar-view')

    context = {
        'event': event,
    }
    return render(request, 'chat/calendar_event_confirm_delete.html', context)


@login_required
def calendar_events_json(request, year, month):
    """دریافت رویدادها به صورت JSON (برای نمایش در تقویم)"""
    user = request.user
    events = CalendarEvent.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    )

    data = []
    for event in events:
        data.append({
            'id': event.id,
            'title': event.title,
            'date': event.date.strftime('%Y-%m-%d'),
            'time': event.time.strftime('%H:%M') if event.time else '',
            'color': event.color,
            'is_important': event.is_important,
        })

    return JsonResponse(data, safe=False)