# Generated by Django 5.0.2 on 2024-04-20 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0018_remove_match_so'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='ot',
        ),
    ]