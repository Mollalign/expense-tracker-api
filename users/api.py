from ninja import Router
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .schema import (
    UserRegisterSchema, 
    UserLoginSchema, 
    TokenSchema,
    ForgotPasswordSchema,
    VerifyCodeSchema
)
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from .models import PasswordResetCode
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout


router = Router(tags=["User Auth"])


# register route
@router.post("/register")
def register(request, data: UserRegisterSchema):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username already taken")
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already taken")
    
    user = User.objects.create(
        username=data.username,
        email=data.email,
        password=make_password(data.password)
    )

    return {"message": "User registered successfully"}


# Login route
@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        raise HttpError(401, "Invalid credentials")
    
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@router.post("/logout")
def user_logout(request):
    logout(request)
    return {"message": "Logged out successfully"}


# Forgot Password route
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
        'molledan69@gmail.com',
        [data.email],
        fail_silently=False
    )

    return {"message": "Password reset code sent to your email"}


# verify-code route
@router.post("/verify-code")
def verify_code(request, data: VerifyCodeSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(404, "User with this email does not exist")
    

    try:
        reset_code = PasswordResetCode.objects.filter(user=user).latest('created_at')
    except User.DoesNotExist:
        raise HttpError(404, "No reset code found")
    
    # Check expiry - 15 minutes ago from now
    expiry_time = timezone.now() - timedelta(minutes=15)
    if reset_code.created_at < expiry_time:
        raise HttpError(400, "Reset code expired")
    
    if reset_code.code != data.code:
        raise HttpError(400, "Invalid code")
    
    user.password = make_password(data.new_password)
    user.save()

    reset_code.delete()
    
    return {"message": "Password updated successfully"}






    

