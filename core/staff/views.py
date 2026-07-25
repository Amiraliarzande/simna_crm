# staff/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import StaffProfile
from .forms import StaffCreateForm, StaffEditForm


@login_required
def staff_list(request):
    """لیست کارکنان - همه کاربران می‌توانند ببینند"""
    # همه کاربران می‌توانند لیست را ببینند
    staff = StaffProfile.objects.all()
    search_query = request.GET.get('search')
    if search_query:
        staff = staff.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    status_filter = request.GET.get('status')
    if status_filter == 'active':
        staff = staff.filter(is_active=True)
    elif status_filter == 'inactive':
        staff = staff.filter(is_active=False)

    department_filter = request.GET.get('department')
    if department_filter:
        staff = staff.filter(department=department_filter)

    stats = {
        'total': StaffProfile.objects.count(),
        'active': StaffProfile.objects.filter(is_active=True).count(),
        'inactive': StaffProfile.objects.filter(is_active=False).count(),
    }

    # بررسی اینکه آیا کاربر مدیر است (دسترسی ویرایش و حذف)
    profile = getattr(request.user, 'staff_profile', None)
    is_manager = profile and profile.department == 'management'

    context = {
        'staff': staff,
        'stats': stats,
        'search_query': search_query,
        'current_status': status_filter,
        'current_department': department_filter,
        'department_choices': StaffProfile.DEPARTMENT_CHOICES,
        'is_manager': is_manager,  # <-- برای کنترل نمایش دکمه‌ها در قالب
    }
    return render(request, 'staff/staff_list.html', context)


@login_required
def staff_create(request):
    """ایجاد کارمند جدید - فقط مدیر"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department not in ['management']:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('staff:staff-list')

    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                staff = form.save()
                messages.success(request, f'کارمند {staff.full_name} با موفقیت ایجاد شد.')
                return redirect('staff:staff-list')
            except Exception as e:
                messages.error(request, f'خطا در ایجاد کارمند: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StaffCreateForm()

    return render(request, 'staff/staff_form.html', {'form': form, 'title': 'ایجاد کارمند جدید'})


@login_required
def staff_edit(request, pk):
    """ویرایش کارمند - فقط مدیر"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department not in ['management']:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('staff:staff-list')

    staff = get_object_or_404(StaffProfile, pk=pk)

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'اطلاعات {staff.full_name} با موفقیت ویرایش شد.')
                return redirect('staff:staff-list')
            except Exception as e:
                messages.error(request, f'خطا در ویرایش: {str(e)}')
                print(f"Exception: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
                    print(f"{field}: {error}")
    else:
        form = StaffEditForm(instance=staff)

    return render(request, 'staff/staff_form.html', {
        'form': form,
        'staff': staff,
        'title': f'ویرایش {staff.full_name}'
    })


@login_required
def staff_detail(request, pk):
    """جزئیات کارمند - همه کاربران"""
    staff = get_object_or_404(StaffProfile, pk=pk)
    return render(request, 'staff/staff_detail.html', {'staff': staff})


@login_required
def staff_toggle_status(request, pk):
    """تغییر وضعیت فعال/غیرفعال کارمند - فقط مدیر"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department not in ['management']:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('staff:staff-list')

    staff = get_object_or_404(StaffProfile, pk=pk)

    if staff.user == request.user:
        messages.error(request, 'شما نمی‌توانید وضعیت خود را تغییر دهید.')
        return redirect('staff:staff-list')

    staff.is_active = not staff.is_active
    staff.user.is_active = staff.is_active
    staff.user.save()
    staff.save()

    status = 'فعال' if staff.is_active else 'غیرفعال'
    messages.success(request, f'وضعیت {staff.full_name} به "{status}" تغییر کرد.')
    return redirect('staff:staff-list')


@login_required
def staff_delete(request, pk):
    """حذف کارمند - فقط مدیر"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department not in ['management']:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('staff:staff-list')

    staff = get_object_or_404(StaffProfile, pk=pk)

    if staff.user == request.user:
        messages.error(request, 'شما نمی‌توانید خود را حذف کنید.')
        return redirect('staff:staff-list')

    if request.method == 'POST':
        staff_name = staff.full_name
        staff.user.delete()
        messages.success(request, f'کارمند {staff_name} با موفقیت حذف شد.')
        return redirect('staff:staff-list')

    return render(request, 'staff/staff_confirm_delete.html', {'staff': staff})


@login_required
def staff_dashboard(request):
    """داشبورد کارکنان - شامل چت و یادداشت‌ها"""
    user = request.user

    # ============ چت‌ها ============
    rooms = ChatRoom.objects.filter(
        participants=user,
        is_active=True
    ).order_by('-updated_at')

    # دریافت چت‌های پین شده
    from chat.models import PinnedChat
    pinned_room_ids = PinnedChat.objects.filter(user=user).values_list('room_id', flat=True)
    pinned_rooms = rooms.filter(id__in=pinned_room_ids)
    other_rooms = rooms.exclude(id__in=pinned_room_ids)

    # دریافت آخرین پیام و تعداد پیام‌های خوانده نشده هر اتاق
    chat_list = []

    for room in pinned_rooms:
        last_msg = room.messages.order_by('-created_at').first()
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()
        chat_list.append({
            'id': room.id,
            'room': room,
            'last_msg': last_msg,
            'unread_count': unread_count,
            'is_pinned': True,
        })

    for room in other_rooms:
        last_msg = room.messages.order_by('-created_at').first()
        unread_count = room.messages.filter(is_read=False).exclude(sender=user).count()
        chat_list.append({
            'id': room.id,
            'room': room,
            'last_msg': last_msg,
            'unread_count': unread_count,
            'is_pinned': False,
        })

    # ============ یادداشت‌ها ============
    notes = Note.objects.filter(user=user, is_archived=False)
    pinned_notes = notes.filter(is_pinned=True)
    other_notes = notes.filter(is_pinned=False)

    # ============ اطلاعات کاربر ============
    profile = getattr(user, 'staff_profile', None)

    context = {
        # چت
        'chat_list': chat_list,
        'has_pinned_chat': pinned_rooms.exists(),
        # یادداشت‌ها
        'pinned_notes': pinned_notes,
        'other_notes': other_notes,
        'total_notes': notes.count(),
        # کاربر
        'profile': profile,
    }
    return render(request, 'staff/staff_dashboard.html', context)
