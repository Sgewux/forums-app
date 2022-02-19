from django.urls import path
from . import views

app_name = 'members'
urlpatterns = [
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/singup/', views.singup_user, name='singup'),
    path('profile/', views.show_profile, name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),
    path('profile/delete', views.delete_account, name='delete_account'),
    path('members/<str:member_username>', views.show_member, name='show_member'),
    path('feed/', views.user_feed, name='feed')
]