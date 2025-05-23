from django.db import models
from django.contrib.auth.models import User


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
    contact_date = models.DateTimeField()
    contact_status = models.CharField(max_length=60)
    notes = models.TextField()
    updated_by = models.CharField(max_length=50, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
