from datetime import datetime

from django.conf import settings
from django.db import models

# Create your models here.
class Tag(models.Model):
    title = models.CharField(max_length=32)

    @staticmethod
    def getOrCreate(name):
        return Tag.objects.update_or_create(title=name)[0]

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

    # We cache tags on each question to avoid needing to traverse tags table
    tags = models.CharField(max_length=256, null=True, blank=True)

    @staticmethod
    def getPosts(qid):
        return Post.objects.prefetch_related('comment_set').filter(parent_id=qid)

    @staticmethod
    def updateTag(post, tag):
        # If the tag does not already exist create a new one
        tag = Tag.getOrCreate(tag)
        PostTag.update(tag, post)

    @staticmethod
    def getRelated(post):
        # Get related questions
        return Post.objects.filter(title__icontains=post.title, post_type=PostType.QUESTION)

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    body = models.TextField()

class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    @staticmethod
    def update(tid, pid):
        PostTag.objects.update_or_create(post=pid, tag=tid)