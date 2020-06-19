from django.contrib import admin
from .models import Post, Question

# Register your models here.
admin.site.register(Question)
admin.site.register(Post)