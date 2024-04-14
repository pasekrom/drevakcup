from django import template


register = template.Library()


@register.filter(name='get_match_tip')
def get_match_tip(table_data, match_id):
    return [row[1] for row in table_data if row[0].id == match_id][0] if table_data else None


@register.filter(name='get_user_tip')
def get_user_tip(match_tips, user_id):
    if hasattr(match_tips, '__iter__'):
        return next((tip for tip in match_tips if tip.user.id == user_id), None)
    return None
