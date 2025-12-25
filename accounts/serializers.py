from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile
from products.serializers import ProductSerializer

CustomUser = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'email', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['phone', 'email', 'password', 'profile']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = CustomUser.objects.create_user(**validated_data)
        profile = user.profile
        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('last_name', profile.last_name)
        profile.save()
        return user

class ProfileFavoritesSerializer(serializers.ModelSerializer):
    favorites = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['favorites']

class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

    def validate_phone(self, value):
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("این شماره تلفن قبلاً استفاده شده است.")
        return value

class OTPVerifyRegisterSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True)
    otp_code = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['phone', 'email', 'password', 'profile', 'otp_code']

class PhonePasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

class PhoneOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    otp_code = serializers.CharField(max_length=6)

class UserManagementSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone', 'email', 'profile', 
            'is_active', 'is_staff', 'is_superuser', 
            'date_joined', 'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()  
        return instance

class ProductIdSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

class JWTLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})