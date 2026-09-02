#!/bin/bash
echo "==========================================="
echo "   GoodbyeDPI MacOS (SpoofDPI) Baslatiliyor"
echo "==========================================="
echo "Bu pencere acik kaldigi surece Discord ve tum yasakli sitelere"
echo "erisebilirsiniz. Oyun pinginiz (UDP) ETKILENMEZ!"
echo "Discord'u normal sekilde baslatin."
echo "Iptal etmek icin pencereyi kapatin veya Ctrl+C yapin."
echo "-------------------------------------------"

# Sudo yetkisi gerekebilir ag ayarlari icin
sudo /opt/homebrew/opt/spoofdpi/bin/spoofdpi --auto-configure-network --dns-mode doh --no-tui
