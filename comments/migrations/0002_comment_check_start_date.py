# Generated by Django 4.0.2 on 2022-04-13 23:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='comment',
            constraint=models.CheckConstraint(check=models.Q(('points', 12)), name='check_start_date'),
        ),
    ]