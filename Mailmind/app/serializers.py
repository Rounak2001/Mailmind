from rest_framework import serializers
from .models import PostData

class ScannedPostSerializer(serializers.ModelSerializer):
    image1_url = serializers.SerializerMethodField()
    image2_url = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    updated_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = PostData
        fields = [
            'id',
            'image1_url',
            'image2_url',
            'sender_name',
            'sender_contact',
            'sender_address',
            'sender_pincode',
            'receiver_name',
            'receiver_contact',
            'receiver_address',
            'receiver_pincode',
            'modified_receiver_pincode',
            'merged_reciever_pincode',
            'receiver_latitude',
            'receiver_longitude',
            'customer_feedback',
            'chat_status',
            'created_at',
            'updated_at',
            'created_at_formatted',
            'updated_at_formatted',
        ]

    def get_image1_url(self, obj):
        request = self.context.get('request')
        if obj.image1 and request:
            return request.build_absolute_uri(obj.image1.url)
        return None

    def get_image2_url(self, obj):
        request = self.context.get('request')
        if obj.image2 and request:
            return request.build_absolute_uri(obj.image2.url)
        return None

    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None

    def get_updated_at_formatted(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S') if obj.updated_at else None
