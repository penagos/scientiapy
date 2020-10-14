from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# Ancillary information for user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=0)
    about = models.TextField(default='', null=True, blank=True)
    email_confirmed = models.DateTimeField(null=True, blank=True)


class Setting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    receive_digests = models.BooleanField(default=True)
    subscribe_all = models.BooleanField(default=False)

    @staticmethod
    def getGlobalNotifyList():
        return Setting.objects.filter(subscribe_all=True)
