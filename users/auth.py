import logging
from ninja.security import HttpBearer
from ninja.errors import HttpError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        print("Token received:", token)
        """
        Validate the token and return the user instance.
        Raises HttpError(401) on failure.
        """
        try:
           signing_key = settings.SIMPLE_JWT.get("SIGNING_KEY", settings.SECRET_KEY)
           token_backend = TokenBackend(algorithm=settings.SIMPLE_JWT.get("ALGORITHM", "HS256"), signing_key=signing_key)
           validated_data = token_backend.decode(token, verify=True)

           user_id = validated_data.get("user_id")

           if not user_id:
                raise HttpError(401, "Invalid token payload")
           
           user = User.objects.get(id=user_id)

           if not user.is_active:
                raise HttpError(401, "User is inactive")

           
           return user

        except Exception as e:
            logger.warning(f"JWT authentication failed: {e}")
            raise HttpError(401, "Invalid or expired token")