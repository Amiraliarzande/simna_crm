from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Customer, CustomerNote, CustomerGroup
from .forms import CustomerForm, CustomerNoteForm, CustomerGroupForm


@login_required
def customer_list(request):
    """لیست مشتریان با فیلتر و جستجو"""
    customers = Customer.objects.all()

    # دریافت پارامترهای فیلتر از URL
    status_filter = request.GET.get('status')
    owner_filter = request.GET.get('owner')
    customer_type_filter = request.GET.get('customer_type')
    search_query = request.GET.get('search')

    # اعمال فیلترها
    if status_filter == 'active':
        customers = customers.filter(is_active=True)
    elif status_filter == 'inactive':
        customers = customers.filter(is_active=False)
    elif status_filter == 'potential':
        customers = customers.filter(is_potential=True)

    if owner_filter:
        customers = customers.filter(owner_id=owner_filter)

    if customer_type_filter:
        customers = customers.filter(customer_type=customer_type_filter)

    if search_query:
        customers = customers.filter(
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )

    # آمار
    stats = {
        'total': Customer.objects.count(),
        'active': Customer.objects.filter(is_active=True, is_archived=False).count(),
        'inactive': Customer.objects.filter(is_active=False, is_archived=False).count(),
        'potential': Customer.objects.filter(is_potential=True, is_archived=False).count(),
        'archived': Customer.objects.filter(is_archived=True).count(),
    }
    if status_filter == 'archived':
        customers = customers.filter(is_archived=True)

    # لیست کارشناسان برای فیلتر
    owners = User.objects.filter(is_active=True)

    context = {
        'customers': customers,
        'stats': stats,
        'owners': owners,
        'current_status': status_filter,
        'current_owner': owner_filter,
        'current_customer_type': customer_type_filter,
        'search_query': search_query,
    }
    return render(request, 'customers/customer_list.html', context)


@login_required
def customer_detail(request, pk):
    """جزئیات مشتری با یادداشت‌ها"""
    customer = get_object_or_404(Customer, pk=pk)
    notes = customer.notes.all()

    if request.method == 'POST' and 'note_submit' in request.POST:
        note_form = CustomerNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.customer = customer
            note.created_by = request.user
            note.save()
            messages.success(request, 'یادداشت با موفقیت اضافه شد.')
            return redirect('customers:customer-detail', pk=customer.pk)
    else:
        note_form = CustomerNoteForm()

    context = {
        'customer': customer,
        'notes': notes,
        'note_form': note_form,
    }
    return render(request, 'customers/customer_detail.html', context)


@login_required
def customer_create(request):
    """ایجاد مشتری جدید"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            if not customer.owner:
                customer.owner = request.user
            customer.last_check_date = timezone.now()
            customer.save()
            messages.success(request, 'مشتری با موفقیت ایجاد شد.')
            return redirect('customers:customer-detail', pk=customer.pk)
    else:
        form = CustomerForm()
        if request.GET.get('potential'):
            form.fields['is_potential'].initial = True
            form.fields['potential_status'].initial = 'new_lead'

    return render(request, 'customers/customer_form.html', {'form': form})


@login_required
def customer_edit(request, pk):
    """ویرایش مشتری"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'مشتری با موفقیت ویرایش شد.')
            return redirect('customers:customer-detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_form.html', {'form': form, 'customer': customer})


@login_required
def customer_delete(request, pk):
    """حذف مشتری"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'مشتری با موفقیت حذف شد.')
        return redirect('customers:customer-list')
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})


@login_required
def customer_toggle_status(request, pk):
    """تغییر وضعیت فعال/غیرفعال مشتری"""
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_active = not customer.is_active
    if customer.is_active:
        customer.last_check_date = timezone.now()
    customer.save()

    status = 'فعال' if customer.is_active else 'غیرفعال'
    messages.success(request, f'وضعیت مشتری به "{status}" تغییر کرد.')
    return redirect('customers:customer-list')


@login_required
def potential_customers(request):
    """لیست مشتریان بالقوه"""
    customers = Customer.objects.filter(is_potential=True)

    # آمار کلی (قبل از اعمال فیلترها)
    total_count = customers.count()
    active_count = customers.filter(is_active=True).count()
    inactive_count = customers.filter(is_active=False).count()

    # دریافت پارامترها
    status_filter = request.GET.get('status')
    owner_filter = request.GET.get('owner')
    active_filter = request.GET.get('active')
    search_query = request.GET.get('search')

    # فیلتر بر اساس وضعیت بالقوه
    if status_filter and status_filter != 'all':
        customers = customers.filter(potential_status=status_filter)

    # فیلتر بر اساس کارشناس
    if owner_filter and owner_filter != 'all':
        customers = customers.filter(owner_id=owner_filter)

    # فیلتر بر اساس فعال/غیرفعال (از کارت‌ها)
    if active_filter == 'active':
        customers = customers.filter(is_active=True)
    elif active_filter == 'inactive':
        customers = customers.filter(is_active=False)

    # جستجو
    if search_query:
        customers = customers.filter(
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )

    # لیست وضعیت‌ها برای فیلتر
    potential_statuses = Customer.POTENTIAL_STATUS_CHOICES

    # لیست کارشناسان برای فیلتر
    owners = User.objects.filter(is_active=True)

    context = {
        'customers': customers,
        'potential_statuses': potential_statuses,
        'owners': owners,
        'current_status': status_filter if status_filter else 'all',
        'current_owner': owner_filter if owner_filter else 'all',
        'current_active': active_filter if active_filter else 'all',
        'search_query': search_query,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }
    return render(request, 'customers/potential_customers.html', context)


@login_required
def customer_club(request):
    """باشگاه مشتریان - نمایش گروه‌ها و اعضا"""
    groups = CustomerGroup.objects.filter(is_active=True).order_by('name')

    # آمار کلی
    total_members = Customer.objects.filter(group__isnull=False).count()
    total_groups = groups.count()

    # ایجاد لیست جدید با اطلاعات گروه‌ها و تعداد اعضا
    group_list = []
    for group in groups:
        group_list.append({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'discount_percent': group.discount_percent,
            'bonus_points': group.bonus_points,
            'bonus_description': group.bonus_description,
            'min_purchase': group.min_purchase,
            'min_visits': group.min_visits,
            'department': group.department,
            'is_active': group.is_active,
            'created_at': group.created_at,
            'updated_at': group.updated_at,
            'created_by': group.created_by,
            'member_count': group.customers.count(),  # اینجا count را محاسبه می‌کنیم
        })

    context = {
        'groups': group_list,  # ارسال لیست به جای QuerySet
        'total_members': total_members,
        'total_groups': total_groups,
    }
    return render(request, 'customers/customer_club.html', context)

@login_required
def club_group_detail(request, pk):
    """جزئیات یک گروه باشگاه مشتریان"""
    group = get_object_or_404(CustomerGroup, pk=pk)
    customers = group.customers.all()

    context = {
        'group': group,
        'customers': customers,
    }
    return render(request, 'customers/club_group_detail.html', context)


@login_required
def club_group_create(request):
    """ایجاد گروه جدید باشگاه مشتریان"""
    if request.method == 'POST':
        form = CustomerGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            messages.success(request, f'گروه "{group.name}" با موفقیت ایجاد شد.')
            return redirect('customers:customer-club')
    else:
        form = CustomerGroupForm()

    context = {
        'form': form,
        'title': 'ایجاد گروه جدید',
    }
    return render(request, 'customers/club_group_form.html', context)


@login_required
def club_group_edit(request, pk):
    """ویرایش گروه باشگاه مشتریان"""
    group = get_object_or_404(CustomerGroup, pk=pk)
    if request.method == 'POST':
        form = CustomerGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'گروه "{group.name}" با موفقیت ویرایش شد.')
            return redirect('customers:customer-club')
    else:
        form = CustomerGroupForm(instance=group)

    context = {
        'form': form,
        'group': group,
        'title': f'ویرایش گروه {group.name}',
    }
    return render(request, 'customers/club_group_form.html', context)


@login_required
def club_group_delete(request, pk):
    """حذف گروه باشگاه مشتریان"""
    group = get_object_or_404(CustomerGroup, pk=pk)
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'گروه "{group_name}" با موفقیت حذف شد.')
        return redirect('customers:customer-club')

    context = {
        'group': group,
    }
    return render(request, 'customers/club_group_confirm_delete.html', context)


@login_required
def club_group_add_member(request, pk):
    """افزودن عضو به گروه باشگاه مشتریان"""
    group = get_object_or_404(CustomerGroup, pk=pk)

    # دریافت مشتریانی که در این گروه نیستند
    existing_members = group.customers.values_list('id', flat=True)
    available_customers = Customer.objects.exclude(id__in=existing_members)

    # فیلتر بر اساس نوع مشتری
    customer_type_filter = request.GET.get('customer_type')
    if customer_type_filter == 'potential':
        available_customers = available_customers.filter(is_potential=True)
    elif customer_type_filter == 'regular':
        available_customers = available_customers.filter(is_potential=False)

    # جستجو
    search_query = request.GET.get('search')
    if search_query:
        available_customers = available_customers.filter(
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )

    if request.method == 'POST':
        customer_ids = request.POST.getlist('customers')
        if customer_ids:
            customers = Customer.objects.filter(id__in=customer_ids)
            for customer in customers:
                customer.group = group
                customer.save()
            messages.success(request, f'{len(customer_ids)} مشتری با موفقیت به گروه "{group.name}" اضافه شدند.')
            return redirect('customers:club-group-detail', pk=group.pk)
        else:
            messages.warning(request, 'لطفاً حداقل یک مشتری را انتخاب کنید.')

    # آمار برای نمایش
    total_available = available_customers.count()
    potential_count = available_customers.filter(is_potential=True).count()
    regular_count = available_customers.filter(is_potential=False).count()

    context = {
        'group': group,
        'available_customers': available_customers,
        'total_available': total_available,
        'potential_count': potential_count,
        'regular_count': regular_count,
        'current_filter': customer_type_filter,
        'search_query': search_query,
    }
    return render(request, 'customers/club_group_add_member.html', context)

@login_required
def note_edit(request, pk):
    """ویرایش یادداشت"""
    note = get_object_or_404(CustomerNote, pk=pk)
    if request.method == 'POST':
        form = CustomerNoteForm(request.POST, instance=note)
        if form.is_valid():
            note.is_edited = True
            form.save()
            messages.success(request, 'یادداشت با موفقیت ویرایش شد.')
            return redirect('customers:customer-detail', pk=note.customer.pk)
    else:
        form = CustomerNoteForm(instance=note)
    return render(request, 'customers/note_form.html', {'form': form, 'note': note})


@login_required
def note_delete(request, pk):
    """حذف یادداشت"""
    note = get_object_or_404(CustomerNote, pk=pk)
    customer_pk = note.customer.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'یادداشت با موفقیت حذف شد.')
        return redirect('customers:customer-detail', pk=customer_pk)
    return render(request, 'customers/note_confirm_delete.html', {'note': note})


@login_required
def note_toggle_pin(request, pk):
    """پین/آنپین کردن یادداشت"""
    note = get_object_or_404(CustomerNote, pk=pk)
    note.is_pinned = not note.is_pinned
    note.save()

    status = 'پین شد' if note.is_pinned else 'آنپین شد'
    messages.success(request, f'یادداشت {status}.')
    return redirect('customers:customer-detail', pk=note.customer.pk)


@login_required
def check_and_deactivate(request):
    """بررسی و غیرفعال کردن خودکار مشتریان"""
    customers = Customer.objects.filter(is_active=True)
    deactivated = 0
    for customer in customers:
        if customer.check_and_deactivate():
            deactivated += 1

    if deactivated > 0:
        messages.info(request, f'{deactivated} مشتری به دلیل عدم بررسی غیرفعال شدند.')
    else:
        messages.info(request, 'همه مشتریان به‌روز هستند.')
    return redirect('customers:customer-list')


# customers/views.py

@login_required
def archived_customers(request):
    """لیست مشتریان بایگانی شده"""
    customers = Customer.objects.filter(is_archived=True)

    # جستجو
    search_query = request.GET.get('search')
    if search_query:
        customers = customers.filter(
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )

    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'customers/archived_customers.html', context)


@login_required
def customer_archive(request, pk):
    """بایگانی کردن مشتری"""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        customer.is_archived = True
        customer.is_active = False
        customer.archived_at = timezone.now()
        customer.archived_by = request.user
        customer.archive_reason = reason
        customer.save()
        messages.success(request, f'مشتری "{customer.full_name}" با موفقیت بایگانی شد.')
        return redirect('customers:customer-list')

    context = {
        'customer': customer,
    }
    return render(request, 'customers/customer_archive_confirm.html', context)


@login_required
def customer_unarchive(request, pk):
    """بازگرداندن مشتری از بایگانی"""
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_archived = False
    customer.is_active = True
    customer.archived_at = None
    customer.archived_by = None
    customer.archive_reason = None
    customer.save()
    messages.success(request, f'مشتری "{customer.full_name}" از بایگانی بازگردانده شد.')
    return redirect('customers:archived-customers')


@login_required
def customer_archive_delete(request, pk):
    """حذف دائمی مشتری بایگانی شده"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer_name = customer.full_name
        customer.delete()
        messages.success(request, f'مشتری "{customer_name}" به طور دائمی حذف شد.')
        return redirect('customers:archived-customers')

    context = {
        'customer': customer,
    }
    return render(request, 'customers/archive_delete_confirm.html', context)