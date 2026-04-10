from typing import List
from faker import Faker
from flask import Flask

from backend.repositories.user_repository import UserRepository

fake = Faker()
Faker.seed(42)


def init_mocks(app: Flask) -> None:
    with app.app_context():
        # determine if we need to init mocks
        user_repository = UserRepository()
        users = generate_mock_users()
        user_repository.insert_users(users)


def generate_mock_users(count: int = 50) -> List[dict]:
    users = []
    for i in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}.{i + 1}@{fake.free_email_domain()}"
        users.append(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "created_at": fake.past_datetime(),
                "is_admin": False,
                "is_analyst": False,
            }
        )
    return users
