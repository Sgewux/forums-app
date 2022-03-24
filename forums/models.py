import re

from django.db import models
from django.contrib.auth.models import User

from members.models import Member
from forum_app.abstract_models import Vote


class TooSimilarNameException(Exception):
    '''
    We dont want forums with very similar names. For example, names like:
    -tiktoknews
    -TikTokNews
    -tik_tok_news
    Are too similar, therefore, we can guess that their content is very related.
    This exeption is meant to be raised by the .save() method of Forum model class
    when the user tries to create a forum with a name that is very similar to an existent one.

    The logic that determines if a name is very similar to another is inside that method.
    '''
    def __init__(self, name):
        super().__init__(
            f'We already have forums with names very similar to "{name}". Try with another one'
            )

class Forum(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15, unique=True)
    real_name = models.CharField(max_length=15, null=True)
    description = models.CharField(max_length=255)
    creation_date = models.DateField('creation_date', auto_now_add=True)
    members = models.ManyToManyField(Member)

    def __str__(self):
        return f'forum: {self.name}, owner {self.owner.username}'

    def save(self, *args, **kwargs):
        '''
        This method is being overriden because whe want to ensure that the new forum's name is not
        too similar to an already existent one. In order to achieve this, we are removing everything
        that is NOT a letter (_, - , ; , [spaces] , [actual commas], numbers) using regex. This
        will give us a "real name" signature, for example:
        -tiktoknews
        -TikTokNews
        -tik_tok_news
        if we remove the underscores from the second one, and compare the lowecase versions of those 3
        names (without any value that is not a letter) we will realize that they are equal.

        If we find that there is at least one forum with the same "ral_name" in the db, we will not
        add the new one to the db and raise a TooSimilarNameException
        '''
        
        self.real_name = re.sub('[^a-zA-Z]', '', self.name).lower()
        if Forum.objects.filter(real_name=self.real_name).exists():
            raise TooSimilarNameException(self.name)

        super().save(*args, **kwargs)


class Post(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    poster = models.ForeignKey(Member, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    edited = models.BooleanField(default=False)
    pub_date = models.DateTimeField('pub_date', auto_now_add=True)

    def __str__(self):
        return f'tittle: {self.title}, from: {self.forum}, by: {self.poster.user.username}'

    def was_posted_by(self, member):
        '''Utility function to know if a given member was the one who post this post'''
        return self.poster == member

    # class Meta:
    #     permissions = [
    #         ('comment', 'Can send coments to the post')
    #     ]


class PostVote(Vote):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'], 
                name='unique_vote_per_post'
                )
        ]