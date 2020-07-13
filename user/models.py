from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# Ancillary information for user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=0)
    email_confirmed = models.DateTimeField(null=True, blank=True)