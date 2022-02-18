from django.urls import path
from . import views

app_name = 'members'
urlpatterns = [
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/singup/', views.singup_user, name='singup'),
    path('feed/', views.user_feed, name='feed')
]
