#/users/sarah/downloads/smart-city-project/auth_service/users/serializers.py
from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'city', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            city=validated_data.get('city'),
            phone=validated_data.get('phone'),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at', 'city', 'phone']
