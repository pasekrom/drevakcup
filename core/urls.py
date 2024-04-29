from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from core import settings, views
from core.views import Home, UserProfile, Cups, SignUpView, MyLoginView, forgot_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('iihf/', include('iihf.urls')),
    path('', Home.as_view(), name='home'),
    path('user/', UserProfile.as_view(), name='user'),
    path('cups/', Cups.as_view(), name='cups'),
    path('', Home.as_view(), name='sign-out'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
