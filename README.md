# 🏥 MediConnect Backend – AI Hospital Appointment System

## 📌 Overview

MediConnect Backend is a **FastAPI-based REST API** powering an AI-assisted hospital appointment system. It handles authentication, doctor discovery, appointment management, report tracking, and automation triggers for patient communication.

The backend is designed as a **scalable, modular service** that acts as the **central source of truth** for all application data.

---

## 🚀 Features

### 🔐 Authentication

* User registration and login
* Token-based authentication
* Role support (Patient / Doctor)

### 👤 Patient Features

* Search doctors
* View doctor availability
* Book appointments
* Reschedule appointments
* Cancel appointments
* View personal appointments

### 🧑‍⚕️ Doctor Features

* Set availability schedules
* Mark reports as ready

### 🤖 Automation Integration

* Fetch tomorrow’s appointments for reminders
* Trigger external automation agents (n8n-ready)
* Event-driven architecture for notifications

---

## 🏗️ Tech Stack

* **Framework:** FastAPI
* **Language:** Python
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Validation:** Pydantic
* **API Docs:** OpenAPI (Swagger UI)

---

## 📂 Project Structure

```
mediconnect-backend/
├── app/
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── database.py        # DB connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── auth.py            # Authentication logic
│   ├── doctor.py          # Doctor APIs
│   ├── patient.py         # Patient APIs
│   ├── agent.py           # Automation endpoints
│
├── requirements.txt
├── seed.py                # Seed data script
└── .gitignore
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone <repo-url>
cd mediconnect-backend
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Database

Update your database connection in `app/database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/hospital"
```

---

### 4️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

---

### 5️⃣ Access API Docs

Open in browser:

```
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

### 🔐 Auth

```
POST /auth/register     # Register user
POST /auth/login        # Login user
```

---

### 👤 Patient APIs

```
GET  /doctors                          # Get doctors
GET  /doctors/{doctor_id}/availability # Get availability

POST /appointments/book                # Book appointment
PUT  /appointments/reschedule          # Reschedule appointment
PUT  /appointments/cancel/{appointment_id}  # Cancel appointment

GET  /appointments/my/{patient_id}     # Get user appointments
GET  /appointments/tomorrow            # Get tomorrow appointments
```

---

### 🧑‍⚕️ Doctor APIs

```
POST /availability/set           # Set doctor availability
POST /reports/set-ready-date     # Mark report ready
GET  /doctors/all                # Get all doctors (admin/doctor)
```

---

### 🤖 Agent APIs

```
GET /appointments/tomorrow
```

Used by automation tools (n8n) for sending reminders.

---

## 📦 Schemas

Key request/response models:

* `UserRegister`
* `UserLogin`
* `TokenResponse`
* `AppointmentCreate`
* `AppointmentReschedule`
* `AvailabilitySet`
* `ReportReady`

All schemas are defined in:

```
app/schemas.py
```

---

## 🔄 Core Workflows

### 📅 Appointment Booking

1. User logs in
2. Fetch doctors
3. Select doctor & availability
4. Book appointment
5. Stored in database
6. Available for automation triggers

---

### 🔁 Appointment Management

* Reschedule appointments
* Cancel appointments
* Track appointment status

---

### 📢 Automation Flow

1. Fetch tomorrow’s appointments
2. Send to automation agent (n8n)
3. Trigger reminders / notifications

---

## 🧪 Seed Data

Run seed script:

```bash
python seed.py
```

This will populate:

* Sample doctors
* Initial data for testing

---

## 🧩 Design Principles

* Modular architecture
* Separation of concerns
* RESTful API design
* Event-driven integration ready
* Scalable and extensible

---

## 🔥 API Request / Response Examples

### 1. Register User

**Request**

```json
POST /auth/register
{
  "name": "Sarthak Singh",
  "email": "sarthak@example.com",
  "password": "password123",
  "role": "PATIENT"
}
```

**Response**

```json
{
  "message": "User registered successfully"
}
```

---

### 2. Login

**Request**

```json
POST /auth/login
{
  "email": "sarthak@example.com",
  "password": "password123"
}
```

**Response**

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

---

### 3. Get Doctors

```http
GET /doctors
```

**Response**

```json
[
  {
    "id": 1,
    "name": "Dr. Rahul Sharma",
    "specialization": "Cardiology"
  }
]
```

---

### 4. Book Appointment

**Request**

```json
POST /appointments/book
{
  "patient_id": 1,
  "doctor_id": 2,
  "date_time": "2026-03-25T10:00:00"
}
```

**Response**

```json
{
  "message": "Appointment booked successfully",
  "appointment_id": 101
}
```

---

### 5. Reschedule Appointment

```json
PUT /appointments/reschedule
{
  "appointment_id": 101,
  "new_time": "2026-03-26T11:00:00"
}
```

---

## 🧪 Postman Collection (Import Ready)

```json
{
  "info": {
    "name": "MediConnect API",
    "_postman_id": "12345",
    "description": "Hospital Appointment APIs",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Register",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/register",
        "body": {
          "mode": "raw",
          "raw": "{\"name\":\"Test\",\"email\":\"test@test.com\",\"password\":\"123456\",\"role\":\"PATIENT\"}"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/login"
      }
    },
    {
      "name": "Get Doctors",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/doctors"
      }
    },
    {
      "name": "Book Appointment",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/appointments/book"
      }
    }
  ]
}
```

## 📈 Architecture Diagram

```text
            ┌────────────────────┐
            │   Frontend (UI)    │
            │ HTML / CSS / JS    │
            └─────────┬──────────┘
                      │ REST API
                      ▼
            ┌────────────────────┐
            │   FastAPI Backend  │
            │  Auth + Logic + DB │
            └─────────┬──────────┘
                      │
          ┌───────────┴────────────┐
          ▼                        ▼
 ┌───────────────┐        ┌────────────────┐
 │ PostgreSQL DB │        │   n8n Agent    │
 │ Appointments  │        │ Automation/AI  │
 └───────────────┘        └────────────────┘
                                   │
                                   ▼
                          Notifications (SMS/Email)
```

---




## 🚧 Future Improvements


* Personalized dashboard
* Medicine Tracker
* Dockerfile for FastAPI backend
* Docker Compose setup with PostgreSQL
* One-command local environment setup
* AI assistant 
* JWT refresh tokens
* Role-based access control (RBAC)
* Rate limiting


---

## 📜 License

MIT License

Copyright (c) 2026 Sarthak Singh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE

---

## 👤 Author

**Sarthak Singh**

---

## 🏁 Summary

MediConnect Backend provides a robust, scalable API layer for a modern hospital appointment system. It integrates seamlessly with frontend applications and automation agents, enabling intelligent healthcare workflows.

---
