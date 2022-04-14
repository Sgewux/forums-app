from django.shortcuts import render, get_object_or_404

from . models import Comment

def show_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    commenter_username = comment.commenter.user.username
    replies = comment.comment_set.all()

    return render(request, 'comments/comment.html', {
        'comment': comment,
        'commenter_username': commenter_username,
        'replies': replies
    })