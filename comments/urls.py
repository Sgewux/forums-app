from django.urls import path

from  . import views

app_name = 'comments'
urlpatterns = [
    path('<int:comment_id>/', views.show_comment, name='show_comment'),
    path('<int:comment_id>/upvote', views.upvote_comment, name='upvote_comment'),
    path('<int:comment_id>/downvote', views.downvote_comment, name='downvote_comment'),
]