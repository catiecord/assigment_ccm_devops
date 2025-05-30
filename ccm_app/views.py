

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm, UpdateRecordForm, RecordForm
from .models import Record
from django.contrib.auth.models import User
import logging
logger = logging.getLogger('audit')

# ----------------------------
# Authentication and Homepage
# ----------------------------

# Handles login logic with user existence and active status checks
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

    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        if user.is_active:
            login(request, user)
            messages.success(request, 'You have been logged in!')
        else:
            messages.error(request, 'Account is inactive. Contact admin.')
        return redirect('home')
    else:
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'User does not exist.')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
        return redirect('home')

# Displays all records or handles login via POST
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

def payment_record(request, pk):
    if request.user.is_authenticated:
        pay_record = get_object_or_404(Record, id=pk)
        return render(request, 'record.html', {'record': pay_record})
    else:
        messages.error(request, 'You must be logged in to view records!')
        return redirect('home')

def add_record(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to add records!')
        return redirect('home')

    form = RecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.created_by = request.user
        record.save()
        messages.success(request, 'Record has been added!')
        return redirect('home')
    elif request.method == 'POST':
        messages.error(request, 'Error adding record - please try again...')
    return render(request, 'add_record.html', {'form': form})

def update_record(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to update records!')
        return redirect('home')

    current_record = get_object_or_404(Record, id=pk)
    form = RecordForm(request.POST or None, instance=current_record)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Record has been updated!')
            return redirect('home')
        else:
            messages.error(request, 'Error updating record - please try again...')
    return render(request, 'update_record.html', {'form': form})

def delete_record(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to delete records!')
        return redirect('home')

    if not request.user.is_staff:
        messages.error(request, 'You must be an admin to delete records!')
        return redirect('home')

    record = get_object_or_404(Record, id=pk)
    logger.info(f"{request.user} deleted record {record.id}")
    record.delete()
    messages.success(request, 'Record has been deleted!')
    return redirect('home')

# ----------------------------
# Admin & User Management
# ----------------------------

def user_management(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to view users!')
        return redirect('home')

    if not request.user.is_staff:
        messages.error(request, 'You must be an admin to view users!')
        return redirect('home')

    users = get_user_model().objects.all()
    return render(request, 'user_management.html', {'users': users})

def user_active_status(request, user_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to perform this action.")
        return redirect("home")

    if not request.user.is_staff:
        messages.error(request, "You must be an admin to modify user status.")
        return redirect("home")

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

    message = f"{target_user.username}'s account has been {'activated' if target_user.is_active else 'deactivated'}."
    messages.success(request, message)
    return redirect("user_management")

# ----------------------------
# Search and Audit Logs
# ----------------------------

def search_results(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to search records!')
        return redirect('home')

    if request.method == 'POST':
        searched = request.POST.get('searched', '')
        records = Record.objects.filter(first_name__icontains=searched) |                   Record.objects.filter(last_name__icontains=searched) |                   Record.objects.filter(payment_reference__icontains=searched)
        return render(request, 'search_results.html', {'searched': searched, 'records': records})

    messages.error(request, 'Please use the search form to submit your query.')
    return redirect('home')

def audit_logs(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to view the audit log!')
        return redirect('home')

    if not request.user.is_staff:
        messages.error(request, 'You must be an admin to view the audit log!')
        return redirect('home')

    records = Record.objects.all()
    return render(request, 'audit_logs.html', {'records': records})