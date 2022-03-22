from django.urls import reverse
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from forums.models import Post
from .models import Member

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('members:feed'))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'Unsuccesfull login, try again!'
            )
            return render(request, 'members/login.html', {})
    else:
        return render(request, 'members/login.html', {})


def singup_user(request):
    if not request.user.is_authenticated:  #  We dont want an already logged user to create accounts
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            password_again = request.POST.get('password_again', '').strip()

            if all((username, password, password_again)):  # The user didnt leave blank fields
                if password == password_again:  #  The user filled the form correctly
                    user = User(username=username)
                    user.set_password(password)
                    try:
                        user.save()
                    except IntegrityError:
                        messages.add_message(
                            request,
                            messages.INFO,
                            'That user already exists!'
                        )
                        return render(request, 'members/singup.html', {})
                    else:
                        Member.objects.create(user=user, bio='Hello everyone, i\'m using ForumsApp!')
                        login(request, user)
                        return HttpResponseRedirect(reverse('members:feed'))
                else:
                    messages.add_message(
                        request,
                        messages.INFO,
                        'Passwords were not equal!'
                    )
                    return render(request, 'members/singup.html', {})
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    'Please fill all the fields'
                )
                return render(request, 'members/singup.html', {})
        else:
            return render(request, 'members/singup.html', {})
    else:
        return HttpResponseRedirect(reverse('members:feed'))


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('forums:forums_home'))


@login_required
def show_profile(request):
    return render(request, 'members/profile.html', {
        'user_name': request.user.username,
        'bio_content':request.user.member.bio,
        'is_owner': True
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        member = request.user.member
        new_bio = request.POST.get('new_bio', '').strip()
        if new_bio:
            member.bio = new_bio 
            member.save(update_fields=['bio'])
        else:
            messages.add_message(
                request,
                messages.INFO,
                'Please provide a new Bio'
            )
            return render(request, 'members/edit_profile.html', {})

        return HttpResponseRedirect(reverse('members:profile'))
    else:
        return render(request, 'members/edit_profile.html', {
            'old_bio': request.user.member.bio
        })


@login_required
def delete_account(request):
    if request.method == 'POST':
        if request.user.check_password(request.POST.get('password')):
            former_user = request.user
            logout(request)
            former_user.delete()

            return HttpResponseRedirect(reverse('forums:forums_home'))
        
        else:
            messages.add_message(
                request,
                messages.INFO,
                'You wrote the wrong password! seems like you dont really want to leave...'
            )
            return render(request, 'members/delete_account.html', {})

    else:
        return render(request, 'members/delete_account.html',{})


@login_required
def user_feed(request):
    latest_posts = Post.objects.raw(
            f'SELECT * FROM forums_post WHERE id IN \
            (SELECT MAX(id) FROM forums_post WHERE forum_id IN \
            (SELECT forum_id FROM forums_forum_members WHERE member_id = {request.user.pk})\
            GROUP BY forum_id);')
    return render(request, 'members/feed.html', {
        'posts_to_show': latest_posts
    })


def show_member(request, member_username):
    if request.user.is_authenticated and member_username == request.user.username:
        #  user trying acces to his own profile through this way.
        return HttpResponseRedirect(reverse('members:profile'))
    else:
        user = get_object_or_404(User, username=member_username)
        return render(request, 'members/profile.html', {
            'user_name': user.username,
            'bio_content': user.member.bio,
            'is_owner': False
        })