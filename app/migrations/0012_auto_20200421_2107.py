# Generated by Django 2.2 on 2020-04-21 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20200421_2106'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='idea',
            options={'ordering': ['-votes', 'date_time']},
        ),
    ]
