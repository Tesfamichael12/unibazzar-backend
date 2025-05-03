from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class University(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("University")
        verbose_name_plural = _("Universities")
        ordering = ['name']
    
    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    """Define a custom manager for the User model with no username field."""
    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Basic fields
    full_name = models.CharField(_('full name'), max_length=255)
    email = models.EmailField(_('email address'), unique=True)
    
    # Phone number (no validation)
    phone_number = models.CharField(
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name=_('phone number')
    )
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('profile picture')
    )
    
    # University and role
    university = models.ForeignKey(
        'University', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name=_('university')
    )
    
    ROLE_CHOICES = [
        ('student', _('Student')),
        ('merchant', _('Merchant')),
        ('tutor', _('Tutor')),
        ('service_provider', _('Service Provider')),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        verbose_name=_('role')
    )
    
    # Verification status
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_('email verified')
    )
    
    # Additional fields
    bio = models.TextField(blank=True, null=True, verbose_name=_('biography'))
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=_('date of birth'))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('address'))
    
    # Social media links
    facebook = models.URLField(blank=True, null=True, verbose_name=_('Facebook'))
    twitter = models.URLField(blank=True, null=True, verbose_name=_('Twitter'))
    instagram = models.URLField(blank=True, null=True, verbose_name=_('Instagram'))
    linkedin = models.URLField(blank=True, null=True, verbose_name=_('LinkedIn'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Set email as the USERNAME_FIELD and remove username from REQUIRED_FIELDS
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']
    
    # Use the custom manager
    objects = UserManager()
    
    # Fix for removing the username field
    username = None
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email

class StudentProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='student_profile')
    university_id = models.CharField(max_length=100)
    university_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.full_name} - {self.university_name}"

class MerchantProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='merchant_profile')
    store_name = models.CharField(max_length=255)
    nearest_university = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    tin_number = models.CharField(max_length=50)
    business_docs = models.FileField(upload_to='business_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.store_name}"

class TutorProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='tutor_profile')
    department = models.CharField(max_length=255)
    year = models.IntegerField()
    subjects_scores = models.JSONField(default=dict, blank=True)
    teaching_levels = models.CharField(max_length=255)
    edu_docs = models.FileField(upload_to='edu_docs/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.department}"

class CampusAdminProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='campus_admin_profile')
    university = models.CharField(max_length=255)
    admin_role = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.full_name} - {self.university} ({self.admin_role})"