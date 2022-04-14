# Generated by Django 4.0.2 on 2022-04-13 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_comment_check_start_date'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='comment',
            name='check_start_date',
        ),
        migrations.AddConstraint(
            model_name='comment',
            constraint=models.CheckConstraint(check=models.Q(('post', None), ('in_reply_to', None), _negated=True), name='check_is_linked_to_anything'),
        ),
    ]
