# 🎓🛒 UniBazzar Backend

Welcome to the **UniBazzar** backend!  
A modern Django REST API for a university marketplace platform, supporting students, merchants, tutors, and campus admins.  
Built with ❤️ for hackathons, learning, and real-world deployment.

---

## 🚀 Features

- 🔐 **JWT Authentication** (with email verification)
- 📧 **Email Verification & Password Reset** (custom HTML emails)
- 👤 **User Profiles** (student, merchant, tutor, campus admin)
- 🏫 **University Directory** (CSV import, API listing)
- 🖼️ **Profile Picture Upload**
- 📱 **Phone & Email Update**
- 🔄 **Swagger & Redoc API Docs**
- 🛠️ **Admin Panel** (Django admin)
- 🌍 **CORS & Social Auth Ready**
- 🧪 **Comprehensive Tests**

---

## 🏗️ Project Structure

```
database-schema.mermaid
db.sqlite3
manage.py
requirements.txt
universities.csv
staticfiles/
    ...
templates/
    home.html
    users/
        email_reset_password.html
        email_reset_password.txt
        email_verification_failed.html
        email_verification_success.html
        email_verification.html
unibazzar/
    __init__.py
    asgi.py
    init_env.py
    settings.py
    urls.py
    wsgi.py
    ...
users/
    __init__.py
    admin.py
    apps.py
    authentication.py
    backends.py
    models.py
    serializers.py
    signals.py
    tests.py
    tokens.py
    urls_profile.py
    urls.py
    utils.py
    views_profile.py
    views.py
    ...
```

---

## ⚙️ Setup & Installation

1. **Clone the repo**

   ```bash
   git clone <your-repo-url>
   cd unibazzar-backend
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Create a `.env` file in the project root (if not present).
   - Set your email credentials and secret keys.

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Load universities (optional)**

   ```bash
   python manage.py load_universities
   ```

7. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the server**
   ```bash
   python manage.py runserver
   ```

---

## 🧑‍💻 API Endpoints

- **Swagger UI:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **Redoc:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Admin Panel:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Main Endpoints

| Endpoint                                | Method        | Description                      |
| --------------------------------------- | ------------- | -------------------------------- |
| `/api/users/register/`                  | POST          | Register new user                |
| `/api/users/login/`                     | POST          | Login (JWT)                      |
| `/api/users/logout/`                    | POST          | Logout (blacklist refresh token) |
| `/api/users/verify-email/`              | GET           | Email verification               |
| `/api/users/resend-verification-email/` | POST          | Resend verification email        |
| `/api/users/me/`                        | GET/PUT/PATCH | User profile                     |
| `/api/users/me/avatar/`                 | POST/DELETE   | Profile picture upload/delete    |
| `/api/users/me/email/`                  | PATCH         | Change email (with verification) |
| `/api/users/me/phone/`                  | PATCH         | Update phone number              |
| `/api/users/me/password/`               | POST          | Change password                  |
| `/api/users/universities/`              | GET           | List universities                |
| `/api/password_reset/`                  | POST          | Request password reset (email)   |
| `/api/password_reset/confirm/`          | POST          | Confirm password reset (token)   |

---

## 🛡️ Authentication

- Uses **JWT** (via djangorestframework-simplejwt)
- Email verification required before login
- Password reset via email (HTML & plain text)

---

## 🏫 University Import

- Add new universities to `universities.csv`
- Run:
  ```bash
  python manage.py load_universities
  ```

---

## 🧪 Running Tests

```bash
python manage.py test users
```

---

## 📦 Environment Variables (`.env`)

- `SECRET_KEY` – Django secret key
- `DEBUG` – Set to `True` for development
- `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` – For sending emails
- `DEFAULT_FROM_EMAIL` – Default sender
- `FRONTEND_URL` – Used in email templates for links

---

## 📝 Tech Stack

- 🐍 Python 3.10+
- 🦄 Django 4.x
- 🛡️ Django REST Framework
- 🔑 SimpleJWT
- 📧 django-rest-passwordreset
- 🦄 drf-yasg (Swagger docs)
- 🦉 django-allauth (social auth ready)
- 🏫 SQLite (default) or PostgreSQL (Supabase ready)

---

## 💡 Tips

- For development, emails are printed to the console if SMTP fails.
- You can customize email templates in `templates/users/`.
- Use the admin panel to manage users and universities.

---

## 🤝 Contributing

Pull requests are welcome!  
Please open an issue first to discuss what you would like to change.

---

## 🧑‍🎓 Authors

- Tesfamichael Tafere & Team
- ***

## 📄 License

BSD License

---

## 🌟 Enjoy building with UniBazzar! 🌟
