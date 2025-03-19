import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app import app
from models import User
from routes.user import Register

client = TestClient(app)

class TestUserRegister(unittest.TestCase):

    @patch('your_module.SessionLocal')
    @patch('your_module.hashed_password')
    @patch('your_module.create_access_token')
    @patch('your_module.create_refresh_token')
    def test_user_register_success(self, mock_create_refresh_token, mock_create_access_token, mock_hashed_password, mock_session):
        """Тест успешной регистрации пользователя."""
        # Настройка
        mock_user = Register(
            login="testuser",
            password="strongpassword",
            email="test@example.com"
        )

        # Имитация поведения базы данных
        mock_session.return_value.query.return_value.filter.return_value.first.return_value = None  # Нет существующего пользователя
        mock_hashed_password.return_value = "hashedpassword"
        mock_create_access_token.return_value = "access_token"
        mock_create_refresh_token.return_value = "refresh_token"

        # Выполнение запроса
        response = client.post("/register", json=mock_user.dict())

        # Проверка результата
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "user": "testuser",
            "access_token": "access_token",
            "refresh_token": "refresh_token"
        })

    @patch('your_module.SessionLocal')
    def test_user_register_existing_user(self, mock_session):
        """Тест регистрации с уже существующим логином или email."""
        # Настройка
        mock_user = Register(
            login="testuser",
            password="strongpassword",
            email="test@example.com"
        )

        # Имитация поведения базы данных
        existing_user = User(login="testuser", email="test@example.com")
        mock_session.return_value.query.return_value.filter.return_value.first.return_value = existing_user  # Пользователь уже существует

        # Выполнение запроса
        response = client.post("/register", json=mock_user.dict())

        # Проверка результата
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Такой логин или email уже существует!"})

    @patch('your_module.SessionLocal')
    def test_user_register_server_error(self, mock_session):
        """Тест обработки ошибки сервера."""
        # Настройка
        mock_user = Register(
            login="testuser",
            password="strongpassword",
            email="test@example.com"
        )

        # Имитация поведения базы данных
        mock_session.return_value.query.return_value.filter.return_value.first.side_effect = Exception("Database error")  # Исключение при запросе

        # Выполнение запроса
        response = client.post("/register", json=mock_user.dict())

        # Проверка результата
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Произошла ошибка на сервере"})

if __name__ == '__main__':
    unittest.main()