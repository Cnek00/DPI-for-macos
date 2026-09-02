#!/usr/bin/env python3
"""
Discord DPI Bypass Launcher — v3.0
macOS • Animasyonlu • Sudo Yönetimli • Startup Desteği
"""

import tkinter as tk
from tkinter import messagebox
import subprocess, threading, time, os, sys, math, plistlib
from pathlib import Path
import datetime

# ═══════════════════════════════════════════════════════════
#  TEMA
# ═══════════════════════════════════════════════════════════
C = {
    "bg":         "#0b0d14",
    "surface":    "#13151f",
    "surface2":   "#1a1d2e",
    "surface3":   "#212438",
    "border":     "#2a2d45",
    "border2":    "#353a5a",

    "blue":       "#5865f2",
    "blue_d":     "#3b45d4",
    "blue_glow":  "#2b3080",
    "purple":     "#7289da",
    "green":      "#3ba55c",
    "green_glow": "#1a5c30",
    "yellow":     "#faa81a",
    "yellow_glow":"#7a5008",
    "red":        "#ed4245",
    "red_glow":   "#7a1a1a",
    "teal":       "#00b0f4",

    "text":       "#e3e5e8",
    "text2":      "#b5bac1",
    "text3":      "#72767d",
    "white":      "#ffffff",
}

F_TITLE  = ("Helvetica Neue", 20, "bold")
F_HEAD   = ("Helvetica Neue", 13, "bold")
F_BODY   = ("Helvetica Neue", 11)
F_SMALL  = ("Helvetica Neue", 9)
F_MONO   = ("Courier New",    9)
F_BTN    = ("Helvetica Neue", 12, "bold")
F_BTN_SM = ("Helvetica Neue", 10, "bold")

SCRIPT_DIR     = Path(os.path.dirname(os.path.abspath(__file__)))
LAUNCHAGENT    = Path.home() / "Library/LaunchAgents/com.discord.dpibypass.plist"
PLIST_LABEL    = "com.discord.dpibypass"

# ═══════════════════════════════════════════════════════════
#  YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════
def run(cmd, sudo_pass=None, timeout=10):
    try:
        if sudo_pass and cmd[0] == "sudo":
            proc = subprocess.Popen(
                cmd, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = proc.communicate(
                input=(sudo_pass + "\n").encode(), timeout=timeout
            )
            return proc.returncode == 0, out.decode(), err.decode()
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.returncode == 0, r.stdout, r.stderr
    except Exception as e:
        return False, "", str(e)

def warp_installed():
    ok, _, _ = run(["which", "warp-cli"])
    return ok

def spoofdpi_installed():
    return Path("/opt/homebrew/opt/spoofdpi/bin/spoofdpi").exists()

def brave_installed():
    return Path("/Applications/Brave Browser.app").exists()

def warp_status():
    ok, out, _ = run(["warp-cli", "status"])
    if not ok:
        return "unknown"
    if "Connected" in out:
        return "connected"
    if "Connecting" in out:
        return "connecting"
    return "disconnected"

def spoofdpi_running():
    ok, _, _ = run(["pgrep", "-f", "spoofdpi"])
    return ok

def verify_sudo(password):
    proc = subprocess.Popen(
        ["sudo", "-S", "true"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _, err = proc.communicate(input=(password + "\n").encode(), timeout=5)
    return proc.returncode == 0

def startup_installed():
    return LAUNCHAGENT.exists()

def install_startup(launcher_path):
    plist = {
        "Label": PLIST_LABEL,
        "ProgramArguments": ["/usr/bin/python3", str(launcher_path)],
        "RunAtLoad": True,
        "KeepAlive": False,
    }
    LAUNCHAGENT.parent.mkdir(parents=True, exist_ok=True)
    with open(LAUNCHAGENT, "wb") as f:
        plistlib.dump(plist, f)
    run(["launchctl", "load", str(LAUNCHAGENT)])

def uninstall_startup():
    if LAUNCHAGENT.exists():
        run(["launchctl", "unload", str(LAUNCHAGENT)])
        LAUNCHAGENT.unlink()

# ═══════════════════════════════════════════════════════════
#  ANIMATED CANVAS DOT  (canlı gösterge)
# ═══════════════════════════════════════════════════════════
class PulseDot(tk.Canvas):
    """Animasyonlu nefes alan nokta göstergesi"""
    STATES = {
        "idle":    (C["text3"],  C["text3"],  False),
        "active":  (C["yellow"], C["yellow_glow"], True),
        "ok":      (C["green"],  C["green_glow"],  True),
        "error":   (C["red"],    C["red_glow"],    False),
        "running": (C["blue"],   C["blue_glow"],   True),
    }

    def __init__(self, master, size=14, **kw):
        super().__init__(master, width=size+8, height=size+8,
                         bg=kw.pop("bg", C["surface"]),
                         highlightthickness=0, **kw)
        self.size = size
        self._state = "idle"
        self._phase = 0.0
        self._animating = False
        self._draw()

    def set_state(self, state):
        self._state = state
        color, glow, animate = self.STATES.get(state, self.STATES["idle"])
        if animate and not self._animating:
            self._animating = True
            self._animate()
        elif not animate:
            self._animating = False
            self._phase = 0.0
            self._draw()

    def _draw(self):
        self.delete("all")
        color, glow, _ = self.STATES.get(self._state, self.STATES["idle"])
        cx = (self.winfo_reqwidth() or self.size+8) / 2
        cy = (self.winfo_reqheight() or self.size+8) / 2
        r  = self.size / 2
        # glow halkası
        if self._animating:
            alpha = 0.4 + 0.4 * math.sin(self._phase)
            gr = r + 3 + 2 * math.sin(self._phase)
            # tkinter Canvas hex renk trick
            self.create_oval(cx-gr, cy-gr, cx+gr, cy+gr,
                             fill=glow, outline="", tags="glow")
        # ana nokta
        self.create_oval(cx-r, cy-r, cx+r, cy+r,
                         fill=color, outline="", tags="dot")

    def _animate(self):
        if not self._animating:
            return
        self._phase += 0.12
        self._draw()
        self.after(40, self._animate)

# ═══════════════════════════════════════════════════════════
#  CUSTOM TOGGLE SWITCH
# ═══════════════════════════════════════════════════════════
class ToggleSwitch(tk.Canvas):
    def __init__(self, master, command=None, initial=False, **kw):
        w, h = 46, 24
        super().__init__(master, width=w, height=h,
                         bg=kw.pop("bg", C["surface"]),
                         highlightthickness=0, cursor="hand2", **kw)
        self.w, self.h = w, h
        self._on = initial
        self._command = command
        self._anim_x = w - h//2 - 2 if initial else h//2 + 2
        self.bind("<Button-1>", self._toggle)
        self._draw()

    @property
    def is_on(self):
        return self._on

    def _toggle(self, _=None):
        self._on = not self._on
        target = self.w - self.h//2 - 2 if self._on else self.h//2 + 2
        self._animate_to(target)
        if self._command:
            self._command(self._on)

    def set(self, value):
        if value != self._on:
            self._toggle()

    def _animate_to(self, target):
        diff = target - self._anim_x
        if abs(diff) < 1:
            self._anim_x = target
            self._draw()
            return
        self._anim_x += diff * 0.3
        self._draw()
        self.after(16, lambda: self._animate_to(target))

    def _draw(self):
        self.delete("all")
        r = self.h // 2
        bg = C["blue"] if self._on else C["border"]
        # track
        self.create_oval(0, 0, self.h, self.h, fill=bg, outline="")
        self.create_rectangle(r, 0, self.w - r, self.h, fill=bg, outline="")
        self.create_oval(self.w-self.h, 0, self.w, self.h, fill=bg, outline="")
        # thumb
        cx = self._anim_x
        cy = self.h // 2
        cr = r - 3
        self.create_oval(cx-cr, cy-cr, cx+cr, cy+cr,
                         fill=C["white"], outline="")

# ═══════════════════════════════════════════════════════════
#  STEP ROW
# ═══════════════════════════════════════════════════════════
class StepRow(tk.Frame):
    ICONS = {"idle":"○", "running":"◌", "ok":"✓", "error":"✗"}

    def __init__(self, master, number, title, subtitle, **kw):
        super().__init__(master, bg=kw.pop("bg", C["surface2"]), **kw)
        self._state = "idle"

        # Sol numaralı daire (Canvas)
        self.num_cv = tk.Canvas(self, width=32, height=32,
                                bg=self["bg"], highlightthickness=0)
        self.num_cv.pack(side="left", padx=(12,10), pady=8)
        self._num = number
        self._draw_num()

        # Metin
        txt = tk.Frame(self, bg=self["bg"])
        txt.pack(side="left", fill="x", expand=True)
        self.title_lbl = tk.Label(txt, text=title, font=F_HEAD,
                                  bg=self["bg"], fg=C["text"], anchor="w")
        self.title_lbl.pack(anchor="w")
        self.sub_lbl = tk.Label(txt, text=subtitle, font=F_SMALL,
                                bg=self["bg"], fg=C["text3"], anchor="w")
        self.sub_lbl.pack(anchor="w")

        # Sağ pulse dot
        self.dot = PulseDot(self, bg=self["bg"])
        self.dot.pack(side="right", padx=14)

    def _draw_num(self):
        self.num_cv.delete("all")
        colors = {
            "idle":    (C["surface3"], C["text3"]),
            "running": (C["blue"],     C["white"]),
            "ok":      (C["green"],    C["white"]),
            "error":   (C["red"],      C["white"]),
        }
        bg, fg = colors.get(self._state, colors["idle"])
        self.num_cv.create_oval(1,1,31,31, fill=bg, outline=C["border"])
        self.num_cv.create_text(16,16, text=str(self._num),
                                 font=("Helvetica Neue",11,"bold"), fill=fg)

    def set_state(self, state):
        self._state = state
        self._draw_num()
        self.dot.set_state(state)
        c = {"idle":C["text3"],"running":C["yellow"],"ok":C["green"],"error":C["red"]}
        self.title_lbl.configure(fg=c.get(state, C["text"]))

# ═══════════════════════════════════════════════════════════
#  ŞİFRE DİYALOĞU
# ═══════════════════════════════════════════════════════════
class PasswordDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.result = None
        self.title("Sistem Şifresi")
        self.resizable(False, False)
        self.configure(bg=C["surface"])
        self.grab_set()
        self.focus_set()

        # Ortala
        self.update_idletasks()
        w, h = 400, 310
        px = master.winfo_x() + (master.winfo_width()  - w) // 2
        py = master.winfo_y() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")

        self._build()
        self.bind("<Return>", lambda _: self._submit())
        self.bind("<Escape>", lambda _: self.destroy())

    def _build(self):
        # İkon + başlık
        top = tk.Frame(self, bg=C["surface"])
        top.pack(fill="x", padx=28, pady=(28,0))

        tk.Label(top, text="🔐", font=("Arial",36),
                 bg=C["surface"], fg=C["blue"]).pack()
        tk.Label(top, text="Sistem Şifresi Gerekiyor",
                 font=F_HEAD, bg=C["surface"], fg=C["text"]).pack(pady=(4,0))
        tk.Label(top,
                 text="SpoofDPI, ağ ayarlarını değiştirmek için\nsudo yetkisi gerektirir. Şifre sadece\noturum boyunca bellekte tutulur.",
                 font=F_SMALL, bg=C["surface"], fg=C["text3"],
                 justify="center").pack(pady=(8,0))

        # Şifre alanı
        field_frame = tk.Frame(self, bg=C["border"], bd=0)
        field_frame.pack(fill="x", padx=28, pady=18)

        inner = tk.Frame(field_frame, bg=C["surface3"])
        inner.pack(fill="x", padx=1, pady=1)

        tk.Label(inner, text="🔑 ", font=("Arial",12),
                 bg=C["surface3"], fg=C["text3"]).pack(side="left", padx=8)
        self.pw_var = tk.StringVar()
        self.entry = tk.Entry(inner, textvariable=self.pw_var, show="●",
                              font=("Helvetica Neue",13),
                              bg=C["surface3"], fg=C["text"],
                              insertbackground=C["blue"],
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=10)
        self.entry.focus_set()

        # Hata etiketi
        self.err_lbl = tk.Label(self, text="", font=F_SMALL,
                                bg=C["surface"], fg=C["red"])
        self.err_lbl.pack()

        # Butonlar
        btns = tk.Frame(self, bg=C["surface"])
        btns.pack(fill="x", padx=28, pady=(4,24))

        tk.Button(btns, text="Atla", font=F_BTN_SM,
                  bg=C["surface3"], fg=C["text3"],
                  activebackground=C["border"], activeforeground=C["text"],
                  relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
                  command=self.destroy).pack(side="left")

        tk.Button(btns, text="Devam Et →", font=F_BTN_SM,
                  bg=C["blue"], fg=C["white"],
                  activebackground=C["blue_d"], activeforeground=C["white"],
                  relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
                  command=self._submit).pack(side="right")

    def _submit(self):
        pw = self.pw_var.get().strip()
        if not pw:
            self.err_lbl.configure(text="Şifre boş olamaz")
            return
        # Doğrula
        self.err_lbl.configure(text="⟳ Doğrulanıyor...", fg=C["yellow"])
        self.update()
        try:
            ok = verify_sudo(pw)
        except Exception:
            ok = False
        if ok:
            self.result = pw
            self.destroy()
        else:
            self.err_lbl.configure(text="✗ Hatalı şifre, tekrar dene", fg=C["red"])
            self.pw_var.set("")
            self.entry.focus_set()

# ═══════════════════════════════════════════════════════════
#  LOG PANEL
# ═══════════════════════════════════════════════════════════
class LogPanel(tk.Frame):
    TAG_CFG = {
        "INFO":    C["text3"],
        "CMD":     C["blue"],
        "OK":      C["green"],
        "WARN":    C["yellow"],
        "ERR":     C["red"],
        "HEAD":    C["purple"],
        "TIME":    C["text3"],
    }

    def __init__(self, master, **kw):
        super().__init__(master, bg=C["surface"], **kw)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=C["surface"])
        hdr.pack(fill="x", padx=12, pady=(10,4))
        tk.Label(hdr, text="📜  Sistem Günlüğü", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        tk.Button(hdr, text="Temizle", font=F_SMALL,
                  bg=C["surface3"], fg=C["text3"],
                  activebackground=C["border"],
                  relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
                  command=self.clear).pack(side="right")

        frame = tk.Frame(self, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.txt = tk.Text(frame, bg=C["bg"], fg=C["text"],
                           font=F_MONO, relief="flat", bd=0,
                           wrap="word", state="disabled",
                           selectbackground=C["blue"],
                           insertbackground=C["blue"],
                           cursor="arrow")
        self.txt.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(frame, command=self.txt.yview,
                          bg=C["surface2"], troughcolor=C["bg"],
                          relief="flat", bd=0, width=6)
        sb.pack(side="right", fill="y")
        self.txt.configure(yscrollcommand=sb.set)

        for tag, color in self.TAG_CFG.items():
            self.txt.tag_configure(tag, foreground=color)

    def log(self, msg, level="INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO":"·","CMD":"$","OK":"✓","WARN":"⚠","ERR":"✗","HEAD":"▶"}.get(level,"·")
        self.txt.configure(state="normal")
        self.txt.insert("end", f"[{ts}] ", "TIME")
        self.txt.insert("end", f"{prefix} {msg}\n", level)
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def clear(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0","end")
        self.txt.configure(state="disabled")

# ═══════════════════════════════════════════════════════════
#  STATUS CARD
# ═══════════════════════════════════════════════════════════
class StatusCard(tk.Frame):
    def __init__(self, master, label, **kw):
        super().__init__(master, bg=C["surface3"],
                         highlightbackground=C["border"],
                         highlightthickness=1, **kw)
        self.dot = PulseDot(self, size=10, bg=C["surface3"])
        self.dot.pack(pady=(8,2))
        tk.Label(self, text=label, font=F_SMALL,
                 bg=C["surface3"], fg=C["text3"]).pack(pady=(0,8))

    def set(self, ok):
        self.dot.set_state("ok" if ok else "idle")

    def set_state(self, state):
        self.dot.set_state(state)

# ═══════════════════════════════════════════════════════════
#  GLASSY BUTTON
# ═══════════════════════════════════════════════════════════
def make_btn(parent, text, command, color=C["blue"], width=None):
    cfg = dict(
        text=text, command=command,
        font=F_BTN_SM,
        bg=color, fg=C["white"],
        activebackground=C["blue_d"],
        activeforeground=C["white"],
        relief="flat", bd=0,
        padx=14, pady=7,
        cursor="hand2",
    )
    if width:
        cfg["width"] = width
    return tk.Button(parent, **cfg)

# ═══════════════════════════════════════════════════════════
#  ANA UYGULAMA
# ═══════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord DPI Bypass")
        self.resizable(False, False)
        self.configure(bg=C["bg"])

        w, h = 860, 700
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # State
        self._sudo_pass  = None
        self._warp_mode  = tk.StringVar(value="warp")
        self._start_up   = tk.BooleanVar(value=startup_installed())
        self._uptime_s   = 0
        self._uptime_run = False

        self._build_ui()
        self._check_deps()
        self._poll_status()

        # Şifre diyaloğunu biraz geciktirerek aç
        self.after(600, self._ask_password)

    # ────────────────────────── UI ────────────────────────────
    def _build_ui(self):
        self._build_header()
        sep = tk.Frame(self, bg=C["border"], height=1)
        sep.pack(fill="x")
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)
        self._build_left(body)
        self._build_right(body)
        self._build_footer()

    # ── Header ───────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=C["surface"], height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Sol logo
        left = tk.Frame(hdr, bg=C["surface"])
        left.pack(side="left", fill="y", padx=20)

        # Animasyonlu merkez nokta
        self._hdr_dot = PulseDot(left, size=16, bg=C["surface"])
        self._hdr_dot.pack(side="left", padx=(0,12), pady=24)
        self._hdr_dot.set_state("active")

        ttl = tk.Frame(left, bg=C["surface"])
        ttl.pack(side="left", pady=14)
        tk.Label(ttl, text="Discord  DPI Bypass",
                 font=("Helvetica Neue",18,"bold"),
                 bg=C["surface"], fg=C["white"]).pack(anchor="w")
        tk.Label(ttl, text="macOS • Sıfır Ping Optimizasyonu",
                 font=F_SMALL, bg=C["surface"], fg=C["text3"]).pack(anchor="w")

        # Sağ: durum + uptime
        right = tk.Frame(hdr, bg=C["surface"])
        right.pack(side="right", padx=20, fill="y")

        self._status_lbl = tk.Label(right, text="⬤  Hazır",
                                    font=("Helvetica Neue",11,"bold"),
                                    bg=C["surface"], fg=C["yellow"])
        self._status_lbl.pack(anchor="e", pady=(18,2))

        self._uptime_lbl = tk.Label(right, text="",
                                    font=F_SMALL,
                                    bg=C["surface"], fg=C["text3"])
        self._uptime_lbl.pack(anchor="e")

        # Sudo durum etiketi
        self._sudo_lbl = tk.Label(right, text="🔒 Şifre yok",
                                  font=F_SMALL, bg=C["surface"], fg=C["red"])
        self._sudo_lbl.pack(anchor="e")

    # ── Sol Panel ────────────────────────────────────────────
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(16,8), pady=16)

        self._build_steps(left)
        self._build_warp_opts(left)
        self._build_settings_card(left)

    # ── Adımlar ─────────────────────────────────────────────
    def _build_steps(self, parent):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0,10))

        hdr = tk.Frame(card, bg=C["surface"])
        hdr.pack(fill="x", padx=14, pady=(12,6))
        tk.Label(hdr, text="📋  Başlatma Sırası", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        tk.Label(hdr, text="Otomatik sıralı yürütme", font=F_SMALL,
                 bg=C["surface"], fg=C["text3"]).pack(side="right")

        steps_data = [
            (1, "Cloudflare WARP",  "VPN tüneli aktif edilecek"),
            (2, "SpoofDPI",         "DPI atlama başlatılacak"),
            (3, "Discord",          "Brave Browser üzerinden açılacak"),
        ]
        self._steps = {}
        for num, title, sub in steps_data:
            key = ["warp","spoof","discord"][num-1]
            row = StepRow(card, num, title, sub, bg=C["surface2"])
            row.pack(fill="x", padx=8, pady=3)
            # ayırıcı çizgi
            if num < 3:
                tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=20)
            self._steps[key] = row

        tk.Frame(card, bg=C["surface"], height=8).pack()

    # ── WARP Seçenekleri ────────────────────────────────────
    def _build_warp_opts(self, parent):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0,10))

        tk.Label(card, text="⚡  WARP Modu", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=14, pady=(12,6))

        opts = [
            ("warp",  "🛡️  Tam VPN",   "Tüm trafik korunur"),
            ("proxy", "🔌  Proxy",      "SOCKS5 :40000"),
        ]
        for val, lbl, hint in opts:
            row = tk.Frame(card, bg=C["surface"])
            row.pack(fill="x", padx=14, pady=3)

            rb = tk.Radiobutton(row, text=lbl, variable=self._warp_mode, value=val,
                                font=("Helvetica Neue",11),
                                bg=C["surface"], fg=C["text"],
                                selectcolor=C["bg"],
                                activebackground=C["surface"],
                                activeforeground=C["text"],
                                cursor="hand2")
            rb.pack(side="left")

            tk.Label(row, text=hint, font=F_SMALL,
                     bg=C["surface"], fg=C["text3"]).pack(side="right", padx=4)

        tk.Frame(card, bg=C["surface"], height=6).pack()

    # ── Ayarlar Kartı ────────────────────────────────────────
    def _build_settings_card(self, parent):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0,0))

        tk.Label(card, text="⚙️  Ayarlar", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=14, pady=(12,8))

        # — Başlangıçta aç toggle —
        row1 = tk.Frame(card, bg=C["surface"])
        row1.pack(fill="x", padx=14, pady=(0,8))

        txt_f = tk.Frame(row1, bg=C["surface"])
        txt_f.pack(side="left", fill="x", expand=True)
        tk.Label(txt_f, text="Başlangıçta Otomatik Aç",
                 font=("Helvetica Neue",11), bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(txt_f, text="Mac açıldığında bu uygulama otomatik başlar",
                 font=F_SMALL, bg=C["surface"], fg=C["text3"]).pack(anchor="w")

        self._startup_toggle = ToggleSwitch(
            row1, command=self._on_startup_toggle,
            initial=startup_installed(), bg=C["surface"]
        )
        self._startup_toggle.pack(side="right")

        tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=10)

        # — Şifreyi yenile —
        row2 = tk.Frame(card, bg=C["surface"])
        row2.pack(fill="x", padx=14, pady=8)

        txt_f2 = tk.Frame(row2, bg=C["surface"])
        txt_f2.pack(side="left", fill="x", expand=True)
        tk.Label(txt_f2, text="Sudo Şifresi",
                 font=("Helvetica Neue",11), bg=C["surface"], fg=C["text"]).pack(anchor="w")
        self._pw_status_lbl = tk.Label(txt_f2,
                                        text="Şifre girilmedi" if not self._sudo_pass else "✓ Şifre aktif",
                                        font=F_SMALL, bg=C["surface"],
                                        fg=C["red"] if not self._sudo_pass else C["green"])
        self._pw_status_lbl.pack(anchor="w")

        make_btn(row2, "🔐 Şifre Gir", self._ask_password,
                 color=C["surface3"]).pack(side="right")

        tk.Frame(card, bg=C["surface"], height=4).pack()

    # ── Sağ Panel ────────────────────────────────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=C["bg"])
        right.pack(side="right", fill="both", expand=True, padx=(8,16), pady=16)

        self._build_status_cards(right)
        self._build_quick_actions(right)
        self._log = LogPanel(right)
        self._log.pack(fill="both", expand=True)

    # ── Durum Kartları ──────────────────────────────────────
    def _build_status_cards(self, parent):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0,10))

        tk.Label(card, text="📊  Sistem Durumu", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=14, pady=(10,6))

        grid = tk.Frame(card, bg=C["surface"])
        grid.pack(fill="x", padx=10, pady=(0,10))

        items = [
            ("warp_inst",  "WARP Kurulu"),
            ("warp_conn",  "WARP Bağlı"),
            ("dpi_inst",   "DPI Kurulu"),
            ("dpi_run",    "DPI Aktif"),
            ("brave",      "Brave"),
            ("sudo",       "Sudo Hazır"),
        ]
        self._cards = {}
        for i, (key, lbl) in enumerate(items):
            sc = StatusCard(grid, lbl)
            sc.grid(row=i//3, column=i%3, padx=4, pady=3, sticky="nsew")
            self._cards[key] = sc
        for c in range(3):
            grid.columnconfigure(c, weight=1)

    # ── Hızlı İşlemler ──────────────────────────────────────
    def _build_quick_actions(self, parent):
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=(0,10))

        tk.Label(card, text="🔧  Hızlı İşlemler", font=F_HEAD,
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", padx=14, pady=(10,6))

        grid = tk.Frame(card, bg=C["surface"])
        grid.pack(fill="x", padx=10, pady=(0,10))

        actions = [
            ("WARP Bağlan",  self._act_warp_connect,     C["blue"]),
            ("WARP Kes",     self._act_warp_disconnect,   C["surface3"]),
            ("DPI Başlat",   self._act_dpi_start,         C["green"]),
            ("DPI Durdur",   self._act_dpi_stop,          C["surface3"]),
        ]
        for i, (lbl, cmd, col) in enumerate(actions):
            b = make_btn(grid, lbl, cmd, color=col)
            b.grid(row=i//2, column=i%2, padx=4, pady=3, sticky="ew")
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    # ── Footer ───────────────────────────────────────────────
    def _build_footer(self):
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        foot = tk.Frame(self, bg=C["surface"], height=60)
        foot.pack(fill="x")
        foot.pack_propagate(False)

        # Ana başlat
        self._launch_btn = tk.Button(
            foot, text="🚀  Sistemi Başlat",
            font=("Helvetica Neue",13,"bold"),
            bg=C["blue"], fg=C["white"],
            activebackground=C["blue_d"], activeforeground=C["white"],
            relief="flat", bd=0, padx=32, pady=10, cursor="hand2",
            command=self._launch_all
        )
        self._launch_btn.pack(side="left", padx=18, pady=10)

        # Discord Aç
        self._discord_btn = tk.Button(
            foot, text="💬  Discord'u Aç",
            font=F_BTN,
            bg=C["purple"], fg=C["white"],
            activebackground="#5a6fbf", activeforeground=C["white"],
            relief="flat", bd=0, padx=22, pady=10, cursor="hand2",
            command=self._act_discord,
            state="normal"
        )
        self._discord_btn.pack(side="left", padx=0, pady=10)

        # Durdur
        tk.Button(
            foot, text="⏹  Durdur",
            font=F_BTN,
            bg=C["surface3"], fg=C["red"],
            activebackground=C["border"], activeforeground=C["red"],
            relief="flat", bd=0, padx=22, pady=10, cursor="hand2",
            command=self._stop_all
        ).pack(side="left", padx=10, pady=10)

        # Sağ: versiyon
        tk.Label(foot, text="v3.0 • DPI Bypass",
                 font=F_SMALL, bg=C["surface"], fg=C["text3"]
                 ).pack(side="right", padx=18)

    # ════════════════════════════════════════════════════════
    #  ŞİFRE
    # ════════════════════════════════════════════════════════
    def _ask_password(self):
        dlg = PasswordDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self._sudo_pass = dlg.result
            self._sudo_lbl.configure(text="🔓 Şifre aktif", fg=C["green"])
            self._pw_status_lbl.configure(text="✓ Şifre aktif", fg=C["green"])
            self._cards["sudo"].set(True)
            self._log.log("Sudo şifresi doğrulandı ✓", "OK")
        else:
            self._log.log("Şifre girilmedi — sudo gerektiren işlemler çalışmayabilir", "WARN")

    # ════════════════════════════════════════════════════════
    #  STARTUP TOGGLE
    # ════════════════════════════════════════════════════════
    def _on_startup_toggle(self, state):
        launcher = SCRIPT_DIR / "discord_launcher.py"
        if state:
            install_startup(launcher)
            self._log.log("Başlangıçta otomatik açılma aktif ✓", "OK")
        else:
            uninstall_startup()
            self._log.log("Başlangıç özelliği kapatıldı", "WARN")

    # ════════════════════════════════════════════════════════
    #  BAĞIMLILIK KONTROLÜ
    # ════════════════════════════════════════════════════════
    def _check_deps(self):
        def _run():
            items = {
                "warp_inst": warp_installed,
                "dpi_inst":  spoofdpi_installed,
                "brave":     brave_installed,
            }
            for key, fn in items.items():
                ok = fn()
                self.after(0, lambda k=key, v=ok: self._cards[k].set(v))
                lbl = {"warp_inst":"WARP","dpi_inst":"SpoofDPI","brave":"Brave"}[key]
                lvl = "OK" if ok else "WARN"
                msg = f"{lbl} {'kurulu ✓' if ok else 'kurulu değil!'}"
                self.after(0, lambda m=msg, l=lvl: self._log.log(m, l))
        threading.Thread(target=_run, daemon=True).start()

    # ════════════════════════════════════════════════════════
    #  STATUS POLLING
    # ════════════════════════════════════════════════════════
    def _poll_status(self):
        def _run():
            while True:
                try:
                    w = warp_status() == "connected"
                    d = spoofdpi_running()
                    self.after(0, lambda wc=w, dr=d: self._update_live(wc, dr))
                except Exception:
                    pass
                time.sleep(4)
        threading.Thread(target=_run, daemon=True).start()

    def _update_live(self, warp_conn, dpi_run):
        self._cards["warp_conn"].set(warp_conn)
        self._cards["dpi_run"].set(dpi_run)
        self._cards["sudo"].set(self._sudo_pass is not None)

        if warp_conn and dpi_run:
            self._status_lbl.configure(text="⬤  Aktif", fg=C["green"])
            self._hdr_dot.set_state("ok")
        elif warp_conn or dpi_run:
            self._status_lbl.configure(text="⬤  Kısmi", fg=C["yellow"])
            self._hdr_dot.set_state("active")
        else:
            self._status_lbl.configure(text="⬤  Bekleniyor", fg=C["yellow"])
            self._hdr_dot.set_state("active")

    # ════════════════════════════════════════════════════════
    #  ADIM YÖNETİMİ
    # ════════════════════════════════════════════════════════
    def _set_step(self, key, state):
        if key in self._steps:
            self._steps[key].set_state(state)

    # ════════════════════════════════════════════════════════
    #  TÜM SİSTEMİ BAŞLAT
    # ════════════════════════════════════════════════════════
    def _launch_all(self):
        self._launch_btn.configure(state="disabled", text="⏳  Başlatılıyor...")
        self._log.log("━━━ Tam başlatma başlıyor ━━━", "HEAD")
        threading.Thread(target=self._run_launch, daemon=True).start()

    def _run_launch(self):
        # 1 — WARP
        self.after(0, lambda: self._set_step("warp", "running"))
        self.after(0, lambda: self._log.log("WARP bağlantısı kuruluyor...", "CMD"))
        ok1 = self._do_warp_connect()
        state1 = "ok" if ok1 else "error"
        self.after(0, lambda s=state1: self._set_step("warp", s))
        msg1 = "WARP bağlandı ✓" if ok1 else "WARP bağlantısı başarısız!"
        lvl1 = "OK" if ok1 else "ERR"
        self.after(0, lambda m=msg1, l=lvl1: self._log.log(m, l))
        time.sleep(1.5)

        # 2 — SpoofDPI
        self.after(0, lambda: self._set_step("spoof", "running"))
        self.after(0, lambda: self._log.log("SpoofDPI başlatılıyor...", "CMD"))
        ok2 = self._do_dpi_start()
        state2 = "ok" if ok2 else "error"
        self.after(0, lambda s=state2: self._set_step("spoof", s))
        msg2 = "SpoofDPI aktif ✓" if ok2 else "SpoofDPI başlatılamadı!"
        lvl2 = "OK" if ok2 else "ERR"
        self.after(0, lambda m=msg2, l=lvl2: self._log.log(m, l))
        time.sleep(2)

        # 3 — Discord
        self.after(0, lambda: self._set_step("discord", "running"))
        self.after(0, lambda: self._log.log("Discord açılıyor...", "CMD"))
        ok3 = self._do_discord()
        state3 = "ok" if ok3 else "error"
        self.after(0, lambda s=state3: self._set_step("discord", s))
        msg3 = "Discord açıldı ✓" if ok3 else "Discord açılamadı!"
        lvl3 = "OK" if ok3 else "ERR"
        self.after(0, lambda m=msg3, l=lvl3: self._log.log(m, l))

        if ok1 and ok2:
            self.after(0, self._start_uptime)
        self.after(0, lambda: self._launch_btn.configure(
            state="normal", text="🚀  Sistemi Başlat"))
        self.after(0, lambda: self._log.log("━━━ Başlatma tamamlandı ━━━", "HEAD"))

    # ════════════════════════════════════════════════════════
    #  WARP İŞLEMLERİ
    # ════════════════════════════════════════════════════════
    def _do_warp_connect(self):
        try:
            mode = self._warp_mode.get()
            run(["warp-cli", "mode", mode])
            if mode == "proxy":
                run(["warp-cli", "proxy", "port", "40000"])
            run(["warp-cli", "connect"])
            time.sleep(2)
            return warp_status() in ("connected", "connecting")
        except Exception as e:
            self.after(0, lambda: self._log.log(f"WARP hatası: {e}", "ERR"))
            return False

    def _do_warp_disconnect(self):
        run(["warp-cli", "disconnect"])

    def _act_warp_connect(self):
        threading.Thread(target=lambda: (
            self.after(0, lambda: self._log.log("WARP bağlanıyor...", "CMD")),
            self._do_warp_connect(),
            self.after(0, lambda: self._log.log("WARP ✓", "OK"))
        ), daemon=True).start()

    def _act_warp_disconnect(self):
        threading.Thread(target=lambda: (
            self.after(0, lambda: self._log.log("WARP kesiliyor...", "CMD")),
            self._do_warp_disconnect(),
            self.after(0, lambda: self._log.log("WARP bağlantısı kesildi", "WARN"))
        ), daemon=True).start()

    # ════════════════════════════════════════════════════════
    #  SPOOFDPI İŞLEMLERİ
    # ════════════════════════════════════════════════════════
    def _do_dpi_start(self):
        if spoofdpi_running():
            self.after(0, lambda: self._log.log("SpoofDPI zaten çalışıyor", "INFO"))
            return True
        try:
            # Terminal penceresinde sudo ile çalıştır
            # Şifre varsa echo trick kullan
            if self._sudo_pass:
                apple_script = (
                    'tell application "Terminal"\n'
                    '  activate\n'
                    f'  do script "echo {repr(self._sudo_pass)} | sudo -S '
                    '/opt/homebrew/opt/spoofdpi/bin/spoofdpi '
                    '--auto-configure-network --dns-mode doh --no-tui"\n'
                    'end tell'
                )
            else:
                script_path = SCRIPT_DIR / "Mac_GoodbyeDPI.command"
                apple_script = (
                    'tell application "Terminal"\n'
                    '  activate\n'
                    f'  do script "bash {script_path}"\n'
                    'end tell'
                )
            subprocess.Popen(["osascript", "-e", apple_script])
            time.sleep(3)
            return True
        except Exception as e:
            self.after(0, lambda: self._log.log(f"DPI hatası: {e}", "ERR"))
            return False

    def _do_dpi_stop(self):
        ok, _, _ = run(["sudo", "-S", "pkill", "-f", "spoofdpi"],
                       sudo_pass=self._sudo_pass)
        return ok

    def _act_dpi_start(self):
        threading.Thread(target=lambda: (
            self.after(0, lambda: self._log.log("DPI başlatılıyor...", "CMD")),
            self._do_dpi_start(),
            self.after(0, lambda: self._log.log("SpoofDPI aktif ✓", "OK"))
        ), daemon=True).start()

    def _act_dpi_stop(self):
        threading.Thread(target=lambda: (
            self.after(0, lambda: self._log.log("DPI durduruluyor...", "CMD")),
            self._do_dpi_stop(),
            self.after(0, lambda: self._log.log("SpoofDPI durduruldu", "WARN"))
        ), daemon=True).start()

    # ════════════════════════════════════════════════════════
    #  DISCORD
    # ════════════════════════════════════════════════════════
    def _do_discord(self):
        try:
            subprocess.Popen([
                "open", "-na", "Brave Browser",
                "--args", "--app=https://discord.com/channels/@me"
            ])
            return True
        except Exception:
            try:
                subprocess.Popen(["open", "-a", "Discord"])
                return True
            except Exception as e:
                self.after(0, lambda: self._log.log(f"Discord açılamadı: {e}", "ERR"))
                return False

    def _act_discord(self):
        threading.Thread(target=lambda: (
            self.after(0, lambda: self._log.log("Discord açılıyor...", "CMD")),
            self._do_discord()
        ), daemon=True).start()

    # ════════════════════════════════════════════════════════
    #  TÜMÜNÜ DURDUR
    # ════════════════════════════════════════════════════════
    def _stop_all(self):
        if not messagebox.askyesno("Onayla", "Tüm hizmetler durdurulacak.\nDevam?", icon="warning"):
            return
        threading.Thread(target=self._run_stop, daemon=True).start()

    def _run_stop(self):
        self.after(0, lambda: self._log.log("━━━ Durdurma başlıyor ━━━", "HEAD"))
        self._do_dpi_stop()
        time.sleep(0.5)
        self._do_warp_disconnect()
        time.sleep(0.5)
        for k in ("warp","spoof","discord"):
            self.after(0, lambda key=k: self._set_step(key, "idle"))
        self._stop_uptime()
        self.after(0, lambda: self._status_lbl.configure(text="⬤  Durduruldu", fg=C["red"]))
        self.after(0, lambda: self._hdr_dot.set_state("idle"))
        self.after(0, lambda: self._log.log("━━━ Tüm hizmetler durduruldu ━━━", "WARN"))

    # ════════════════════════════════════════════════════════
    #  UPTIME SAYACI
    # ════════════════════════════════════════════════════════
    def _start_uptime(self):
        self._uptime_s = 0
        self._uptime_run = True
        self._tick_uptime()

    def _stop_uptime(self):
        self._uptime_run = False
        self.after(0, lambda: self._uptime_lbl.configure(text=""))

    def _tick_uptime(self):
        if not self._uptime_run:
            return
        m, s = divmod(self._uptime_s, 60)
        h, m = divmod(m, 60)
        self._uptime_lbl.configure(
            text=f"⏱ {h:02d}:{m:02d}:{s:02d}"
        )
        self._uptime_s += 1
        self.after(1000, self._tick_uptime)


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
