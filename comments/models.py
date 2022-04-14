from django.db import models
from django.db.models import Q, CheckConstraint

from abstract_models.vote import Vote
from forums.models import Post
from members.models import Member


class Comment(models.Model):
    commenter = models.ForeignKey(Member, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    in_reply_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, 
        null=True
        )
    content = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    pub_date = models.DateTimeField('pub_date', auto_now_add=True)
        
    class Meta:
        constraints = [
            # Ensures constraint on DB level, raises IntegrityError (500 on debug=False)
            CheckConstraint(
                check= ~(Q(post=None) & Q(in_reply_to=None)), 
                name='check_is_linked_to_anything',
            ),
        ]

class CommentVote(Vote):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'comment'], 
                name='unique_vote_per_user_for_comments'
                )
        ]