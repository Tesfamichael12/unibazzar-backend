from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MerchantProduct(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='merchant_products')
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='merchant_products/')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='merchant_products')
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    nearest_university = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.owner and getattr(self.owner, 'university', None):
            self.nearest_university = str(self.owner.university)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class StudentProduct(models.Model):
    CONDITION_CHOICES = [
        ('used', 'Used'),
        ('slightly used', 'Slightly Used'),
        ('new', 'New'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_products')
    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='student_products')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    photo = models.ImageField(upload_to='student_products/')
    description = models.TextField()
    tags = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    university = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.owner and getattr(self.owner, 'university', None):
            self.university = str(self.owner.university)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TutorService(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_services')
    banner_photo = models.ImageField(upload_to='tutor_services/')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_services')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    university = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if self.owner and getattr(self.owner, 'university', None):
            self.university = str(self.owner.university)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TutorService by {self.owner}"

class Review(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    rating = models.IntegerField()
    comment = models.TextField()
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return f"Review by {self.reviewer} ({self.rating})"
