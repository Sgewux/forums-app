from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from . models import Comment, CommentVote

def show_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    commenter_username = comment.commenter.user.username
    replies = comment.comment_set.all()

    return render(request, 'comments/comment.html', {
        'comment': comment,
        'commenter_username': commenter_username,
        'replies': replies
    })

def do_vote_stuff(comment, * , user, vote_record=None, upvoting=False, downvoting=False):
    '''
    Function to avoid DRY in upvote and downvote comment views.
    
    Parameters:
        - Comment: a comment object (models.Comment) to be upvoted/downvoted
        - User: a User object (django.contrib.auth.models.User) whos upvoting/downvoting comment
        - vote_record: a CommentVote object (models.CommentVote) if the comment was already upvoted/downvoted
        - upvoting: True if user wants to upvote comment, else False
        - downvoting: True if user wants to downvote comment, else false
    '''
    if vote_record: # Has voted before
        if vote_record.is_upvote():
            if upvoting:
                comment.points -= 1  # Removing the upvote
                vote_record.delete()
            elif downvoting:
                comment.points -= 2  # Removing upvote effect and downvoting

                vote_record.kind_of_vote = 'D'  # Updating vote record
                vote_record.save(update_fields=['kind_of_vote'])     

        elif vote_record.is_downvote():
            if upvoting:
                comment.points += 2  # Remove downvt effects and upvoting

                vote_record.kind_of_vote = 'U'  # Updating vote record
                vote_record.save(update_fields=['kind_of_vote'])
                
            elif downvoting:
                comment.points += 1  # Removing the downvote
                vote_record.delete()

    else:  # Voting first time
        if upvoting:
            comment.points += 1

            # Creating vote record
            CommentVote.objects.create(
            comment=comment,
            user=user,
            kind_of_vote='U'
        )

        elif downvoting:
            comment.points -= 1

            CommentVote.objects.create(
            comment=comment,
            user=user,
            kind_of_vote='D'
        )

    comment.save(update_fields=['points'])  # Saving changes


@login_required
@require_POST
def upvote_comment(request, comment_id):
    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('comments:show_comment', args=(comment_id,))
        )
    comment = get_object_or_404(Comment, pk=comment_id)

    try:
        vote_record = CommentVote.objects.get(comment=comment, user=request.user)
    except CommentVote.DoesNotExist:
        vote_record=None

    do_vote_stuff(comment, vote_record=vote_record, user=request.user, upvoting=True)

    return HttpResponseRedirect(redirection_url)


@login_required
@require_POST
def downvote_comment(request, comment_id):
    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('comments:show_comment', args=(comment_id,))
        )
    comment = get_object_or_404(Comment, pk=comment_id)

    try:
        vote_record = CommentVote.objects.get(comment=comment, user=request.user)
    except CommentVote.DoesNotExist:
        vote_record=None

    do_vote_stuff(comment, vote_record=vote_record, user=request.user, downvoting=True)

    return HttpResponseRedirect(redirection_url)
