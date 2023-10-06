from rest_framework import serializers
from account.models import Account


class VerifyOtpSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=10)
    to = serializers.CharField(required=True, max_length=25)

    class Meta:
        model = Account
        fields = ("to", "code",)
