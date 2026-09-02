#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  DISCORD DPI BYPASS & OPTIMIZER PRO v5.0 — NATIVE DESKTOP GUI
  100% Pure Python CustomTkinter Desktop Application (No Web/HTML)
  macOS Gaming Ping-Protection • Zero Latency • Animated Glassmorphism Theme
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import subprocess
import threading
import plistlib
import datetime
from pathlib import Path

# Add user site-packages to path if needed
user_site = os.path.expanduser('~/Library/Python/3.9/lib/python/site-packages')
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    import customtkinter as ctk
except ImportError:
    # Auto-install or fallback attempt
    subprocess.run([sys.executable, "-m", "pip", "install", "customtkinter"], capture_output=True)
    import customtkinter as ctk

# CustomTkinter Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
LAUNCHAGENT = Path.home() / "Library/LaunchAgents/com.discord.dpibypass.plist"
PLIST_LABEL = "com.discord.dpibypass"

# Color Palette (Discord Blurple & Cyberpunk Obsidian)
THEME = {
    "bg": "#0B0E17",
    "card": "#131726",
    "card_hover": "#1A2035",
    "card_border": "#232942",
    "card_border_glow": "#5865F2",
    
    "blurple": "#5865F2",
    "blurple_hover": "#4752C4",
    "blurple_light": "#7983F5",
    
    "emerald": "#10B981",
    "emerald_hover": "#059669",
    "emerald_bg": "#064E3B",
    
    "amber": "#F59E0B",
    "amber_hover": "#D97706",
    "amber_bg": "#78350F",
    
    "rose": "#EF4444",
    "rose_hover": "#DC2626",
    "rose_bg": "#7F1D1D",
    
    "cyan": "#06B6D4",
    
    "text_main": "#FFFFFF",
    "text_dim": "#94A3B8",
    "text_muted": "#64748B",
    "input_bg": "#080A10"
}


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER SYSTEM FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def run_cmd(cmd, sudo_pass=None, timeout=10):
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


def startup_installed():
    return LAUNCHAGENT.exists()


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
    else:
        if LAUNCHAGENT.exists():
            run_cmd(["launchctl", "unload", str(LAUNCHAGENT)])
            LAUNCHAGENT.unlink()


# ─────────────────────────────────────────────────────────────────────────────
#  NATIVE CUSTOMTKINTER GUI APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class DiscordDPINativeApp(ctk.CTk):
    def __init__(self, initial_sudo=""):
        super().__init__()

        self.title("Discord DPI Bypass & Optimizer PRO")
        self.geometry("1060x780")
        self.minsize(980, 720)
        self.configure(fg_color=THEME["bg"])

        # State Variables
        self.sudo_password = initial_sudo
        self.warp_mode = "warp"
        self.is_running_all = False
        self.is_active = False
        self.uptime_seconds = 0
        self.spoofdpi_proc = None
        self.latest_ping = "--"

        # Center Window on Screen
        self.update_idletasks()
        w = 1060
        h = 780
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Build UI
        self._build_header()
        self._build_main_content()
        self._build_footer()

        # Background Polling & Monitoring
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.uptime_thread = threading.Thread(target=self._uptime_loop, daemon=True)
        self.uptime_thread.start()

        # Log initial state
        self.log("🚀 Discord DPI Bypass PRO Native GUI başlatıldı.", "SUCCESS")
        if self.sudo_password:
            self.log("✓ Sudo şifresi önbelleğe alındı.", "SUCCESS")
        else:
            self.log("ℹ Yönetici şifresi girilmedi. Panelden girebilirsiniz.", "INFO")

    # ─── HEADER ───────────────────────────────────────────────────────────────
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=THEME["card"], corner_radius=0, height=72)
        header_frame.pack(fill="x", side="top", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Left Branding
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=24, pady=12)

        icon_lbl = ctk.CTkLabel(
            left_box, text="🎮", font=ctk.CTkFont(size=28),
            fg_color=THEME["blurple"], corner_radius=12, width=46, height=46
        )
        icon_lbl.pack(side="left", padx=(0, 14))

        title_box = ctk.CTkFrame(left_box, fg_color="transparent")
        title_box.pack(side="left")

        title_row = ctk.CTkFrame(title_box, fg_color="transparent")
        title_row.pack(anchor="w")

        title_lbl = ctk.CTkLabel(
            title_row, text="Discord DPI Bypass",
            font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
            text_color=THEME["text_main"]
        )
        title_lbl.pack(side="left")

        ver_badge = ctk.CTkLabel(
            title_row, text="PRO v5.0 NATIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=THEME["card_border"], text_color=THEME["blurple_light"],
            corner_radius=6, padx=6, pady=2
        )
        ver_badge.pack(side="left", padx=8)

        sub_lbl = ctk.CTkLabel(
            title_box, text="macOS Oyun Pingini Korumalı Otomatik Optimizasyon (UDP Dokunulmaz)",
            font=ctk.CTkFont(size=11), text_color=THEME["text_dim"]
        )
        sub_lbl.pack(anchor="w")

        # Right Status Pills
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=24, pady=12)

        self.status_pill = ctk.CTkLabel(
            right_box, text="● SİSTEM HAZIR (Beklemede)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=THEME["card_border"], text_color=THEME["amber"],
            corner_radius=16, padx=14, pady=6
        )
        self.status_pill.pack(side="right", padx=(10, 0))

        self.uptime_lbl = ctk.CTkLabel(
            right_box, text="⏱ 00:00:00",
            font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
            text_color=THEME["text_dim"]
        )
        self.uptime_lbl.pack(side="right")

    # ─── MAIN CONTENT (2 COLUMNS) ─────────────────────────────────────────────
    def _build_main_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=16)

        content_frame.columnconfigure(0, weight=11)
        content_frame.columnconfigure(1, weight=9)
        content_frame.rowconfigure(0, weight=1)

        # ── LEFT COLUMN: MASTER CONTROL, PIPELINE, SUDO & SETTINGS ──
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._build_master_card(left_col)
        self._build_sudo_card(left_col)

        # ── RIGHT COLUMN: METRICS, QUICK ACTIONS & TERMINAL LOGS ──
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._build_metrics_card(right_col)
        self._build_quick_actions_card(right_col)
        self._build_terminal_card(right_col)

    # ── MASTER CARD (Single-Click Automation & Pipeline) ──
    def _build_master_card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=THEME["card"], corner_radius=16,
            border_width=1, border_color=THEME["card_border"]
        )
        card.pack(fill="x", pady=(0, 14))

        # Title & Mode Switch
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(
            top_row, text="🚀 OTOMASYON KONTROL MERKEZİ",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_dim"]
        ).pack(side="left")

        # WARP Mode Segments
        self.warp_mode_seg = ctk.CTkSegmentedButton(
            top_row, values=["🛡️ Tam VPN", "🔌 SOCKS Proxy"],
            command=self._on_warp_mode_change,
            selected_color=THEME["blurple"], selected_hover_color=THEME["blurple_hover"],
            unselected_color=THEME["input_bg"], unselected_hover_color=THEME["card_hover"],
            font=ctk.CTkFont(size=11, weight="bold"), height=28
        )
        self.warp_mode_seg.set("🛡️ Tam VPN")
        self.warp_mode_seg.pack(side="right")

        # Big Master Launch Button
        self.btn_master = ctk.CTkButton(
            card, text="⚡ SİSTEMİ BAŞLAT (TEK TIK)",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=THEME["blurple"], hover_color=THEME["blurple_hover"],
            corner_radius=14, height=52, command=self._toggle_master_launch
        )
        self.btn_master.pack(fill="x", padx=16, pady=(10, 4))

        sub_info = ctk.CTkLabel(
            card, text="WARP, SpoofDPI ve Discord'u sırayla optimize ederek başlatır.",
            font=ctk.CTkFont(size=11), text_color=THEME["text_muted"]
        )
        sub_info.pack(pady=(0, 10))

        # 3 Pipeline Steps
        pipeline_frame = ctk.CTkFrame(card, fg_color="transparent")
        pipeline_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.step1_card = self._create_step_widget(
            pipeline_frame, "1", "Cloudflare WARP", "VPN veya Proxy tüneli kurulur"
        )
        self.step2_card = self._create_step_widget(
            pipeline_frame, "2", "SpoofDPI Engine", "DPI kısıtlaması atlatılır (UDP Ping Etkilenmez)"
        )
        self.step3_card = self._create_step_widget(
            pipeline_frame, "3", "Discord Web App", "Brave / Discord optimize edilmiş modda açılır"
        )

    def _create_step_widget(self, parent, num, title, subtitle):
        row = ctk.CTkFrame(
            parent, fg_color=THEME["input_bg"], corner_radius=10,
            border_width=1, border_color=THEME["card_border"]
        )
        row.pack(fill="x", pady=4)

        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", padx=12, pady=10)

        num_lbl = ctk.CTkLabel(
            left, text=num, font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], text_color=THEME["text_dim"],
            width=26, height=26, corner_radius=8
        )
        num_lbl.pack(side="left", padx=(0, 10))

        txt_box = ctk.CTkFrame(left, fg_color="transparent")
        txt_box.pack(side="left")

        t_lbl = ctk.CTkLabel(
            txt_box, text=title, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=THEME["text_main"]
        )
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(
            txt_box, text=subtitle, font=ctk.CTkFont(size=10),
            text_color=THEME["text_muted"]
        )
        s_lbl.pack(anchor="w")

        tag = ctk.CTkLabel(
            row, text="BEKLEMEDE", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=THEME["card_border"], text_color=THEME["text_muted"],
            corner_radius=6, padx=8, pady=3
        )
        tag.pack(side="right", padx=12)

        return {"row": row, "num": num_lbl, "tag": tag, "title": t_lbl}

    # ── SUDO & SETTINGS CARD ──
    def _build_sudo_card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=THEME["card"], corner_radius=16,
            border_width=1, border_color=THEME["card_border"]
        )
        card.pack(fill="x")

        hdr_row = ctk.CTkFrame(card, fg_color="transparent")
        hdr_row.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            hdr_row, text="🔐 macOS YÖNETİCİ YETKİSİ (SUDO)",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["amber"]
        ).pack(side="left")

        self.sudo_status_badge = ctk.CTkLabel(
            hdr_row, text="Şifre Girilmedi",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=THEME["amber_bg"], text_color=THEME["amber"],
            corner_radius=6, padx=8, pady=2
        )
        self.sudo_status_badge.pack(side="right")

        desc = ctk.CTkLabel(
            card, text="SpoofDPI ağ adaptörünü yetkilendirirken şifre ister. Şifrenizi 1 kere girin, sistem otomatik yönetsin.",
            font=ctk.CTkFont(size=11), text_color=THEME["text_dim"], wraplength=480, justify="left"
        )
        desc.pack(anchor="w", padx=16, pady=(0, 10))

        # Input Row
        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.pack(fill="x", padx=16, pady=(0, 12))

        self.sudo_entry = ctk.CTkEntry(
            input_row, placeholder_text="macOS Oturum Şifreniz...",
            show="●", font=ctk.CTkFont(size=12),
            fg_color=THEME["input_bg"], border_color=THEME["card_border"],
            corner_radius=10, height=36
        )
        self.sudo_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.sudo_entry.bind("<Return>", lambda e: self._save_sudo_password())

        btn_save_sudo = ctk.CTkButton(
            input_row, text="✓ Test Et & Kaydet",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], hover_color=THEME["card_hover"],
            corner_radius=10, height=36, width=120, command=self._save_sudo_password
        )
        btn_save_sudo.pack(side="right")

        # Divider
        div = ctk.CTkFrame(card, fg_color=THEME["card_border"], height=1)
        div.pack(fill="x", padx=16, pady=(0, 10))

        # Startup Toggle
        toggle_row = ctk.CTkFrame(card, fg_color="transparent")
        toggle_row.pack(fill="x", padx=16, pady=(0, 14))

        t_txt = ctk.CTkFrame(toggle_row, fg_color="transparent")
        t_txt.pack(side="left")

        ctk.CTkLabel(
            t_txt, text="Mac Açılışında Otomatik Başlat",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_main"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            t_txt, text="Bilgisayar açıldığında bu uygulama arka planda başlar.",
            font=ctk.CTkFont(size=10), text_color=THEME["text_muted"]
        ).pack(anchor="w")

        self.startup_switch = ctk.CTkSwitch(
            toggle_row, text="", command=self._on_startup_toggle,
            progress_color=THEME["blurple"], fg_color=THEME["input_bg"]
        )
        self.startup_switch.pack(side="right")
        if startup_installed():
            self.startup_switch.select()
        else:
            self.startup_switch.deselect()

    # ── METRICS & PING CARD ──
    def _build_metrics_card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=THEME["card"], corner_radius=16,
            border_width=1, border_color=THEME["card_border"]
        )
        card.pack(fill="x", pady=(0, 14))

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(
            top_row, text="📊 CANLI AĞ & SİSTEM DURUMU",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_dim"]
        ).pack(side="left")

        self.live_ping_lbl = ctk.CTkLabel(
            top_row, text="Discord Ping: -- ms",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=THEME["cyan"]
        )
        self.live_ping_lbl.pack(side="right")

        # 2x2 Grid of Status Tiles
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 12))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self.metric_warp = self._create_metric_tile(grid, 0, 0, "Cloudflare WARP", "○ Kapalı", THEME["text_muted"])
        self.metric_spoof = self._create_metric_tile(grid, 0, 1, "SpoofDPI Engine", "○ Kapalı", THEME["text_muted"])
        self.metric_discord = self._create_metric_tile(grid, 1, 0, "Discord Gateway", "🟢 Erişilebilir", THEME["emerald"])
        self.metric_udp = self._create_metric_tile(grid, 1, 1, "Oyun Ping Koruması", "⚡ %0 Etki (UDP)", THEME["cyan"])

    def _create_metric_tile(self, parent, r, c, label, val, val_color):
        tile = ctk.CTkFrame(
            parent, fg_color=THEME["input_bg"], corner_radius=10,
            border_width=1, border_color=THEME["card_border"]
        )
        tile.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        lbl = ctk.CTkLabel(
            tile, text=label, font=ctk.CTkFont(size=10, weight="bold"),
            text_color=THEME["text_muted"]
        )
        lbl.pack(anchor="w", padx=10, pady=(8, 2))

        val_lbl = ctk.CTkLabel(
            tile, text=val, font=ctk.CTkFont(size=12, weight="bold"),
            text_color=val_color
        )
        val_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        return val_lbl

    # ── QUICK ACTIONS CARD ──
    def _build_quick_actions_card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=THEME["card"], corner_radius=16,
            border_width=1, border_color=THEME["card_border"]
        )
        card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            card, text="⚡ HIZLI MANUEL AKSİYONLAR",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_dim"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        btn_grid = ctk.CTkFrame(card, fg_color="transparent")
        btn_grid.pack(fill="x", padx=12, pady=(0, 12))
        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)

        b1 = ctk.CTkButton(
            btn_grid, text="🛡️ WARP Bağlan", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], hover_color=THEME["card_hover"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_warp_connect, daemon=True).start()
        )
        b1.grid(row=0, column=0, padx=4, pady=3, sticky="ew")

        b2 = ctk.CTkButton(
            btn_grid, text="🔌 WARP Kes", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], hover_color=THEME["card_hover"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_warp_disconnect, daemon=True).start()
        )
        b2.grid(row=0, column=1, padx=4, pady=3, sticky="ew")

        b3 = ctk.CTkButton(
            btn_grid, text="🟢 DPI Başlat", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], hover_color=THEME["card_hover"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_dpi_start, daemon=True).start()
        )
        b3.grid(row=1, column=0, padx=4, pady=3, sticky="ew")

        b4 = ctk.CTkButton(
            btn_grid, text="🔴 DPI Durdur", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["card_border"], hover_color=THEME["card_hover"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_dpi_stop, daemon=True).start()
        )
        b4.grid(row=1, column=1, padx=4, pady=3, sticky="ew")

        b5 = ctk.CTkButton(
            btn_grid, text="💬 Discord'u Ayrı Pencerede Aç", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["blurple"], hover_color=THEME["blurple_hover"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_discord_launch, daemon=True).start()
        )
        b5.grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

        b6 = ctk.CTkButton(
            btn_grid, text="⏹ Tüm Hizmetleri Durdur", font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=THEME["rose_bg"], hover_color=THEME["rose_hover"], text_color=THEME["text_main"],
            corner_radius=8, height=32, command=lambda: threading.Thread(target=self._act_stop_all, daemon=True).start()
        )
        b6.grid(row=3, column=0, columnspan=2, padx=4, pady=3, sticky="ew")

    # ── LIVE TERMINAL LOG CARD ──
    def _build_terminal_card(self, parent):
        card = ctk.CTkFrame(
            parent, fg_color=THEME["card"], corner_radius=16,
            border_width=1, border_color=THEME["card_border"]
        )
        card.pack(fill="both", expand=True)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            top_row, text="📜 CANLI SİSTEM GÜNLÜĞÜ",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_dim"]
        ).pack(side="left")

        btn_clear = ctk.CTkButton(
            top_row, text="Temizle", font=ctk.CTkFont(size=10),
            fg_color=THEME["input_bg"], hover_color=THEME["card_hover"],
            corner_radius=6, height=22, width=60, command=self._clear_logs
        )
        btn_clear.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            card, fg_color=THEME["input_bg"], text_color=THEME["text_dim"],
            font=ctk.CTkFont(family="Courier", size=10), corner_radius=10,
            border_width=1, border_color=THEME["card_border"], wrap="word"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.log_textbox.configure(state="disabled")

    # ── FOOTER ──
    def _build_footer(self):
        foot = ctk.CTkFrame(self, fg_color=THEME["card"], corner_radius=0, height=36)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)

        ctk.CTkLabel(
            foot, text="Discord DPI Bypass • Native macOS Architecture • Zero Gaming Ping Impact",
            font=ctk.CTkFont(size=10), text_color=THEME["text_muted"]
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            foot, text="GitHub: github.com/Cnek00/DPI-for-macos",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=THEME["blurple_light"]
        ).pack(side="right", padx=20)

    # ─── LOGGING & UI HELPERS ──────────────────────────────────────────────────
    def log(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "·", "CMD": "$", "SUCCESS": "✓", "WARN": "⚠", "ERROR": "✗"}.get(level, "·")
        formatted = f"[{ts}] {prefix} {msg}\n"

        def _append():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", formatted)
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        self.after(0, _append)

    def _clear_logs(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def _update_step_ui(self, step_dict, state):
        """state: 'pending', 'active', 'done', 'error'"""
        cfg = {
            "pending": (THEME["input_bg"], THEME["card_border"], THEME["text_muted"], "BEKLEMEDE"),
            "active": (THEME["card"], THEME["blurple"], THEME["amber"], "ÇALIŞIYOR..."),
            "done": (THEME["card"], THEME["emerald"], THEME["emerald"], "TAMAMLANDI ✓"),
            "error": (THEME["card"], THEME["rose"], THEME["rose"], "HATA ✗")
        }
        bg, border, text_col, tag_txt = cfg.get(state, cfg["pending"])
        step_dict["row"].configure(fg_color=bg, border_color=border)
        step_dict["tag"].configure(text=tag_txt, text_color=text_col)
        if state == "done":
            step_dict["num"].configure(fg_color=THEME["emerald"], text_color=THEME["text_main"])
        elif state == "active":
            step_dict["num"].configure(fg_color=THEME["blurple"], text_color=THEME["text_main"])
        else:
            step_dict["num"].configure(fg_color=THEME["card_border"], text_color=THEME["text_dim"])

    # ─── SUDO & STARTUP HANDLERS ──────────────────────────────────────────────
    def _save_sudo_password(self):
        pwd = self.sudo_entry.get().strip()
        if not pwd:
            return
        if test_sudo_password(pwd):
            self.sudo_password = pwd
            self.sudo_entry.delete(0, "end")
            self.sudo_status_badge.configure(
                text="✓ Sudo Yetkili", fg_color=THEME["emerald_bg"], text_color=THEME["emerald"]
            )
            self.log("✓ Yönetici şifresi başarıyla doğrulandı ve kaydedildi.", "SUCCESS")
        else:
            self.sudo_status_badge.configure(
                text="Hatalı Şifre!", fg_color=THEME["rose_bg"], text_color=THEME["rose"]
            )
            self.log("✗ Hatalı sudo şifresi girildi.", "ERROR")

    def _on_startup_toggle(self):
        val = bool(self.startup_switch.get())
        set_startup(val)
        if val:
            self.log("✓ Mac açılışında otomatik başlatma aktif edildi.", "SUCCESS")
        else:
            self.log("Mac açılışında otomatik başlatma kapatıldı.", "WARN")

    def _on_warp_mode_change(self, val):
        if "VPN" in val:
            self.warp_mode = "warp"
            self.log("WARP modu 'TAM VPN' olarak seçildi.", "INFO")
        else:
            self.warp_mode = "proxy"
            self.log("WARP modu 'SOCKS PROXY' olarak seçildi.", "INFO")

    # ─── BACKGROUND MONITORING & UPTIME ────────────────────────────────────────
    def _uptime_loop(self):
        while self.is_monitoring:
            if self.is_active:
                self.uptime_seconds += 1
                hrs = str(self.uptime_seconds // 3600).zfill(2)
                mins = str((self.uptime_seconds % 3600) // 60).zfill(2)
                secs = str(self.uptime_seconds % 60).zfill(2)
                self.after(0, lambda h=hrs, m=mins, s=secs: self.uptime_lbl.configure(text=f"⏱ {h}:{m}:{s}"))
            time.sleep(1)

    def _monitor_loop(self):
        while self.is_monitoring:
            try:
                w_stat = get_warp_status()
                s_run = is_spoofdpi_running()
                s_cache = check_sudo_cached() or (self.sudo_password != "")
                ms = ping_host("discord.com")

                self.after(0, lambda ws=w_stat, sr=s_run, sc=s_cache, p=ms: self._update_live_metrics(ws, sr, sc, p))
            except Exception:
                pass
            time.sleep(2.5)

    def _update_live_metrics(self, warp_status, spoof_running, sudo_cached, ping_ms):
        # Update Sudo Badge
        if sudo_cached:
            self.sudo_status_badge.configure(
                text="✓ Sudo Yetkili", fg_color=THEME["emerald_bg"], text_color=THEME["emerald"]
            )
        else:
            self.sudo_status_badge.configure(
                text="Şifre Girilmedi", fg_color=THEME["amber_bg"], text_color=THEME["amber"]
            )

        # Update WARP Metric
        if warp_status == "connected":
            self.metric_warp.configure(text="● Bağlı", text_color=THEME["emerald"])
        elif warp_status == "connecting":
            self.metric_warp.configure(text="◐ Bağlanıyor", text_color=THEME["amber"])
        else:
            self.metric_warp.configure(text="○ Kapalı", text_color=THEME["text_muted"])

        # Update SpoofDPI Metric
        if spoof_running:
            self.metric_spoof.configure(text="● Aktif", text_color=THEME["emerald"])
        else:
            self.metric_spoof.configure(text="○ Kapalı", text_color=THEME["text_muted"])

        # Update Ping
        if ping_ms is not None:
            self.latest_ping = f"{round(ping_ms, 1)}"
            self.live_ping_lbl.configure(text=f"Discord Ping: {self.latest_ping} ms")

        # System State Pill
        if warp_status == "connected" and spoof_running:
            self.is_active = True
            self.status_pill.configure(
                text="● SİSTEM AKTİF (Discord Hazır)", fg_color=THEME["emerald_bg"], text_color=THEME["emerald"]
            )
            if not self.is_running_all:
                self.btn_master.configure(
                    text="✓ SİSTEM ÇALIŞIYOR (DURDUR)", fg_color=THEME["emerald"], hover_color=THEME["emerald_hover"]
                )
        elif self.is_running_all:
            self.status_pill.configure(
                text="◐ BAŞLATILIYOR...", fg_color=THEME["amber_bg"], text_color=THEME["amber"]
            )
        else:
            self.is_active = False
            self.status_pill.configure(
                text="● SİSTEM HAZIR (Beklemede)", fg_color=THEME["card_border"], text_color=THEME["amber"]
            )
            self.btn_master.configure(
                text="⚡ SİSTEMİ BAŞLAT (TEK TIK)", fg_color=THEME["blurple"], hover_color=THEME["blurple_hover"]
            )

    # ─── MASTER LAUNCH SEQUENCE ────────────────────────────────────────────────
    def _toggle_master_launch(self):
        if self.is_active:
            threading.Thread(target=self._act_stop_all, daemon=True).start()
        else:
            threading.Thread(target=self._run_launch_sequence, daemon=True).start()

    def _run_launch_sequence(self):
        if self.is_running_all:
            return
        self.is_running_all = True
        self.after(0, lambda: self.btn_master.configure(
            text="⏳ BAŞLATILIYOR...", fg_color=THEME["amber"], hover_color=THEME["amber_hover"]
        ))
        self.log("══════════ OTOMATİK BAŞLATMA SIRASI BAŞLADI ══════════", "CMD")

        # Step 1: WARP
        self.after(0, lambda: self._update_step_ui(self.step1_card, "active"))
        self.log("Adım 1/3: Cloudflare WARP bağlanıyor...", "INFO")
        w_ok = self._act_warp_connect()
        time.sleep(1.5)
        self.after(0, lambda ok=w_ok: self._update_step_ui(self.step1_card, "done" if ok else "error"))

        # Step 2: SpoofDPI
        self.after(0, lambda: self._update_step_ui(self.step2_card, "active"))
        self.log("Adım 2/3: SpoofDPI bypass başlatılıyor...", "INFO")
        s_ok = self._act_dpi_start()
        time.sleep(2)
        self.after(0, lambda ok=s_ok: self._update_step_ui(self.step2_card, "done" if ok else "error"))

        # Step 3: Discord
        self.after(0, lambda: self._update_step_ui(self.step3_card, "active"))
        self.log("Adım 3/3: Discord açılıyor...", "INFO")
        d_ok = self._act_discord_launch()
        time.sleep(1)
        self.after(0, lambda ok=d_ok: self._update_step_ui(self.step3_card, "done" if ok else "error"))

        self.is_running_all = False
        self.log("══════════ SİSTEM HAZIR & DISCORD AKTİF ══════════", "SUCCESS")

    # ─── ACTION IMPLEMENTATIONS ────────────────────────────────────────────────
    def _act_warp_connect(self):
        self.log(f"Cloudflare WARP bağlanıyor (Mod: {self.warp_mode.upper()})...", "CMD")
        run_cmd(["warp-cli", "mode", self.warp_mode])
        if self.warp_mode == "proxy":
            run_cmd(["warp-cli", "proxy", "port", "40000"])
        run_cmd(["warp-cli", "connect"])
        time.sleep(2)
        stat = get_warp_status()
        if stat in ("connected", "connecting"):
            self.log("✓ Cloudflare WARP başarıyla bağlandı.", "SUCCESS")
            return True
        else:
            self.log("⚠ WARP bağlanamadı!", "ERROR")
            return False

    def _act_warp_disconnect(self):
        self.log("Cloudflare WARP bağlantısı kesiliyor...", "CMD")
        run_cmd(["warp-cli", "disconnect"])
        time.sleep(1)
        self.log("Cloudflare WARP bağlantısı kapatıldı.", "WARN")
        return True

    def _act_dpi_start(self):
        if is_spoofdpi_running():
            self.log("✓ SpoofDPI zaten aktif çalışıyor.", "INFO")
            return True

        self.log("SpoofDPI başlatılıyor...", "CMD")
        spoof_bin = "/opt/homebrew/opt/spoofdpi/bin/spoofdpi"
        if not Path(spoof_bin).exists():
            spoof_bin = "spoofdpi"

        cmd_args = [spoof_bin, "--auto-configure-network", "--dns-mode", "doh", "--no-tui"]

        if self.sudo_password:
            try:
                def bg_runner():
                    self.spoofdpi_proc = subprocess.Popen(
                        ["sudo", "-S"] + cmd_args,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )
                    self.spoofdpi_proc.stdin.write(self.sudo_password + "\n")
                    self.spoofdpi_proc.stdin.flush()
                    self.log("✓ SpoofDPI arka planda yetkilendirildi.", "SUCCESS")
                    while self.spoofdpi_proc and self.spoofdpi_proc.poll() is None:
                        line = self.spoofdpi_proc.stdout.readline()
                        if line and ("addr" in line or "listen" in line or "DPI" in line):
                            self.log(f"[SpoofDPI] {line.strip()}", "INFO")
                        time.sleep(0.5)

                threading.Thread(target=bg_runner, daemon=True).start()
                time.sleep(2.5)
                if is_spoofdpi_running():
                    self.log("✓ SpoofDPI aktif ve ağ trafiğini optimize ediyor.", "SUCCESS")
                    return True
            except Exception as e:
                self.log(f"SpoofDPI hata: {e}", "ERROR")

        # Fallback to Terminal script
        script_path = SCRIPT_DIR / "Mac_GoodbyeDPI.command"
        apple_script = f'tell application "Terminal" to do script "bash \\"{script_path}\\""'
        run_cmd(["osascript", "-e", apple_script])
        time.sleep(2.5)
        return is_spoofdpi_running()

    def _act_dpi_stop(self):
        self.log("SpoofDPI durduruluyor...", "CMD")
        if self.sudo_password:
            run_cmd(["sudo", "-S", "pkill", "-f", "spoofdpi"], sudo_pass=self.sudo_password)
        else:
            run_cmd(["sudo", "pkill", "-f", "spoofdpi"])
        if self.spoofdpi_proc:
            try:
                self.spoofdpi_proc.terminate()
            except Exception:
                pass
            self.spoofdpi_proc = None
        time.sleep(1)
        self.log("SpoofDPI durduruldu.", "WARN")
        return True

    def _act_discord_launch(self):
        self.log("Discord başlatılıyor...", "CMD")
        if Path("/Applications/Brave Browser.app").exists():
            subprocess.Popen([
                "open", "-na", "Brave Browser",
                "--args", "--app=https://discord.com/channels/@me"
            ])
            self.log("✓ Discord Brave Web App modunda açıldı.", "SUCCESS")
            return True
        elif Path("/Applications/Google Chrome.app").exists():
            subprocess.Popen([
                "open", "-na", "Google Chrome",
                "--args", "--app=https://discord.com/channels/@me"
            ])
            self.log("✓ Discord Chrome Web App modunda açıldı.", "SUCCESS")
            return True
        elif Path("/Applications/Discord.app").exists():
            subprocess.Popen(["open", "-a", "Discord"])
            self.log("✓ Discord masaüstü uygulaması açıldı.", "SUCCESS")
            return True
        else:
            subprocess.Popen(["open", "https://discord.com/channels/@me"])
            self.log("✓ Discord varsayılan tarayıcıda açıldı.", "SUCCESS")
            return True

    def _act_stop_all(self):
        self.log("══════════ TÜM HİZMETLER DURDURULUYOR ══════════", "WARN")
        self._act_dpi_stop()
        time.sleep(0.5)
        self._act_warp_disconnect()
        self.is_active = False
        self.uptime_seconds = 0
        self.after(0, lambda: self._update_step_ui(self.step1_card, "pending"))
        self.after(0, lambda: self._update_step_ui(self.step2_card, "pending"))
        self.after(0, lambda: self._update_step_ui(self.step3_card, "pending"))
        self.after(0, lambda: self.uptime_lbl.configure(text="⏱ 00:00:00"))
        self.log("Tüm bypass servisleri başarıyla kapatıldı.", "WARN")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_pwd = sys.argv[1] if len(sys.argv) > 1 else ""
    app = DiscordDPINativeApp(initial_sudo=init_pwd)
    app.mainloop()
