"""
Keycloak authentication backend (prepared for future use).
"""
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class KeycloakAuthentication(authentication.BaseAuthentication):
    """
    Keycloak token authentication.
    To be implemented when Keycloak is configured.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Keycloak token.
        
        This is a placeholder implementation. When Keycloak is configured:
        1. Extract token from Authorization header
        2. Validate token with Keycloak
        3. Get or create user from Keycloak user info
        4. Return (user, token)
        """
        # TODO: Implement Keycloak token validation
        # For now, return None to fall back to session authentication
        return None
