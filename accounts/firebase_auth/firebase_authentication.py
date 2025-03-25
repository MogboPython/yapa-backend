import firebase_admin
from firebase_admin import auth, credentials
from rest_framework import authentication

from accounts.models import User
from yapa_backend.settings import env

from .firebase_exceptions import EmailVerification, FirebaseError, InvalidAuthToken, NoAuthToken

# Firebase Admin SDK credentials
try:
  cred = credentials.Certificate(env.str("FIREBASE_ADMIN_SDK_CREDENTIALS_PATH"))
  default_app = firebase_admin.initialize_app(cred)
except Exception:
  raise FirebaseError("Firebase Admin SDK credentials not found.")

class FirebaseAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        # FIXME: remove this
        # auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not token:
          msg = "No authentication token provided."
          raise NoAuthToken(msg)

        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token["uid"]
        except Exception as e:
            msg = "Invalid authentication token provided"
            raise InvalidAuthToken(msg) from e

        if not token or not decoded_token:
            return None

        email_verified = decoded_token.get("email_verified")
        if not email_verified:
            msg = "Email not verified. please verify your email address"
            raise EmailVerification(msg)

        try:
            user = User.objects.get(firebase_uid=uid)
        except User.DoesNotExist:
            msg = "The user proivded with auth token is not a firebase user. it has no firebase uid."
            raise FirebaseError(msg)
        return (user, None)
