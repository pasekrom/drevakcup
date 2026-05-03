"""
Authentication views for session-based login (no Keycloak).
"""
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Log in with email and password. Uses Django session.
    No authentication required.
    """
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    if not email or not password:
        return Response(
            {'detail': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'detail': 'This account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )

    login(request, user)
    serializer = UserSerializer(user, context={'request': request})
    return Response({'user': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Log out and clear session."""
    logout(request)
    return Response({'detail': 'Successfully logged out.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """GET: return current user. PATCH: update profile (name, avatar)."""
    if request.method == 'GET':
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    # PATCH: update name and/or avatar only (email is read-only)
    user = request.user
    update_fields = ['updated_at']
    name = request.data.get('name')
    if name is not None:
        user.name = (name or '').strip()[:30]
        update_fields.append('name')
    avatar_file = request.FILES.get('avatar') if hasattr(request, 'FILES') else None
    if avatar_file is not None:
        user.avatar = avatar_file
        update_fields.append('avatar')
    elif request.data.get('clear_avatar'):
        user.avatar = None
        update_fields.append('avatar')
    user.save(update_fields=update_fields)
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    Create a new user account. No authentication required.
    """
    from django.contrib.auth.hashers import make_password

    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')
    name = request.data.get('name', '').strip()

    if not email:
        return Response(
            {'detail': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not password:
        return Response(
            {'detail': 'Password is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(password) < 8:
        return Response(
            {'detail': 'Password must be at least 8 characters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'A user with this email already exists.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create(
        email=email,
        name=name or email.split('@')[0],
        password=make_password(password),
        is_active=True,
    )
    login(request, user)
    serializer = UserSerializer(user, context={'request': request})
    return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Change password for the current user."""
    current = request.data.get('current_password', '')
    new_password = request.data.get('new_password', '')
    if not current or not new_password:
        return Response(
            {'detail': 'Current password and new password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if not request.user.check_password(current):
        return Response(
            {'detail': 'Current password is incorrect.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if len(new_password) < 8:
        return Response(
            {'detail': 'New password must be at least 8 characters.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    request.user.set_password(new_password)
    request.user.save(update_fields=['password'])
    return Response({'detail': 'Password updated successfully.'})
