from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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
                user = User(username=username, password=password)
                try:
                    user.save()
                except IntegrityError:
                    return render(request, 'members/singup.html', {
                        'user_already_exists': True
                    })
                else:
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
def user_feed(request):
    print(f'{request.user.username}')
    print(f'{request.user.pk}')
    return render(request, 'members/feed.html', {
        'user_name': request.user.username
    })