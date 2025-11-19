from urllib.parse import urlsplit
from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated or request.path.startswith("/login"):
            return self.get_response(request)
        else:
            path = request.build_absolute_uri()
            resolved_login_url = settings.LOGIN_URL
            # If the login url is the same scheme and net location then use the
            # path as the "next" url.
            login_scheme, login_netloc = urlsplit(resolved_login_url)[:2]
            current_scheme, current_netloc = urlsplit(path)[:2]
            if (not login_scheme or login_scheme == current_scheme) and (
                not login_netloc or login_netloc == current_netloc
            ):
                path = request.get_full_path()

            return redirect_to_login(
                path,
                resolved_login_url,
            )
