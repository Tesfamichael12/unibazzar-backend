from django.contrib.auth.models import AbstractUser, BaseUserManager, AbstractBaseUser, PermissionsMixin
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

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('merchant', 'Merchant'),
        ('campus_admin', 'Campus Admin'),
        ('super_admin', 'Super Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    # address = models.CharField(max_length=255, blank=True, null=True) # Removed
    
    # Social media links - Removed
    # facebook = models.URLField(blank=True, null=True)
    # twitter = models.URLField(blank=True, null=True)
    # instagram = models.URLField(blank=True, null=True)
    # linkedin = models.URLField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # Required for Django admin
    is_superuser = models.BooleanField(default=False) # Required for Django admin
    is_email_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

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

    class Meta:
        ordering = ['pk']

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