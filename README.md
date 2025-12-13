# GONSTERS Backend Assessment

Real-time machine data ingestion backend microservice built with **Flask**, **PostgreSQL**, and **InfluxDB**.

## About the Project

This is the solution for the **GONSTERS Back End Developer** Technical Assessment. The system is designed to handle sensor data from hundreds of industrial machines in real-time, focusing on performance, security, and scalability.

**Key Features Implemented:**
- **PostgreSQL** for machine metadata and user management.
- **InfluxDB** for storing time-series sensor data.
- **REST API** with generic JWT authentication, Role-Based Access Control (RBAC), and token blacklist (logout).
- **MQTT Subscriber** for data ingestion from brokers.
- **Redis Caching** for query optimization and token blacklisting.
- **Test Coverage** 75.69% with 87 passing test cases (75% threshold).
- **Docker Support** for both development and production environments.
- **CI/CD Pipeline** using GitHub Actions.

> **References:**
> - [Flask Documentation](https://flask.palletsprojects.com/)
> - [PostgreSQL Official Site](https://www.postgresql.org/)

## System Architecture

The system utilizes a microservice architecture with the following components:

1.  **MQTT Broker**: Receives data from industrial machines.
2.  **Flask Backend**: Subscribes to MQTT and exposes REST APIs.
3.  **PostgreSQL**: Stores machine metadata and user accounts.
4.  **InfluxDB**: Stores time-series data from sensors.
5.  **Redis**: Caching layer for query optimization.

**Data Flow:**
Industrial Machines publish data to the MQTT Broker -> Backend subscribes and writes to InfluxDB -> Clients query data via REST API (accelerated by Redis caching).

> **References:**
> - [MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
> - [InfluxDB Key Concepts](https://docs.influxdata.com/influxdb/v2/reference/key-concepts/)

## Database Schema

### PostgreSQL Tables

**`machine_metadata`** - Stores machine information:
-   `id` (UUID): Primary key.
-   `name` (VARCHAR): Machine name (e.g., "CNC-Machine-01").
-   `location` (VARCHAR): Physical location.
-   `sensor_type` (VARCHAR): Installed sensor type.
-   `status` (VARCHAR): Operational status (Active, Inactive, Maintenance, Error).
-   `created_at`, `updated_at` (TIMESTAMP): Audit trail.

**`users`** - Stores authentication and authorization data:
-   `id` (UUID): Primary key.
-   `username`, `email`: Login credentials.
-   `password_hash`: Bcrypt hashed password.
-   `role`: Operator, Supervisor, or Management.
-   `is_active`: Soft delete flag.
-   `factory_id`, `department`: Additional info.

*Indexes are applied to frequently queried columns (name, location, status) for performance optimization.*

### InfluxDB Measurement

**`sensor_readings`** structure:
-   **Tags** (Indexed): `machine_id`, `sensor_type`, `location`
-   **Fields**: `temperature`, `pressure`, `speed`
-   **Timestamp**: Nanosecond precision.

*Tags are used for filtering (indexed), while fields store the actual values.*

## Quick Start

### Prerequisites
-   Docker & Docker Compose
-   Python 3.11+
-   pip

### Setup and Installation

Use the provided `run.sh` script for easy setup:

```bash
# Clone repository
git clone https://github.com/username/gonsters-be-assessment.git
cd gonsters-be-assessment

# Make script executable
chmod +x scripts/run.sh

# Run development mode
# Automatically generates JWT keys, builds images, and starts services
./scripts/run.sh dev

# Optional: Install local dependencies for IDE autocomplete
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Once running, the API is accessible at `http://localhost:5000`.

Database migrations run automatically on container start. To run manually:
```bash
docker exec -i gonsters-postgres psql -U postgres -d gonsters_db < migrations/init_db.sql
docker exec -i gonsters-postgres psql -U postgres -d gonsters_db < migrations/create_users_table.sql
```

## API Endpoints

### Data Ingestion
-   **POST** `/api/v1/data/ingest` (Protected)
    -   Ingests batch sensor data from gateways. Supports multiple machines/readings per request. Requires `Authorization: Bearer <token>`.

### Machine Management
-   **POST** `/api/v1/data/machine` (Protected - Supervisor/Management)
    -   Adds a new machine to the system.
    -   **Body**:
        ```json
        {
          "name": "Machine-01",
          "location": "Factory A",
          "sensor_type": "Temperature",
          "status": "active"
        }
        ```
-   **GET** `/api/v1/data/machines` (Protected - All Users)
    -   Lists all machines. Supports filtering via query params (`location`, `status`, `sensor_type`).

### Data Retrieval
-   **GET** `/api/v1/data/machine/{machine_id}` (Protected)
    -   Retrieves historical data for a specific machine.
    -   **Query Params**: `start_time` (Required), `end_time`, `interval`, `fields`, `limit`, `offset`.

### Authentication
-   **POST** `/api/v1/auth/register` - Register new user.
-   **POST** `/api/v1/auth/login` - Login and receive JWTs.
-   **POST** `/api/v1/auth/refresh` - Refresh expired access token.
-   **POST** `/api/v1/auth/logout` - Logout (Server-side token revocation/blacklist).
-   **GET** `/api/v1/auth/me` - Get current user info.

### Configuration (Protected)
-   **GET** `/api/v1/config` - Read system config (Requires `read:config`).
-   **POST** `/api/v1/config/update` - Update config (Management role only).

### System Health
-   **GET** `/health` - Health check.
-   **GET** `/` - API info and version.

> **References:**
> - [REST API Design Guidelines](https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/)
> - [JWT Introduction](https://jwt.io/introduction)

## Testing

### Test Suite
Total of **87 passing test cases** covering:
-   **Unit Tests**: Database handlers, schemas, routes.
-   **Integration Tests**: Cross-database operations.
-   **E2E Tests**: Full API workflows.

*All tests passing with 75.69% coverage (above 75% threshold).*

### Running Tests

Using the script (Recommended):
```bash
./scripts/run.sh dev --test
```

Manual execution with pytest:
```bash
# All tests
pytest tests/ -v --cov=app --cov-report=html

# Specific test types
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
pytest tests/e2e/ -m e2e
```

### Coverage Report
-   **Current Coverage**: 75.69%
-   **Target**: 75%

View `htmlcov/index.html` for detailed reporting.

> **References:**
> - [Pytest Documentation](https://docs.pytest.org/en/7.4.x/)

## Deployment

### 1. Docker (Local Development)
```bash
# Start dev environment
./scripts/run.sh dev
```

### 2. Deployment (Production Server)
CI/CD workflow automatically deploys to the server. For manual deployment:
1.  Copy `docker/` and `scripts/` to the server.
2.  Run:
    ```bash
    ./scripts/run.sh prod
    ```

> **References:**
> - [Docker Compose Overview](https://docs.docker.com/compose/)
> - [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Project Structure

```
gonsters-be-assessment/  
- app/                 # Main Source Code
  - config.py          # Configuration Management
  - models/            # SQLAlchemy Models
  - database/          # Database Handlers (Postgres, InfluxDB, Redis)
  - schemas/           # Pydantic Schemas
  - routes/            # API Endpoints
  - auth/              # JWT Handlers & Middleware
  - utils/             # Utility Modules (Caching, etc.)
  - mqtt/              # MQTT Subscriber
- migrations/          # SQL Migration Files
- tests/               # Test Suite
- docker/              # Docker Configs
- .github/workflows/   # CI/CD Pipeline
```

## Tech Stack

**Core Framework:**
-   **Flask 3.0.0**: Web Framework ([Docs](https://flask.palletsprojects.com/))
-   **SQLAlchemy 2.0.23**: ORM for PostgreSQL ([Docs](https://www.sqlalchemy.org/))
-   **Pydantic 2.5.0**: Data Validation ([Docs](https://docs.pydantic.dev/))

**Databases:**
-   **InfluxDB Client 1.38.0**: Time-series Client ([Docs](https://github.com/influxdata/influxdb-client-python))
-   **Redis 5.0.1** (Client) / **Redis 7.0** (Server): Caching ([Docs](https://redis.io/docs/))

**Messaging & Auth:**
-   **Paho-MQTT 1.6.1**: MQTT Client ([Docs](https://eclipse.dev/paho/))
-   **PyJWT 2.8.0**: JWT Auth ([Docs](https://pyjwt.readthedocs.io/))

**Testing:**
-   **Pytest 7.4.3**: Testing Framework

## License

Created for **GONSTERS Technical Skill Assessment**.

## Author

**Yoga Putra Pratama** - GONSTERS Assessment

