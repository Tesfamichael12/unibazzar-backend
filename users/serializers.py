from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import University
from .utils import validate_password_strength
from .models import StudentProfile, MerchantProfile, TutorProfile, CampusAdminProfile
from .models import User
from products.serializers import StudentProductSerializer, MerchantProductSerializer, TutorServiceSerializer

User = get_user_model()

class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ['id', 'name', 'location', 'website']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), required=False, allow_null=True)
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'confirm_password', 'university', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        if not value or '@' not in value:
            raise serializers.ValidationError("Enter a valid email address.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        is_valid, message = validate_password_strength(attrs['password'])
        if not is_valid:
            raise serializers.ValidationError({"password": message})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            university=validated_data.get('university'),
            is_active=True,
            is_email_verified=False,
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

# Define Profile Serializers BEFORE UserProfileSerializer
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        # Includes all fields from the StudentProfile model
        fields = "__all__"

        # To include all fields automatically (less explicit, but comprehensive):
        # fields = '__all__' 
        # exclude = ['user'] # Exclude the direct user link if UserProfileSerializer handles user details

class MerchantProfileSerializer(serializers.ModelSerializer):
    # If nearest_university is a ForeignKey to University model and you want nested details:
    # nearest_university_details = UniversitySerializer(source='nearest_university', read_only=True)
    class Meta:
        model = MerchantProfile
        # Includes all fields from the MerchantProfile model
        fields = "__all__"
        # To include all fields automatically:
        # fields = '__all__'
        # exclude = ['user']

class TutorProfileSerializer(serializers.ModelSerializer):
    # If university_preference is a ForeignKey to University model and you want nested details:
    # university_preference_details = UniversitySerializer(source='university_preference', read_only=True)
    class Meta:
        model = TutorProfile
        # Includes all fields from the TutorProfile model
        fields = '__all__'
        # To include all fields automatically:
        # fields = '__all__'
        # exclude = ['user']

class CampusAdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusAdminProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for user profile information, including role-specific details.
    This is intended for the /users/me/ endpoint and login response.
    """
    is_student = serializers.SerializerMethodField()
    is_tutor = serializers.SerializerMethodField()
    is_merchant = serializers.SerializerMethodField()

    # Nested profile data - these will now use the updated profile serializers
    student_profile_data = StudentProfileSerializer(source='student_profile', read_only=True, required=False, allow_null=True)
    tutor_profile_data = TutorProfileSerializer(source='tutor_profile', read_only=True, required=False, allow_null=True)
    merchant_profile_data = MerchantProfileSerializer(source='merchant_profile', read_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'phone_number', 
            'profile_picture', 
            'role', 
            'bio', 
            'date_of_birth', 
            'university', 
            'is_email_verified',
            'date_joined',
            'last_login',
            'is_student',
            'is_tutor',
            'is_merchant',
            'student_profile_data',
            'tutor_profile_data',
            'merchant_profile_data',
        ]
        read_only_fields = fields

    def get_is_student(self, obj):
        return hasattr(obj, 'student_profile') and obj.student_profile is not None

    def get_is_tutor(self, obj):
        return hasattr(obj, 'tutor_profile') and obj.tutor_profile is not None

    def get_is_merchant(self, obj):
        return hasattr(obj, 'merchant_profile') and obj.merchant_profile is not None

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'full_name', 'phone_number', 'university', 'role', 'bio',
            'date_of_birth'
        ]

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']

class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class PhoneNumberUpdateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        ref_name = 'UserPasswordChange'

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Password fields didn't match."})
        is_valid, message = validate_password_strength(attrs['new_password'])
        if not is_valid:
            raise serializers.ValidationError({"new_password": message})
        return attrs

class UserListingsSerializer(serializers.ModelSerializer): # MODIFIED
    """
    Serializer for a user's listed products and services.
    """
    # These fields will use the related_name from the User model
    # (e.g., user.student_products, user.merchant_products, user.tutor_services)
    student_products = StudentProductSerializer(many=True, read_only=True)
    merchant_products = MerchantProductSerializer(many=True, read_only=True)
    tutor_services = TutorServiceSerializer(many=True, read_only=True)

    class Meta:
        model = User # MODIFIED - specify the model
        fields = [
            'id', 
            'full_name', 
            'email', 
            'student_products', 
            'merchant_products', 
            'tutor_services'
        ]
        # Optional: if you want to ensure this serializer is only for reading
        read_only_fields = ['id', 'full_name', 'email', 'student_products', 'merchant_products', 'tutor_services']


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class CustomJWTSerializer(serializers.Serializer):
    access = serializers.CharField(source='access_token', read_only=True)
    refresh = serializers.CharField(source='refresh_token', read_only=True)
    user = UserProfileSerializer(read_only=True)

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()