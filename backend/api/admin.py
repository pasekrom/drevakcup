"""
Django admin configuration.
"""
from django.contrib import admin
from .models import (
    User, Cup, Team, Match, Playoff, MatchTip, SpecialTip, Special, UserPoint
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'first_name', 'last_name', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'name', 'first_name', 'last_name']


@admin.register(Cup)
class CupAdmin(admin.ModelAdmin):
    list_display = ['year', 'location', 'date_start', 'date_end']
    list_filter = ['year']
    search_fields = ['location']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'year', 'group', 'points', 'gp', 'win', 'los']
    list_filter = ['year', 'group', 'cup']
    search_fields = ['name']
    ordering = ['-year', '-points']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['date', 'team_a', 'team_b', 'score_a', 'score_b', 'cup']
    list_filter = ['cup', 'date', 'overtime', 'shootout']
    search_fields = ['team_a__name', 'team_b__name']
    date_hierarchy = 'date'


@admin.register(Playoff)
class PlayoffAdmin(admin.ModelAdmin):
    list_display = ['playoff_type', 'date', 'team_a', 'team_b', 'score_a', 'score_b', 'cup']
    list_filter = ['cup', 'playoff_type', 'date']
    search_fields = ['team_a__name', 'team_b__name']


@admin.register(MatchTip)
class MatchTipAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'score_a', 'score_b']
    list_filter = ['match__cup', 'match__date']
    search_fields = ['user__email', 'match__team_a__name', 'match__team_b__name']


@admin.register(SpecialTip)
class SpecialTipAdmin(admin.ModelAdmin):
    list_display = ['user', 'cup', 'winner']
    list_filter = ['cup']
    search_fields = ['user__email']


@admin.register(Special)
class SpecialAdmin(admin.ModelAdmin):
    list_display = ['cup', 'winner', 'final_a', 'final_b']
    list_filter = ['cup']
    readonly_fields = [
        'winner',
        'final_a',
        'final_b',
        'bronze_a',
        'bronze_b',
        'team_most_goals',
        'team_least_goals',
        'max_goals_per_game',
        'overtimes',
    ]


@admin.register(UserPoint)
class UserPointAdmin(admin.ModelAdmin):
    list_display = ['user', 'cup', 'part', 'points']
    list_filter = ['cup', 'part']
    search_fields = ['user__email']
    ordering = ['-cup__year', '-points']
