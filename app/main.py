from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import patient, doctor
from app import auth

app = FastAPI(title="🏥 AI Hospital Appointment System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mediconnect-frontend-seav.onrender.com",
        "http://localhost:3000",  # for local development
        "http://localhost:5500",  # for VS Code Live Server
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(doctor.router)


@app.get("/")
def home():
    return {"status": "Hospital Backend Running Successfully 🚀"}