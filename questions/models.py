from datetime import datetime

from django.conf import settings
from django.db import models

# Create your models here.
class PostType(models.TextChoices):
    QUESTION = 'QQ', 'question'
    ANSWER = 'AA', 'answer'

class Post(models.Model):
    post_type = models.CharField(max_length=2, choices=PostType.choices)
    title = models.CharField(max_length=128, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent_id = models.ForeignKey('Post', blank=True, null=True, on_delete=models.CASCADE)

    # Need to pass function and not function() to eval at insertion time
    published_date = models.DateTimeField(default=datetime.now)
    edit_date = models.DateTimeField(null=True, blank=True)
    body = models.TextField()

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)