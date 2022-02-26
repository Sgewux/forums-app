from django.urls import path

from . import views

app_name = 'forums'
urlpatterns = [
    path('', views.show_forums, name='forums_home'),
    path('create/', views.create_forum, name='create_forum'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='show_post'),
    #pah('post/<int:post_id>/upvote', views.upvote_post, name='upvote_post'),
    #pah('post/<int:post_id>/downvote', views.downvote_post, name='downvote_post'),
    path('<str:forum_name>/', views.show_forum, name='show_forum'),
    #path('<str:forum_name>/post', views.show_forum, name='post_in_forum'),
    path('<str:forum_name>/join', views.join_forum, name='join_forum'),
    path('<str:forum_name>/leave', views.leave_forum, name='leave_forum')
]