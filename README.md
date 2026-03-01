# Interneers Lab 2026

Interneers Lab 2026 is a structured full-stack development program focused on building an end-to-end Inventory Management System using modern backend and frontend technologies.

This repository serves as the working codebase for incremental weekly assignments. The system is designed using clean architecture principles and professional engineering practices.

---

## Tech Stack

- Backend (Python) – Django
- Backend (Go) – Golang
- Frontend – React + TypeScript

---

## Repository Structure

```
backend/
  go/          # Golang backend
  python/      # Django backend
frontend/      # React + TypeScript frontend
```

Each stack contains its own setup instructions where applicable.

---

## Getting Started

### Clone the Repository

```bash
git clone git@github.com:<YourUsername>/interneers-lab.git
cd interneers-lab
```

Ensure Git is configured with the same email used during onboarding:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Running the Python Backend

From the `backend/python` directory:

```bash
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py runserver
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## Architecture Overview (Python Backend)

The Python backend follows a layered, hexagonal structure:

```
core/
    domain/            # Business models
    application/       # Use cases and validations
    adapters/
        api/           # HTTP interface (Django views)
```

Business logic remains independent of the framework.

---

## Weekly Progress

### Week 1
- Repository setup
- Development environment configuration
- Initial API setup
- Introduction to layered architecture

### Week 2
- Product domain model
- In-memory repository
- CRUD APIs
- Input validation
- Pagination support

Future weeks will extend the system with persistence and frontend integration.