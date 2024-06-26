# Generated by Django 5.0.2 on 2024-02-12 11:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0009_match_ot_match_so'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='score_a',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='score_b',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Playoff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playoff', models.CharField(choices=[('QFA1', 'QFA1'), ('QFA2', 'QFA2'), ('QFB1', 'QFB1'), ('QFB2', 'QFB2'), ('SFA', 'SFA'), ('SFB', 'SFB'), ('BMG', 'BMG'), ('GMG', 'GMG')], max_length=4)),
                ('score_a', models.IntegerField(blank=True, null=True)),
                ('score_b', models.IntegerField(blank=True, null=True)),
                ('ot', models.CharField(blank=True, max_length=1)),
                ('so', models.CharField(blank=True, max_length=1)),
                ('cup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iihf.cup')),
                ('team_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playoff_team_a', to='iihf.team')),
                ('team_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playoff_team_b', to='iihf.team')),
            ],
        ),
    ]
