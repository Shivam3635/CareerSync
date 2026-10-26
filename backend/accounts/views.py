from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout, get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DemoLoginView(APIView):
    """
    1-Click demo authentication for development and demo mode.
    Only allows 'student' or 'admin'.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        account_type = request.data.get('account_type', 'student')
        email = "admin@careersync.demo" if account_type == 'admin' else "student@careersync.demo"

        try:
            user = User.objects.get(email=email)
            login(request, user)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response(
                {"error": f"Demo account '{email}' not found. Please run seed_data first."},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."})


class CurrentUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({"authenticated": False, "user": None})
