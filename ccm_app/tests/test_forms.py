from django.test import TestCase
from ccm_app.forms import SignUpForm, AddRecordForm, UpdateRecordForm, RecordSearch , RecordForm
from django.contrib.auth.models import User
from django import forms


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        form = SignUpForm()
        expected_fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    def test_form_valid(self):
        form = SignUpForm(data={
            'username': 'test_user',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123.',
            'password2': 'password123.'
        })
        self.assertTrue(form.is_valid())
    def test_form_invalid(self):
        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)

    def test_clean_email(self):
        form = SignUpForm(data={
            'username': 'test_user',
            'email': '',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['This field is required.'])

    def test_clean_username(self):
        form = SignUpForm(data={
            'username': '',
            'email': 'user_o@he.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

    def test_username_already_exists(self):
        user = User.objects.create(username='test_user', password='password123')
        form = SignUpForm(data={
            'username': 'test_user',
            'email': '',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['Username already exists.'])
    def test_email_already_exists(self):
        User.objects.create_user(username='existing_user', email='test@example.com', password='password123')
        form = SignUpForm(data={
            'username': 'new_user',
            'email': 'test@example.com',  # same email as existing user
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123.',
            'password2': 'password123.'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Email address is already in use.'])
    def test_signup_form_email_already_exists(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        form = SignUpForm(data={
            'username': 'newuser',
            'email': 'existing@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'password123.',
            'password2': 'password123.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Email address is already in use.', form.errors['email'])



class AddRecordFormTest(TestCase):
    def test_form_has_fields(self):
        form = AddRecordForm()
        expected_fields = ['payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status', 'notes']
        self.assertTrue(all(field in form.fields for field in expected_fields))
        def test_record_form_invalid_email(self):
            class EmailRecordForm(RecordForm):
                email = forms.CharField()  # override for testing clean_email if not already in the form

            form = EmailRecordForm(data={
                'payment_reference': 'PAY123',
                'first_name': 'Test',
                'last_name': 'User',
                'contact_method': 'Email',
                'contact_date': '2025-06-01T10:00',
                'contact_status': 'Contact successful',
                'notes': 'Sample notes',
                'email': 'invalidemail'  # invalid email, missing '@'
            })
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)
            self.assertIn('Enter a valid email address.', form.errors['email'])

    # You could also test the custom validation logic, form save functionality, etc.

class UpdateRecordFormTest(TestCase):
    def test_form_has_fields(self):
        form = UpdateRecordForm()
        expected_fields = ['payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status', 'notes', 'updated_by']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    # Test updating a record, validation, and any custom methods.
class RecordFormCleanNameTest(TestCase):
    def test_clean_name_too_long(self):
        class TestFormWithNameField(RecordForm):
            name = forms.CharField()

            def clean_name(self):
                name = self.cleaned_data['name']
                if len(name) > 100:
                    raise forms.ValidationError("Name must be under 100 characters.")
                return name

        form = TestFormWithNameField(data={
            'name': 'x' * 101,  # too long
            'payment_reference': 'ref',
            'first_name': 'a',
            'last_name': 'b',
            'contact_method': 'email',
            'contact_date': '2024-01-01T12:00',
            'contact_status': 'Contact successful',
            'notes': 'test'
        })

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'][0], "Name must be under 100 characters.")

class RecordSearchTest(TestCase):
    def test_form_field(self):
        form = RecordSearch()
        expected_fields = ['search']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    # Test the form's search functionality if applicable.
    
