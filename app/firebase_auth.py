import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Initialize Firebase Admin ───────────────────────────
# Uses GOOGLE_APPLICATION_CREDENTIALS env variable
# or service account JSON

_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if not _firebase_initialized:
        try:
            # Use service account from environment variable
            import json
            service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if service_account:
                cred_dict = json.loads(service_account)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
            else:
                # Fallback for local development
                firebase_admin.initialize_app()
            _firebase_initialized = True
        except Exception as e:
            print(f"Firebase init error: {e}")


def verify_firebase_token(id_token: str) -> dict:
    """
    Verifies a Firebase ID token and returns the decoded token.
    Raises HTTPException if token is invalid.
    """
    init_firebase()
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )