from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from members.models import Member
from forums.models import Forum, Post, PostVote

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

    def test_forum_with_saem_name_is_not_allowed(self):
        '''If the user tries to create a forum with an already existent forums name it will not create the forum and display a message'''
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

    def test_create_forum_with_empty_name_not_permited(self):
        '''the forum creation without providing name should not be allowd'''
        user = User(username='julianXXX')
        user.set_password('1234')
        user.save()
        Member.objects.create(user=user, bio='asds')

        self.client.login(username='julianXXX', password='1234')
        response = self.client.post(reverse('forums:create_forum'), {
            'forum_name': '    ',
            'description': '    '
        })

        self.assertIs(
            Forum.objects.filter(name='', description='', owner=user).exists(), 
            False
            )
        self.assertContains(response, 
        'You must provide a name and description to the new forum'
        )

class UpvoteAndDownvote(TestCase):

    def test_upvote_works_fine(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum
        post = Post(
            forum=forum,
            poster=user.member,
            title='a',
            content='a'
        )
        post.save()

        self.client.login(username='hellothere', password='pass')
        response = self.client.post(reverse('forums:upvote_post', args=(post.pk,)), follow=True)
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, "Remove Upvote")  # the button now says remove upvote instead of upvote
        self.assertIs(Post.objects.get(pk=post.pk).points, 1) # upvoted
        self.assertTrue(PostVote.objects.filter(
            post__pk=post.pk, user=user).exists(),  # Vote record was created
            True
            )
        self.assertIs(PostVote.objects.get(
            post__pk=post.pk, user=user).is_upvote(), # is an upvote
            True
            )

    def test_downvote_works_fine(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum
        post = Post(
            forum=forum,
            poster=user.member,
            title='a',
            content='a'
        )
        post.save()

        self.client.login(username='hellothere', password='pass')
        response = self.client.post(reverse('forums:downvote_post', args=(post.pk,)), follow=True)
        self.client.logout()

        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, "Remove Downvote")  # the button now says remove downvote instead of upvote
        self.assertEqual(Post.objects.get(pk=post.pk).points, -1) # downvoted
        self.assertIs(PostVote.objects.filter(
            post__pk=post.pk, user=user).exists(),  # Vote record was created
            True
            )
        self.assertIs(PostVote.objects.get(
            post__pk=post.pk, user=user).is_downvote(), # is a downvote
            True
            )

    def test_upvote_two_times_remove_upvote(self):
        '''If a user upvotes a post that was already upvoted by him, the upvote will be removed'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum
        post = Post(
            forum=forum,
            poster=user.member,
            title='a',
            content='a'
        )
        post.save()

        self.client.login(username='hellothere', password='pass')
        self.client.post(reverse('forums:upvote_post', args=(post.pk,)))  # Upvoting first time
        self.client.post(reverse('forums:upvote_post', args=(post.pk,)))  # Second time
        self.client.logout()

        self.assertEqual(Post.objects.get(pk=post.pk).points, 0) # upvote was removed, therefore no points fot this post
        self.assertIs(PostVote.objects.filter(
            post__pk=post.pk, user=user).exists(),  # Vote record does not exists because it was deleted
            False
            )

    def test_downvote_two_times_remove_downvote(self):
        '''If a user downvotes a post that was already downvoted by him, the downvote will be removed'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        Member.objects.create(user=user, bio='sdd')
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)  # Adding user to forum
        post = Post(
            forum=forum,
            poster=user.member,
            title='a',
            content='a'
        )
        post.save()

        self.client.login(username='hellothere', password='pass')
        self.client.post(reverse('forums:downvote_post', args=(post.pk,)))  # downvoting first time
        self.client.post(reverse('forums:downvote_post', args=(post.pk,)))  # Second time
        self.client.logout()

        self.assertEqual(Post.objects.get(pk=post.pk).points, 0) # downvote was removed, therefore no points fot this post
        self.assertIs(PostVote.objects.filter(
            post__pk=post.pk, user=user).exists(),  # Vote record does not exists because it was deleted
            False
            )    

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
            'post_title': '   ',
            'post_content': '  '
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
        self.assertIs(forum.post_set.all().contains(post), True)  
        # post was not posted by user, hence post was not deleted

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
            'new_content': '   '
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