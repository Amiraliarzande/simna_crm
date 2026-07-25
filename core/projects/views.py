# projects/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from customers.models import Customer
from staff.models import StaffProfile
from .models import Project, ProjectComment, ProjectFile
from .forms import ProjectForm, ProjectCommentForm


@login_required
def project_list(request):
    """لیست پروژه‌ها"""
    user = request.user
    profile = getattr(user, 'staff_profile', None)

    # دریافت پروژه‌های قابل مشاهده
    projects = Project.objects.filter(
        Q(created_by=user) |
        Q(members=user) |
        Q(visibility='public')
    )

    # اگر کاربر دپارتمان دارد، پروژه‌های دپارتمان را هم ببیند
    if profile and profile.department:
        dept_members = User.objects.filter(staff_profile__department=profile.department)
        projects = projects | Project.objects.filter(
            visibility='department',
            members__in=dept_members
        )

    projects = projects.distinct().order_by('-created_at')

    # فیلترها
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)

    type_filter = request.GET.get('type')
    if type_filter:
        projects = projects.filter(project_type=type_filter)

    # آمار
    stats = {
        'total': projects.count(),
        'not_started': projects.filter(status='not_started').count(),
        'in_progress': projects.filter(status='in_progress').count(),
        'pending': projects.filter(status='pending').count(),
        'completed': projects.filter(status='completed').count(),
        'cancelled': projects.filter(status='cancelled').count(),
    }

    context = {
        'projects': projects,
        'stats': stats,
        'status_choices': Project.STATUS_CHOICES,
        'type_choices': Project.PROJECT_TYPE_CHOICES,
        'current_status': status_filter,
        'current_type': type_filter,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_create(request):
    """ایجاد پروژه جدید"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user

            # اگر پروژه داخلی است، مشتری را حذف کن
            if project.project_type == 'internal':
                project.customer = None

            project.save()
            form.save_m2m()  # ذخیره members

            messages.success(request, f'پروژه "{project.title}" با موفقیت ایجاد شد.')
            return redirect('projects:project-detail', pk=project.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProjectForm()

    context = {
        'form': form,
        'title': 'ایجاد پروژه جدید',
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_detail(request, pk):
    """جزئیات پروژه"""
    project = get_object_or_404(Project, pk=pk)

    # بررسی دسترسی
    if not project.is_visible_to(request.user):
        messages.error(request, 'شما دسترسی لازم برای مشاهده این پروژه را ندارید.')
        return redirect('projects:project-list')

    comments = project.comments.all()

    if request.method == 'POST':
        form = ProjectCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
            messages.success(request, 'نظر شما ثبت شد.')
            return redirect('projects:project-detail', pk=project.pk)
    else:
        form = ProjectCommentForm()

    context = {
        'project': project,
        'comments': comments,
        'form': form,
        'can_edit': project.created_by == request.user,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_edit(request, pk):
    """ویرایش پروژه"""
    project = get_object_or_404(Project, pk=pk)

    if project.created_by != request.user:
        messages.error(request, 'شما دسترسی لازم برای ویرایش این پروژه را ندارید.')
        return redirect('projects:project-list')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            if project.project_type == 'internal':
                project.customer = None
            project.save()
            form.save_m2m()
            messages.success(request, f'پروژه "{project.title}" با موفقیت ویرایش شد.')
            return redirect('projects:project-detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    context = {
        'form': form,
        'project': project,
        'title': f'ویرایش: {project.title}',
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_delete(request, pk):
    """حذف پروژه"""
    project = get_object_or_404(Project, pk=pk)

    if project.created_by != request.user:
        messages.error(request, 'شما دسترسی لازم برای حذف این پروژه را ندارید.')
        return redirect('projects:project-list')

    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'پروژه "{project_title}" با موفقیت حذف شد.')
        return redirect('projects:project-list')

    context = {
        'project': project,
    }
    return render(request, 'projects/project_confirm_delete.html', context)


@login_required
def project_change_status(request, pk):
    """تغییر وضعیت پروژه"""
    project = get_object_or_404(Project, pk=pk)

    if not project.is_visible_to(request.user):
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('projects:project-list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.STATUS_CHOICES):
            project.status = new_status
            if new_status == 'completed':
                project.actual_end_date = timezone.now().date()
            project.save()
            messages.success(request, f'وضعیت پروژه به "{dict(Project.STATUS_CHOICES).get(new_status)}" تغییر کرد.')

    return redirect('projects:project-detail', pk=project.pk)


@login_required
def project_select_type(request):
    """انتخاب نوع پروژه (داخلی/خارجی)"""
    return render(request, 'projects/project_select_type.html')


@login_required
def project_create(request, project_type=None):
    """ایجاد پروژه جدید"""
    # اگر نوع پروژه انتخاب نشده، به صفحه انتخاب هدایت کن
    if not project_type or project_type not in ['internal', 'external']:
        return redirect('projects:project-select-type')

    if request.method == 'POST':
        form = ProjectForm(request.POST, project_type=project_type)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.project_type = project_type

            # اگر پروژه داخلی است، مشتری را حذف کن
            if project_type == 'internal':
                project.customer = None

            project.save()
            form.save_m2m()  # ذخیره members

            messages.success(request, f'پروژه "{project.title}" با موفقیت ایجاد شد.')
            return redirect('projects:project-detail', pk=project.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProjectForm(project_type=project_type)

    context = {
        'form': form,
        'title': 'ایجاد پروژه جدید',
        'project_type': project_type,
        'project_type_display': 'داخلی' if project_type == 'internal' else 'خارجی',
    }
    return render(request, 'projects/project_form.html', context)