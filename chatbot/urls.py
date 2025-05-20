from django.urls import path
from .views import ChatbotView

app_name = 'chatbot'

urlpatterns = [
    path('', ChatbotView.as_view(), name='send_message'), # Changed 'send/' to ''
]