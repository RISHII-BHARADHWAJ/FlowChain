"""Accounts template views"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        from accounts.models import UserActivity
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('new_password_confirm')
        if not request.user.check_password(old):
            messages.error(request, 'Old password is incorrect.')
        elif new != confirm:
            messages.error(request, 'New passwords do not match.')
        elif len(new) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        else:
            request.user.set_password(new)
            request.user.last_password_change = timezone.now()
            request.user.save()
            UserActivity.objects.create(user=request.user, action='password_change')
            messages.success(request, 'Password changed successfully. Please log in again.')
            return redirect('accounts:login')
    return render(request, 'accounts/change_password.html')


def forgot_password_view(request):
    if request.method == 'POST':
        from accounts.models import PasswordResetToken
        from django.contrib.auth import get_user_model
        from datetime import timedelta
        User = get_user_model()
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=True)
            PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=24),
                created_from_ip=request.META.get('REMOTE_ADDR'),
            )
        except Exception:
            pass
        messages.success(request, 'If this email exists, you will receive a reset link shortly.')
        return redirect('accounts:login')
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    from accounts.models import PasswordResetToken
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, 'This link has expired.')
            return redirect('accounts:login')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('accounts:login')

    if request.method == 'POST':
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        if new != confirm:
            messages.error(request, 'Passwords do not match.')
        else:
            reset_token.user.set_password(new)
            reset_token.user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('accounts:login')
    return render(request, 'accounts/reset_password.html', {'token': token})


def verify_email_view(request, token):
    from accounts.models import EmailVerificationToken
    try:
        verification = EmailVerificationToken.objects.get(token=token)
        if not verification.is_valid():
            messages.error(request, 'Verification link has expired.')
        else:
            verification.user.is_verified = True
            verification.user.save()
            verification.is_used = True
            verification.save()
            messages.success(request, 'Email verified successfully!')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('accounts:login')
