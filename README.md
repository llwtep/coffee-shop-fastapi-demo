# ☕ Coffee Shop API — User Management Module

This project implements the **User Management** block for the Coffee Shop API.  
It includes authentication, registration, email verification, role-based access control, and background cleanup tasks.

---

## 🚀 Tech Stack

- **FastAPI** — Web framework  
- **SQLAlchemy (async)** — ORM for PostgreSQL  
- **Alembic** — Database migrations  
- **JWT (JSON Web Tokens)** — Authentication  
- **Celery + Redis** — Background tasks (user cleanup, email sending)  
- **Docker / Docker Compose** — Containerized deployment

---

## 📁 Project Structure

app/  
├── api/  
│ ├── init.py  
│ ├── auth.py # Authentication & authorization endpoints  
│ ├── router.py # Main API router  
│ ├── users.py # User management endpoints  
│  
├── core/  
│ ├── init.py  
│ ├── config.py # Environment variables and settings  
│ ├── security.py # JWT creation and password hashing  
│  
├── db/  
│ ├── init.py  
│ ├── database.py # Async SQLAlchemy database connection  
│ ├── User.py # SQLAlchemy User model  
│  
├── schemas/  
│ ├── init.py  
│ ├── UserSchema.py # Pydantic schemas for user requests/responses  
│  
├── services/  
│ ├── init.py  
│ ├── UserService.py # Business logic for users  
│  
├── utils/  
│ ├── email_verification.py # Email verification utilities  
│  
├── workers/   
│ ├── init.py    
│ ├── celery_app.py # Celery initialization    
│ ├── tasks/       
│  ├── init.py        
│  ├── user_cleanup.py # Task for cleaning unverified users       
│      
migrations/ # Alembic migration directory    
Dockerfile # Docker build configuration     
docker-compose.yaml # Docker Compose configuration    
.env # Environment variables file    
main.py # FastAPI entry point   
---

## ⚙️ Environment Variables (`.env`)

You must create a `.env` file in the project root with the following content:  
**DB_USER=**  
**DB_PASSWORD=**  
**DB_HOST=**  
**DB_PORT=**  
**DB_NAME=**  
**JWT_SECRET_KEY=**  
**EMAIL=**  
**PASS=**  

> 📝 Note: `EMAIL` and `PASS` are used for sending verification emails.

---

## 🗄️ Database Setup and Alembic Migrations

This project **does not create a database inside Docker** —  
you must connect to your **own external PostgreSQL database**.

Before starting the application in Docker, apply the Alembic migrations manually:

```bash
# Apply migrations to your database
alembic upgrade head
```
Make sure your .env file contains correct PostgreSQL connection credentials.


---
## 🐳 Docker Instructions
1️⃣ Build Docker Image
```bash
docker build -t coffee-shop-api .
```

2️⃣ Run with Docker Compose
```bash
docker-compose up --build
```

3️⃣ Access the API Docs

Once the container is running, open:
http://localhost:8000/docs

This will open Swagger UI with interactive OpenAPI documentation.

---
## 📬 Email Verification

When a new user registers, a verification email is sent.  
The link in the email will call the `/auth/verify` endpoint, marking the user as verified.

---

## 🧱 Summary

| Component | Description |
|------------|-------------|
| **FastAPI** | Main API and endpoints |
| **SQLAlchemy** | ORM models and database operations |
| **JWT Auth** | Secure authentication using tokens |
| **Celery** | Background cleanup and email tasks |
| **Alembic** | Migration tool for managing DB schema |
| **Swagger UI** | Built-in interactive API documentation |

---
## 💡 Tip:
If you're running on Windows, ensure Docker Desktop is installed and running before using Docker Compose.
