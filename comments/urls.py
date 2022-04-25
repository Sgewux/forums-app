from django.urls import path

from  . import views

app_name = 'comments'
urlpatterns = [
    path('<int:comment_id>/', views.show_comment, name='show_comment'),
    path('reply_to_post/<int:post_id>/', views.reply_to_post, name='reply_to_post'),
    path('<int:comment_id>/upvote', views.upvote_comment, name='upvote_comment'),
    path('<int:comment_id>/downvote', views.downvote_comment, name='downvote_comment'),
]