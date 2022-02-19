from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import Member

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('members:feed'))
        else:
            return render(request, 'members/login.html', {
                'login_failed': True
            })
    else:
        return render(request, 'members/login.html', {})


def singup_user(request):
    if not request.user.is_authenticated:  #  We dont want an already logged user to create accounts
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            password_again = request.POST['password_again']

            if password == password_again:  #  The user filled the form correctly
                user = User(username=username)
                user.set_password(password)
                try:
                    user.save()
                except IntegrityError:
                    return render(request, 'members/singup.html', {
                        'user_already_exists': True
                    })
                else:
                    Member.objects.create(user=user, bio='Hello everyone, i\'m using ForumsApp!')
                    login(request, user)
                    return HttpResponseRedirect(reverse('members:feed'))
            else:
                return render(request, 'members/singup.html', {
                    'passwords_are_different': True
                })
        else:
            return render(request, 'members/singup.html', {})
    else:
        return HttpResponseRedirect(reverse('members:feed'))


def logout_user(request):
    logout(request)
    # to do: redirect to the /forums page once its created
    return HttpResponse('forums')


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
        member.bio = request.POST['new_bio']
        member.save()

        return HttpResponseRedirect(reverse('members:profile'))
    else:
        return render(request, 'members/edit_profile.html', {
            'old_bio': request.user.member.bio
        })


@login_required
def delete_account(request):
    if request.method == 'POST':
        if request.user.check_password(request.POST['password']):
            former_user = request.user
            logout(request)
            former_user.delete()

            return HttpResponse('deleted user will be redirected to /forms')
        
        else:
            return render(request, 'members/delete_account.html', {
                'wrong_password': True
            })

    else:
        return render(request, 'members/delete_account.html',{})


@login_required
def user_feed(request):
    return render(request, 'members/feed.html', {
        'user_name': request.user.username
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