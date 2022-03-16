from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from members.models import Member
from forums.models import Forum, Post

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

        response = self.client.post(
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
        response = self.client.post(
            reverse('forums:leave_forum', args=(forum.name,)),
            follow=True
        )
        self.client.logout()
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'Join comunity')
        self.assertIs(forum.members.all().contains(user.member), False)


class TestForumCreation(TestCase):

    def test_forum_model_creation(self):
        '''Test if the forum creation process works properly'''
        user = User(username='julianXXX')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='asds')

        self.client.login(username='julianXXX', password='1234')
        response = self.client.post(reverse('forums:create_forum'), {
            'forum_name': 'testforum1',
            'description': 'des'
        }, follow=True)

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertIs(Forum.objects.filter(name='testforum1').exists(), True)
        self.assertIs(
            Forum.objects.get(name='testforum1').members.all().contains(user.member), 
            True
            )

    def test_forum_model_creation_with_same_name(self):
        '''If the user tries to create a forum with an already existent forums name it will display a message'''
        user = User(username='pedro')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='asds')

        Forum.objects.create(owner=user, name='already exists', description='asdasd')

        self.client.login(username='pedro', password='1234')
        response = self.client.post(reverse('forums:create_forum'), {
            'forum_name': 'already exists',
            'description': 'des'
        })

        self.assertContains(response, 'We already have a forum with that name.')


class UpvoteAndDownvote(TestCase):
    def test_upvote_works_fine(self):
        pass

    def test_downvote_works_fine(self):
        pass

    def test_upvote_two_times_remove_upvote(self):
        pass

    def test_downvote_two_times_remove_downvote(self):
        pass

    def test_remove_downvote_once_downvoted(self):
        pass

    def test_remove_upvote_once_upvoted(self):
        pass
    

class PublishEditAndDeletePost(TestCase):

    def test_post_publishment_works(self):
        '''Test if the publishment process works well'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:publish_post', args=('forum1',)), {
            'post_title': 'whatever',
            'post_content': 'idc'
        }, follow=True)
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertIs(user.member.post_set.filter(title = 'whatever', content='idc').exists(), True)
        self.assertContains(response, 'whatever')

    def test_info_message_when_user_aint_part_of_forum_when_publishin(self):
        '''If the user is not part of the forum, it would not be able to post, wi will show him a message telling him that'''
        user = User(username='useruser')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum2', description='sdasd')
        forum.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:publish_post', args=(forum.name,)), {
            'post_title': 'whatever',
            'post_content': 'idc'
        }, follow=True)
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertIs(user.member.post_set.filter(title = 'whatever', content='idc').exists(), False) # Post was not created
        self.assertContains(response, 'You have to be part of this community to publish a post.') # message
    
    def test_info_message_when_user_sent_blank_fields_when_publishing(self):
        '''IF the user didnt provide a title nor a content fo the post we will show him a message'''
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:publish_post', args=(forum.name,)), {
            'post_title': '',
            'post_content': ''
        })
        self.client.logout()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please fill all the fields')
    
    def test_delete_post_works(self):
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        post = Post(
            forum=forum,
            content='SDAS',
            poster=user.member,
            title='sdsds'
            )
        post.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:delete_post', args=(post.pk,)),
            follow=True
        )
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, f'Your post: {post.title} Was succesfully deleted.')
        self.assertIs(forum.post_set.all().contains(post), False)

    def test_return_forbidden_if_trying_delete_post_isnt_yours(self):
        '''If the user tryes to delete a post that is not his we will return HTTP 403'''
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        post = Post(
            forum=forum,
            content='SDAS',
            poster=user.member,
            title='sdsds'
            )
        post.save()
        user2 = User(username='asdasdeee')
        user2.set_password('pass')
        user2.save()
        Member.objects.create(user=user2, bio='sdd')

        self.client.login(username=user2.username, password='pass')
        response = self.client.post(reverse('forums:delete_post', args=(post.pk,)))
        self.client.logout()

        self.assertEqual(response.status_code, 403)
        self.assertIs(forum.post_set.all().contains(post), True)  # hence post was not deleted

    def test_edit_post_works(self):
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        post = Post(
            forum=forum,
            content='SDAS',
            poster=user.member,
            title='sdsds'
            )
        post.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:edit_post', args=(post.pk,)), {
            'new_content': 'new content'
        }, follow=True)
        self.client.logout()

        edited_post = Post.objects.get(pk=post.pk)
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(edited_post.content, 'new content')
        self.assertIs(edited_post.edited, True)


    def test_edit_post_without_content_displays_message(self):
        '''If the user does not provide a new content for the post we should show a message and dont update that post'''
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        post = Post(
            forum=forum,
            content='first content',
            poster=user.member,
            title='sdsds'
            )
        post.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('forums:edit_post', args=(post.pk,)), {
            'new_content': ''
        })
        self.client.logout()

        edited_post = Post.objects.get(pk=post.pk)
        self.assertContains(response, 'Please provide a new content for the post.')
        self.assertEqual(edited_post.content, 'first content')  # content remains the same
        self.assertIs(edited_post.edited, False)
        
    def test_return_forbidden_if_trying_to_edit_post_isnt_yours(self):
        '''If the user tryies to delete a post that isnt his, we will return 403 forbidden as HTTP statuscode'''
        user = User(username='asdsa8')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum3', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        post = Post(
            forum=forum,
            content='first content',
            poster=user.member,
            title='sdsds'
            )
        post.save()
        user2 = User(username='asdasdeee')
        user2.set_password('pass')
        user2.save()
        Member.objects.create(user=user2, bio='sdd')

        self.client.login(username=user2.username, password='pass')
        response = self.client.post(reverse('forums:edit_post', args=(post.pk,)), {
            'new_content': 'zgzg'
        })
        self.client.logout()
        edited_post = Post.objects.get(pk=post.pk)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(edited_post.content, 'first content')  # content remains the same
        self.assertIs(edited_post.edited, False)