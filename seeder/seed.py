import os
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Optional, cast

from faker import Faker
import mysql.connector
from mysql.connector import Error as MySQLError

fake = Faker()

# seed for consistent mock data
Faker.seed(1)
random.seed(1)

USER_ROWS = 50
GROUP_ROWS = 10
GROUP_MEMBER_ROWS = 150
BILL_ROWS = 60
BILL_ASSIGNMENT_ROWS = 180
CHORE_ROWS = 120
CHORE_ASSIGNMENT_ROWS = 80
EVENT_ROWS = 32
ITEM_ROWS = 40
ITEM_OWNER_ROWS = 60
SUPPORT_TICKETS_COUNT = 15
USER_REPORTS_COUNT = 20
BANS_COUNT = 12
APP_VERSIONS_COUNT = 8
AUDIT_LOGS_COUNT = 40


def generate_picture_url():
    # kitty :3
    sizes = [200, 225, 250, 275, 300]
    width, height = random.choice(sizes), random.choice(sizes)
    return f"https://placekittens.com/{width}/{height}"


HOUSEHOLD_ITEMS = [
    "Vacuum Cleaner",
    "Coffee Maker",
    "Couch",
    "TV",
    "Dining Table",
    "Microwave",
    "Toaster",
    "Blender",
    "Air Fryer",
    "Rice Cooker",
    "Bookshelf",
    "Desk Lamp",
    "Gaming Console",
    "Printer",
    "Router",
    "Bed Frame",
    "Dresser",
    "Mirror",
    "Rug",
    "Standing Fan",
    "Humidifier",
    "Space Heater",
    "Mini Fridge",
    "Kettle",
    "Iron",
    "Mop",
    "Broom",
    "Trash Can",
    "Paper Shredder",
    "Surge Protector",
]

# aliases for template naming
GROUP_MEMBERS_COUNT = GROUP_MEMBER_ROWS
BILLS_COUNT = BILL_ROWS
BILL_ASSIGNMENTS_COUNT = BILL_ASSIGNMENT_ROWS


def generate_mock_users(count: int = USER_ROWS):
    rows = []
    for idx in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        is_admin = False
        is_analyst = False
        created_at = fake.past_datetime("-90d")
        picture_url = generate_picture_url() if random.random() < 0.6 else None

        if idx == 0:
            first_name = "Bob"
            last_name = "McDonald"
            is_admin = True
        elif idx in (1, 2):
            is_admin = True
        elif idx in (3, 4, 5):
            is_analyst = True

        user = (
            first_name,
            last_name,
            email,
            is_admin,
            is_analyst,
            "active",
            fake.sha256(raw_output=False),
            created_at,
            picture_url,
        )
        rows.append(user)
    return rows


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


def connect_with_retry(max_attempts: int = 15, initial_delay: int = 2):
    last_error: Exception | None = None
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("MYSQL_ROOT_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=int(os.getenv("DB_PORT", "3306")),
            )
        except MySQLError as exc:
            last_error = exc
            if attempt == max_attempts:
                break
            print(
                f"Database not ready yet (attempt {attempt}/{max_attempts}). Retrying in {delay} seconds..."
            )
            time.sleep(delay)
            delay = min(delay * 2, 5)

    raise (
        last_error
        if last_error is not None
        else RuntimeError("Unable to connect to the database")
    )


def generate_mock_bills(
    group_to_members: dict[int, list[int]], count: int = BILLS_COUNT
):
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
            paid_at = (
                fake.date_time_between(start_date="-60d", end_date="now")
                if random.random() < 0.55
                else None
            )
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
        assignments_map.setdefault(bill_id, []).append(
            (bill_id, user_id, Decimal("1.000"), None)
        )
        flat_count += 1

    normalized_rows: list[tuple[int, int, Decimal, Optional[datetime]]] = []
    for bill_id, rows in assignments_map.items():
        splits = _split_percentages(len(rows))
        for row, split in zip(rows, splits):
            normalized_rows.append(
                (bill_id, row[1], split, cast(Optional[datetime], row[3]))
            )

    return normalized_rows


def generate_mock_chore_assignments(
    chore_and_group_ids: list[tuple[int, int]],
    group_to_members: dict[int, list[int]],
    count: int = CHORE_ASSIGNMENT_ROWS,
):
    assignments: set[tuple[int, int]] = set()
    i = 0

    while len(assignments) < count:
        chore_id, group_id = chore_and_group_ids[i]
        members = group_to_members[group_id]

        # pick k users from the group to assign this chore to
        assignees = random.sample(members, k=random.randint(1, min(3, len(members))))

        for assignee in assignees:
            assignment = (chore_id, assignee)
            # ensure assignments are unique
            if assignment not in assignments:
                assignments.add(assignment)
                if len(assignments) >= count:
                    break

        # cycle back to the start if we reach the last chore
        i = (i + 1) % len(chore_and_group_ids)

    return list(assignments)


def generate_mock_title() -> str:
    return fake.sentence(nb_words=4).rstrip(".")


def generate_mock_bill(group_id: int, group_members: list[int]):
    title = generate_mock_title()
    total_cost = Decimal(f"{random.uniform(40.0, 2000.0):.2f}")
    created_at = fake.past_datetime("-60d")
    due_at = fake.date_time_between(start_date=created_at, end_date="+14d")
    created_by = random.choice(group_members)
    return (group_id, title, total_cost, due_at, created_by, created_at)


def generate_mock_chore(group_id: int, group_members: list[int]):
    title = generate_mock_title()
    effort = random.choice(["low", "medium", "high"])
    created_by = random.choice(group_members)
    created_at = fake.date_time_between(start_date="-240d", end_date="now")
    due_at = fake.date_time_between(start_date=created_at, end_date="+14d")
    completed_at = random.choice(
        [None, fake.date_time_between(start_date=created_at, end_date="now")]
    )
    return (group_id, title, effort, created_by, created_at, due_at, completed_at)


def generate_mock_event(group_id: int, group_members: list[int]):
    title = generate_mock_title()
    starts_at = fake.future_datetime()
    ends_at = starts_at + timedelta(hours=random.randint(1, 8))
    is_private = fake.boolean(chance_of_getting_true=75)
    created_by = random.choice(group_members)
    created_at = fake.past_datetime("-7d")
    return (group_id, title, starts_at, ends_at, is_private, created_by, created_at)


def generate_mock_support_tickets(
    user_ids: list[int], count: int = SUPPORT_TICKETS_COUNT
):
    statuses = ["open", "in_progress", "closed"]
    priorities = ["low", "medium", "high"]
    ticket_templates = [
        (
            "Payment split looks incorrect",
            "Bill total appears right, but my split percentage is wrong after a roommate left the group.",
        ),
        (
            "Cannot submit chore completion",
            "When I mark a chore as completed, the page refreshes but status stays pending.",
        ),
        (
            "Group invitation expired too early",
            "My roommate's invite link says expired even though it was created today.",
        ),
        (
            "Event not visible to household",
            "I created an event for the group calendar, but other members cannot see it.",
        ),
        (
            "Duplicate charge on monthly bill",
            "The same utility bill appears twice and doubles what members owe.",
        ),
        (
            "Account suspended by mistake",
            "My account was suspended and I cannot access shared bills or chores.",
        ),
        (
            "Notification settings not saving",
            "I disable email notifications, but they are enabled again after refresh.",
        ),
    ]

    rows = []
    for _ in range(count):
        submitted_by = random.choice(user_ids)
        assigned_to = random.choice(user_ids)
        status = random.choices(statuses, weights=[0.45, 0.35, 0.20], k=1)[0]
        created_at = fake.date_time_between(start_date="-90d", end_date="now")
        resolved_at = (
            fake.date_time_between(start_date=created_at, end_date="now")
            if status == "closed"
            else None
        )
        title, description_template = random.choice(ticket_templates)

        rows.append(
            (
                submitted_by,
                status,
                random.choice(priorities),
                f"{description_template} (Ticket submitted by user #{submitted_by})",
                assigned_to,
                title,
                created_at,
                resolved_at,
            )
        )
    return rows


def generate_mock_user_reports(user_ids: list[int], count: int = USER_REPORTS_COUNT):
    statuses = ["pending", "under_review", "resolved", "dismissed"]
    rows = []

    for _ in range(count):
        reported_user = random.choice(user_ids)
        reported_by = random.choice([uid for uid in user_ids if uid != reported_user])
        reviewed_by = random.choice(user_ids)
        status = random.choices(statuses, weights=[0.35, 0.30, 0.25, 0.10], k=1)[0]
        created_at = fake.date_time_between(start_date="-90d", end_date="now")
        reviewed_at = (
            fake.date_time_between(start_date=created_at, end_date="now")
            if status in ("under_review", "resolved", "dismissed")
            else None
        )

        rows.append(
            (
                reported_user,
                reported_by,
                fake.sentence(nb_words=10),
                status,
                reviewed_by,
                reviewed_at,
                created_at,
            )
        )
    return rows


def generate_mock_bans(
    user_ids: list[int], admin_ids: list[int], count: int = BANS_COUNT
):
    rows = []
    eligible_users = [uid for uid in user_ids if uid not in admin_ids]
    for _ in range(min(count, len(eligible_users))):
        user_id = random.choice(eligible_users)
        eligible_users.remove(user_id)
        issued_at = fake.date_time_between(start_date="-60d", end_date="now")
        maybe_expires = random.random() < 0.65
        expires_at = (
            fake.date_time_between(start_date=issued_at, end_date="+30d")
            if maybe_expires
            else None
        )
        rows.append(
            (
                user_id,
                random.choice(admin_ids),
                random.choice(
                    [
                        "Harassment in shared group chat",
                        "Repeated policy violations after warnings",
                        "Fraudulent payment dispute activity",
                        "Abusive behavior reported by multiple users",
                    ]
                ),
                expires_at,
                issued_at,
            )
        )
    return rows


def generate_mock_app_versions(admin_ids: list[int], count: int = APP_VERSIONS_COUNT):
    rows = []
    status_values = ["deployed", "staged", "rolled_back", "deprecated"]
    for version in range(1, count + 1):
        status = random.choices(status_values, weights=[0.65, 0.15, 0.10, 0.10], k=1)[0]
        deployed_at = (
            fake.date_time_between(start_date="-120d", end_date="now")
            if status != "staged"
            else None
        )
        rows.append(
            (
                version,
                random.choice(admin_ids),
                status,
                "\n".join(
                    [
                        f"Version {version} summary:",
                        "- Improved moderation workflow and admin controls",
                        "- Updated dashboard cards and filtering behavior",
                        "- Added bug fixes and minor UX polish",
                    ]
                ),
                deployed_at,
            )
        )
    return rows


def generate_mock_audit_logs(user_ids: list[int], count: int = AUDIT_LOGS_COUNT):
    target_tables = [
        "users",
        "groups",
        "support_tickets",
        "user_reports",
        "bans",
        "app_versions",
    ]
    action_types = ["create", "update", "delete"]

    rows = []
    for _ in range(count):
        target_table = random.choice(target_tables)
        action_type = random.choice(action_types)
        target_id = random.randint(1, 250)
        details = random.choice(
            [
                f"{action_type.title()} performed on {target_table} record #{target_id}",
                f"Admin moderation action: {action_type} {target_table} #{target_id}",
                f"System admin updated {target_table} configuration #{target_id}",
                f"Operational change logged for {target_table} #{target_id}",
            ]
        )

        rows.append(
            (
                random.choice(user_ids),
                details,
                target_table,
                target_id,
                action_type,
                fake.date_time_between(start_date="-90d", end_date="now"),
            )
        )
    return rows


def generate_mock_item(group_id: int, group_members: list[int]):
    name = random.choice(HOUSEHOLD_ITEMS)
    picture_url = generate_picture_url() if random.random() < 0.8 else None
    created_by = random.choice(group_members)
    return (group_id, name, picture_url, created_by)


def generate_mock_item_owners(
    item_and_group_ids: list[tuple[int, int]],
    group_to_members: dict[int, list[int]],
    count: int = ITEM_OWNER_ROWS,
):
    owners: set[tuple[int, int]] = set()

    for item_id, group_id in item_and_group_ids:
        members = group_to_members[group_id]
        owners.add((item_id, random.choice(members)))

    attempts = 0
    while len(owners) < count and attempts < 10000:
        attempts += 1
        item_id, group_id = random.choice(item_and_group_ids)
        user_id = random.choice(group_to_members[group_id])
        owners.add((item_id, user_id))

    return list(owners)


def generate_group_items(
    generator: Callable[[int, list[int]], tuple],
    group_to_members: dict[int, list[int]],
    count: int,
) -> list[tuple]:
    group_ids = list(group_to_members.keys())
    items = []
    i = 0

    while len(items) < count:
        group_id = group_ids[i]
        group_members = group_to_members[group_id]
        item = generator(group_id, group_members)
        items.append(item)
        i = (i + 1) % len(group_ids)

    return items


def seed_db():
    print("Connecting to the database...")
    conn = connect_with_retry()
    cursor = conn.cursor()

    # Rerun-safe reset — TRUNCATE resets auto-increment so IDs start from 1.
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in [
        "audit_logs",
        "app_versions",
        "user_reports",
        "support_tickets",
        "bans",
        "item_owners",
        "items",
        "chore_assignments",
        "chores",
        "bill_assignments",
        "bills",
        "events",
        "group_members",
        "`groups`",
        "users",
    ]:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()

    # --- Users ---
    users = generate_mock_users()
    users_query = """
        INSERT INTO users (first_name, last_name, email, is_admin, is_analyst, account_status, password_hash, created_at, picture_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(users_query, users)
    conn.commit()
    cursor.execute("SELECT user_id FROM users")
    user_ids: list[int] = [cast(int, tuple(row)[0]) for row in cursor.fetchall()]
    cursor.execute("SELECT user_id FROM users WHERE is_admin = TRUE")
    admin_ids: list[int] = [cast(int, tuple(row)[0]) for row in cursor.fetchall()]
    if not admin_ids:
        admin_ids = user_ids[:1]
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
    group_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(group_rows)} groups")

    # --- Group Members ---
    group_memberships = generate_mock_group_memberships(
        user_ids, group_rows, count=GROUP_MEMBERS_COUNT
    )
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
    bill_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(bill_rows)} bills")

    # --- Bill Assignments ---
    assignments = generate_mock_bill_assignments(
        bill_rows, group_to_members, count=BILL_ASSIGNMENTS_COUNT
    )
    cursor.executemany(
        """
        INSERT INTO bill_assignments (bill_id, user_id, split_percentage, paid_at)
        VALUES (%s, %s, %s, %s)
    """,
        assignments,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(assignments)} bill assignments")

    # --- Chores ---
    chores = generate_group_items(generate_mock_chore, group_to_members, CHORE_ROWS)
    chores_query = """
        INSERT INTO chores (group_id, title, effort, created_by, created_at, due_at, completed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(chores_query, chores)
    conn.commit()
    cursor.execute("SELECT chore_id, group_id FROM chores")
    chore_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(chores)} chores")

    # --- Chore Assignments ---
    chore_assignments = generate_mock_chore_assignments(chore_rows, group_to_members)
    chore_assignments_query = """
        INSERT INTO chore_assignments (chore_id, user_id)
        VALUES (%s, %s)
    """
    cursor.executemany(chore_assignments_query, chore_assignments)
    conn.commit()
    print(f"  ✔ Seeded {len(chore_assignments)} chore assignments")

    # --- Events ---
    events = generate_group_items(generate_mock_event, group_to_members, EVENT_ROWS)
    events_query = """
        INSERT INTO events (group_id, title, starts_at, ends_at, is_private, created_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(events_query, events)
    conn.commit()
    print(f"  ✔ Seeded {len(events)} events")

    # --- Support Tickets ---
    support_tickets = generate_mock_support_tickets(
        user_ids, count=SUPPORT_TICKETS_COUNT
    )
    cursor.executemany(
        """
        INSERT INTO support_tickets (submitted_by, status, priority, description, assigned_to, title, created_at, resolved_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
        support_tickets,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(support_tickets)} support tickets")

    # --- User Reports ---
    user_reports = generate_mock_user_reports(user_ids, count=USER_REPORTS_COUNT)
    cursor.executemany(
        """
        INSERT INTO user_reports (reported_user, reported_by, reason, status, reviewed_by, reviewed_at, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
        user_reports,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(user_reports)} user reports")

    # --- Bans ---
    bans = generate_mock_bans(user_ids, admin_ids, count=BANS_COUNT)
    cursor.executemany(
        """
        INSERT INTO bans (user_id, issued_by, reasons, expires_at, issued_at)
        VALUES (%s, %s, %s, %s, %s)
    """,
        bans,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(bans)} bans")

    # Keep account status consistent with active bans.
    cursor.execute(
        """
        UPDATE users u
        SET account_status = 'suspended'
        WHERE EXISTS (
            SELECT 1
            FROM bans b
            WHERE b.user_id = u.user_id
              AND (b.expires_at IS NULL OR b.expires_at > NOW())
        )
    """
    )
    conn.commit()

    # --- App Versions ---
    app_versions = generate_mock_app_versions(admin_ids, count=APP_VERSIONS_COUNT)
    cursor.executemany(
        """
        INSERT INTO app_versions (version_number, deployed_by, status, release_notes, deployed_at)
        VALUES (%s, %s, %s, %s, %s)
    """,
        app_versions,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(app_versions)} app versions")

    # --- Audit Logs ---
    audit_logs = generate_mock_audit_logs(user_ids, count=AUDIT_LOGS_COUNT)
    cursor.executemany(
        """
        INSERT INTO audit_logs (user_id, details, target_table, target_id, action_type, performed_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        audit_logs,
    )
    conn.commit()
    print(f"  ✔ Seeded {len(audit_logs)} audit logs")

    # --- Items ---
    items = generate_group_items(generate_mock_item, group_to_members, ITEM_ROWS)
    items_query = """
        INSERT INTO items (group_id, name, picture_url, created_by)
        VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(items_query, items)
    conn.commit()
    cursor.execute("SELECT item_id, group_id FROM items")
    item_rows = [cast(tuple[int, int], row) for row in cursor.fetchall()]
    print(f"  ✔ Seeded {len(item_rows)} items")

    # --- Item Owners ---
    item_owners = generate_mock_item_owners(item_rows, group_to_members)
    item_owners_query = """
        INSERT INTO item_owners (item_id, user_id)
        VALUES (%s, %s)
    """
    cursor.executemany(item_owners_query, item_owners)
    conn.commit()
    print(f"  ✔ Seeded {len(item_owners)} item owners")

    cursor.close()
    conn.close()
    print("Database seeding complete!")


if __name__ == "__main__":
    seed_db()
