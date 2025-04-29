from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import University
from .utils import validate_password_strength

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
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        
        # Basic format validation (more complex validation could be added here)
        if not value or '@' not in value:
            raise serializers.ValidationError("Enter a valid email address.")
            
        # Check domain for educational emails if needed
        # Uncomment this if you want to restrict to .edu emails
        # if not value.endswith('.edu') and not value.endswith('.edu.et'):
        #     raise serializers.ValidationError("Please use an educational email address.")
        
        return value
    
    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        
        # Validate password strength (simplified for development)
        is_valid, message = validate_password_strength(attrs['password'])
        if not is_valid:
            raise serializers.ValidationError({"password": message})
        
        # Django's built-in validators are bypassed for development
        # try:
        #     validate_password(attrs['password'])
        # except ValidationError as e:
        #     raise serializers.ValidationError({"password": list(e.messages)})
        
        return attrs
    
    def create(self, validated_data):
        # Remove confirm_password from validated data
        validated_data.pop('confirm_password')
        
        # Create user with is_active=True but is_email_verified=False
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

class UserProfileSerializer(serializers.ModelSerializer):
    university_details = UniversitySerializer(source='university', read_only=True)
    phone_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number', 'profile_picture',
            'university', 'university_details', 'role', 'bio', 'date_of_birth',
            'address', 'facebook', 'twitter', 'instagram', 'linkedin',
            'is_email_verified', 'date_joined', 'last_login'
        ]
        read_only_fields = ['email', 'is_email_verified', 'date_joined', 'last_login', 'phone_number']
        extra_kwargs = {
            'university': {'write_only': True},
        }

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'full_name', 'phone_number', 'university', 'role', 'bio',
            'date_of_birth', 'address', 'facebook', 'twitter', 'instagram', 'linkedin'
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
    
    def validate(self, attrs):
        # Check if new passwords match
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Password fields didn't match."})
         # Validate new password strength
        # Validate new password strength (simplified for development)
        is_valid, message = validate_password_strength(attrs['new_password'])
        if not is_valid:
            raise serializers.ValidationError({"new_password": message})
        

        # # Validate new password using Django's built-in validators
        # try:
        #     validate_password(attrs['new_password'])
        # except ValidationError as e:
        #     raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs

# Added Serializer
class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        # Optional: Check if the user actually exists
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        # Optional: Check if the email is already verified
        # user = User.objects.get(email=value) # Already fetched above
        # if user.is_email_verified:
        #     raise serializers.ValidationError("This email is already verified.")
        return value