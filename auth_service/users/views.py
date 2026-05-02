# auth_service/users/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .models import User
from .serializers import RegisterSerializer, UserSerializer
from .permissions import IsSuperAdmin


class CustomLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            refresh['role'] = user.role  # ✅ embed role so report-service can read it
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            })
        else:
            return Response(
                {'error': 'Identifiants incorrects'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RefreshTokenView(TokenRefreshView):
    pass


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ FIX: Actually blacklist the refresh token so it can't be reused.
        # Before this fix, logout just returned a success message
        # but the token stayed valid for the full 1-day lifetime.
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'error': 'Refresh token requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # ← this is the actual logout
            return Response({'message': 'Déconnecté avec succès'})
        except TokenError:
            return Response(
                {'error': 'Token invalide ou déjà révoqué'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'message': 'Inscription réussie'
        }, status=status.HTTP_201_CREATED)


class CreateAdminView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def perform_create(self, serializer):
        user = serializer.save()
        user.role = 'admin'
        user.save()


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'city': user.city,
            'role': user.role,
            'is_citizen': user.is_citizen,
            'is_official': user.is_official,
            'created_at': user.created_at
        })


class VerifyUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'role': user.role
        })


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class PublicAdminListView(generics.ListAPIView):
    """
    Public endpoint to get list of admins and superadmins.
    Used by report-service to send notifications without auth.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(role__in=['admin', 'superadmin'])


# Ajouter cette classe

class UserDetailView(generics.RetrieveAPIView):
    """
    Get a single user by ID.
    Accessible to: superadmin (all users), admin (all users), user (only themselves)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticated
        return [IsAuthenticated()]
    
    def get_object(self):
        user_id = self.kwargs.get('pk')
        requesting_user = self.request.user
        
        # Superadmin can see anyone
        if requesting_user.role == 'superadmin':
            return User.objects.get(pk=user_id)
        # Admin can see anyone
        elif requesting_user.role == 'admin':
            return User.objects.get(pk=user_id)
        # Regular user can only see themselves
        elif requesting_user.id == user_id:
            return requesting_user
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this user")