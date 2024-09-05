from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction
User = get_user_model()
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'name', 'phone', 'email', 'amount', 'transaction_date', 'status']
        read_only_fields = ['transaction_id'] 


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            user_type=validated_data.get('user_type', 'staff')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user