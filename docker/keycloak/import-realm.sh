#!/bin/sh
set -e

# Import Keycloak realm on startup
# This script imports the realm-export.json into the running Keycloak instance

KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8080}"
KEYCLOAK_REALM="${KEYCLOAK_REALM:-signal-lab}"

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to be ready..."
for i in $(seq 1 30); do
    if curl -s -o /dev/null -w "" --connect-timeout 2 "$KEYCLOAK_URL/health/ready"; then
        echo "Keycloak is ready"
        break
    fi
    echo "Attempt $i: Keycloak not ready, waiting..."
    sleep 2
done

# Import the realm using Keycloak's admin API or kcadm.sh
REALM_FILE="/opt/keycloak/data/import/realm-export.json"

if [ -f "$REALM_FILE" ]; then
    echo "Importing realm from $REALM_FILE"
    
    # Use kcadm.sh to import the realm
    # First, create a temporary admin credentials file
    KC_ADMIN="${KEYCLOAK_ADMIN:-admin}"
    KC_ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
    
    # Try using kcadm if available, otherwise use curl with admin token
    if [ -x "$(command -v kcadm.sh)" ]; then
        kcadm.sh update realms -f "$REALM_URL" --server "$KEYCLOAK_URL" --realm "$KEYCLOAK_REALM" --user "$KC_ADMIN" --password "$KC_ADMIN_PASSWORD" 2>/dev/null || \
        kcadm.sh create realms -f "$REALM_FILE" --server "$KEYCLOAK_URL" 2>/dev/null || echo "Realm import via kcadm failed, trying curl"
    fi
    
    # Fallback: use curl with bearer token
    # Get admin token
    TOKEN_RESPONSE=$(curl -s -d "client_id=admin-cli" \
        -d "username=$KC_ADMIN" \
        -d "password=$KC_ADMIN_PASSWORD" \
        -d "grant_type=password" \
        "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token")
    
    ADMIN_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    
    if [ -n "$ADMIN_TOKEN" ]; then
        curl -s -X POST "$KEYCLOAK_URL/realms/master/entities/realms" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d "@$REALM_FILE" && echo "Realm imported successfully"
    else
        echo "Could not obtain admin token, realm import skipped"
    fi
else
    echo "Realm file not found at $REALM_FILE"
fi
