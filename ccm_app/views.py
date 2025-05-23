from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm, UpdateRecordForm, RecordForm
from .models import Record
from django.contrib.auth.models import User


# This is the view function for the home page
def home(request):
    # Get all records
    records = Record.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in!')
            return redirect('home')
        else:
            if not User.objects.filter(username=username).exists():
                messages.error(request, 'User does not exist.')
            else:
                messages.error(request, 'Incorrect password. Please try again.')
            return redirect('home')
    else:
        return render(request, 'home.html', {'records': records})

# This is the view function for the logout page
def logout_user(request):
    # Logout user, provide feedback and redirect to the home page
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('home')

# This is the view function for the register page
def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            authenticated_user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if authenticated_user is not None:
                login(request, authenticated_user)
                messages.success(request, 'You have been registered! Welcome to the CCM App!')
                return redirect('/')
            else:
                messages.error(request, 'Failed to log in after registration.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            # Instead of redirecting, render the template with the invalid form
            return render(request, 'register.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


# This is the view function for the payment record page
def payment_record(request, pk):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Look up the payment record
        pay_record = Record.objects.get(id=pk)
        # Render the payment record page
        return render(request, 'record.html', {'record': pay_record})
    # If the user is not authenticated, provide feedback and redirect to the home page
    else:
        messages.error(request, 'You must be logged in to view records!')
        return redirect('home')


# This is the view function for the 'Add Record' page
# It handles both GET (display form) and POST (submit form) requests
def add_record(request):
    # Initialize the form with POST data if available; otherwise, it’s an empty form
    form = RecordForm(request.POST or None)

    # Check if the user is logged in
    if request.user.is_authenticated:
        # If the form was submitted (POST request)
        if request.method == 'POST':
            # Validate the form
            if form.is_valid():
                # Create a record object but don't commit to DB yet
                record = form.save(commit=False)
                # Assign the currently logged-in user as the creator
                record.created_by = request.user
                # Save the record to the database
                record.save()
                # Show a success message
                messages.success(request, 'Record has been added!')
                # Redirect to the homepage or record list page
                return redirect('home')
            else:
                # If the form is not valid, show an error message
                messages.error(request, 'Error adding record - please try again...')
                return render(request, 'add_record.html', {'form': form})
        else:
            # If GET request, render the blank form
            return render(request, 'add_record.html', {'form': form})
    else:
        # If user is not authenticated, show an error and redirect
        messages.error(request, 'You must be logged in to add records!')
        return redirect('home')


# This is the view function for the update record page
def update_record(request, pk):
    # Ensure the user is authenticated before allowing access
    if request.user.is_authenticated:
        # Try to retrieve the specific record by primary key (pk)
        try:
            current_record = Record.objects.get(id=pk)
        except Record.DoesNotExist:
            messages.error(request, 'Record not found!')
            return redirect('home')

        # Initialize the form either with POST data or the existing record
        form = RecordForm(request.POST or None, instance=current_record)

        # If the form was submitted via POST
        if request.method == 'POST':
            # Validate the submitted data
            if form.is_valid():
                form.save()  # Save the updated record
                messages.success(request, 'Record has been updated!')
                return redirect('home')
            else:
                # If validation fails, re-render the form with error messages
                messages.error(request, 'Error updating record - please try again...')
                return render(request, 'update_record.html', {'form': form})
        else:
            # If it's a GET request, render the form with the existing record's data
            return render(request, 'update_record.html', {'form': form})
    else:
        # Block unauthenticated access
        messages.error(request, 'You must be logged in to update records!')
        return redirect('home')


# This is the view function for the delete record page
def delete_record(request, pk):
    # Only authenticated users can access this view
    if request.user.is_authenticated:
        # Only staff (admin) users are allowed to delete records
        if request.user.is_staff:
            try:
                # Try to fetch the record by its ID
                delete_it = Record.objects.get(id=pk)
            except Record.DoesNotExist:
                messages.error(request, 'Record not found!')
                return redirect('home')

            # Delete the record and notify the user
            delete_it.delete()
            messages.success(request, 'Record has been deleted!')
            return redirect('home')
        else:
            # Show error if user is not staff
            messages.error(request, 'You must be an admin to delete records!')
            return redirect('home')
    else:
        # Redirect unauthenticated users
        messages.error(request, 'You must be logged in to delete records!')
        return redirect('home')



# This is the view function for the user management page
def user_management(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user is staff
        if request.user.is_staff:
            # Get all users
            user = get_user_model()
            users = user.objects.all()
            # Render the user management page
            return render(request, 'user_management.html', {'users': users})
        # If the user is not staff, provide feedback and redirect to the home page
        else:
            messages.error(request, 'You must be an admin to view users!')
            return redirect('home')
    # If the user is not authenticated, provide feedback and redirect to the home page
    else:
        messages.error(request, 'You must be logged in to view users!')
        return redirect('home')


# Function to toggle the active status of a user
def user_active_status(request, user_id):
    # Check if user is authenticated
    if request.user.is_authenticated:
        # Check if the user is staff
        if request.user.is_staff:
            user = get_user_model()
            try:
                # Get the user by ID
                user = user.objects.get(pk=user_id)
            except user.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("user_management")

            # Check if the user to toggle is the same as the logged-in user
            if user.pk == request.user.pk:
                messages.error(request, "You cannot deactivate your own account!")
                return redirect("user_management")

            # Toggle the user's active status
            user.is_active = not user.is_active
            user.save()

            # Provide feedback to the superuser
            if user.is_active:
                message = f"{user.username}'s account has been activated."
            else:
                message = f"{user.username}'s account has been deactivated."

            messages.success(request, message)
            # Redirect to user management page after action
            return redirect("user_management")
        # If the user is not staff, provide feedback and redirect to the home page
        else:
            messages.error(request, "You must be an admin to modify user status.")
            return redirect("home")
    # If the user is not authenticated, provide feedback and redirect to the home page
    else:
        messages.error(request, "You must be logged in to perform this action.")
        return redirect("home")


# This is the view function for the search results page
def search_results(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the request method is POST
        if request.method == 'POST':
            searched = request.POST.get('searched', '')
            # Conduct the search across specified fields
            records = Record.objects.filter(first_name__icontains=searched) | \
                      Record.objects.filter(last_name__icontains=searched) | \
                      Record.objects.filter(payment_reference__icontains=searched)
            return render(request, 'search_results.html', {'searched': searched, 'records': records})
        else:
            # If the request is not POST, inform the user about the correct method to search
            messages.error(request, 'Please use the search form to submit your query.')
            return redirect('home')
    else:
        # If the user is not authenticated, inform them and redirect to the login page or home page
        messages.error(request, 'You must be logged in to search records!')
        return redirect('home')


# This is the view function for the audit logs page
def audit_logs(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Check if the user is staff
        if request.user.is_staff:
            # Get all records
            records = Record.objects.all()
            return render(request, 'audit_logs.html', {'records': records})
        # If the user is not staff, provide feedback and redirect to the home page
        else:
            messages.error(request, 'You must be an admin to view the audit log!')
            return redirect('home')
    # If the user is not authenticated, provide feedback and redirect to the home page
    else:
        messages.error(request, 'You must be logged in to view the audit log!')
        return redirect('home')
