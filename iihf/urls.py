from django.urls import path
from .views import Home, Rules, Ladder, Teams

urlpatterns = [
    path('<int:year>/home/', Home.as_view(), name='iihf-home'),
    path('<int:year>/teams/', Teams.as_view(), name='iihf-teams'),
    path('<int:year>/ladder/', Ladder.as_view(), name='iihf-ladder'),
    path('<int:year>/rules/', Rules.as_view(), name='iihf-rules'),
]
