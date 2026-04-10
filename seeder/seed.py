import os
import random
import time
from faker import Faker
import mysql.connector

fake = Faker()

# seed for consistent mock data
Faker.seed(1)
random.seed(1)


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


def generate_mock_groups(user_ids: list, count: int = 10):
    return [
        (
            random.choice(user_ids),  # group_leader
            fake.sentence(nb_words=3).rstrip("."),  # name
            fake.street_address(),  # address
            fake.city(),  # city
            fake.state_abbr(),  # state
            int(fake.zipcode()),  # zip_code
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

    # --- Users ---
    users = generate_mock_users(50)
    cursor.executemany(
        """
        INSERT INTO users (first_name, last_name, email, is_admin, is_analyst, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        users,
    )
    conn.commit()
    cursor.execute("SELECT user_id FROM users")
    user_ids = [tuple(row)[0] for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(user_ids)} users")

    # --- Groups ---
    groups = generate_mock_groups(user_ids, count=10)
    cursor.executemany(
        """
        INSERT INTO `groups` (group_leader, name, address, city, state, zip_code)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        groups,
    )
    conn.commit()
    cursor.execute("SELECT group_id FROM `groups`")
    group_ids = [tuple(row)[0] for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(group_ids)} groups")

    cursor.close()
    conn.close()
    print("Database seeding complete!")


if __name__ == "__main__":
    sleep_time = 7
    print(f"Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)
    seed_db()
