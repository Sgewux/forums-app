from django import template

from comments.models import CommentVote

register = template.Library()

@register.filter
def already_upvoted_by(comment, user):
    try:
        if CommentVote.objects.get(comment=comment, user=user).is_upvote():
            return 'Remove Upvote'
        else:
            return 'Upvote'

    except CommentVote.DoesNotExist:
        return 'Upvote'


@register.filter
def already_downvoted_by(comment, user):
    try:
        if CommentVote.objects.get(comment=comment, user=user).is_downvote():
            return 'Remove Downvote'
        else:
            return 'Downvote'

    except CommentVote.DoesNotExist:
        return 'Downvote'