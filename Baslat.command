#!/bin/bash
# ============================================================
#   Discord DPI Bypass - Otomatik Başlatıcı
#   Sırasıyla: WARP → SpoofDPI → Discord GUI
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_PY="$SCRIPT_DIR/discord_launcher.py"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
RESET='\033[0m'
BOLD='\033[1m'

clear

echo ""
echo -e "${PURPLE}${BOLD}"
echo "  ██████╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ██████╗ "
echo "  ██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗"
echo "  ██║  ██║██║███████╗██║     ██║   ██║██████╔╝██║  ██║"
echo "  ██║  ██║██║╚════██║██║     ██║   ██║██╔══██╗██║  ██║"
echo "  ██████╔╝██║███████║╚██████╗╚██████╔╝██║  ██║██████╔╝"
echo "  ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ "
echo -e "${RESET}"
echo -e "${CYAN}${BOLD}        DPI Bypass - macOS Otomatik Başlatıcı${RESET}"
echo -e "${WHITE}        GitHub: github.com/Cnek00/DPI-for-macos${RESET}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# ─── Python kontrolü ───────────────────────────
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
    elif command -v python &>/dev/null; then
        PYTHON="python"
    else
        echo -e "${RED}✗ Python bulunamadı! Lütfen Python 3 kurun.${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python bulundu: $(${PYTHON} --version)${RESET}"
}

# ─── WARP kontrolü ─────────────────────────────
check_warp() {
    echo -e "${YELLOW}⟳ Cloudflare WARP kontrol ediliyor...${RESET}"
    if ! command -v warp-cli &>/dev/null; then
        echo -e "${RED}✗ Cloudflare WARP kurulu değil!${RESET}"
        echo -e "${WHITE}  Kurmak için: brew install --cask cloudflare-warp${RESET}"
        echo ""
        read -p "  WARP kurulumu atlanarak devam edilsin mi? (e/h): " skip
        if [[ "$skip" != "e" && "$skip" != "E" ]]; then
            echo -e "${RED}  Çıkış yapılıyor.${RESET}"
            exit 1
        fi
        return 1
    fi
    echo -e "${GREEN}✓ Cloudflare WARP kurulu${RESET}"
    return 0
}

# ─── SpoofDPI kontrolü ─────────────────────────
check_spoofdpi() {
    echo -e "${YELLOW}⟳ SpoofDPI kontrol ediliyor...${RESET}"
    if [ ! -f "/opt/homebrew/opt/spoofdpi/bin/spoofdpi" ]; then
        echo -e "${RED}✗ SpoofDPI kurulu değil!${RESET}"
        echo -e "${WHITE}  Kurmak için: brew install spoofdpi${RESET}"
        echo ""
        read -p "  SpoofDPI kurulumu atlanarak devam edilsin mi? (e/h): " skip
        if [[ "$skip" != "e" && "$skip" != "E" ]]; then
            echo -e "${RED}  Çıkış yapılıyor.${RESET}"
            exit 1
        fi
        return 1
    fi
    echo -e "${GREEN}✓ SpoofDPI kurulu${RESET}"
    return 0
}

# ─── Tkinter kontrolü ──────────────────────────
check_tkinter() {
    echo -e "${YELLOW}⟳ Tkinter kontrol ediliyor...${RESET}"
    if ! $PYTHON -c "import tkinter" &>/dev/null; then
        echo -e "${RED}✗ Tkinter bulunamadı!${RESET}"
        echo -e "${WHITE}  macOS'ta genellikle python.org'dan Python kurulumu gerekir.${RESET}"
        echo -e "${WHITE}  Veya: brew install python-tk${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✓ Tkinter hazır${RESET}"
}

# ─── Kontrolleri yap ───────────────────────────
echo -e "${BOLD}${WHITE}[ Bağımlılık Kontrolleri ]${RESET}"
echo ""
check_python
check_warp
check_spoofdpi
check_tkinter
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "${GREEN}${BOLD}✓ Tüm kontroller tamamlandı!${RESET}"
echo -e "${WHITE}  GUI başlatıcı açılıyor...${RESET}"
echo ""
sleep 1

# ─── GUI'yi başlat ─────────────────────────────
if [ -f "$LAUNCHER_PY" ]; then
    $PYTHON "$LAUNCHER_PY" &
    LAUNCHER_PID=$!
    echo -e "${GREEN}✓ Discord DPI Bypass Başlatıcı açıldı (PID: $LAUNCHER_PID)${RESET}"
else
    echo -e "${RED}✗ discord_launcher.py bulunamadı!${RESET}"
    echo -e "${WHITE}  Beklenen konum: $LAUNCHER_PY${RESET}"
    exit 1
fi

echo ""
echo -e "${CYAN}  GUI penceresi açıldı. Bu terminal penceresi kapatılabilir.${RESET}"
echo ""
