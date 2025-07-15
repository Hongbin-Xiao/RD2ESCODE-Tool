from rest_framework import serializers
from user.models import SysUser
from django.contrib.auth.hashers import make_password

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = ['username', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return SysUser.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = ['id', 'username', 'phone']
