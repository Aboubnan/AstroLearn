# tests/test_db_connexion.py
from model.database import get_db_connection, get_all_categories


def test_database():
    conn = get_db_connection()
    assert conn is not None, "Impossible de joindre la base de données."
    try:
        categories = get_all_categories()
        assert categories is not None
    finally:
        conn.close()


if __name__ == "__main__":
    test_database()
