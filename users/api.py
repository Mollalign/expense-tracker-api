from ninja import Router
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from ninja.errors import HttpError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import random
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.http import JsonResponse

from .schema import (
    UserRegisterSchema, 
    UserLoginSchema, 
    TokenSchema,
    ForgotPasswordSchema,
    VerifyCodeSchema
)
from .models import PasswordResetCode

User = get_user_model()
router = Router(tags=["User Auth"])

# ------------------------
# Register
# ------------------------
@router.post("/register")
def register(request, data: UserRegisterSchema):
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already taken")

    # Create user
    user = User.objects.create(
        username=data.full_name,  
        email=data.email,
        password=make_password(data.password)
    )

    return {"message": "User registered successfully"}


# ------------------------
# Login
# ------------------------
@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    user = authenticate(email=data.email, password=data.password)
    if not user:
        raise HttpError(401, "Invalid credentials")

    refresh = RefreshToken.for_user(user)
    # Add extra claims so React can decode
    refresh["sub"] = user.id
    refresh["email"] = user.email

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


# ------------------------
# Refresh Token
# ------------------------
@router.post("/refresh")
def refresh_token(request, data: dict):
    try:
        refresh = RefreshToken(data["refresh"])
        access = refresh.access_token
        return JsonResponse({
            "access": str(access)
        })
    except (TokenError, InvalidToken):
        return JsonResponse({"detail": "Invalid or expired refresh token"}, status=401)



# ------------------------
# Forgot Password
# ------------------------
@router.post("/forgot-password")
def forgot_password(request, data: ForgotPasswordSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(404, "User with this email does not exist")

    code = str(random.randint(100000, 999999))
    PasswordResetCode.objects.create(user=user, code=code)

    send_mail(
        'Your Password Reset Code',
        f'Your code is {code}',
        'no-reply@example.com',
        [data.email],
        fail_silently=False
    )

    return {"message": "Password reset code sent to your email"}


# ------------------------
# Verify Code & Reset Password
# ------------------------
@router.post("/verify-code")
def verify_code(request, data: VerifyCodeSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(404, "User with this email does not exist")

    try:
        reset_code = PasswordResetCode.objects.filter(user=user).latest('created_at')
    except PasswordResetCode.DoesNotExist:
        raise HttpError(404, "No reset code found")

    expiry_time = timezone.now() - timedelta(minutes=15)
    if reset_code.created_at < expiry_time:
        raise HttpError(400, "Reset code expired")

    if reset_code.code != data.code:
        raise HttpError(400, "Invalid code")

    user.password = make_password(data.new_password)
    user.save()
    reset_code.delete()

    return {"message": "Password updated successfully"}
