"""
Business logic services for point calculation and statistics.
"""
import unicodedata

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Q, Prefetch
from django.utils import timezone
from .models import Cup, Match, Playoff, Team, MatchTip, SpecialTip, Special, UserPoint, User


def is_tournament_started(cup: Cup) -> bool:
    """Check if tournament has started."""
    first_match = Match.objects.filter(cup=cup).order_by('date').first()
    if not first_match:
        return False
    return timezone.now() >= first_match.date


def _play_final_scores(obj):
    """Vrátí (sa, sb) z finálního nebo základního skóre, nebo (None, None)."""
    sa = obj.score_a_final if obj.score_a_final is not None else obj.score_a
    sb = obj.score_b_final if obj.score_b_final is not None else obj.score_b
    return sa, sb


def sync_special_derived_stats(cup: Cup) -> None:
    """
    Z výsledků zápasů + tabulky týmů (gf/ga po calculate) doplní do Special:
    team_most_goals, team_least_goals, max_goals_per_game, overtimes.
    Ručně ve správě zůstávají jen první/poslední branka (team_first_goal, team_last_goal) a ostatní sekce.
    """
    special = Special.objects.filter(cup=cup).first()
    if not special:
        return

    teams = list(Team.objects.filter(cup=cup))
    played = [t for t in teams if (t.gp or 0) > 0]

    most_team = None
    least_team = None
    if played:
        max_gf = max(t.gf for t in played)
        most_candidates = [t for t in played if t.gf == max_gf]
        most_team = min(most_candidates, key=lambda t: (t.ga, t.id))

        min_ga = min(t.ga for t in played)
        least_candidates = [t for t in played if t.ga == min_ga]
        least_team = max(least_candidates, key=lambda t: (t.gf, t.id))

    max_total = 0
    ot_draws = 0
    _play_fields = (
        'score_a', 'score_b', 'score_a_final', 'score_b_final', 'overtime', 'shootout'
    )
    for m in Match.objects.filter(cup=cup).only(*_play_fields):
        sa, sb = _play_final_scores(m)
        if sa is not None and sb is not None:
            max_total = max(max_total, sa + sb)
            if m.overtime or m.shootout or sa == sb:
                ot_draws += 1
    for p in Playoff.objects.filter(cup=cup).only(*_play_fields):
        sa, sb = _play_final_scores(p)
        if sa is not None and sb is not None:
            max_total = max(max_total, sa + sb)
            if p.overtime or p.shootout or sa == sb:
                ot_draws += 1

    special.team_most_goals = most_team
    special.team_least_goals = least_team
    special.max_goals_per_game = max_total
    special.overtimes = ot_draws
    special.save(
        update_fields=[
            'team_most_goals',
            'team_least_goals',
            'max_goals_per_game',
            'overtimes',
            'updated_at',
        ]
    )


def sync_special_from_playoffs(cup: Cup) -> None:
    """
    Z play-offů doplní do Special: finále (GMG), o bronz (BMG), vítěze z konečného skóre finále.
    Volá se při přepočtu bodů; pokud pro turnaj neexistuje žádný play-off záznam, nic nemění.
    """
    qs = Playoff.objects.filter(cup=cup).select_related('team_a', 'team_b')
    if not qs.exists():
        return
    special, _ = Special.objects.get_or_create(cup=cup)
    by_type = {p.playoff_type: p for p in qs}
    gmg = by_type.get('GMG')
    if gmg is not None:
        special.final_a = gmg.team_a
        special.final_b = gmg.team_b
        sa, sb = _play_final_scores(gmg)
        if (
            gmg.team_a_id
            and gmg.team_b_id
            and sa is not None
            and sb is not None
            and sa != sb
        ):
            special.winner = gmg.team_a if sa > sb else gmg.team_b
        else:
            special.winner = None
    bmg = by_type.get('BMG')
    if bmg is not None:
        special.bronze_a = bmg.team_a
        special.bronze_b = bmg.team_b
    special.save(
        update_fields=[
            'final_a',
            'final_b',
            'winner',
            'bronze_a',
            'bronze_b',
            'updated_at',
        ]
    )


def fold_text(value) -> str:
    """
    Malá písmena, trim, bez diakritiky — pro porovnání jmen (Pastrňák ≈ Pastrnak).
    """
    if value is None:
        return ''
    if not isinstance(value, str):
        value = str(value)
    value = value.strip().lower()
    if not value:
        return ''
    normalized = unicodedata.normalize('NFD', value)
    return ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')


@transaction.atomic
def calculate_points(cup: Cup):
    """
    Optimized point calculation with proper transaction handling.
    Uses select_related and prefetch_related to avoid N+1 queries.
    """
    # Reset team statistics
    Team.objects.filter(cup=cup).update(
        gp=0, win=0, los=0, wot=0, lot=0, gf=0, ga=0, points=0
    )
    
    # V produkci jen po startu turnaje; při DEBUG=True i dřív (ladění tipů / žebříčku).
    started = is_tournament_started(cup) or settings.DEBUG
    
    # Prefetch all matches with teams
    all_matches = Match.objects.filter(cup=cup).select_related(
        'team_a', 'team_b'
    ).prefetch_related('tips')
    
    # Update team statistics from matches
    teams_dict = {}
    for match in all_matches:
        sa = match.score_a_final if match.score_a_final is not None else match.score_a
        sb = match.score_b_final if match.score_b_final is not None else match.score_b
        if sa is not None and sb is not None:
            team_a = match.team_a
            team_b = match.team_b
            
            if team_a.id not in teams_dict:
                teams_dict[team_a.id] = team_a
            if team_b.id not in teams_dict:
                teams_dict[team_b.id] = team_b
            
            team_a = teams_dict[team_a.id]
            team_b = teams_dict[team_b.id]
            
            team_a.gp += 1
            team_b.gp += 1
            
            # Determine winner (overtime => 2+1 pts, else regulation 3 pts)
            if match.overtime:
                if sa > sb:
                    team_a.wot += 1
                    team_b.lot += 1
                    team_a.points += 2
                    team_b.points += 1
                elif sa < sb:
                    team_b.wot += 1
                    team_a.lot += 1
                    team_b.points += 2
                    team_a.points += 1
            else:
                if match.score_a > match.score_b:
                    team_a.win += 1
                    team_b.los += 1
                    team_a.points += 3
                elif match.score_a < match.score_b:
                    team_b.win += 1
                    team_a.los += 1
                    team_b.points += 3
            
            team_a.gf += sa
            team_a.ga += sb
            team_b.gf += sb
            team_b.ga += sa
    
    # Update playoff statistics
    playoffs = Playoff.objects.filter(cup=cup).select_related('team_a', 'team_b')
    for playoff in playoffs:
        if playoff.team_a_id is None or playoff.team_b_id is None:
            continue
        if playoff.score_a_final is not None and playoff.score_b_final is not None:
            team_a = playoff.team_a
            team_b = playoff.team_b
            
            if team_a.id not in teams_dict:
                teams_dict[team_a.id] = team_a
            if team_b.id not in teams_dict:
                teams_dict[team_b.id] = team_b
            
            team_a = teams_dict[team_a.id]
            team_b = teams_dict[team_b.id]
            
            team_a.gp += 1
            team_b.gp += 1
            team_a.gf += playoff.score_a_final
            team_a.ga += playoff.score_b_final
            team_b.gf += playoff.score_b_final
            team_b.ga += playoff.score_a_final
    
    # Bulk update teams
    if teams_dict:
        Team.objects.bulk_update(teams_dict.values(), [
            'gp', 'win', 'los', 'wot', 'lot', 'gf', 'ga', 'points'
        ])

    sync_special_from_playoffs(cup)
    sync_special_derived_stats(cup)

    # Calculate user points
    users = User.objects.filter(is_active=True).prefetch_related(
        Prefetch('match_tips', queryset=MatchTip.objects.select_related('match')),
        Prefetch('special_tips', queryset=SpecialTip.objects.select_related(
            'cup', 'final_a', 'final_b', 'bronze_a', 'bronze_b'
        ))
    )

    special = Special.objects.filter(cup=cup).select_related(
        'winner',
        'final_a', 'final_b', 'bronze_a', 'bronze_b',
        'group_a_1', 'group_b_1', 'group_a_2', 'group_b_2',
        'group_a_3', 'group_b_3', 'group_a_4', 'group_b_4',
        'team_most_goals', 'team_least_goals', 'team_first_goal', 'team_last_goal',
        'team_drop_a', 'team_drop_b',
    ).first()
    
    user_points_to_update = []
    
    for user in users:
        # Part A: Match tips (get_or_create already saves when creating, so we only update)
        user_point_a, _ = UserPoint.objects.get_or_create(
            user=user, cup=cup, part='A',
            defaults={'points': 0}
        )
        user_point_a.points = 0
        
        if started:
            for match_tip in user.match_tips.all():
                match = match_tip.match
                if match.cup_id != cup.id:
                    continue
                if match.score_a is not None and match.score_b is not None:
                    if match_tip.score_a == match.score_a and match_tip.score_b == match.score_b:
                        user_point_a.points += 7
                    elif ((match.score_a > match.score_b and match_tip.score_a > match_tip.score_b) or
                          (match.score_a < match.score_b and match_tip.score_a < match_tip.score_b) or
                          (match.score_a == match.score_b and match_tip.score_a == match_tip.score_b)):
                        user_point_a.points += 3
        
        user_points_to_update.append(user_point_a)
        
        # Part B: Special tips
        user_point_b, _ = UserPoint.objects.get_or_create(
            user=user, cup=cup, part='B',
            defaults={'points': 0}
        )
        user_point_b.points = 0
        
        special_tip = user.special_tips.filter(cup=cup).first()
        if special_tip and special and started:
            if special.winner_id and special.winner_id == special_tip.winner_id:
                user_point_b.points += 24
            
            matched_conditions = set()
            # Compare by ID so we don't rely on FK instance identity
            sa_id = special.final_a_id
            sb_id = special.final_b_id
            ta_id = special_tip.final_a_id
            tb_id = special_tip.final_b_id
            if sa_id and (sa_id == ta_id or sa_id == tb_id):
                if 'final_a' not in matched_conditions:
                    user_point_b.points += 16
                    matched_conditions.add('final_a')
            if sb_id and (sb_id == tb_id or sb_id == ta_id):
                if 'final_b' not in matched_conditions:
                    user_point_b.points += 16
                    matched_conditions.add('final_b')
            ba_id = special.bronze_a_id
            bb_id = special.bronze_b_id
            bta_id = special_tip.bronze_a_id
            btb_id = special_tip.bronze_b_id
            if ba_id and (ba_id == bta_id or ba_id == btb_id):
                if 'bronze_a' not in matched_conditions:
                    user_point_b.points += 12
                    matched_conditions.add('bronze_a')
            if bb_id and (bb_id == btb_id or bb_id == bta_id):
                if 'bronze_b' not in matched_conditions:
                    user_point_b.points += 12
                    matched_conditions.add('bronze_b')
            
            # Other special predictions
            checks = [
                ('czech_shooter_first', 12),
                ('czech_shooter_last', 12),
                ('max_goals_per_game', 12),
                ('group_a_1', 9),
                ('group_b_1', 9),
                ('group_a_2', 6),
                ('group_b_2', 6),
                ('group_a_3', 6),
                ('group_b_3', 6),
                ('group_a_4', 6),
                ('group_b_4', 6),
                ('team_most_goals', 12),
                ('team_least_goals', 12),
                ('team_first_goal', 3),
                ('team_last_goal', 12),
                ('team_drop_a', 6),
                ('team_drop_b', 6),
                ('overtimes', 24),
            ]
            
            for field, points in checks:
                val_res = getattr(special, field)
                val_tip = getattr(special_tip, field)
                if field in ('czech_shooter_first', 'czech_shooter_last'):
                    folded_res = fold_text(val_res)
                    if folded_res and folded_res == fold_text(val_tip):
                        user_point_b.points += points
                elif val_res == val_tip:
                    user_point_b.points += points
        
        user_points_to_update.append(user_point_b)
        
        # Part C: Total points
        user_point_c, _ = UserPoint.objects.get_or_create(
            user=user, cup=cup, part='C',
            defaults={'points': user_point_a.points + user_point_b.points}
        )
        user_point_c.points = user_point_a.points + user_point_b.points
        
        user_points_to_update.append(user_point_c)
    
    if user_points_to_update:
        UserPoint.objects.bulk_update(user_points_to_update, ['points'])
