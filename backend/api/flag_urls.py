"""
Absolutní URL pro statiku / média za reverse proxy (vlajky v /static/…).
"""
from django.conf import settings


def public_or_request_url(request, relative_url: str) -> str:
    """
    relative_url začíná / (např. z django.templatetags.static.static()).
    SITE_PUBLIC_URL = https://new.drevakcup.cz → výsledek https://new.drevakcup.cz/static/…
    """
    rel = relative_url if relative_url.startswith('/') else '/' + relative_url
    base = (getattr(settings, 'SITE_PUBLIC_URL', None) or '').strip().rstrip('/')
    if base:
        return f'{base}{rel}'
    if request:
        return request.build_absolute_uri(rel)
    return rel
