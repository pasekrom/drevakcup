"""
API viewsets and views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    Cup, Team, Match, Playoff, MatchTip, SpecialTip, Special, UserPoint, User
)
from .serializers import (
    CupSerializer, TeamSerializer, MatchSerializer, PlayoffSerializer,
    MatchTipSerializer, SpecialTipSerializer, SpecialSerializer,
    UserPointSerializer, LadderSerializer, UserSerializer
)
from .services import calculate_points, is_tournament_started
from .tips_matrix import build_tips_matrix


class CupViewSet(viewsets.ModelViewSet):
    """Cup viewset. List/read for all; create/update/delete for staff only."""
    queryset = Cup.objects.all()
    serializer_class = CupSerializer
    filterset_fields = ['year']
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'current'):
            return [AllowAny()]
        if self.action == 'tips_matrix':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current (latest) cup."""
        cup = Cup.objects.order_by('-year').first()
        if not cup:
            return Response({'detail': 'No cup found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(cup)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def tips_matrix(self, request, pk=None):
        """Přehled tipů všech uživatelů (zápasy + speciál) pro jeden turnaj."""
        cup = self.get_object()
        return Response(build_tips_matrix(cup, request))


class TeamViewSet(viewsets.ModelViewSet):
    """Team viewset. Read for authenticated; create/update/delete for staff only."""
    queryset = Team.objects.select_related('cup')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['year', 'group', 'cup']
    search_fields = ['name']
    ordering_fields = ['points', 'name']
    ordering = ['-points', 'name']
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        cup_id = self.request.query_params.get('cup')
        
        if year:
            queryset = queryset.filter(year=year)
        if cup_id:
            queryset = queryset.filter(cup_id=cup_id)
        
        return queryset


class MatchViewSet(viewsets.ModelViewSet):
    """Match viewset. Read for authenticated; create/update/delete for staff only."""
    queryset = Match.objects.select_related('team_a', 'team_b', 'cup')
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ['cup', 'date']
    ordering_fields = ['date']
    ordering = ['date']
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'tips', 'upcoming'):
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        cup_id = self.request.query_params.get('cup')
        
        if year:
            queryset = queryset.filter(cup__year=year)
        if cup_id:
            queryset = queryset.filter(cup_id=cup_id)
        
        return queryset
    
    def perform_update(self, serializer):
        serializer.save()
        instance = serializer.instance
        if any(k in self.request.data for k in ('score_a', 'score_b', 'score_a_final', 'score_b_final')):
            calculate_points(instance.cup)

    @action(detail=True, methods=['get'])
    def tips(self, request, pk=None):
        """Get all tips for a match."""
        match = self.get_object()
        tips = MatchTip.objects.filter(match=match).select_related('user')
        serializer = MatchTipSerializer(tips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Nejbližší zápasy, které ještě nezačaly (čas serveru / DB), seřazené podle data."""
        try:
            limit = int(request.query_params.get('limit', '4'))
        except ValueError:
            limit = 4
        limit = max(1, min(limit, 20))
        # get_queryset() only — nefilter_queryset(), ať ?ordering= z requestu nezmění výběr „nejbližších“
        qs = (
            self.get_queryset()
            .filter(date__gt=timezone.now())
            .order_by('date')[:limit]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PlayoffViewSet(viewsets.ModelViewSet):
    """Playoff viewset — čtení pro přihlášené, zápis jen staff."""

    queryset = Playoff.objects.select_related('team_a', 'team_b', 'cup')
    serializer_class = PlayoffSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['cup', 'playoff_type']
    ordering_fields = ['date', 'playoff_type']
    ordering = ['playoff_type']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        instance = serializer.save()
        calculate_points(instance.cup)

    def perform_update(self, serializer):
        instance = serializer.save()
        calculate_points(instance.cup)

    def perform_destroy(self, instance):
        cup = instance.cup
        super().perform_destroy(instance)
        calculate_points(cup)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def ensure(self, request):
        """Založí 8 play-off řádků (QF×4, SF×2, bronz, finále), pokud ještě neexistují."""
        from datetime import datetime, time

        cup_id = request.data.get('cup_id')
        if not cup_id:
            return Response(
                {'detail': 'cup_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cup = get_object_or_404(Cup, pk=cup_id)
        order = ['QFA1', 'QFA2', 'QFB1', 'QFB2', 'SFA', 'SFB', 'BMG', 'GMG']
        if cup.date_end:
            dt = timezone.make_aware(datetime.combine(cup.date_end, time(20, 0)))
        else:
            dt = timezone.now()
        created_types = []
        for ptype in order:
            _, was_created = Playoff.objects.get_or_create(
                cup=cup,
                playoff_type=ptype,
                defaults={
                    'date': dt,
                    'team_a': None,
                    'team_b': None,
                },
            )
            if was_created:
                created_types.append(ptype)
        calculate_points(cup)
        qs = Playoff.objects.filter(cup=cup).select_related('team_a', 'team_b', 'cup').order_by(
            'playoff_type'
        )
        ser = PlayoffSerializer(qs, many=True, context={'request': request})
        return Response({'created': created_types, 'playoffs': ser.data})


class MatchTipViewSet(viewsets.ModelViewSet):
    """Match tip viewset."""
    serializer_class = MatchTipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MatchTip.objects.filter(
            user=self.request.user
        ).select_related('match__team_a', 'match__team_b', 'match__cup', 'user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_cup(self, request):
        """Get all tips for a cup."""
        cup_id = request.query_params.get('cup')
        year = request.query_params.get('year')
        
        if cup_id:
            tips = self.get_queryset().filter(match__cup_id=cup_id)
        elif year:
            tips = self.get_queryset().filter(match__cup__year=year)
        else:
            return Response(
                {'detail': 'cup or year parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(tips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update match tips."""
        tips_data = request.data.get('tips', [])
        cup_ids = set()
        for tip_data in tips_data:
            match_id = tip_data.get('match_id')
            if match_id is None:
                continue
            try:
                m = Match.objects.select_related('cup').get(id=match_id)
                cup_ids.add(m.cup_id)
            except Match.DoesNotExist:
                return Response(
                    {'detail': f'Zápas {match_id} nenalezen.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        if len(cup_ids) > 1:
            return Response(
                {'detail': 'Všechny tipy musí patřit do stejného turnaje.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if cup_ids:
            cup = Cup.objects.get(pk=next(iter(cup_ids)))
            if is_tournament_started(cup):
                return Response(
                    {'detail': 'Turnaj už začal — tipy na zápasy nelze měnit.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

        created_count = 0
        updated_count = 0

        for tip_data in tips_data:
            match_id = tip_data.get('match_id')
            score_a = tip_data.get('score_a')
            score_b = tip_data.get('score_b')
            
            if match_id is None or score_a is None or score_b is None:
                continue
            
            try:
                match = Match.objects.get(id=match_id)

                match_tip, created = MatchTip.objects.get_or_create(
                    match=match,
                    user=request.user,
                    defaults={'score_a': score_a, 'score_b': score_b}
                )
                
                if not created:
                    match_tip.score_a = score_a
                    match_tip.score_b = score_b
                    match_tip.save()
                    updated_count += 1
                else:
                    created_count += 1
            except Match.DoesNotExist:
                continue
        
        return Response({
            'created': created_count,
            'updated': updated_count
        })


class SpecialTipViewSet(viewsets.ModelViewSet):
    """Special tip viewset."""
    serializer_class = SpecialTipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SpecialTip.objects.filter(
            user=self.request.user
        ).select_related('cup', 'user').prefetch_related(
            'winner', 'final_a', 'final_b', 'bronze_a', 'bronze_b',
            'group_a_1', 'group_b_1', 'group_a_2', 'group_b_2',
            'group_a_3', 'group_b_3', 'group_a_4', 'group_b_4',
            'team_most_goals', 'team_least_goals',
            'team_first_goal', 'team_last_goal',
            'team_drop_a', 'team_drop_b'
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def _reject_if_tournament_started(self, cup):
        if is_tournament_started(cup):
            return Response(
                {
                    'detail': 'Turnaj už začal (od začátku prvního zápasu). Speciální tipy nelze měnit.',
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def create(self, request, *args, **kwargs):
        """Create or update special tip for this user+cup (idempotent save)."""
        cup_id = request.data.get('cup_id')
        if not cup_id:
            return Response(
                {'detail': 'cup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cup = get_object_or_404(Cup, pk=cup_id)
        blocked = self._reject_if_tournament_started(cup)
        if blocked:
            return blocked
        existing = self.get_queryset().filter(cup_id=cup_id).first()
        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        blocked = self._reject_if_tournament_started(instance.cup)
        if blocked:
            return blocked
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        blocked = self._reject_if_tournament_started(instance.cup)
        if blocked:
            return blocked
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def by_cup(self, request):
        """Get special tip for a cup."""
        cup_id = request.query_params.get('cup')
        year = request.query_params.get('year')
        
        if cup_id:
            tip = self.get_queryset().filter(cup_id=cup_id).first()
        elif year:
            tip = self.get_queryset().filter(cup__year=year).first()
        else:
            return Response(
                {'detail': 'cup or year parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not tip:
            return Response({'detail': 'Tip not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(tip)
        return Response(serializer.data)


class UserPointViewSet(viewsets.ReadOnlyModelViewSet):
    """User point viewset."""
    serializer_class = UserPointSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['cup', 'part']
    
    def get_queryset(self):
        return UserPoint.objects.filter(
            user=self.request.user
        ).select_related('user', 'cup')
    
    @action(detail=False, methods=['get'])
    def ladder(self, request):
        """Get leaderboard for a cup."""
        cup_id = request.query_params.get('cup')
        year = request.query_params.get('year')
        
        if not cup_id and not year:
            return Response(
                {'detail': 'cup or year parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cup_id:
            cup = get_object_or_404(Cup, id=cup_id)
        else:
            cup = get_object_or_404(Cup, year=year)
        
        # Get all user points for this cup
        points_a = UserPoint.objects.filter(cup=cup, part='A').select_related('user')
        points_b = UserPoint.objects.filter(cup=cup, part='B').select_related('user')
        points_c = UserPoint.objects.filter(cup=cup, part='C').select_related('user')
        
        # Create dictionaries for quick lookup
        points_a_dict = {p.user_id: p.points for p in points_a}
        points_b_dict = {p.user_id: p.points for p in points_b}
        points_c_dict = {p.user_id: p.points for p in points_c}
        
        # Include all active users (show 0 points if no UserPoint yet)
        users = User.objects.filter(is_active=True).order_by('email')
        
        # Build ladder (pass User instances so LadderSerializer can nest UserSerializer)
        ladder_data = []
        for user in users:
            ladder_data.append({
                'user': user,
                'points_a': points_a_dict.get(user.id, 0),
                'points_b': points_b_dict.get(user.id, 0),
                'points_c': points_c_dict.get(user.id, 0),
                'rank': 0
            })
        
        # Sort by total points (part C), then by email for stable order at 0
        ladder_data.sort(key=lambda x: (-x['points_c'], (x['user'].email or '')))
        for rank, item in enumerate(ladder_data, 1):
            item['rank'] = rank
        
        serializer = LadderSerializer(ladder_data, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    """GET /api/leaderboard/?cup=X or ?year=Y. Requires auth to return data."""
    cup_id = request.query_params.get('cup')
    year = request.query_params.get('year')
    if not cup_id and not year:
        return Response(
            {'detail': 'cup or year parameter required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not request.user.is_authenticated:
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=status.HTTP_403_FORBIDDEN
        )
    if cup_id:
        cup = get_object_or_404(Cup, id=cup_id)
    else:
        cup = get_object_or_404(Cup, year=year)
    points_a = UserPoint.objects.filter(cup=cup, part='A').select_related('user')
    points_b = UserPoint.objects.filter(cup=cup, part='B').select_related('user')
    points_c = UserPoint.objects.filter(cup=cup, part='C').select_related('user')
    points_a_dict = {p.user_id: p.points for p in points_a}
    points_b_dict = {p.user_id: p.points for p in points_b}
    points_c_dict = {p.user_id: p.points for p in points_c}
    users = User.objects.filter(is_active=True).order_by('email')
    ladder_data = []
    for user in users:
        ladder_data.append({
            'user': user,
            'points_a': points_a_dict.get(user.id, 0),
            'points_b': points_b_dict.get(user.id, 0),
            'points_c': points_c_dict.get(user.id, 0),
            'rank': 0,
        })
    ladder_data.sort(key=lambda x: (-x['points_c'], (x['user'].email or '')))
    for rank, item in enumerate(ladder_data, 1):
        item['rank'] = rank
    return Response(LadderSerializer(ladder_data, many=True, context={'request': request}).data)


class SpecialViewSet(viewsets.ModelViewSet):
    """Special results viewset. List/retrieve for authenticated; create/update for staff."""
    queryset = Special.objects.select_related('cup').prefetch_related(
        'winner', 'final_a', 'final_b', 'bronze_a', 'bronze_b',
        'group_a_1', 'group_b_1', 'group_a_2', 'group_b_2',
        'group_a_3', 'group_b_3', 'group_a_4', 'group_b_4',
        'team_most_goals', 'team_least_goals', 'team_first_goal', 'team_last_goal',
        'team_drop_a', 'team_drop_b',
    )
    serializer_class = SpecialSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'by_cup') and self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get', 'put'], url_path='by_cup')
    def by_cup(self, request):
        """Get or set special results for a cup. PUT requires staff."""
        cup_id = request.query_params.get('cup') or (request.data and request.data.get('cup_id'))
        year = request.query_params.get('year')
        
        if not cup_id and not year:
            return Response(
                {'detail': 'cup or year parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'PUT':
            if not request.user.is_staff:
                return Response({'detail': 'Staff only'}, status=status.HTTP_403_FORBIDDEN)
            cup = None
            if cup_id:
                cup = Cup.objects.filter(id=cup_id).first()
            elif year:
                cup = Cup.objects.filter(year=year).first()
            if not cup:
                return Response({'detail': 'Cup not found'}, status=status.HTTP_404_NOT_FOUND)
            special, created = Special.objects.get_or_create(cup=cup)
            serializer = self.get_serializer(special, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            calculate_points(cup)
            return Response(serializer.data)
        
        # GET
        if cup_id:
            special = self.get_queryset().filter(cup_id=cup_id).first()
        else:
            special = self.get_queryset().filter(cup__year=year).first()
        
        if not special:
            return Response({'detail': 'Special results not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(special)
        return Response(serializer.data)


class AdminViewSet(viewsets.ViewSet):
    """Admin-only actions."""
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def calculate_points(self, request):
        """Calculate points for a cup."""
        cup_id = request.data.get('cup_id')
        year = request.data.get('year')
        
        if cup_id:
            cup = get_object_or_404(Cup, id=cup_id)
        elif year:
            cup = get_object_or_404(Cup, year=year)
        else:
            return Response(
                {'detail': 'cup_id or year required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            calculate_points(cup)
            return Response({'status': 'success', 'cup': CupSerializer(cup).data})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
