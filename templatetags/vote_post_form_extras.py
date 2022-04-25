from django import template

from forums.models import PostVote

register = template.Library()
vote_record = None 

# Normally the following functions will be executed by template in the following order
# first: already_upvoted_by, second: already_downvoted_by. We use this behaviour to 
# reach a more efficient aproach and reducing the db calls: in already_upvoted_by we obtain the 
# vote record (if exists) and store it into vote_record global var. If record does not exists we will change the 
# prior value of vote_record to None, to ensure the was_downvoted_by function will not return the text based in 
# another vote record that is refering to another post.

# Every post will call the already_upvoted_by function at first, so will be calling the db in seek of
# vote records asosiated with it. So we can be sure the vote_record variable will be updated in every iteration 

@register.filter
def already_upvoted_by(post, user):
    global vote_record
    try: 
        # storing record into vote_record so as to have it available for was_downvoted_by
        vote_record = PostVote.objects.get(post=post, user=user)
        if vote_record.is_upvote():
            return 'Remove Upvote'
        else:
            return 'Upvote'

    except PostVote.DoesNotExist:
        vote_record = None  # Setting record to None to make sure was_downvoted_by will work as expected
        return 'Upvote'


@register.filter
def already_downvoted_by(post, user):
    global vote_record
    try:
        if vote_record.is_downvote():  # Will throw AttributeError if vote_record is None
            return 'Remove Downvote'
        else:
            return 'Downvote'

    except AttributeError:  # vote_record was None, that means user has not voted this post yet
        return 'Downvote'