from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, Exists, OuterRef, F
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, FormView

from core.models import User
from iihf.forms import MatchTipForm, SpecialTipForm
from iihf.models import Team, Match, MatchTip, Playoff, Special, SpecialTip, Cup, UserPoint


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'iihf/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = kwargs.get('year')

        # calculate_points(self.request, year)

        authenticated_user = self.request.user
        # other_users = User.objects.exclude(pk=authenticated_user.pk).exclude(is_active=False).order_by('name')

        other_users = User.objects.exclude(
            pk=authenticated_user.pk
        ).annotate(
            has_match_tip=Exists(
                MatchTip.objects.filter(
                    user=OuterRef('pk'),
                    match__cup__year=year
                )
            )
        ).filter(
            has_match_tip=True,
            is_active=True
        ).order_by('name')

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
        all_match_tips = MatchTip.objects.filter(match__cup__year=year)

        special_tips = SpecialTip.objects.filter(cup__year=year)

        user_points_a = UserPoint.objects.filter(cup__year=year, part='A')
        user_points_b = UserPoint.objects.filter(cup__year=year, part='B')
        user_points_c = UserPoint.objects.filter(cup__year=year, part='C')

        context['year'] = year
        context['users'] = users
        context['match_list'] = match_list
        context['all_match_tips'] = all_match_tips
        context['started'] = started
        context['special'] = special
        context['special_tips'] = special_tips
        context['user_points_a'] = user_points_a
        context['user_points_b'] = user_points_b
        context['user_points_c'] = user_points_c
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

        year = kwargs.get('year')

        # calculate_points(self.request, year)

        users = User.objects.annotate(
            total_points_c=Sum('userpoint__points', filter=Q(userpoint__cup__year=year, userpoint__part='C')),
            has_match_tip=Exists(
                MatchTip.objects.filter(
                    user=OuterRef('pk'),
                    match__cup__year=year
                )
            )
        ).filter(
            is_active=True,
            has_match_tip=True
        ).order_by('-total_points_c')

        user_points_a = UserPoint.objects.filter(cup__year=year, part='A')
        user_points_b = UserPoint.objects.filter(cup__year=year, part='B')
        user_points_c = UserPoint.objects.filter(cup__year=year, part='C')

        context['year'] = kwargs.get('year')
        context['users'] = users
        context['user_points_a'] = user_points_a
        context['user_points_b'] = user_points_b
        context['user_points_c'] = user_points_c
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
    form_class = SpecialTipForm

    def get(self, request, *args, **kwargs):
        year = kwargs.get('year')
        cup = get_object_or_404(Cup, year=year)
        form = self.form_class(cup=cup)
        return render(request, self.template_name, {'form': form, 'year': year})

    def post(self, request, *args, **kwargs):
        year = kwargs.get('year')
        cup = get_object_or_404(Cup, year=year)
        form = SpecialTipForm(request.POST, cup=cup)
        if form.is_valid():
            try:
                # Get or create a SpecialTip object for the current user
                special_tip, created = SpecialTip.objects.get_or_create(user=request.user, cup=cup)

                # Update the SpecialTip object with the form data
                for field in form.cleaned_data:
                    setattr(special_tip, field, form.cleaned_data[field])

                # Save the changes
                special_tip.save()

                # Redirect to a success URL
                return redirect('iihf-home', year=kwargs.get('year'))
            except Exception as e:
                # Handle any unexpected errors
                print(f"Error saving SpecialTip: {e}")
                # You can customize error handling here, such as displaying a message to the user
                pass
        else:
            # If the form is not valid, re-render the form with errors
            return render(request, self.template_name, {'form': form, 'year': kwargs.get('year')})


def reset_team_statistics():
    # Reset team statistics
    Team.objects.update(
        gp=0,
        win=0,
        los=0,
        wot=0,
        lot=0,
        gf=0,
        ga=0,
        points=0
    )


def calculate_points(request, year):
    cup = Cup.objects.get(year=year)
    reset_team_statistics()

    users = User.objects.all()
    all_matches = Match.objects.filter(cup=cup)
    playoffs = Playoff.objects.filter(cup=cup)
    special = Special.objects.filter(cup=cup).first()

    started = False

    match_list = Match.objects.filter(cup=cup).order_by('date', 'team_a__group')

    if match_list:
        start_date = Match.objects.filter(cup=cup).order_by('date', 'team_a__group').values('date').first()
        start_date = start_date['date']
        start_date = start_date.astimezone(timezone.get_current_timezone())
        start_date_formatted = start_date.strftime("%Y-%m-%d %H:%M:%S.%f")
        current_date = str(datetime.now())
        if current_date > start_date_formatted:
            started = True
        else:
            started = False

    for match in all_matches:
        # Fetch team instances separately for each team in the match
        team_a = Team.objects.get(name=match.team_a.name, year=cup.year)
        team_b = Team.objects.get(name=match.team_b.name, year=cup.year)

        # Increment games played count for each team
        if match.score_a_final is not None and match.score_b_final is not None:
            team_a.gp += 1
            team_b.gp += 1

            # Update other team statistics based on match result
            if match.score_a > match.score_b:
                team_a.win += 1
                team_b.los += 1
                team_a.points += 3
            elif match.score_a < match.score_b:
                team_b.win += 1
                team_a.los += 1
                team_b.points += 3
            elif match.score_a_final > match.score_b_final:
                team_a.wot += 1
                team_b.lot += 1
                team_a.points += 2
                team_b.points += 1
            elif match.score_a_final < match.score_b_final:
                team_b.wot += 1
                team_a.lot += 1
                team_b.points += 2
                team_a.points += 1

            team_a.gf += match.score_a_final
            team_a.ga += match.score_b_final
            team_b.gf += match.score_b_final
            team_b.ga += match.score_a_final

            # Save the updated team statistics
            team_a.save()
            team_b.save()

    for match in playoffs:
        # Fetch team instances separately for each team in the match
        team_a = Team.objects.get(name=match.team_a.name, year=cup.year)
        team_b = Team.objects.get(name=match.team_b.name, year=cup.year)

        # Increment games played count for each team
        if match.score_a_final is not None and match.score_b_final is not None:
            team_a.gp += 1
            team_b.gp += 1

            team_a.gf += match.score_a_final
            team_a.ga += match.score_b_final
            team_b.gf += match.score_b_final
            team_b.ga += match.score_a_final

            # Save the updated team statistics
            team_a.save()
            team_b.save()

    for user in users:
        user_point, created = UserPoint.objects.get_or_create(user=user, cup=cup, part='A')
        user_point.points = 0

        if started:
            for match in all_matches:
                match_tips = MatchTip.objects.filter(match=match, user=user)

                for match_tip in match_tips:
                    if match.score_a is not None and match.score_b is not None:
                        if match_tip.score_a == match.score_a and match_tip.score_b == match.score_b:
                            user_point.points += 7
                        elif (match.score_a > match.score_b and match_tip.score_a > match_tip.score_b) or (
                                match.score_a < match.score_b and match_tip.score_a < match_tip.score_b) or (
                                match.score_a == match.score_b and match_tip.score_a == match_tip.score_b):
                            user_point.points += 3

                    user_point.part = 'A'
                    user_point.save()

        user_point_b, created = UserPoint.objects.get_or_create(user=user, cup=cup, part='B')
        user_point_b.points = 0

        special_tips = SpecialTip.objects.filter(user=user, cup=cup).first()

        if special_tips and special and started:

            if special.winner == special_tips.winner:
                user_point_b.points += 24
            if special.final_a == special_tips.final_a or special.final_a == special_tips.final_b:
                user_point_b.points += 16
            if special.final_b == special_tips.final_b or special.final_b == special_tips.final_a and special_tips.final_a != special_tips.final_b:
                user_point_b.points += 16
            if special.bronze_a == special_tips.bronze_a or special.bronze_a == special_tips.bronze_b:
                user_point_b.points += 12
            if special.bronze_b == special_tips.bronze_b or special.bronze_b == special_tips.bronze_a and special_tips.bronze_a != special_tips.bronze_b:
                user_point_b.points += 12
            if special.czech_shooter_first == special_tips.czech_shooter_first:
                user_point_b.points += 12
            if special.czech_shooter_last == special_tips.czech_shooter_last:
                user_point_b.points += 12
            if special.max_goals_per_game == special_tips.max_goals_per_game:
                user_point_b.points += 12
            if special.group_a_1 == special_tips.group_a_1:
                user_point_b.points += 9
            if special.group_b_1 == special_tips.group_b_1:
                user_point_b.points += 9
            if special.group_a_2 == special_tips.group_a_2:
                user_point_b.points += 6
            if special.group_b_2 == special_tips.group_b_2:
                user_point_b.points += 6
            if special.group_a_3 == special_tips.group_a_3:
                user_point_b.points += 6
            if special.group_b_3 == special_tips.group_b_3:
                user_point_b.points += 6
            if special.group_a_4 == special_tips.group_a_4:
                user_point_b.points += 6
            if special.group_b_4 == special_tips.group_b_4:
                user_point_b.points += 6
            if special.team_most_goals == special_tips.team_most_goals:
                user_point_b.points += 12
            if special.team_least_goals == special_tips.team_least_goals:
                user_point_b.points += 12
            if special.team_first_goal == special_tips.team_first_goal:
                user_point_b.points += 3
            if special.team_last_goal == special_tips.team_last_goal:
                user_point_b.points += 12
            if special.team_drop_a == special_tips.team_drop_a:
                user_point_b.points += 6
            if special.team_drop_b == special_tips.team_drop_b:
                user_point_b.points += 6
            if special.overtimes == special_tips.overtimes:
                user_point_b.points += 24

        user_point_b.part = 'B'
        user_point_b.save()

        user_point_c, created = UserPoint.objects.get_or_create(user=user, cup=cup, part='C')
        user_point_c.points = user_point.points + user_point_b.points

        user_point_c.part = 'C'
        user_point_c.save()

    return redirect('home')
