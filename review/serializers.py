from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review
from products.models import Product

User = get_user_model()


class ReviewUserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "phone", "email", "full_name"]

    def get_full_name(self, obj):
        try:
            profile = obj.profile
            if profile.first_name and profile.last_name:
                return f"{profile.first_name} {profile.last_name}"
            elif profile.first_name:
                return profile.first_name
            return obj.phone
        except:
            return obj.phone


class ReviewProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image"]


class ReviewSerializer(serializers.ModelSerializer):
    """سریالایزر کامل برای نمایش نظرات"""

    user = ReviewUserSerializer(read_only=True)
    product = ReviewProductSerializer(read_only=True)
    is_verified_buyer = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "user", "product", "text", "rating", "is_approved", "created_at", "updated_at", "is_verified_buyer", "is_owner"]
        read_only_fields = ["id", "created_at", "updated_at", "is_approved"]

    def get_is_verified_buyer(self, obj):
        return obj.is_verified_buyer

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False


class ReviewCreateSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = ["text", "rating", "product_id"]

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("محصول با این شناسه یافت نشد")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد")
        return value

    def validate_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("متن نظر باید حداقل 5 کاراکتر باشد")
        return value.strip()

    def create(self, validated_data):
        product_id = validated_data.pop("product_id")
        product = Product.objects.get(id=product_id)
        user = self.context["request"].user

        # بررسی وجود نظر قبلی
        existing_review = Review.objects.filter(user=user, product=product).first()
        if existing_review:
            raise serializers.ValidationError("شما قبلاً برای این محصول نظر داده‌اید")

        return Review.objects.create(user=user, product=product, **validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["text", "rating"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("امتیاز باید بین 1 تا 5 باشد")
        return value

    def validate_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("متن نظر باید حداقل 5 کاراکتر باشد")
        return value.strip()

    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.rating = validated_data.get("rating", instance.rating)
        instance.is_approved = False  
        instance.save()
        return instance


class ReviewListSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    short_text = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user_name",
            "product_name",
            "short_text",
            "rating",
            "is_approved",
            "created_at",
        ]

    def get_user_name(self, obj):
        try:
            profile = obj.user.profile
            if profile.first_name:
                return profile.first_name
            return obj.user.phone
        except:
            return obj.user.phone

    def get_short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text


class ReviewStatsSerializer(serializers.Serializer):

    total_reviews = serializers.IntegerField()
    approved_reviews = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()


class ProductReviewStatsSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
