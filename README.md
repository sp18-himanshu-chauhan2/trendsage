# 📈 TrendSage

**TrendSage** is an AI-powered trend research platform that integrates with the **Perplexity API** to fetch, analyze, and deliver trends. It provides versioned results, scheduled refreshes, and email notifications — so users never miss what’s trending in their industry.  

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
│   └── wsgi.py
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

### 5. Environment Variables
- Copy the sample env file and update with your secrets:
```bash
cp .env.sample .env
```
- Fill ```.env``` with your values:
```bash
# Database
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY='your-secret-key-here'
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# External APIs
PERPLEXITY_API_KEY=your-perplexity-api-key-here

# Redis
REDIS_URL=redis://127.0.0.1:6379/0

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_digit_generated_app_password
DEFAULT_FROM_EMAIL=TrendSage <no-reply@trendsage.com>

```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Run Server
```bash
python manage.py runserver
```
Now visit 👉 http://127.0.0.1:8000/trendsage/web/login/

## ⏱️ Celery Setup
### Start Redis (Broker)
```bash
redis-server                            # Mac
docker run -d -p 6379:6379 redis        # Windows on WSL
```

### Start Celery Worker
```bash
celery -A trendsage worker -l info              # for deployment
celery -A trendsage worker -l info -P solo      # for localhost
```

### Start Celery Beat (Scheduler)
```bash
celery -A trendsage beat -l info
```

#### Tasks:
- process_trend_query → handles new queries.
- refresh_trend_queries → refreshes all queries daily and emails results.

## 🔗 API Endpoints (Brief)

### Auth
- ```POST /api/auth/signup/start/``` → Start signup (send OTP)
- ```POST /api/auth/signup/verify/``` → Verify OTP & create account
- ```POST /api/auth/login/``` → Login
- ```POST /api/auth/logout/``` → Logout
- ```POST /api/auth/token/``` → Obtain auth token (DRF default)

### Trends
- ```POST /api/trends/query/ ```→ Create new trend query
- ```GET /api/trends/query/<id>/``` → Get query detail (latest version + metadata)
- ```GET /api/trends/<id>/``` → Get specific trend result detail
- ```POST /api/trends/query/<id>/subscription/``` → Toggle email subscription (legacy)
- ```POST /api/trends/query/<id>/subscription/toggle/``` → Toggle email subscription (preferred)

### Dashboard
- ```GET /api/dashboard/``` → List all queries for the logged-in user

### Profile
- ```GET /api/profile/me/``` → Get current user profile

## 🌐 Web Endpoints (UI)

### Query
- ```GET /trendsage/web/query/``` → New query form
- ```POST /trendsage/web/query/submit/``` → Submit new query
- ```GET /trendsage/web/query/<id>/results/``` → Query detail (latest results, version switcher)
- ```GET /trendsage/web/query/<query_id>/results/<id>/``` → Specific trend result detail
- ```POST /trendsage/web/query/<id>/retry/``` → Retry a failed query

### Auth (UI)
- ```GET /trendsage/web/signup/``` → Signup page
- ```GET /trendsage/web/login/``` → Login page
- ```GET /trendsage/web/logout/``` → Logout

### Dashboard
- ```GET /trendsage/web/dashboard/``` → User dashboard (list queries)

### Subscription
- ```POST /trendsage/web/query/<id>/subscription/toggle/```→ Toggle subscription
- ```GET /trendsage/web/query/<query_id>/subscription/unsubscribe/<user_id>/``` → Unsubscribe confirmation page

### Profile
- ```GET /trendsage/web/profile/``` → Profile page

---

<p align="center">I hope <strong>TrendSage</strong> helps you stay ahead of trends! 🌟</p>