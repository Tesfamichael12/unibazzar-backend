# UniBazzar Backend API Endpoints

This document lists all major API endpoints in the UniBazzar backend, their purpose, request/response formats, and authentication requirements.

---

## Users API (`/api/users/`)

### Registration & Authentication

- **POST `/api/users/register/`**
  - Register a new user.
  - Request: `{ "email": ..., "password": ... }`
  - Response: Success or error, with verification email status.
- **GET `/api/users/verify-email/<uidb64>/<token>/`**
  - Verify user email via link.
  - Response: HTML page (success/failure).
- **POST `/api/users/resend-verification-email/`**
  - Resend verification email.
  - Request: `{ "email": ... }`
  - Response: Success or error.
- **POST `/api/users/login/`**
  - Login (JWT).
  - Request: `{ "email": ..., "password": ... }`
  - Response: `{ "access": ..., "refresh": ... }` or error.
- **POST `/api/users/logout/`**
  - Logout (blacklist refresh token).
  - Request: `{ "refresh": ... }`
  - Response: Success or error.

### Profile & Listings

- **GET/PUT/PATCH `/api/users/me/`**
  - Get or update current user's profile.
  - Auth required.
- **POST/DELETE `/api/users/me/avatar/`**
  - Upload or remove profile picture.
  - Auth required.
- **PATCH `/api/users/me/email/`**
  - Change email (triggers verification).
  - Auth required.
- **PATCH `/api/users/me/phone/`**
  - Update phone number.
  - Auth required.
- **POST `/api/users/me/password/`**
  - Change password.
  - Auth required.
- **GET `/api/users/<user_id>/listings/`**
  - Get all listings for a user.

### Universities

- **GET `/api/users/universities/`**
  - List all universities.

---

## Products API (`/api/products/`)

- **Merchant Products**
  - **GET/POST `/api/products/merchant-products/`**
  - **GET/PUT/PATCH/DELETE `/api/products/merchant-products/<id>/`**
- **Student Products**
  - **GET/POST `/api/products/student-products/`**
  - **GET/PUT/PATCH/DELETE `/api/products/student-products/<id>/`**
- **Tutor Services**
  - **GET/POST `/api/products/tutor-services/`**
  - **GET/PUT/PATCH/DELETE `/api/products/tutor-services/<id>/`**
- **Reviews**
  - **GET/POST `/api/products/reviews/`**
  - **GET/PUT/PATCH/DELETE `/api/products/reviews/<id>/`**
- **Categories**
  - **GET/POST `/api/products/categories/`**
  - **GET/PUT/PATCH/DELETE `/api/products/categories/<id>/`**

All product endpoints support standard REST actions. Some require authentication.

---

## Chatbot API (`/api/chatbot/`)

- **POST `/api/chatbot/`**
  - Send a message to the UniBazzar AI chatbot.
  - Request: `{ "message": ... }`
  - Response: `{ "reply": ... }` or error.

---

## Auth & Password Reset

- **POST `/api/token/refresh/`**
  - Refresh JWT token.
- **POST `/api/token/verify/`**
  - Verify JWT token.
- **Password Reset**
  - **POST `/api/password_reset/`**
  - **POST `/api/password_reset/confirm/`**
  - (See [django-rest-passwordreset](https://github.com/anx-ckreuzberger/django-rest-passwordreset) for details)

---

## API Documentation

- **Swagger UI:** `/swagger/`
- **Redoc:** `/redoc/`

---

## Notes

- Most endpoints return JSON unless otherwise noted.
- Authentication is via JWT for protected endpoints.
- See Swagger UI for detailed request/response schemas.
