from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import Member
from forums.models import Post
from comments.models import Comment


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


def create_new_account(request, username, password, password_again):
    '''
    This function will handle all the account (User/Member models pair) creation process
    it is NOT meant to be used as a view, it will only be called inside singup_user view
    to reduce its cognitive complexity
    '''
    if password == password_again and ' ' not in username:  #  The user filled the form correctly
        user = User(username=username)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            messages.add_message(
                request,
                messages.ERROR,
                'That user already exists!'
            )
            return render(request, 'members/singup.html', {})
        else:
            Member.objects.create(user=user, bio='Hello everyone, i\'m using ForumsApp!')
            login(request, user)
            return HttpResponseRedirect(reverse('members:feed'))

    elif password != password_again:
        messages.add_message(
            request,
            messages.ERROR,
            'Passwords were not equal!'
        )
        return render(request, 'members/singup.html', {})

    elif ' ' in username:
        messages.add_message(
            request,
            messages.INFO,
            'Spaces are not allowed in username'
        )
        return render(request, 'members/singup.html', {})


def singup_user(request):
    if not request.user.is_authenticated:  #  We dont want an already logged user to create accounts
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            password_again = request.POST.get('password_again', '')

            if all((
                username, 
                password.strip(), 
                password_again.strip()
                )):  # The user didnt leave blank fields
                # Notice that due to the str inmutability, the password obj is not modified by .strip()
                # Your passwd will remain the same, the strip is just to check if you sent a blank as passwd

                return create_new_account(request, username ,password, password_again)

            else:
                messages.add_message(
                    request,
                    messages.ERROR,
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
    
    # The most recent comments posted as a reply to a comment made by the user or a post
    latest_replies = Comment.objects.filter(
        (Q(post__poster=request.user.member) | Q(in_reply_to__commenter=request.user.member))
        &
        ~Q(commenter=request.user.member)
    ).order_by('-pub_date')[:3]

    return render(request, 'members/feed.html', {
        'posts_to_show': latest_posts,
        'replies': latest_replies  # Naming context as "replies" to be able to include show_replies.html into feed template
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