from django import template

from comments.models import CommentVote

register = template.Library()
vote_record = None

# The aproach used in this module to reduce db calls is described in detail in template_tags.vote_post_form_extras.py

@register.filter
def already_upvoted_by(comment, user):
    global vote_record
    try:
        vote_record = CommentVote.objects.get(comment=comment, user=user)
        if vote_record.is_upvote():
            return 'Remove Upvote'
        else:
            return 'Upvote'

    except CommentVote.DoesNotExist:
        vote_record = None
        return 'Upvote'


@register.filter
def already_downvoted_by(comment, user):
    global vote_record
    try:
        if vote_record.is_downvote():
            return 'Remove Downvote'
        else:
            return 'Downvote'

    except AttributeError:
        return 'Downvote'