import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from products.models import MerchantProduct, StudentProduct, TutorService, Category
from django.contrib.auth import get_user_model

User = get_user_model()

PRODUCT_NAMES = [
    "Laptop", "Smartphone", "Headphones", "Backpack", "Notebook", "Pen", "Desk Lamp", "Calculator", "USB Drive", "Monitor",
    "Textbook", "Reference Book", "Lab Kit", "Drawing Set", "Whiteboard", "Projector", "Tablet", "Charger", "Speaker", "Camera"
]
FOOD_NAMES = [
    "Injera with Wot", "Burger", "Pizza", "Pasta", "Salad", "Sandwich", "Coffee", "Juice", "Smoothie", "Cake"
]
TUTOR_TOPICS = [
    "Mathematics", "Physics", "Chemistry", "Biology", "English", "Programming", "History", "Economics", "Statistics", "Art"
]
SERVICE_NAMES = [
    "Laundry", "Printing", "Room Cleaning", "Transport", "Event Planning", "Tutoring", "Mentoring", "Resume Review", "Career Advice", "Counseling"
]

def get_image_paths(folder):
    folder_path = os.path.join(settings.MEDIA_ROOT, folder)
    if not os.path.exists(folder_path):
        return []
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

def get_random_phone():
    return "+2519" + "".join([str(random.randint(0,9)) for _ in range(8)])

class Command(BaseCommand):
    help = "Seed the database with ALL demo products/services using every image in the media folder."

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(email="demo@unibazzar.com", defaults={
            "full_name": "Demo User",
            "role": "merchant",
            "is_email_verified": True,
            "is_active": True,
            "password": "demo1234"
        })
        categories = {c.name.lower(): c for c in Category.objects.all()}
        product_images = get_image_paths("Product_image")
        food_images = get_image_paths("food_image")
        tutor_images = get_image_paths("image_tutor")
        merchant_images = get_image_paths("merchant_products")
        student_images = get_image_paths("student_products")
        tutor_service_images = get_image_paths("tutor_services")
        # MerchantProduct (products)
        for i, img_path in enumerate(product_images):
            name = random.choice(PRODUCT_NAMES)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} Demo {i+1}",
                photo=photo,
                category=categories.get("products"),
                description=f"Demo {name} description.",
                tags="demo,product",
                price=round(random.uniform(100, 2000), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        # MerchantProduct (food)
        for i, img_path in enumerate(food_images):
            name = random.choice(FOOD_NAMES)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} Food Demo {i+1}",
                photo=photo,
                category=categories.get("food"),
                description=f"Delicious {name} for sale.",
                tags="food,merchant",
                price=round(random.uniform(20, 200), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        # StudentProduct (student_products images)
        for i, img_path in enumerate(student_images):
            name = random.choice(PRODUCT_NAMES)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            StudentProduct.objects.create(
                owner=user,
                name=f"{name} Student Demo {i+1}",
                category=categories.get("educational materials"),
                condition=random.choice(["used", "slightly used", "new"]),
                photo=photo,
                description=f"Demo {name} for students.",
                tags="student,product",
                price=round(random.uniform(50, 1000), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        # TutorService (tutor_services images)
        for i, img_path in enumerate(tutor_service_images):
            topic = random.choice(TUTOR_TOPICS)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            TutorService.objects.create(
                owner=user,
                banner_photo=photo,
                category=categories.get("tutoring"),
                description=f"Expert tutoring in {topic}.",
                price=round(random.uniform(100, 500), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        # TutorService (image_tutor images)
        for i, img_path in enumerate(tutor_images):
            topic = random.choice(TUTOR_TOPICS)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            TutorService.objects.create(
                owner=user,
                banner_photo=photo,
                category=categories.get("tutoring"),
                description=f"Expert tutoring in {topic}.",
                price=round(random.uniform(100, 500), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        # MerchantProduct (merchant_products images)
        for i, img_path in enumerate(merchant_images):
            name = random.choice(PRODUCT_NAMES)
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path))
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} Merchant Demo {i+1}",
                photo=photo,
                category=categories.get("services"),
                description=f"Demo {name} merchant service.",
                tags="merchant,service",
                price=round(random.uniform(100, 2000), 2),
                phone_number=get_random_phone()
            )
            photo.close()
        self.stdout.write(self.style.SUCCESS("Seeded all demo products/services from media folder!"))
