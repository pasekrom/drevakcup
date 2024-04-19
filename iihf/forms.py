from django import forms
from django.db.models import Q

from .models import MatchTip, SpecialTip, Team


class MatchTipForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        match_tips = kwargs.pop('match_tips', None)
        super(MatchTipForm, self).__init__(*args, **kwargs)
        if match_tips:
            for match_id, match_tip in match_tips.items():
                if match_tip:
                    self.fields[f'score_a_{match_id}'].initial = match_tip.score_a
                    self.fields[f'score_b_{match_id}'].initial = match_tip.score_b

    class Meta:
        model = MatchTip
        fields = ['score_a', 'score_b']


class SpecialTipForm(forms.ModelForm):
    class Meta:
        model = SpecialTip
        exclude = ['user', 'cup']  # Exclude user and cup fields from the form
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

    def save(self, user, commit=True):
        # Check if a SpecialTip instance already exists for the user
        special_tip_instance = SpecialTip.objects.filter(user=user).first()

        # If an instance exists, update its fields with the form data
        if special_tip_instance:
            for field, value in self.cleaned_data.items():
                setattr(special_tip_instance, field, value)
        else:
            # If no instance exists, create a new one and assign the user
            special_tip_instance = super().save(commit=False)
            special_tip_instance.user = user

        # Save the instance to the database
        if commit:
            special_tip_instance.save()

        return special_tip_instance

    def __init__(self, *args, cup=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cup:
            year = cup.year
            self.fields['winner'].queryset = self.fields['final_a'].queryset = self.fields['final_b'].queryset = \
                self.fields['bronze_a'].queryset = self.fields['bronze_b'].queryset = \
                self.fields['team_most_goals'].queryset = self.fields['team_least_goals'].queryset = \
                self.fields['team_first_goal'].queryset = self.fields['team_last_goal'].queryset = \
                Team.objects.filter(Q(year=year) & (Q(group='A') | Q(group='B')))

            self.fields['group_a_1'].queryset = self.fields['group_a_2'].queryset = \
                self.fields['group_a_3'].queryset = self.fields['group_a_4'].queryset = \
                self.fields['team_drop_a'].queryset = Team.objects.filter(Q(year=year) & (Q(group='A')))

            self.fields['group_b_1'].queryset = self.fields['group_b_2'].queryset = \
                self.fields['group_b_3'].queryset = self.fields['group_b_4'].queryset = \
                self.fields['team_drop_b'].queryset = Team.objects.filter(Q(year=year) & (Q(group='B')))
            