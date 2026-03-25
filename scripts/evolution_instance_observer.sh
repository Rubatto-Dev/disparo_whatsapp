#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-/home/rubatto-dev/disparo_whatsapp/.env}"

read_env_value() {
  local key="$1"
  local value

  if [[ ! -f "$ENV_FILE" ]]; then
    return 1
  fi

  value="$(grep -E "^${key}=" "$ENV_FILE" | tail -n 1 | cut -d '=' -f2- || true)"
  if [[ -z "$value" ]]; then
    return 1
  fi

  printf '%s' "$value"
}

INSTANCE="${INSTANCE:-}"
API_KEY="${API_KEY:-}"
BASE_URL="${BASE_URL:-}"
POLL_SECONDS="${POLL_SECONDS:-}"
QR_REFRESH_COOLDOWN="${QR_REFRESH_COOLDOWN:-}"
OUT_DIR="${OUT_DIR:-}"

ALERT_PREFIX="${ALERT_PREFIX:-}"
ALERT_NOTIFY_ON_OPEN="${ALERT_NOTIFY_ON_OPEN:-}"
ALERT_NOTIFY_ON_CONNECTING="${ALERT_NOTIFY_ON_CONNECTING:-}"
ALERT_NOTIFY_ON_CLOSE="${ALERT_NOTIFY_ON_CLOSE:-}"
ALERT_DOWN_REMINDER_ENABLED="${ALERT_DOWN_REMINDER_ENABLED:-}"
ALERT_DOWN_REMINDER_COOLDOWN="${ALERT_DOWN_REMINDER_COOLDOWN:-}"

ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"
ALERT_SLACK_WEBHOOK_URL="${ALERT_SLACK_WEBHOOK_URL:-}"
ALERT_TELEGRAM_BOT_TOKEN="${ALERT_TELEGRAM_BOT_TOKEN:-}"
ALERT_TELEGRAM_CHAT_ID="${ALERT_TELEGRAM_CHAT_ID:-}"

INSTANCE="${INSTANCE:-$(read_env_value EVOLUTION_INSTANCE || true)}"
API_KEY="${API_KEY:-$(read_env_value EVOLUTION_API_KEY || true)}"
BASE_URL="${BASE_URL:-$(read_env_value EVOLUTION_BASE_URL || true)}"

ALERT_PREFIX="${ALERT_PREFIX:-$(read_env_value ALERT_PREFIX || true)}"
ALERT_NOTIFY_ON_OPEN="${ALERT_NOTIFY_ON_OPEN:-$(read_env_value ALERT_NOTIFY_ON_OPEN || true)}"
ALERT_NOTIFY_ON_CONNECTING="${ALERT_NOTIFY_ON_CONNECTING:-$(read_env_value ALERT_NOTIFY_ON_CONNECTING || true)}"
ALERT_NOTIFY_ON_CLOSE="${ALERT_NOTIFY_ON_CLOSE:-$(read_env_value ALERT_NOTIFY_ON_CLOSE || true)}"
ALERT_DOWN_REMINDER_ENABLED="${ALERT_DOWN_REMINDER_ENABLED:-$(read_env_value ALERT_DOWN_REMINDER_ENABLED || true)}"
ALERT_DOWN_REMINDER_COOLDOWN="${ALERT_DOWN_REMINDER_COOLDOWN:-$(read_env_value ALERT_DOWN_REMINDER_COOLDOWN || true)}"
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-$(read_env_value ALERT_WEBHOOK_URL || true)}"
ALERT_SLACK_WEBHOOK_URL="${ALERT_SLACK_WEBHOOK_URL:-$(read_env_value ALERT_SLACK_WEBHOOK_URL || true)}"
ALERT_TELEGRAM_BOT_TOKEN="${ALERT_TELEGRAM_BOT_TOKEN:-$(read_env_value ALERT_TELEGRAM_BOT_TOKEN || true)}"
ALERT_TELEGRAM_CHAT_ID="${ALERT_TELEGRAM_CHAT_ID:-$(read_env_value ALERT_TELEGRAM_CHAT_ID || true)}"

INSTANCE="${INSTANCE:-hogar-luxo}"
API_KEY="${API_KEY:-}"
BASE_URL="${BASE_URL:-http://localhost:8080}"
POLL_SECONDS="${POLL_SECONDS:-20}"
QR_REFRESH_COOLDOWN="${QR_REFRESH_COOLDOWN:-90}"
OUT_DIR="${OUT_DIR:-/home/rubatto-dev/disparo_whatsapp/tmp_observer}"

ALERT_PREFIX="${ALERT_PREFIX:-[Evolution Observer]}"
ALERT_NOTIFY_ON_OPEN="${ALERT_NOTIFY_ON_OPEN:-true}"
ALERT_NOTIFY_ON_CONNECTING="${ALERT_NOTIFY_ON_CONNECTING:-true}"
ALERT_NOTIFY_ON_CLOSE="${ALERT_NOTIFY_ON_CLOSE:-true}"
ALERT_DOWN_REMINDER_ENABLED="${ALERT_DOWN_REMINDER_ENABLED:-true}"
ALERT_DOWN_REMINDER_COOLDOWN="${ALERT_DOWN_REMINDER_COOLDOWN:-900}"

mkdir -p "$OUT_DIR"

last_status=""
last_qr_refresh=0
last_down_reminder=0
warned_no_channels=0

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*"
}

is_true() {
  case "${1:-}" in
    1|true|TRUE|True|yes|YES|sim|SIM|on|ON|y|Y) return 0 ;;
    *) return 1 ;;
  esac
}

if ! [[ "$POLL_SECONDS" =~ ^[0-9]+$ ]]; then
  POLL_SECONDS=20
fi

if ! [[ "$QR_REFRESH_COOLDOWN" =~ ^[0-9]+$ ]]; then
  QR_REFRESH_COOLDOWN=90
fi

if ! [[ "$ALERT_DOWN_REMINDER_COOLDOWN" =~ ^[0-9]+$ ]]; then
  ALERT_DOWN_REMINDER_COOLDOWN=900
fi

if [[ -z "$API_KEY" ]]; then
  echo "ERRO: EVOLUTION_API_KEY/API_KEY nao definido para o observer." >&2
  exit 1
fi

post_json() {
  local url="$1"
  local payload="$2"

  if [[ -z "$url" ]]; then
    return 1
  fi

  curl -sS --max-time 15 \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$url" >/dev/null 2>&1
}

notify_external() {
  local event="$1"
  local status="$2"
  local reason="$3"
  local updated_at="$4"
  local qr_png="${5:-}"

  local ts_iso
  ts_iso="$(date -Iseconds)"

  local message
  message="${ALERT_PREFIX}
instance: ${INSTANCE}
event: ${event}
status: ${status}
reason: ${reason:--}
updatedAt: ${updated_at:--}
time: ${ts_iso}"

  if [[ -n "$qr_png" ]]; then
    message="${message}
qr: ${qr_png}"
  fi

  local payload
  payload="$(jq -n \
    --arg prefix "$ALERT_PREFIX" \
    --arg instance "$INSTANCE" \
    --arg event "$event" \
    --arg status "$status" \
    --arg reason "$reason" \
    --arg updatedAt "$updated_at" \
    --arg time "$ts_iso" \
    --arg message "$message" \
    --arg qr "$qr_png" \
    '{
      prefix: $prefix,
      instance: $instance,
      event: $event,
      status: $status,
      reason: $reason,
      updatedAt: $updatedAt,
      time: $time,
      message: $message,
      qr: $qr
    }')"

  local sent=0

  if [[ -n "$ALERT_WEBHOOK_URL" ]]; then
    if post_json "$ALERT_WEBHOOK_URL" "$payload"; then
      sent=1
    else
      log "falha ao notificar ALERT_WEBHOOK_URL"
    fi
  fi

  if [[ -n "$ALERT_SLACK_WEBHOOK_URL" ]]; then
    local slack_payload
    slack_payload="$(jq -n --arg text "$message" '{text: $text}')"
    if post_json "$ALERT_SLACK_WEBHOOK_URL" "$slack_payload"; then
      sent=1
    else
      log "falha ao notificar ALERT_SLACK_WEBHOOK_URL"
    fi
  fi

  if [[ -n "$ALERT_TELEGRAM_BOT_TOKEN" && -n "$ALERT_TELEGRAM_CHAT_ID" ]]; then
    local telegram_url
    local telegram_payload
    telegram_url="https://api.telegram.org/bot${ALERT_TELEGRAM_BOT_TOKEN}/sendMessage"
    telegram_payload="$(jq -n \
      --arg chat_id "$ALERT_TELEGRAM_CHAT_ID" \
      --arg text "$message" \
      '{chat_id: $chat_id, text: $text, disable_web_page_preview: true}')"

    if post_json "$telegram_url" "$telegram_payload"; then
      sent=1
    else
      log "falha ao notificar Telegram"
    fi
  fi

  if (( sent == 0 )) && (( warned_no_channels == 0 )); then
    log "nenhum canal externo configurado (ALERT_WEBHOOK_URL / ALERT_SLACK_WEBHOOK_URL / TELEGRAM)"
    warned_no_channels=1
  fi
}

should_notify_status() {
  local current="$1"

  case "$current" in
    open)
      is_true "$ALERT_NOTIFY_ON_OPEN"
      return $?
      ;;
    connecting)
      is_true "$ALERT_NOTIFY_ON_CONNECTING"
      return $?
      ;;
    *)
      is_true "$ALERT_NOTIFY_ON_CLOSE"
      return $?
      ;;
  esac
}

log "Observer iniciado. instance=${INSTANCE} poll=${POLL_SECONDS}s qr_cooldown=${QR_REFRESH_COOLDOWN}s reminder=${ALERT_DOWN_REMINDER_COOLDOWN}s"

while true; do
  payload="$(curl -sS -H "apikey: ${API_KEY}" "${BASE_URL}/instance/fetchInstances" || true)"

  if [[ -z "${payload}" ]]; then
    log "fetchInstances sem resposta; aguardando ${POLL_SECONDS}s"
    sleep "$POLL_SECONDS"
    continue
  fi

  status="$(echo "$payload" | jq -r ".[] | select(.name==\"${INSTANCE}\") | .connectionStatus" || true)"
  reason="$(echo "$payload" | jq -r ".[] | select(.name==\"${INSTANCE}\") | (.disconnectionReasonCode // \"\")" || true)"
  updated_at="$(echo "$payload" | jq -r ".[] | select(.name==\"${INSTANCE}\") | (.updatedAt // \"\")" || true)"

  if [[ -z "$status" || "$status" == "null" ]]; then
    log "instancia '${INSTANCE}' nao encontrada; aguardando ${POLL_SECONDS}s"
    sleep "$POLL_SECONDS"
    continue
  fi

  now="$(date +%s)"
  changed=0
  if [[ "$status" != "$last_status" ]]; then
    changed=1
  fi

  latest_qr_png=""

  if [[ "$status" != "open" ]] && (( now - last_qr_refresh >= QR_REFRESH_COOLDOWN )); then
    ts="$(date +%Y%m%d_%H%M%S)"
    qr_json="${OUT_DIR}/evolution_connect_${ts}.json"
    qr_png="${OUT_DIR}/evolution_connect_${ts}.png"

    http_code="$(curl -sS -o "$qr_json" -w '%{http_code}' -H "apikey: ${API_KEY}" -X GET "${BASE_URL}/instance/connect/${INSTANCE}" || true)"

    if [[ "$http_code" == "200" ]]; then
      qr_base64="$(jq -r '.base64 // empty' "$qr_json" || true)"
      if [[ -n "$qr_base64" ]]; then
        echo "$qr_base64" | sed 's#^data:image/png;base64,##' | base64 -d > "$qr_png" || true
        latest_qr_png="$qr_png"
        log "QR renovado: ${qr_png}"
      else
        log "connect retornou sem base64 (json salvo em ${qr_json})"
      fi
    else
      log "falha ao renovar QR (http=${http_code})"
    fi

    last_qr_refresh=$now
  fi

  if (( changed == 1 )); then
    log "status ${last_status:-<none>} -> ${status} | reason=${reason:--} | updatedAt=${updated_at:--}"

    if should_notify_status "$status"; then
      notify_external "status_change" "$status" "${reason:--}" "${updated_at:--}" "$latest_qr_png"
    fi

    if [[ "$status" == "open" ]]; then
      last_down_reminder=0
    else
      last_down_reminder=$now
    fi

    last_status="$status"
  fi

  if [[ "$status" != "open" ]] && is_true "$ALERT_DOWN_REMINDER_ENABLED"; then
    if (( now - last_down_reminder >= ALERT_DOWN_REMINDER_COOLDOWN )); then
      notify_external "down_reminder" "$status" "${reason:--}" "${updated_at:--}" "$latest_qr_png"
      last_down_reminder=$now
    fi
  fi

  sleep "$POLL_SECONDS"
done
