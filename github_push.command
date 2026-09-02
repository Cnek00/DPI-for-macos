#!/bin/bash
# ============================================================
#   GitHub'a Push Scripti
#   Bu script repoyu GitHub'a yükler
# ============================================================

echo ""
echo "🔐 GitHub kimlik bilgilerinizi girin:"
echo ""
read -p "  GitHub kullanıcı adı: " GH_USER
read -sp "  GitHub Personal Access Token (PAT): " GH_TOKEN
echo ""
echo ""

cd "$(dirname "$0")"

# Remote URL'yi güncelle
git remote set-url origin "https://${GH_USER}:${GH_TOKEN}@github.com/Cnek00/DPI-for-macos.git"

echo "📤 GitHub'a yükleniyor..."
git push -u origin main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Başarıyla yüklendi!"
    echo "   https://github.com/Cnek00/DPI-for-macos"
else
    echo ""
    echo "❌ Yükleme başarısız!"
    echo "   GitHub'da Personal Access Token oluşturduğunuzdan emin olun:"
    echo "   https://github.com/settings/tokens"
fi

# Token'ı temizle (güvenlik için)
git remote set-url origin "https://github.com/Cnek00/DPI-for-macos.git"
echo ""
read -p "Pencereyi kapatmak için Enter'a basın..."
