# GreenDesk — IT Asset Management API

A REST API for managing and controlling technical equipment inventory (Laptops, Monitors, Peripherals). It allows you to register assets, assign them to users, manage loans, and maintain a complete audit history with JSONB.

---

## Technologies

| Technology | Version | Usage |
|---|---|---|
| FastAPI | 0.115.8 | Main API framework |
| SQLAlchemy | 2.0.36 | Modern typed ORM |
| PostgreSQL | 15 | Relational database |
| Alembic | 1.14.0 | Database migrations |
| Pydantic v2 | 2.10.3 | Data validation and schemas |
| Docker + Compose | — | Containerization |
| pytest + httpx | 8.3.3 + 0.28.1 | Async testing with HTTP client |

---

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [Make](https://www.gnu.org/software/make/)
- **Windows users:** [WSL 2 with Ubuntu](https://docs.microsoft.com/en-us/windows/wsl/install) (recommended optional)

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd greendesk
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your values:

```env
DB_USER=admin
DB_PASSWORD=admin123
DB_NAME=greendesk_db
DB_HOST=db
DB_PORT=5432
PGADMIN_EMAIL=admin@admin.com
PGADMIN_PASSWORD=admin
```

For testing, configure the `.env.test`:

```env
DB_USER=admin
DB_PASSWORD=admin123
DB_NAME=greendesk_test
DB_HOST=db_test
DB_PORT=5432
```

### 3. Start the Environment

```bash
make dev
```

This builds the images, starts the containers in the background, and displays the available URLs. Migrations are applied automatically when starting thanks to `start.sh`.

---

## Available Commands

Run `make help` to see all commands. The most commonly used are:

```bash
make dev          # Start the complete development environment
make dev-down     # Stop the containers
make logs         # Show app logs in real time
make migrate      # Apply Alembic migrations manually
make test         # Run tests in an isolated environment
make test-clean   # Clean test containers and images
```

---

## Project Architecture

```
greendesk/
├── app/
│   ├── api/
│   │   ├── main.py              # FastAPI instance and middlewares
│   │   └── routes/
│   │       ├── devices.py       # Device endpoints
│   │       ├── users.py         # User endpoints
│   │       └── generic.py       # Generic endpoint by model
│   ├── db/
│   │   └── database.py          # SQLAlchemy connection and get_db
│   ├── models/                  # ORM models (SQLAlchemy)
│   │   ├── device.py
│   │   ├── user.py
│   │   └── audit_log.py
│   ├── repositories/            # Data access layer
│   │   ├── device_repository.py
│   │   ├── user_repository.py
│   │   └── audit_log_repository.py
│   ├── schemas/                 # Pydantic DTOs (input/output)
│   │   ├── device.py
│   │   ├── user.py
│   │   └── audit_log.py
│   └── services/                # Business logic
│       ├── device_service.py
│       ├── user_service.py
│       └── audit_log_service.py
├── alembic/                     # Database migrations
│   └── versions/
├── tests/
│   ├── conftest.py              # Global fixtures (DB, HTTP client)
│   └── api/
│       ├── test_devices.py
│       └── test_user.py
├── docker-compose.yml           # Development environment
├── docker-compose.test.yml      # Isolated testing environment
├── Dockerfile
├── Makefile
├── start.sh                     # Container startup script
├── pytest.ini
└── requirements.txt
```

### Layered Architecture Pattern

The project follows a strict layered architecture. HTTP requests reach the **routes**, which delegate to the **services** for business logic, which in turn use the **repositories** to access the database. Pydantic **schemas** validate input and output, and SQLAlchemy **models** define the database structure.

---

## API Reference

Interactive documentation (Swagger UI) is available at:

```
http://localhost:8000/docs
```

### Devices

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/devices/` | List all devices. Optional filters: `?category=Laptop&status=available` |
| `POST` | `/devices/` | Register a new device |
| `GET` | `/devices/{id}` | Get a device by ID |
| `PATCH` | `/devices/{id}/loan/{user_id}` | Assign a device to a user. Param: `?days=7` |
| `PATCH` | `/devices/{id}/return` | Mark a device as returned |
| `GET` | `/devices/{id}/history` | Device audit history |

**Example — Create device:**

```bash
curl -X POST http://localhost:8000/devices/ \
  -H "Content-Type: application/json" \
  -d '{"serial_number": "SN-001", "model": "Dell Latitude", "category": "Laptop"}'
```

**Possible device states:** `available`, `loaned`

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/` | List all users |
| `POST` | `/users/` | Create a new user |
| `GET` | `/users/{id}` | Get a user by ID |

**Example — Create user:**

```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jdoe", "full_name": "John Doe"}'
```

### Generic

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/generic/{model}/{id}` | Get any entity by model and ID |
| `GET` | `/generic/{model}` | List all entities of a model |

Available models: `devices`, `users`, `logs`

---

## Database

### Models

**User**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Unique identifier |
| username | String(50) unique | Username |
| full_name | String(100) | Full name |

**Device**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Unique identifier |
| serial_number | String(50) unique | Serial number |
| model | String(100) | Device model |
| category | String(50) | Category (Laptop, Monitor, etc.) |
| status | String | Current status |
| specs | JSONB | Technical specifications |
| return_date | DateTime | Expected return date |
| owner_id | FK → users.id | Assigned user |

**AuditLog**

| Field | Type | Description |
|---|---|---|
| id | Integer PK | Unique identifier |
| target_model | String(50) | Affected model (Device, User...) |
| target_id | Integer | ID of affected record |
| action | String(20) | Action performed (create, return...) |
| changes | JSONB | State before/after change |
| created_at | DateTime | Event timestamp |

### Migrations with Alembic

```bash
# Create a new migration
make shell
alembic revision --autogenerate -m "description_of_change"

# Apply migrations
make migrate

# Revert last migration
alembic downgrade -1
```

---

## Testing

Tests run in a completely isolated environment with their own in-memory PostgreSQL database (tmpfs), which is destroyed when finished.

```bash
make test
```

This starts `docker-compose.test.yml`, runs pytest with coverage, and cleans up everything when finished. The coverage report is generated in `htmlcov/`.

### How Tests Are Organized

```
tests/
├── conftest.py          # Fixtures: DB, rollback session, async HTTP client
└── api/
    ├── test_devices.py  # Device endpoints tests
    └── test_user.py     # User endpoints tests
```

Each test works within a transaction that is rolled back when finished, ensuring tests are independent of each other.

---

## Database Administration

pgAdmin 4 is available to inspect and manage the database:

- **URL:** http://localhost:5050
- **Email and password:** defined in the `.env`

To connect to the database from pgAdmin, use `db` as the host (container name) and the credentials from `.env`.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DB_USER` | PostgreSQL user | `admin` |
| `DB_PASSWORD` | PostgreSQL password | `admin123` |
| `DB_NAME` | Database name | `greendesk_db` |
| `DB_HOST` | Database host (container name) | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `PGADMIN_EMAIL` | pgAdmin login email | `admin@admin.com` |
| `PGADMIN_PASSWORD` | pgAdmin password | `admin` |

> ⚠️ Never upload the `.env` file to the repository. It is included in `.gitignore`.

---

## Docker Infrastructure

The project uses two compose files to separate environments:

**`docker-compose.yml` (development)** starts three services: `db` (PostgreSQL with healthcheck), `app` (FastAPI with hot-reload via `start.sh`), and `pgadmin`. The app waits for the database to be ready before starting and applies migrations automatically.

**`docker-compose.test.yml` (testing)** starts an ephemeral in-memory database (`tmpfs`) on port 5433 to avoid interfering with development, and a container that runs pytest. When finished, everything is destroyed with `down -v`.