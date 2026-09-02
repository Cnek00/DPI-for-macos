#!/bin/bash
set -e

echo "══════════════════════════════════════════════════════════════════"
echo "  🚀 DISCORD DPI BYPASS & SPOOFDPI CONTAINER STARTED"
echo "══════════════════════════════════════════════════════════════════"
echo "  • Proxy Port : ${PROXY_PORT:-8080}"
echo "  • DNS Mode   : ${DNS_MODE:-doh}"
echo "  • DNS Server : ${DNS_ADDR:-1.1.1.1}"
echo "══════════════════════════════════════════════════════════════════"

# Build SpoofDPI arguments
ARGS="--port ${PROXY_PORT:-8080} --dns-mode ${DNS_MODE:-doh} --dns-addr ${DNS_ADDR:-1.1.1.1} --no-tui"

if [ -n "$PATTERN" ]; then
    ARGS="$ARGS --pattern $PATTERN"
fi

if [ -n "$DEBUG" ]; then
    ARGS="$ARGS --debug"
fi

# Handle termination signals cleanly
trap 'echo "Stopping SpoofDPI Container..."; exit 0' SIGTERM SIGINT

echo "Starting SpoofDPI Engine..."
exec /usr/local/bin/spoofdpi $ARGS
