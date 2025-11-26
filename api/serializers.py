from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Show, Booking

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    show = ShowSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
