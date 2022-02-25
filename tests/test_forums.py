from unittest import TestCase
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from members.models import Member
from forums.models import Forum

class TestJoinAndLeaveForumView(TestCase):
    def test_succesfull_join(self):
        '''Test if the join view is working correctly'''
        owner = User(username='seb')
        owner.set_password('asdfas')
        owner.save()
        Member.objects.create(user=owner, bio='dfsdf')

        user = User(username='julian')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='dfsdf')

        forum = Forum.objects.create(owner=owner, name='forum1', description='adfsfadf')
        forum.save()

        self.client.login(username='julian', password='1234')

        response = self.client.get(
            reverse('forums:join_forum', args=(forum.name,)), 
            follow=True
            )
        self.client.logout()
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'Leave comunity')
        self.assertIs(forum.members.all().contains(user.member), True)  # contains() is available since django 4.0
    
    def test_leave(self):
        '''Test if the user can leave the form correctly'''
        owner = User(username='sebad')
        owner.set_password('asdfas')
        owner.save()
        Member.objects.create(user=owner, bio='dfsdf')

        user = User(username='juliaasdn')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='dfsdf')

        forum = Forum.objects.create(owner=owner, name='forum2', description='adfsfadf')
        forum.save()

        forum.members.add(user.member)

        self.client.login(username='juliaasdn', password='1234')
        response = self.client.get(
            reverse('forums:leave_forum', args=(forum.name,)),
            follow=True
        )
        self.client.logout()
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'Join comunity')
        self.assertIs(forum.members.all().contains(user.member), False)