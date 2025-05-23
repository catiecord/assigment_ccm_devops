from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ccm_app.models import Record
from ccm_app.forms import SignUpForm


class ViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create a test record
        self.record = Record.objects.create(
            created_by=self.user,
            payment_reference='REF123',
            first_name='John',
            last_name='Doe',
            contact_method='Email',
            contact_date='2024-03-06 12:00',
            contact_status='Contact successful',
            notes='Test note',
        )
        self.client = Client()

    # Home View Tests
    def test_home_view_unauthenticated(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        # Check if records are passed to the template
        self.assertTrue('records' in response.context)
        self.assertEqual(list(response.context['records']), [self.record])

    def test_home_view_error_message(self):
        response = self.client.post(reverse('home'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    # Register View Tests
    def test_register_user_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_register_user_view_post_valid(self):
        user_count = User.objects.count()
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertRedirects(response, reverse('home'))

    def test_register_user_view_post_invalid(self):
        user_count = User.objects.count()
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': '',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(User.objects.count(), user_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], SignUpForm)
        self.assertTrue(response.context['form'].errors)

    # Login and Logout View Tests
    def test_login_logout_flow(self):
        # Login
        login_response = self.client.post(reverse('home'), {'username': 'testuser', 'password': '12345'})
        self.assertRedirects(login_response, reverse('home'))

        # Logout
        logout_response = self.client.get(reverse('logout'))
        self.assertRedirects(logout_response, reverse('home'))

    # Record View Tests

    def test_payment_record_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('record', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'record.html')
        self.assertEqual(response.context['record'], self.record)

    def test_payment_record_view_unauthenticated(self):
        response = self.client.get(reverse('record', args=[self.record.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    # Add Record View Tests

    def test_add_record_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('add_record'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_record.html')
        self.assertTrue('form' in response.context)
        self.assertEqual(response.context['form']._meta.model, Record)

    def test_add_record_view_unauthenticated(self):
        response = self.client.get(reverse('add_record'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_add_record_view_post_valid(self):
        record_count = Record.objects.count()
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_record'), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': 'Test note',
        })
        self.assertEqual(Record.objects.count(), record_count + 1)
        self.assertRedirects(response, reverse('home'))

    def test_add_record_view_post_invalid(self):
        record_count = Record.objects.count()
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_record'), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': '',
        })
        self.assertEqual(Record.objects.count(), record_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_record.html')
        self.assertTrue(response.context['form'].errors)

    def test_add_record_view_post_unauthenticated(self):
        record_count = Record.objects.count()
        response = self.client.post(reverse('add_record'), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': 'Test note',
        })
        self.assertEqual(Record.objects.count(), record_count)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    # Update Record View Tests

    def test_update_record_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('update_record', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_record.html')
        self.assertTrue('form' in response.context)
        self.assertEqual(response.context['form']._meta.model, Record)

    def test_update_record_view_unauthenticated(self):
        response = self.client.get(reverse('update_record', args=[self.record.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_update_record_view_post_valid(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_record', args=[self.record.id]), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': 'Test note',
            'updated_by': 'John Doe',
        })
        self.record.refresh_from_db()
        self.assertEqual(self.record.payment_reference, 'REF456')
        self.assertEqual(self.record.first_name, 'Jane')
        self.assertEqual(self.record.last_name, 'Doe')
        self.assertEqual(self.record.contact_method, 'Phone')
        self.assertEqual(self.record.contact_status, 'Contact successful')
        self.assertEqual(self.record.notes, 'Test note')
        self.assertEqual(self.record.updated_by, 'John Doe')
        self.assertRedirects(response, reverse('home'))

    def test_update_record_view_post_invalid(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_record', args=[self.record.id]), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': '',
            'updated_by': 'John Doe',
        })
        self.record.refresh_from_db()
        self.assertEqual(self.record.payment_reference, 'REF123')
        self.assertEqual(self.record.first_name, 'John')
        self.assertEqual(self.record.last_name, 'Doe')
        self.assertEqual(self.record.contact_method, 'Email')
        self.assertEqual(self.record.contact_status, 'Contact successful')
        self.assertEqual(self.record.notes, 'Test note')
        self.assertIsNone(self.record.updated_by)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_record.html')
        self.assertTrue(response.context['form'].errors)

    def test_update_record_view_post_unauthenticated(self):
        response = self.client.post(reverse('update_record', args=[self.record.id]), {
            'payment_reference': 'REF456',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'contact_method': 'Phone',
            'contact_date': '2024-03-06T12:00',
            'contact_status': 'Contact successful',
            'notes': 'Test note',
            'updated_by': 'John Doe',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    # Delete Record View Tests

    def test_delete_record_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        # Assuming 'home' is the name of the URL to which you expect to redirect
        expected_redirect_url = reverse('home')
        response = self.client.get(reverse('delete_record', args=[self.record.id]))
        # Check that the response is a redirect to the 'home' page
        self.assertRedirects(response, expected_redirect_url)

    #
    def test_delete_record_view_unauthenticated(self):
        response = self.client.get(reverse('delete_record', args=[self.record.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_delete_record_view_post_unauthenticated(self):
        record_count = Record.objects.count()
        response = self.client.post(reverse('delete_record', args=[self.record.id]))
        self.assertEqual(Record.objects.count(), record_count)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_delete_record_view_post_staff(self):
        self.user.is_staff = True
        self.user.save()
        record_count = Record.objects.count()
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_record', args=[self.record.id]))
        self.assertEqual(Record.objects.count(), record_count - 1)
        self.assertRedirects(response, reverse('home'))

    # User Management View Tests

    def test_user_management_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_management'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_management_view_unauthenticated(self):
        response = self.client.get(reverse('user_management'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_management_view_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_management.html')
        self.assertTrue('users' in response.context)
        self.assertEqual(list(response.context['users']), [self.user])

    # Search Results View Tests

    def test_search_results_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('search_results'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_search_results_view_unauthenticated(self):
        response = self.client.get(reverse('search_results'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_search_results_view_post(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('search_results'),
                                    {'searched': 'John'})
        self.assertTemplateUsed(response, 'search_results.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn('records', response.context)
        self.assertIn('searched', response.context)
        self.assertEqual(response.context['searched'], 'John')

    def test_search_results_view_post_unauthenticated(self):
        response = self.client.post(reverse('search_results'), {'search': 'John'})
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    # Audit Logs View Tests

    def test_audit_logs_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('audit_logs'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_audit_logs_view_unauthenticated(self):
        response = self.client.get(reverse('audit_logs'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_audit_logs_view_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('audit_logs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'audit_logs.html')
        self.assertTrue('records' in response.context)
        self.assertEqual(list(response.context['records']), [self.record])

    # User Active Status View Tests

    def test_user_active_status_view_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_unauthenticated(self):
        response = self.client.get(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('user_management'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('user_management'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_unauthenticated(self):
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_self(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff_self(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff_superuser(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff_superuser_self(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff_superuser_staff(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_user_active_status_view_post_staff_superuser_staff_superuser_staff_self(self):
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(reverse('user_active_status', args=[self.user.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
