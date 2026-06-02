from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from .models import (
    RegistrationApprovalRequest, RegistrationAuditLog, ReminderLog, StaffLockLog,
    StaffPermission, StudentProfile, Complaint, Event, Notification, College, Branch
)
from .models import StudyMaterial
try:
    from .forms import StudyMaterialForm
except Exception:
    StudyMaterialForm = None


def is_staff_user(user):
    try:
        return user.user_role.role != 'student'
    except Exception:
        return False



@login_required(login_url='smru:login')
def add_study_material(request):
    # endpoint removed — redirect to home
    return redirect('smru:home')


@login_required(login_url='smru:login')
def manage_staff_permissions(request):
    # removed UI; keep server-side grant/revoke support via API or admin only
    if request.method == 'POST':
        action = request.POST.get('action')
        staff_id = request.POST.get('staff_id')
        permission = request.POST.get('permission')
        try:
            staff = User.objects.get(id=staff_id)
            if action == 'grant' and permission:
                StaffPermission.objects.get_or_create(user=staff, permission=permission)
            elif action == 'revoke' and permission:
                StaffPermission.objects.filter(user=staff, permission=permission).delete()
        except User.DoesNotExist:
            pass
    return redirect('smru:home')


@login_required(login_url='smru:login')
@user_passes_test(lambda u: u.is_superuser or getattr(getattr(u, 'user_role', None), 'role', None) == 'admin', login_url='smru:login')
def unlock_staff_account(request, lock_log_id):
    try:
        lock = StaffLockLog.objects.get(id=lock_log_id)
        lock.unlocked_at = timezone.now()
        lock.save()
        # restore account lock record
        try:
            account_lock = lock.staff.useraccountlock
            account_lock.is_locked = False
            account_lock.unlock_at = None
            account_lock.lock_reason = ''
            account_lock.save()
        except Exception:
            pass
    except StaffLockLog.DoesNotExist:
        pass
    return redirect('smru:home')


@login_required(login_url='smru:login')
def approve_registration(request, registration_id):
    try:
        reg = RegistrationApprovalRequest.objects.get(id=registration_id)
    except RegistrationApprovalRequest.DoesNotExist:
        return redirect('smru:home')

    # Only assigned staff or admin can approve
    role = getattr(getattr(request.user, 'user_role', None), 'role', '')
    if reg.assigned_staff != request.user and not (request.user.is_superuser or role == 'admin'):
        return redirect('smru:home')

    reg.status = 'approved'
    reg.save()
    RegistrationAuditLog.objects.create(request=reg, action='approved', performed_by=request.user, details='Approved by staff')
    # Activate student account only after approval
    try:
        user = reg.user
        user.is_active = True
        user.save()
        # mark student profile approved
        if reg.student_profile:
            reg.student_profile.is_approved = True
            reg.student_profile.save()
    except Exception:
        pass
    return redirect('smru:home')


@login_required(login_url='smru:login')
def reject_registration(request, registration_id):
    try:
        reg = RegistrationApprovalRequest.objects.get(id=registration_id)
    except RegistrationApprovalRequest.DoesNotExist:
        return redirect('smru:home')

    role = getattr(getattr(request.user, 'user_role', None), 'role', '')
    if reg.assigned_staff != request.user and not (request.user.is_superuser or role == 'admin'):
        return redirect('smru:home')

    reg.status = 'rejected'
    reg.save()
    RegistrationAuditLog.objects.create(request=reg, action='rejected', performed_by=request.user, details='Rejected by staff')
    return redirect('smru:home')
