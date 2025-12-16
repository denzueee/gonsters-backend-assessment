# GONSTERS Real-time Monitoring System

> **Full-Stack Real-time Machine Monitoring Dashboard**
> Flask Backend + React Frontend + Real-time WebSocket + Auto-Linting

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ESLint](https://img.shields.io/badge/linting-eslint-4B32C3.svg)](https://eslint.org/)

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Auto-Linting](#auto-linting)
- [Deployment](#deployment)
- [License](#license)

---

## 🎯 About

Real-time machine monitoring system untuk GONSTERS Technical Assessment. System ini menggabungkan **Flask backend microservice** dengan **React frontend dashboard** untuk monitoring ratusan mesin industri secara real-time.

**Problem Solved:**

- ✅ Real-time monitoring untuk ratusan mesin industri
- ✅ Time-series data visualization dengan chart interaktif
- ✅ Alert system dengan WebSocket notifications
- ✅ Role-based access control (RBAC)
- ✅ Scalable architecture dengan Redis caching
- ✅ Production-ready dengan Docker & CI/CD

---

## ✨ Features

### 🔥 Core Features

#### Backend (Flask Microservice):

- ✅ **MQTT Subscriber** - Subscribe ke MQTT broker untuk data ingestion
- ✅ **REST API** - Comprehensive API dengan JWT authentication
- ✅ **PostgreSQL** - Machine metadata & user management
- ✅ **InfluxDB** - Time-series sensor data storage
- ✅ **Redis Caching** - Query optimization & token blacklist
- ✅ **WebSocket (Socket.IO)** - Real-time data streaming
- ✅ **RBAC** - Role-based access control (Operator/Supervisor/Management)
- ✅ **Security** - JWT tokens, password hashing, token blacklist

#### Frontend (React Dashboard):

- ✅ **Real-time Dashboard** - Live data visualization
- ✅ **WebSocket Integration** - Real-time sensor data updates
- ✅ **Interactive Charts** - Temperature, pressure, speed monitoring
- ✅ **Alert Panel** - Real-time alerts with sound notifications
- ✅ **Machine Management** - Add, list, filter machines
- ✅ **Historical Data** - Query & export historical data (CSV)
- ✅ **Date Range Filtering** - Custom time range selection
- ✅ **Dark Mode** - Full dark mode support
- ✅ **Responsive Design** - Mobile, tablet, desktop optimized
- ✅ **Settings Panel** - Configure thresholds (Management only)

### 🛡️ Security Features:

- ✅ JWT Access & Refresh Tokens
- ✅ Token Blacklist (Redis-based logout)
- ✅ Bcrypt Password Hashing
- ✅ Role-based Access Control (RBAC)
- ✅ Protected Routes & API Endpoints
- ✅ CORS Configuration
- ✅ Security Headers

### 🎨 UI/UX Features:

- ✅ Glassmorphism Design
- ✅ Smooth Animations & Transitions
- ✅ Infinite Scroll Pagination
- ✅ Responsive Sidebars (Toggle-able)
- ✅ Toast Notifications
- ✅ Loading States & Skeletons
- ✅ Browser Notifications
- ✅ Sound Alert System

### 📊 Data Features:

- ✅ Real-time Sensor Data Streaming
- ✅ Historical Data Query with Intervals
- ✅ CSV Data Export
- ✅ Pagination with Offset/Limit
- ✅ Date Range Filtering
- ✅ Machine Filtering by Status/Location
- ✅ Threshold-based Alerting

### 🧪 Quality Assurance:

- ✅ **75.69% Test Coverage** (87 passing tests)
- ✅ **Auto-Linting** - Black, Flake8, isort, Bandit (Python)
- ✅ **Auto-Formatting** - ESLint, Prettier (JavaScript/React)
- ✅ **Pre-commit Hooks** - Automatic code quality on push
- ✅ **CI/CD Pipeline** - GitHub Actions automation
- ✅ **Docker Support** - Development & production environments

---

## 🛠️ Tech Stack

### Backend:

| Technology         | Version | Purpose                 |
| ------------------ | ------- | ----------------------- |
| **Flask**          | 3.0.0   | Web framework           |
| **PostgreSQL**     | 15      | Relational database     |
| **InfluxDB**       | 2.7     | Time-series database    |
| **Redis**          | 7.0     | Caching & session store |
| **SQLAlchemy**     | 2.0.23  | ORM                     |
| **Pydantic**       | 2.5.0   | Data validation         |
| **PyJWT**          | 2.8.0   | JWT authentication      |
| **Paho-MQTT**      | 1.6.1   | MQTT client             |
| **Flask-SocketIO** | 5.3.5   | WebSocket support       |
| **Bcrypt**         | 4.1.2   | Password hashing        |

### Frontend:

| Technology           | Version | Purpose            |
| -------------------- | ------- | ------------------ |
| **React**            | 18.2.0  | UI framework       |
| **Vite**             | 5.0.8   | Build tool         |
| **TailwindCSS**      | 3.3.6   | Styling            |
| **Recharts**         | 2.10.3  | Data visualization |
| **Socket.IO Client** | 4.8.1   | WebSocket client   |
| **Axios**            | 1.6.2   | HTTP client        |
| **React Router**     | 6.20.0  | Routing            |
| **Lucide React**     | 0.294.0 | Icons              |

### Development Tools:

| Tool           | Purpose            |
| -------------- | ------------------ |
| **Black**      | Python formatter   |
| **Flake8**     | Python linter      |
| **isort**      | Import sorter      |
| **Bandit**     | Security scanner   |
| **ESLint**     | JavaScript linter  |
| **Prettier**   | JS/React formatter |
| **Pre-commit** | Git hooks          |
| **Pytest**     | Testing framework  |
| **Docker**     | Containerization   |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (Recommended)
- **Python** 3.12+
- **Node.js** 18+ & **npm**
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/username/gonsters-be-assessment.git
cd gonsters-be-assessment
```

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration (optional)
nano .env
```

### 3. Run with Docker (Recommended)

```bash
# Make script executable
chmod +x scripts/run.sh

# Start development environment
./scripts/run.sh dev

# Or production mode
./scripts/run.sh prod
```

The script will automatically:

- ✅ Generate JWT keys
- ✅ Build Docker images
- ✅ Start all services (Flask, PostgreSQL, InfluxDB, Redis)
- ✅ Run database migrations
- ✅ Build React frontend
- ✅ Serve application

**Access Points:**

- 🌐 **Dashboard**: http://localhost:5000
- 🔌 **API**: http://localhost:5000/api/v1
- 📊 **InfluxDB UI**: http://localhost:8086
- 🗄️ **PostgreSQL**: localhost:5432

**Default Login:**

- **Username**: `manager1`
- **Password**: `Password123!`

### 4. Local Development (Without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Setup linting tools
chmod +x scripts/setup-linting.sh
./scripts/setup-linting.sh

# 4. Install frontend dependencies
cd app/ui
npm install
cd ../..

# 5. Run Flask backend
python -m app

# 6. Run React frontend (in another terminal)
cd app/ui
npm run dev
```

---

## 📁 Project Structure

```
gonsters-be-assessment/
├── 📂 app/                        # Main application
│   ├── 📂 auth/                   # JWT authentication & middleware
│   ├── 📂 database/               # PostgreSQL, InfluxDB, Redis handlers
│   ├── 📂 models/                 # SQLAlchemy models
│   ├── 📂 mqtt/                   # MQTT subscriber
│   ├── 📂 routes/                 # API endpoints (auth, data, config)
│   ├── 📂 schemas/                # Pydantic validation schemas
│   ├── 📂 utils/                  # Utilities (caching, logging)
│   ├── 📂 websocket/              # Socket.IO handlers
│   ├── 📂 ui/                     # React Frontend
│   │   ├── 📂 src/
│   │   │   ├── 📂 components/    # React components
│   │   │   ├── 📂 contexts/      # Auth & WebSocket contexts
│   │   │   ├── 📂 pages/         # Dashboard & Login pages
│   │   │   ├── App.jsx           # Main app component
│   │   │   └── main.jsx          # Entry point
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── __init__.py                # Flask app factory
│   └── config.py                  # Configuration management
├── 📂 docker/                     # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── 📂 migrations/                 # SQL migration scripts
├── 📂 scripts/                    # Automation scripts
│   ├── run.sh                     # Main deployment script
│   ├── data_simulator.py          # MQTT data simulator
│   └── setup-linting.sh           # Linting setup
├── 📂 tests/                      # Test suite
│   ├── 📂 unit/                   # Unit tests
│   ├── 📂 integration/            # Integration tests
│   └── 📂 e2e/                    # End-to-end tests
├── 📂 docs/                       # Documentation
│   ├── ASSESSMENT_ANSWERS.md      # Assessment documentation
│   └── LINTING.md                 # Linting guide
├── .env.example                   # Environment template
├── .flake8                        # Flake8 configuration
├── .eslintrc.json                 # ESLint configuration
├── .prettierrc.json               # Prettier configuration
├── .pre-commit-config.yaml        # Pre-commit hooks
├── pyproject.toml                 # Python project config
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── CODE_REVIEW.md                 # Code review summary
├── LINTING_SETUP.md               # Linting setup guide
└── README.md                      # This file
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Authentication Endpoints

#### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "username": "user1",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "role": "Operator",
  "factory_id": "FAC-001"
}
```

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "manager1",
  "password": "Password123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "refresh_token": "eyJ0eXAiOiJKV1...",
  "user": { ... }
}
```

#### Refresh Token

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

#### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

#### Get Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

### Data Endpoints

#### Ingest Sensor Data

```http
POST /data/ingest
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "gateway_id": "Gateway-001",
  "timestamp": "2024-01-15T10:30:00Z",
  "batch": [
    {
      "machine_id": "uuid",
      "sensor_type": "Temperature",
      "location": "Factory A",
      "readings": [
        {
          "timestamp": "2024-01-15T10:30:00Z",
          "temperature": 72.5,
          "pressure": 101.3,
          "speed": 1500
        }
      ]
    }
  ]
}
```

#### Add Machine

```http
POST /data/machine
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "CNC-Machine-01",
  "location": "Factory A",
  "sensor_type": "Temperature",
  "status": "active"
}
```

#### List Machines

```http
GET /data/machines?limit=10&offset=0&location=Factory A&status=active
Authorization: Bearer <access_token>
```

#### Get Machine Data

```http
GET /data/machine/{machine_id}?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z&interval=1h&limit=100
Authorization: Bearer <access_token>
```

### Configuration Endpoints

#### Get Config

```http
GET /config
Authorization: Bearer <access_token>
```

#### Update Config (Management Only)

```http
POST /config/update
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "setting_name": "max_temperature_threshold",
  "setting_value": "85.0"
}
```

### WebSocket Events

#### Connect

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000', {
    query: { token: 'Bearer <access_token>' },
});
```

#### Subscribe to All Machines

```javascript
socket.emit('subscribe_all');
```

#### Subscribe to Specific Machine

```javascript
socket.emit('subscribe_machine', { machine_id: 'uuid' });
```

#### Receive Sensor Data

```javascript
socket.on('sensor_data', (data) => {
    console.log('Real-time data:', data);
});
```

#### Receive Alerts

```javascript
socket.on('alert', (alert) => {
    console.log('Alert:', alert);
});
```

**Full API Documentation**: See [docs/ASSESSMENT_ANSWERS.md](docs/ASSESSMENT_ANSWERS.md)

---

## 🧪 Testing

### Test Coverage

**Current Status:**

- ✅ **87 passing tests**
- ✅ **75.69% coverage** (target: 75%)
- ✅ Unit, Integration, and E2E tests

### Run Tests

```bash
# Using run script (recommended)
./scripts/run.sh dev --test

# Manual with pytest
pytest tests/ -v --cov=app --cov-report=html

# Specific test types
pytest tests/unit/ -m unit
pytest tests/integration/ -m integration
pytest tests/e2e/ -m e2e

# View coverage report
open htmlcov/index.html
```

### Test Structure

```
tests/
├── unit/              # Unit tests (models, schemas, utils)
├── integration/       # Integration tests (database, MQTT)
├── e2e/               # End-to-end API tests
├── conftest.py        # Pytest fixtures
└── test_*.py          # Test files
```

---

## 🎨 Auto-Linting

Project ini menggunakan **auto-linting** yang akan otomatis check dan fix code style sebelum push.

### Quick Setup

```bash
# Run setup script
chmod +x scripts/setup-linting.sh
./scripts/setup-linting.sh

# Manual install
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
pre-commit install --hook-type pre-push

cd app/ui && npm install
```

### Tools Used

**Python/Flask:**

- **Black** - Auto-formatter
- **Flake8** - Linter
- **isort** - Import sorter
- **Bandit** - Security scanner

**JavaScript/React:**

- **ESLint** - Linter with auto-fix
- **Prettier** - Code formatter

### How It Works

**On `git push`**, pre-commit hooks will automatically:

1. ✅ Format Python code with Black
2. ✅ Sort Python imports with isort
3. ✅ Lint Python with Flake8
4. ✅ Scan for security issues with Bandit
5. ✅ Format React code with Prettier
6. ✅ Lint React with ESLint (auto-fix)
7. ✅ Remove trailing whitespace
8. ✅ Check YAML/JSON syntax

### Manual Linting

```bash
# Python
black .
isort .
flake8 .
bandit -r app

# React
cd app/ui
npm run lint
npm run format

# Run all checks
pre-commit run --all-files
```

**Full Documentation**: See [docs/LINTING.md](docs/LINTING.md) and [LINTING_SETUP.md](LINTING_SETUP.md)

---

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
# Development
./scripts/run.sh dev

# Production
./scripts/run.sh prod

# With testing
./scripts/run.sh dev --test

# Stop services
./scripts/run.sh stop
```

### CI/CD Pipeline

GitHub Actions workflow automatically:

1. ✅ Runs linting (Black, Flake8, ESLint)
2. ✅ Runs test suite
3. ✅ Checks test coverage (75% minimum)
4. ✅ Builds Docker images
5. ✅ Deploys to production (on main branch)

**Workflow File**: `.github/workflows/ci-cd.yml`

### Environment Variables

Key environment variables (see `.env.example`):

```bash
# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=gonsters_db

# InfluxDB
INFLUXDB_TOKEN=your-token
INFLUXDB_ORG=gonsters
INFLUXDB_BUCKET=sensor_data

# Redis
REDIS_URL=redis://redis:6379/0

# MQTT
MQTT_BROKER_HOST=broker.hivemq.com
MQTT_BROKER_PORT=1883
MQTT_TOPIC=gonsters/sensors/#

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

---

## 📊 Database Schema

### PostgreSQL Tables

**`machine_metadata`**

```sql
- id (UUID, PK)
- name (VARCHAR) - Machine name
- location (VARCHAR) - Physical location
- sensor_type (VARCHAR) - Sensor type
- status (VARCHAR) - Status: active/inactive/maintenance
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

**`users`**

```sql
- id (UUID, PK)
- username (VARCHAR, UNIQUE)
- email (VARCHAR, UNIQUE)
- password_hash (VARCHAR)
- role (VARCHAR) - Operator/Supervisor/Management
- is_active (BOOLEAN)
- factory_id (VARCHAR)
- department (VARCHAR)
- created_at (TIMESTAMP)
```

**`system_config`**

```sql
- id (SERIAL, PK)
- setting_name (VARCHAR, UNIQUE)
- setting_value (TEXT)
- description (TEXT)
- updated_at (TIMESTAMP)
```

### InfluxDB Measurement

**`sensor_readings`**

```
Tags (Indexed):
- machine_id
- sensor_type
- location

Fields:
- temperature (float)
- pressure (float)
- speed (float)

Timestamp: Nanosecond precision
```

---

## 🔒 Security

### Implemented Security Measures:

1. **Authentication & Authorization**
    - JWT Access & Refresh Tokens
    - Role-based Access Control (RBAC)
    - Token Blacklist (Redis-based)
    - Bcrypt Password Hashing

2. **API Security**
    - CORS Configuration
    - Request Validation (Pydantic)
    - SQL Injection Prevention (SQLAlchemy)
    - Rate Limiting (Ready for implementation)

3. **Code Security**
    - Bandit Security Scanner
    - No Hardcoded Secrets
    - Environment Variables
    - .gitignore for Sensitive Files

4. **Network Security**
    - Docker Network Isolation
    - Service-to-Service Communication
    - TLS/SSL Ready

---

## 📚 Documentation

- **[ASSESSMENT_ANSWERS.md](docs/ASSESSMENT_ANSWERS.md)** - Complete assessment documentation
- **[LINTING.md](docs/LINTING.md)** - Auto-linting guide
- **[LINTING_SETUP.md](LINTING_SETUP.md)** - Linting setup summary
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - Code review and cleanup summary

### Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

## 🤝 Contributing

### Code Style

Project ini menggunakan:

- **Python**: Black, Flake8, isort (120 char line length)
- **JavaScript/React**: ESLint, Prettier (120 char line length)

Auto-linting akan run otomatis saat push.

### Development Workflow

1. Create feature branch
2. Make changes
3. Run tests: `pytest tests/`
4. Commit changes (pre-commit hooks akan run)
5. Push (pre-push hooks akan run auto-linting)
6. Create Pull Request

---

## 📝 License

Created for **GONSTERS Technical Skill Assessment** - Back End Developer Position

---

## 👨‍💻 Author

**Yoga Putra Pratama**
GONSTERS Backend Assessment

---

## 🎉 Acknowledgments

- GONSTERS Team untuk assessment ini
- Open-source community untuk amazing tools
- All documentation references linked throughout this README

---

## 📞 Support

Jika ada pertanyaan atau issues:

1. Check dokumentasi di folder `docs/`
2. Review `LINTING_SETUP.md` untuk linting issues
3. Check `.env.example` untuk environment setup
4. Run `./scripts/run.sh dev --test` untuk verify setup

---

**⭐ Star this repo if you found it useful!**
