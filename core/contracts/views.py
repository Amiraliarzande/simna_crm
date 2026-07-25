# contracts/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from staff.models import StaffProfile
from .models import Contract, ContractNotification
from .forms import ContractForm, ContractSignForm


@login_required
def contract_list(request):
    """لیست قراردادها - فقط مدیران همه قراردادها را می‌بینند، کارمندان فقط قراردادهای خودشان"""
    profile = getattr(request.user, 'staff_profile', None)
    is_manager = profile and profile.department == 'management'

    if is_manager:
        contracts = Contract.objects.all().order_by('-created_at')
    else:
        contracts = Contract.objects.filter(employee=request.user).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter and is_manager:
        contracts = contracts.filter(status=status_filter)

    employee_filter = request.GET.get('employee')
    if employee_filter and is_manager:
        contracts = contracts.filter(employee_id=employee_filter)

    if is_manager:
        stats = {
            'total': Contract.objects.count(),
            'draft': Contract.objects.filter(status='draft').count(),
            'pending_admin': Contract.objects.filter(status='pending_admin').count(),
            'pending_employee': Contract.objects.filter(status='pending_employee').count(),
            'signed': Contract.objects.filter(status='signed').count(),
            'rejected': Contract.objects.filter(status='rejected').count(),
        }
        employees = User.objects.filter(is_active=True)
    else:
        stats = {
            'total': contracts.count(),
            'draft': contracts.filter(status='draft').count(),
            'pending_admin': contracts.filter(status='pending_admin').count(),
            'pending_employee': contracts.filter(status='pending_employee').count(),
            'signed': contracts.filter(status='signed').count(),
            'rejected': contracts.filter(status='rejected').count(),
        }
        employees = []

    context = {
        'contracts': contracts,
        'stats': stats,
        'employees': employees,
        'status_choices': Contract.STATUS_CHOICES,
        'current_status': status_filter,
        'current_employee': employee_filter,
        'is_manager': is_manager,
    }
    return render(request, 'contracts/contract_list.html', context)


@login_required
def contract_create(request):
    """ایجاد قرارداد جدید - فقط مدیران"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department != 'management':
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.save()

            ContractNotification.objects.create(
                user=contract.employee,
                contract=contract,
                message=f'قرارداد جدید "{contract.title}" برای شما ثبت شد.'
            )

            messages.success(request, f'قرارداد "{contract.title}" با موفقیت ایجاد شد.')
            return redirect('contracts:contract-detail', pk=contract.pk)
    else:
        form = ContractForm()

    context = {
        'form': form,
        'title': 'ایجاد قرارداد جدید',
    }
    return render(request, 'contracts/contract_form.html', context)


@login_required
def contract_detail(request, pk):
    """جزئیات قرارداد"""
    contract = get_object_or_404(Contract, pk=pk)
    profile = getattr(request.user, 'staff_profile', None)

    is_manager = profile and profile.department == 'management'
    is_employee = contract.employee == request.user

    if not is_manager and not is_employee:
        messages.error(request, 'شما دسترسی لازم برای مشاهده این بخش را ندارید.')
        return redirect('home')

    sign_form = ContractSignForm()

    context = {
        'contract': contract,
        'sign_form': sign_form,
        'is_manager': is_manager,
        'is_employee': is_employee,
    }
    return render(request, 'contracts/contract_detail.html', context)


@login_required
def contract_sign_admin(request, pk):
    """امضای قرارداد توسط مدیر"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department != 'management':
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    contract = get_object_or_404(Contract, pk=pk)

    if request.method == 'POST':
        form = ContractSignForm(request.POST)
        if form.is_valid():
            signature = form.cleaned_data.get('signature')
            if contract.sign_by_admin(request.user, signature):
                messages.success(request, 'قرارداد با موفقیت امضا شد و برای کارمند ارسال گردید.')

                ContractNotification.objects.create(
                    user=contract.employee,
                    contract=contract,
                    message=f'قرارداد "{contract.title}" توسط مدیر امضا شد. لطفاً آن را امضا کنید.'
                )
            else:
                messages.error(request, 'امکان امضای این قرارداد وجود ندارد.')
            return redirect('contracts:contract-detail', pk=contract.pk)

    return redirect('contracts:contract-detail', pk=contract.pk)


@login_required
def contract_sign_employee(request, pk):
    """امضای قرارداد توسط کارمند"""
    contract = get_object_or_404(Contract, pk=pk)

    if contract.employee != request.user:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    if request.method == 'POST':
        form = ContractSignForm(request.POST)
        if form.is_valid():
            signature = form.cleaned_data.get('signature')
            if contract.sign_by_employee(request.user, signature):
                messages.success(request, 'قرارداد با موفقیت امضا شد.')

                managers = User.objects.filter(staff_profile__department='management')
                for manager in managers:
                    ContractNotification.objects.create(
                        user=manager,
                        contract=contract,
                        message=f'قرارداد "{contract.title}" توسط کارمند امضا شد.'
                    )
            else:
                messages.error(request, 'امکان امضای این قرارداد وجود ندارد.')
            return redirect('contracts:contract-detail', pk=contract.pk)

    return redirect('contracts:contract-detail', pk=contract.pk)


@login_required
def contract_send_to_employee(request, pk):
    """ارسال قرارداد به کارمند برای امضا - فقط مدیران"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department != 'management':
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    contract = get_object_or_404(Contract, pk=pk)

    if contract.send_to_employee(request.user):
        messages.success(request, 'قرارداد برای کارمند ارسال شد.')
        ContractNotification.objects.create(
            user=contract.employee,
            contract=contract,
            message=f'قرارداد "{contract.title}" برای امضا برای شما ارسال شد.'
        )
    else:
        messages.error(request, 'امکان ارسال این قرارداد وجود ندارد.')

    return redirect('contracts:contract-detail', pk=contract.pk)


@login_required
def contract_reject(request, pk):
    """رد قرارداد - فقط مدیران"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department != 'management':
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    contract = get_object_or_404(Contract, pk=pk)
    reason = request.POST.get('reason', '')

    if contract.reject(request.user, reason):
        messages.success(request, 'قرارداد رد شد.')
        ContractNotification.objects.create(
            user=contract.employee,
            contract=contract,
            message=f'قرارداد "{contract.title}" توسط مدیر رد شد.'
        )
    else:
        messages.error(request, 'امکان رد این قرارداد وجود ندارد.')

    return redirect('contracts:contract-detail', pk=contract.pk)


@login_required
def contract_delete(request, pk):
    """حذف قرارداد - فقط مدیران"""
    profile = getattr(request.user, 'staff_profile', None)
    if not profile or profile.department != 'management':
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    contract = get_object_or_404(Contract, pk=pk)

    if request.method == 'POST':
        contract_title = contract.title
        contract.delete()
        messages.success(request, f'قرارداد "{contract_title}" با موفقیت حذف شد.')
        return redirect('contracts:contract-list')

    return render(request, 'contracts/contract_confirm_delete.html', {'contract': contract})


@login_required
def contract_employee_list(request):
    """لیست قراردادهای کارمند جاری - فقط برای کارمندان"""
    contracts = Contract.objects.filter(employee=request.user).order_by('-created_at')

    context = {
        'contracts': contracts,
    }
    return render(request, 'contracts/contract_employee_list.html', context)


@login_required
def contract_employee_respond(request, pk):
    """پاسخ کارمند به قرارداد (پذیرش یا رد)"""
    contract = get_object_or_404(Contract, pk=pk)

    # فقط خود کارمند می‌تواند پاسخ دهد
    if contract.employee != request.user:
        messages.error(request, 'شما دسترسی لازم برای این کار را ندارید.')
        return redirect('home')

    # فقط قراردادهایی که در انتظار امضای کارمند هستند
    if contract.status != 'pending_employee':
        messages.error(request, 'این قرارداد در وضعیت قابل پاسخگویی نیست.')
        return redirect('contracts:contract-detail', pk=contract.pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        signature = request.POST.get('signature', '')

        if action == 'accept':
            # پذیرش و امضای قرارداد
            if contract.sign_by_employee(request.user, signature):
                messages.success(request, 'قرارداد با موفقیت پذیرفته و امضا شد.')

                # نوتیفیکیشن برای مدیران
                managers = User.objects.filter(staff_profile__department='management')
                for manager in managers:
                    ContractNotification.objects.create(
                        user=manager,
                        contract=contract,
                        message=f'قرارداد "{contract.title}" توسط کارمند پذیرفته و امضا شد.'
                    )
            else:
                messages.error(request, 'امکان پذیرش این قرارداد وجود ندارد.')

        elif action == 'reject':
            # رد قرارداد توسط کارمند
            reason = request.POST.get('reason', '')
            contract.status = 'rejected'
            contract.notes = reason or 'کارمند قرارداد را رد کرد.'
            contract.save()
            messages.success(request, 'قرارداد با موفقیت رد شد.')

            # نوتیفیکیشن برای مدیران
            managers = User.objects.filter(staff_profile__department='management')
            for manager in managers:
                ContractNotification.objects.create(
                    user=manager,
                    contract=contract,
                    message=f'قرارداد "{contract.title}" توسط کارمند رد شد.'
                )

        return redirect('contracts:contract-detail', pk=contract.pk)

    return redirect('contracts:contract-detail', pk=contract.pk)

