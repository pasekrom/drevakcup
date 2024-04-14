from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from core.models import User
from iihf.models import Team, Match, MatchTip, Playoff


class Home(TemplateView):
    template_name = 'iihf/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = kwargs.get('year')

        users = User.objects.all().order_by('name')
        match_list = Match.objects.filter(cup__year=year).order_by('date', 'team_a__group')
        all_match_tips = MatchTip.objects.all()

        context['year'] = year
        context['users'] = users
        context['match_list'] = match_list
        context['all_match_tips'] = all_match_tips
        return context


class Teams(TemplateView):
    template_name = 'iihf/teams.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = kwargs.get('year')

        teams = Team.objects.filter(year=year).order_by('-points', 'name')
        teams_a = Team.objects.filter(year=year, group='A').order_by('-points', 'name')
        teams_b = Team.objects.filter(year=year, group='B').order_by('-points', 'name')
        playoff = Playoff.objects.filter(cup__year=year)

        context['year'] = year
        context['teams'] = teams
        context['teams_a'] = teams_a
        context['teams_b'] = teams_b
        context['playoff_list'] = playoff
        return context


class Ladder(TemplateView):
    template_name = 'iihf/ladder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = kwargs.get('year')
        return context


class Rules(TemplateView):
    template_name = 'iihf/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = kwargs.get('year')
        return context
