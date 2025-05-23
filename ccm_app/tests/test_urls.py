from django.test import TestCase
from django.urls import reverse, resolve
from ccm_app import views

class UrlsTest(TestCase):
    # Test that the correct view is called for each URL
    def test_home_url(self):
        url = reverse('home')
        self.assertEqual(resolve(url).func, views.home)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, views.logout_user)

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register_user)

    def test_payment_record_url(self):
        url = reverse('record', args=[1])
        self.assertEqual(resolve(url).func, views.payment_record)

    def test_delete_record_url(self):
        url = reverse('delete_record', args=[1])
        self.assertEqual(resolve(url).func, views.delete_record)

    def test_update_record_url(self):
        url = reverse('update_record', args=[1])
        self.assertEqual(resolve(url).func, views.update_record)

    def test_add_record_url(self):
        url = reverse('add_record')
        self.assertEqual(resolve(url).func, views.add_record)

    def test_user_management_url(self):
        url = reverse('user_management')
        self.assertEqual(resolve(url).func, views.user_management)

    def test_search_results_url(self):
        url = reverse('search_results')
        self.assertEqual(resolve(url).func, views.search_results)

    def test_user_active_status_url(self):
        url = reverse('user_active_status', args=[1])
        self.assertEqual(resolve(url).func, views.user_active_status)

    def test_audit_logs_url(self):
        url = reverse('audit_logs')
        self.assertEqual(resolve(url).func, views.audit_logs)
