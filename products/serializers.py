from rest_framework import serializers
from .models import MerchantProduct, StudentProduct, TutorService, Review, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MerchantProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    nearest_university = serializers.CharField(read_only=True)
    phone_number = serializers.CharField()

    class Meta:
        model = MerchantProduct
        fields = '__all__'
        read_only_fields = ['owner', 'nearest_university']

class StudentProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    university = serializers.CharField(read_only=True)
    phone_number = serializers.CharField()

    class Meta:
        model = StudentProduct
        fields = '__all__'
        read_only_fields = ['owner', 'university']

class TutorServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    university = serializers.CharField(read_only=True)
    phone_number = serializers.CharField()

    class Meta:
        model = TutorService
        fields = '__all__'
        read_only_fields = ['owner', 'university']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['reviewer']
