# Generated by Django 5.0.2 on 2024-02-11 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0008_team_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='ot',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='match',
            name='so',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]