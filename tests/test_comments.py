from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from comments.models import Comment, CommentVote
from members.models import Member
from forums.models import Post, Forum

class CommentModelTests(TestCase):
    def test_both_post_and_in_reply_to_are_none(self):
        '''If the comment is neither a reply to another comment nor to a post an IntegrityError should be thrown'''
        u = User(username='usr')
        u.set_password('pass')
        u.save()

        m = Member(user=u, bio='adasf')
        m.save()

        try:
            Comment.objects.create(commenter=m, content='dfdf', post=None, in_reply_to=None, points=0)
        except IntegrityError:
            integrity_error_was_thrown=True
        else:
            integrity_error_was_thrown=False

        self.assertIs(integrity_error_was_thrown, True)


    def test_in_repl_to_none(self):
        '''If the Comment is a reply to a post and NOT a reply to a comment no Error should be thrown'''
        u = User(username='usr')
        u.set_password('pass')
        u.save()

        m = Member(user=u, bio='adasf')
        m.save()

        f = Forum(owner=u, name='a', description='afaf')
        f.save()

        p = Post(forum=f, poster=m, title='ad', content='adad')
        p.save()


        try:
            Comment.objects.create(commenter=m, content='dfdf', post=p, in_reply_to=None, points=0)
        except IntegrityError:
            integrity_error_was_thrown=True
        else:
            integrity_error_was_thrown=False

        self.assertIs(integrity_error_was_thrown, False)

    def test_post_is_none(self):
        '''If the comment is a reply to another comment and NOT a reply to a post, no error should be thrown'''
        u = User(username='usr')
        u.set_password('pass')
        u.save()

        m = Member(user=u, bio='adasf')
        m.save()

        f = Forum(owner=u, name='a', description='afaf')
        f.save()

        p = Post(forum=f, poster=m, title='ad', content='adad')
        p.save()

        c = Comment(commenter=m, content='dfdf', post=p, in_reply_to=None)
        c.save()


        try:
            Comment.objects.create(commenter=m, content='dfdf', post=None, in_reply_to=c, points=0)
        except IntegrityError:
            integrity_error_was_thrown=True
        else:
            integrity_error_was_thrown=False

        self.assertIs(integrity_error_was_thrown, False)

    def test_both_are_not_none(self):
        '''If the comment is linked to a post and to another comment AT THE SAME TIME, integrity error must be thrown'''
        u = User(username='usr')
        u.set_password('pass')
        u.save()

        m = Member(user=u, bio='adasf')
        m.save()

        f = Forum(owner=u, name='a', description='afaf')
        f.save()

        p = Post(forum=f, poster=m, title='ad', content='adad')
        p.save()

        c = Comment(commenter=m, content='dfdf', post=p, in_reply_to=None)
        c.save()


        try:
            Comment.objects.create(commenter=m, content='dfdf', post=p, in_reply_to=c, points=0)
        except IntegrityError:
            integrity_error_was_thrown=True
        else:
            integrity_error_was_thrown=False

        self.assertIs(integrity_error_was_thrown, True)
    
    def test_user_cant_vote_a_comment_two_times(self):
        '''A user cant have two votes for the same comment'''
        u = User(username='usr')
        u.set_password('pass')
        u.save()

        m = Member(user=u, bio='adasf')
        m.save()

        f = Forum(owner=u, name='a', description='afaf')
        f.save()

        p = Post(forum=f, poster=m, title='ad', content='adad')
        p.save()

        c = Comment(commenter=m, content='dfdf', post=p, in_reply_to=None)
        c.save()

        try:
            CommentVote.objects.create(user=u, comment=c, kind_of_vote='U')
            CommentVote.objects.create(user=u, comment=c, kind_of_vote='U')
        except IntegrityError:
            integrity_error_was_thrown = True
        else:
            integrity_error_was_thrown = False
        
        self.assertIs(integrity_error_was_thrown, True)


class ReplyToPostAndCommentViewsTests(TestCase):
    def test_reply_to_post_without_content_shows_message(self):
        '''If user tried to send a message without content we will send a message'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:reply_to_post', args=(p.pk,)), {
            'comment_content': '  '
        },follow=True)

        self.assertEqual(p.comment_set.count(), 0)  # Reply was not added
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, 'Please provide a content!')
    
    def test_reply_to_comment_without_content_shows_message(self):
        '''If user tries to reply to a comment without providing content we must show a message'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:reply_to_comment', args=(c.pk,)), {
            'comment_content': '  '
        })

        self.assertEqual(c.comment_set.count(), 0)  # Reply was not added!
        self.assertContains(response, 'Please provide a content!')

    def test_reply_to_comment_works(self):
        '''If we send a reply to a comment in a proper way we should be able to see the reply'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:reply_to_comment', args=(c.pk,)), {
            'comment_content': 'comment content, nice'
        }, follow=True)

        self.assertEqual(c.comment_set.count(), 1)  # A reply was added
        #  An upvote record was automatically registered in name of the user who made the comment, to its comment
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='U', comment=(c.comment_set.first())
                ).exists(),
                True
            )
        self.assertEqual(response.redirect_chain[0][1], 302) # redirecting to new comment
        self.assertContains(response, 'comment content, nice') # comment content showing

    def test_reply_to_post_works(self):
        '''If we send a reply to a comment in a proper way we should be able to see the reply'''
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:reply_to_post', args=(p.pk,)), {
            'comment_content': 'comment content, nice'
        }, follow=True)

        self.assertEqual(p.comment_set.count(), 1)  # A reply was added
        #  An upvote record was automatically registered in name of the user who made the comment, to its comment
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='U', comment=(p.comment_set.first())
                ).exists(),
                True
            )
        self.assertEqual(response.redirect_chain[0][1], 302) # redirecting to new comment
        self.assertContains(response, 'comment content, nice') # comment content showing


class UpvoteAndDownvote(TestCase):
    def test_upvote_comment_works(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:upvote_comment', args=(c.pk,)), follow=True)

        # Upvote record exists
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='U', comment=c
                ).exists(),
                True
            )
        self.assertEqual(response.redirect_chain[0][1], 302)  # redirection
        self.assertContains(response, 'Remove Upvote')
        

    
    def test_downvote_comment_works(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:downvote_comment', args=(c.pk,)), follow=True)

        # Downvote record exists
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='D', comment=c
                ).exists(),
                True
            )
        self.assertEqual(response.redirect_chain[0][1], 302)  # redirection
        self.assertContains(response, 'Remove Downvote')

    def test_upvote_two_times_removes_upvote(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        self.client.post(reverse('comments:upvote_comment', args=(c.pk,))) # Upvoting first time
        response = self.client.post(reverse('comments:upvote_comment', args=(c.pk,)), follow=True)

        # Upvote record was removed
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='U', comment=c
                ).exists(),
                False
            )
        self.assertEqual(response.redirect_chain[0][1], 302)  # redirection
        # buttons in normal state
        self.assertNotContains(response, 'Remove Upvote')
        self.assertNotContains(response, 'Remove Downvote')


    def test_downvote_two_times_removes_downvote(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        self.client.post(reverse('comments:downvote_comment', args=(c.pk,))) # Downvoting first time
        response = self.client.post(reverse('comments:downvote_comment', args=(c.pk,)), follow=True)

        # downvote record was removed
        self.assertIs(
            CommentVote.objects.filter(
                user=user, kind_of_vote='D', comment=c
                ).exists(),
                False
            )
        self.assertEqual(response.redirect_chain[0][1], 302)  # redirection
        # buttons in normal state
        self.assertNotContains(response, 'Remove Upvote')
        self.assertNotContains(response, 'Remove Downvote')


class EditCommentView(TestCase):
    def test_edit_comment_works(self):
        user = User(username='hellothere')
        user.set_password('pass')
        user.save()
        member = Member(user=user, bio='sdd')
        member.save()
        forum = Forum(owner=user, name='forum1', description='sdasd')
        forum.save()
        forum.members.add(user.member)
        p = Post(forum=forum, poster=member, title='ad', content='adad')
        p.save()
        c = Comment(commenter=member, post=p, content='adfdf')
        c.save()

        self.client.login(username=user.username, password='pass')
        response = self.client.post(reverse('comments:edit_comment', args=(c.pk,)), {
            'new_content': 'newly edited comment'
        }, follow=True)

        self.assertEqual(Comment.objects.get(pk=c.pk).content, 'newly edited comment')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(response, '(edited)')
        self.assertContains(response, 'newly edited comment')

    def test_cant_edit_comment_aint_yours(self):
        pass

    def test_edit_comment_withoud_content_shows_message(self):
        pass
