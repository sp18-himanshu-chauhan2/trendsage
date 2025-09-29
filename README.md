# 📈 TrendSage

**TrendSage** is an AI-powered trend research platform that integrates with the **Perplexity API** to fetch, analyze, and deliver trends.  
It provides versioned results, scheduled refreshes, and email notifications — so users never miss what’s trending in their industry.  

---

## 🚀 Features

- **User Authentication**
  - Email-based signup with OTP verification (3 attempts limit).
  - Login/Logout with Django session auth.
  - Profile page to see and update query details (like email notifications, activate or deactivate the query).

- **Trend Queries**
  - Submit trend queries with filters (industry, region, persona, date range).
  - Query versioning — new version created on each refresh.
  - Activate/Deactivate queries (control email notifications without deleting).
  - Dashboard with all user queries.
  - Detail page with results, version switcher, and historical view.

- **Background Processing**
  - Celery worker for async Perplexity API fetch.
  - Celery Beat for daily refresh of completed queries.
  - Automatic new trend versions on refresh.

- **Email Notifications**
  - Daily HTML + text emails with trend results.
  - Includes top results, sources, scores, and links back to detail page.
  - Per-query unsubscribe option in emails.

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework  
- **Task Queue:** Celery + Redis  
- **Database:** PostgreSQL  
- **External API:** Perplexity API  
- **Frontend:** Django templates (Bootstrap)  
- **Email:** Django Email Backend (SMTP with Gmail or custom provider) 

---

## 📂 Project Structure

```bash
TrendSage/
├── templates/
│   ├── emails/
│   ├── trends/
│   └── base.html
│  
├── trends/             # Core App
│   ├── email_utils.py
│   ├── models.py
│   ├── query_builder.py
│   ├── serializers.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls_ui.py      # WEB urls
│   ├── views_ui.py
│   ├── views.py        # API views
│   └── urls.py         # API urls
│          
├── trendsage/          # Project root
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └──wsgi.py
│  
├── manage.py
├── README.md           # <------ you are here...
└── requirements.txt
```
## ⚙️ Setup Instructions

### 1. Clone Repo
```bash
git clone https://github.com/sp18-himanshu-chauhan2/trendsage.git
cd trendsage
```
### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL

- Install PostgreSQL (if not already).
- Create a database:

```sql
CREATE DATABASE trendsage_db;
```

- In trendsage/settings.py, configure DB:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "trendsage_db",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```
### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Configure Email

In trendsage/settings.py, add:
```bash
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"   # Generate from Gmail App Passwords
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### 8. Run Server
```bash
python manage.py runserver
```
Now visit 👉 http://127.0.0.1:8000

## ⏱️ Celery Setup
### Start Redis (Broker)
```bash
redis-server
```

### Start Celery Worker
```bash
celery -A trendsage worker -l info
```

### Start Celery Beat (Scheduler)
```bash
celery -A trendsage beat -l info
```
Tasks:

process_trend_query → handles new queries.

refresh_trend_queries → refreshes all queries daily and emails results.

## 📧 Email Setup

### Update settings.py with SMTP:
```bash
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

## 🔗 API Endpoints (Brief)

### Auth
<ul>
    <li>POST /api/signup/start/ → Start signup (send OTP)</li>
    <li>POST /api/signup/verify/ → Verify OTP & create account</li>
    <li>POST /api/login/ → Login</li>
    <li>POST /api/logout/ → Logout</li>
</ul>

### Trends
<ul>
    <li>POST /api/trends/submit/ → Submit new query</li>
    <li>GET /api/trends/ → List queries (with filters)</li>
    <li>GET /api/trends/<id>/ → Query detail (latest version)</li>
    <li>GET /api/trends/<id>/history/ → Query history (all versions)</li>
    <li>POST /api/trends/<id>/deactivate/ → Pause a query</li>
    <li>POST /api/trends/<id>/activate/ → Reactivate a query</li>
</ul>










