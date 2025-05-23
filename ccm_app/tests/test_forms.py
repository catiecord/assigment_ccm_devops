from django.test import TestCase
from ccm_app.forms import SignUpForm, AddRecordForm, UpdateRecordForm, RecordSearch
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


class AddRecordFormTest(TestCase):
    def test_form_has_fields(self):
        form = AddRecordForm()
        expected_fields = ['payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status', 'notes']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    # You could also test the custom validation logic, form save functionality, etc.

class UpdateRecordFormTest(TestCase):
    def test_form_has_fields(self):
        form = UpdateRecordForm()
        expected_fields = ['payment_reference', 'first_name', 'last_name', 'contact_method', 'contact_date', 'contact_status', 'notes', 'updated_by']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    # Test updating a record, validation, and any custom methods.

class RecordSearchTest(TestCase):
    def test_form_field(self):
        form = RecordSearch()
        expected_fields = ['search']
        self.assertTrue(all(field in form.fields for field in expected_fields))

    # Test the form's search functionality if applicable.
