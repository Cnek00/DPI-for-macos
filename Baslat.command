#!/bin/bash
# ============================================================
#   🚀 DISCORD DPI BYPASS & OPTIMIZER PRO v4.0 (macOS)
#   Oyun Pingini Korumalı Otomatik Optimizasyon
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
echo -e "${CYAN}${BOLD}           Discord DPI Bypass • macOS Pro Control Center${RESET}"
echo -e "${WHITE}           GitHub: https://github.com/Cnek00/DPI-for-macos${RESET}"
echo ""
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Sudo kontrolü ve şifre alımı
echo -e "${YELLOW}${BOLD}🔐 YÖNETİCİ ŞİFRESİ (SUDO)${RESET}"
echo -e "${WHITE}SpoofDPI ağ adaptörü bypass yetkisi için şifreniz gerekmektedir.${RESET}"
echo -e "${WHITE}(Şifrenizi şimdi girebilir veya açılan arayüzden de girebilirsiniz)${RESET}"
echo ""

SUDO_PASS=""

# Sudo önbellekte var mı kontrol et
if sudo -n true 2>/dev/null; then
    echo -e "${GREEN}✓ Yönetici yetkisi zaten aktif!${RESET}"
else
    # Şifreyi iste
    read -s -p "🔑 Lütfen macOS Yönetici Şifrenizi Girin (veya Enter ile atlayın): " SUDO_PASS
    echo ""
    if [ -n "$SUDO_PASS" ]; then
        # Şifreyi test et
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
echo -e "${GREEN}${BOLD}🚀 Modern Kontrol Paneli Açılıyor...${RESET}"
echo ""

# Python ile Launcher'ı başlat
if [ -f "$LAUNCHER_PY" ]; then
    python3 "$LAUNCHER_PY" "$SUDO_PASS" &
    PID=$!
    echo -e "${CYAN}✓ Dashboard arka planda başlatıldı (PID: $PID)${RESET}"
    echo -e "${WHITE}  Pencere birazdan otomatik olarak açılacaktır.${RESET}"
else
    echo -e "${RED}✗ $LAUNCHER_PY bulunamadı!${RESET}"
    exit 1
fi

echo ""
echo -e "${GREEN}İşlem tamamlandı. Bu terminal penceresi arka planda kalabilir.${RESET}"
echo ""
sleep 2
