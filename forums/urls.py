from django.urls import path

from . import views

app_name = 'forums'
urlpatterns = [
    path('', views.show_forums, name='forums_home'),
    path('create/', views.create_forum, name='create_forum'),
    path('<str:forum_name>/', views.show_forum, name='show_forum'),
    path('<str:forum_name>/join', views.join_forum, name='join_forum'),
    path('<str:forum_name>/leave', views.leave_forum, name='leave_forum')
]
