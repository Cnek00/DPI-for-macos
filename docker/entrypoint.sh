#!/bin/bash
set -e

echo "══════════════════════════════════════════════════════════════════"
echo "  🚀 DISCORD DPI BYPASS & SPOOFDPI CONTAINER STARTED"
echo "══════════════════════════════════════════════════════════════════"
echo "  • Proxy Port : ${PROXY_PORT:-8080}"
echo "  • DNS Mode   : ${DNS_MODE:-https}"
if [ "${DNS_MODE:-https}" = "https" ]; then
    echo "  • DoH Server : ${DNS_HTTPS_URL:-https://cloudflare-dns.com/dns-query}"
else
    echo "  • DNS Server : ${DNS_ADDR:-1.1.1.1:53}"
fi
echo "══════════════════════════════════════════════════════════════════"

# Build SpoofDPI arguments without relying on shell word splitting.
ARGS=(
    --listen-addr "0.0.0.0:${PROXY_PORT:-8080}"
    --app-mode http
    --dns-mode "${DNS_MODE:-https}"
    --log-level "${LOG_LEVEL:-info}"
    --no-tui
)

if [ "${DNS_MODE:-https}" = "https" ]; then
    ARGS+=(--dns-https-url "${DNS_HTTPS_URL:-https://cloudflare-dns.com/dns-query}")
else
    ARGS+=(--dns-addr "${DNS_ADDR:-1.1.1.1:53}")
fi

# Handle termination signals cleanly
trap 'echo "Stopping SpoofDPI Container..."; exit 0' SIGTERM SIGINT

echo "Starting SpoofDPI Engine..."
exec /usr/local/bin/spoofdpi "${ARGS[@]}"
