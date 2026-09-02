<div align="center">

<img src="https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/Cloudflare-F38020?style=for-the-badge&logo=cloudflare&logoColor=white"/>

# 🎮 Discord DPI Bypass for macOS

**macOS için Discord ping sorununu tamamen çözen otomatik DPI atlama sistemi**

*Oyun içinde sıfır ekstra ping, Discord'da kesintisiz bağlantı*

</div>

---

## 🤔 Bu Nedir?

Bazı internet servis sağlayıcıları (ISP'ler) **DPI (Deep Packet Inspection)** yöntemiyle Discord trafiğini kısıtlar veya yavaşlatır. Bu sistem, **SpoofDPI** aracını ve **Cloudflare WARP** VPN'ini birlikte kullanarak:

- Discord bağlantısını kısıtlamadan geçirir
- Oyun trafiğinizi (UDP) **hiç etkilemez**
- Ekstra ping eklemez
- Kolay bir GUI ile yönetilir

---

## 📋 Gereksinimler

Sistemi kullanmadan önce aşağıdaki yazılımların kurulu olması gerekir:

### 1. Homebrew (macOS Paket Yöneticisi)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Cloudflare WARP
```bash
brew install --cask cloudflare-warp
```
> Kurulumdan sonra WARP uygulamasını bir kez açın ve hesap oluşturun (ücretsiz).

### 3. SpoofDPI
```bash
brew install spoofdpi
```

### 4. Python 3 (Tkinter ile)
```bash
brew install python-tk
```

### 5. Brave Browser *(önerilen)*
```bash
brew install --cask brave-browser
```
> Discord'u Brave Browser üzerinden web uygulaması olarak çalıştırır. Daha iyi performans sunar.

---

## 🚀 Kurulum

```bash
# Repoyu klonla
git clone https://github.com/Cnek00/DPI-for-macos.git
cd DPI-for-macos

# Çalıştırma izni ver
chmod +x Baslat.command
chmod +x Warp_Ayarlari.command
chmod +x Mac_GoodbyeDPI.command
chmod +x Discord_Uygulamasi.command
```

---

## 🖥️ Kullanım

### Otomatik Yöntem (Önerilen)

`Baslat.command` dosyasına çift tıklayın. Bu script:
1. Tüm bağımlılıkları kontrol eder
2. Python GUI başlatıcısını açar
3. GUI üzerinden tüm sistemi tek tuşla yönetebilirsiniz

### Manuel Yöntem (Sırasıyla)

Eğer GUI kullanmak istemezseniz, aşağıdaki dosyaları **sırasıyla** çalıştırın:

```
1️⃣  Warp_Ayarlari.command     → WARP VPN modunu seç ve bağlan
2️⃣  Mac_GoodbyeDPI.command    → SpoofDPI DPI atlama başlat  
3️⃣  Discord_Uygulamasi.command → Brave üzerinden Discord'u aç
```

> ⚠️ **Önemli:** Sıra kritiktir. VPN önce aktif olmalı, ardından DPI atlama başlamalı.

---

## 🎨 GUI Özellikleri

<div align="center">

| Özellik | Açıklama |
|---------|----------|
| 🚀 Tek Tıkla Başlatma | Tüm sistemi sırasıyla otomatik başlatır |
| 📊 Canlı Durum | WARP ve SpoofDPI durumu gerçek zamanlı gösterilir |
| 📋 Adım Göstergesi | Hangi adımın tamamlandığını görir |
| ⚡ WARP Modu | VPN veya Proxy modu arasında seçim |
| 📜 Sistem Günlüğü | Tüm işlemler kayıt altına alınır |
| ⏱️ Çalışma Süresi | Sistemin ne kadar süredir aktif olduğunu gösterir |
| 🔧 Hızlı İşlemler | Tek tek hizmetleri başlatıp durdurabilirsiniz |

</div>

---

## ⚙️ WARP Modları

### 🛡️ Tam VPN Modu (`warp`)
- Tüm cihaz trafiği Cloudflare üzerinden geçer
- En güçlü koruma
- Tüm uygulamalar korunur

### 🔌 Proxy Modu (`proxy`)
- Sadece belirli uygulamalar proxy üzerinden bağlanır
- Port: `40000` üzerinden SOCKS5 proxy
- Daha hafif, oyun UDP trafiğine etkisi minimum

---

## 🛠️ Sorun Giderme

### SpoofDPI başlamıyor
```bash
# sudo yetkisi gerekiyor, şifreni gir
sudo /opt/homebrew/opt/spoofdpi/bin/spoofdpi --auto-configure-network --dns-mode doh --no-tui
```

### WARP bağlanmıyor
```bash
# WARP servisini yeniden başlat
warp-cli disconnect
warp-cli connect
```

### Tkinter bulunamadı
```bash
# python.org'dan Python indir veya:
brew install python-tk
```

### Brave Browser üzerinden Discord açılmıyor
```bash
# Brave yolunu kontrol et
ls /Applications/Brave\ Browser.app
# Yoksa:
brew install --cask brave-browser
```

---

## 📁 Dosya Yapısı

```
DPI-for-macos/
├── Baslat.command              # ← Ana başlatıcı (bunu çift tıkla!)
├── discord_launcher.py         # Python GUI uygulaması
├── Warp_Ayarlari.command       # WARP ayar scripti
├── Mac_GoodbyeDPI.command      # SpoofDPI başlatma scripti
├── Discord_Uygulamasi.command  # Discord açma scripti
└── README.md
```

---

## 🔒 Güvenlik Notu

- `Mac_GoodbyeDPI.command` ağ ayarlarını değiştirmek için `sudo` yetkisi ister — bu normaldir
- WARP, Cloudflare'in resmi uygulamasıdır ve güvenilirdir
- SpoofDPI yalnızca DNS/HTTPS sorgularını manipüle eder, trafiği şifre çözmez

---

## 📄 Lisans

MIT License © 2025 Cnek00

---

<div align="center">

⭐ **Bu projeyi beğendiyseniz star vermeyi unutmayın!**

[GitHub'da Görüntüle](https://github.com/Cnek00/DPI-for-macos) · [Sorun Bildir](https://github.com/Cnek00/DPI-for-macos/issues)

</div>
