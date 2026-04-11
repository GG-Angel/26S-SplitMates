# Database Seeder

Run the following command to seed the database with mock data:

```bash
docker-compose --profile seed build seeder && docker-compose --profile seed run --rm seeder
```

All in one command to reset the database with mock data:

```bash
docker compose down db -v && docker compose up db -d && docker-compose --profile seed build seeder && docker-compose --profile seed run --rm seeder
```

## Repeatable workflow (recommended)

1. Recreate the DB container/volume so schema SQL is re-applied.
2. Run the seeder profile.
3. Verify row counts in DataGrip (or MySQL CLI) before demo/testing.

This keeps generated data deterministic because Faker and Python `random` are seeded in `seeder/seed.py`.

## Expected row counts after seeding

- `users`: 50
- `groups`: 10
- `group_members`: 150
- `bills`: 60
- `bill_assignments`: at least 180 (can be higher depending on assignment generation)

## Quick verification queries

```sql
SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS groups_count FROM `groups`;
SELECT COUNT(*) AS group_members_count FROM group_members;
SELECT COUNT(*) AS bills_count FROM bills;
SELECT COUNT(*) AS bill_assignments_count FROM bill_assignments;
```
