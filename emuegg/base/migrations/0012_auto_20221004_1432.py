# Generated by Django 3.2.15 on 2022-10-04 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_alter_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='Topics',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='Courses',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
