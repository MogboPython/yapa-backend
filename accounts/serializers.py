from rest_framework import serializers

from .models import Account


class CreateAccountSerializer(serializers.ModelSerializer):
    address = serializers.CharField(required=True)
    username = serializers.CharField(required=False)
    profile_picture = serializers.ImageField(required=False)

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('uuid', 'address', 'username', 'profile_picture_url', 'created_at', 'updated_at')
