import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.cloud.firestore


def get_db_client_with_default_credentials() -> google.cloud.firestore.Client:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
