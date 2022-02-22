from audioop import reverse
from unittest import TestCase
from urllib import request
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from members.models import Member

class SingupViewTests(TestCase):
    def test_display_message_user_already_exists(self):
        '''If we try to use a username that already exists we will se a message'''
        user = User(username='juan1')
        user.set_password('examplepasswd')
        user.save()

        response = self.client.post(reverse('members:singup'), {
            'username': user.username,  #  Sending request with an already used username
            'password': 'pass',
            'password_again': 'pass'
            })
        
        self.assertContains(response, 'That user already exists!')
    
    def test_display_different_passwd_message(self):
        '''If we filled the singup form with two diferent passwords, we will see a message'''
        
        response = self.client.post(reverse('members:singup'), {
            'username': 'roberto',
            'password': 'firstpasswd',
            'password_again': 'secondpasswd'
            })
        
        self.assertContains(response, 'Passwords were not equal!')
             
    def test_correct_singup_process(self):
        '''If the user properly filled the form, a Member object should be created and user should be redirected to its feed'''
        
        response = self.client.post(reverse('members:singup'), {
            'username': 'carlos',
            'password': '1234',
            'password_again': '1234'
            })
        
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(User.objects.get(username='carlos'))  # User carlos exists
        self.assertIsNotNone(User.objects.get(username='carlos').member)  # Member object related to carlos exists
    
    def test_already_logged_user_creating_accounts(self):
        '''if a user is already logged in we dont want it to create an account, we will redirect to his feed'''
        
        user = User(username='david')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='bio')

        self.client.login(username='david', password='1234')
        response = self.client.get(reverse('members:singup'))
        
        self.client.logout()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('members:feed'))


class LoginViewTests(TestCase):

    def test_unsuccesful_login(self):
        '''if the login proces didnt work (due to wrong credentials) will display an error messsage'''
        response = self.client.post(reverse('members:login'), {
            'username': 'unexsistent_username',
            'password': 'unexistend_password'
        })

        self.assertContains(response, 'Unsuccesfull login, try again!')
    
    def test_succesful_login(self):
        '''If the loggin process worked user should be redirected to it's feed'''
        
        user = User(username='sebastian')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='bio')

        response = self.client.post(reverse('members:login'), {
            'username': 'sebastian',
            'password': '1234'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('members:feed'))


class ShowMemberViewTests(TestCase):
    
    def test_authenticated_user_accesing_his_own_profile(self):
        '''If an already auth user tries to acces to it's profile through this way, we will redirect it to /profile'''

        user = User(username='sebas')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='bio')

        self.client.login(username='sebas', password='1234')
        response = self.client.get(
            reverse('members:show_member', args=(user.username,)),
            follow=True
            )
        self.client.logout()
        self.assertEqual(response.redirect_chain[0][1], 302)  # The first response was a redirect
        self.assertContains(response, 'Edit Bio?')  # If accesing to its own profile has the right to edit its 
    
    def test_authenticated_user_accesing_to_different_profile(self):
        '''If an already auth user tries to acces to different profile, the view works without redirections'''
        user1 = User(username='maria')
        user1.set_password('1234')
        user1.save()
        Member.objects.create(user=user1, bio='bio')
        self.client.login(username='maria', password='1234')

        user2 = User(username='lmao')
        user2.set_password('12345')
        user2.save()
        Member.objects.create(user=user2, bio='bio')

        response = self.client.get(
            reverse('members:show_member', args=('lmao',)),
            )
        self.client.logout()
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Edit Bio?')


class EditProfileViewTests(TestCase):
    def test_edit_profile_works_correctly(self):
        '''The profile's bio is actually updated'''
        
        user = User(username='jose')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='firstbio')
        self.client.login(username='jose', password='1234')

        response = self.client.post(reverse('members:edit_profile'),
        {
            'new_bio':'secondbio'
        }, follow=True)
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'secondbio')
        self.assertEqual(
            Member.objects.get(user__username='jose').bio,
            'secondbio')


class DeleteAccountTests(TestCase):
    def test_delete_account_works(self):
        '''test if the account is actually deleted'''
        user = User(username='josejose')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='firstbio')

        self.client.login(username='josejose', password='1234')
        self.client.post(reverse('members:delete_account'), {'password':'1234'})

        self.assertIs(User.objects.all().contains(user), False)  # queryset.contains() is available since Django 4.0
    
    def test_wrong_password_in_delete_form(self):
        '''If user wrote a wrong password a funny message should be displayed'''

        user = User(username='josecarlos')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='firstbio')

        self.client.login(username='josecarlos', password='1234')
        response = self.client.post(reverse('members:delete_account'), 
        {
            'password':'wrongpasswd'
        })
        
        self.assertContains(response, 
        'You wrote the wrong pasword! seems like you don\'t really want to leave...')