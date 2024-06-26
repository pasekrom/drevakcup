# Generated by Django 5.0.2 on 2024-05-13 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0022_userpoint_part'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playoff',
            name='ot',
        ),
        migrations.RemoveField(
            model_name='playoff',
            name='so',
        ),
        migrations.AddField(
            model_name='playoff',
            name='overtime',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playoff',
            name='score_a_final',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='playoff',
            name='score_b_final',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='playoff',
            name='shootout',
            field=models.BooleanField(default=False),
        ),
    ]
