from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication for SPA API requests that does not enforce CSRF checks,
    relying on SameSite cookie policies and CORS protection.
    """
    def enforce_csrf(self, request):
        return  # CSRF exemption for REST API
