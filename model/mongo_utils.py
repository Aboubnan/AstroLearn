# model/mongo_utils.py

from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from config import MONGO_URI, MONGO_DB_NAME

_client: Optional[MongoClient] = None


def get_mongo_client() -> MongoClient:
    """Retourne un client MongoDB réutilisé entre les appels (connexion paresseuse)."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_commentaires_collection() -> Collection:
    """Collection MongoDB stockant, pour chaque objet céleste, l'arbre de commentaires."""
    return get_mongo_client()[MONGO_DB_NAME]["commentaires"]
