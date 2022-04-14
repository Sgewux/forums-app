from django.urls import path

from  . import views

app_name = 'comments'
urlpatterns = [
    path('<int:comment_id>/', views.show_comment, name='show_comment')
]