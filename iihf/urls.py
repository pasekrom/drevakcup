from django.urls import path
from .views import Home, Rules, Ladder, Teams, MatchTipFormView, SpecialTipFormView

urlpatterns = [
    path('<int:year>/home/', Home.as_view(), name='iihf-home'),
    path('<int:year>/teams/', Teams.as_view(), name='iihf-teams'),
    path('<int:year>/ladder/', Ladder.as_view(), name='iihf-ladder'),
    path('<int:year>/rules/', Rules.as_view(), name='iihf-rules'),
    path('<int:year>/match_tip/', MatchTipFormView.as_view(), name='iihf-match-tip'),
    path('<int:year>/special_tip/', SpecialTipFormView.as_view(), name='iihf-special-tip'),
]
