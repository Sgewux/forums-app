from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    bio = models.CharField(max_length=255)

    def __str__(self):
        return f'User: {self.user.username}'