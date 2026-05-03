"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_auth as auth_views
from .views import (
    CupViewSet, TeamViewSet, MatchViewSet, PlayoffViewSet,
    MatchTipViewSet, SpecialTipViewSet, UserPointViewSet,
    SpecialViewSet, AdminViewSet, leaderboard_view
)

router = DefaultRouter()
router.register(r'cups', CupViewSet, basename='cup')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'playoffs', PlayoffViewSet, basename='playoff')
router.register(r'match-tips', MatchTipViewSet, basename='match-tip')
router.register(r'special-tips', SpecialTipViewSet, basename='special-tip')
router.register(r'user-points', UserPointViewSet, basename='user-point')
router.register(r'special', SpecialViewSet, basename='special')
router.register(r'admin', AdminViewSet, basename='admin')

urlpatterns = [
    path('auth/login/', auth_views.login_view),
    path('auth/logout/', auth_views.logout_view),
    path('auth/user/', auth_views.current_user_view),
    path('auth/change-password/', auth_views.change_password_view),
    path('auth/signup/', auth_views.signup_view),
    path('leaderboard/', leaderboard_view),
    path('', include(router.urls)),
]
