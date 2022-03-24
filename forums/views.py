from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
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


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'forums/post.html'
    pk_url_kwarg = 'post_id'  # kwarg to be used in url


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

    if not PostVote.objects.filter(
        post = post, 
        user = request.user
        ).exists():  # If the user has not upvoted nor downvoted this post yet
    
        # We create the vote record.
        PostVote.objects.create(
            post=post, user=request.user, 
            kind_of_vote='U'
            )

        # Update the post points number.
        post.points += 1
        post.save(update_fields=['points'])

        return HttpResponseRedirect(redirection_url)
    else:
        vote_record = PostVote.objects.get(post=post, user=request.user)
        # If user has downvoted this post before
        if vote_record.is_downvote():
            post.points += 2  # Reverting the downvote effect, and then upvoting the post
            post.save(update_fields=['points'])

            vote_record.kind_of_vote = 'U'  # The former vote record is updated to be an upvote
            vote_record.save(update_fields=['kind_of_vote'])

            return HttpResponseRedirect(redirection_url)
        else:
            post.points -= 1  # If the post was already upvoted by the user, we wll remove that upvote
            post.save(update_fields=['points'])

            vote_record.delete()  # Then delete the vote_recond from db

            return HttpResponseRedirect(redirection_url)
        

@login_required
@require_POST
def downvote_post(request, post_id):

    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('forums:show_post', args=(post_id,))
        )

    post = get_object_or_404(Post, pk=post_id)

    if not PostVote.objects.filter(
        post__pk = post_id, 
        user = request.user
        ).exists(): 
    
        PostVote.objects.create(
            post=post, user=request.user, 
            kind_of_vote='D'
            )

        post.points -= 1
        post.save(update_fields=['points'])

        return HttpResponseRedirect(redirection_url)
    else:
        vote_record = PostVote.objects.get(post=post, user=request.user)

        if vote_record.is_upvote():
            post.points -= 2 
            post.save(update_fields=['points'])

            vote_record.kind_of_vote = 'D'
            vote_record.save(update_fields=['kind_of_vote'])

            return HttpResponseRedirect(redirection_url)
        else:
            post.points += 1
            post.save(update_fields=['points'])

            vote_record.delete()

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