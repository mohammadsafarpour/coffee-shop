from rest_framework import serializers
from .models import CustomUser, Profile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    This serializer is used to serialize the Profile model and its related fields.
    """

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'favorites']
        read_only_fields = ['favorites']

    def update(self, instance, validated_data):
        """
        Updates the profile instance with the validated data.

        :param instance: The profile instance to be updated.
        :type instance: Profile
        :param validated_data: The validated data to be used for the update.
        :type validated_data: dict
        :return: The updated profile instance.
        :rtype: Profile
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if validated_data.get('avatar'):
            instance.avatar.delete(save=False)
            instance.avatar = validated_data.get('avatar')
        instance.save()
        return instance

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    This serializer is used to serialize the CustomUser model and its related fields.
    """

    class Meta:
        model = CustomUser
        fields = ['phone', 'email']
        read_only_fields = []

    def update(self, instance, validated_data):
        """
        Updates the user instance with the validated data.

        :param instance: The user instance to be updated.
        :type instance: CustomUser
        :param validated_data: The validated data to be used for the update.
        :type validated_data: dict
        :return: The updated user instance.
        :rtype: CustomUser
        """
        for key, value in validated_data.items():
            if key != 'phone':
                setattr(instance, key, value)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Creates a new user instance with the validated data.

        :param validated_data: The validated data to be used for the creation.
        :type validated_data: dict
        :return: The created user instance.
        :rtype: CustomUser
        """
        user = CustomUser.objects.create_user(**validated_data)
        user.save()
        return user

class CustomUserSerializerWithProfile(CustomUserSerializer):
    """
    CustomUserSerializer with profile data.

    This serializer extends the CustomUserSerializer with the profile data.
    """

    profile = ProfileSerializer()

    class Meta(CustomUserSerializer.Meta):
        """
        Meta class for CustomUserSerializerWithProfile.

        The fields of this serializer are the fields of the CustomUserSerializer
        plus the profile data.
        """
        fields = CustomUserSerializer.Meta.fields + ['profile']

    def create(self, validated_data):
        """
        Create a new user with profile data.

        :param validated_data: The validated data to be used for the creation.
        :type validated_data: dict
        :return: The created user instance.
        :rtype: CustomUser
        """
        profile_data = validated_data.pop('profile', {})
        user = CustomUser.objects.create_user(**validated_data)
        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user

    def update(self, instance, validated_data):
        """
        Update a user with profile data.

        :param instance: The user instance to be updated.
        :type instance: CustomUser
        :param validated_data: The validated data to be used for the update.
        :type validated_data: dict
        :return: The updated user instance.
        :rtype: CustomUser
        """
        profile_data = validated_data.pop('profile', None)
        user = super().update(instance, validated_data)
        if profile_data is not None:
            Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user

    def to_internal_value(self, data):
        """
        Internal value for a user with profile data.

        :param data: The data to be converted to the internal value.
        :type data: dict
        :return: The internal value.
        :rtype: dict
        """
        data = data.copy()
        profile_data = data.pop('profile', None)
        internal = super().to_internal_value(data)
        if profile_data is not None:
            internal['profile'] = profile_data
        return internal
