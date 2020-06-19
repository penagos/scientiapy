from django.db import models

# Create your models here.
class Question(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title;
 
class Post(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = models.TextField()