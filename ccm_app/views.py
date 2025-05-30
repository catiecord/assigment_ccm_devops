from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .forms import SignUpForm, RecordForm, AddRecordForm, UpdateRecordForm
from .models import Record, AuditLog
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

import logging
logger = logging.getLogger('audit')


def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/login/'
    )(view_func)

# ----------------------------
# Authentication and Homepage
# ----------------------------

def login_view(request):
    # Show messages based on the 'next' URL query parameter (if redirected due to login required)
    next_url = request.GET.get('next')
    if next_url and not request.user.is_authenticated:
        if 'add_record' in next_url:
            messages.info(request, 'You must be logged in to add records!')
        elif 'search_results' in next_url:
            messages.info(request, 'You must be logged in to search records!')
        elif 'user_management' in next_url:
            messages.info(request, 'You must be logged in to view users!')
        # Add more cases here if needed

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists first for better error messages
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return render(request, 'login.html')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You have been logged in!')
                # Redirect to next if provided, else home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Account is inactive. Contact admin.')
        else:
            messages.error(request, 'Incorrect password. Please try again.')

    return render(request, 'login.html')


@login_required
def home(request):
    records = Record.objects.all()
    return render(request, 'home.html', {'records': records})

# ----------------------------
# User Registration and Logout
# ----------------------------

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('login')

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
        form = AddRecordForm(request.POST)
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
            messages.success(request, 'Record has been added!')
            return redirect('home')
        else:
            messages.error(request, 'Error adding record - please try again...')
    else:
        form = AddRecordForm()
    return render(request, 'add_record.html', {'form': form})

@login_required
def update_record(request, pk):
    current_record = get_object_or_404(Record, id=pk)
    form = UpdateRecordForm(request.POST or None, instance=current_record)
    if request.method == 'POST':
        if form.is_valid():
            updated_record = form.save(commit=False)
            updated_record.updated_by = request.user.username
            updated_record.save()

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
        messages.success(request, 'Record has been deleted!')
        return redirect('home')
    return render(request, 'confirm_delete.html', {'record': record})

# ----------------------------
# Admin & User Management
# ----------------------------

@login_required
@staff_required
def user_management(request):
    users = get_user_model().objects.all()
    return render(request, 'user_management.html', {'users': users})

@login_required
@staff_required
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

@login_required
@staff_required
def audit_logs(request):
    logs = AuditLog.objects.order_by('-timestamp')
    return render(request, 'audit_logs.html', {'logs': logs})
