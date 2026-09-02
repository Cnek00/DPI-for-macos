# ═══════════════════════════════════════════════════════════════════════════════
#   DISCORD DPI BYPASS & OPTIMIZER — DOCKER CONTAINER
#   Multi-Stage Lightweight Build • SpoofDPI + DoH Engine
# ═══════════════════════════════════════════════════════════════════════════════

# Stage 1: Build SpoofDPI from source
FROM golang:1.22-alpine AS builder

RUN apk add --no-cache git make

WORKDIR /build
RUN git clone --depth 1 https://github.com/xvzc/SpoofDPI.git .
RUN go build -ldflags "-s -w" -o /build/spoofdpi ./cmd/spoofdpi

# Stage 2: Final Minimal Runtime Image
FROM alpine:3.19

RUN apk add --no-cache ca-certificates tzdata curl bash bind-tools iptables

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/spoofdpi /usr/local/bin/spoofdpi

# Copy Entrypoint
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /usr/local/bin/spoofdpi

# Environment Configuration
ENV PROXY_PORT=8080
ENV DNS_ADDR=1.1.1.1
ENV DNS_PORT=53
ENV DNS_MODE=doh
ENV ENABLE_LOGS=true

# Expose Proxy Port
EXPOSE 8080 40000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -x http://127.0.0.1:${PROXY_PORT} -sI https://discord.com || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
