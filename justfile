# For jamie:
set shell := ["powershell.exe", "-NoLogo", "-Command"]

# justfile for Django project using Docker Compose

check:
    ruff check

checkf:
    ruff check --fix

# Stages all changes, formats code, and prepares a commit message
commit:
    git add .
    pre-commit
    cz c

# Stages specified files, formats code, and prepares a commit message
commitf *files:
    git add {{files}}
    pre-commit
    cz c 

# List all available commands
[default]
default:
    @just --list

down:
    docker compose down

logs:
    docker compose logs -f web

format:
    ruff format

# Create new migrations
makemigrations:
    docker compose exec web python manage.py makemigrations

# Apply database migrations
migrate:
    docker compose exec web python manage.py migrate

# *DANGER* Drop your local db and recreate it with seed data
recreatedb: 
    docker compose down -v
    docker compose up -d
    docker compose exec web python manage.py migrate
    docker compose exec web python manage.py loaddata fixtures/seed_data.json

ruff:
    ruff check --fix
    ruff format

# Run tests with optional arguments
# Usage: just test
# Usage: just test -k test_retrieve_no_profiles -vv
test *args:
    docker compose exec web pytest {{args}}

# Run unit tests with optional arguments
# Usage: just testu
# Usage: just testu -k test_retrieve_no_profiles -vv
testu *args:
    docker compose exec web pytest -m unit {{args}}

# Run integration tests with optional arguments
# Usage: just testi
# Usage: just testi -k test_name -vv
testi *args:
    docker compose exec web pytest -m integration {{args}}

up:
    docker compose up --build -d

# Update API schema docs
updatedocs:
    docker compose run --rm web python manage.py spectacular --file schema.yml