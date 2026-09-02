#!/bin/bash
# ============================================================
#   🐳 DISCORD DPI BYPASS - DOCKER BAŞLATICI (macOS)
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

clear
echo "============================================================"
echo "  🐳 Discord DPI Bypass - Docker Container Başlatılıyor"
echo "============================================================"
echo ""

if ! command -v docker &>/dev/null; then
    echo "❌ Docker bulunamadı! Lütfen Docker Desktop kurun."
    echo "   https://www.docker.com/products/docker-desktop/"
    echo ""
    read -p "Çıkmak için Enter'a basın..."
    exit 1
fi

echo "🚀 Docker Compose ile container başlatılıyor..."
docker compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Container başarıyla çalıştırıldı!"
    echo "   • HTTP/HTTPS DPI Proxy : http://127.0.0.1:8080"
    echo "   • SOCKS5 Proxy         : socks5://127.0.0.1:40000"
    echo ""
    echo "Durdurmak için: docker compose down"
else
    echo "❌ Docker başlatılamadı!"
fi

echo ""
read -p "Pencereyi kapatmak için Enter'a basın..."
