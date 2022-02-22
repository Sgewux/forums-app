from django.contrib import admin

from .models import Forum, Post

admin.site.register(Forum)
admin.site.register(Post)