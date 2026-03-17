from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


def save_document(document: dict) -> None:
    """Insère un document dans MongoDB."""
    collection.insert_one(document)


def get_all_documents() -> list[dict]:
    """Retourne tous les documents sans le champ interne _id de MongoDB."""
    return list(collection.find({}, {"_id": 0}))


def get_document_by_id(doc_id: str) -> dict | None:
    """Retourne un document par son doc_id."""
    return collection.find_one({"doc_id": doc_id}, {"_id": 0})
