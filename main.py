from fastapi import FastAPI
from app.database import Base, engine

from app.routes import patient, doctor

app = FastAPI(title="🏥 AI Hospital Appointment System")

# Create tables automatically
Base.metadata.create_all(bind=engine)

# Include APIs
app.include_router(patient.router)
app.include_router(doctor.router)


@app.get("/")
def home():
    return {"status": "Hospital Backend Running Successfully 🚀"}
