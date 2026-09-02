<div align="center">

<img src="https://img.shields.io/badge/macOS-PRO_Glassmorphism_Dashboard-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-Bypass_%26_Ping_Shield-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/SpoofDPI-Deep_Packet_Bypass-10B981?style=for-the-badge&logo=shield&logoColor=white"/>

# 🎮 Discord DPI Bypass & Optimizer PRO for macOS

**macOS için Discord kısıtlamalarını kaldıran, sıfır ek ping ile çalışan, yeni nesil Cyberpunk & Glassmorphism kontrol paneli ve Docker desteği.**

*Oyun içinde (UDP) sıfır ek ping, canlı Discord ping monitörü, 120 FPS GPU hızlandırmalı masaüstü arayüzü ve Docker altyapısı.*

</div>

---

## 🌟 Neler Sunuyor? (PRO v6.0)

- 🎨 **Next-Gen Cyberpunk & Glassmorphism Dashboard**: Discord Blurple, neon zümrüt yeşili ve koyu cam efektleri, ambient ışık orbları ve ses efektleri.
- ⚡ **Tek Tıkla Akıllı Başlatma**: `Cloudflare WARP → SpoofDPI → Discord Web App` sırasını tek tuşla, hatasız arka planda yönetir.
- 🔐 **Gelişmiş Sudo / Şifre Yönetimi**: Şifrenizi ister terminalden açılışta 1 kere girin, ister arayüzdeki şifre kartından test edip kaydedin.
- 🚀 **Mac Açılışında Otomatik Başlat**: Tek anahtarla bilgisayar açıldığında otomatik başlama desteği (`LaunchAgents`).
- 📊 **Canlı Discord Ping & Ağ Monitörü**: `discord.com` sunucularına olan anlık milisaniye gecikmenizi canlı çizen dinamik Bezier eğrisi grafiği.
- 📜 **Canlı Terminal Günlüğü**: Arka planda çalışan komutların anlık çıktılarını gösteren renk kodlu konsol kutusu.
- 🎮 **Oyun Ping Koruması**: CS2, Valorant, LoL vb. oyunların kullandığı UDP paketleri yönlendirilmez, oyun pinginiz kesinlikle artmaz.
- 🐳 **Docker & Docker Compose Desteği**: İster yerel macOS uygulamasından çalıştırın, ister Docker container üzerinden (`docker compose up -d`).

---

## 🚀 Başlatma & Kullanım

### 1. Yerel Kontrol Paneli (Önerilen)

Sadece **`Baslat.command`** dosyasına çift tıklayın!

1. Terminal açılır ve SpoofDPI için yönetici şifrenizi ister (ister terminalde girin, ister Enter'a basıp panelden girin).
2. Modern, animasyonlu kontrol paneli bağımsız bir masaüstü penceresi olarak açılır.
3. **`⚡ SİSTEMİ BAŞLAT (TEK TIK)`** butonuna tıklayın:
   - 🛡️ WARP bağlanır
   - 🟢 SpoofDPI bypass başlatılır
   - 💬 Discord ultra hızlı Web App modunda açılır

---

### 2. Docker ile Başlatma

Eğer Docker Desktop kullanıyorsanız veya sistemi container içinde çalıştırmak isterseniz:

```bash
# Docker Compose ile başlat
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

## 📋 Gereksinimler

```bash
# 1. Homebrew paketleri
brew install --cask cloudflare-warp
brew install spoofdpi
brew install --cask brave-browser
```

---

## 📁 Proje Dosya Yapısı

```
DPI-for-macos/
├── Baslat.command              # 🚀 PRO Dashboard Başlatıcı (Çift tıklayın!)
├── discord_launcher.py         # 🖥️ PRO Dashboard Motoru & Web App Engine
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
- Cloudflare WARP resmi ve güvenli DNS/VPN altyapısı sunar.

---

## 📄 Lisans

MIT License © 2026 Cnek00
