from datetime import datetime

from django.conf import settings
from django.db import models

# Create your models here.
class Question(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title
 
class Post(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Need to pass function and not function() to eval at insertion time
    published_date = models.DateTimeField(default=datetime.now)
    edit_date = models.DateTimeField(null=True, blank=True)
    body = models.TextField()