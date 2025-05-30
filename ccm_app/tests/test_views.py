from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ccm_app.models import Record
from django.utils import timezone
from unittest.mock import patch

class ViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.staff_user = User.objects.create_user(username='adminuser', password='adminpass', is_staff=True)
        self.record = Record.objects.create(
            payment_reference='PAY123456',
            first_name='Test',
            last_name='User',
            contact_method='Email',
            contact_date=timezone.now(),
            contact_status='Pending',
            notes='Initial contact.',
            created_by=self.staff_user,
            updated_by='adminuser',
            updated_at=timezone.now()
        )

    # Authentication & Session Tests
    def test_home_get(self):
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/login/?next=/')  

    def test_handle_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass'}, follow=True)
        self.assertContains(response, 'You have been logged in!')

    def test_handle_login_user_does_not_exist_message(self):
        response = self.client.post(reverse('login'), {'username': 'nonexistentuser', 'password': 'irrelevant'}, follow=True)
        self.assertContains(response, 'User does not exist.')

    def test_handle_login_existing_user_wrong_password_message(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'}, follow=True)
        self.assertContains(response, 'Incorrect password. Please try again.')

    def test_handle_login_inactive_message(self):
        inactive_user = User.objects.create_user(username='inactiveuser', password='testpass', is_active=False)
        response = self.client.post(reverse('login'), {'username': 'inactiveuser', 'password': 'testpass'}, follow=True)
        self.assertContains(response, 'Account is inactive. Contact admin.')

    def test_logout_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertContains(response, 'You have been logged out!')

    # Registration Tests
    def test_register_user_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_user_post_valid(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Test', 'last_name': 'User', 'username': 'newuser',
            'email': 'newuser@example.com', 'password1': 'StrongPass123!', 'password2': 'StrongPass123!'} )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))



    def test_register_user_post_invalid(self):
        response = self.client.post(reverse('register'), {
            'username': '', 'password1': 'password', 'password2': 'different_password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_user_post_invalid_messages(self):
        response = self.client.post(reverse('register'), {
            'username': '', 'password1': 'short', 'password2': 'mismatch'}, follow=True)
        self.assertContains(response, 'Username:')

    def test_register_user_authentication_fails(self):
        self.client.logout()
        response = self.client.post(reverse('register'), {
            'first_name': 'Fail', 'last_name': 'Login', 'username': 'failuser',
            'email': 'fail@example.com', 'password1': 'StrongPass123!', 'password2': 'StrongPass123!'}, follow=True)
        self.assertContains(response, 'You have been registered!')

    @patch('ccm_app.views.authenticate', return_value=None)
    def test_register_user_post_authentication_fail(self, mock_auth):
        response = self.client.post(reverse('register'), {
            'first_name': 'Fail', 'last_name': 'Login', 'username': 'faillogin',
            'email': 'fail@example.com', 'password1': 'SomeStrongPassword123!', 'password2': 'SomeStrongPassword123!'}, follow=True)
        self.assertContains(response, 'Failed to log in after registration.')

    # Record Tests
    def test_add_record_success(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(reverse('add_record'), {
            'payment_reference': 'REF123', 'first_name': 'Jane', 'last_name': 'Doe',
            'contact_method': 'Phone', 'contact_date': timezone.now(),
            'contact_status': 'Completed', 'notes': 'Test note'}, follow=True)
        self.assertContains(response, 'Record has been added!')

    def test_add_record_post_invalid(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_record'), {'first_name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_record.html')

    def test_add_record_post_invalid_message(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_record'), {'payment_reference': ''}, follow=True)
        self.assertContains(response, 'Error adding record - please try again...')

    def test_payment_record_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('payment_record', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_payment_record_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('payment_record', args=[self.record.id]))
        self.assertRedirects(response, f'/login/?next={reverse("payment_record", args=[self.record.id])}')


    def test_update_record_authenticated_get(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('update_record', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_update_record_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('update_record', args=[self.record.id]))
        self.assertRedirects(response, f'/login/?next={reverse("update_record", args=[self.record.id])}')


    def test_update_record_success(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(reverse('update_record', args=[self.record.id]), {
            'payment_reference': 'UPDATED123', 'first_name': 'Updated', 'last_name': 'User',
            'contact_method': 'Email', 'contact_date': timezone.now(),
            'contact_status': 'Completed', 'notes': 'Updated note'}, follow=True)
        self.assertContains(response, 'Record has been updated!')

    def test_update_record_post_invalid_message(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('update_record', args=[self.record.id]), {
            'payment_reference': ''}, follow=True)
        self.assertContains(response, 'Error updating record - please try again...')

    def test_delete_record_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('delete_record', args=[self.record.id]))
        self.assertRedirects(response, f'/login/?next={reverse("delete_record", args=[self.record.id])}')



    def test_delete_record_non_staff(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('delete_record', args=[self.record.id]))
        self.assertRedirects(response, '/login/?next=/user_management/')

    def test_delete_record_success(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('delete_record', args=[self.record.id]), follow=True)
        self.assertContains(response, 'Record has been deleted!')

    # User Management Tests
    def test_user_management_requires_login(self):
        response = self.client.get(reverse('user_management'), follow=True)
        self.assertRedirects(response, f'/login/?next={reverse("user_management")}')

        self.assertContains(response, 'You must be logged in to view users!')

    def test_user_management_requires_staff(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_management'))
        self.assertRedirects(response, '/login/?next=/user_management/')

        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)

    def test_user_active_status_toggle(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('user_active_status', args=[self.staff_user.id]))
        self.assertRedirects(response, reverse('user_management'))
        self.staff_user.refresh_from_db()
        self.assertFalse(self.staff_user.is_active)

    def test_user_active_status_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('user_active_status', args=[self.staff_user.id]))
        self.assertRedirects(response, f'/login/?next={reverse("user_active_status", args=[self.staff_user.id])}')



    def test_user_active_status_non_staff(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_active_status', args=[self.staff_user.id]))
        self.assertRedirects(response, f'/login/?next={reverse("user_active_status", args=[self.staff_user.id])}')



    def test_user_active_status_self_toggle_denied(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('user_active_status', args=[self.staff_user.id]))
        self.assertRedirects(response, reverse('user_management'))
        self.staff_user.refresh_from_db()
        self.assertTrue(self.staff_user.is_active)

    def test_user_active_status_message(self):
        self.client.login(username='adminuser', password='adminpass')
        user = User.objects.create_user(username='targetuser', password='pass')
        response = self.client.get(reverse('user_active_status', args=[self.staff_user.id]), follow=True)
        self.assertContains(response, "account has been deactivated.")

    def test_user_active_status_user_not_found(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('user_active_status', args=[99999]), follow=True)
        self.assertRedirects(response, reverse('user_management'))
        self.assertContains(response, "User not found.")

    # Search and Audit Logs
    def test_search_results_requires_login(self):
        response = self.client.post(reverse('search_results'), {'searched': 'Test'}, follow=True)
        self.assertRedirects(response, f'/login/?next={reverse("search_results")}')

        self.assertContains(response, 'You must be logged in to search records!')

    def test_search_results_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('search_results'), {'searched': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")

    def test_search_results_get_message(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('search_results'), follow=True)
        self.assertContains(response, 'Please use the search form to submit your query.')

    def test_search_results_match_displayed(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(reverse('search_results'), {'searched': 'Test'}, follow=True)
        self.assertContains(response, 'Test')

    def test_audit_logs_render(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('audit_logs'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.record.payment_reference)

    def test_audit_logs_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('audit_logs'))
        self.assertRedirects(response, f'/login/?next={reverse("audit_logs")}')


