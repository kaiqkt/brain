---
title: "Docker"
tags: [tools, docker]
created: 2026-06-15
updated: 2026-06-15
---

# Docker

## Container Management

```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers, networks and volumes
docker rm -f $(docker ps -a -q) && docker network prune -f && docker volume prune -f

# Remove dangling volumes
docker volume rm $(docker volume ls -qf dangling=true)
```

## Compose

```bash
# Bring down and remove volumes
docker compose down -v
```

## Build

```bash
# Spring Boot — build image
./gradlew bootBuildImage --imageName=yourusername/yourimagename:tag
```

## Execute Commands Inside Container

**Step 1 — find container:**

```bash
docker ps
```

**Step 2 — enter container:**

```bash
docker exec -it <container_id_or_name> bash
# Alpine / distroless fallback
docker exec -it <container_id_or_name> sh
```

**Step 3 — delete data (per database):**

PostgreSQL:

```sql
-- Connect
psql -U <user> -d <database>

-- Delete rows
DELETE FROM <table>;

-- Truncate (faster, resets sequences)
TRUNCATE TABLE <table> RESTART IDENTITY CASCADE;
```

MySQL / MariaDB:

```sql
-- Connect
mysql -u <user> -p<password> <database>

-- Delete rows
DELETE FROM <table>;

-- Truncate
TRUNCATE TABLE <table>;
```

MongoDB:

```js
// Connect
mongosh -u <user> -p <password> --authenticationDatabase admin

// Delete all documents
use <database>
db.<collection>.deleteMany({})

// Drop collection
db.<collection>.drop()
```

**Exit:**

```bash
exit
```
