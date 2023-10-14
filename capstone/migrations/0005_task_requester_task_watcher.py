# Generated by Django 4.2.5 on 2023-09-25 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0004_remove_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='requester',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='requester', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='watcher',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
