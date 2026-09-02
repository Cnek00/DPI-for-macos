#!/bin/bash
# ============================================================
#   🚀 DISCORD DPI BYPASS & OPTIMIZER PRO v5.0 (macOS)
#   %100 Yerel Python Masaüstü GUI (Native Desktop App)
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_PY="$SCRIPT_DIR/discord_launcher.py"

# Renkler
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
WHITE='\033[1;37m'
RESET='\033[0m'
BOLD='\033[1m'

clear

echo ""
echo -e "${PURPLE}${BOLD}"
echo "  ██████╗ ██████╗ ██╗    ██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗"
echo "  ██╔══██╗██╔══██╗██║    ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝"
echo "  ██║  ██║██████╔╝██║    ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗"
echo "  ██║  ██║██╔═══╝ ██║    ██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║"
echo "  ██████╔╝██║     ██║    ██████╔╝   ██║   ██║     ██║  ██║███████║███████║"
echo "  ╚═════╝ ╚═╝     ╚═╝    ╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝"
echo -e "${RESET}"
echo -e "${CYAN}${BOLD}        Discord DPI Bypass • macOS Native Control Center v5.0${RESET}"
echo -e "${WHITE}        GitHub: https://github.com/Cnek00/DPI-for-macos${RESET}"
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# CustomTkinter kontrolü
if ! python3 -c "import customtkinter" 2>/dev/null; then
    echo -e "${YELLOW}⟳ Native GUI kütüphanesi (customtkinter) hazırlanıyor...${RESET}"
    pip3 install customtkinter >/dev/null 2>&1 || python3 -m pip install customtkinter >/dev/null 2>&1
fi

# Sudo kontrolü ve şifre alımı
echo -e "${YELLOW}${BOLD}🔐 YÖNETİCİ ŞİFRESİ (SUDO)${RESET}"
echo -e "${WHITE}SpoofDPI ağ adaptörü yetkilendirmesi için şifreniz istenebilir.${RESET}"
echo -e "${WHITE}(Şifrenizi şimdi girebilir veya açılan yerel GUI'den de girebilirsiniz)${RESET}"
echo ""

SUDO_PASS=""

if sudo -n true 2>/dev/null; then
    echo -e "${GREEN}✓ Yönetici yetkisi zaten aktif!${RESET}"
else
    read -s -p "🔑 Lütfen macOS Yönetici Şifrenizi Girin (veya Enter ile atlayın): " SUDO_PASS
    echo ""
    if [ -n "$SUDO_PASS" ]; then
        if echo "$SUDO_PASS" | sudo -S true 2>/dev/null; then
            echo -e "${GREEN}✓ Şifre doğrulandı!${RESET}"
        else
            echo -e "${RED}✗ Şifre hatalı! Arayüz üzerinden tekrar girebilirsiniz.${RESET}"
            SUDO_PASS=""
        fi
    else
        echo -e "${YELLOW}ℹ Şifre atlandı. Panelden dilediğiniz zaman girebilirsiniz.${RESET}"
    fi
fi

echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}${BOLD}🚀 Yerel Python GUI Başlatılıyor...${RESET}"
echo ""

# Native GUI'yi başlat
if [ -f "$LAUNCHER_PY" ]; then
    python3 "$LAUNCHER_PY" "$SUDO_PASS" &
    PID=$!
    echo -e "${CYAN}✓ Masaüstü uygulaması açıldı (PID: $PID)${RESET}"
else
    echo -e "${RED}✗ $LAUNCHER_PY bulunamadı!${RESET}"
    exit 1
fi

echo ""
echo -e "${GREEN}İşlem tamamlandı. Bu pencereyi kapatabilir veya arka planda tutabilirsiniz.${RESET}"
echo ""
sleep 2
