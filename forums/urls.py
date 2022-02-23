from django.urls import path

from . import views

app_name = 'forums'
urlpatterns = [
    path('', views.show_forums, name='forums_home')
]
