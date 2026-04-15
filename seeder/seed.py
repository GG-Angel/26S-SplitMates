import os
import random
import time
from datetime import timedelta
from decimal import Decimal
from typing import Callable, cast

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
SUPPORT_TICKETS_COUNT = 15
USER_REPORTS_COUNT = 20
BANS_COUNT = 12
APP_VERSIONS_COUNT = 8
AUDIT_LOGS_COUNT = 40

# aliases for template naming
GROUP_MEMBERS_COUNT = GROUP_MEMBER_ROWS
BILLS_COUNT = BILL_ROWS
BILL_ASSIGNMENTS_COUNT = BILL_ASSIGNMENT_ROWS

def generate_mock_users(count: int = USER_ROWS):
    rows = []
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        is_admin = False
        is_analyst = False
        account_status = "active"
        password_hash = "mock_hash"
        created_at = fake.past_datetime("-90d")

        user = (
            first_name,
            last_name,
            email,
            is_admin,
            is_analyst,
            account_status,
            password_hash,
            created_at,
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
            print(f"Database not ready yet (attempt {attempt}/{max_attempts}). Retrying in {delay} seconds...")
            time.sleep(delay)
            delay = min(delay * 2, 5)

    raise last_error if last_error is not None else RuntimeError("Unable to connect to the database")


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


def generate_mock_support_tickets(user_ids: list[int], count: int = SUPPORT_TICKETS_COUNT):
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
            fake.date_time_between(start_date=created_at, end_date="now") if status == "closed" else None
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


def generate_mock_bans(user_ids: list[int], admin_ids: list[int], count: int = BANS_COUNT):
    rows = []
    eligible_users = [uid for uid in user_ids if uid not in admin_ids]
    for _ in range(min(count, len(eligible_users))):
        user_id = random.choice(eligible_users)
        eligible_users.remove(user_id)
        issued_at = fake.date_time_between(start_date="-60d", end_date="now")
        maybe_expires = random.random() < 0.65
        expires_at = fake.date_time_between(start_date=issued_at, end_date="+30d") if maybe_expires else None
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
        deployed_at = fake.date_time_between(start_date="-120d", end_date="now") if status != "staged" else None
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
    target_tables = ["users", "groups", "support_tickets", "user_reports", "bans", "app_versions"]
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


def seed_db():
    print("Connecting to the database...")
    conn = connect_with_retry()
    cursor = conn.cursor()

    # Rerun-safe reset in FK order.
    cursor.execute("DELETE FROM audit_logs")
    cursor.execute("DELETE FROM app_versions")
    cursor.execute("DELETE FROM user_reports")
    cursor.execute("DELETE FROM support_tickets")
    cursor.execute("DELETE FROM bans")
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
        INSERT INTO users (first_name, last_name, email, is_admin, is_analyst, account_status, password_hash, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """,
        users,
    )
    conn.commit()
    cursor.execute("SELECT user_id FROM users")
    user_ids: list[int] = [cast(int, tuple(row)[0]) for row in cursor.fetchall()]
    cursor.execute("SELECT user_id FROM users WHERE is_admin = TRUE")
    admin_ids: list[int] = [cast(int, tuple(row)[0]) for row in cursor.fetchall()]
    if not admin_ids:
        admin_ids = user_ids[:1]
    print(f"  ✔ Seeded {len(user_ids)} users")

    # --- Sysadmin Data ---
    support_tickets = generate_mock_support_tickets(user_ids)
    support_tickets_query = """
        INSERT INTO support_tickets (
            submitted_by,
            status,
            priority,
            description,
            assigned_to,
            title,
            created_at,
            resolved_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(support_tickets_query, support_tickets)
    conn.commit()
    print(f"  ✔ Seeded {len(support_tickets)} support tickets")

    user_reports = generate_mock_user_reports(user_ids)
    user_reports_query = """
        INSERT INTO user_reports (
            reported_user,
            reported_by,
            reason,
            status,
            reviewed_by,
            reviewed_at,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(user_reports_query, user_reports)
    conn.commit()
    print(f"  ✔ Seeded {len(user_reports)} user reports")

    bans = generate_mock_bans(user_ids, admin_ids)
    bans_query = """
        INSERT INTO bans (
            user_id,
            issued_by,
            reasons,
            expires_at,
            issued_at
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(bans_query, bans)
    conn.commit()
    print(f"  ✔ Seeded {len(bans)} bans")

    app_versions = generate_mock_app_versions(admin_ids)
    app_versions_query = """
        INSERT INTO app_versions (
            version_number,
            deployed_by,
            status,
            release_notes,
            deployed_at
        )
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(app_versions_query, app_versions)
    conn.commit()
    print(f"  ✔ Seeded {len(app_versions)} app versions")

    audit_logs = generate_mock_audit_logs(user_ids)
    audit_logs_query = """
        INSERT INTO audit_logs (
            user_id,
            details,
            target_table,
            target_id,
            action_type,
            performed_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(audit_logs_query, audit_logs)
    conn.commit()
    print(f"  ✔ Seeded {len(audit_logs)} audit logs")

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

    # --- Support Tickets ---
    support_tickets = generate_mock_support_tickets(user_ids, count=SUPPORT_TICKETS_COUNT)
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

    cursor.close()
    conn.close()
    print("Database seeding complete!")


if __name__ == "__main__":
    seed_db()

# TODO: add invitations mocks
