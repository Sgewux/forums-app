from django import template

from forums.models import PostVote

register = template.Library()

@register.filter
def already_upvoted_by(post, user):
    if PostVote.objects.filter(user=user, post=post).exists():
        if PostVote.objects.get(user=user, post=post).is_upvote():
            return 'Remove Upvote'
        else:
            return 'Upvote'
    else:
        return 'Upvote'


@register.filter
def already_downvoted_by(post, user):
    if PostVote.objects.filter(user=user, post=post).exists():
        if PostVote.objects.get(user=user, post=post).is_downvote():
            return 'Remove Downvote'
        else:
            return 'Downvote'
    else:
        return 'Downvote'