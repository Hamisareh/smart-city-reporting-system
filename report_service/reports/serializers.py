# reports/serializers.py

from rest_framework import serializers
from .models import Report, Category, ReportImage, StatusHistory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportImage
        fields = '__all__'


class StatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusHistory
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    images = ReportImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Report
        fields = [
            'id', 'description', 'latitude', 'longitude', 'status',
            'priority', 'user_id', 'category', 'created_at', 'images', 'uploaded_images'
        ]
        # ✅ FIX: status removed from read_only_fields so PATCH can update it.
        # user_id stays read-only — always set from JWT token, never from client.
        read_only_fields = ['id', 'created_at', 'user_id']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        # ✅ Force status to 'pending' on creation regardless of what client sends
        validated_data['status'] = 'pending'
        report = Report.objects.create(**validated_data)

        for image in uploaded_images:
            ReportImage.objects.create(report=report, image=image)

        return report