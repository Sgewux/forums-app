from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Forum, Post, PostVote, TooSimilarNameException

def show_forums(request):
    like = request.GET.get('q', None)
    if like:
        return render(request, 'forums/forums.html',{
            'forums_list': Forum.objects.filter(name__icontains = like)
        })
    else:
        return render(request, 'forums/forums.html', {
            'forums_list': Forum.objects.all()
        })


def show_forum(request, forum_name):
    forum = get_object_or_404(Forum, name=forum_name)
    if request.user.is_authenticated:
        member = request.user.member
        belongs = forum.members.all().contains(member)
    else:
        belongs = False
    
    if request.GET.get('q'):
        posts = forum.post_set.filter(
            Q(title__icontains = request.GET['q']) | 
            Q(content__icontains = request.GET['q'])
            ).order_by('points')
    else:
        posts = forum.post_set.order_by('-pub_date')[:15]

    return render(request, 'forums/forum.html', {
        'forum': forum,
        'posts_to_show': posts,
        'member_belongs': belongs
    })


@login_required
@require_POST
def join_forum(request, forum_name):
    forum = get_object_or_404(Forum, name=forum_name)

    if not forum.members.all().contains(request.user.member):  #  If the user is not already in forum
        forum.members.add(request.user.member)
    
    return HttpResponseRedirect(reverse('forums:show_forum', args=(forum_name,)))


@login_required
@require_POST
def leave_forum(request, forum_name):
    forum = get_object_or_404(Forum, name=forum_name)

    if forum.members.all().contains(request.user.member):  # If the user is in the forum
        forum.members.remove(request.user.member)
    
    return HttpResponseRedirect(reverse('forums:show_forum', args=(forum_name,)))


@login_required
def create_forum(request):  
    if request.method == 'POST':
        try:
            # Using get to avoid KeyError, using strip() to remove leading spaces
            new_forum_name = request.POST.get('forum_name', '').strip()
            new_forum_description = request.POST.get('description', '').strip()

            if new_forum_name and new_forum_description:  # True if both are NOT empty strings nor blank
                forum = Forum(
                    owner=request.user,
                    name=new_forum_name,
                    description=new_forum_description
                    )
                forum.save()
            
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'You must provide a name and description to the new forum'
                )
                return render(request, 'forums/create_forum.html')

        # TODO: once i switch to postgres i got to add here the logic for
        # a name or desc which uses a greather than permited lenght
        except TooSimilarNameException as e:  # Exeption declared in forums.models.py

            messages.add_message(
                request,
                messages.INFO,
                str(e)
            )
            return render(request, 'forums/create_forum.html', {})
        else:
            forum.members.add(request.user.member)  # The user who created the forum is added as a member by default
            return HttpResponseRedirect(reverse('forums:show_forum', 
            args=(new_forum_name,))
            )
    else:
        return render(request, 'forums/create_forum.html', {})


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_replies = post.comment_set.all()

    return render(request, 'forums/post.html', {
        'post': post,
        'replies': post_replies
    })


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST' and post.was_posted_by(request.user.member):
        new_content = request.POST.get('new_content', '').strip()
        if new_content:
            post.edited = True
            post.content = new_content
            post.save(update_fields=['content', 'edited'])

            return HttpResponseRedirect(
                reverse('forums:show_post', args=(post.pk,))
                )

        else:
            messages.add_message(
                request,
                messages.INFO,
                'Please provide a new content for the post.'
            )

            return render(request, 'forums/edit_post.html',{
                'post': post
            })
    else:
        if not post.was_posted_by(request.user.member):
            raise PermissionDenied  # If someone is trying to edit post that aint his
        return render(request, 'forums/edit_post.html', {
            'post': post
        })


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if post.was_posted_by(request.user.member):
        title = post.title
        forum_name = post.forum.name
        post.delete()

        messages.add_message(
            request,
            messages.INFO,
            f'Your post: {title} Was succesfully deleted.'
        )

        return HttpResponseRedirect(
            reverse('forums:show_forum', args=(forum_name,))
            )
    else:
        raise PermissionDenied  # Same as 403 forbidden

def do_vote_stuff(post, * , user, vote_record=None, upvoting=False, downvoting=False):
    '''
    Function to avoid DRY in upvote and downvote post views.
    
    Parameters:
        - post: a post object (models.post) to be upvoted/downvoted
        - User: a User object (django.contrib.auth.models.User) whos upvoting/downvoting post
        - vote_record: a postVote object (models.postVote) if the post was already upvoted/downvoted
        - upvoting: True if user wants to upvote post, else False
        - downvoting: True if user wants to downvote post, else false
    '''
    if vote_record: # Has voted before
        if vote_record.is_upvote():
            if upvoting:
                post.points -= 1  # Removing the upvote
                vote_record.delete()
            elif downvoting:
                post.points -= 2  # Removing upvote effect and downvoting

                vote_record.kind_of_vote = 'D'  # Updating vote record
                vote_record.save(update_fields=['kind_of_vote'])     

        elif vote_record.is_downvote():
            if upvoting:
                post.points += 2  # Remove downvt effects and upvoting

                vote_record.kind_of_vote = 'U'  # Updating vote record
                vote_record.save(update_fields=['kind_of_vote'])
                
            elif downvoting:
                post.points += 1  # Removing the downvote
                vote_record.delete()

    else:  # Voting first time
        if upvoting:
            post.points += 1

            # Creating vote record
            PostVote.objects.create(
            post=post,
            user=user,
            kind_of_vote='U'
        )

        elif downvoting:
            post.points -= 1

            PostVote.objects.create(
            post=post,
            user=user,
            kind_of_vote='D'
        )

    post.save(update_fields=['points'])  # Saving changes

@login_required
@require_POST
def upvote_post(request, post_id):

    # If the user upvoted the post from /forums/forum_name
    # it will be redirected there again once the vote logic has been executed
    # if the request came from /forums/post/post_id, then it will be redirected there
    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('forums:show_post', args=(post_id,))
        )
    
    post = get_object_or_404(Post, pk=post_id)

    try:
        vote_record = PostVote.objects.get(post=post, user=request.user)
    except PostVote.DoesNotExist:
        vote_record = None
    
    do_vote_stuff(post, vote_record=vote_record, user=request.user, upvoting=True)

    return HttpResponseRedirect(redirection_url)
        

@login_required
@require_POST
def downvote_post(request, post_id):
    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('forums:show_post', args=(post_id,))
        )

    post = get_object_or_404(Post, pk=post_id)
    
    try:
        vote_record = PostVote.objects.get(post=post, user=request.user)
    except PostVote.DoesNotExist:
        vote_record = None
    
    do_vote_stuff(post, vote_record=vote_record, user=request.user, downvoting=True)

    return HttpResponseRedirect(redirection_url)


@login_required
def publish_post(request, forum_name):
    forum = get_object_or_404(Forum, name=forum_name)
    if request.method == 'POST' and forum.members.contains(request.user.member):
        # Using .get() to avoid KeyError, '' as default to avoid AtributeError
        # .strip() to remove leading spaces
        title = request.POST.get('post_title', '').strip()
        content = request.POST.get('post_content', '').strip()
        if all((title, content)):  # True if both are NOT empty string nor blank
            post = Post(
                forum=forum, 
                poster=request.user.member, 
                title=title, 
                content=content
                )
            post.save()
            return HttpResponseRedirect(
                reverse('forums:show_post', args=(post.pk,))
                )

        else:
            messages.add_message(
                request, 
                messages.INFO,
                'Please fill all the fields'
                )
            return render(request, 'forums/publish_post.html', {
                'forum_name': forum.name
            })
                
    else:
        if forum.members.contains(request.user.member):  # The user has already joined the forum
            return render(request, 'forums/publish_post.html', {
            'forum_name': forum.name
        })
        else:  # The user have not join to the forum yet
            messages.add_message(
                request, 
                messages.INFO, 
                'You have to be part of this community to publish a post.'
                )
            return HttpResponseRedirect(
                reverse('forums:show_forum', args=(forum.name,))
                )