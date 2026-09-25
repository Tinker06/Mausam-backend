import os

import firebase_admin
from firebase_admin import credentials, firestore


# Find the project root folder
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# Path to Firebase service-account JSON
SERVICE_ACCOUNT_PATH = os.path.join(
    BASE_DIR,
    "firebase-service-account.json"
)

# Initialize Firebase
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)

firebase_admin.initialize_app(cred)

# Connect to Firestore
db = firestore.client()