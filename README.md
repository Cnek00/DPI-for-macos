<div align="center">

<img src="https://img.shields.io/badge/macOS-DPI_Bypass-000000?style=for-the-badge&logo=apple&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-Access-5865F2?style=for-the-badge&logo=discord&logoColor=white"/>
<img src="https://img.shields.io/badge/WARP-Cloudflare-10B981?style=for-the-badge&logo=cloudflare&logoColor=white"/>
<img src="https://img.shields.io/badge/SpoofDPI-Enabled-0EA5E9?style=for-the-badge&logo=shield&logoColor=white"/>

# DPI for macOS

A macOS automation toolkit for improving Discord access and reducing DPI-related traffic filtering using Cloudflare WARP, SpoofDPI, and a custom launcher dashboard.

</div>

---

## Overview

This project is built for macOS users who want a practical and streamlined workflow to:

- launch Discord through a browser/web-app mode optimized for access
- connect to Cloudflare WARP
- start SpoofDPI to help bypass DPI and packet inspection
- manage the flow from a custom desktop-style dashboard
- run the full setup locally or with Docker

The tool combines Python automation, shell scripts, and a graphical launcher to provide a simple one-click experience for network optimization and Discord access.

---

## Features

- Modern macOS launcher dashboard
- One-click startup flow: WARP → SpoofDPI → Discord
- Cloudflare WARP support with VPN or proxy mode
- SpoofDPI start/stop controls
- Discord launch support via Brave browser app mode or native app
- Optional LaunchAgent startup support
- Docker and Docker Compose support
- Real-time log output and status monitoring
- Manual helper scripts for direct control

---

## Project Structure

```bash
DPI-for-macos/
├── Baslat.command              # Main launcher script
├── discord_launcher.py         # Python automation and dashboard logic
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Docker Compose setup
├── docker/
│   └── entrypoint.sh          # Docker container startup script
├── docker_start.command        # Docker startup helper
├── Warp_Ayarlari.command       # WARP configuration helper
├── Mac_GoodbyeDPI.command      # SpoofDPI startup helper
├── Discord_Uygulamasi.command  # Discord launch helper
├── github_push.command         # GitHub upload helper
├── README.md                   # Project documentation
├── LICENSE                     # License file (if present)
└── .gitignore                  # Git ignore rules (if present)
```

---

## Requirements

This project targets macOS and assumes the following tools are available:

- macOS
- Homebrew
- Cloudflare WARP
- SpoofDPI
- Brave Browser (recommended)
- Docker Desktop (optional)

Install core dependencies with:

```bash
brew install --cask cloudflare-warp
brew install spoofdpi
brew install --cask brave-browser
```

Confirm Docker is installed if needed:

```bash
docker --version
```

---

## Quick Start

### Option 1: Use the desktop launcher

Double-click the launcher script:

```bash
./Baslat.command
```

This opens the dashboard and allows you to:

1. connect to WARP
2. start SpoofDPI
3. launch Discord in an optimized browser/app mode

---

### Option 2: Use the helper scripts manually

Run the scripts individually:

```bash
./Warp_Ayarlari.command
./Mac_GoodbyeDPI.command
./Discord_Uygulamasi.command
```

This gives you direct control over each service.

---

### Option 3: Run with Docker

Start the service stack:

```bash
docker compose up -d
```

Or use the helper script:

```bash
./docker_start.command
```

Stop the container stack:

```bash
docker compose down
```

---

## How It Works

The workflow is intentionally simple:

1. Cloudflare WARP is enabled in either VPN or proxy mode.
2. SpoofDPI is started to help bypass DPI and packet inspection.
3. Discord is launched in a browser-based app flow or native app mode.
4. Status and command output are displayed inside the dashboard for monitoring.

This creates a single environment where the user can launch the required network tools without juggling several commands manually.

---

## Security Notes

- Administrator password is only used temporarily in the sudo flow and is not stored permanently.
- SpoofDPI is a traffic manipulation tool; use it responsibly and in accordance with local policies and platform rules.
- Cloudflare WARP is an official service used for routing, DNS, and secure network access.

> This project is intended for local experimentation and network troubleshooting on macOS. Always follow your local environment policies and platform terms.

---

## Troubleshooting

### Discord does not open

- Ensure Brave is installed.
- Launch Discord from the helper script again.
- Check whether the native Discord app exists in `/Applications/Discord.app`.

### WARP is not connected

- Confirm Cloudflare WARP is installed.
- Run the WARP helper script and choose the correct mode.
- Verify the required permissions are available.

### SpoofDPI does not start

- Confirm the `spoofdpi` binary is available in your environment.
- Re-run the script after entering the required admin password.
- Review the output in the dashboard for detailed errors.

---

## License

This project is provided as-is for personal and educational use.

If you publish it publicly, make sure to include the proper project license and credit the original author.

---

## Author

Cnek00

---

## GitHub Setup

If you want to initialize the repository and push it to GitHub, use:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Cnek00/DPI-for-macos.git
git push -u origin main
```

If you are only updating an existing repository README:

```bash
git add README.md
git commit -m "Update README"
git push origin main
```

---

## Disclaimer

This project is a macOS utility for testing and experimentation. It does not guarantee access in every network environment, and results may vary depending on system configuration, ISP, firewall, and network policy.
