from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name')
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create user and associated profile."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        
        # Create associated profile
        Profile.objects.create(user=user)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (read-only for profile endpoints)."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ('id', 'display_name', 'bio', 'avatar', 'user')
        read_only_fields = ('id', 'user')
    
    def update(self, instance, validated_data):
        """Update profile and related user data if provided."""
        user_data = validated_data.pop('user', {})
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update user fields if provided
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr != 'email':  # Don't allow email updates
                    setattr(user, attr, value)
            user.save()
        
        return instance