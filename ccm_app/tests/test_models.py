from django.test import TestCase
from django.contrib.auth.models import User
from datetime import datetime
from ccm_app.models import Record

class RecordModelTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='test_user', password='password123')

    def test_record_creation(self):
        # Create a Record object
        record = Record.objects.create(
            created_by=self.user,
            payment_reference='TestPayment123',
            first_name='John',
            last_name='Doe',
            contact_method='Email',
            contact_date=datetime.now(),
            contact_status='Pending',
            notes='This is a test note.',
            updated_by='Admin',
        )

        # Check if the record was created successfully
        self.assertIsNotNone(record)
        self.assertEqual(record.payment_reference, 'TestPayment123')
        self.assertEqual(record.first_name, 'John')
        self.assertEqual(record.last_name, 'Doe')
        self.assertEqual(record.contact_method, 'Email')
        self.assertEqual(record.contact_status, 'Pending')
        self.assertEqual(record.notes, 'This is a test note.')
        self.assertEqual(record.updated_by, 'Admin')

    def test_record_update(self):
        # Create a Record object
        record = Record.objects.create(
            created_by=self.user,
            payment_reference='TestPayment123',
            first_name='John',
            last_name='Doe',
            contact_method='Email',
            contact_date=datetime.now(),
            contact_status='Pending',
            notes='This is a test note.',
            updated_by='Admin',
        )

        # Update the record
        record.payment_reference = 'UpdatedPayment456'
        record.save()

        # Retrieve the updated record from the database
        updated_record = Record.objects.get(id=record.id)

        # Check if the record was updated successfully
        self.assertEqual(updated_record.payment_reference, 'UpdatedPayment456')

    def test_record_deletion(self):
        # Create a Record object
        record = Record.objects.create(
            created_by=self.user,
            payment_reference='TestPayment123',
            first_name='John',
            last_name='Doe',
            contact_method='Email',
            contact_date=datetime.now(),
            contact_status='Pending',
            notes='This is a test note.',
            updated_by='Admin',
        )

        # Delete the record
        record.delete()

        # Attempt to retrieve the deleted record from the database
        with self.assertRaises(Record.DoesNotExist):
            Record.objects.get(id=record.id)
