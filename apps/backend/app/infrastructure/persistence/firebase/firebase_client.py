"""
Firebase client singleton for Firestore access
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional
import os
from app.config import get_settings


class FirebaseClient:
    """Singleton Firebase client"""
    _instance: Optional['FirebaseClient'] = None
    _db: Optional[firestore.Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            settings = get_settings()
            
            # Try multiple paths for the service account file
            possible_paths = [
                # Current working directory
                settings.firebase_credentials_path,
                # Backend directory
                os.path.join('apps', 'backend', settings.firebase_credentials_path),
                # Relative to this file
                os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                    settings.firebase_credentials_path
                ),
                # Root directory
                os.path.join('..', '..', settings.firebase_credentials_path)
            ]
            
            cred_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    cred_path = path
                    break
            
            if cred_path is None:
                print(f"⚠️ Firebase service account file not found. Tried paths:")
                for path in possible_paths:
                    print(f"  - {os.path.abspath(path)}")
                print("Running without Firebase - repository will use mock data")
                return
            
            try:
                # Initialize Firebase Admin
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print(f"✅ Firebase initialized successfully from: {cred_path}")
            except Exception as e:
                print(f"⚠️ Failed to initialize Firebase: {e}")
                print("Running without Firebase - repository will use mock data")
                return
        
        # Get Firestore client
        try:
            self._db = firestore.client()
            print("✅ Firestore client created successfully")
        except Exception as e:
            print(f"⚠️ Failed to create Firestore client: {e}")
    
    def collection(self, name: str):
        """Get collection reference"""
        if self._db is None:
            raise RuntimeError("Firestore client not initialized")
        return self._db.collection(name)
    
    @property
    def is_available(self) -> bool:
        """Check if Firebase is available"""
        return self._db is not None


# Global instance
firebase_client = FirebaseClient()