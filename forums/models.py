from django.db import models
from django.contrib.auth.models import User

from members.models import Member

class Forum(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=255)
    creation_date = models.DateField('creation_date', auto_now_add=True)
    members = models.ManyToManyField(Member)

    def __str__(self):
        return f'forum: {self.name}, owner {self.owner.username}'

    # class Meta:
    #     permissions = [
    #         ('post_on_forum', 'Can post stuff on forum')
    #     ]


class Post(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    poster = models.ForeignKey(Member, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    pub_date = models.DateTimeField('pub_date', auto_now_add=True)

    def __str__(self):
        return f'tittle: {self.title}, from: {self.forum}, by: {self.poster.user.username}'

    # class Meta:
    #     permissions = [
    #         ('comment', 'Can send coments to the post')
    #     ]
