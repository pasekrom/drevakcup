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
    ot = models.CharField(max_length=1, blank=True)
    so = models.CharField(max_length=1, blank=True)
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
