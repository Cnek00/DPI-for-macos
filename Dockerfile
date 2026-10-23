# ═══════════════════════════════════════════════════════════════════════════════
#   DISCORD DPI BYPASS & OPTIMIZER — DOCKER CONTAINER
#   Multi-Stage Lightweight Build • SpoofDPI + DoH Engine
# ═══════════════════════════════════════════════════════════════════════════════

# Stage 1: Build SpoofDPI from source
FROM golang:1.26-alpine AS builder

ARG SPOOFDPI_VERSION=1.5.5

RUN apk add --no-cache git make

WORKDIR /build
RUN git clone --depth 1 --branch "v${SPOOFDPI_VERSION}" \
        https://github.com/xvzc/SpoofDPI.git .
RUN go build -ldflags "-s -w" -o /build/spoofdpi ./cmd/spoofdpi

# Stage 2: Final Minimal Runtime Image
FROM alpine:3.19

RUN apk add --no-cache ca-certificates tzdata curl bash bind-tools iptables netcat-openbsd

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/spoofdpi /usr/local/bin/spoofdpi

# Copy Entrypoint
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /usr/local/bin/spoofdpi

# Environment Configuration
ENV PROXY_PORT=8080
ENV DNS_MODE=https
ENV DNS_HTTPS_URL=https://cloudflare-dns.com/dns-query
ENV DNS_ADDR=1.1.1.1:53
ENV LOG_LEVEL=info

# The container runs SpoofDPI only; WARP stays on the host.
EXPOSE 8080

# Healthcheck: the proxy is healthy when its local listener accepts connections.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD nc -z 127.0.0.1 "${PROXY_PORT}" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
