from django.db import models
from django.contrib.auth.models import User

class Vote(models.Model):
    UPVOTE = 'U'
    DOWNVOTE = 'D'

    KIND_OF_VOTE_CHOICES = [
        (UPVOTE, 'upvote'),
        (DOWNVOTE, 'downvote')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kind_of_vote = models.CharField(
        max_length=1, 
        choices=KIND_OF_VOTE_CHOICES
        )

    def is_upvote(self):
        return self.kind_of_vote == Vote.UPVOTE
    
    def is_downvote(self):
        return self.kind_of_vote == Vote.DOWNVOTE

    class Meta:
        abstract = True