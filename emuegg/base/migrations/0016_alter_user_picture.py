# Generated by Django 3.2.15 on 2022-10-13 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_alter_user_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Picture',
            field=models.ImageField(default='', null=True, upload_to=''),
        ),
    ]
