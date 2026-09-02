<div align="center">

<img src="https://img.shields.io/badge/macOS-Apple_Silicon_%26_Intel-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-Bypass_%26_Ping_Shield-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/Cloudflare_WARP-Zero_Lag-F38020?style=for-the-badge&logo=cloudflare&logoColor=white"/>
<img src="https://img.shields.io/badge/SpoofDPI-Deep_Packet_Bypass-10B981?style=for-the-badge&logo=shield&logoColor=white"/>

# 🎮 Discord DPI Bypass & Optimizer PRO for macOS

**macOS için Discord kısıtlamalarını kaldıran, oyun pingini (UDP) kesinlikle etkilemeyen yeni nesil kontrol paneli.**

*Sıfır ek ping, canlı gecikme monitörü, tek tıkla otomatik başlatma ve modern Cyberpunk/Glassmorphism arayüz.*

</div>

---

## 🌟 Neler Yeni? (v4.0 PRO)

- 🎨 **Modern Cyberpunk / Glassmorphism Kontrol Paneli**: Animasyonlu orblar, canlı grafikler ve şık Discord estetiği.
- ⚡ **Tek Tıkla Akıllı Başlatma**: `WARP → SpoofDPI → Discord Web App` sırasını otomatik olarak ve hatasız yönetir.
- 🔐 **Gelişmiş Şifre (Sudo) Yönetimi**: Şifrenizi ister terminalden açılışta 1 kere girin, ister arayüzdeki şifre kartından test edip kaydedin.
- 🚀 **Mac Açılışında Otomatik Başlat**: Tek anahtarla bilgisayar açıldığında otomatik devreye girme desteği (LaunchAgent).
- 📊 **Canlı Discord Ping & Ağ Monitörü**: Discord sunucularına olan anlık milisaniye gecikmenizi canlı çizen dinamik grafik.
- 📜 **Canlı Terminal Günlüğü**: Arka planda ne olup bittiğini anlık gösteren renk kodlu konsol.
- 🎮 **Oyun Ping Koruması**: UDP trafiği yönlendirilmez, CS2, Valorant, LoL veya diğer oyunlardaki pinginiz asla artmaz.

---

## 📋 Gereksinimler & Kurulum

Sistemi kullanmadan önce aşağıdaki paketlerin kurulu olduğundan emin olun:

### 1. Homebrew (macOS Paket Yöneticisi)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Cloudflare WARP & SpoofDPI
```bash
# Cloudflare WARP
brew install --cask cloudflare-warp

# SpoofDPI
brew install spoofdpi

# Brave Browser (Önerilen - En düşük gecikme ve web app modu için)
brew install --cask brave-browser
```

---

## 🚀 Başlatma & Kullanım

### 1. Otomatik & Önerilen Yöntem (PRO Dashboard)

Sadece **`Baslat.command`** dosyasına çift tıklayın!

1. Terminal açılır ve SpoofDPI için yönetici şifrenizi ister (ister terminalde girin, ister Enter'a basıp panelden girin).
2. Modern, animasyonlu kontrol paneli bağımsız bir masaüstü penceresi olarak açılır.
3. **`🚀 SİSTEMİ BAŞLAT (TEK TIK)`** butonuna tıklayın:
   - 🛡️ WARP bağlanır
   - 🟢 SpoofDPI bypass başlatılır
   - 💬 Discord ultra hızlı Web App modunda açılır

---

### 2. Manuel Komut Dosyaları (İsteğe Bağlı)

Eğer komut satırından tek tek çalıştırmak isterseniz orijinal dosyalar korunmuştur:

```
1️⃣  Warp_Ayarlari.command     → WARP VPN modunu seç ve bağlan
2️⃣  Mac_GoodbyeDPI.command    → SpoofDPI DPI atlamasını başlat  
3️⃣  Discord_Uygulamasi.command → Brave üzerinden Discord'u aç
```

---

## ⚙️ WARP Modları

| Mod | Açıklama |
|---|---|
| **🛡️ Tam VPN (`warp`)** | Tüm cihaz trafiği Cloudflare güvenli tünelinden geçer. |
| **🔌 SOCKS5 Proxy (`proxy`)** | Port 40000 üzerinden yerel proxy açar, sistem genelini etkilemez. |

---

## 📁 Proje Dosya Yapısı

```
DPI-for-macos/
├── Baslat.command              # 🚀 Ana başlatıcı (Çift tıklayın!)
├── discord_launcher.py         # 🖥️ PRO Dashboard Motoru & Web App
├── Warp_Ayarlari.command       # 🛡️ WARP Ayarları
├── Mac_GoodbyeDPI.command      # 🟢 SpoofDPI Başlatıcı
├── Discord_Uygulamasi.command  # 💬 Discord Başlatıcı
├── github_push.command         # 📤 GitHub Güncelleme Aracı
└── README.md                   # 📖 Dokümantasyon
```

---

## 🔒 Güvenlik

- Şifreniz asla kalıcı olarak dosyalara yazılmaz, sadece RAM üzerinde `sudo -S` oturumu için tutulur.
- SpoofDPI açık kaynaklı bir DPI bypass aracıdır, trafiği çözmez veya kaydetmez.
- Cloudflare WARP resmi ve güvenli DNS/VPN altyapısı sunar.

---

## 📄 Lisans

MIT License © 2026 Cnek00
