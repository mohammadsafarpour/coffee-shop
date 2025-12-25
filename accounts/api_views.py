import pyotp
from django.utils import timezone

from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from products.models import Product
from .models import Profile, OTPRequest
from .serializers import (
    UserSerializer, RegisterSerializer, ProfileSerializer, ProfileFavoritesSerializer,
    OTPRequestSerializer, OTPVerifyRegisterSerializer, UserManagementSerializer,
    PhonePasswordSerializer, PhoneOTPSerializer, ProductIdSerializer, JWTLoginSerializer
)

CustomUser = get_user_model()

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_serializer_class(self):
        if self.action == 'request_otp':
            return OTPRequestSerializer
        elif self.action == 'verify_and_register':
            return OTPVerifyRegisterSerializer
        return serializers.Serializer
    
    @extend_schema(
        request=OTPRequestSerializer,
        summary="OTP First Step : Code submitting"
    )

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
        return Response({'detail': 'کد تایید با موفقیت به شماره شما ارسال شد.'}, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=OTPVerifyRegisterSerializer,
        summary="OTP Second Step : Code Verification"
    )

    @action(detail=False, methods=['post'], url_path='register/verify')
    def verify_and_register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone, otp_code = data['phone'], data['otp_code']
        
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
        return Response({'token': token.key, 'user': user_data}, status=status.HTTP_201_CREATED)

class LoginOTPViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(request=PhonePasswordSerializer, summary="OTP First Step : Code submitting ")
    @action(detail=False, methods=['post'], url_path='request')
    def request_otp(self, request):
        serializer = PhonePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
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
    
    @extend_schema(request=PhoneOTPSerializer, summary="OTP Second Step : Code Verification")
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_otp(self, request):
        serializer = PhoneOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp_code']
        
        try:
            user = CustomUser.objects.get(phone=phone)
            profile = user.profile
            if not profile.otp_secret or not profile.otp_created_at or (timezone.now() - profile.otp_created_at).total_seconds() > 300:
                return Response({'error': 'کد تایید منقضی شده یا وجود ندارد.'}, status=status.HTTP_400_BAD_REQUEST)
            
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

class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

#--------------new for test-------------------
    def get_serializer_class(self):
        if self.action == 'update_my_profile':
            return ProfileSerializer
        if self.action == 'view_my_favorites':
            return ProfileFavoritesSerializer
        return UserSerializer
#------------------end-----------------------

    @extend_schema(responses=UserSerializer)
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request): #view_my_profile -> me
        serializer = UserSerializer(request.user)
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
    @extend_schema(request=ProfileSerializer, responses=UserSerializer)
    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_my_profile(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = UserSerializer(request.user)
        return Response(response_serializer.data)

    @extend_schema(responses=ProfileFavoritesSerializer)
    @action(detail=False, methods=['get'], url_path='me/favorites')
    def view_my_favorites(self, request):
        serializer = ProfileFavoritesSerializer(request.user.profile)
        return Response(serializer.data)
    
    @extend_schema(
        request=ProductIdSerializer,
        summary="Add Favorite Product"
    )

    @action(detail=False, methods=['post'], url_path='me/favorites/add')
    def add_favorite(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, pk=product_id)
        request.user.profile.favorites.add(product)
        return Response({'status': 'added to favorites'}, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=ProductIdSerializer,
        summary="Remove Favorite Product"
    )
        
    @action(detail=False, methods=['post'], url_path='me/favorites/remove')
    def remove_favorite(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)
        request.user.profile.favorites.remove(product)
        return Response({'status': 'removed from favorites'}, status=status.HTTP_200_OK)

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().select_related('profile')
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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
        responses={200: UserManagementSerializer}
    )

    @action(detail=True, methods=['patch'], url_path='update-profile')
    def update_user_profile(self, request, pk=None):
        user = self.get_object()
        serializer = ProfileSerializer(user.profile, data=request.data, partial=True)
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

class JWTLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = JWTLoginSerializer

    @extend_schema(
        request=JWTLoginSerializer,
        summary="Login with phone and password to get JWT tokens"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        
        user = authenticate(username=phone, password=password)
        
        if user: # is not None:
            # outstanding_tokens = OutstandingToken.objects.filter(user=user)

            # for token in outstanding_tokens:
            #     try:
            #         RefreshToken(out_token.token).blacklist()
            #     except Exception:
            #         pass 

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })    
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    request=TokenRefreshSerializer,
    summary="Refresh Access Token"
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass