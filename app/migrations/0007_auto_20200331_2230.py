# Generated by Django 2.2 on 2020-03-31 17:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20200328_0521'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('username', 'platform', 'email')},
        ),
    ]
