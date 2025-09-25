from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import jwt
from django.conf import settings

from .models import Profile
from .serializers import UserSerializer, ProfileSerializer


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """POST /auth/register"""
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """POST /auth/login"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        response = Response({
            'access_token': access_token,
            'user': UserSerializer(user).data
        })
        
        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            'refresh_token', 
            refresh_token, 
            httponly=True, 
            secure=True, 
            samesite='Strict',
            max_age=7*24*60*60  # 7 days
        )
        
        return response
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """POST /auth/refresh"""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            access_token = self._generate_access_token(user)
            return Response({'access_token': access_token})
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """POST /auth/logout"""
        response = Response({'message': 'Logged out successfully'})
        response.delete_cookie('refresh_token')
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /auth/me"""
        return Response({
            'user': UserSerializer(request.user).data,
            'profile': ProfileSerializer(request.user.profile).data
        })
    
    def _generate_access_token(self, user):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def _generate_refresh_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


class ProfileViewSet(viewsets.ModelViewSet):
    """Profile management"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.profile

