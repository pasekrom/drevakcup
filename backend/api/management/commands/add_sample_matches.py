"""
Management command to add sample matches with results to a cup.
Usage:
  python manage.py add_sample_matches --year 2026
  python manage.py add_sample_matches --cup-id 1
"""
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Cup, Match, Team


class Command(BaseCommand):
    help = 'Add sample matches with results for a cup (by year or cup-id).'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='Cup year (e.g. 2026)')
        parser.add_argument('--cup-id', type=int, help='Cup ID')
        parser.add_argument('--dry-run', action='store_true', help='Only show what would be created')

    def handle(self, *args, **options):
        cup = None
        if options.get('cup_id'):
            cup = Cup.objects.filter(id=options['cup_id']).first()
        elif options.get('year'):
            cup = Cup.objects.filter(year=options['year']).first()
        else:
            cup = Cup.objects.order_by('-year').first()
        if not cup:
            self.stderr.write(self.style.ERROR('No cup found. Use --year or --cup-id.'))
            return
        teams = list(Team.objects.filter(cup=cup).order_by('group', 'name'))
        if len(teams) < 2:
            self.stderr.write(self.style.ERROR(f'Cup {cup.year} has fewer than 2 teams. Add teams first.'))
            return

        group_a = [t for t in teams if t.group == 'A']
        group_b = [t for t in teams if t.group == 'B']
        # Build pairs: within-group matches (and optionally cross-group)
        pairs = []
        for i, ta in enumerate(group_a):
            for tb in group_a[i + 1:]:
                pairs.append((ta, tb))
        for i, ta in enumerate(group_b):
            for tb in group_b[i + 1:]:
                pairs.append((ta, tb))
        # If we have few pairs, add some cross-group
        if len(pairs) < 4 and group_a and group_b:
            for ta in group_a[:2]:
                for tb in group_b[:2]:
                    if ta != tb:
                        pairs.append((ta, tb))

        # Sample results: (score_a, score_b, overtime)
        results = [
            (3, 2, False), (2, 1, False), (4, 1, False), (1, 0, False),
            (2, 2, True),  # 2-2 then OT (we store final as 3-2 or 2-3)
            (1, 1, True), (0, 2, False), (3, 0, False), (2, 3, False),
            (5, 4, True), (2, 4, False), (1, 3, False), (0, 1, False),
        ]
        base_date = timezone.now() - timedelta(days=14)
        dry_run = options.get('dry_run', False)
        created = 0
        for idx, (team_a, team_b) in enumerate(pairs):
            if idx >= 12:
                break
            sa, sb, ot = results[idx % len(results)]
            if random.choice([True, False]):
                sa, sb = sb, sa
            date = base_date + timedelta(days=idx, hours=idx % 3 * 4)
            if dry_run:
                self.stdout.write(
                    f'Would create: {team_a.name} vs {team_b.name} '
                    f'{sa}:{sb} {"(OT)" if ot else ""} @ {date}'
                )
                created += 1
                continue
            obj, created = Match.objects.get_or_create(
                cup=cup,
                team_a=team_a,
                team_b=team_b,
                date=date,
                defaults={
                    'score_a': sa,
                    'score_b': sb,
                    'score_a_final': sa,
                    'score_b_final': sb,
                    'overtime': ot,
                },
            )
            if not created and (obj.score_a is None or obj.score_b is None):
                obj.score_a = sa
                obj.score_b = sb
                obj.score_a_final = sa
                obj.score_b_final = sb
                obj.overtime = ot
                obj.save()
            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'  {team_a.name} vs {team_b.name} {sa}:{sb} {"(OT)" if ot else ""}'
                )
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(f'Dry run: would create {created} matches.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Done. Created/ensured {created} matches for cup {cup.year}.'))
            self.stdout.write('Run point calculation (Správa → Přepočítat body) or save a match to recalc.')
