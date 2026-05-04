"""
Data pro přehledovou tabulku tipů všech uživatelů (zápasy + speciál).
"""
from __future__ import annotations

from django.templatetags.static import static as django_static

from .flag_urls import public_or_request_url
from .models import Cup, Match, MatchTip, Special, SpecialTip, Team, User, UserPoint
from .team_flags import get_team_display_label
from .services import is_tournament_started


# (tip_field na SpecialTip, klíč výsledku ve flat dict, popisek, body, mód, typ: team|text|number)
SPECIAL_MATRIX_ROWS: list[tuple[str, str, str, int, str, str]] = [
    ('winner_id', 'winner_id', 'Vítěz', 24, 'exact', 'team'),
    ('final_a_id', 'final_a_id', 'Finalista 1', 16, 'either_final', 'team'),
    ('final_b_id', 'final_b_id', 'Finalista 2', 16, 'either_final', 'team'),
    ('bronze_a_id', 'bronze_a_id', 'Tým 1, který se utká o bronz', 12, 'either_bronze', 'team'),
    ('bronze_b_id', 'bronze_b_id', 'Tým 2, který se utká o bronz', 12, 'either_bronze', 'team'),
    ('czech_shooter_first', 'czech_shooter_first', 'Český střelec 1. gólu', 12, 'fold_text', 'text'),
    ('czech_shooter_last', 'czech_shooter_last', 'Český střelec posledního gólu', 12, 'fold_text', 'text'),
    ('max_goals_per_game', 'max_goals_per_game', 'Nejvíce branek v jednom utkání (dohromady)', 12, 'exact_num', 'number'),
    ('group_a_1_id', 'group_a_1_id', 'Vítěz skupiny A', 9, 'exact', 'team'),
    ('group_b_1_id', 'group_b_1_id', 'Vítěz skupiny B', 9, 'exact', 'team'),
    ('group_a_2_id', 'group_a_2_id', '2. místo ve skupině A', 6, 'exact', 'team'),
    ('group_b_2_id', 'group_b_2_id', '2. místo ve skupině B', 6, 'exact', 'team'),
    ('group_a_3_id', 'group_a_3_id', '3. místo ve skupině A', 6, 'exact', 'team'),
    ('group_b_3_id', 'group_b_3_id', '3. místo ve skupině B', 6, 'exact', 'team'),
    ('group_a_4_id', 'group_a_4_id', '4. místo ve skupině A', 6, 'exact', 'team'),
    ('group_b_4_id', 'group_b_4_id', '4. místo ve skupině B', 6, 'exact', 'team'),
    ('team_most_goals_id', 'team_most_goals_id', 'Tým – nejvíce vstřelených branek', 12, 'exact', 'team'),
    ('team_least_goals_id', 'team_least_goals_id', 'Tým – nejméně obdržených branek', 12, 'exact', 'team'),
    ('team_first_goal_id', 'team_first_goal_id', 'Tým – první branka MS', 3, 'exact', 'team'),
    ('team_last_goal_id', 'team_last_goal_id', 'Tým – poslední branka MS', 12, 'exact', 'team'),
    ('team_drop_a_id', 'team_drop_a_id', 'Sestup ze skupiny A', 6, 'exact', 'team'),
    ('team_drop_b_id', 'team_drop_b_id', 'Sestup ze skupiny B', 6, 'exact', 'team'),
    ('overtimes', 'overtimes', 'Počet remíz/prodloužení (celkem za MS)', 24, 'exact_num', 'number'),
]


def _special_to_flat(sp: Special) -> dict:
    return {
        'winner_id': sp.winner_id,
        'final_a_id': sp.final_a_id,
        'final_b_id': sp.final_b_id,
        'bronze_a_id': sp.bronze_a_id,
        'bronze_b_id': sp.bronze_b_id,
        'czech_shooter_first': sp.czech_shooter_first or '',
        'czech_shooter_last': sp.czech_shooter_last or '',
        'max_goals_per_game': sp.max_goals_per_game,
        'group_a_1_id': sp.group_a_1_id,
        'group_b_1_id': sp.group_b_1_id,
        'group_a_2_id': sp.group_a_2_id,
        'group_b_2_id': sp.group_b_2_id,
        'group_a_3_id': sp.group_a_3_id,
        'group_b_3_id': sp.group_b_3_id,
        'group_a_4_id': sp.group_a_4_id,
        'group_b_4_id': sp.group_b_4_id,
        'team_most_goals_id': sp.team_most_goals_id,
        'team_least_goals_id': sp.team_least_goals_id,
        'team_first_goal_id': sp.team_first_goal_id,
        'team_last_goal_id': sp.team_last_goal_id,
        'team_drop_a_id': sp.team_drop_a_id,
        'team_drop_b_id': sp.team_drop_b_id,
        'overtimes': sp.overtimes,
    }


def _team_dict_for_matrix(team: Team, request) -> dict:
    """Zkratka + URL vlajky (stejná logika jako TeamSerializer)."""
    from .team_flags import get_team_flag_shortcut

    sc = get_team_flag_shortcut(team.name)
    code_upper = sc.upper() if sc else None
    flag_url = None
    if team.flag:
        u = team.flag.url
        flag_url = u if u.startswith('http') else public_or_request_url(request, u)
    elif sc:
        rel = django_static(f'team_flags/{sc}.png')
        flag_url = public_or_request_url(request, rel)
    return {
        'id': team.id,
        'name': team.name,
        'display_name': get_team_display_label(team.name),
        'shortcut': code_upper,
        'flag_url': flag_url,
    }


def _special_tip_to_flat(st: SpecialTip) -> dict:
    return {
        'winner_id': st.winner_id,
        'final_a_id': st.final_a_id,
        'final_b_id': st.final_b_id,
        'bronze_a_id': st.bronze_a_id,
        'bronze_b_id': st.bronze_b_id,
        'czech_shooter_first': st.czech_shooter_first or '',
        'czech_shooter_last': st.czech_shooter_last or '',
        'max_goals_per_game': st.max_goals_per_game,
        'group_a_1_id': st.group_a_1_id,
        'group_b_1_id': st.group_b_1_id,
        'group_a_2_id': st.group_a_2_id,
        'group_b_2_id': st.group_b_2_id,
        'group_a_3_id': st.group_a_3_id,
        'group_b_3_id': st.group_b_3_id,
        'group_a_4_id': st.group_a_4_id,
        'group_b_4_id': st.group_b_4_id,
        'team_most_goals_id': st.team_most_goals_id,
        'team_least_goals_id': st.team_least_goals_id,
        'team_first_goal_id': st.team_first_goal_id,
        'team_last_goal_id': st.team_last_goal_id,
        'team_drop_a_id': st.team_drop_a_id,
        'team_drop_b_id': st.team_drop_b_id,
        'overtimes': st.overtimes,
    }


def build_tips_matrix(cup: Cup, request=None) -> dict:
    started = is_tournament_started(cup)

    user_ids = set(
        MatchTip.objects.filter(match__cup=cup).values_list('user_id', flat=True)
    ) | set(SpecialTip.objects.filter(cup=cup).values_list('user_id', flat=True))
    users = list(
        User.objects.filter(id__in=user_ids, is_active=True)
    )
    points_a = {up.user_id: up.points for up in UserPoint.objects.filter(cup=cup, part='A')}
    points_b = {up.user_id: up.points for up in UserPoint.objects.filter(cup=cup, part='B')}
    user_payload = [
        {
            'id': u.id,
            'display_name': (u.name or '').strip() or u.email,
            'points_part_a': points_a.get(u.id, 0),
            'points_part_b': points_b.get(u.id, 0),
        }
        for u in users
    ]

    matches = list(
        Match.objects.filter(cup=cup)
        .select_related('team_a', 'team_b')
        .order_by('date', 'id')
    )

    tips_qs = MatchTip.objects.filter(match__cup=cup).select_related('user', 'match')
    mt_map: dict[tuple[int, int], MatchTip] = {}
    for t in tips_qs:
        mt_map[(t.match_id, t.user_id)] = t

    matches_out = []
    for m in matches:
        tips_out = {}
        for u in users:
            if not started:
                tips_out[str(u.id)] = None
                continue
            tip = mt_map.get((m.id, u.id))
            if not tip or tip.score_a is None or tip.score_b is None:
                tips_out[str(u.id)] = None
            else:
                tips_out[str(u.id)] = {'score_a': tip.score_a, 'score_b': tip.score_b}
        matches_out.append(
            {
                'id': m.id,
                'date': m.date,
                'team_a': _team_dict_for_matrix(m.team_a, request),
                'team_b': _team_dict_for_matrix(m.team_b, request),
                'score_a': m.score_a,
                'score_b': m.score_b,
                'score_a_final': m.score_a_final,
                'score_b_final': m.score_b_final,
                'overtime': m.overtime,
                'shootout': m.shootout,
                'tips': tips_out,
            }
        )

    special = Special.objects.filter(cup=cup).first()
    special_flat = _special_to_flat(special) if special else None

    stips = {
        st.user_id: st
        for st in SpecialTip.objects.filter(cup=cup).select_related('user')
    }

    special_rows_out = []
    for tip_field, res_field, label, points, mode, ftype in SPECIAL_MATRIX_ROWS:
        res_val = special_flat.get(res_field) if special_flat else None
        tips_cell = {}
        for u in users:
            if not started:
                tips_cell[str(u.id)] = None
                continue
            st = stips.get(u.id)
            if not st:
                tips_cell[str(u.id)] = None
            else:
                flat = _special_tip_to_flat(st)
                tips_cell[str(u.id)] = flat.get(tip_field)
        special_rows_out.append(
            {
                'tip_field': tip_field,
                'result_field': res_field,
                'label': label,
                'points': points,
                'mode': mode,
                'field_type': ftype,
                'result': res_val,
                'tips': tips_cell,
            }
        )

    teams_payload = [
        {
            'id': t.id,
            'name': t.name,
            'display_name': get_team_display_label(t.name),
        }
        for t in Team.objects.filter(cup=cup)
    ]

    return {
        'cup_id': cup.id,
        'tournament_started': started,
        'users': user_payload,
        'teams': teams_payload,
        'matches': matches_out,
        'special_rows': special_rows_out,
        'special_result': special_flat,
        'special_exists': special is not None,
    }
