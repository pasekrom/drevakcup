# Generated by Django 5.0.2 on 2024-02-12 11:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0010_alter_match_score_a_alter_match_score_b_playoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='playoff',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
