from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# This is the model file for the ccm_app app.
# It defines the database schema for the app
# It defines the Record model
# It defines the fields for the Record model
# It defines the data types for the fields
# It defines the constraints for the fields
# It defines the relationships between the fields
class Record(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    payment_reference = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_method = models.CharField(max_length=60)
    contact_date = models.DateTimeField(default=timezone.now,)
    contact_status = models.CharField(max_length=60)
    notes = models.TextField()
    updated_by = models.CharField(max_length=50, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('REGISTER', 'User Registration'),
        ('PROMOTE', 'Admin Promotion'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"