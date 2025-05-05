from django import forms
from django.db.models import Q

from .models import MatchTip, SpecialTip, Team


class MatchTipForm(forms.Form):
    def __init__(self, *args, matches=None, match_tips=None, **kwargs):
        super().__init__(*args, **kwargs)
        if matches:
            for match in matches:
                self.fields[f'score_a_{match.id}'] = forms.IntegerField(
                    label=f"{match.team_a.name} góly", min_value=0, required=False)
                self.fields[f'score_b_{match.id}'] = forms.IntegerField(
                    label=f"{match.team_b.name} góly", min_value=0, required=False)

                # If tips exist, pre-fill
                if match_tips and match.id in match_tips and match_tips[match.id]:
                    self.fields[f'score_a_{match.id}'].initial = match_tips[match.id].score_a
                    self.fields[f'score_b_{match.id}'].initial = match_tips[match.id].score_b


class SpecialTipForm(forms.ModelForm):
    class Meta:
        model = SpecialTip
        exclude = ['user', 'cup']
        labels = {
            'winner': 'Vítěz',
            'final_a': 'Finalista 1',
            'final_b': 'Finalista 2',
            'bronze_a': 'Tým 1, který se utká o bronz',
            'bronze_b': 'Tým 2, který se utká o bronz',
            'czech_shooter_first': 'Český střelec 1. gólu',
            'czech_shooter_last': 'Český střelec posledního gólu',
            'max_goals_per_game': 'Nejvíce branek v jednom utkání (dohromady)',
            'group_a_1': 'Vítěz skupiny A',
            'group_b_1': 'Vítěz skupiny B',
            'group_a_2': '2. místo ve skupině A',
            'group_b_2': '2. místo ve skupině B',
            'group_a_3': '3. místo ve skupině A',
            'group_b_3': '3. místo ve skupině B',
            'group_a_4': '4. místo ve skupině A',
            'group_b_4': '4. místo ve skupině B',
            'team_most_goals': 'Tým, který vstřelí nejvíce branek (celkem na MS)',
            'team_least_goals': 'Tým, který obdrží nejméně branek (celkem na MS)',
            'team_first_goal': 'Tým, který vstřelí první branku na MS',
            'team_last_goal': 'Tým, který vstřelí poslední branku na MS',
            'team_drop_a': 'Tým, který sestoupí ve skupině A',
            'team_drop_b': 'Tým, který sestoupí ve skupině B',
            'overtimes': 'Počet remíz/prodloužení (celkem za MS)',
        }

    def __init__(self, *args, cup=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cup:
            year = cup.year
            all_teams = Team.objects.filter(Q(year=year), Q(group__in=['A', 'B']))
            group_a_teams = Team.objects.filter(year=year, group='A')
            group_b_teams = Team.objects.filter(year=year, group='B')

            for field in [
                'winner', 'final_a', 'final_b', 'bronze_a', 'bronze_b',
                'team_most_goals', 'team_least_goals',
                'team_first_goal', 'team_last_goal'
            ]:
                self.fields[field].queryset = all_teams

            for field in ['group_a_1', 'group_a_2', 'group_a_3', 'group_a_4', 'team_drop_a']:
                self.fields[field].queryset = group_a_teams

            for field in ['group_b_1', 'group_b_2', 'group_b_3', 'group_b_4', 'team_drop_b']:
                self.fields[field].queryset = group_b_teams
            