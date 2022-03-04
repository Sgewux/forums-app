from django.db.models import Q
from django.urls import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Forum, Post, PostVote

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
            forum = Forum(
                owner=request.user, 
                name=request.POST['forum_name'],
                description=request.POST['description']
                )
            forum.save()
        except IntegrityError as e:
            # todo: once i switch to postgres i got to add here the logic for
            # a name or desc which uses a greather than permited lenght
            return render(request, 'forums/create_forum.html', {
                'already_used_name': True
            })
        else:
            forum.members.add(request.user.member)
            return HttpResponseRedirect(reverse('forums:show_forum', 
            args=(request.POST['forum_name'],))
            )
    else:
        return render(request, 'forums/create_forum.html', {})


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'forums/post.html'


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

    if not PostVote.objects.filter(
        post__pk = post_id, 
        user = request.user
        ).exists():  # If the user has not upvoted nor downvoted this post yet

        post = get_object_or_404(Post, pk=post_id)
    
        # We create the vote record.
        PostVote.objects.create(
            post=post, user=request.user, 
            kind_of_vote='U'
            )

        # Update the post points number.
        post.points += 1
        post.save()

        return HttpResponseRedirect(redirection_url)
    else:
        post = get_object_or_404(Post, pk=post_id)
        vote_record = PostVote.objects.get(post=post, user=request.user)
        # If user has downvoted this post before
        if vote_record.is_downvote():
            post.points += 2  # Reverting the downvote effect, and then upvoting the post
            post.save()

            vote_record.kind_of_vote = 'U'  # The former vote record is updated to be an upvote
            vote_record.save()

            return HttpResponseRedirect(redirection_url)
        else:
            post.points -= 1  # If the post was already upvoted by the user, we wll remove that upvote
            post.save()

            vote_record.delete()  # Then delete the vote_recond from db

            return HttpResponseRedirect(redirection_url)
        

@login_required
@require_POST
def downvote_post(request, post_id):

    redirection_url = request.META.get(
        'HTTP_REFERER', 
        reverse('forums:show_post', args=(post_id,))
        )

    if not PostVote.objects.filter(
        post__pk = post_id, 
        user = request.user
        ).exists(): 

        post = get_object_or_404(Post, pk=post_id)
    
        PostVote.objects.create(
            post=post, user=request.user, 
            kind_of_vote='D'
            )

        post.points -= 1
        post.save()

        return HttpResponseRedirect(redirection_url)
    else:
        post = get_object_or_404(Post, pk=post_id)
        vote_record = PostVote.objects.get(post=post, user=request.user)

        if vote_record.is_upvote():
            post.points -= 2 
            post.save()

            vote_record.kind_of_vote = 'D'
            vote_record.save()

            return HttpResponseRedirect(redirection_url)
        else:
            post.points += 1
            post.save()

            vote_record.delete()

            return HttpResponseRedirect(redirection_url)