from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import Base, engine
from app import patient, doctor, auth

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="🏥 MediConnect API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mediconnect-frontend-seav.onrender.com",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
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
    return {"status": "MediConnect Backend Running Successfully 🚀"}



@app.middleware("http")
async def rate_limit_login(request: Request, call_next):
    return await call_next(request)