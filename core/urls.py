from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core import settings
from core.views import Home, User, Cups

urlpatterns = [
    path('admin/', admin.site.urls),
    path('iihf/', include('iihf.urls')),
    path('', Home.as_view(), name='home'),
    path('user/', User.as_view(), name='user'),
    path('cups/', Cups.as_view(), name='cups'),
    path('', Home.as_view(), name='sign-out'),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
