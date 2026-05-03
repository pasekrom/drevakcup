"""
Print Special result and SpecialTip final/bronze IDs for a cup to debug point calculation.
Usage:
  python manage.py debug_special_points --cup-id 1
  python manage.py debug_special_points --cup-id 1 --user-id 2
"""
from django.core.management.base import BaseCommand

from api.models import Cup, Special, SpecialTip, UserPoint


class Command(BaseCommand):
    help = 'Debug special tips vs results (final_a/b, bronze_a/b) for a cup.'

    def add_arguments(self, parser):
        parser.add_argument('--cup-id', type=int, required=True, help='Cup ID')
        parser.add_argument('--user-id', type=int, help='Limit to this user ID')

    def handle(self, *args, **options):
        cup_id = options['cup_id']
        user_id = options.get('user_id')
        cup = Cup.objects.filter(id=cup_id).first()
        if not cup:
            self.stderr.write(self.style.ERROR(f'Cup id={cup_id} not found.'))
            return
        special = Special.objects.filter(cup=cup).select_related(
            'final_a', 'final_b', 'bronze_a', 'bronze_b', 'winner'
        ).first()
        if not special:
            self.stdout.write('No Special result for this cup.')
            return
        self.stdout.write(f'Cup {cup.year} (id={cup.id})')
        self.stdout.write(
            f'  Result: winner_id={special.winner_id} final_a_id={special.final_a_id} final_b_id={special.final_b_id} '
            f'bronze_a_id={special.bronze_a_id} bronze_b_id={special.bronze_b_id}'
        )
        qs = SpecialTip.objects.filter(cup=cup).select_related('user', 'final_a', 'final_b', 'bronze_a', 'bronze_b')
        if user_id:
            qs = qs.filter(user_id=user_id)
        for st in qs:
            up_b = UserPoint.objects.filter(user=st.user, cup=cup, part='B').first()
            pts = up_b.points if up_b else 0
            self.stdout.write(
                f'  User {st.user_id} ({st.user.email}): '
                f'final_a_id={st.final_a_id} final_b_id={st.final_b_id} '
                f'bronze_a_id={st.bronze_a_id} bronze_b_id={st.bronze_b_id} -> Part B points={pts}'
            )
            if special.final_a_id and (special.final_a_id == st.final_a_id or special.final_a_id == st.final_b_id):
                self.stdout.write(self.style.SUCCESS('    -> final_a match: should get +16'))
            elif special.final_a_id:
                self.stdout.write(
                    self.style.WARNING(f'    -> final_a no match (result={special.final_a_id}, tip={st.final_a_id}/{st.final_b_id})')
                )
