from django.test import TestCase
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