# Generated by Django 5.0.2 on 2024-04-15 14:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iihf', '0011_playoff_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialTip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('czech_shooter_first', models.CharField(blank=True, max_length=64)),
                ('czech_shooter_last', models.CharField(blank=True, max_length=64)),
                ('max_goals_per_game', models.IntegerField(default=0)),
                ('overtimes', models.IntegerField(default=0)),
                ('bronze_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bronze_a_special_tips', to='iihf.team')),
                ('bronze_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bronze_b_special_tips', to='iihf.team')),
                ('final_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_a_special_tips', to='iihf.team')),
                ('final_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='final_b_special_tips', to='iihf.team')),
                ('group_a_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_a_1_special_tips', to='iihf.team')),
                ('group_a_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_a_2_special_tips', to='iihf.team')),
                ('group_a_3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_a_3_special_tips', to='iihf.team')),
                ('group_a_4', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_a_4_special_tips', to='iihf.team')),
                ('group_b_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_b_1_special_tips', to='iihf.team')),
                ('group_b_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_b_2_special_tips', to='iihf.team')),
                ('group_b_3', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_b_3_special_tips', to='iihf.team')),
                ('group_b_4', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_b_4_special_tips', to='iihf.team')),
                ('team_drop_a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_drop_a_special_tips', to='iihf.team')),
                ('team_drop_b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_drop_b_special_tips', to='iihf.team')),
                ('team_first_goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_first_goal_special_tips', to='iihf.team')),
                ('team_last_goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_last_goal_special_tips', to='iihf.team')),
                ('team_least_goals', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_least_goals_special_tips', to='iihf.team')),
                ('team_most_goals', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_most_goals_special_tips', to='iihf.team')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='winner_special_tips', to='iihf.team')),
            ],
        ),
    ]
