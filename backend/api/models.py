"""
Optimized models for IIHF tournament prediction platform.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Will be replaced by Keycloak user sync in production.
    """
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_set',
        related_query_name='user',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.email


class Cup(models.Model):
    """IIHF Tournament/Cup."""
    year = models.IntegerField(unique=True, db_index=True)
    logo = models.ImageField(upload_to='iihf_logo/', null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cups'
        ordering = ['-year']
        indexes = [
            models.Index(fields=['year']),
        ]

    def __str__(self):
        return f'{self.year}: {self.location}'


class Team(models.Model):
    """Team participating in a tournament."""
    name = models.CharField(max_length=255, db_index=True)
    flag = models.ImageField(upload_to='team_flags/', null=True, blank=True)
    gp = models.IntegerField(default=0)  # Games played
    win = models.IntegerField(default=0)
    los = models.IntegerField(default=0)  # Losses
    wot = models.IntegerField(default=0)  # Wins in overtime
    lot = models.IntegerField(default=0)  # Losses in overtime
    gf = models.IntegerField(default=0)  # Goals for
    ga = models.IntegerField(default=0)  # Goals against
    points = models.IntegerField(default=0)
    year = models.IntegerField(db_index=True)
    group = models.CharField(max_length=1, default='A')
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='teams', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teams'
        unique_together = [('name', 'year', 'cup')]
        indexes = [
            models.Index(fields=['year', 'group']),
            models.Index(fields=['cup', 'group']),
            models.Index(fields=['-points', 'name']),
        ]

    def __str__(self):
        return f'{self.year}: {self.name}'


class Match(models.Model):
    """Regular tournament match."""
    team_a = models.ForeignKey(Team, related_name='matches_as_team_a', on_delete=models.CASCADE, db_index=True)
    team_b = models.ForeignKey(Team, related_name='matches_as_team_b', on_delete=models.CASCADE, db_index=True)
    score_a = models.IntegerField(blank=True, null=True)
    score_b = models.IntegerField(blank=True, null=True)
    score_a_final = models.IntegerField(blank=True, null=True)
    score_b_final = models.IntegerField(blank=True, null=True)
    overtime = models.BooleanField(default=False)
    shootout = models.BooleanField(default=False)
    date = models.DateTimeField(db_index=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='matches', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        ordering = ['date', 'team_a__group']
        indexes = [
            models.Index(fields=['cup', 'date']),
            models.Index(fields=['team_a', 'team_b']),
        ]

    def __str__(self):
        return f'{self.date} - {self.team_a.name} vs {self.team_b.name}'


class Playoff(models.Model):
    """Playoff match."""
    PLAYOFF_TYPES = [
        ('QFA1', 'QFA1'),
        ('QFA2', 'QFA2'),
        ('QFB1', 'QFB1'),
        ('QFB2', 'QFB2'),
        ('SFA', 'SFA'),
        ('SFB', 'SFB'),
        ('BMG', 'BMG'),
        ('GMG', 'GMG')
    ]
    
    playoff_type = models.CharField(max_length=4, choices=PLAYOFF_TYPES, db_index=True)
    team_a = models.ForeignKey(
        Team,
        related_name='playoffs_as_team_a',
        on_delete=models.CASCADE,
        db_index=True,
        null=True,
        blank=True,
    )
    team_b = models.ForeignKey(
        Team,
        related_name='playoffs_as_team_b',
        on_delete=models.CASCADE,
        db_index=True,
        null=True,
        blank=True,
    )
    score_a = models.IntegerField(blank=True, null=True)
    score_b = models.IntegerField(blank=True, null=True)
    score_a_final = models.IntegerField(blank=True, null=True)
    score_b_final = models.IntegerField(blank=True, null=True)
    overtime = models.BooleanField(default=False)
    shootout = models.BooleanField(default=False)
    date = models.DateTimeField(db_index=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='playoffs', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'playoffs'
        ordering = ['date', 'playoff_type']
        indexes = [
            models.Index(fields=['cup', 'date']),
            models.Index(fields=['playoff_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['cup', 'playoff_type'],
                name='uniq_playoff_cup_playoff_type',
            ),
        ]

    def __str__(self):
        na = self.team_a.name if self.team_a_id else '?'
        nb = self.team_b.name if self.team_b_id else '?'
        return f'{self.playoff_type} - {na} vs {nb}'


class MatchTip(models.Model):
    """User's prediction for a match."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='tips', db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_tips', db_index=True)
    score_a = models.IntegerField(blank=True, null=True)
    score_b = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'match_tips'
        unique_together = [('match', 'user')]
        indexes = [
            models.Index(fields=['user', 'match']),
            models.Index(fields=['match']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.match}'


class Special(models.Model):
    """Actual tournament results for special predictions."""
    cup = models.OneToOneField(Cup, on_delete=models.CASCADE, related_name='special_results', db_index=True)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='won_tournaments', blank=True, null=True)
    final_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='final_a_results', blank=True, null=True)
    final_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='final_b_results', blank=True, null=True)
    bronze_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bronze_a_results', blank=True, null=True)
    bronze_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bronze_b_results', blank=True, null=True)
    czech_shooter_first = models.CharField(max_length=64, blank=True)
    czech_shooter_last = models.CharField(max_length=64, blank=True)
    max_goals_per_game = models.IntegerField(default=0)
    group_a_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_1_results', blank=True, null=True)
    group_b_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_1_results', blank=True, null=True)
    group_a_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_2_results', blank=True, null=True)
    group_b_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_2_results', blank=True, null=True)
    group_a_3 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_3_results', blank=True, null=True)
    group_b_3 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_3_results', blank=True, null=True)
    group_a_4 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_4_results', blank=True, null=True)
    group_b_4 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_4_results', blank=True, null=True)
    team_most_goals = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='most_goals_results', blank=True, null=True)
    team_least_goals = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='least_goals_results', blank=True, null=True)
    team_first_goal = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_goal_results', blank=True, null=True)
    team_last_goal = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='last_goal_results', blank=True, null=True)
    team_drop_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drop_a_results', blank=True, null=True)
    team_drop_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drop_b_results', blank=True, null=True)
    overtimes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'special_results'

    def __str__(self):
        return f'Special Results - {self.cup.year}'


class SpecialTip(models.Model):
    """User's special predictions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='special_tips', db_index=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='special_tips', db_index=True)
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='winner_tips', blank=True, null=True)
    final_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='final_a_tips', blank=True, null=True)
    final_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='final_b_tips', blank=True, null=True)
    bronze_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bronze_a_tips', blank=True, null=True)
    bronze_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bronze_b_tips', blank=True, null=True)
    czech_shooter_first = models.CharField(max_length=64, blank=True)
    czech_shooter_last = models.CharField(max_length=64, blank=True)
    max_goals_per_game = models.IntegerField(default=0)
    group_a_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_1_tips', blank=True, null=True)
    group_b_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_1_tips', blank=True, null=True)
    group_a_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_2_tips', blank=True, null=True)
    group_b_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_2_tips', blank=True, null=True)
    group_a_3 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_3_tips', blank=True, null=True)
    group_b_3 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_3_tips', blank=True, null=True)
    group_a_4 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_a_4_tips', blank=True, null=True)
    group_b_4 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='group_b_4_tips', blank=True, null=True)
    team_most_goals = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='most_goals_tips', blank=True, null=True)
    team_least_goals = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='least_goals_tips', blank=True, null=True)
    team_first_goal = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_goal_tips', blank=True, null=True)
    team_last_goal = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='last_goal_tips', blank=True, null=True)
    team_drop_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drop_a_tips', blank=True, null=True)
    team_drop_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drop_b_tips', blank=True, null=True)
    overtimes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'special_tips'
        unique_together = [('user', 'cup')]
        indexes = [
            models.Index(fields=['user', 'cup']),
        ]

    def __str__(self):
        return f'{self.user.email} - {self.cup.year}'


class UserPoint(models.Model):
    """User points for a tournament."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_points', db_index=True)
    cup = models.ForeignKey(Cup, on_delete=models.CASCADE, related_name='user_points', db_index=True)
    points = models.IntegerField(default=0)
    part = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default='A')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_points'
        unique_together = [('user', 'cup', 'part')]
        indexes = [
            models.Index(fields=['user', 'cup', 'part']),
            models.Index(fields=['cup', 'part', '-points']),
        ]

    def __str__(self):
        return f'{self.cup.year} - {self.user.email} - Part {self.part}: {self.points}'
