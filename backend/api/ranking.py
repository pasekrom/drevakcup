"""
Kritéria pořadí při rovnosti celkových bodů (A + B).
"""
from __future__ import annotations

from .models import Cup, MatchTip, Special, SpecialTip


def tiebreak_defaults() -> dict:
    return {
        'winner_guessed': False,
        'exact_7_count': 0,
        'final_b_guessed': False,
    }


def winner_tip_hit(special: Special | None, special_tip: SpecialTip | None) -> bool:
    if not special or not special_tip:
        return False
    return bool(special.winner_id and special.winner_id == special_tip.winner_id)


def final_b_tip_hit(special: Special | None, special_tip: SpecialTip | None) -> bool:
    """Uhádnutí tipu „Finalista 2“ (stejná logika jako bodování v services)."""
    if not special or not special_tip:
        return False
    sb_id = special.final_b_id
    if not sb_id:
        return False
    ta_id = special_tip.final_a_id
    tb_id = special_tip.final_b_id
    return sb_id == tb_id or sb_id == ta_id


def load_tiebreak_stats(cup: Cup, user_ids: set[int]) -> dict[int, dict]:
    """Vrátí tiebreak pole pro každého uživatele z user_ids."""
    result = {uid: tiebreak_defaults() for uid in user_ids}
    if not user_ids:
        return result

    special = Special.objects.filter(cup=cup).first()
    stips = {
        st.user_id: st
        for st in SpecialTip.objects.filter(cup=cup, user_id__in=user_ids)
    }

    for uid in user_ids:
        st = stips.get(uid)
        result[uid] = {
            'winner_guessed': winner_tip_hit(special, st),
            'exact_7_count': 0,
            'final_b_guessed': final_b_tip_hit(special, st),
        }

    for tip in MatchTip.objects.filter(match__cup=cup, user_id__in=user_ids).select_related('match'):
        match = tip.match
        if match.score_a is None or match.score_b is None:
            continue
        if tip.score_a == match.score_a and tip.score_b == match.score_b:
            result[tip.user_id]['exact_7_count'] += 1

    return result


def ladder_sort_key(entry: dict) -> tuple:
    user = entry['user']
    name = (getattr(user, 'email', None) or getattr(user, 'name', None) or '').lower()
    tb = entry.get('tiebreak') or tiebreak_defaults()
    return (
        -entry['points_c'],
        -entry['points_a'],
        -int(tb['winner_guessed']),
        -tb['exact_7_count'],
        -int(tb['final_b_guessed']),
        name,
    )
