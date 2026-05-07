"""
Serializers for API endpoints.
"""
from django.templatetags.static import static as static_url
from rest_framework import serializers
from .models import (
    User, Cup, Team, Match, Playoff, MatchTip, SpecialTip, Special, UserPoint
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    avatar_url = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'display_name', 'first_name', 'last_name',
            'avatar', 'avatar_url', 'is_active', 'is_staff'
        ]
        read_only_fields = ['id', 'email', 'is_active', 'is_staff']
    
    def get_avatar_url(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url
    
    def get_display_name(self, obj):
        name = (obj.name or '').strip()
        if name:
            return name
        email = (obj.email or '').strip()
        if not email:
            return ''
        return email.split('@', 1)[0] or email


class CupSerializer(serializers.ModelSerializer):
    """Cup serializer."""

    tournament_started = serializers.SerializerMethodField()

    class Meta:
        model = Cup
        fields = [
            'id',
            'year',
            'logo',
            'location',
            'date_start',
            'date_end',
            'tournament_started',
        ]
        read_only_fields = ['id', 'tournament_started']

    def get_tournament_started(self, obj):
        from .services import is_tournament_started

        return is_tournament_started(obj)


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer."""
    cup = CupSerializer(read_only=True)
    cup_id = serializers.IntegerField(write_only=True)
    flag_url = serializers.SerializerMethodField()
    shortcut = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'display_name', 'shortcut', 'flag', 'flag_url', 'gp', 'win', 'los', 'wot', 'lot',
            'gf', 'ga', 'points', 'year', 'group', 'cup', 'cup_id'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'year': {'required': False},
            'flag': {'required': False},
            'gp': {'required': False},
            'win': {'required': False},
            'los': {'required': False},
            'wot': {'required': False},
            'lot': {'required': False},
            'gf': {'required': False},
            'ga': {'required': False},
            'points': {'required': False},
        }
    
    def get_shortcut(self, obj):
        """Return 3-letter display code (e.g. CZE, CAN) or None."""
        from .team_flags import get_team_flag_shortcut
        code = get_team_flag_shortcut(obj.name)
        return code.upper() if code else None

    def get_display_name(self, obj):
        from .team_flags import get_team_display_label

        return get_team_display_label(obj.name)

    def get_flag_url(self, obj):
        from .flag_urls import public_or_request_url
        from .team_flags import get_team_flag_shortcut

        request = self.context.get('request')
        # 1. Nahraná vlajka
        if obj.flag:
            url = obj.flag.url
            if url.startswith('http'):
                return url
            return public_or_request_url(request, url)
        # 2. Bundlované PNG podle názvu / zkratky týmu
        shortcut = get_team_flag_shortcut(obj.name)
        if not shortcut:
            return None
        rel = static_url(f'team_flags/{shortcut}.png')
        return public_or_request_url(request, rel)
    
    def create(self, validated_data):
        cup_id = validated_data.pop('cup_id')
        cup = Cup.objects.get(id=cup_id)
        validated_data['cup'] = cup
        validated_data.setdefault('year', cup.year)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'cup_id' in validated_data:
            cup = Cup.objects.get(id=validated_data.pop('cup_id'))
            validated_data['cup'] = cup
            validated_data.setdefault('year', cup.year)
        return super().update(instance, validated_data)


class MatchSerializer(serializers.ModelSerializer):
    """Match serializer."""
    team_a = TeamSerializer(read_only=True)
    team_b = TeamSerializer(read_only=True)
    team_a_id = serializers.IntegerField(write_only=True)
    team_b_id = serializers.IntegerField(write_only=True)
    cup = CupSerializer(read_only=True)
    cup_id = serializers.IntegerField(write_only=True)
    has_started = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b', 'team_a_id', 'team_b_id',
            'score_a', 'score_b', 'score_a_final', 'score_b_final',
            'overtime', 'shootout', 'date', 'cup', 'cup_id', 'has_started'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        from .models import Cup, Team
        cup_id = validated_data.pop('cup_id')
        team_a_id = validated_data.pop('team_a_id')
        team_b_id = validated_data.pop('team_b_id')
        cup = Cup.objects.get(id=cup_id)
        team_a = Team.objects.get(id=team_a_id)
        team_b = Team.objects.get(id=team_b_id)
        validated_data['cup'] = cup
        validated_data['team_a'] = team_a
        validated_data['team_b'] = team_b
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        from .models import Cup, Team
        if 'cup_id' in validated_data:
            instance.cup = Cup.objects.get(id=validated_data.pop('cup_id'))
        if 'team_a_id' in validated_data:
            instance.team_a = Team.objects.get(id=validated_data.pop('team_a_id'))
        if 'team_b_id' in validated_data:
            instance.team_b = Team.objects.get(id=validated_data.pop('team_b_id'))
        # When score is set, sync _final if not provided so team stats and GF/GA are calculated
        if 'score_a' in validated_data or 'score_b' in validated_data:
            validated_data.setdefault('score_a_final', validated_data.get('score_a', instance.score_a))
            validated_data.setdefault('score_b_final', validated_data.get('score_b', instance.score_b))
        # Infer overtime from regulation vs final score (no separate checkbox needed)
        sa = validated_data.get('score_a', instance.score_a)
        sb = validated_data.get('score_b', instance.score_b)
        sa_f = validated_data.get('score_a_final', instance.score_a_final)
        sb_f = validated_data.get('score_b_final', instance.score_b_final)
        if sa is not None and sb is not None and sa_f is not None and sb_f is not None:
            ot = (sa != sa_f or sb != sb_f)
            if validated_data.get('shootout', instance.shootout):
                ot = True
            validated_data['overtime'] = ot
        return super().update(instance, validated_data)
    
    def get_has_started(self, obj):
        """Check if match has started."""
        from django.utils import timezone
        return timezone.now() >= obj.date


class PlayoffSerializer(serializers.ModelSerializer):
    """Playoff serializer (základní čas + skóre; týmy volitelné až po založení řádků)."""

    team_a = TeamSerializer(read_only=True)
    team_b = TeamSerializer(read_only=True)
    team_a_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_b_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    cup = CupSerializer(read_only=True)
    cup_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Playoff
        fields = [
            'id', 'playoff_type', 'team_a', 'team_b', 'team_a_id', 'team_b_id',
            'score_a', 'score_b', 'score_a_final', 'score_b_final',
            'overtime', 'shootout', 'date', 'cup', 'cup_id',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        cup = attrs.get('cup')
        if cup is None and self.instance:
            cup = self.instance.cup
        if cup is None and attrs.get('cup_id'):
            cup = Cup.objects.filter(pk=attrs['cup_id']).first()
        for key in ('team_a_id', 'team_b_id'):
            if key not in attrs:
                continue
            tid = attrs.get(key)
            if tid is None or cup is None:
                continue
            if not Team.objects.filter(id=tid, cup=cup).exists():
                raise serializers.ValidationError({key: 'Tým nepatří do tohoto turnaje.'})
        return attrs

    def create(self, validated_data):
        from .models import Cup, Team

        cup_id = validated_data.pop('cup_id')
        cup = Cup.objects.get(id=cup_id)
        team_a_id = validated_data.pop('team_a_id', None)
        team_b_id = validated_data.pop('team_b_id', None)
        validated_data['cup'] = cup
        validated_data['team_a'] = Team.objects.get(pk=team_a_id) if team_a_id is not None else None
        validated_data['team_b'] = Team.objects.get(pk=team_b_id) if team_b_id is not None else None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        from .models import Cup, Team

        if 'cup_id' in validated_data:
            instance.cup = Cup.objects.get(id=validated_data.pop('cup_id'))
        if 'team_a_id' in validated_data:
            tid = validated_data.pop('team_a_id')
            instance.team_a = Team.objects.get(pk=tid) if tid is not None else None
        if 'team_b_id' in validated_data:
            tid = validated_data.pop('team_b_id')
            instance.team_b = Team.objects.get(pk=tid) if tid is not None else None
        if 'score_a' in validated_data or 'score_b' in validated_data:
            validated_data.setdefault(
                'score_a_final',
                validated_data.get('score_a', instance.score_a),
            )
            validated_data.setdefault(
                'score_b_final',
                validated_data.get('score_b', instance.score_b),
            )
        sa = validated_data.get('score_a', instance.score_a)
        sb = validated_data.get('score_b', instance.score_b)
        sa_f = validated_data.get('score_a_final', instance.score_a_final)
        sb_f = validated_data.get('score_b_final', instance.score_b_final)
        if sa is not None and sb is not None and sa_f is not None and sb_f is not None:
            ot = (sa != sa_f or sb != sb_f)
            if validated_data.get('shootout', instance.shootout):
                ot = True
            validated_data['overtime'] = ot
        return super().update(instance, validated_data)


class MatchTipSerializer(serializers.ModelSerializer):
    """Match tip serializer."""
    match = MatchSerializer(read_only=True)
    match_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = MatchTip
        fields = ['id', 'match', 'match_id', 'user', 'score_a', 'score_b']
        read_only_fields = ['id', 'user']
    
    def validate(self, data):
        """Tipy na zápasy jen do začátku prvního zápasu turnaje (viz is_tournament_started)."""
        from .services import is_tournament_started

        match = None
        if self.instance:
            match = self.instance.match
        else:
            match_id = data.get('match_id')
            if match_id:
                match = Match.objects.filter(id=match_id).select_related('cup').first()
        if match and is_tournament_started(match.cup):
            raise serializers.ValidationError(
                'Turnaj už začal — tipy na zápasy nelze měnit.'
            )
        return data


class SpecialTipSerializer(serializers.ModelSerializer):
    """Special tip serializer."""
    cup = CupSerializer(read_only=True)
    cup_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    # Team fields
    winner = TeamSerializer(read_only=True)
    winner_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    final_a = TeamSerializer(read_only=True)
    final_a_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    final_b = TeamSerializer(read_only=True)
    final_b_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    bronze_a = TeamSerializer(read_only=True)
    bronze_a_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    bronze_b = TeamSerializer(read_only=True)
    bronze_b_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    group_a_1 = TeamSerializer(read_only=True)
    group_a_1_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_b_1 = TeamSerializer(read_only=True)
    group_b_1_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_a_2 = TeamSerializer(read_only=True)
    group_a_2_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_b_2 = TeamSerializer(read_only=True)
    group_b_2_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_a_3 = TeamSerializer(read_only=True)
    group_a_3_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_b_3 = TeamSerializer(read_only=True)
    group_b_3_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_a_4 = TeamSerializer(read_only=True)
    group_a_4_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    group_b_4 = TeamSerializer(read_only=True)
    group_b_4_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    team_most_goals = TeamSerializer(read_only=True)
    team_most_goals_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_least_goals = TeamSerializer(read_only=True)
    team_least_goals_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_first_goal = TeamSerializer(read_only=True)
    team_first_goal_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_last_goal = TeamSerializer(read_only=True)
    team_last_goal_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_drop_a = TeamSerializer(read_only=True)
    team_drop_a_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    team_drop_b = TeamSerializer(read_only=True)
    team_drop_b_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = SpecialTip
        fields = [
            'id', 'user', 'cup', 'cup_id', 'winner', 'winner_id',
            'final_a', 'final_a_id', 'final_b', 'final_b_id',
            'bronze_a', 'bronze_a_id', 'bronze_b', 'bronze_b_id',
            'czech_shooter_first', 'czech_shooter_last', 'max_goals_per_game',
            'group_a_1', 'group_a_1_id', 'group_b_1', 'group_b_1_id',
            'group_a_2', 'group_a_2_id', 'group_b_2', 'group_b_2_id',
            'group_a_3', 'group_a_3_id', 'group_b_3', 'group_b_3_id',
            'group_a_4', 'group_a_4_id', 'group_b_4', 'group_b_4_id',
            'team_most_goals', 'team_most_goals_id',
            'team_least_goals', 'team_least_goals_id',
            'team_first_goal', 'team_first_goal_id',
            'team_last_goal', 'team_last_goal_id',
            'team_drop_a', 'team_drop_a_id',
            'team_drop_b', 'team_drop_b_id',
            'overtimes'
        ]
        read_only_fields = ['id', 'user']
    
    def validate(self, attrs):
        """Model nemá u těchto polí null=True — prázdná hodnota z formuláře jako null musí být 0."""
        if 'max_goals_per_game' in attrs and attrs['max_goals_per_game'] is None:
            attrs['max_goals_per_game'] = 0
        if 'overtimes' in attrs and attrs['overtimes'] is None:
            attrs['overtimes'] = 0
        return attrs
    
    def create(self, validated_data):
        """Create SpecialTip; map _id fields to model (Django accepts winner_id=...)."""
        return SpecialTip.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update SpecialTip."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SpecialSerializer(serializers.ModelSerializer):
    """Special results serializer (read + write for staff)."""
    cup = CupSerializer(read_only=True)
    cup_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Special
        fields = '__all__'
        read_only_fields = [
            'id',
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
    
    def create(self, validated_data):
        cup_id = validated_data.pop('cup_id', None) or validated_data.pop('cup', None)
        for k in (
            'winner',
            'final_a',
            'final_b',
            'bronze_a',
            'bronze_b',
            'winner_id',
            'final_a_id',
            'final_b_id',
            'bronze_a_id',
            'bronze_b_id',
            'max_goals_per_game',
            'overtimes',
            'team_most_goals',
            'team_least_goals',
            'team_most_goals_id',
            'team_least_goals_id',
        ):
            validated_data.pop(k, None)
        if cup_id is not None:
            from .models import Cup
            validated_data['cup'] = Cup.objects.get(pk=cup_id)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('cup_id', None)
        validated_data.pop('cup', None)
        for k in (
            'winner',
            'final_a',
            'final_b',
            'bronze_a',
            'bronze_b',
            'winner_id',
            'final_a_id',
            'final_b_id',
            'bronze_a_id',
            'bronze_b_id',
            'max_goals_per_game',
            'overtimes',
            'team_most_goals',
            'team_least_goals',
            'team_most_goals_id',
            'team_least_goals_id',
        ):
            validated_data.pop(k, None)
        return super().update(instance, validated_data)


class UserPointSerializer(serializers.ModelSerializer):
    """User point serializer."""
    user = UserSerializer(read_only=True)
    cup = CupSerializer(read_only=True)
    
    class Meta:
        model = UserPoint
        fields = ['id', 'user', 'cup', 'points', 'part']
        read_only_fields = ['id']


class LadderSerializer(serializers.Serializer):
    """Ladder serializer for leaderboard."""
    user = UserSerializer()
    points_a = serializers.IntegerField()
    points_b = serializers.IntegerField()
    points_c = serializers.IntegerField()
    rank = serializers.IntegerField()
