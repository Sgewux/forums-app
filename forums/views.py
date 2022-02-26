from django.db.models import Q
from django.urls import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from members.models import Member
from .models import Forum

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
def join_forum(request, forum_name):
    forum = get_object_or_404(Forum, name=forum_name)

    if not forum.members.all().contains(request.user.member):  #  If the user is not already in forum
        forum.members.add(request.user.member)
    
    return HttpResponseRedirect(reverse('forums:show_forum', args=(forum_name,)))


@login_required
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