# ⚙️ MediConnect Backend (FastAPI)

Backend service for MediConnect, handling authentication, appointment management, doctor-patient interactions, and system workflows.

---

## 🚀 Features

### 🔐 Authentication
- User login system (extendable to JWT)
- Role-based access (Patient, Doctor, Admin)

---

### 📅 Appointment Management
- Book, reschedule, cancel appointments
- Track appointment status
- Doctor approval/rejection flow

---

### 👨‍⚕️ Doctor Operations
- Fetch daily schedules
- Access patient history
- Upload reports
- Assign medicines

---

### 🧑 Patient Operations
- Search doctors
- View appointments & reports
- Track health metrics
- View prescriptions

---

### 🛠️ Admin Controls
- Manage users
- Add/remove doctors
- Monitor system activity

---

## 🧱 Tech Stack

- FastAPI (Python)
- NeonDB (PostgreSQL)
- SQLAlchemy / ORM
- Pydantic (validation)

---

## 🔄 Automation (n8n Integration)

- Appointment reminders
- Report-ready notifications
- Event-based triggers via API/webhooks

---

## 📂 Project Structure

```id="3y1n0f"
mediconnect-backend/
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── admin_routes.py
│   ├── agent.py
│   ├── auth.py
│   ├── database.py
│   ├── doctor_routes.py
│   ├── doctor.py
│   ├── firebase_auth.py
│   ├── main.py
│   ├── models.py
│   ├── patient.py
│   └── schemas.py
├── README.md
├── requirements.txt
└── seed.py

```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash id="c6s5vd"
git clone <repo-url>
cd mediconnect-frontend
```

---

### 2️⃣ Configure Backend URL

Update API base URL in:

```js id="3u0xgm"
js/config.js
```

Example:

```js id="a9o3m2"
const API_BASE = "http://localhost:8000";
```

---

### 3️⃣ Run Frontend

Simply open:

```bash id="1p1l3s"
index.html
```

Or use **Live Server** in VS Code.

---

## ⚡ API Design

- RESTful architecture
- Modular route handling
- Scalable service layer

---

## 📌 Future Improvements

- JWT Authentication
- Role-based middleware
- WebSocket notifications
- Rate limiting & security enhancements

---

## ▶️ Run Locally

```bash
uvicorn main:app --reload


## 🔄 Application Flow

1. User logs in → `index.html`
2. Redirect to → `dashboard.html`
3. Navigate via sidebar:

   * Search doctors
   * Book appointment
   * View bookings
   * Profile
4. API calls handled via `config.js`

---


## 🎯 Design Principles

* Clean dashboard UI
* Modular CSS per screen
* Feature-based JS structure
* Separation of concerns
* Backend-agnostic frontend

---

## 🌟 Future Enhancements

* React / Next.js migration
* Mobile responsive design
* Dark mode
* AI chatbot UI
* Push notifications

---

## 📌 Author

**Sarthak Singh**

---

## 📜 License

MIT License

Copyright (c) 2026 Sarthak Singh

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

---
