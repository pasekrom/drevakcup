from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, FormView

from core.models import User
from iihf.forms import MatchTipForm, SpecialTipForm
from iihf.models import Team, Match, MatchTip, Playoff, Special, SpecialTip


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'iihf/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = kwargs.get('year')

        authenticated_user = self.request.user
        other_users = User.objects.exclude(pk=authenticated_user.pk).order_by('name')
        users = [authenticated_user] + list(other_users)

        match_list = Match.objects.filter(cup__year=year).order_by('date', 'team_a__group')
        started = False

        special = Special.objects.filter(cup__year=year).first()

        if match_list:
            start_date = Match.objects.filter(cup__year=year).order_by('date', 'team_a__group').values('date').first()
            start_date = start_date['date']
            start_date = start_date.astimezone(timezone.get_current_timezone())
            start_date_formatted = start_date.strftime("%Y-%m-%d %H:%M:%S.%f")
            current_date = str(datetime.now())
            if current_date > start_date_formatted:
                started = True
            else:
                started = False
        all_match_tips = MatchTip.objects.all()

        special_tips = SpecialTip.objects.filter(cup__year=year)

        context['year'] = year
        context['users'] = users
        context['match_list'] = match_list
        context['all_match_tips'] = all_match_tips
        context['started'] = started
        context['special'] = special
        context['special_tips'] = special_tips
        return context


class Teams(LoginRequiredMixin, TemplateView):
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


class Ladder(LoginRequiredMixin, TemplateView):
    template_name = 'iihf/ladder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = kwargs.get('year')
        return context


class Rules(LoginRequiredMixin, TemplateView):
    template_name = 'iihf/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = kwargs.get('year')
        return context


class MatchTipFormView(FormView):
    template_name = 'iihf/form_match_tip.html'
    form_class = MatchTipForm

    def get(self, request, *args, **kwargs):
        matches = Match.objects.filter(cup__year=kwargs.get('year')).order_by('date', 'team_a__group')
        match_tips = {}
        for match in matches:
            try:
                match_tip = MatchTip.objects.get(match=match, user=request.user)
            except MatchTip.DoesNotExist:
                match_tip = None
            match_tips[match.id] = match_tip
        initial_values = {}
        for match_id, match_tip in match_tips.items():
            if match_tip:
                initial_values[f'score_a_{match_id}'] = match_tip.score_a
                initial_values[f'score_b_{match_id}'] = match_tip.score_b
            else:
                initial_values[f'score_a_{match_id}'] = 0
                initial_values[f'score_b_{match_id}'] = 0
        form = MatchTipForm(initial=initial_values)
        return render(request, self.template_name, {'matches': matches, 'form': form, 'year': kwargs.get('year')})

    def post(self, request, *args, **kwargs):
        for match in Match.objects.all():
            score_a = request.POST.get(f'score_a_{match.id}')
            score_b = request.POST.get(f'score_b_{match.id}')

            # Check if both scores are provided
            if score_a is not None and score_b is not None:
                # Check if MatchTip already exists for the current user and match
                try:
                    match_tip = MatchTip.objects.get(match=match, user=request.user)
                except MatchTip.DoesNotExist:
                    match_tip = None

                # Update or create MatchTip instance
                if match_tip:
                    # MatchTip already exists, update scores
                    match_tip.score_a = score_a
                    match_tip.score_b = score_b
                    match_tip.save()
                else:
                    # MatchTip doesn't exist, create new instance
                    MatchTip.objects.create(
                        match=match,
                        user=request.user,
                        score_a=score_a,
                        score_b=score_b
                    )

        return redirect('iihf-home', year=kwargs.get('year'))


class SpecialTipFormView(FormView):
    template_name = 'iihf/form_special.html'
    form_class = SpecialTipForm  # Set the form class here

    def get(self, request, *args, **kwargs):
        form = self.form_class()  # Instantiate the form
        return render(request, self.template_name, {'form': form, 'year': kwargs.get('year')})

    def post(self, request, *args, **kwargs):
        form = SpecialTipForm(request.POST)
        if form.is_valid():
            # Check if the SpecialTip object exists for the current user
            special_tip, created = SpecialTip.objects.get_or_create(user=request.user)

            # Update the existing object with the form data
            special_tip.winner = form.cleaned_data['winner']
            special_tip.final_a = form.cleaned_data['final_a']
            special_tip.final_b = form.cleaned_data['final_b']
            special_tip.bronze_a = form.cleaned_data['bronze_a']
            special_tip.bronze_b = form.cleaned_data['bronze_b']
            special_tip.czech_shooter_first = form.cleaned_data['czech_shooter_first']
            special_tip.czech_shooter_last = form.cleaned_data['czech_shooter_last']
            special_tip.max_goals_per_game = form.cleaned_data['max_goals_per_game']
            special_tip.group_a_1 = form.cleaned_data['group_a_1']
            special_tip.group_b_1 = form.cleaned_data['group_b_1']
            special_tip.group_a_2 = form.cleaned_data['group_a_2']
            special_tip.group_b_2 = form.cleaned_data['group_b_2']
            special_tip.group_a_3 = form.cleaned_data['group_a_3']
            special_tip.group_b_3 = form.cleaned_data['group_b_3']
            special_tip.group_a_4 = form.cleaned_data['group_a_4']
            special_tip.group_b_4 = form.cleaned_data['group_b_4']
            special_tip.team_most_goals = form.cleaned_data['team_most_goals']
            special_tip.team_least_goals = form.cleaned_data['team_least_goals']
            special_tip.team_first_goal = form.cleaned_data['team_first_goal']
            special_tip.team_last_goal = form.cleaned_data['team_last_goal']
            special_tip.team_drop_a = form.cleaned_data['team_drop_a']
            special_tip.team_drop_b = form.cleaned_data['team_drop_b']
            special_tip.overtimes = form.cleaned_data['overtimes']

            # Save the changes
            special_tip.save()
            # Redirect to a success URL or any other page
            return redirect('iihf-home', year=kwargs.get('year'))
        else:
            # If the form is not valid, handle the error (redirect, display message, etc.)
            pass  # Handle form errors here