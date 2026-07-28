# tests/test_csrf.py
import re

from app import app


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "Aucun token CSRF trouvé dans la page."
    return match.group(1)


def test_login_form_contains_csrf_token():
    with app.test_client() as client:
        response = client.get("/connexion")
        html = response.get_data(as_text=True)

        _extract_csrf_token(html)


def test_login_post_without_csrf_token_is_rejected():
    with app.test_client() as client:
        response = client.post(
            "/connexion", data={"pseudo": "test", "password": "test"}
        )

        assert response.status_code == 400


def test_login_post_with_csrf_token_is_not_rejected_by_csrf():
    with app.test_client() as client:
        html = client.get("/connexion").get_data(as_text=True)
        token = _extract_csrf_token(html)

        response = client.post(
            "/connexion",
            data={"pseudo": "test", "password": "test", "csrf_token": token},
        )

        # Le CSRF ne doit pas être la cause d'un éventuel échec : plus de 400.
        assert response.status_code != 400


def test_chatbot_api_without_csrf_header_is_rejected():
    with app.test_client() as client:
        response = client.post("/api/chatbot", json={"message": "Salut"})

        assert response.status_code == 400
