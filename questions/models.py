from datetime import datetime
from functools import reduce

from django.conf import settings
from django.db import models
from django.db.models import Count, Q

# Create your models here.
class Tag(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)

    @staticmethod
    def getOrCreate(name):
        return Tag.objects.update_or_create(title=name)[0]

class PostTag(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    @staticmethod
    def update(tid, pid):
        PostTag.objects.update_or_create(post=pid, tag=tid)

    @staticmethod
    def getAllTags():
        return PostTag.objects.values('tag__title', 'tag__description').annotate(posts=Count('post')).order_by('-posts')

class PostType(models.TextChoices):
    QUESTION = 'QQ', 'question'
    ANSWER = 'AA', 'answer'

class Post(models.Model):
    post_type = models.CharField(max_length=2, choices=PostType.choices)
    title = models.CharField(max_length=128, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_edit = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='author_editid')
    parent_id = models.ForeignKey('Post', blank=True, null=True, on_delete=models.CASCADE)
    accepted_id = models.ForeignKey('Post', blank=True, null=True, on_delete=models.CASCADE, related_name='accepted_idfk')

    # Need to pass function and not function() to eval at insertion time
    published_date = models.DateTimeField(default=datetime.now)
    edit_date = models.DateTimeField(null=True, blank=True)
    body = models.TextField()

    # We cache tags on each question to avoid needing to traverse tags table
    tags = models.CharField(max_length=256, null=True, blank=True)

    # Cache vote count on each question for easy access
    votes = models.IntegerField(default=0)

    @staticmethod
    def getPosts(qid):
        return Post.objects.prefetch_related('comment_set').filter(parent_id=qid)

    @staticmethod
    def updateTag(post, tag):
        # If the tag does not already exist create a new one
        tag = Tag.getOrCreate(tag)
        PostTag.update(tag, post)

    @staticmethod
    def removeTags(post, tags):
        tags = PostTag.objects.filter(post=post)

        for tag in list(tags):
            if tag.tag.title not in tags:
                PostTag.objects.filter(pk=tag.id).delete()

    @staticmethod
    def getRelated(post):
        # Get related questions by either title or tag
        # TODO: remove this once DB data has been normalized
        keywords = post.title.split(' ')

        if post.tags is not None:
            if isinstance(post.tags, list):
                keywords += post.tags
            else:
                keywords += post.tags.split(',')

        return Post.objects.filter(reduce(lambda x, y: x | y, [Q(title__icontains=word) for word in keywords]), post_type=PostType.QUESTION).annotate(answers=Count('post'))[:10]

    @staticmethod
    def getHotQuestions():
        # Get "hot" questions
        return Post.objects.filter(post_type=PostType.QUESTION).annotate(answers=Count('post')).order_by('-answers')[:5]

    @staticmethod
    def getRecentQuestions():
        # Get new questions
        return Post.objects.filter(post_type=PostType.QUESTION).annotate(answers=Count('post')).order_by('-published_date')[:5]

    @staticmethod
    def getUnansweredQuestions():
        # Get unanswered questions
        return Post.objects.filter(post_type=PostType.QUESTION).annotate(answers=Count('post')).order_by('answers')[:5]

    @staticmethod
    def getRecentQuestionsByUser(uid, count):
        # Get X most recent questions by user
        return Post.objects.filter(post_type=PostType.QUESTION, author=uid).annotate(answers=Count('post')).order_by('-published_date')[:count]

    @staticmethod
    def getRecentAnswersByUser(uid, count):
        # Get X most recent answers by user
        return Post.objects.filter(post_type=PostType.ANSWER, author=uid).order_by('-published_date')[:count]

class Vote(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)
    body = models.TextField()