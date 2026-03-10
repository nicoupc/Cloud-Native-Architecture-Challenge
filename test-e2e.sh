#!/bin/bash

# ============================================================
# E2E Test Script - Cloud Native Architecture Challenge
# Prueba el flujo completo: Event -> Booking -> Payment -> Notification
# ============================================================

set -e

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

EVENT_URL="http://localhost:8080/api/v1/events"
BOOKING_URL="http://localhost:3001/api/v1/bookings"
PAYMENT_URL="http://localhost:3002/api/v1/sagas"
SQS_URL="http://localhost:4566"
QUEUE_URL="http://localhost:4566/000000000000/notification-queue"

PASS=0
FAIL=0

# Portable JSON field extractor: tries jq, python, python3, then sed fallback
json_field() {
  local json="$1"
  local field="$2"
  local result=""
  if command -v jq &>/dev/null; then
    result=$(echo "$json" | jq -r ".$field" 2>/dev/null)
  elif python -c "pass" &>/dev/null; then
    result=$(echo "$json" | python -c "import sys,json; print(json.load(sys.stdin)['${field}'])" 2>/dev/null)
  elif python3 -c "pass" &>/dev/null; then
    result=$(echo "$json" | python3 -c "import sys,json; print(json.load(sys.stdin)['${field}'])" 2>/dev/null)
  else
    result=$(echo "$json" | sed -n "s/.*\"${field}\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1)
  fi
  [ -n "$result" ] && [ "$result" != "null" ] && echo "$result" || echo "PARSE_ERROR"
}

# Nested JSON field extractor (e.g., "data.id")
json_nested() {
  local json="$1"
  local path="$2"
  local result=""
  if command -v jq &>/dev/null; then
    result=$(echo "$json" | jq -r ".${path}" 2>/dev/null)
  elif python -c "pass" &>/dev/null; then
    result=$(echo "$json" | python -c "
import sys,json
d=json.load(sys.stdin)
for k in '${path}'.split('.'):
    d=d[k]
print(d)" 2>/dev/null)
  elif python3 -c "pass" &>/dev/null; then
    result=$(echo "$json" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for k in '${path}'.split('.'):
    d=d[k]
print(d)" 2>/dev/null)
  fi
  [ -n "$result" ] && [ "$result" != "null" ] && echo "$result" || echo "PARSE_ERROR"
}

check() {
    local desc="$1"
    local expected="$2"
    local actual="$3"
    if echo "$actual" | grep -qE "$expected"; then
        echo "  [PASS] $desc"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $desc (expected: $expected)"
        echo "         got: $(echo "$actual" | head -c 200)"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "=========================================="
echo " E2E Test - Cloud Native Event Management"
echo "=========================================="
echo ""

# ─── Pre-check: Health endpoints ───
echo "--- Pre-check: Health Endpoints ---"
EVENT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $EVENT_URL/health)
check "Event Service health" "200" "$EVENT_HEALTH"

BOOKING_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/health)
check "Booking Service health" "200" "$BOOKING_HEALTH"

PAYMENT_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/health)
check "Payment Service health" "200" "$PAYMENT_HEALTH"

echo ""

# ─── Step 1: Create Event ───
echo "--- Step 1: Crear Evento ---"
NEXT_YEAR=$(date -d "+1 year" +%Y 2>/dev/null || date -v+1y +%Y 2>/dev/null || echo "2027")
CREATE_EVENT_RESPONSE=$(curl -s -X POST $EVENT_URL \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"E2E Test Concert\",
    \"description\": \"End-to-end test event\",
    \"type\": \"CONCERT\",
    \"eventDate\": \"${NEXT_YEAR}-12-31T20:00:00\",
    \"capacity\": 500,
    \"price\": \"75.00\",
    \"locationVenue\": \"Estadio Nacional\",
    \"locationCity\": \"Lima\",
    \"locationCountry\": \"Peru\"
  }")

EVENT_ID=$(json_field "$CREATE_EVENT_RESPONSE" "id")
check "Evento creado (status DRAFT)" "DRAFT" "$CREATE_EVENT_RESPONSE"
echo "  Event ID: $EVENT_ID"

# ─── Step 2: Publish Event ───
echo ""
echo "--- Step 2: Publicar Evento ---"
PUBLISH_RESPONSE=$(curl -s -X POST "$EVENT_URL/$EVENT_ID/publish")
check "Evento publicado (status PUBLISHED)" "PUBLISHED" "$PUBLISH_RESPONSE"

# ─── Step 3: Create Booking ───
echo ""
echo "--- Step 3: Crear Reserva ---"
USER_ID="550e8400-e29b-41d4-a716-446655440001"
CREATE_BOOKING_RESPONSE=$(curl -s -X POST $BOOKING_URL \
  -H "Content-Type: application/json" \
  -d "{
    \"userId\": \"$USER_ID\",
    \"eventId\": \"$EVENT_ID\",
    \"ticketQuantity\": 3,
    \"pricePerTicket\": 75.00
  }")

BOOKING_ID=$(json_nested "$CREATE_BOOKING_RESPONSE" "data.id")
check "Reserva creada (status PENDING)" "PENDING" "$CREATE_BOOKING_RESPONSE"
echo "  Booking ID: $BOOKING_ID"

# ─── Step 4: Start Payment Saga ───
echo ""
echo "--- Step 4: Iniciar Saga de Pago ---"
START_SAGA_RESPONSE=$(curl -s -X POST $PAYMENT_URL \
  -H "Content-Type: application/json" \
  -d "{
    \"booking_id\": \"$BOOKING_ID\",
    \"amount\": 225.00,
    \"currency\": \"USD\"
  }")

SAGA_ID=$(json_field "$START_SAGA_RESPONSE" "saga_id")
echo "  Saga ID: $SAGA_ID"

# Wait for saga to complete
sleep 3

# ─── Step 5: Verify Saga Status ───
echo ""
echo "--- Step 5: Verificar Estado de Saga ---"
SAGA_STATUS=$(curl -s "$PAYMENT_URL/$SAGA_ID")
check "Saga completada o compensada" "COMPLETED|COMPENSATED" "$SAGA_STATUS"
SAGA_ST=$(json_field "$SAGA_STATUS" "status")
echo "  Saga status: $SAGA_ST"

# ─── Step 6: Verify Booking Confirmed ───
echo ""
echo "--- Step 6: Verificar Reserva Confirmada ---"
BOOKING_STATUS=$(curl -s "$BOOKING_URL/$BOOKING_ID")
BOOKING_ST=$(json_nested "$BOOKING_STATUS" "data.status")
echo "  Booking status: $BOOKING_ST"

# ─── Step 7: Check SQS for notifications ───
echo ""
echo "--- Step 7: Verificar Notificaciones en SQS ---"
SQS_ATTRS=$(aws --endpoint-url=$SQS_URL sqs get-queue-attributes \
  --queue-url $QUEUE_URL \
  --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible \
  --region us-east-1 --output json 2>/dev/null || echo '{"error":"SQS unavailable"}')
echo "  SQS queue attributes: $SQS_ATTRS"

# ─── Step 8: Query events (CQRS read) ───
echo ""
echo "--- Step 8: Consultas CQRS ---"
ALL_EVENTS=$(curl -s "$EVENT_URL")
check "Listar eventos devuelve array" '\[' "$ALL_EVENTS"

USER_BOOKINGS=$(curl -s "$BOOKING_URL/user/$USER_ID")
check "Reservas del usuario devuelve datos" "data" "$USER_BOOKINGS"

# ─── Step 9: Cancel flow ───
echo ""
echo "--- Step 9: Cancelar Evento ---"
CANCEL_RESPONSE=$(curl -s -X POST "$EVENT_URL/$EVENT_ID/cancel" \
  -H "Content-Type: application/json" \
  -d '{"reason":"E2E test - cancellation flow"}')
check "Evento cancelado (status CANCELLED)" "CANCELLED" "$CANCEL_RESPONSE"

# ─── Results ───
echo ""
echo "=========================================="
echo " RESULTADOS E2E"
echo "=========================================="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Total:  $((PASS + FAIL))"
echo "=========================================="

if [ $FAIL -eq 0 ]; then
    echo "  ALL TESTS PASSED!"
else
    echo "  SOME TESTS FAILED"
    exit 1
fi