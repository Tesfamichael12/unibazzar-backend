import google.generativeai as genai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny # Or IsAuthenticated if you want to protect it

# --- Gemini API Configuration ---
GEMINI_API_CONFIGURED = False
GEMINI_MODEL_INITIALIZED = False
GENERATIVE_MODEL = None

if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        GEMINI_API_CONFIGURED = True
        # Using gemini-1.5-flash-latest for a balance of speed and capability.
        GENERATIVE_MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')
        GEMINI_MODEL_INITIALIZED = True
        print("Gemini API configured and model initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to configure Gemini API or initialize model: {e}")
else:
    print("WARNING: GEMINI_API_KEY not set. Chatbot functionality will be disabled.")
# --- End Gemini API Configuration ---


class ChatbotView(APIView):
    """
    API View for interacting with the Gemini chatbot.
    Accepts a POST request with a 'message' field in the JSON body
    and returns a 'reply' from the Gemini model.
    """
    permission_classes = [AllowAny] # Change to [IsAuthenticated] to restrict access

    # Define the project context here
    PROJECT_CONTEXT = """You are UniBazzar Helper, an intelligent and friendly AI assistant for the UniBazzar platform.

**About UniBazzar:**
UniBazzar is a comprehensive online marketplace and service hub designed specifically for university and college communities. Our mission is to connect students, merchants, tutors, and local service providers in a seamless and efficient digital environment.

**Key Features & What Users Can Do:**
*   **Marketplace (Products):**
    *   Students can buy and sell a wide variety of items, including new and used textbooks, electronics, furniture, clothing, class notes, and more.
    *   Merchants (e.g., local bookstores, electronics shops, campus stores) can list their products for sale to the student community.
*   **Services:**
    *   **Tutoring:** Students can find tutors for various subjects and academic levels. Tutors can list their services, expertise, and availability.
    *   **Campus Services:** Users can discover and offer various campus-related services, such as freelance work (graphic design, writing), repair services, food delivery from local vendors, laundry services, etc.
*   **User Roles:**
    *   **Students:** Can buy, sell, search for tutors, and look for services.
    *   **Merchants:** Can set up a store profile, list products, and manage orders.
    *   **Tutors:** Can create a tutor profile, list subjects they teach, set their rates, and manage tutoring requests.
    *   **Service Providers:** Can list various services they offer to the campus community.

**Your Role as UniBazzar Helper:**
*   **Guide Users:** Help users navigate the platform. For example, if a user asks "How do I sell my old laptop?", explain the steps to list an item on UniBazzar.
*   **Answer Questions:** Provide information about UniBazzar\'s features, policies (if known, otherwise state you don\'t have access to specific policy details), and how to use the platform effectively.
*   **Promote UniBazzar:** Encourage users to explore different sections of UniBazzar.
*   **Problem Solving:** Offer general advice on how to resolve common issues or direct them to where they might find help (e.g., "For payment issues, please check our FAQ or contact support through the app.").
*   **Maintain Context:** Keep your answers focused on UniBazzar. If a user asks a general question unrelated to UniBazzar or university life, politely provide a brief answer if appropriate, and then try to steer the conversation back to UniBazzar\'s services. For example: "The capital of France is Paris. Now, are you interested in finding any study materials for your French class on UniBazzar?"

**Tone:**
Be friendly, approachable, helpful, and professional. Use clear and concise language.

**Limitations:**
*   You do not have access to real-time user data, personal account information, or live inventory. Do not pretend to.
*   You cannot process transactions or make changes to user accounts.
*   Avoid giving opinions on products or services unless it\'s based on general, publicly known information.
*   If you don\'t know the answer to something specific about UniBazzar\'s internal operations or a very niche query, it\'s okay to say "I don\'t have that specific information, but you can try searching our help section on the UniBazzar platform."

Please use this understanding of UniBazzar to assist users effectively.
"""

    def post(self, request, *args, **kwargs):
        if not GEMINI_API_CONFIGURED:
            return Response(
                {"error": "Gemini API key not configured on the server. Please check server logs and .env file."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        if not GEMINI_MODEL_INITIALIZED or GENERATIVE_MODEL is None:
            return Response(
                {"error": "Gemini model not initialized. Please check server logs."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        user_message = request.data.get('message')
        if not user_message:
            return Response(
                {"error": "No 'message' field found in the request body."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_message, str) or not user_message.strip():
            return Response(
                {"error": "'message' field must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Prepend the project context to the user's message
            prompt_with_context = f"{self.PROJECT_CONTEXT}\n\nUser query: {user_message}"
            
            response = GENERATIVE_MODEL.generate_content(prompt_with_context)
            
            bot_response_text = ""
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'text'):
                        bot_response_text += part.text
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason_message = getattr(response.prompt_feedback, 'block_reason_message', 'Content blocked')
                bot_response_text = f"I'm sorry, I can't respond to that. Reason: {block_reason_message}."
                print(f"Gemini content blocked. Reason: {response.prompt_feedback.block_reason}, Message: {block_reason_message}")
            else:
                bot_response_text = "I received your message, but I'm unable to generate a specific reply at this moment."
                print(f"Gemini response did not contain expected text parts. Full response: {response}")

            return Response({"reply": bot_response_text.strip()}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR: Exception during Gemini API call: {type(e).__name__} - {e}")
            return Response(
                {"error": "An unexpected error occurred while communicating with the chatbot service."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
