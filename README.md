# Interneers Lab

Welcome to the Interneers Lab repository. This project serves as a foundational codebase for building a small end-to-end **Inventory Management System** over the duration of the program.

The repository includes:

- Django (Python)
- Golang (Go)
- React (TypeScript)
- MongoDB (via Docker Compose)

Use the same email shared during onboarding when configuring Git.

---

## Current Backend Implementation (Week 1)

The Python backend has been structured using **Hexagonal Architecture (Ports and Adapters pattern)**.

At this stage, the system exposes a simple HTTP GET endpoint:

GET /api/greet/?name=<username>

### Example

http://127.0.0.1:8000/api/greet/?name=Rudrakshi

### Response

```json
{
  "message": "Hello Rudrakshi"
}
```

If no name is provided:

GET /api/greet/

A default greeting response is returned.

---

## Architecture Overview

The Python backend follows this layered structure:

backend/python/  
├── django_app/        # Django project configuration  
└── core/  
&nbsp;&nbsp;&nbsp;&nbsp;├── domain/         # Business logic  
&nbsp;&nbsp;&nbsp;&nbsp;├── application/    # Use cases  
&nbsp;&nbsp;&nbsp;&nbsp;└── adapters/api/   # HTTP interface  

### Layer Responsibilities

- **Domain**: Contains pure business logic without framework dependencies.
- **Application**: Coordinates use cases and business rules.
- **Adapters**: Handles HTTP requests and connects them to the application layer.

This separation ensures that business logic remains independent from the web framework and can be extended in future iterations.

---

## Running the Python Backend

From the repository root:

```
cd backend/python
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The server runs at:

http://127.0.0.1:8000

---

## Project Structure

backend/  
&nbsp;&nbsp;go/          # Golang backend  
&nbsp;&nbsp;python/      # Django backend  
frontend/      # React (TypeScript)  

---

This project will be progressively expanded in upcoming weeks to build a functional Inventory Management System.
---

## Table of Contents

1. [Getting Started with Git & Forking](#getting-started-with-git-and-forking)
2. [Prerequisites & where to find them](#prerequisites--where-to-find-them)
3. [Setting up & running](#setting-up--running)
4. [Development Workflow](#development-workflow)
   - [Pushing Your First Change](#pushing-your-first-change)
5. [Making your first change](#making-your-first-change)
6. [Running Tests](#running-tests)
7. [Frontend Setup](#frontend-setup)
8. [Further Reading](#further-reading)

---

## Getting Started with Git and Forking

### 1. Setting up Git and the Repo

1. **Install Git** (if not already):
   - **macOS**: [Homebrew](https://brew.sh/) users can run `brew install git`.
   - **Windows**: Use [Git for Windows](https://gitforwindows.org/).
   - **Linux**: Install via your distro's package manager, e.g., `sudo apt-get install git` (Ubuntu/Debian).

2. **Configure Git** with your name and email:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com" # Use the same email you shared during onboarding
   ```

3. **What is Forking?**

   Forking a repository on GitHub creates your own copy under your GitHub account, where you can make changes independently without affecting the original repo. Later, you can make pull requests to merge changes back if needed.

4. Fork the Rippling/interneers-lab repository (ensure you're in the correct org or your personal GitHub account, as directed).
5. **Clone** your forked repo:
   ```bash
   git clone git@github.com:<YourUsername>/interneers-lab.git
   cd interneers-lab
   ```

## Prerequisites & where to find them

Prerequisites (Python, Go, Node, Docker, etc.) and how to verify your setup are documented in each part of the repo:

- **[backend/python/README.md](backend/python/README.md)** — Python/Django, virtualenv, MongoDB
- **[backend/go/README.md](backend/go/README.md)** — Go, MongoDB
- **[frontend/README.md](frontend/README.md)** — Node, Yarn, React

Use the README for the part you're working on.

---

## Setting up & running

Setup and run instructions live in the domain READMEs:

- **Python backend:** [backend/python/README.md](backend/python/README.md) — venv, dependencies, `runserver`, Docker Compose for MongoDB
- **Go backend:** [backend/go/README.md](backend/go/README.md) — `make setup`, `make build-and-run`, Docker Compose
- **Frontend:** [frontend/README.md](frontend/README.md)

---

## Development Workflow

### Making your first change

Step-by-step tutorials live in the domain READMEs:

- **[backend/python/README.md](backend/python/README.md)** — Django starters (e.g. Hello World, Hello {name} API)
- **[backend/go/README.md](backend/go/README.md)** — Go hello-world and APIs
- **[frontend/README.md](frontend/README.md)** — React hello-world and APIs

### Pushing Your First Change

1. **Stage and commit**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```
2. **Push to your forked repo (main branch by default):**
   ```bash
   git push origin main
   ```

---

## Running Tests

See the domain READMEs for how to run tests in each stack:

- [backend/python/README.md](backend/python/README.md)
- [backend/go/README.md](backend/go/README.md)
- [frontend/README.md](frontend/README.md)

---

## Further Reading

Each domain has detailed README with links to relevant docs. In general:

- **Django:** [docs.djangoproject.com](https://docs.djangoproject.com/)
- **React:** [react.dev](https://react.dev/learn)
- **Go:** [go.dev/doc](https://go.dev/doc/)
- **MongoDB:** [docs.mongodb.com](https://docs.mongodb.com/)
- **Docker Compose:** [docs.docker.com/compose](https://docs.docker.com/compose/)
