# Generated by Django 3.2.15 on 2022-10-14 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_alter_user_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Country',
            field=models.CharField(default='Australia', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='Courses',
            field=models.CharField(default='CSSE2002,COMP3506,INFS2200', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='Major',
            field=models.CharField(default='CS', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='Topics',
            field=models.CharField(default='Study,Culture,News', max_length=200, null=True),
        ),
    ]
