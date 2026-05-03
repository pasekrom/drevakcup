# Generated manually for Special model: allow null/blank on team FKs

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='special',
            name='winner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='won_tournaments', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='final_a',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='final_a_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='final_b',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='final_b_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='bronze_a',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bronze_a_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='bronze_b',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bronze_b_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_a_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_a_1_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_b_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_b_1_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_a_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_a_2_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_b_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_b_2_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_a_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_a_3_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_b_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_b_3_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_a_4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_a_4_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='group_b_4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_b_4_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_most_goals',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='most_goals_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_least_goals',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='least_goals_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_first_goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='first_goal_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_last_goal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_goal_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_drop_a',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drop_a_results', to='api.team'),
        ),
        migrations.AlterField(
            model_name='special',
            name='team_drop_b',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drop_b_results', to='api.team'),
        ),
    ]
