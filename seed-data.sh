#!/bin/bash
set -e

# =============================================================================
#  Cloud-Native Architecture Challenge — Seed Data Script
# =============================================================================

# --------------- colours (ANSI) ---------------
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

# --------------- base URLs ---------------
EVENT_SERVICE_URL="http://localhost:8080"
BOOKING_SERVICE_URL="http://localhost:3001"
PAYMENT_SERVICE_URL="http://localhost:3002"

# --------------- counters ---------------
SUCCESS_COUNT=0
FAIL_COUNT=0

# --------------- helpers ---------------
banner() {
  echo ""
  echo -e "${CYAN}======================================================${NC}"
  echo -e "${CYAN}  $1${NC}"
  echo -e "${CYAN}======================================================${NC}"
  echo ""
}

ok()   { echo -e "  ${GREEN}✓ $1${NC}"; SUCCESS_COUNT=$((SUCCESS_COUNT + 1)); }
fail() { echo -e "  ${RED}✗ $1${NC}";   FAIL_COUNT=$((FAIL_COUNT + 1)); }

# Extract a JSON field — uses jq when available, otherwise a grep/sed fallback
json_field() {
  local json="$1"
  local field="$2"
  if command -v jq &>/dev/null; then
    echo "$json" | jq -r ".$field"
  else
    # Fallback: simple grep extraction (handles "field": "value" and "field": value)
    echo "$json" | grep -o "\"$field\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" \
      | head -1 | sed "s/\"$field\"[[:space:]]*:[[:space:]]*\"//;s/\"$//" \
      || echo "$json" | grep -o "\"$field\"[[:space:]]*:[[:space:]]*[0-9.]*" \
      | head -1 | sed "s/\"$field\"[[:space:]]*:[[:space:]]*//"
  fi
}

# --------------- health checks ---------------
banner "Checking Service Health"

check_health() {
  local name="$1"
  local url="$2"
  if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
    ok "$name is healthy"
    return 0
  else
    fail "$name is NOT reachable at $url"
    return 1
  fi
}

ALL_HEALTHY=true
check_health "Event Service"   "${EVENT_SERVICE_URL}/api/v1/events/health"   || ALL_HEALTHY=false
check_health "Booking Service" "${BOOKING_SERVICE_URL}/health"               || ALL_HEALTHY=false
check_health "Payment Service" "${PAYMENT_SERVICE_URL}/health"               || ALL_HEALTHY=false

if [ "$ALL_HEALTHY" = false ]; then
  echo ""
  echo -e "${RED}One or more services are not reachable. Make sure all containers are running.${NC}"
  echo -e "${YELLOW}Hint: docker compose up -d${NC}"
  exit 1
fi

# =============================================================================
#  1. EVENT SERVICE — create 3 events, publish 2
# =============================================================================
banner "Seeding Event Service (PostgreSQL)"

EVENT1_JSON=$(curl -sf -X POST "${EVENT_SERVICE_URL}/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Summer Rock Festival",
    "description": "An outdoor rock music festival featuring top bands from around the world.",
    "type": "CONCERT",
    "eventDate": "2025-08-15T18:00:00",
    "capacity": 5000,
    "price": "75.00",
    "locationVenue": "Central Park Amphitheatre",
    "locationCity": "New York",
    "locationCountry": "USA"
  }') && ok "Created event: Summer Rock Festival" || fail "Failed to create event 1"

EVENT2_JSON=$(curl -sf -X POST "${EVENT_SERVICE_URL}/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Innovation Conference 2025",
    "description": "A two-day conference on cloud-native, AI, and distributed systems.",
    "type": "CONFERENCE",
    "eventDate": "2025-10-20T09:00:00",
    "capacity": 1200,
    "price": "199.99",
    "locationVenue": "Convention Centre",
    "locationCity": "San Francisco",
    "locationCountry": "USA"
  }') && ok "Created event: Tech Innovation Conference 2025" || fail "Failed to create event 2"

EVENT3_JSON=$(curl -sf -X POST "${EVENT_SERVICE_URL}/api/v1/events" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Champions League Final Viewing",
    "description": "Live screening of the Champions League final with food and drinks.",
    "type": "SPORTS",
    "eventDate": "2025-06-01T20:00:00",
    "capacity": 800,
    "price": "45.00",
    "locationVenue": "Olympic Stadium Lounge",
    "locationCity": "London",
    "locationCountry": "UK"
  }') && ok "Created event: Champions League Final Viewing" || fail "Failed to create event 3"

# Extract IDs
EVENT1_ID=$(json_field "$EVENT1_JSON" "id")
EVENT2_ID=$(json_field "$EVENT2_JSON" "id")
EVENT3_ID=$(json_field "$EVENT3_JSON" "id")

echo ""
echo -e "  ${YELLOW}Event IDs:${NC}"
echo -e "    Event 1 (Concert)    : ${EVENT1_ID}"
echo -e "    Event 2 (Conference) : ${EVENT2_ID}"
echo -e "    Event 3 (Sports)     : ${EVENT3_ID}"
echo ""

# Publish events 1 & 2 (leave event 3 as DRAFT)
curl -sf -X POST "${EVENT_SERVICE_URL}/api/v1/events/${EVENT1_ID}/publish" > /dev/null \
  && ok "Published event: Summer Rock Festival" \
  || fail "Failed to publish event 1"

curl -sf -X POST "${EVENT_SERVICE_URL}/api/v1/events/${EVENT2_ID}/publish" > /dev/null \
  && ok "Published event: Tech Innovation Conference 2025" \
  || fail "Failed to publish event 2"

echo -e "  ${YELLOW}(Event 3 left as DRAFT intentionally)${NC}"

# =============================================================================
#  2. BOOKING SERVICE — create 3 bookings
# =============================================================================
banner "Seeding Booking Service (DynamoDB)"

# Use real event IDs for the first two bookings; placeholder UUID for the third
USER1_ID="a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
USER2_ID="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
USER3_ID="c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f"

BOOKING1_JSON=$(curl -sf -X POST "${BOOKING_SERVICE_URL}/api/v1/bookings" \
  -H "Content-Type: application/json" \
  -d "{
    \"eventId\": \"${EVENT1_ID}\",
    \"userId\": \"${USER1_ID}\",
    \"ticketQuantity\": 2,
    \"pricePerTicket\": 75.00
  }") && ok "Created booking: 2 tickets for Summer Rock Festival" || fail "Failed to create booking 1"

BOOKING2_JSON=$(curl -sf -X POST "${BOOKING_SERVICE_URL}/api/v1/bookings" \
  -H "Content-Type: application/json" \
  -d "{
    \"eventId\": \"${EVENT2_ID}\",
    \"userId\": \"${USER2_ID}\",
    \"ticketQuantity\": 1,
    \"pricePerTicket\": 199.99
  }") && ok "Created booking: 1 ticket for Tech Innovation Conference" || fail "Failed to create booking 2"

BOOKING3_JSON=$(curl -sf -X POST "${BOOKING_SERVICE_URL}/api/v1/bookings" \
  -H "Content-Type: application/json" \
  -d "{
    \"eventId\": \"${EVENT1_ID}\",
    \"userId\": \"${USER3_ID}\",
    \"ticketQuantity\": 5,
    \"pricePerTicket\": 75.00
  }") && ok "Created booking: 5 tickets for Summer Rock Festival" || fail "Failed to create booking 3"

# Extract booking IDs (response shape: { success: true, data: { id: "..." } })
BOOKING1_ID=$(json_field "$(echo "$BOOKING1_JSON" | (command -v jq &>/dev/null && jq '.data' || cat))" "id")
BOOKING2_ID=$(json_field "$(echo "$BOOKING2_JSON" | (command -v jq &>/dev/null && jq '.data' || cat))" "id")
BOOKING3_ID=$(json_field "$(echo "$BOOKING3_JSON" | (command -v jq &>/dev/null && jq '.data' || cat))" "id")

echo ""
echo -e "  ${YELLOW}Booking IDs:${NC}"
echo -e "    Booking 1 : ${BOOKING1_ID}"
echo -e "    Booking 2 : ${BOOKING2_ID}"
echo -e "    Booking 3 : ${BOOKING3_ID}"

# =============================================================================
#  3. PAYMENT SERVICE — create 2 sagas
# =============================================================================
banner "Seeding Payment Service (DynamoDB)"

SAGA1_JSON=$(curl -sf -X POST "${PAYMENT_SERVICE_URL}/api/v1/sagas" \
  -H "Content-Type: application/json" \
  -d "{
    \"booking_id\": \"${BOOKING1_ID}\",
    \"amount\": 150.00,
    \"currency\": \"USD\"
  }") && ok "Created payment saga for Booking 1 (\$150.00)" || fail "Failed to create saga 1"

SAGA2_JSON=$(curl -sf -X POST "${PAYMENT_SERVICE_URL}/api/v1/sagas" \
  -H "Content-Type: application/json" \
  -d "{
    \"booking_id\": \"${BOOKING2_ID}\",
    \"amount\": 199.99,
    \"currency\": \"USD\"
  }") && ok "Created payment saga for Booking 2 (\$199.99)" || fail "Failed to create saga 2"

SAGA1_ID=$(json_field "$SAGA1_JSON" "saga_id")
SAGA2_ID=$(json_field "$SAGA2_JSON" "saga_id")

echo ""
echo -e "  ${YELLOW}Saga IDs:${NC}"
echo -e "    Saga 1 : ${SAGA1_ID}"
echo -e "    Saga 2 : ${SAGA2_ID}"

# =============================================================================
#  Summary
# =============================================================================
banner "Seed Complete"

TOTAL=$((SUCCESS_COUNT + FAIL_COUNT))
echo -e "  ${GREEN}Succeeded: ${SUCCESS_COUNT}${NC} / ${TOTAL}"
if [ "$FAIL_COUNT" -gt 0 ]; then
  echo -e "  ${RED}Failed:    ${FAIL_COUNT}${NC} / ${TOTAL}"
fi

echo ""
echo -e "  ${CYAN}Resources created:${NC}"
echo "    • 3 events   (2 published, 1 draft)"
echo "    • 3 bookings (pending)"
echo "    • 2 payment sagas"
echo ""
