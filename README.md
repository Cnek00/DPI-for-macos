<div align="center">

<img src="https://img.shields.io/badge/macOS-Native_CustomTkinter_GUI-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-Bypass_%26_Ping_Shield-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/SpoofDPI-Deep_Packet_Bypass-10B981?style=for-the-badge&logo=shield&logoColor=white"/>

# 🎮 Discord DPI Bypass & Optimizer PRO for macOS

**macOS için Discord kısıtlamalarını kaldıran, %100 yerel Python masaüstü uygulaması ve Docker container desteği sunan yeni nesil bypass sistemi.**

*Oyun içinde (UDP) sıfır ek ping, canlı Discord ping monitörü, yerel masaüstü arayüzü ve Docker desteği.*

</div>

---

## 🌟 Özellikler (v5.0 Native GUI & Docker)

- 🖥️ **%100 Yerel Masaüstü GUI (CustomTkinter)**: Web veya tarayıcı bağımlılığı olmaksızın, tamamen yerel Python penceresi olarak çalışan Discord temalı modern arayüz.
- 🐳 **Docker & Docker Compose Desteği**: İster yerel macOS uygulamasından çalıştırın, ister Docker container üzerinden (`docker compose up -d`).
- ⚡ **Tek Tıkla Otomatik Başlatma**: `Cloudflare WARP → SpoofDPI → Discord` sırasını tek tuşla, arka planda sırayla yönetir.
- 🔐 **Akıllı Sudo / Şifre Yönetimi**: Başlangıçta terminalden veya panel içerisinden şifrenizi girin, sistem arka planda güvenle yetkilendirsin.
- 🚀 **Mac Açılışında Otomatik Başlat**: Tek anahtarla bilgisayar açıldığında otomatik başlama desteği (`LaunchAgents`).
- 📊 **Canlı Discord Ping Monitörü**: `discord.com` sunucularına olan anlık milisaniye gecikmesini gerçek zamanlı takip eder.
- 🎮 **Oyun Ping Koruması**: CS2, Valorant, LoL vb. oyunların kullandığı UDP paketleri yönlendirilmez, oyun pinginiz kesinlikle artmaz.

---

## 🚀 Başlatma Yöntemleri

### 1. Yerel Masaüstü Arayüzü (Önerilen)

Sadece **`Baslat.command`** dosyasına çift tıklayın!

1. Terminal açılır, gerekli kütüphaneleri otomatik kontrol eder.
2. Yönetici şifrenizi girmeniz istenir (isterseniz Enter ile atlayıp panelden de girebilirsiniz).
3. **Yerel CustomTkinter Masaüstü Penceresi** açılır.
4. **`⚡ SİSTEMİ BAŞLAT (TEK TIK)`** butonuna tıklayarak tüm sistemi devreye alın.

---

### 2. Docker ile Başlatma

Eğer Docker Desktop kullanıyorsanız veya sistemi container içinde çalıştırmak isterseniz:

```bash
# 1. Docker Compose ile arka planda başlat
docker compose up -d

# Veya tek tıkla başlatmak için:
./docker_start.command
```

**Konteyner Portları:**
- **HTTP/HTTPS DPI Proxy**: `http://127.0.0.1:8080`
- **SOCKS5 Proxy**: `socks5://127.0.0.1:40000`

Durdurmak için:
```bash
docker compose down
```

---

### 3. Klasik Manuel Komut Dosyaları

Terminal üzerinden tek tek çalıştırmak isterseniz:

```
1️⃣  Warp_Ayarlari.command     → WARP VPN modunu seç ve bağlan
2️⃣  Mac_GoodbyeDPI.command    → SpoofDPI DPI atlamasını başlat  
3️⃣  Discord_Uygulamasi.command → Brave / Tarayıcı üzerinden Discord'u aç
```

---

## 📋 Manuel Kurulum Gereksinimleri

```bash
# 1. Homebrew paketleri
brew install --cask cloudflare-warp
brew install spoofdpi
brew install --cask brave-browser

# 2. Python CustomTkinter (Baslat.command otomatik kurar)
pip3 install customtkinter
```

---

## 📁 Proje Dosya Yapısı

```
DPI-for-macos/
├── Baslat.command              # 🚀 Yerel Masaüstü GUI Başlatıcı
├── discord_launcher.py         # 🖥️ %100 Yerel Python CustomTkinter Arayüzü
├── docker_start.command        # 🐳 1-Tık Docker Başlatıcı
├── Dockerfile                  # 📦 Çok Aşamalı Hafif Docker Kalıbı
├── docker-compose.yml          # 🐳 Docker Compose Yapılandırması
├── docker/
│   └── entrypoint.sh          # ⚙️ Docker Başlangıç Betiği
├── Warp_Ayarlari.command       # 🛡️ WARP Ayar Betiği
├── Mac_GoodbyeDPI.command      # 🟢 SpoofDPI Başlatıcı Betiği
├── Discord_Uygulamasi.command  # 💬 Discord Başlatıcı Betiği
├── github_push.command         # 📤 GitHub Depo Güncelleme Aracı
└── README.md                   # 📖 Dokümantasyon
```

---

## 🔒 Güvenlik

- Şifreniz asla dosyalara kaydedilmez; yalnızca oturum süresince bellekte `sudo -S` için tutulur.
- SpoofDPI yalnızca DNS ve HTTPS SNI paketlerini fragmente eder; verilerinizi şifrelemez veya kaydetmez.

---

## 📄 Lisans

MIT License © 2026 Cnek00
