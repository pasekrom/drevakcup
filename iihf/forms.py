from django import forms
from .models import MatchTip, SpecialTip


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
