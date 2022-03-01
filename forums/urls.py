from django.urls import path

from . import views

app_name = 'forums'
urlpatterns = [
    path('', views.show_forums, name='forums_home'),
    path('create/', views.create_forum, name='create_forum'),
    path('post/<int:post_id>/', views.show_post, name='show_post'),
    path('post/<int:post_id>/upvote', views.upvote_post, name='upvote_post'),
    path('post/<int:post_id>/downvote', views.downvote_post, name='downvote_post'),
    path('<str:forum_name>/', views.show_forum, name='show_forum'),
    path('<str:forum_name>/join', views.join_forum, name='join_forum'),
    path('<str:forum_name>/leave', views.leave_forum, name='leave_forum')
]