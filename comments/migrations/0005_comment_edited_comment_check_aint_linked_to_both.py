# Generated by Django 4.0.2 on 2022-04-14 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_commentvote_unique_vote_per_user_for_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='comment',
            constraint=models.CheckConstraint(check=models.Q(('post__isnull', False), ('in_reply_to__isnull', False), _negated=True), name='check_aint_linked_to_both'),
        ),
    ]
