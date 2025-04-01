from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication


def get_user(request):
    auth = JWTAuthentication()
    try:
        user_auth_tuple = auth.authenticate(request)
        if user_auth_tuple is not None:
            return user_auth_tuple[0]
    except:
        pass
    return AnonymousUser()

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
        return self.get_response(request)
