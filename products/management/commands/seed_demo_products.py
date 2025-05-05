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
    help = "Seed the database with demo products, food, tutoring, and services"

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
        online_product_images = [
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
            "https://images.unsplash.com/photo-1519125323398-675f0ddb6308"
        ]
        online_food_images = [
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
            "https://images.unsplash.com/photo-1464306076886-debca5e8a6b0"
        ]
        online_tutor_images = [
            "https://images.unsplash.com/photo-1513258496099-48168024aec0",
            "https://images.unsplash.com/photo-1503676382389-4809596d5290"
        ]
        online_service_images = [
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
        ]
        # MerchantProduct (products)
        for i in range(25):
            name = random.choice(PRODUCT_NAMES)
            img_path = product_images[i % len(product_images)] if product_images else None
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path)) if img_path else None
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} {i+1}",
                photo=photo if photo else online_product_images[i % len(online_product_images)],
                category=categories.get("products"),
                description=f"Demo {name} description.",
                tags="demo,product",
                price=round(random.uniform(100, 2000), 2),
                phone_number=get_random_phone()
            )
            if photo:
                photo.close()
        # StudentProduct (educational materials)
        for i in range(25):
            name = random.choice(PRODUCT_NAMES)
            img_path = product_images[i % len(product_images)] if product_images else None
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path)) if img_path else None
            StudentProduct.objects.create(
                owner=user,
                name=f"{name} {i+1}",
                category=categories.get("educational materials"),
                condition=random.choice(["used", "slightly used", "new"]),
                photo=photo if photo else online_product_images[i % len(online_product_images)],
                description=f"Demo {name} for students.",
                tags="student,product",
                price=round(random.uniform(50, 1000), 2),
                phone_number=get_random_phone()
            )
            if photo:
                photo.close()
        # MerchantProduct (food)
        for i in range(20):
            name = random.choice(FOOD_NAMES)
            img_path = food_images[i % len(food_images)] if food_images else None
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path)) if img_path else None
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} {i+1}",
                photo=photo if photo else online_food_images[i % len(online_food_images)],
                category=categories.get("food"),
                description=f"Delicious {name} for sale.",
                tags="food,merchant",
                price=round(random.uniform(20, 200), 2),
                phone_number=get_random_phone()
            )
            if photo:
                photo.close()
        # TutorService (tutoring)
        for i in range(20):
            topic = random.choice(TUTOR_TOPICS)
            img_path = tutor_images[i % len(tutor_images)] if tutor_images else None
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path)) if img_path else None
            TutorService.objects.create(
                owner=user,
                banner_photo=photo if photo else online_tutor_images[i % len(online_tutor_images)],
                category=categories.get("tutoring"),
                description=f"Expert tutoring in {topic}.",
                price=round(random.uniform(100, 500), 2),
                phone_number=get_random_phone()
            )
            if photo:
                photo.close()
        # MerchantProduct (services)
        for i in range(10):
            name = random.choice(SERVICE_NAMES)
            img_path = product_images[i % len(product_images)] if product_images else None
            photo = File(open(img_path, "rb"), name=os.path.basename(img_path)) if img_path else None
            MerchantProduct.objects.create(
                owner=user,
                name=f"{name} Service {i+1}",
                photo=photo if photo else online_service_images[i % len(online_service_images)],
                category=categories.get("services"),
                description=f"Professional {name} service.",
                tags="service,merchant",
                price=round(random.uniform(50, 500), 2),
                phone_number=get_random_phone()
            )
            if photo:
                photo.close()
        self.stdout.write(self.style.SUCCESS("Seeded 100 demo products/services!"))
