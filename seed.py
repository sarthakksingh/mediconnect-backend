

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, Doctor, Appointment
from app.auth import hash_password
from datetime import datetime, timedelta

# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def clear_existing():
    print("🗑️  Clearing existing data...")
    db.query(Appointment).delete()
    db.query(Doctor).delete()
    db.query(User).delete()
    db.commit()

def seed_users():
    print("👤 Seeding users...")
    users = [
        User(
            name="Sarthak Singh",
            email="sarthak@example.com",
            phone="+91 98765 43210",
            hashed_password=hash_password("password123"),
            role="PATIENT"
        ),
        User(
            name="Anushka Pathak",
            email="anushka@example.com",
            phone="+91 91234 56789",
            hashed_password=hash_password("password123"),
            role="PATIENT"
        ),
        User(
            name="Admin User",
            email="admin@hospital.com",
            phone="+91 99999 00000",
            hashed_password=hash_password("admin123"),
            role="ADMIN"
        ),
    ]
    db.add_all(users)
    db.commit()
    print(f"   ✅ {len(users)} users created")
    return users

def seed_doctors():
    print("👨‍⚕️ Seeding doctors...")
    doctors = [
        Doctor(
            name="Rahul Sharma",
            specialization="Cardiology",
            experience_years=12,
            patients_count=320,
            availability={
                "monday":    "10:00 AM, 10:30 AM, 11:00 AM, 11:30 AM",
                "wednesday": "10:00 AM, 10:30 AM, 11:00 AM, 11:30 AM",
                "friday":    "10:00 AM, 10:30 AM, 11:00 AM, 11:30 AM"
            }
        ),
        Doctor(
            name="Neha Mehta",
            specialization="Dermatology",
            experience_years=8,
            patients_count=210,
            availability={
                "tuesday":  "02:00 PM, 02:30 PM, 03:00 PM, 03:30 PM",
                "thursday": "02:00 PM, 02:30 PM, 03:00 PM, 03:30 PM"
            }
        ),
        Doctor(
            name="Arjun Kapoor",
            specialization="Orthopedics",
            experience_years=15,
            patients_count=450,
            availability={
                "monday":    "09:00 AM, 09:30 AM, 10:00 AM",
                "tuesday":   "09:00 AM, 09:30 AM, 10:00 AM",
                "thursday":  "09:00 AM, 09:30 AM, 10:00 AM",
                "saturday":  "09:00 AM, 09:30 AM, 10:00 AM"
            }
        ),
        Doctor(
            name="Priya Nair",
            specialization="Neurology",
            experience_years=10,
            patients_count=180,
            availability={
                "wednesday": "11:00 AM, 11:30 AM, 12:00 PM",
                "friday":    "11:00 AM, 11:30 AM, 12:00 PM"
            }
        ),
        Doctor(
            name="Vikram Desai",
            specialization="Pediatrics",
            experience_years=6,
            patients_count=290,
            availability={
                "monday":    "03:00 PM, 03:30 PM, 04:00 PM, 04:30 PM",
                "wednesday": "03:00 PM, 03:30 PM, 04:00 PM, 04:30 PM",
                "friday":    "03:00 PM, 03:30 PM, 04:00 PM, 04:30 PM"
            }
        ),
        Doctor(
            name="Sunita Rao",
            specialization="General Medicine",
            experience_years=20,
            patients_count=600,
            availability={
                "monday":    "08:00 AM, 08:30 AM, 09:00 AM, 09:30 AM",
                "tuesday":   "08:00 AM, 08:30 AM, 09:00 AM, 09:30 AM",
                "wednesday": "08:00 AM, 08:30 AM, 09:00 AM, 09:30 AM",
                "thursday":  "08:00 AM, 08:30 AM, 09:00 AM, 09:30 AM",
                "friday":    "08:00 AM, 08:30 AM, 09:00 AM, 09:30 AM"
            }
        ),
    ]
    db.add_all(doctors)
    db.commit()
    print(f"   ✅ {len(doctors)} doctors created")
    return doctors

def seed_appointments(users, doctors):
    print("📅 Seeding sample appointments...")
    patient = users[0]  # Sarthak

    appointments = [
        Appointment(
            patient_id=patient.id,
            doctor_id=doctors[0].id,  # Dr. Rahul Sharma
            date_time=datetime.now() + timedelta(days=1),
            reason="Chest pain checkup",
            status="booked"
        ),
        Appointment(
            patient_id=patient.id,
            doctor_id=doctors[2].id,  # Dr. Arjun Kapoor
            date_time=datetime.now() + timedelta(days=5),
            reason="Knee pain follow-up",
            status="booked"
        ),
        Appointment(
            patient_id=patient.id,
            doctor_id=doctors[5].id,  # Dr. Sunita Rao
            date_time=datetime.now() - timedelta(days=7),
            reason="General checkup",
            status="completed"
        ),
        Appointment(
            patient_id=patient.id,
            doctor_id=doctors[1].id,  # Dr. Neha Mehta
            date_time=datetime.now() - timedelta(days=14),
            reason="Skin rash",
            status="completed"
        ),
    ]
    db.add_all(appointments)
    db.commit()
    print(f"   ✅ {len(appointments)} appointments created")

def print_summary():
    print("\n" + "="*50)
    print("✅ DATABASE SEEDED SUCCESSFULLY")
    print("="*50)
    print("\n🔑 Test Login Credentials:")
    print("   Email:    sarthak@example.com")
    print("   Password: password123")
    print("\n   Email:    anushka@example.com")
    print("   Password: password123")
    print("\n   Email:    admin@hospital.com")
    print("   Password: admin123")
    print("\n📊 Data created:")
    print(f"   Users:        {db.query(User).count()}")
    print(f"   Doctors:      {db.query(Doctor).count()}")
    print(f"   Appointments: {db.query(Appointment).count()}")
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        clear_existing()
        users = seed_users()
        doctors = seed_doctors()
        seed_appointments(users, doctors)
        print_summary()
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()