from datetime import datetime
import os
import random
import time
from decimal import Decimal
from typing import Optional, cast
from faker import Faker
import mysql.connector

fake = Faker()

# seed for consistent mock data
Faker.seed(1)
random.seed(1)

USER_ROWS = 50
GROUP_ROWS = 10
GROUP_MEMBER_ROWS = 150
BILL_ROWS = 60
BILL_ASSIGNMENT_ROWS = 180


def generate_mock_users(count: int = USER_ROWS):
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


def generate_mock_groups(user_ids: list, count: int = GROUP_ROWS):
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


def generate_mock_group_memberships(
    user_ids: list[int],
    group_ids_and_leaders: list[tuple[int, int]],
    count: int = GROUP_MEMBER_ROWS,
):
    memberships: set[tuple[int, int]] = set()

    # Participation constraint: every group has members and includes the leader.
    for group_id, group_leader in group_ids_and_leaders:
        group_size = random.randint(3, min(8, len(user_ids)))
        other_users = [uid for uid in user_ids if uid != group_leader]
        chosen_users = random.sample(other_users, k=max(0, group_size - 1))

        memberships.add((group_leader, group_id))
        for member_id in chosen_users:
            memberships.add((member_id, group_id))

    # Top up to target bridge-table volume.
    group_ids = [row[0] for row in group_ids_and_leaders]
    max_possible = len(user_ids) * len(group_ids)
    target = min(count, max_possible)
    while len(memberships) < target:
        memberships.add((random.choice(user_ids), random.choice(group_ids)))

    return list(memberships)


def _build_group_to_members(memberships: list[tuple[int, int]]) -> dict[int, list[int]]:
    group_to_members: dict[int, list[int]] = {}
    for user_id, group_id in memberships:
        group_to_members.setdefault(group_id, []).append(user_id)
    return group_to_members


def generate_mock_bills(group_to_members: dict[int, list[int]], count: int = BILL_ROWS):
    group_ids = list(group_to_members.keys())
    bills = []

    # Ensure each group has at least one bill if count allows.
    for group_id in group_ids[: min(len(group_ids), count)]:
        creator = random.choice(group_to_members[group_id])
        created_at = fake.date_time_between(start_date="-240d", end_date="now")
        bills.append(
            (
                group_id,
                Decimal(f"{random.uniform(40.0, 2000.0):.2f}"),
                fake.date_time_between(start_date=created_at, end_date="+120d"),
                fake.sentence(nb_words=4).rstrip("."),
                creator,
                created_at,
            )
        )

    while len(bills) < count:
        group_id = random.choice(group_ids)
        creator = random.choice(group_to_members[group_id])
        created_at = fake.date_time_between(start_date="-240d", end_date="now")
        bills.append(
            (
                group_id,
                Decimal(f"{random.uniform(40.0, 2000.0):.2f}"),
                fake.date_time_between(start_date=created_at, end_date="+120d"),
                fake.sentence(nb_words=4).rstrip("."),
                creator,
                created_at,
            )
        )

    return bills


def _split_percentages(n: int) -> list[Decimal]:
    # Produce n positive values that sum to exactly 1.000.
    cuts = sorted(random.sample(range(1, 1000), n - 1))
    parts = (
        [cuts[0]]
        + [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))]
        + [1000 - cuts[-1]]
    )
    return [Decimal(p) / Decimal(1000) for p in parts]


def generate_mock_bill_assignments(
    bill_rows: list[tuple[int, int]],
    group_to_members: dict[int, list[int]],
    count: int = BILL_ASSIGNMENT_ROWS,
):
    used_pairs: set[tuple[int, int]] = set()
    assignments: list[tuple[int, int, Decimal, Optional[datetime]]] = []

    for bill_id, group_id in bill_rows:
        members = group_to_members[group_id]
        assignees = random.sample(members, k=random.randint(2, min(6, len(members))))
        for user_id, split in zip(assignees, _split_percentages(len(assignees))):
            used_pairs.add((bill_id, user_id))
            paid_at = (
                fake.date_time_between(start_date="-60d", end_date="now")
                if random.random() < 0.55
                else None
            )
            assignments.append((bill_id, user_id, split, paid_at))

    attempts = 0
    while len(assignments) < count and attempts < 10000:
        attempts += 1
        bill_id, group_id = random.choice(bill_rows)
        user_id = random.choice(group_to_members[group_id])
        if (bill_id, user_id) in used_pairs:
            continue
        used_pairs.add((bill_id, user_id))
        assignments.append((bill_id, user_id, Decimal("1.000"), None))

    return assignments


def seed_db():
    print("Connecting to the database...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", "3306")),
    )
    cursor = conn.cursor()

    # --- Users ---
    users = generate_mock_users()
    users_query = """
        INSERT INTO users (first_name, last_name, email, is_admin, is_analyst, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(users_query, users)
    conn.commit()
    cursor.execute("SELECT user_id FROM users")
    user_ids: list[int] = [cast(int, tuple(row)[0]) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(user_ids)} users")

    # --- Groups ---
    groups = generate_mock_groups(user_ids)
    groups_query = """
        INSERT INTO `groups` (group_leader, name, address, city, state, zip_code)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(groups_query, groups)
    conn.commit()
    cursor.execute("SELECT group_id, group_leader FROM `groups`")
    group_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(group_rows)} groups")

    # --- Group Members ---
    group_memberships = generate_mock_group_memberships(user_ids, group_rows)
    group_memberships_query = """
        INSERT INTO group_members (user_id, group_id)
        VALUES (%s, %s)
    """
    cursor.executemany(group_memberships_query, group_memberships)
    conn.commit()
    print(f"  ✔ Seeded {len(group_memberships)} group memberships")

    # --- Bills ---
    group_to_members = _build_group_to_members(group_memberships)
    bills = generate_mock_bills(group_to_members)
    bills_query = """
        INSERT INTO bills (group_id, total_cost, due_at, title, created_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(bills_query, bills)
    conn.commit()
    cursor.execute("SELECT bill_id, group_id FROM bills")
    bill_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(bill_rows)} bills")

    # --- Bill Assignments ---
    assignments = generate_mock_bill_assignments(bill_rows, group_to_members)
    assignments_query = """
        INSERT INTO bill_assignments (bill_id, user_id, split_percentage, paid_at)
        VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(assignments_query, assignments)
    conn.commit()
    print(f"  ✔ Seeded {len(assignments)} bill assignments")

    cursor.close()
    conn.close()
    print("Database seeding complete!")


if __name__ == "__main__":
    sleep_time = 7
    print(f"Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)
    seed_db()
