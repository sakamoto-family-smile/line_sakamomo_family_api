from datetime import datetime

import firebase_admin
import google.cloud.firestore
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter


def get_db_client_with_default_credentials() -> google.cloud.firestore.Client:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


def register_todo(
    db: google.cloud.firestore.Client,
    collection_id: str,
    document_id: str,
    target_date: datetime,
    todo_text: str,
):
    data = {"date": target_date, "todo": todo_text}
    db.collection(collection_id).document(document_id).set(data, merge=True)


def get_todo_list(db: google.cloud.firestore.Client, collection_id: str, target_date: datetime, family_id: str):
    collections = (
        db.collection(collection_id)
        .where(filter=FieldFilter("family_id", "==", family_id))
        .where(filter=FieldFilter("date", "==", target_date))
        .stream()
    )
    return collections
