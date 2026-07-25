# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from staff.models import StaffProfile
from accounts.models import Profile


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        # دریافت اطلاعات از فرم
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        avatar = request.FILES.get('avatar')

        # اعتبارسنجی
        has_error = False

        # بررسی ایمیل تکراری
        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'این ایمیل قبلاً ثبت شده است.')
            has_error = True

        # بررسی رمز عبور
        if new_password and new_password != confirm_password:
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند.')
            has_error = True

        if new_password and len(new_password) < 8:
            messages.error(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد.')
            has_error = True

        if not has_error:
            # به‌روزرسانی اطلاعات کاربر
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            # به‌روزرسانی پروفایل
            profile.phone = phone
            if avatar:
                profile.avatar = avatar
            profile.save()

            # به‌روزرسانی StaffProfile اگر وجود دارد
            try:
                staff_profile = user.staff_profile
                staff_profile.phone = phone
                staff_profile.save()
            except:
                pass

            # تغییر رمز عبور
            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'رمز عبور با موفقیت تغییر کرد.')

            messages.success(request, 'اطلاعات پروفایل با موفقیت به‌روزرسانی شد.')
            return redirect('profile')

    context = {
        'profile': profile,
        'user': user,
    }
    return render(request, 'accounts/profile.html', context)

