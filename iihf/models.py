from django.db import models

from core.models import User


class Team(models.Model):
    name = models.CharField(max_length=255)
    flag = models.ImageField(upload_to='team_flags/', null=True, blank=True)
    gp = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    los = models.IntegerField(default=0)
    wot = models.IntegerField(default=0)
    lot = models.IntegerField(default=0)
    gf = models.IntegerField(default=0)
    ga = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    year = models.IntegerField(default=2024)
    group = models.CharField(max_length=1, default='A')

    def __str__(self):
        return f'{self.year}: {self.name}'


class Cup(models.Model):
    year = models.IntegerField(default=2024, unique=True)
    logo = models.ImageField(upload_to='iihf_logo/', null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.year}: {self.location}'


class Match(models.Model):
    team_a = models.ForeignKey(Team, related_name='matches_team_a', on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name='matches_team_b', on_delete=models.CASCADE)
    score_a = models.IntegerField(blank=True, null=True)
    score_b = models.IntegerField(blank=True, null=True)
    score_a_final = models.IntegerField(blank=True, null=True)
    score_b_final = models.IntegerField(blank=True, null=True)
    overtime = models.BooleanField(default=False)
    shootout = models.BooleanField(default=False)
    date = models.DateTimeField()
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.date} - {self.team_a.name}:{self.team_b.name}'


class Playoff(models.Model):
    PLAYOFF = [
        ('QFA1', 'QFA1'),
        ('QFA2', 'QFA2'),
        ('QFB1', 'QFB1'),
        ('QFB2', 'QFB2'),
        ('SFA', 'SFA'),
        ('SFB', 'SFB'),
        ('BMG', 'BMG'),
        ('GMG', 'GMG')
    ]
    playoff = models.CharField(max_length=4, choices=PLAYOFF)
    team_a = models.ForeignKey(Team, related_name='playoff_team_a', on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name='playoff_team_b', on_delete=models.CASCADE)
    score_a = models.IntegerField(blank=True, null=True)
    score_b = models.IntegerField(blank=True, null=True)
    ot = models.CharField(max_length=1, blank=True)
    so = models.CharField(max_length=1, blank=True)
    date = models.DateTimeField()
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.playoff} - {self.team_a.name}:{self.team_b.name}'


class MatchTip(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_a = models.IntegerField()
    score_b = models.IntegerField()

    def __str__(self):
        return f'{self.user} - {self.match}'


class Special(models.Model):
    winner = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_winner_special_tips')
    final_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_final_a_special_tips')
    final_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_final_b_special_tips')
    bronze_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_bronze_a_special_tips')
    bronze_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_bronze_b_special_tips')
    czech_shooter_first = models.CharField(max_length=64, blank=True)
    czech_shooter_last = models.CharField(max_length=64, blank=True)
    max_goals_per_game = models.IntegerField(default=0)
    group_a_1 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_a_1_special_tips')
    group_b_1 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_b_1_special_tips')
    group_a_2 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_a_2_special_tips')
    group_b_2 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_b_2_special_tips')
    group_a_3 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_a_3_special_tips')
    group_b_3 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_b_3_special_tips')
    group_a_4 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_a_4_special_tips')
    group_b_4 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_group_b_4_special_tips')
    team_most_goals = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_most_goals_special_tips')
    team_least_goals = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_least_goals_special_tips')
    team_first_goal = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_first_goal_special_tips')
    team_last_goal = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_last_goal_special_tips')
    team_drop_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_drop_a_special_tips')
    team_drop_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='sp_team_drop_b_special_tips')
    overtimes = models.IntegerField(default=0)
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='sp_cup')


class SpecialTip(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    winner = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='winner_special_tips', blank=True, null=True)
    final_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='final_a_special_tips', blank=True, null=True)
    final_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='final_b_special_tips', blank=True, null=True)
    bronze_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='bronze_a_special_tips', blank=True, null=True)
    bronze_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='bronze_b_special_tips', blank=True, null=True)
    czech_shooter_first = models.CharField(max_length=64, blank=True)
    czech_shooter_last = models.CharField(max_length=64, blank=True)
    max_goals_per_game = models.IntegerField(default=0)
    group_a_1 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_a_1_special_tips', blank=True, null=True)
    group_b_1 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_b_1_special_tips', blank=True, null=True)
    group_a_2 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_a_2_special_tips', blank=True, null=True)
    group_b_2 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_b_2_special_tips', blank=True, null=True)
    group_a_3 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_a_3_special_tips', blank=True, null=True)
    group_b_3 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_b_3_special_tips', blank=True, null=True)
    group_a_4 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_a_4_special_tips', blank=True, null=True)
    group_b_4 = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='group_b_4_special_tips', blank=True, null=True)
    team_most_goals = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_most_goals_special_tips', blank=True, null=True)
    team_least_goals = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_least_goals_special_tips', blank=True, null=True)
    team_first_goal = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_first_goal_special_tips', blank=True, null=True)
    team_last_goal = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_last_goal_special_tips', blank=True, null=True)
    team_drop_a = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_drop_a_special_tips', blank=True, null=True)
    team_drop_b = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='team_drop_b_special_tips', blank=True, null=True)
    overtimes = models.IntegerField(default=0)
    cup = models.ForeignKey('Cup', on_delete=models.CASCADE, related_name='cup', blank=True, null=True)

    def __str__(self):
        return f'{self.user}'
