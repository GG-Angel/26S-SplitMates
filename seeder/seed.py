import os
import time
from faker import Faker
import mysql.connector

fake = Faker()
Faker.seed(42)


def generate_mock_users(count: int = 50):
    return [
        (
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            False,  # is_admin
            False,  # is_analyst
            fake.past_datetime(),  # created_at
        )
        for _ in range(count)
    ]


def seed_db():
    print("Connecting to the database...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
    )
    cursor = conn.cursor()

    users = generate_mock_users()
    query = """
        INSERT INTO users (first_name, last_name, email, is_admin, is_analyst, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    print(f"Inserting {len(users)} mock users...")
    cursor.executemany(query, users)
    conn.commit()

    cursor.close()
    conn.close()
    print("Database seeding complete!")


if __name__ == "__main__":
    seed_db()
