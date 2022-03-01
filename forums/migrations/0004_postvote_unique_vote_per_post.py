# Generated by Django 4.0.2 on 2022-03-01 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0003_postvote'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='postvote',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_vote_per_post'),
        ),
    ]
