# tasks/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from staff.models import StaffProfile
from .models import Task, TaskComment, TaskNotification
from .forms import TaskForm, TaskCommentForm


@login_required
def task_list(request):
    """لیست وظایف قابل مشاهده برای کاربر"""
    user = request.user
    profile = getattr(user, 'staff_profile', None)

    # ============================================
    # دریافت وظایف قابل مشاهده برای کاربر
    # ============================================

    # شرط اول: وظایفی که کاربر ایجاد کرده است
    created_by_user = Q(created_by=user)

    # شرط دوم: وظایف عمومی (visibility='public')
    public_tasks = Q(visibility='public')

    # شرط سوم: وظایفی که به کاربر اختصاص داده شده است (visibility='assigned')
    assigned_to_user = Q(visibility='assigned', assigned_to=user)

    # شرط چهارم: وظایف دپارتمان (visibility='department')
    department_tasks = Q()
    if profile and profile.department:
        department_tasks = Q(visibility='department', assigned_department=profile.department)

    # ترکیب همه شرایط
    tasks = Task.objects.filter(
        created_by_user | public_tasks | assigned_to_user | department_tasks
    ).distinct().order_by('-priority', 'due_date')

    # ============================================
    # اعمال فیلترها
    # ============================================

    # فیلتر بر اساس وضعیت
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # فیلتر بر اساس اولویت
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # فیلتر بر اساس نوع اختصاص
    assigned_filter = request.GET.get('assigned')
    if assigned_filter == 'me':
        tasks = tasks.filter(assigned_to=user)
    elif assigned_filter == 'my_department':
        if profile and profile.department:
            tasks = tasks.filter(assigned_department=profile.department)
    elif assigned_filter == 'created_by_me':
        tasks = tasks.filter(created_by=user)

    # ============================================
    # آمار وظایف
    # ============================================

    stats = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'completed': tasks.filter(status='completed').count(),
        'overdue': tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(
            status__in=['completed', 'cancelled']
        ).count(),
    }

    # ============================================
    # آماده سازی context
    # ============================================

    context = {
        'tasks': tasks,
        'stats': stats,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'visibility_choices': Task.VISIBILITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'current_assigned': assigned_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    """ایجاد وظیفه جدید"""
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()  # ذخیره ManyToMany (assigned_to)

            # ایجاد نوتیفیکیشن برای افراد مسئول
            for assigned_user in task.assigned_to.all():
                if assigned_user != request.user:
                    TaskNotification.objects.create(
                        user=assigned_user,
                        task=task,
                        message=f'وظیفه جدید "{task.title}" به شما اختصاص داده شد.'
                    )

            # نوتیفیکیشن برای دپارتمان
            if task.assigned_department:
                staff_users = StaffProfile.objects.filter(department=task.assigned_department)
                for staff in staff_users:
                    if staff.user != request.user and not task.assigned_to.filter(id=staff.user.id).exists():
                        TaskNotification.objects.create(
                            user=staff.user,
                            task=task,
                            message=f'وظیفه جدید "{task.title}" برای دپارتمان {dict(StaffProfile.DEPARTMENT_CHOICES).get(task.assigned_department)} ایجاد شد.'
                        )

            messages.success(request, f'وظیفه "{task.title}" با موفقیت ایجاد شد.')
            return redirect('tasks:task-detail', pk=task.pk)
        else:
            # نمایش خطاها
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TaskForm()

    context = {
        'form': form,
        'title': 'ایجاد وظیفه جدید',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_detail(request, pk):
    """جزئیات وظیفه"""
    task = get_object_or_404(Task, pk=pk)

    # بررسی دسترسی با تابع is_visible_to
    if not task.is_visible_to(request.user):
        messages.error(request, 'شما دسترسی لازم برای مشاهده این وظیفه را ندارید.')
        return redirect('tasks:task-list')

    # نظرات
    comments = task.comments.all()

    if request.method == 'POST':
        form = TaskCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()

            # نوتیفیکیشن برای افراد مرتبط
            for assigned_user in task.assigned_to.all():
                if assigned_user != request.user:
                    TaskNotification.objects.create(
                        user=assigned_user,
                        task=task,
                        message=f'{request.user.get_full_name()} روی وظیفه "{task.title}" نظر داد.'
                    )
            if task.created_by != request.user:
                TaskNotification.objects.create(
                    user=task.created_by,
                    task=task,
                    message=f'{request.user.get_full_name()} روی وظیفه "{task.title}" نظر داد.'
                )

            messages.success(request, 'نظر شما ثبت شد.')
            return redirect('tasks:task-detail', pk=task.pk)
    else:
        form = TaskCommentForm()

    context = {
        'task': task,
        'comments': comments,
        'form': form,
        'can_edit': task.created_by == request.user or task.assigned_to.filter(id=request.user.id).exists(),
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_edit(request, pk):
    """ویرایش وظیفه"""
    task = get_object_or_404(Task, pk=pk)

    # فقط ایجاد کننده یا افراد اختصاص داده شده می‌توانند ویرایش کنند
    if task.created_by != request.user and not task.assigned_to.filter(id=request.user.id).exists():
        messages.error(request, 'شما دسترسی لازم برای ویرایش این وظیفه را ندارید.')
        return redirect('tasks:task-list')

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'وظیفه "{task.title}" با موفقیت ویرایش شد.')
            return redirect('tasks:task-detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'title': f'ویرایش: {task.title}',
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, pk):
    """حذف وظیفه"""
    task = get_object_or_404(Task, pk=pk)

    # فقط ایجاد کننده می‌تواند حذف کند
    if task.created_by != request.user:
        messages.error(request, 'شما دسترسی لازم برای حذف این وظیفه را ندارید.')
        return redirect('tasks:task-list')

    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'وظیفه "{task_title}" با موفقیت حذف شد.')
        return redirect('tasks:task-list')

    context = {
        'task': task,
    }
    return render(request, 'tasks/task_confirm_delete.html', context)


@login_required
def task_change_status(request, pk):
    """تغییر وضعیت وظیفه"""
    task = get_object_or_404(Task, pk=pk)

    if not task.is_visible_to(request.user):
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('tasks:task-list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, f'وضعیت وظیفه به "{dict(Task.STATUS_CHOICES).get(new_status)}" تغییر کرد.')

    return redirect('tasks:task-detail', pk=task.pk)


@login_required
def task_my_tasks(request):
    """وظایف من"""
    user = request.user
    tasks = Task.objects.filter(
        Q(assigned_to=user) | Q(created_by=user)
    ).distinct().order_by('-priority', 'due_date')

    context = {
        'tasks': tasks,
        'title': 'وظایف من',
    }
    return render(request, 'tasks/task_list.html', context)