#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  DISCORD DPI BYPASS & OPTIMIZER — macOS PRO DASHBOARD v6.0
  Next-Gen Cyberpunk & Glassmorphism Web-Engine Desktop App
  Zero Dependencies • 120 FPS GPU Rendered • Gaming UDP Ping-Shield
═══════════════════════════════════════════════════════════════════════════════
"""

import http.server
import socketserver
import json
import subprocess
import threading
import time
import os
import sys
import socket
import urllib.parse
from pathlib import Path
import plistlib
import datetime

PORT = 49221
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
LAUNCHAGENT = Path.home() / "Library/LaunchAgents/com.discord.dpibypass.plist"
PLIST_LABEL = "com.discord.dpibypass"

# Global System State
STATE = {
    "warp_installed": False,
    "warp_status": "disconnected",  # connected, connecting, disconnected
    "warp_mode": "warp",           # warp, proxy
    "spoofdpi_installed": False,
    "spoofdpi_running": False,
    "brave_installed": False,
    "discord_installed": False,
    "sudo_cached": False,
    "sudo_password": "",
    "startup_enabled": False,
    "running_all": False,
    "step": 0,                     # 0: idle, 1: warp, 2: spoofdpi, 3: discord, 4: active
    "uptime_seconds": 0,
    "is_active": False,
    "logs": [],
    "pings": []
}

STATE_LOCK = threading.Lock()
SPOOFDPI_PROC = None


def add_log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = {"time": timestamp, "msg": msg, "level": level}
    with STATE_LOCK:
        STATE["logs"].append(entry)
        if len(STATE["logs"]) > 250:
            STATE["logs"] = STATE["logs"][-250:]


def run_cmd(cmd, sudo_pass=None, timeout=12):
    try:
        if sudo_pass and cmd[0] == "sudo":
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            out, err = proc.communicate(input=sudo_pass + "\n", timeout=timeout)
            return proc.returncode == 0, out.strip(), err.strip()
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def check_sudo_cached():
    ok, _, _ = run_cmd(["sudo", "-n", "true"])
    return ok


def test_sudo_password(password):
    if not password:
        return False
    ok, _, _ = run_cmd(["sudo", "-S", "-k", "true"], sudo_pass=password, timeout=4)
    return ok


def get_warp_status():
    ok, out, _ = run_cmd(["warp-cli", "status"])
    if not ok:
        return "disconnected"
    if "Connected" in out:
        return "connected"
    if "Connecting" in out:
        return "connecting"
    return "disconnected"


def is_spoofdpi_running():
    ok, out, _ = run_cmd(["pgrep", "-f", "spoofdpi"])
    return ok and len(out) > 0


def ping_host(host="discord.com"):
    try:
        ok, out, _ = run_cmd(["ping", "-c", "1", "-W", "1500", host], timeout=2)
        if ok and "time=" in out:
            part = out.split("time=")[1].split(" ")[0]
            return float(part)
        return None
    except Exception:
        return None


def poll_system_state():
    while True:
        try:
            w_inst = run_cmd(["which", "warp-cli"])[0]
            s_inst = Path("/opt/homebrew/opt/spoofdpi/bin/spoofdpi").exists() or run_cmd(["which", "spoofdpi"])[0]
            b_inst = Path("/Applications/Brave Browser.app").exists()
            d_inst = Path("/Applications/Discord.app").exists()
            w_stat = get_warp_status()
            s_run = is_spoofdpi_running()
            s_cache = check_sudo_cached() or (STATE["sudo_password"] != "")
            startup = LAUNCHAGENT.exists()

            ms = ping_host("discord.com")

            with STATE_LOCK:
                STATE["warp_installed"] = w_inst
                STATE["spoofdpi_installed"] = s_inst
                STATE["brave_installed"] = b_inst
                STATE["discord_installed"] = d_inst
                STATE["warp_status"] = w_stat
                STATE["spoofdpi_running"] = s_run
                STATE["sudo_cached"] = s_cache
                STATE["startup_enabled"] = startup
                if ms is not None:
                    STATE["pings"].append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "ms": round(ms, 1)})
                    if len(STATE["pings"]) > 30:
                        STATE["pings"] = STATE["pings"][-30:]

                if w_stat == "connected" and s_run:
                    STATE["is_active"] = True
                    STATE["step"] = 4
                elif w_stat == "connected" or s_run:
                    STATE["is_active"] = False
                else:
                    STATE["is_active"] = False
                    if not STATE["running_all"]:
                        STATE["step"] = 0

            if STATE["is_active"]:
                with STATE_LOCK:
                    STATE["uptime_seconds"] += 2

        except Exception:
            pass
        time.sleep(2)


# Action Handlers
def do_warp_connect(mode="warp"):
    add_log(f"Cloudflare WARP bağlantısı kuruluyor (Mod: {mode.upper()})...", "CMD")
    run_cmd(["warp-cli", "mode", mode])
    if mode == "proxy":
        run_cmd(["warp-cli", "proxy", "port", "40000"])
    ok, out, err = run_cmd(["warp-cli", "connect"])
    time.sleep(1.5)
    stat = get_warp_status()
    if stat in ("connected", "connecting"):
        add_log("✓ Cloudflare WARP başarıyla bağlandı.", "SUCCESS")
        return True
    else:
        add_log(f"⚠ WARP bağlanamadı: {err or out}", "ERROR")
        return False


def do_warp_disconnect():
    add_log("Cloudflare WARP bağlantısı kesiliyor...", "CMD")
    run_cmd(["warp-cli", "disconnect"])
    time.sleep(1)
    add_log("Cloudflare WARP bağlantısı kapatıldı.", "WARN")
    return True


def do_spoofdpi_start():
    global SPOOFDPI_PROC
    if is_spoofdpi_running():
        add_log("✓ SpoofDPI zaten aktif çalışıyor.", "INFO")
        return True

    add_log("SpoofDPI Engine başlatılıyor...", "CMD")
    spoof_bin = "/opt/homebrew/opt/spoofdpi/bin/spoofdpi"
    if not Path(spoof_bin).exists():
        spoof_bin = "spoofdpi"

    cmd_args = [spoof_bin, "--auto-configure-network", "--dns-mode", "doh", "--no-tui"]

    pwd = STATE["sudo_password"]
    if pwd:
        try:
            def bg_runner():
                global SPOOFDPI_PROC
                SPOOFDPI_PROC = subprocess.Popen(
                    ["sudo", "-S"] + cmd_args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                SPOOFDPI_PROC.stdin.write(pwd + "\n")
                SPOOFDPI_PROC.stdin.flush()
                add_log("✓ SpoofDPI arka planda yetkilendirildi.", "SUCCESS")
                while SPOOFDPI_PROC and SPOOFDPI_PROC.poll() is None:
                    line = SPOOFDPI_PROC.stdout.readline()
                    if line and ("addr" in line or "listen" in line or "DPI" in line):
                        add_log(f"[SpoofDPI] {line.strip()}", "INFO")
                    time.sleep(0.5)

            threading.Thread(target=bg_runner, daemon=True).start()
            time.sleep(2)
            if is_spoofdpi_running():
                add_log("✓ SpoofDPI aktif ve ağ trafiğini optimize ediyor.", "SUCCESS")
                return True
        except Exception as e:
            add_log(f"SpoofDPI hata: {e}", "ERROR")

    script_path = SCRIPT_DIR / "Mac_GoodbyeDPI.command"
    apple_script = f'tell application "Terminal" to do script "bash \\"{script_path}\\""'
    run_cmd(["osascript", "-e", apple_script])
    time.sleep(2.5)
    return is_spoofdpi_running()


def do_spoofdpi_stop():
    global SPOOFDPI_PROC
    add_log("SpoofDPI durduruluyor...", "CMD")
    pwd = STATE["sudo_password"]
    if pwd:
        run_cmd(["sudo", "-S", "pkill", "-f", "spoofdpi"], sudo_pass=pwd)
    else:
        run_cmd(["sudo", "pkill", "-f", "spoofdpi"])
    if SPOOFDPI_PROC:
        try:
            SPOOFDPI_PROC.terminate()
        except Exception:
            pass
        SPOOFDPI_PROC = None
    time.sleep(1)
    add_log("SpoofDPI durduruldu.", "WARN")
    return True


def do_launch_discord():
    add_log("Discord başlatılıyor...", "CMD")
    if Path("/Applications/Brave Browser.app").exists():
        subprocess.Popen([
            "open", "-na", "Brave Browser",
            "--args", "--app=https://discord.com/channels/@me"
        ])
        add_log("✓ Discord Brave Web App modunda açıldı.", "SUCCESS")
        return True
    elif Path("/Applications/Google Chrome.app").exists():
        subprocess.Popen([
            "open", "-na", "Google Chrome",
            "--args", "--app=https://discord.com/channels/@me"
        ])
        add_log("✓ Discord Chrome Web App modunda açıldı.", "SUCCESS")
        return True
    elif Path("/Applications/Discord.app").exists():
        subprocess.Popen(["open", "-a", "Discord"])
        add_log("✓ Discord masaüstü uygulaması açıldı.", "SUCCESS")
        return True
    else:
        subprocess.Popen(["open", "https://discord.com/channels/@me"])
        add_log("✓ Discord varsayılan tarayıcıda açıldı.", "SUCCESS")
        return True


def do_launch_all_sequence():
    with STATE_LOCK:
        if STATE["running_all"]:
            return
        STATE["running_all"] = True
        STATE["step"] = 1

    add_log("══════════ OTOMATİK BAŞLATMA SIRASI BAŞLADI ══════════", "CMD")
    
    # 1. WARP
    add_log("Adım 1/3: Cloudflare WARP bağlanıyor...", "INFO")
    w_ok = do_warp_connect(STATE["warp_mode"])
    time.sleep(1.5)
    
    with STATE_LOCK:
        STATE["step"] = 2

    # 2. SpoofDPI
    add_log("Adım 2/3: SpoofDPI bypass başlatılıyor...", "INFO")
    s_ok = do_spoofdpi_start()
    time.sleep(2)

    with STATE_LOCK:
        STATE["step"] = 3

    # 3. Discord
    add_log("Adım 3/3: Discord açılıyor...", "INFO")
    d_ok = do_launch_discord()
    time.sleep(1)

    with STATE_LOCK:
        STATE["running_all"] = False
        STATE["step"] = 4
        STATE["is_active"] = True

    add_log("══════════ SİSTEM HAZIR & DISCORD AKTİF ══════════", "SUCCESS")


def do_stop_all():
    add_log("══════════ TÜM HİZMETLER DURDURULUYOR ══════════", "WARN")
    do_spoofdpi_stop()
    time.sleep(0.5)
    do_warp_disconnect()
    with STATE_LOCK:
        STATE["is_active"] = False
        STATE["step"] = 0
        STATE["uptime_seconds"] = 0
    add_log("Tüm bypass servisleri başarıyla kapatıldı.", "WARN")


def set_startup(enable):
    launcher_path = SCRIPT_DIR / "Baslat.command"
    if enable:
        plist = {
            "Label": PLIST_LABEL,
            "ProgramArguments": ["/bin/bash", str(launcher_path)],
            "RunAtLoad": True,
            "KeepAlive": False,
        }
        LAUNCHAGENT.parent.mkdir(parents=True, exist_ok=True)
        with open(LAUNCHAGENT, "wb") as f:
            plistlib.dump(plist, f)
        run_cmd(["launchctl", "load", str(LAUNCHAGENT)])
        add_log("✓ Başlangıçta otomatik başlatma aktif edildi.", "SUCCESS")
    else:
        if LAUNCHAGENT.exists():
            run_cmd(["launchctl", "unload", str(LAUNCHAGENT)])
            LAUNCHAGENT.unlink()
        add_log("Başlangıçta otomatik başlatma kapatıldı.", "WARN")


# ═══════════════════════════════════════════════════════════════════════════════
#  NEXT-GEN CYBERPUNK & GLASSMORPHISM DASHBOARD (HTML/CSS/JS)
# ═══════════════════════════════════════════════════════════════════════════════
HTML_DASHBOARD = r"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Discord DPI Bypass Pro Dashboard</title>
<style>
:root {
  --bg: #07090e;
  --bg-card: rgba(15, 18, 30, 0.78);
  --bg-card-hover: rgba(24, 29, 48, 0.88);
  --bg-sub: rgba(9, 12, 20, 0.85);
  --border: rgba(255, 255, 255, 0.08);
  --border-active: rgba(88, 101, 242, 0.5);
  
  --blurple: #5865F2;
  --blurple-glow: rgba(88, 101, 242, 0.4);
  --blurple-dark: #4752C4;
  --blurple-light: #7983F5;
  
  --emerald: #10B981;
  --emerald-glow: rgba(16, 185, 129, 0.4);
  --amber: #F59E0B;
  --amber-glow: rgba(245, 158, 11, 0.4);
  --rose: #EF4444;
  --rose-glow: rgba(239, 68, 68, 0.4);
  --cyan: #00F0FF;
  --cyan-glow: rgba(0, 240, 255, 0.35);
  
  --text-main: #FFFFFF;
  --text-dim: #94A3B8;
  --text-muted: #64748B;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
  user-select: none;
}

body {
  background: var(--bg);
  color: var(--text-main);
  min-height: 100vh;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Dynamic Ambient Glow Orbs */
.orb {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(60px);
}

.orb-1 {
  top: -120px;
  left: -120px;
  width: 480px;
  height: 480px;
  background: radial-gradient(circle, rgba(88, 101, 242, 0.18) 0%, transparent 70%);
  animation: floatOrb 14s ease-in-out infinite alternate;
}

.orb-2 {
  bottom: -140px;
  right: -140px;
  width: 520px;
  height: 520px;
  background: radial-gradient(circle, rgba(0, 240, 255, 0.14) 0%, transparent 70%);
  animation: floatOrb 18s ease-in-out infinite alternate-reverse;
}

.orb-3 {
  top: 40%;
  left: 45%;
  width: 380px;
  height: 380px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
  animation: floatOrb 22s ease-in-out infinite alternate;
}

@keyframes floatOrb {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(50px, 40px) scale(1.15); }
}

/* App Header */
header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(7, 9, 14, 0.82);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--border);
  padding: 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.app-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #5865F2, #854CE6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 8px 24px var(--blurple-glow);
  position: relative;
}

.app-icon::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(88, 101, 242, 0.6), transparent);
  z-index: -1;
}

.logo-text h1 {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-text .badge-ver {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(88, 101, 242, 0.2);
  color: var(--blurple-light);
  border: 1px solid rgba(88, 101, 242, 0.35);
  font-weight: 700;
  letter-spacing: 0.5px;
}

.logo-text p {
  font-size: 12px;
  color: var(--text-dim);
  margin-top: 2px;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 14px;
}

.audio-btn {
  background: var(--bg-sub);
  border: 1px solid var(--border);
  color: var(--text-dim);
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.audio-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #FFF;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px;
  background: var(--bg-sub);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 10px var(--amber-glow);
  transition: all 0.3s ease;
}

.status-dot.active {
  background: var(--emerald);
  box-shadow: 0 0 14px var(--emerald-glow);
  animation: pulseDot 1.8s infinite;
}

.status-dot.error {
  background: var(--rose);
  box-shadow: 0 0 12px var(--rose-glow);
}

@keyframes pulseDot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.35); opacity: 0.8; }
}

.uptime-badge {
  font-size: 12px;
  color: var(--text-dim);
  font-family: ui-monospace, monospace;
}

/* Layout */
main {
  flex: 1;
  padding: 24px 28px;
  max-width: 1220px;
  margin: 0 auto;
  width: 100%;
  display: grid;
  grid-template-columns: 1.18fr 0.82fr;
  gap: 24px;
  position: relative;
  z-index: 1;
}

/* Glass Card */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.2s ease;
  position: relative;
}

.glass-card:hover {
  border-color: rgba(255, 255, 255, 0.14);
}

.card-title {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-dim);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Master Action Card */
.master-card {
  background: linear-gradient(145deg, rgba(20, 25, 44, 0.9), rgba(12, 15, 28, 0.92));
  border: 1px solid rgba(88, 101, 242, 0.28);
  position: relative;
  overflow: hidden;
}

.master-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--blurple), var(--cyan), var(--emerald));
}

.master-btn-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 8px;
  text-align: center;
}

.btn-master {
  width: 100%;
  max-width: 440px;
  padding: 18px 28px;
  border-radius: 16px;
  border: none;
  font-size: 15px;
  font-weight: 700;
  color: #FFF;
  background: linear-gradient(135deg, #5865F2, #4752C4);
  box-shadow: 0 10px 32px var(--blurple-glow);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.btn-master:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 44px rgba(88, 101, 242, 0.6);
}

.btn-master:active {
  transform: translateY(1px) scale(0.98);
}

.btn-master.running {
  background: linear-gradient(135deg, #F59E0B, #D97706);
  box-shadow: 0 10px 30px var(--amber-glow);
}

.btn-master.active {
  background: linear-gradient(135deg, #10B981, #059669);
  box-shadow: 0 10px 30px var(--emerald-glow);
}

/* Pipeline Step Cards */
.pipeline {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.step-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: rgba(10, 13, 22, 0.65);
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all 0.3s ease;
}

.step-card.active {
  border-color: var(--blurple);
  background: rgba(88, 101, 242, 0.1);
  box-shadow: 0 0 24px rgba(88, 101, 242, 0.18);
}

.step-card.done {
  border-color: rgba(16, 185, 129, 0.45);
  background: rgba(16, 185, 129, 0.06);
}

.step-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-dim);
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.step-card.active .step-num {
  background: var(--blurple);
  color: #FFF;
}

.step-card.done .step-num {
  background: var(--emerald);
  color: #FFF;
}

.step-info h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.step-info p {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.step-status-tag {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 8px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.step-card.active .step-status-tag {
  background: rgba(245, 158, 11, 0.18);
  color: var(--amber);
}

.step-card.done .step-status-tag {
  background: rgba(16, 185, 129, 0.18);
  color: var(--emerald);
}

/* Sudo / Password Card */
.sudo-card {
  background: rgba(14, 18, 30, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.28);
  border-radius: 16px;
  padding: 18px;
}

.sudo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.sudo-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #FCD34D;
}

.sudo-input-row {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.sudo-input-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.sudo-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.45);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 38px 10px 14px;
  font-size: 13px;
  color: #FFF;
  outline: none;
  transition: border-color 0.2s ease;
}

.sudo-input:focus {
  border-color: var(--blurple);
}

.eye-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: #FFF;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.16);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #FCA5A5;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.25);
}

/* Toggle Switch */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 2px 0;
  border-top: 1px solid var(--border);
  margin-top: 14px;
}

.toggle-info h5 {
  font-size: 12px;
  font-weight: 600;
}

.toggle-info p {
  font-size: 11px;
  color: var(--text-muted);
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.15);
  transition: .3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--blurple);
}

input:checked + .slider:before {
  transform: translateX(20px);
}

/* System Monitor & Ping */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 14px;
}

.metric-box {
  background: var(--bg-sub);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.metric-val {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 6px;
}

.ping-canvas-container {
  height: 64px;
  width: 100%;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 12px;
  padding: 6px;
  border: 1px solid var(--border);
}

canvas#pingChart {
  width: 100%;
  height: 100%;
}

/* Terminal Console Log */
.terminal-container {
  display: flex;
  flex-direction: column;
  height: 240px;
}

.terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.terminal-box {
  flex: 1;
  background: #040508;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  overflow-y: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;
  font-size: 11px;
  line-height: 1.5;
  color: #CBD5E1;
}

.terminal-box::-webkit-scrollbar {
  width: 6px;
}
.terminal-box::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

.log-line {
  margin-bottom: 4px;
  display: flex;
  gap: 8px;
}

.log-time {
  color: var(--text-muted);
}

.log-badge {
  font-weight: 700;
  padding: 0 4px;
  border-radius: 4px;
  font-size: 10px;
}

.log-badge.INFO { color: var(--text-dim); }
.log-badge.CMD { color: #818CF8; }
.log-badge.SUCCESS { color: var(--emerald); }
.log-badge.WARN { color: var(--amber); }
.log-badge.ERROR { color: var(--rose); }

/* Quick Action Buttons Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 10px;
}

/* Footer Controls */
footer {
  padding: 14px 28px;
  background: rgba(7, 9, 14, 0.82);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
}

.warp-mode-select {
  display: flex;
  background: var(--bg-sub);
  padding: 3px;
  border-radius: 10px;
  border: 1px solid var(--border);
  gap: 4px;
}

.warp-mode-opt {
  padding: 5px 12px;
  border-radius: 7px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  color: var(--text-dim);
  transition: all 0.2s ease;
}

.warp-mode-opt.selected {
  background: var(--blurple);
  color: #FFF;
}
</style>
</head>
<body>

<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>

<header>
  <div class="logo-group">
    <div class="app-icon">🎮</div>
    <div class="logo-text">
      <h1>Discord DPI Bypass <span class="badge-ver">PRO v6.0</span></h1>
      <p>macOS Oyun Pingini Korumalı Otomatik Optimizasyon</p>
    </div>
  </div>

  <div class="header-status">
    <button class="audio-btn" id="audioToggleBtn" title="Ses Efektlerini Aç/Kapat" onclick="toggleAudio()">🔊</button>
    <div class="status-pill">
      <div class="status-dot" id="headerDot"></div>
      <span id="headerStatusText">Kontrol Ediliyor...</span>
    </div>
    <div class="uptime-badge" id="uptimeDisplay">⏱ 00:00:00</div>
  </div>
</header>

<main>
  <!-- SOL KOLON: Ana Kontrol, Pipeline, Sudo -->
  <div style="display: flex; flex-direction: column; gap: 18px;">
    
    <!-- MASTER ACTION CARD -->
    <div class="glass-card master-card">
      <div class="card-title">
        <span>🚀 Otomasyon Kontrol Merkezi</span>
        <div class="warp-mode-select">
          <div class="warp-mode-opt selected" id="modeWarp" onclick="setWarpMode('warp')">🛡️ Tam VPN</div>
          <div class="warp-mode-opt" id="modeProxy" onclick="setWarpMode('proxy')">🔌 SOCKS Proxy</div>
        </div>
      </div>

      <div class="master-btn-container">
        <button class="btn-master" id="btnMaster" onclick="toggleMasterLaunch()">
          <span id="btnMasterIcon" style="font-size: 20px;">⚡</span>
          <span id="btnMasterText">SİSTEMİ BAŞLAT (TEK TIK)</span>
        </button>
        <p style="font-size: 12px; color: var(--text-dim); margin-top: 12px;">
          WARP, SpoofDPI ve Discord'u sırayla doğru konfigürasyonla başlatır.
        </p>
      </div>

      <!-- Pipeline Adımları -->
      <div class="pipeline">
        <div class="step-card" id="step1">
          <div class="step-left">
            <div class="step-num">1</div>
            <div class="step-info">
              <h4>Cloudflare WARP</h4>
              <p>Güvenli VPN veya SOCKS Proxy tüneli kurulur</p>
            </div>
          </div>
          <div class="step-status-tag" id="step1Status">BEKLEMEDE</div>
        </div>

        <div class="step-card" id="step2">
          <div class="step-left">
            <div class="step-num">2</div>
            <div class="step-info">
              <h4>SpoofDPI Engine</h4>
              <p>Derin paket incelemesi (DPI) atlatılır (UDP Ping Dokunulmaz)</p>
            </div>
          </div>
          <div class="step-status-tag" id="step2Status">BEKLEMEDE</div>
        </div>

        <div class="step-card" id="step3">
          <div class="step-left">
            <div class="step-num">3</div>
            <div class="step-info">
              <h4>Discord Web App</h4>
              <p>Brave / Discord optimize edilmiş modda açılır</p>
            </div>
          </div>
          <div class="step-status-tag" id="step3Status">BEKLEMEDE</div>
        </div>
      </div>
    </div>

    <!-- SUDO & AYARLAR KARTI -->
    <div class="glass-card sudo-card">
      <div class="sudo-header">
        <div class="sudo-title">
          <span>🔐 macOS Yönetici Yetkisi (Sudo)</span>
        </div>
        <span id="sudoBadge" style="font-size: 11px; padding: 3px 8px; border-radius: 6px; background: rgba(245, 158, 11, 0.2); color: #FCD34D; font-weight: 600;">Şifre Bekleniyor</span>
      </div>
      <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 8px;">
        SpoofDPI ağ adaptörünü yapılandırırken şifre ister. Şifrenizi 1 kere girin, sistem arka planda yönetsin.
      </p>
      
      <div class="sudo-input-row">
        <div class="sudo-input-container">
          <input type="password" class="sudo-input" id="sudoPasswordInput" placeholder="macOS Şifreniz..." onkeydown="if(event.key==='Enter') saveSudoPassword()" />
          <button class="eye-btn" onclick="togglePasswordVisibility()">👁️</button>
        </div>
        <button class="btn-secondary" onclick="saveSudoPassword()">✓ Test Et & Kaydet</button>
      </div>

      <div class="toggle-row">
        <div class="toggle-info">
          <h5>Mac Açılışında Otomatik Başlat</h5>
          <p>Bilgisayar açıldığında Discord DPI Bypass otomatik çalışır</p>
        </div>
        <label class="switch">
          <input type="checkbox" id="startupToggle" onchange="toggleStartup(this.checked)">
          <span class="slider"></span>
        </label>
      </div>
    </div>

  </div>

  <!-- SAĞ KOLON: Canlı Metrikler, Hızlı İşlemler, Konsol Logu -->
  <div style="display: flex; flex-direction: column; gap: 18px;">
    
    <!-- METRİKLER VE CANLI PING GRAFİĞİ -->
    <div class="glass-card">
      <div class="card-title">
        <span>📊 Canlı Ağ & Sistem Durumu</span>
        <span style="font-size: 11px; color: var(--cyan); font-weight: 700;" id="livePingText">Ping: -- ms</span>
      </div>

      <div class="metrics-grid">
        <div class="metric-box">
          <span class="metric-label">Cloudflare WARP</span>
          <span class="metric-val" id="valWarp"><span style="color:var(--text-muted)">○</span> Kapalı</span>
        </div>
        <div class="metric-box">
          <span class="metric-label">SpoofDPI Engine</span>
          <span class="metric-val" id="valSpoof"><span style="color:var(--text-muted)">○</span> Kapalı</span>
        </div>
        <div class="metric-box">
          <span class="metric-label">Discord Gateway</span>
          <span class="metric-val" id="valDiscord" style="color: var(--emerald);">🟢 Erişilebilir</span>
        </div>
        <div class="metric-box">
          <span class="metric-label">Oyun Ping Koruması</span>
          <span class="metric-val" style="color: var(--cyan);">⚡ %0 Etki (UDP)</span>
        </div>
      </div>

      <div class="ping-canvas-container">
        <canvas id="pingChart"></canvas>
      </div>
    </div>

    <!-- HIZLI AKSİYONLAR -->
    <div class="glass-card">
      <div class="card-title">
        <span>⚡ Hızlı Manuel Aksiyonlar</span>
      </div>
      <div class="actions-grid">
        <button class="btn-secondary" onclick="actionCall('warp_connect')">🛡️ WARP Bağlan</button>
        <button class="btn-secondary" onclick="actionCall('warp_disconnect')">🔌 WARP Kes</button>
        <button class="btn-secondary" onclick="actionCall('dpi_start')">🟢 DPI Başlat</button>
        <button class="btn-secondary" onclick="actionCall('dpi_stop')">🔴 DPI Durdur</button>
        <button class="btn-secondary" style="grid-column: span 2;" onclick="actionCall('discord_launch')">💬 Discord'u Ayrı Pencerede Aç</button>
        <button class="btn-secondary btn-danger" style="grid-column: span 2;" onclick="actionCall('stop_all')">⏹ Tüm Hizmetleri Durdur</button>
      </div>
    </div>

    <!-- CANLI TERMİNAL GÜNLÜĞÜ -->
    <div class="glass-card terminal-container">
      <div class="terminal-header">
        <span class="card-title" style="margin-bottom: 0;">📜 Canlı Sistem Günlüğü</span>
        <button class="btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="clearLogs()">Temizle</button>
      </div>
      <div class="terminal-box" id="terminalLog">
        <div class="log-line"><span class="log-time">[00:00:00]</span> <span class="log-badge INFO">INFO</span> Sistem başlatılıyor...</div>
      </div>
    </div>

  </div>
</main>

<footer>
  <span>Discord DPI Bypass • macOS Architecture • Ping-Free Routing</span>
  <span>Geliştirici: <a href="https://github.com/Cnek00/DPI-for-macos" target="_blank" style="color: var(--blurple); text-decoration: none; font-weight: 600;">github.com/Cnek00/DPI-for-macos</a></span>
</footer>

<script>
let lastState = {};
let pingHistory = [];
let audioEnabled = true;
let audioCtx = null;

function playSound(freq, duration, type='sine') {
  if (!audioEnabled) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch(e) {}
}

function toggleAudio() {
  audioEnabled = !audioEnabled;
  document.getElementById('audioToggleBtn').innerText = audioEnabled ? '🔊' : '🔇';
  if (audioEnabled) playSound(580, 0.1);
}

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    updateUI(data);
  } catch (e) {
    console.error(e);
  }
}

function updateUI(state) {
  lastState = state;

  const dot = document.getElementById('headerDot');
  const txt = document.getElementById('headerStatusText');
  const btnMaster = document.getElementById('btnMaster');
  const btnText = document.getElementById('btnMasterText');
  const btnIcon = document.getElementById('btnMasterIcon');

  if (state.is_active) {
    dot.className = 'status-dot active';
    txt.innerText = 'SİSTEM AKTİF (Discord Hazır)';
    txt.style.color = 'var(--emerald)';
    btnMaster.className = 'btn-master active';
    btnText.innerText = 'SİSTEM ÇALIŞIYOR (DURDUR)';
    btnIcon.innerText = '✓';
  } else if (state.running_all) {
    dot.className = 'status-dot active';
    txt.innerText = 'BAŞLATILIYOR...';
    txt.style.color = 'var(--amber)';
    btnMaster.className = 'btn-master running';
    btnText.innerText = 'BAŞLATILIYOR...';
    btnIcon.innerText = '⏳';
  } else {
    dot.className = 'status-dot';
    txt.innerText = 'HAZIR (Beklemede)';
    txt.style.color = 'var(--text-dim)';
    btnMaster.className = 'btn-master';
    btnText.innerText = 'SİSTEMİ BAŞLAT (TEK TIK)';
    btnIcon.innerText = '⚡';
  }

  // Uptime
  const s = state.uptime_seconds || 0;
  const hrs = String(Math.floor(s / 3600)).padStart(2, '0');
  const mins = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
  const secs = String(s % 60).padStart(2, '0');
  document.getElementById('uptimeDisplay').innerText = `⏱ ${hrs}:${mins}:${secs}`;

  // Steps
  updateStep(1, state.step >= 1, state.step > 1 || state.warp_status === 'connected');
  updateStep(2, state.step >= 2, state.step > 2 || state.spoofdpi_running);
  updateStep(3, state.step >= 3, state.step >= 4);

  // Sudo badge
  const sudoBadge = document.getElementById('sudoBadge');
  if (state.sudo_cached) {
    sudoBadge.innerText = '✓ Sudo Yetkili';
    sudoBadge.style.background = 'rgba(16, 185, 129, 0.2)';
    sudoBadge.style.color = '#34D399';
  } else {
    sudoBadge.innerText = 'Şifre Girilmedi';
    sudoBadge.style.background = 'rgba(245, 158, 11, 0.2)';
    sudoBadge.style.color = '#FCD34D';
  }

  // Startup toggle
  document.getElementById('startupToggle').checked = state.startup_enabled;

  // Metric Boxes
  const valWarp = document.getElementById('valWarp');
  if (state.warp_status === 'connected') {
    valWarp.innerHTML = '<span style="color:var(--emerald)">●</span> Bağlı';
  } else if (state.warp_status === 'connecting') {
    valWarp.innerHTML = '<span style="color:var(--amber)">◐</span> Bağlanıyor';
  } else {
    valWarp.innerHTML = '<span style="color:var(--text-muted)">○</span> Kapalı';
  }

  const valSpoof = document.getElementById('valSpoof');
  if (state.spoofdpi_running) {
    valSpoof.innerHTML = '<span style="color:var(--emerald)">●</span> Aktif';
  } else {
    valSpoof.innerHTML = '<span style="color:var(--text-muted)">○</span> Kapalı';
  }

  // Pings
  if (state.pings && state.pings.length > 0) {
    const latest = state.pings[state.pings.length - 1];
    document.getElementById('livePingText').innerText = `Discord Ping: ${latest.ms} ms`;
    pingHistory = state.pings.map(p => p.ms);
    drawPingChart();
  }

  // Logs
  if (state.logs) {
    renderLogs(state.logs);
  }
}

function updateStep(num, isRunning, isDone) {
  const card = document.getElementById(`step${num}`);
  const tag = document.getElementById(`step${num}Status`);
  if (isDone) {
    card.className = 'step-card done';
    tag.innerText = 'TAMAMLANDI ✓';
  } else if (isRunning) {
    card.className = 'step-card active';
    tag.innerText = 'ÇALIŞIYOR...';
  } else {
    card.className = 'step-card';
    tag.innerText = 'BEKLEMEDE';
  }
}

function renderLogs(logs) {
  const box = document.getElementById('terminalLog');
  const wasScrolledToBottom = box.scrollHeight - box.clientHeight <= box.scrollTop + 30;
  
  box.innerHTML = logs.map(l => `
    <div class="log-line">
      <span class="log-time">[${l.time}]</span>
      <span class="log-badge ${l.level}">${l.level}</span>
      <span>${escapeHtml(l.msg)}</span>
    </div>
  `).join('');

  if (wasScrolledToBottom) {
    box.scrollTop = box.scrollHeight;
  }
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

async function toggleMasterLaunch() {
  playSound(720, 0.12);
  if (lastState.is_active) {
    await fetch('/api/stop_all', { method: 'POST' });
  } else {
    await fetch('/api/launch_all', { method: 'POST' });
  }
  fetchStatus();
}

async function actionCall(endpoint) {
  playSound(550, 0.08);
  await fetch(`/api/${endpoint}`, { method: 'POST' });
  fetchStatus();
}

function togglePasswordVisibility() {
  const input = document.getElementById('sudoPasswordInput');
  input.type = input.type === 'password' ? 'text' : 'password';
}

async function saveSudoPassword() {
  const pwd = document.getElementById('sudoPasswordInput').value;
  if (!pwd) return;
  playSound(600, 0.1);
  const res = await fetch('/api/set_password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password: pwd })
  });
  const data = await res.json();
  if (data.ok) {
    playSound(880, 0.2);
    alert('✓ Yönetici şifresi başarıyla doğrulandı ve kaydedildi!');
    document.getElementById('sudoPasswordInput').value = '';
  } else {
    playSound(320, 0.3, 'sawtooth');
    alert('❌ Hatalı şifre! Lütfen macOS oturum şifrenizi doğru girin.');
  }
  fetchStatus();
}

async function toggleStartup(enabled) {
  playSound(520, 0.1);
  await fetch('/api/toggle_startup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enabled: enabled })
  });
  fetchStatus();
}

function setWarpMode(mode) {
  playSound(480, 0.08);
  document.getElementById('modeWarp').className = mode === 'warp' ? 'warp-mode-opt selected' : 'warp-mode-opt';
  document.getElementById('modeProxy').className = mode === 'proxy' ? 'warp-mode-opt selected' : 'warp-mode-opt';
  fetch('/api/set_warp_mode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: mode })
  });
}

function clearLogs() {
  playSound(400, 0.08);
  document.getElementById('terminalLog').innerHTML = '';
}

// Live Ping Bezier Canvas Graph
function drawPingChart() {
  const canvas = document.getElementById('pingChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.parentElement.clientWidth;
  const h = canvas.parentElement.clientHeight;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, w, h);
  if (pingHistory.length < 2) return;

  const maxPing = Math.max(...pingHistory, 80);
  const minPing = Math.min(...pingHistory, 10);

  ctx.beginPath();
  const step = w / (pingHistory.length - 1);
  pingHistory.forEach((val, i) => {
    const x = i * step;
    const y = h - ((val - minPing) / (maxPing - minPing + 1)) * (h - 12) - 6;
    if (i === 0) ctx.moveTo(x, y);
    else {
      // Smooth quadratic curve
      const prevX = (i - 1) * step;
      const prevVal = pingHistory[i - 1];
      const prevY = h - ((prevVal - minPing) / (maxPing - minPing + 1)) * (h - 12) - 6;
      const cpX = (prevX + x) / 2;
      ctx.quadraticCurveTo(cpX, prevY, x, y);
    }
  });

  ctx.strokeStyle = '#00F0FF';
  ctx.lineWidth = 2.5;
  ctx.shadowColor = 'rgba(0, 240, 255, 0.6)';
  ctx.shadowBlur = 8;
  ctx.stroke();

  // Gradient fill below
  ctx.lineTo(w, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  const grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(0, 240, 255, 0.3)');
  grad.addColorStop(1, 'rgba(0, 240, 255, 0.0)');
  ctx.fillStyle = grad;
  ctx.shadowBlur = 0;
  ctx.fill();
}

fetchStatus();
setInterval(fetchStatus, 1500);
</script>
</body>
</html>
"""


class DashboardRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with STATE_LOCK:
                data = dict(STATE)
                data["sudo_password"] = "***" if STATE["sudo_password"] else ""
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        response = {"ok": True}

        if parsed.path == "/api/launch_all":
            threading.Thread(target=do_launch_all_sequence, daemon=True).start()
        elif parsed.path == "/api/stop_all":
            threading.Thread(target=do_stop_all, daemon=True).start()
        elif parsed.path == "/api/warp_connect":
            threading.Thread(target=lambda: do_warp_connect(STATE["warp_mode"]), daemon=True).start()
        elif parsed.path == "/api/warp_disconnect":
            threading.Thread(target=do_warp_disconnect, daemon=True).start()
        elif parsed.path == "/api/dpi_start":
            threading.Thread(target=do_spoofdpi_start, daemon=True).start()
        elif parsed.path == "/api/dpi_stop":
            threading.Thread(target=do_spoofdpi_stop, daemon=True).start()
        elif parsed.path == "/api/discord_launch":
            threading.Thread(target=do_launch_discord, daemon=True).start()
        elif parsed.path == "/api/set_password":
            pwd = payload.get("password", "")
            if test_sudo_password(pwd):
                with STATE_LOCK:
                    STATE["sudo_password"] = pwd
                    STATE["sudo_cached"] = True
                add_log("✓ Sudo şifresi doğrulandı ve kaydedildi.", "SUCCESS")
                response = {"ok": True}
            else:
                add_log("✗ Hatalı sudo şifresi denendi.", "ERROR")
                response = {"ok": False, "error": "Invalid password"}
        elif parsed.path == "/api/set_warp_mode":
            mode = payload.get("mode", "warp")
            with STATE_LOCK:
                STATE["warp_mode"] = mode
            add_log(f"WARP modu '{mode.upper()}' olarak ayarlandı.", "INFO")
        elif parsed.path == "/api/toggle_startup":
            enabled = payload.get("enabled", False)
            set_startup(enabled)
            with STATE_LOCK:
                STATE["startup_enabled"] = enabled

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


def open_desktop_window(url):
    time.sleep(0.8)
    brave_path = "/Applications/Brave Browser.app"
    chrome_path = "/Applications/Google Chrome.app"
    profile_dir = "/tmp/discord_dpi_app_profile"
    
    if Path(brave_path).exists():
        subprocess.Popen([
            "open", "-na", "Brave Browser",
            "--args",
            f"--app={url}",
            "--window-size=1180,860",
            f"--user-data-dir={profile_dir}"
        ])
    elif Path(chrome_path).exists():
        subprocess.Popen([
            "open", "-na", "Google Chrome",
            "--args",
            f"--app={url}",
            "--window-size=1180,860",
            f"--user-data-dir={profile_dir}"
        ])
    else:
        subprocess.Popen(["open", url])


def main():
    if len(sys.argv) > 1 and sys.argv[1]:
        init_pass = sys.argv[1]
        if test_sudo_password(init_pass):
            STATE["sudo_password"] = init_pass
            STATE["sudo_cached"] = True
            add_log("✓ Terminalden iletilen sudo şifresi doğrulandı.", "SUCCESS")

    add_log("Discord DPI Bypass Motoru Hazırlanıyor...", "INFO")

    threading.Thread(target=poll_system_state, daemon=True).start()

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    target_port = PORT
    server = None
    for p in range(PORT, PORT + 20):
        try:
            server = ReusableTCPServer(("127.0.0.1", p), DashboardRequestHandler)
            target_port = p
            break
        except Exception:
            continue

    if not server:
        print("Port could not be bound.")
        sys.exit(1)

    url = f"http://127.0.0.1:{target_port}"
    add_log(f"Kontrol paneli hazır: {url}", "SUCCESS")
    print(f"🚀 Discord DPI Bypass Dashboard: {url}")

    threading.Thread(target=lambda: open_desktop_window(url), daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Sunucu kapatılıyor...")
        server.server_close()


if __name__ == "__main__":
    main()
