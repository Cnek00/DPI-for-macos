#!/bin/bash
clear
echo "================================================="
echo "        Cloudflare WARP Ayar Yoneticisi"
echo "================================================="
echo "1) WARP'i Tam VPN Modunda Baslat (Tum Cihaz Korunur)"
echo "2) WARP'i Proxy Modunda Baslat (Sadece Secili Uygulamalar - Port 40000)"
echo "3) WARP'i Tamamen Kapat (Disconnect)"
echo "4) Cikis"
echo "================================================="
read -p "Seciminiz (1-4): " secim

case $secim in
    1)
        echo "WARP tam VPN moduna aliniyor..."
        warp-cli mode warp
        warp-cli connect
        echo "Basariyla baglanildi!"
        ;;
    2)
        echo "WARP proxy moduna aliniyor (Port: 40000)..."
        warp-cli mode proxy
        warp-cli proxy port 40000
        warp-cli connect
        echo "Proxy basariyla acildi! (SOCKS5 127.0.0.1:40000)"
        ;;
    3)
        echo "WARP kapatiliyor..."
        warp-cli disconnect
        echo "WARP baglantisi kesildi."
        ;;
    4)
        echo "Cikiliyor..."
        ;;
    *)
        echo "Gecersiz secim!"
        ;;
esac

echo ""
read -p "Pencereyi kapatmak icin Enter'a basin..."
