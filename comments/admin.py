from django.contrib import admin

from comments.models import Comment

class CommentAdmin(admin.ModelAdmin):
    exclude = ['post']

admin.site.register(Comment, CommentAdmin)