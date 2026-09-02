#!/usr/bin/env python3
"""
Discord DPI Bypass Launcher
macOS için Discord ping sorununu çözen otomatik başlatıcı
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
import sys
import json
from pathlib import Path
import datetime

# ─────────────────────────────────────────────
# Renk Paleti & Tasarım Sabitleri
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark":       "#0f1117",
    "bg_card":       "#1a1d27",
    "bg_card2":      "#1e2130",
    "accent_blue":   "#5865f2",
    "accent_green":  "#23a55a",
    "accent_yellow": "#f0b132",
    "accent_red":    "#ed4245",
    "accent_purple": "#7289da",
    "text_primary":  "#ffffff",
    "text_secondary":"#b5bac1",
    "text_muted":    "#6d737d",
    "border":        "#2d3142",
    "hover":         "#2b2d3e",
    "success_bg":    "#1a3a2a",
    "warning_bg":    "#3a2a0a",
    "error_bg":      "#3a1a1a",
    "step_active":   "#5865f2",
    "step_done":     "#23a55a",
    "step_pending":  "#2d3142",
}

FONTS = {
    "title":    ("SF Pro Display", 22, "bold"),
    "subtitle": ("SF Pro Display", 13),
    "label":    ("SF Pro Text", 12, "bold"),
    "body":     ("SF Pro Text", 11),
    "small":    ("SF Pro Text", 10),
    "mono":     ("SF Mono", 10),
    "button":   ("SF Pro Text", 12, "bold"),
    "step":     ("SF Pro Display", 14, "bold"),
}

# Fallback fontlar (SF Pro yoksa)
FONTS_FALLBACK = {
    "title":    ("Helvetica Neue", 22, "bold"),
    "subtitle": ("Helvetica Neue", 13),
    "label":    ("Helvetica Neue", 12, "bold"),
    "body":     ("Helvetica Neue", 11),
    "small":    ("Helvetica Neue", 10),
    "mono":     ("Courier New", 10),
    "button":   ("Helvetica Neue", 12, "bold"),
    "step":     ("Helvetica Neue", 14, "bold"),
}

# ─────────────────────────────────────────────
# Yardımcı Fonksiyonlar
# ─────────────────────────────────────────────
def get_script_dir():
    return Path(os.path.dirname(os.path.abspath(__file__)))

def is_warp_installed():
    result = subprocess.run(["which", "warp-cli"], capture_output=True, text=True)
    return result.returncode == 0

def is_spoofdpi_installed():
    result = subprocess.run(
        ["/opt/homebrew/opt/spoofdpi/bin/spoofdpi", "--version"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def get_warp_status():
    try:
        result = subprocess.run(["warp-cli", "status"], capture_output=True, text=True, timeout=3)
        if "Connected" in result.stdout:
            return "connected"
        elif "Connecting" in result.stdout:
            return "connecting"
        else:
            return "disconnected"
    except Exception:
        return "unknown"

def is_spoofdpi_running():
    result = subprocess.run(["pgrep", "-f", "spoofdpi"], capture_output=True, text=True)
    return result.returncode == 0

def is_brave_installed():
    brave_paths = [
        "/Applications/Brave Browser.app",
        "/Applications/Brave Browser Beta.app",
    ]
    return any(Path(p).exists() for p in brave_paths)

def is_discord_app_installed():
    discord_paths = [
        "/Applications/Discord.app",
    ]
    return any(Path(p).exists() for p in discord_paths)

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

# ─────────────────────────────────────────────
# Ana Uygulama
# ─────────────────────────────────────────────
class DiscordDPILauncher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Discord DPI Bypass")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_dark"])

        # Pencereyi ortala
        self.update_idletasks()
        w, h = 780, 680
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # State
        self.warp_mode = tk.StringVar(value="warp")
        self.spoofdpi_process = None
        self.start_time = None
        self.uptime_running = False
        self.log_messages = []

        # Step durumları
        self.step_states = {
            "warp":     "pending",   # pending | running | done | error
            "spoofdpi": "pending",
            "discord":  "pending",
        }

        self._build_ui()
        self._check_dependencies()
        self._start_status_polling()

    # ─── UI İnşaatı ─────────────────────────────
    def _build_ui(self):
        # ─── Header ───
        header = tk.Frame(self, bg=COLORS["bg_dark"], height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Logo alanı
        logo_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        logo_frame.pack(side="left", padx=24, pady=0, fill="y")

        # Discord ikonu (unicode)
        icon_label = tk.Label(
            logo_frame, text="🎮", font=("Arial", 32),
            bg=COLORS["bg_dark"], fg=COLORS["accent_purple"]
        )
        icon_label.pack(side="left", padx=(0, 12), pady=20)

        title_frame = tk.Frame(logo_frame, bg=COLORS["bg_dark"])
        title_frame.pack(side="left", pady=20)

        try:
            title_lbl = tk.Label(
                title_frame, text="Discord DPI Bypass",
                font=FONTS["title"], bg=COLORS["bg_dark"], fg=COLORS["text_primary"]
            )
        except Exception:
            title_lbl = tk.Label(
                title_frame, text="Discord DPI Bypass",
                font=FONTS_FALLBACK["title"], bg=COLORS["bg_dark"], fg=COLORS["text_primary"]
            )
        title_lbl.pack(anchor="w")

        try:
            sub_lbl = tk.Label(
                title_frame, text="macOS için sıfır ping optimizasyonu",
                font=FONTS["subtitle"], bg=COLORS["bg_dark"], fg=COLORS["text_secondary"]
            )
        except Exception:
            sub_lbl = tk.Label(
                title_frame, text="macOS için sıfır ping optimizasyonu",
                font=FONTS_FALLBACK["subtitle"], bg=COLORS["bg_dark"], fg=COLORS["text_secondary"]
            )
        sub_lbl.pack(anchor="w")

        # Sağ: Uptime + Durum
        right_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        right_frame.pack(side="right", padx=24, pady=0, fill="y")

        self.status_badge = tk.Label(
            right_frame, text="⬤  Hazır",
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_dark"], fg=COLORS["accent_yellow"]
        )
        self.status_badge.pack(anchor="e", pady=(22, 2))

        self.uptime_label = tk.Label(
            right_frame, text="",
            font=("Helvetica Neue", 10),
            bg=COLORS["bg_dark"], fg=COLORS["text_muted"]
        )
        self.uptime_label.pack(anchor="e")

        # ─── Ayırıcı ───
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

        # ─── Ana içerik (2 kolon) ───
        content = tk.Frame(self, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=20, pady=16)

        # Sol: Adımlar
        left = tk.Frame(content, bg=COLORS["bg_dark"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Sağ: Log & Kontroller
        right = tk.Frame(content, bg=COLORS["bg_dark"])
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self._build_steps(left)
        self._build_warp_options(left)
        self._build_quick_actions(left)
        self._build_log(right)
        self._build_system_status(right)

        # ─── Alt çubuk ───
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")
        bottom = tk.Frame(self, bg=COLORS["bg_dark"], height=56)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)

        self.launch_btn = tk.Button(
            bottom,
            text="🚀  Sistemi Başlat",
            font=("Helvetica Neue", 13, "bold"),
            bg=COLORS["accent_blue"],
            fg=COLORS["text_primary"],
            activebackground="#4752c4",
            activeforeground=COLORS["text_primary"],
            relief="flat",
            bd=0,
            padx=32,
            pady=10,
            cursor="hand2",
            command=self._launch_all
        )
        self.launch_btn.pack(side="left", padx=20, pady=10)

        self.discord_btn = tk.Button(
            bottom,
            text="💬  Discord'u Aç",
            font=("Helvetica Neue", 12, "bold"),
            bg=COLORS["accent_purple"],
            fg=COLORS["text_primary"],
            activebackground="#5a6fbf",
            activeforeground=COLORS["text_primary"],
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._launch_discord,
            state="disabled"
        )
        self.discord_btn.pack(side="left", padx=8, pady=10)

        stop_btn = tk.Button(
            bottom,
            text="⏹  Durdur",
            font=("Helvetica Neue", 12),
            bg=COLORS["bg_card2"],
            fg=COLORS["accent_red"],
            activebackground=COLORS["error_bg"],
            activeforeground=COLORS["accent_red"],
            relief="flat",
            bd=0,
            padx=24,
            pady=10,
            cursor="hand2",
            command=self._stop_all
        )
        stop_btn.pack(side="left", padx=0, pady=10)

        # Sağ alt: versiyon
        ver_lbl = tk.Label(
            bottom, text="v2.0  |  DPI Bypass",
            font=("Helvetica Neue", 9),
            bg=COLORS["bg_dark"], fg=COLORS["text_muted"]
        )
        ver_lbl.pack(side="right", padx=20)

    def _build_steps(self, parent):
        """3 adım göstergesi"""
        frame = tk.Frame(parent, bg=COLORS["bg_card"], bd=0, relief="flat")
        frame.pack(fill="x", pady=(0, 10))

        # Başlık
        hdr = tk.Frame(frame, bg=COLORS["bg_card"])
        hdr.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(
            hdr, text="📋  Başlatma Adımları",
            font=("Helvetica Neue", 12, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_primary"]
        ).pack(side="left")

        # Adımlar
        steps_data = [
            ("warp",     "1",  "Cloudflare WARP",  "VPN bağlantısı kurulacak"),
            ("spoofdpi", "2",  "SpoofDPI / GoodbyeDPI", "DPI atlama başlatılacak"),
            ("discord",  "3",  "Discord",           "Tarayıcıda açılacak"),
        ]

        self.step_widgets = {}
        for key, num, label, desc in steps_data:
            self.step_widgets[key] = self._create_step_widget(frame, key, num, label, desc)

        tk.Frame(frame, bg=COLORS["bg_card"], height=6).pack()

    def _create_step_widget(self, parent, key, num, label, desc):
        row = tk.Frame(parent, bg=COLORS["bg_card"], cursor="arrow")
        row.pack(fill="x", padx=14, pady=3)

        # Numara çemberi
        circle = tk.Label(
            row, text=num,
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["step_pending"],
            fg=COLORS["text_primary"],
            width=2, height=1,
            relief="flat"
        )
        circle.pack(side="left", padx=(0, 12))

        # Metin
        txt_frame = tk.Frame(row, bg=COLORS["bg_card"])
        txt_frame.pack(side="left", fill="x", expand=True)

        lbl = tk.Label(
            txt_frame, text=label,
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_primary"], anchor="w"
        )
        lbl.pack(anchor="w")

        desc_lbl = tk.Label(
            txt_frame, text=desc,
            font=("Helvetica Neue", 9),
            bg=COLORS["bg_card"], fg=COLORS["text_muted"], anchor="w"
        )
        desc_lbl.pack(anchor="w")

        # Durum ikonu
        status_lbl = tk.Label(
            row, text="○",
            font=("Arial", 16),
            bg=COLORS["bg_card"], fg=COLORS["text_muted"]
        )
        status_lbl.pack(side="right", padx=8)

        return {"circle": circle, "lbl": lbl, "desc": desc_lbl, "status": status_lbl}

    def _build_warp_options(self, parent):
        """WARP mod seçimi"""
        frame = tk.LabelFrame(
            parent, text="  ⚡  Cloudflare WARP Modu  ",
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
            bd=1, relief="flat",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        frame.pack(fill="x", pady=(0, 10))

        opts = [
            ("warp",  "🛡️  Tam VPN Modu",     "Tüm cihaz korunur"),
            ("proxy", "🔌  Proxy Modu",         "SOCKS5 127.0.0.1:40000"),
        ]
        for val, text, hint in opts:
            r = tk.Frame(frame, bg=COLORS["bg_card"])
            r.pack(fill="x", padx=16, pady=4)
            rb = tk.Radiobutton(
                r, text=text,
                variable=self.warp_mode, value=val,
                font=("Helvetica Neue", 11),
                bg=COLORS["bg_card"],
                fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_dark"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["text_primary"],
                cursor="hand2"
            )
            rb.pack(side="left")
            tk.Label(
                r, text=hint,
                font=("Helvetica Neue", 9),
                bg=COLORS["bg_card"], fg=COLORS["text_muted"]
            ).pack(side="left", padx=8)

        tk.Frame(frame, bg=COLORS["bg_card"], height=4).pack()

    def _build_quick_actions(self, parent):
        """Hızlı işlemler"""
        frame = tk.LabelFrame(
            parent, text="  🔧  Hızlı İşlemler  ",
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
            bd=1, relief="flat",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        frame.pack(fill="x", pady=(0, 0))

        btns = [
            ("WARP Bağlan",    self._connect_warp,    COLORS["accent_blue"]),
            ("WARP Kes",       self._disconnect_warp,  COLORS["accent_red"]),
            ("DPI Başlat",     self._start_spoofdpi,   COLORS["accent_green"]),
            ("DPI Durdur",     self._stop_spoofdpi,    COLORS["accent_yellow"]),
        ]

        grid = tk.Frame(frame, bg=COLORS["bg_card"])
        grid.pack(fill="x", padx=12, pady=8)

        for i, (txt, cmd, color) in enumerate(btns):
            b = tk.Button(
                grid, text=txt,
                font=("Helvetica Neue", 10, "bold"),
                bg=COLORS["bg_dark"],
                fg=color,
                activebackground=COLORS["hover"],
                activeforeground=color,
                relief="flat", bd=0,
                padx=12, pady=6,
                cursor="hand2",
                command=cmd,
                width=12
            )
            b.grid(row=i // 2, column=i % 2, padx=4, pady=3, sticky="ew")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        tk.Frame(frame, bg=COLORS["bg_card"], height=4).pack()

    def _build_log(self, parent):
        """Log paneli"""
        frame = tk.LabelFrame(
            parent, text="  📜  Sistem Günlüğü  ",
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
            bd=1, relief="flat",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        frame.pack(fill="both", expand=True, pady=(0, 10))

        # Log metin kutusu
        log_frame = tk.Frame(frame, bg=COLORS["bg_card"])
        log_frame.pack(fill="both", expand=True, padx=10, pady=8)

        self.log_text = tk.Text(
            log_frame,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            font=("Courier New", 9),
            relief="flat",
            bd=0,
            wrap="word",
            state="disabled",
            height=16,
            cursor="arrow",
            selectbackground=COLORS["accent_blue"],
            insertbackground=COLORS["text_primary"]
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Log renk etiketleri
        self.log_text.tag_configure("INFO",    foreground=COLORS["text_secondary"])
        self.log_text.tag_configure("SUCCESS", foreground=COLORS["accent_green"])
        self.log_text.tag_configure("WARNING", foreground=COLORS["accent_yellow"])
        self.log_text.tag_configure("ERROR",   foreground=COLORS["accent_red"])
        self.log_text.tag_configure("TIME",    foreground=COLORS["text_muted"])
        self.log_text.tag_configure("CMD",     foreground=COLORS["accent_blue"])

        # Temizle butonu
        clear_btn = tk.Button(
            frame, text="Günlüğü Temizle",
            font=("Helvetica Neue", 9),
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            activebackground=COLORS["hover"],
            activeforeground=COLORS["text_secondary"],
            relief="flat", bd=0, cursor="hand2",
            command=self._clear_log
        )
        clear_btn.pack(anchor="e", padx=10, pady=(0, 6))

    def _build_system_status(self, parent):
        """Sistem durumu kartları"""
        frame = tk.LabelFrame(
            parent, text="  📊  Sistem Durumu  ",
            font=("Helvetica Neue", 11, "bold"),
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
            bd=1, relief="flat",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        frame.pack(fill="x")

        grid = tk.Frame(frame, bg=COLORS["bg_card"])
        grid.pack(fill="x", padx=12, pady=8)

        self.status_cards = {}
        items = [
            ("warp_installed",   "WARP",      "Kurulu mu?"),
            ("warp_connected",   "WARP Bağlı","Bağlantı"),
            ("spoofdpi_inst",    "SpoofDPI",  "Kurulu mu?"),
            ("spoofdpi_run",     "DPI Aktif", "Çalışıyor?"),
            ("brave_installed",  "Brave",     "Kurulu mu?"),
            ("discord_inst",     "Discord",   "Kurulu mu?"),
        ]

        for i, (key, title, sub) in enumerate(items):
            card = tk.Frame(grid, bg=COLORS["bg_dark"], bd=0, relief="flat")
            card.grid(row=i // 3, column=i % 3, padx=4, pady=3, sticky="ew")

            tk.Label(
                card, text=title,
                font=("Helvetica Neue", 9, "bold"),
                bg=COLORS["bg_dark"], fg=COLORS["text_secondary"]
            ).pack(pady=(5, 0))

            indicator = tk.Label(
                card, text="●",
                font=("Arial", 14),
                bg=COLORS["bg_dark"], fg=COLORS["text_muted"]
            )
            indicator.pack()

            tk.Label(
                card, text=sub,
                font=("Helvetica Neue", 8),
                bg=COLORS["bg_dark"], fg=COLORS["text_muted"]
            ).pack(pady=(0, 5))

            self.status_cards[key] = indicator

        for c in range(3):
            grid.columnconfigure(c, weight=1)

        tk.Frame(frame, bg=COLORS["bg_card"], height=4).pack()

    # ─── Log Fonksiyonları ──────────────────────
    def _log(self, msg, level="INFO"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        tag = level
        prefix = {
            "INFO":    "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR":   "✗",
            "CMD":     "$",
        }.get(level, "·")

        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{now}] ", "TIME")
        self.log_text.insert("end", f"{prefix} {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self._log("Günlük temizlendi.", "INFO")

    # ─── Bağımlılık Kontrolü ────────────────────
    def _check_dependencies(self):
        self._log("Sistem bağımlılıkları kontrol ediliyor...", "INFO")
        threading.Thread(target=self._run_dependency_check, daemon=True).start()

    def _run_dependency_check(self):
        warp    = is_warp_installed()
        spoof   = is_spoofdpi_installed()
        brave   = is_brave_installed()
        discord = is_discord_app_installed()

        def update():
            self._update_status_card("warp_installed", warp)
            self._update_status_card("spoofdpi_inst",  spoof)
            self._update_status_card("brave_installed", brave)
            self._update_status_card("discord_inst",   discord)

            if not warp:
                self._log("Cloudflare WARP kurulu değil! brew install --cask cloudflare-warp", "WARNING")
            else:
                self._log("Cloudflare WARP kurulu ✓", "SUCCESS")

            if not spoof:
                self._log("SpoofDPI kurulu değil! brew install spoofdpi", "WARNING")
            else:
                self._log("SpoofDPI kurulu ✓", "SUCCESS")

            if not brave:
                self._log("Brave Browser bulunamadı (Discord için gerekli)", "WARNING")
            else:
                self._log("Brave Browser kurulu ✓", "SUCCESS")

        self.after(0, update)

    def _update_status_card(self, key, ok):
        if key in self.status_cards:
            color = COLORS["accent_green"] if ok else COLORS["accent_red"]
            self.status_cards[key].configure(fg=color)

    # ─── Durum Polling ──────────────────────────
    def _start_status_polling(self):
        def poll():
            while True:
                try:
                    warp_conn  = get_warp_status() == "connected"
                    spoof_run  = is_spoofdpi_running()
                    self.after(0, lambda w=warp_conn, s=spoof_run: self._update_live_status(w, s))
                except Exception:
                    pass
                time.sleep(5)

        threading.Thread(target=poll, daemon=True).start()

    def _update_live_status(self, warp_conn, spoof_run):
        self._update_status_card("warp_connected", warp_conn)
        self._update_status_card("spoofdpi_run",   spoof_run)

        if warp_conn and spoof_run:
            self.status_badge.configure(text="⬤  Aktif", fg=COLORS["accent_green"])
            self.discord_btn.configure(state="normal")
        elif warp_conn or spoof_run:
            self.status_badge.configure(text="⬤  Kısmi", fg=COLORS["accent_yellow"])
        else:
            self.status_badge.configure(text="⬤  Bekleniyor", fg=COLORS["accent_yellow"])

    # ─── Adım Güncelleme ────────────────────────
    def _set_step(self, key, state):
        """state: pending | running | done | error"""
        self.step_states[key] = state
        w = self.step_widgets.get(key)
        if not w:
            return

        cfg = {
            "pending": (COLORS["step_pending"], COLORS["text_muted"],   "○"),
            "running": (COLORS["accent_yellow"], COLORS["text_primary"], "◐"),
            "done":    (COLORS["step_done"],    COLORS["text_primary"],  "●"),
            "error":   (COLORS["accent_red"],   COLORS["text_primary"],  "✗"),
        }
        bg, fg, icon = cfg.get(state, cfg["pending"])
        w["circle"].configure(bg=bg, fg=fg)
        w["status"].configure(text=icon, fg=fg)

    # ─── Başlatma Fonksiyonları ─────────────────
    def _launch_all(self):
        """Tüm sistemi sırayla başlat"""
        self.launch_btn.configure(state="disabled", text="⏳  Başlatılıyor...")
        self._log("─── Tam başlatma başlıyor ───", "INFO")
        threading.Thread(target=self._run_full_launch, daemon=True).start()

    def _run_full_launch(self):
        # 1. WARP
        self.after(0, lambda: self._set_step("warp", "running"))
        self.after(0, lambda: self._log("WARP bağlantısı kuruluyor...", "CMD"))
        ok = self._do_connect_warp()
        self.after(0, lambda: self._set_step("warp", "done" if ok else "error"))
        if ok:
            self.after(0, lambda: self._log("WARP bağlandı ✓", "SUCCESS"))
        else:
            self.after(0, lambda: self._log("WARP bağlantısı başarısız!", "ERROR"))

        time.sleep(1.5)

        # 2. SpoofDPI
        self.after(0, lambda: self._set_step("spoofdpi", "running"))
        self.after(0, lambda: self._log("SpoofDPI başlatılıyor...", "CMD"))
        ok2 = self._do_start_spoofdpi()
        self.after(0, lambda: self._set_step("spoofdpi", "done" if ok2 else "error"))
        if ok2:
            self.after(0, lambda: self._log("SpoofDPI aktif ✓", "SUCCESS"))
        else:
            self.after(0, lambda: self._log("SpoofDPI başlatılamadı!", "ERROR"))

        time.sleep(2)

        # 3. Discord
        self.after(0, lambda: self._set_step("discord", "running"))
        self.after(0, lambda: self._log("Discord açılıyor...", "CMD"))
        ok3 = self._do_launch_discord()
        self.after(0, lambda: self._set_step("discord", "done" if ok3 else "error"))
        if ok3:
            self.after(0, lambda: self._log("Discord açıldı ✓", "SUCCESS"))
        else:
            self.after(0, lambda: self._log("Discord açılamadı!", "ERROR"))

        # Uptime sayacını başlat
        if ok and ok2:
            self.after(0, self._start_uptime)

        self.after(0, lambda: self.launch_btn.configure(
            state="normal",
            text="🚀  Sistemi Başlat"
        ))
        self.after(0, lambda: self._log("─── Başlatma tamamlandı ───", "SUCCESS"))

    # ─── WARP ───────────────────────────────────
    def _connect_warp(self):
        threading.Thread(target=self._do_connect_warp_log, daemon=True).start()

    def _do_connect_warp_log(self):
        self.after(0, lambda: self._log("WARP bağlanıyor...", "CMD"))
        ok = self._do_connect_warp()
        self.after(0, lambda: self._log("WARP bağlandı ✓" if ok else "WARP hatası!", "SUCCESS" if ok else "ERROR"))

    def _do_connect_warp(self):
        try:
            mode = self.warp_mode.get()
            subprocess.run(["warp-cli", "mode", mode], capture_output=True, timeout=10)
            if mode == "proxy":
                subprocess.run(["warp-cli", "proxy", "port", "40000"], capture_output=True, timeout=10)
            r = subprocess.run(["warp-cli", "connect"], capture_output=True, timeout=15)
            time.sleep(2)
            return get_warp_status() in ("connected", "connecting")
        except Exception as e:
            self.after(0, lambda: self._log(f"WARP hatası: {e}", "ERROR"))
            return False

    def _disconnect_warp(self):
        threading.Thread(target=self._do_disconnect_warp, daemon=True).start()

    def _do_disconnect_warp(self):
        self.after(0, lambda: self._log("WARP kesiliyor...", "CMD"))
        try:
            subprocess.run(["warp-cli", "disconnect"], capture_output=True, timeout=10)
            self.after(0, lambda: self._log("WARP bağlantısı kesildi.", "WARNING"))
        except Exception as e:
            self.after(0, lambda: self._log(f"WARP kes hatası: {e}", "ERROR"))

    # ─── SpoofDPI ───────────────────────────────
    def _start_spoofdpi(self):
        threading.Thread(target=self._do_start_spoofdpi_log, daemon=True).start()

    def _do_start_spoofdpi_log(self):
        self.after(0, lambda: self._log("SpoofDPI başlatılıyor...", "CMD"))
        ok = self._do_start_spoofdpi()
        self.after(0, lambda: self._log(
            "SpoofDPI aktif ✓" if ok else "SpoofDPI başlatılamadı!",
            "SUCCESS" if ok else "ERROR"
        ))

    def _do_start_spoofdpi(self):
        if is_spoofdpi_running():
            self.after(0, lambda: self._log("SpoofDPI zaten çalışıyor.", "INFO"))
            return True
        try:
            # osascript ile yeni Terminal penceresi aç ve spoofdpi'yi sudo ile çalıştır
            script_path = get_script_dir() / "Mac_GoodbyeDPI.command"
            if script_path.exists():
                subprocess.Popen([
                    "osascript", "-e",
                    f'tell application "Terminal" to do script "bash {script_path}"'
                ])
            else:
                subprocess.Popen([
                    "osascript", "-e",
                    'tell application "Terminal" to do script "sudo /opt/homebrew/opt/spoofdpi/bin/spoofdpi --auto-configure-network --dns-mode doh --no-tui"'
                ])
            time.sleep(3)
            return True
        except Exception as e:
            self.after(0, lambda: self._log(f"SpoofDPI hatası: {e}", "ERROR"))
            return False

    def _stop_spoofdpi(self):
        threading.Thread(target=self._do_stop_spoofdpi, daemon=True).start()

    def _do_stop_spoofdpi(self):
        self.after(0, lambda: self._log("SpoofDPI durduruluyor...", "CMD"))
        try:
            subprocess.run(["sudo", "pkill", "-f", "spoofdpi"], capture_output=True)
            self.after(0, lambda: self._log("SpoofDPI durduruldu.", "WARNING"))
        except Exception as e:
            self.after(0, lambda: self._log(f"SpoofDPI durdurma hatası: {e}", "ERROR"))

    # ─── Discord ────────────────────────────────
    def _launch_discord(self):
        threading.Thread(target=self._do_launch_discord_log, daemon=True).start()

    def _do_launch_discord_log(self):
        self.after(0, lambda: self._log("Discord açılıyor...", "CMD"))
        ok = self._do_launch_discord()
        self.after(0, lambda: self._log(
            "Discord açıldı ✓" if ok else "Discord açılamadı!",
            "SUCCESS" if ok else "ERROR"
        ))

    def _do_launch_discord(self):
        try:
            subprocess.Popen([
                "open", "-na", "Brave Browser",
                "--args", "--app=https://discord.com/channels/@me"
            ])
            return True
        except Exception:
            try:
                # Discord uygulaması varsa açmayı dene
                subprocess.Popen(["open", "-a", "Discord"])
                return True
            except Exception as e:
                self.after(0, lambda: self._log(f"Discord açılamadı: {e}", "ERROR"))
                return False

    # ─── Tümünü Durdur ──────────────────────────
    def _stop_all(self):
        if not messagebox.askyesno(
            "Onayla",
            "Tüm hizmetler durdurulacak.\nDevam etmek istiyor musunuz?",
            icon="warning"
        ):
            return
        threading.Thread(target=self._run_stop_all, daemon=True).start()

    def _run_stop_all(self):
        self.after(0, lambda: self._log("─── Tüm hizmetler durduruluyor ───", "WARNING"))
        self._do_stop_spoofdpi()
        time.sleep(0.5)
        self._do_disconnect_warp()
        time.sleep(0.5)

        for key in self.step_states:
            self.after(0, lambda k=key: self._set_step(k, "pending"))

        self._stop_uptime()
        self.after(0, lambda: self.discord_btn.configure(state="disabled"))
        self.after(0, lambda: self.status_badge.configure(
            text="⬤  Durduruldu", fg=COLORS["accent_red"]
        ))
        self.after(0, lambda: self._log("─── Tüm hizmetler durduruldu ───", "WARNING"))

    # ─── Uptime Sayacı ──────────────────────────
    def _start_uptime(self):
        self.start_time = time.time()
        self.uptime_running = True
        self._tick_uptime()

    def _stop_uptime(self):
        self.uptime_running = False
        self.start_time = None
        self.after(0, lambda: self.uptime_label.configure(text=""))

    def _tick_uptime(self):
        if self.uptime_running and self.start_time:
            elapsed = time.time() - self.start_time
            self.uptime_label.configure(text=f"Çalışma: {format_time(elapsed)}")
            self.after(1000, self._tick_uptime)


# ─────────────────────────────────────────────
# Giriş Noktası
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = DiscordDPILauncher()

    # Pencere ikonunu ayarla (macOS için)
    try:
        app.iconbitmap("")
    except Exception:
        pass

    app.mainloop()
