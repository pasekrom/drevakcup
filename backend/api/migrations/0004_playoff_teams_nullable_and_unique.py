from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playoff',
            name='team_a',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='playoffs_as_team_a',
                to='api.team',
            ),
        ),
        migrations.AlterField(
            model_name='playoff',
            name='team_b',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='playoffs_as_team_b',
                to='api.team',
            ),
        ),
        migrations.AddConstraint(
            model_name='playoff',
            constraint=models.UniqueConstraint(
                fields=('cup', 'playoff_type'),
                name='uniq_playoff_cup_playoff_type',
            ),
        ),
    ]
