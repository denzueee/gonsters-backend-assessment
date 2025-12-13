#!/bin/bash

APP_NAME="gonsters-backend"
DOCKER_DIR="docker"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

generate_keys() {
    if [ -f "$ENV_FILE" ]; then
        echo "Environment file .env already exists. Skipping generation."
        return
    fi

    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "Error: .env.example not found"
        exit 1
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"

    # Generate random keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_KEY=$(openssl rand -hex 32)
    POSTGRES_PASS=$(openssl rand -hex 16)
    INFLUX_TOKEN=$(openssl rand -base64 32 | tr -d '+/' | cut -c1-32)
    INFLUX_PASS=$(openssl rand -hex 12)

    python3 -c "
import sys
content = open('$ENV_FILE').read()
content = content.replace('CHANGE_ME_SECRET_KEY', '$SECRET_KEY')
content = content.replace('CHANGE_ME_JWT_KEY', '$JWT_KEY')
content = content.replace('CHANGE_ME_INFLUX_TOKEN', '$INFLUX_TOKEN')
content = content.replace('POSTGRES_PASSWORD=postgres', 'POSTGRES_PASSWORD=$POSTGRES_PASS')
content = content.replace('DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword', 'DOCKER_INFLUXDB_INIT_PASSWORD=$INFLUX_PASS')
open('$ENV_FILE', 'w').write(content)
"
    echo "Environment keys generated successfully."
}

run_tests() {
    echo "========================================="
    echo "Running Test Suite"
    echo "========================================="
    
    # Check if containers are running
    if ! sudo docker ps | grep -q gonsters-backend; then
        echo "Error: Containers are not running"
        echo "Please start environment first with: ./scripts/run.sh dev or ./scripts/run.sh prod"
        exit 1
    fi
    
    # Create test database if it doesn't exist
    echo "Setting up test database..."
    sudo docker exec gonsters-postgres psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'gonsters_test_db'" | grep -q 1 || \
        sudo docker exec gonsters-postgres psql -U postgres -c "CREATE DATABASE gonsters_test_db;"
    
    # Get InfluxDB token from running container
    INFLUX_TOKEN=$(sudo docker exec gonsters-influxdb printenv DOCKER_INFLUXDB_INIT_ADMIN_TOKEN)
    
    # Run tests with proper environment variables
    echo ""
    echo "Running test suite..."
    echo "========================================="
    sudo docker exec \
      -e FLASK_ENV=testing \
      -e POSTGRES_DB=gonsters_test_db \
      -e INFLUXDB_INIT_ADMIN_TOKEN="$INFLUX_TOKEN" \
      gonsters-backend \
      pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html
    
    TEST_EXIT_CODE=$?
    
    echo ""
    echo "========================================="
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo "All tests passed!"
    else
        echo "Some tests failed (Exit code: $TEST_EXIT_CODE)"
    fi
    echo "========================================="
    
    return $TEST_EXIT_CODE
}

run_dev() {
    if [ "$1" == "--test" ]; then
        run_tests
        exit $?
    fi
    
    echo "Starting Development Environment..."
    generate_keys
    
    echo "Building and starting containers..."
    sudo docker-compose --env-file .env -f "$DOCKER_DIR/docker-compose.yml" up -d --build
    
    echo "Dev environment running at http://localhost:5000"
}

run_prod() {
    if [ "$1" == "--test" ]; then
        run_tests
        exit $?
    fi
    
    echo "Deploying Production Environment..."
    generate_keys
    
    echo "Pulling latest images..."
    sudo docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" pull
    
    echo "Starting production containers..."
    sudo docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" up -d
    
    echo "Production deployment successful."
}

stop() {
    echo "Stopping all containers..."
    sudo docker-compose -f "$DOCKER_DIR/docker-compose.yml" down
    sudo docker-compose -f "$DOCKER_DIR/docker-compose.prod.yml" down
}

case "$1" in
    dev)
        run_dev "$2"
        ;;
    prod)
        run_prod "$2"
        ;;
    stop)
        stop
        ;;
    gen-keys)
        generate_keys
        ;;
    *)
        echo "Usage: ./scripts/run.sh {dev|prod|stop|gen-keys} [--test]"
        echo ""
        echo "Commands:"
        echo "  dev              - Start development environment"
        echo "  dev --test       - Run tests on running dev environment"
        echo "  prod             - Deploy production environment"
        echo "  prod --test      - Run tests on running prod environment"
        echo "  stop             - Stop all containers"
        echo "  gen-keys         - Generate environment keys"
        exit 1
        ;;
esac
