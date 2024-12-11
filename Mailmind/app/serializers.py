from rest_framework import serializers
from .models import PostData

class ScannedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostData
        fields = '__all__'
