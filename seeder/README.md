# Database Seeder

Run the following command to seed the database with mock data:

```bash
docker-compose --profile seed build seeder && docker-compose --profile seed run --rm seeder
```

All in one command to reset the database with mock data:

```bash
docker compose down db -v && docker compose up db -d && docker-compose --profile seed build seeder && docker-compose --profile seed run --rm seeder
```
