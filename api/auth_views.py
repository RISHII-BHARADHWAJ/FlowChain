"""API auth views - JWT authentication endpoints"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class LoginView(TokenObtainPairView):
    """JWT login with activity logging"""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                user = User.objects.get(email=request.data.get('email'))
                from accounts.models import UserActivity
                UserActivity.objects.create(
                    user=user,
                    action='login',
                    ip_address=self._get_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                )
            except Exception:
                pass
        return response

    def _get_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            from accounts.models import UserActivity
            UserActivity.objects.create(user=request.user, action='logout')
            return Response({'message': 'Logged out successfully.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from accounts.serializers import UserSerializer
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        from accounts.serializers import UserSerializer
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old = request.data.get('old_password')
        new = request.data.get('new_password')
        if not request.user.check_password(old):
            return Response({'error': 'Old password incorrect.'}, status=400)
        if len(new) < 8:
            return Response({'error': 'Password too short.'}, status=400)
        request.user.set_password(new)
        request.user.last_password_change = timezone.now()
        request.user.save()
        return Response({'message': 'Password changed.'})


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email, is_active=True)
            from accounts.models import PasswordResetToken
            from datetime import timedelta
            PasswordResetToken.objects.create(
                user=user, expires_at=timezone.now() + timedelta(hours=24)
            )
        except User.DoesNotExist:
            pass
        return Response({'message': 'If this email exists, a reset link will be sent.'})


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from accounts.models import PasswordResetToken
        token_val = request.data.get('token')
        new_password = request.data.get('new_password')
        try:
            token = PasswordResetToken.objects.get(token=token_val)
            if not token.is_valid():
                return Response({'error': 'Token expired.'}, status=400)
            token.user.set_password(new_password)
            token.user.save()
            token.is_used = True
            token.save()
            return Response({'message': 'Password reset.'})
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=404)


class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        from accounts.models import EmailVerificationToken
        try:
            v = EmailVerificationToken.objects.get(token=token)
            if not v.is_valid():
                return Response({'error': 'Token expired.'}, status=400)
            v.user.is_verified = True
            v.user.save()
            v.is_used = True
            v.save()
            return Response({'message': 'Email verified.'})
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=404)
