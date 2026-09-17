# Salon Appointment Booking System - Modular Monolith Backend

Production-quality modular monolith backend built with Python, Django, and Django REST Framework for managing salon service offerings and client appointment bookings.

## Architecture

This backend follows a modular monolith architecture pattern. Domain logic is segregated into discrete modules within the `apps/` directory, allowing clean boundaries without unnecessary abstractions or premature microservices overhead.

```
backend/
├── config/             # Project-wide settings, URL routing, WSGI/ASGI entrypoints
├── apps/               # Business domain applications
│   ├── common/         # Cross-cutting endpoints (health check)
│   ├── services/       # Salon services domain (Phase 2)
│   └── appointments/   # Appointment bookings domain (Phase 2)
├── requirements/       # Modular dependency manifests (base.txt, dev.txt)
├── manage.py           # Django administrative CLI wrapper
├── .env.example        # Environment variable template
└── db.sqlite3          # Development SQLite database (git-ignored)
```

## Setup & Running Locally

### Prerequisites
- Python 3.12+

### 1. Environment & Dependencies

From the project root:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r backend/requirements/dev.txt
```

### 2. Environment Configuration

Copy the example environment configuration into `backend/.env`:

```bash
cp backend/.env.example backend/.env
```

Environment Variables:
- `DEBUG`: Controls debug mode (`True` for development, `False` for production).
- `SECRET_KEY`: Secret key for cryptographic signing.
- `ALLOWED_HOSTS`: Comma-separated list of allowed host header values.
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins for cross-origin frontend requests.

### 3. Database & System Verification

Run Django system checks and migrations from the `backend/` directory:

```bash
cd backend
python manage.py check
python manage.py migrate
python manage.py test apps.common
```

### 4. Running Development Server

Start the development server:

```bash
python manage.py runserver
```

The server will start on `http://127.0.0.1:8000/`.

### 5. Health Check Endpoint

To verify system operational status:

```bash
curl http://127.0.0.1:8000/api/health/
```

**Response (`200 OK`):**
```json
{
  "status": "ok"
}
```

## Phase Roadmap

- [x] **Phase 1**: Project initialization, environment setup, modular structure, health check endpoint.
- [ ] **Phase 2**: Services and Appointments business domain models, serializers, views, and business rules.
- [ ] **Phase 3**: Frontend integration (React SPA).
