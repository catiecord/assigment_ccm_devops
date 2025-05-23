# Create sign up form
# This form is used to register new users
# It inherits from UserCreationForm, which is a built-in form for user registration
# It adds fields for first name and last name
# It also customizes the appearance of the form fields
from .models import Record
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create sign up form
class SignUpForm(UserCreationForm):
    # Define form fields
    email = forms.EmailField(label="",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    # Define model and fields
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    # Define form initialization
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Add custom styling to the username field, password1 field, and password2 field
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['placeholder'] = self.fields[field_name].label
            self.fields[field_name].label = ''

        # Add custom styling and help text to the password1 field
        self.fields['password1'].help_text = (
            '<ul class="form-text text-muted small"><li>Your password can\'t be too similar '
            'to your other personal information.</li><li>Your password must contain at least '
            '8 characters.</li><li>Your password can\'t be a commonly used '
            'password.</li><li>Your password can\'t be entirely numeric.</li></ul>')

        # Add custom styling and help text to the password2 field
        self.fields['password2'].help_text = (
            '<span class="form-text text-muted"><small>Enter the same password as before, '
            'for verification.</small></span>')

    # Define form validation
    # Django forms auth already does some of the validation for us
    def clean_username(self):
        # Check if the username already exists
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_email(self):
        # Check if the email already exists
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address is already in use.')
        return email


# Define a model-based form for the Record model
# This form will handle user input for creating and validating Contact records
class RecordForm(forms.ModelForm):
    # Meta class defines metadata for the form
    # It links this form to the Contact model and specifies which fields to include
    class Meta:
        model = Record
        fields = [            
            'payment_reference',
            'first_name',
            'last_name',
            'contact_method',
            'contact_date',
            'contact_status',
            'notes'
            ]  # Only these fields will be rendered and processed in the form

    # Custom validator for the 'name' field
    # This method is automatically called by Django's form validation process
    # It ensures that the name entered by the user does not exceed 100 characters
    def clean_name(self):
        name = self.cleaned_data['name']  # Get the cleaned value from the form input
        if len(name) > 100:
            raise forms.ValidationError("Name must be under 100 characters.")  # Raise an error if validation fails
        return name  # Return the cleaned and validated data

    # Custom validator for the 'email' field
    # This adds a basic check to ensure the email contains an '@' symbol
    # It supplements Django's default email validation with a simple rule
    def clean_email(self):
        email = self.cleaned_data['email']  # Get the cleaned email value
        if '@' not in email:
            raise forms.ValidationError("Enter a valid email address.")  # Raise an error if the input is invalid
        return email  # Return the validated email

# Create custom date time input
# This class is used to customize the appearance of the date time input field
# It inherits from forms.DateTimeInput, which is a built-in form field for date time input
# It sets the input type to 'datetime-local' to display a date time picker in the browser
# It also customizes the appearance of the form field
class CustomDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'


# Define choices for contact status
contact_status_choices = [
    ('', 'Select an option'),
    ('Contact successful', 'Contact successful'),
    ('Awaiting response', 'Awaiting response'),
    ('No contact possible', 'No contact possible'),
]


# Create add record form
# This form is used to add new payment records
# It inherits from forms.ModelForm, which is a built-in form for model-based forms
# It adds fields for payment reference, first name, last name, contact method, contact date, contact status, and notes
class AddRecordForm(forms.ModelForm):
    # Define form fields
    payment_reference = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Payment Reference'}))
    first_name = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    contact_method = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Contact Method'}))
    contact_date = forms.DateTimeField(required=True, label="",
                                       widget=CustomDateTimeInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Contact Date'})
                                       )
    contact_status = forms.ChoiceField(choices=contact_status_choices, required=True, label="", widget=forms.Select(
        attrs={'class': 'form-control', 'placeholder': 'Contact Status'}))
    notes = forms.CharField(label="", widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Notes'}))

    # Define model and fields
    class Meta:
        model = Record
        fields = ('payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status',
                  'notes')


# Create update record form
# This form is used to update existing payment records
# It inherits from forms.ModelForm, which is a built-in form for model-based forms
# It adds fields for payment reference, first name, last name,
# contact method, contact date, contact status, notes, and updated by
class UpdateRecordForm(forms.ModelForm):
    # Define form fields
    payment_reference = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Payment Reference'}))
    first_name = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    contact_method = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Contact Method'}))
    contact_date = forms.DateTimeField(required=True, label="",
                                       widget=CustomDateTimeInput(
                                           attrs={'class': 'form-control', 'placeholder': 'Contact Date'})
                                       )
    contact_status = forms.ChoiceField(choices=contact_status_choices, required=True, label="", widget=forms.Select(
        attrs={'class': 'form-control', 'placeholder': 'Contact Status'}))
    notes = forms.CharField(label="", widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Notes'}))
    updated_by = forms.CharField(required=True, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Updated by:'}))

    # Define model and fields
    class Meta:
        model = Record
        fields = ('payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status',
                  'notes', 'updated_by')


# Create record search form
# This form is used to search for payment records
# It adds a field for the search term
# It also customizes the appearance of the form field
class RecordSearch(forms.Form):
    # Define form fields
    search = forms.CharField(required=False, label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search...'}))
