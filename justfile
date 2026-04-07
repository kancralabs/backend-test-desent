# Default recipe to display available commands
default:
    @just --list

# === Main Commands (Docker-based, recommended) ===

# Create a new migration with auto-generated name (timestamp)
migrate-create:
    #!/usr/bin/env bash
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "Creating migration: auto_migration_${TIMESTAMP}"
    docker-compose exec -T app alembic revision --autogenerate -m "auto_migration_${TIMESTAMP}"

# Create a new migration with custom message
migrate-create-custom MESSAGE:
    @echo "Creating migration: {{MESSAGE}}"
    docker-compose exec -T app alembic revision --autogenerate -m "{{MESSAGE}}"

# Run migrations (upgrade to head)
migrate-up:
    @echo "Running migrations..."
    docker-compose exec -T app alembic upgrade head

# Rollback last migration
migrate-down:
    @echo "Rolling back last migration..."
    docker-compose exec -T app alembic downgrade -1

# Show current migration status
migrate-status:
    @echo "Current migration status:"
    docker-compose exec -T app alembic current

# Show migration history
migrate-history:
    @echo "Migration history:"
    docker-compose exec -T app alembic history --verbose

# Reset database (downgrade all then upgrade)
migrate-reset:
    @echo "Resetting database..."
    docker-compose exec -T app alembic downgrade base
    docker-compose exec -T app alembic upgrade head

# === Local Commands (requires local Python environment) ===

# Local: Create migration with auto-generated name
local-migrate-create:
    #!/usr/bin/env bash
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "Creating migration locally: auto_migration_${TIMESTAMP}"
    alembic revision --autogenerate -m "auto_migration_${TIMESTAMP}"

# Local: Create migration with custom message
local-migrate-create-custom MESSAGE:
    @echo "Creating migration locally: {{MESSAGE}}"
    alembic revision --autogenerate -m "{{MESSAGE}}"

# Local: Run migrations
local-migrate-up:
    @echo "Running migrations locally..."
    alembic upgrade head

# Local: Rollback last migration
local-migrate-down:
    @echo "Rolling back last migration locally..."
    alembic downgrade -1

# Local: Show migration status
local-migrate-status:
    @echo "Current migration status (local):"
    alembic current

# === Docker Management ===

# Start Docker services
up:
    @echo "Starting Docker services..."
    docker-compose up -d

# Stop Docker services
down:
    @echo "Stopping Docker services..."
    docker-compose down

# Rebuild and start Docker services
build:
    @echo "Rebuilding and starting Docker services..."
    docker-compose up --build -d

# View Docker logs (all services)
logs:
    docker-compose logs -f

# View app logs only
logs-app:
    docker-compose logs -f app

# View database logs only
logs-db:
    docker-compose logs -f db

# Run tests
test:
    @echo "Running tests..."
    pytest

# Run tests with coverage
test-coverage:
    @echo "Running tests with coverage..."
    pytest --cov=app --cov-report=html --cov-report=term

# Format code with black
format:
    @echo "Formatting code..."
    black app/

# Lint code with ruff
lint:
    @echo "Linting code..."
    ruff check app/

# Type check with mypy
typecheck:
    @echo "Type checking..."
    mypy app/

# Run all checks (format, lint, typecheck, test)
check: format lint typecheck test
    @echo "All checks passed!"

# Clean up Python cache files
clean:
    @echo "Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
