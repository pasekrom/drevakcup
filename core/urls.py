from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core import settings, views
from core.views import Home, User, Cups, SignUpView, MyLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('iihf/', include('iihf.urls')),
    path('', Home.as_view(), name='home'),
    path('user/', User.as_view(), name='user'),
    path('cups/', Cups.as_view(), name='cups'),
    path('', Home.as_view(), name='sign-out'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', views.logout_page, name='logout'),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
