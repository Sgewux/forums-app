from django import template

from forums.models import PostVote

register = template.Library()
vote_record = None

@register.filter
def already_upvoted_by(post, user):
    global vote_record
    try:
        vote_record = PostVote.objects.get(post=post, user=user)
        if vote_record.is_upvote():
            return 'Remove Upvote'
        else:
            return 'Upvote'

    except PostVote.DoesNotExist:
        vote_record = None
        return 'Upvote'


@register.filter
def already_downvoted_by(post, user):
    global vote_record
    try:
        if vote_record.is_downvote():
            return 'Remove Downvote'
        else:
            return 'Downvote'

    except AttributeError:
        return 'Downvote'