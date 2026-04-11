import os
import random
import time
from decimal import Decimal
from faker import Faker
import mysql.connector

fake = Faker()

# seed for consistent mock data
Faker.seed(1)
random.seed(1)

GROUP_MEMBERS_COUNT = 150
BILLS_COUNT = 60
BILL_ASSIGNMENTS_COUNT = 180


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


def generate_mock_group_memberships(
    user_ids: list[int],
    group_rows: list[tuple[int, int]],
    count: int = GROUP_MEMBERS_COUNT,
):
    memberships: set[tuple[int, int]] = set()

    # Participation constraint: every group has members and includes the leader.
    for group_id, group_leader in group_rows:
        group_size = random.randint(3, min(8, len(user_ids)))
        other_users = [uid for uid in user_ids if uid != group_leader]
        chosen_users = random.sample(other_users, k=max(0, group_size - 1))

        memberships.add((group_leader, group_id))
        for member_id in chosen_users:
            memberships.add((member_id, group_id))

    # Top up to target bridge-table volume.
    group_ids = [row[0] for row in group_rows]
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


def generate_mock_bills(group_to_members: dict[int, list[int]], count: int = BILLS_COUNT):
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
    parts = [cuts[0]] + [cuts[i] - cuts[i - 1] for i in range(1, len(cuts))] + [1000 - cuts[-1]]
    return [Decimal(p) / Decimal(1000) for p in parts]


def generate_mock_bill_assignments(
    bill_rows: list[tuple[int, int]],
    group_to_members: dict[int, list[int]],
    count: int = BILL_ASSIGNMENTS_COUNT,
):
    assignments_map: dict[int, list[tuple[int, int, Decimal, object]]] = {}
    used_pairs: set[tuple[int, int]] = set()

    for bill_id, group_id in bill_rows:
        members = group_to_members[group_id]
        assignee_count = random.randint(2, min(6, len(members)))
        assignees = random.sample(members, k=assignee_count)
        splits = _split_percentages(assignee_count)

        bill_rows_list: list[tuple[int, int, Decimal, object]] = []
        for user_id, split in zip(assignees, splits):
            used_pairs.add((bill_id, user_id))
            paid_at = fake.date_time_between(start_date="-60d", end_date="now") if random.random() < 0.55 else None
            bill_rows_list.append((bill_id, user_id, split, paid_at))
        assignments_map[bill_id] = bill_rows_list

    # Top up unique assignments to meet volume target, then normalize each bill.
    bill_to_group = {bill_id: group_id for bill_id, group_id in bill_rows}
    flat_count = sum(len(v) for v in assignments_map.values())
    attempts = 0
    while flat_count < count and attempts < 10000:
        attempts += 1
        bill_id = random.choice(list(bill_to_group.keys()))
        group_id = bill_to_group[bill_id]
        user_id = random.choice(group_to_members[group_id])
        key = (bill_id, user_id)
        if key in used_pairs:
            continue

        used_pairs.add(key)
        assignments_map.setdefault(bill_id, []).append((bill_id, user_id, Decimal("1.000"), None))
        flat_count += 1

    normalized_rows: list[tuple[int, int, Decimal, object]] = []
    for bill_id, rows in assignments_map.items():
        splits = _split_percentages(len(rows))
        for row, split in zip(rows, splits):
            normalized_rows.append((bill_id, row[1], split, row[3]))

    return normalized_rows


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

    # Rerun-safe reset in FK order.
    cursor.execute("DELETE FROM bill_assignments")
    cursor.execute("DELETE FROM bills")
    cursor.execute("DELETE FROM group_members")
    cursor.execute("DELETE FROM `groups`")
    cursor.execute("DELETE FROM users")
    conn.commit()

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
    cursor.execute("SELECT group_id, group_leader FROM `groups`")
    group_rows = cursor.fetchall()
    print(f"  ✔ Seeded {len(group_rows)} groups")

    # --- Group Members ---
    group_memberships = generate_mock_group_memberships(user_ids, group_rows, count=GROUP_MEMBERS_COUNT)
    cursor.executemany(
        """
        INSERT INTO group_members (user_id, group_id)
        VALUES (%s, %s)
    """,
        group_memberships,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(group_memberships)} group memberships")

    # --- Bills ---
    group_to_members = _build_group_to_members(group_memberships)
    bills = generate_mock_bills(group_to_members, count=BILLS_COUNT)
    cursor.executemany(
        """
        INSERT INTO bills (group_id, total_cost, due_at, title, created_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        bills,
    )
    conn.commit()
    cursor.execute("SELECT bill_id, group_id FROM bills")
    bill_rows = cursor.fetchall()
    print(f"  ✔ Seeded {len(bill_rows)} bills")

    # --- Bill Assignments ---
    assignments = generate_mock_bill_assignments(bill_rows, group_to_members, count=BILL_ASSIGNMENTS_COUNT)
    cursor.executemany(
        """
        INSERT INTO bill_assignments (bill_id, user_id, split_percentage, paid_at)
        VALUES (%s, %s, %s, %s)
    """,
        assignments,
    )
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
