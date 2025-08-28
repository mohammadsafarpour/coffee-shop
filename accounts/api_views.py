import pyotp
import datetime

from rest_framework import viewsets, generics, status, serializers 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.utils import timezone

from products.models import Product
from .models import Profile, OTPRequest

from .serializers import (
    UserSerializer,
    RegisterSerializer, 
    ProfileSerializer, 
    ProfileFavoritesSerializer, 
    UserSerializer, 
    OTPRequestSerializer, 
    OTPVerifyRegisterSerializer,
    UserSerializer, 
    PhonePasswordSerializer, 
    PhoneOTPSerializer,
    UserManagementSerializer
)

CustomUser = get_user_model()

class PhonePasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

class PhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp_code = serializers.CharField()

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'request_otp':
            return OTPRequestSerializer
        elif self.action == 'verify_and_register':
            return OTPVerifyRegisterSerializer
        return serializers.Serializer
    
    @extend_schema(request=OTPRequestSerializer)

    @action(detail=False, methods=['post'], url_path='register/request-otp')
    def request_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp_secret = pyotp.random_base32()
        otp_request, created = OTPRequest.objects.update_or_create(
            phone=phone, defaults={'otp_secret': otp_secret}
        )

        totp = pyotp.TOTP(otp_secret, interval=300)
        otp_code = totp.now()
        print(f"DEBUG: Registration OTP for {phone} is {otp_code}")
        return Response(
            {'detail': 'کد تایید با موفقیت به شماره شما ارسال شد.'}, 
            status=status.HTTP_200_OK
        )
    
    @extend_schema(request=OTPVerifyRegisterSerializer)

    @action(detail=False, methods=['post'], url_path='register/verify')
    def verify_and_register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        phone = data['phone']
        otp_code = data['otp_code']
        
        try:
            otp_request = OTPRequest.objects.get(phone=phone)
        except OTPRequest.DoesNotExist:
            return Response({'error': 'درخواست کدی برای این شماره یافت نشد.'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(otp_request.otp_secret, interval=300)
        if not totp.verify(otp_code):
            return Response({'error': 'کد تایید نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        profile_data = data.pop('profile', {})
        data.pop('otp_code', None)
        
        user = CustomUser.objects.create_user(**data)
        
        profile = user.profile
        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('last_name', profile.last_name)
        profile.save()
        otp_request.delete()
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        
        return Response({
            'token': token.key,
            'user': user_data
        }, status=status.HTTP_201_CREATED)

class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user.profile
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'avatar': {'type': 'string', 'format': 'binary'}
                }
            }
        },
        responses={200: UserSerializer}
    )

    @action(detail=False, methods=['patch'], serializer_class=ProfileSerializer)
    def update_profile(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['get'], serializer_class=ProfileFavoritesSerializer)
    def favorites(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_favorite(self, request, pk=None):
        profile = self.get_object()
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)
        profile.favorites.add(product)
        return Response({'status': 'added to favorites'}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['post'])
    def remove_favorite(self, request, pk=None):
        profile = self.get_object()
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=product_id)
        profile.favorites.remove(product)
        return Response({'status': 'removed from favorites'}, status=status.HTTP_200_OK)

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().select_related('profile')
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'avatar': {'type': 'string', 'format': 'binary'} 
                }
            }
        },
        responses={200: UserManagementSerializer}
    )

    @action(detail=True, methods=['patch'], url_path='update-profile')
    def update_user_profile(self, request, pk=None):
        user = self.get_object()
        profile = user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = self.get_serializer(user)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def make_staff(self, request, pk=None):
        user = self.get_object()
        user.is_staff = True
        user.save()
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['post'])
    def remove_staff(self, request, pk=None):
        user = self.get_object()
        user.is_staff = False
        user.save()
        return Response(self.get_serializer(user).data)

class LoginOTPViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    @extend_schema(
        request=PhonePasswordSerializer,
        summary="Step 1 Login: Request OTP with credentials"
    )
    @action(detail=False, methods=['post'], url_path='request')
    def request_otp(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = authenticate(request, username=phone, password=password)
        if user is not None:
            otp_secret = pyotp.random_base32()
            totp = pyotp.TOTP(otp_secret, interval=300)
            otp_code = totp.now()
            profile = user.profile
            profile.otp_secret = otp_secret
            profile.otp_created_at = timezone.now()
            profile.save()
            print(f"DEBUG: Login OTP for {user.phone} is {otp_code}")
            return Response({'detail': 'کد تایید با موفقیت به شماره شما ارسال شد.'}, status=status.HTTP_200_OK)
        return Response({'error': 'شماره تلفن یا رمز عبور نامعتبر است.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @extend_schema(
        request=PhoneOTPSerializer,
        summary="Step 2 Login: Verify OTP and get token"
    )

    @action(detail=False, methods=['post'], url_path='verify')
    def verify_otp(self, request):
        serializer = PhoneOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = request.data.get('phone')
        otp_code = request.data.get('otp_code')
        
        try:
            user = CustomUser.objects.get(phone=phone)
            profile = user.profile
            
            if not profile.otp_secret or not profile.otp_created_at:
                return Response({'error': 'درخواست کدی برای این کاربر یافت نشد.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if (timezone.now() - profile.otp_created_at).total_seconds() > 300:
                return Response({'error': 'کد تایید منقضی شده است.'}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(profile.otp_secret, interval=300)
            if totp.verify(otp_code):
                profile.otp_secret = None
                profile.otp_created_at = None
                profile.save()
                
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'user': UserSerializer(user).data})
            else:
                return Response({'error': 'کد تایید نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        except CustomUser.DoesNotExist:
            return Response({'error': 'کاربری با این شماره تلفن یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)