#!/bin/bash
# ============================================================
#   🚀 GITHUB TEK TIKLA GİRİŞ & YÜKLEME
# ============================================================

clear
echo "============================================================"
echo "  🚀 GITHUB HESABINA BAĞLANMA & YÜKLEME"
echo "============================================================"
echo ""
echo "  1) Birazdan ekranda 8 haneli bir kod (örn: 1234-ABCD) görünecek."
echo "  2) Enter'a basınca tarayıcında GitHub sayfası açılacak."
echo "  3) Kodu sayfaya yapıştırıp 'Authorize' (Yetkilendir) de."
echo "  4) Tarayıcıyı kapattığında dosyaların otomatik yüklenecek!"
echo ""
echo "============================================================"
echo ""

/opt/homebrew/bin/gh auth login --web -h github.com -p https --git-protocol https

/opt/homebrew/bin/gh auth setup-git

cd "$(dirname "$0")"

echo ""
echo "📤 Dosyalar GitHub'a yükleniyor..."
git push -u origin main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "  🎉 TEBRİKLER! BAŞARIYLA YÜKLENDİ!"
    echo "  🔗 https://github.com/Cnek00/DPI-for-macos"
    echo "============================================================"
else
    echo ""
    echo "❌ Yükleme tamamlanamadı."
fi

echo ""
read -p "Kapatmak için Enter'a basın..."
