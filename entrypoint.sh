#!/usr/bin/env bash

# This script fetches secrets from AWS Secrets Manager and exports them as environment variables.
# It is only needed in our cloud environments. 

set -euo pipefail

# Fetch app secrets
if [[ -n "${APP_SECRETS_ARN:-}" ]]; then
    json=$(aws secretsmanager get-secret-value --secret-id "$APP_SECRETS_ARN" --query SecretString --output text)
    # Export each top-level JSON key as an env var. Requires jq to be installed in the Dockerfile.
    while IFS="=" read -r k v; do
        export "$k"="$v"
    done < <(echo "$json" | jq -r 'to_entries[] | "\(.key|ascii_upcase)=\(.value)"')
fi

# Fetch db password secret (a json), extract the "password" value, and set it to the env variable.
if [[ -n "${DB_PASSWORD_SECRET_ARN:-}" ]]; then
    export POSTGRES_PASSWORD="$(aws secretsmanager get-secret-value --secret-id "$DB_PASSWORD_SECRET_ARN" --query SecretString --output text | jq -r .password)"
fi

CONTAINER_INFO=$(curl -s "$ECS_CONTAINER_METADATA_URI_V4/task")
echo "Container info: $CONTAINER_INFO"

# Append container's private IP to ALLOWED_HOSTS for ALB health checks
CONTAINER_IP=$(curl -s "$ECS_CONTAINER_METADATA_URI_V4/task" \
    | grep -oE '"IPv4Addresses":\["[^"]+"' \
    | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
if [ -n "$CONTAINER_IP" ]; then
    export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS},${CONTAINER_IP}"
    echo "Container private IP: $CONTAINER_IP"
fi

echo "Running Django migrations..."
python manage.py migrate --noinput
echo "Migrations complete."

# Create a Django superuser if not exists
if [[ -n "${DJANGO_SUPERUSER_EMAIL:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
    echo "Ensuring Django superuser exists..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='${DJANGO_SUPERUSER_EMAIL}').exists():
    User.objects.create_superuser(
        email='${DJANGO_SUPERUSER_EMAIL}',
        password='${DJANGO_SUPERUSER_PASSWORD}'
    )
EOF
fi

exec "$@"
