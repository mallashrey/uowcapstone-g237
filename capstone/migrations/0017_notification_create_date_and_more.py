# Generated by Django 4.2.5 on 2023-10-05 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstone', '0016_user_dept'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='create_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification',
            field=models.IntegerField(null=True),
        ),
    ]
