#!/bin/bash
echo "==========================================="
echo "   GoodbyeDPI MacOS (SpoofDPI) Baslatiliyor"
echo "==========================================="
echo "Bu pencere acik kaldigi surece Discord ve tum yasakli sitelere"
echo "erisebilirsiniz. Oyun pinginiz (UDP) ETKILENMEZ!"
echo "Discord'u normal sekilde baslatin."
echo "Iptal etmek icin pencereyi kapatin veya Ctrl+C yapin."
echo "-------------------------------------------"

# SpoofDPI renamed the DoH mode from "doh" to "https" in 1.5.5.
SPOOFDPI_BIN="/opt/homebrew/opt/spoofdpi/bin/spoofdpi"
DNS_MODE="https"
if ! "$SPOOFDPI_BIN" --help 2>&1 | grep -q 'dns-mode.*https'; then
    DNS_MODE="doh"
fi

# Sudo yetkisi gerekebilir ag ayarlari icin
sudo "$SPOOFDPI_BIN" --auto-configure-network --dns-mode "$DNS_MODE" --no-tui
