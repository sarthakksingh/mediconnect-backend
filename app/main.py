from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import patient, doctor
from app import auth

app = FastAPI(title="🏥 AI Hospital Appointment System")

# ✅ CORS — allows your frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

# ✅ Include all routers
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(doctor.router)


@app.get("/")
def home():
    return {"status": "Hospital Backend Running Successfully 🚀"}