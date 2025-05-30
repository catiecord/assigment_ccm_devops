from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .forms import SignUpForm, AddRecordForm, UpdateRecordForm, RecordForm
from .models import Record, AuditLog

import logging
logger = logging.getLogger('audit')

# ----------------------------
# Authentication and Homepage
# ----------------------------

def handle_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
        return redirect('home')

    if not user.is_active:
        messages.error(request, 'Account is inactive. Contact admin.')
        return redirect('home')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, 'You have been logged in!')
    else:
        messages.error(request, 'Incorrect password. Please try again.')

    return redirect('home')

def home(request):
    records = Record.objects.all()
    if request.method == 'POST':
        return handle_login(request)
    return render(request, 'home.html', {'records': records})

# ----------------------------
# User Registration and Logout
# ----------------------------

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if authenticated_user:
                login(request, authenticated_user)
                AuditLog.objects.create(
                    user=authenticated_user,
                    action='REGISTER',
                    description=f"User {user.username} registered"
                )
                messages.success(request, 'You have been registered! Welcome to the CCM App!')
                return redirect('home')
            else:
                messages.error(request, 'Failed to log in after registration.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, 'register.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

# ----------------------------
# Record Management
# ----------------------------

@login_required
def payment_record(request, pk):
    pay_record = get_object_or_404(Record, id=pk)
    return render(request, 'record.html', {'record': pay_record})

@login_required
def add_record(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.updated_by = request.user.username
            record.save()

            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                description=f"Created record {record.payment_reference}"
            )

            return redirect('records_list')
    else:
        form = RecordForm()
    return render(request, 'ccm_app/add_record.html', {'form': form})

@login_required
def update_record(request, pk):
    current_record = get_object_or_404(Record, id=pk)
    form = RecordForm(request.POST or None, instance=current_record)
    if request.method == 'POST':
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                description=f"Updated record {current_record.payment_reference}"
            )

            messages.success(request, 'Record has been updated!')
            return redirect('home')
        else:
            messages.error(request, 'Error updating record - please try again...')
    return render(request, 'update_record.html', {'form': form})

@login_required
def delete_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    if request.method == 'POST':
        AuditLog.objects.create(
            user=request.user,
            action='DELETE',
            description=f"Deleted record {record.payment_reference}"
        )
        record.delete()
        return redirect('records_list')
    return render(request, 'ccm_app/confirm_delete.html', {'record': record})

# ----------------------------
# Admin & User Management
# ----------------------------

@login_required
@staff_member_required
def user_management(request):
    users = get_user_model().objects.all()
    return render(request, 'user_management.html', {'users': users})

@login_required
@staff_member_required
def user_active_status(request, user_id):
    user_model = get_user_model()
    try:
        target_user = user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("user_management")

    if target_user.pk == request.user.pk:
        messages.error(request, "You cannot deactivate your own account!")
        return redirect("user_management")

    target_user.is_active = not target_user.is_active
    target_user.save()

    AuditLog.objects.create(
        user=request.user,
        action='PROMOTE',
        description=f"Toggled active status for user {target_user.username} to {target_user.is_active}"
    )

    message = f"{target_user.username}'s account has been {'activated' if target_user.is_active else 'deactivated'}."
    messages.success(request, message)
    return redirect("user_management")

# ----------------------------
# Search and Audit Logs
# ----------------------------

@login_required
def search_results(request):
    if request.method == 'POST':
        searched = request.POST.get('searched', '')
        records = Record.objects.filter(first_name__icontains=searched) | \
                  Record.objects.filter(last_name__icontains=searched) | \
                  Record.objects.filter(payment_reference__icontains=searched)
        return render(request, 'search_results.html', {'searched': searched, 'records': records})

    messages.error(request, 'Please use the search form to submit your query.')
    return redirect('home')

@staff_member_required
def audit_logs(request):
    logs = AuditLog.objects.order_by('-timestamp')
    return render(request, 'ccm_app/audit_logs.html', {'logs': logs})
