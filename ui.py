import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime, timedelta, timezone
from tkinter import messagebox, ttk

JST = timezone(timedelta(hours=9))

from db import Database
from models import Status


DIALOG_TIMEOUT_MS = 60000

# ---- Linear-inspired design tokens (dark-mode-native) ----
# Background surfaces
BG = "#08090a"              # marketing black (page canvas)
PANEL_BG = "#0f1011"        # panel dark (sidebar / panel)
SURFACE = "#131416"         # approx. rgba(255,255,255,0.02) on BG
SURFACE_2 = "#18191a"       # approx. rgba(255,255,255,0.04) on BG
SURFACE_3 = "#1b1c1e"       # approx. rgba(255,255,255,0.05) on BG
SURFACE_HOVER = "#202124"   # approx. rgba(255,255,255,0.08) on BG

# Text
FG = "#f7f8f8"              # primary (near white, warm cast)
FG_BODY = "#d0d6e0"         # body / secondary
FG_MUTED = "#8a8f98"        # tertiary muted
FG_SUBTLE = "#62666d"       # quaternary subtle

# Borders (tkinter can't use alpha, so pre-blended solids)
BORDER = "#1f2123"          # standard (~rgba(255,255,255,0.08))
BORDER_SUBTLE = "#141516"   # subtle (~rgba(255,255,255,0.05))
BORDER_STRONG = "#23252a"   # prominent

# Brand / accent
ACCENT = "#5e6ad2"          # brand indigo — primary CTA
ACCENT_HOVER = "#7170ff"    # accent violet — interactive
ACCENT_ACTIVE = "#828fff"   # hover/active

# Legacy aliases still referenced in older code paths
MUTED_FG = FG_MUTED
HEADER_BG = PANEL_BG
HEADER_FG = FG
HEADER_SUB_FG = FG_MUTED

SECONDARY_BG = SURFACE_3
SECONDARY_HOVER = SURFACE_HOVER

HOVER_BG = SURFACE_HOVER

SELECT_BG = "#1c2040"       # indigo tinted selection

# ---- Font stack ----
# Inter Variable is Linear's typeface. Tkinter gracefully falls back if
# Inter is not installed on the host.
_FONT_FAMILY = "Inter"
_FONT_MONO = "Berkeley Mono"


def _pick_font(root: tk.Misc) -> tuple[str, str]:
    families = set(tkfont.families(root))
    for cand in ("Inter", "Inter Variable", "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", "Segoe UI", "Helvetica"):
        if cand in families:
            ui = cand
            break
    else:
        ui = "Helvetica"
    for cand in ("Berkeley Mono", "SF Mono", "Menlo", "Consolas", "Courier"):
        if cand in families:
            mono = cand
            break
    else:
        mono = "Courier"
    return ui, mono


# Populated after Tk root is constructed.
UI_FONT = "Helvetica"
MONO_FONT = "Courier"


def F(size: int, weight: str = "normal") -> tuple:
    return (UI_FONT, size, weight)


def _setup_style(root: tk.Misc) -> ttk.Style:
    global UI_FONT, MONO_FONT
    UI_FONT, MONO_FONT = _pick_font(root)

    style = ttk.Style(root)
    for theme in ("clam", "alt", "default"):
        if theme in style.theme_names():
            style.theme_use(theme)
            break

    # Frames
    style.configure("App.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL_BG)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Card.TFrame", background=SURFACE, relief="flat")
    style.configure("Header.TFrame", background=PANEL_BG)
    style.configure("Section.TFrame", background=BG)

    # Labels
    style.configure("App.TLabel", background=BG, foreground=FG_BODY, font=F(13))
    style.configure("Panel.TLabel", background=PANEL_BG, foreground=FG_BODY, font=F(13))
    style.configure("Surface.TLabel", background=SURFACE, foreground=FG_BODY, font=F(13))
    style.configure("Muted.TLabel", background=BG, foreground=FG_MUTED, font=F(12))
    style.configure("Subtle.TLabel", background=BG, foreground=FG_SUBTLE, font=F(11))
    style.configure("PanelMuted.TLabel", background=PANEL_BG, foreground=FG_MUTED, font=F(11))
    style.configure("SurfaceMuted.TLabel", background=SURFACE, foreground=FG_MUTED, font=F(11))

    # Headings — weight 510 isn't available in Tk; 'bold' is the closest emphasis.
    style.configure("SectionTitle.TLabel", background=BG, foreground=FG, font=F(14, "bold"))
    style.configure("PanelSectionTitle.TLabel", background=PANEL_BG, foreground=FG, font=F(13, "bold"))
    style.configure("CardName.TLabel", background=SURFACE, foreground=FG, font=F(17, "bold"))
    style.configure("CardSub.TLabel", background=SURFACE, foreground=FG_MUTED, font=F(11))

    # Dialog typography (display-like, but Tk limits our letter-spacing control).
    style.configure("Dialog.TLabel", background=BG, foreground=FG, font=F(14, "bold"))
    style.configure("DialogHeader.TLabel", background=BG, foreground=FG, font=F(22, "bold"))
    style.configure("DialogBody.TLabel", background=BG, foreground=FG_BODY, font=F(13))
    style.configure("DialogMuted.TLabel", background=BG, foreground=FG_MUTED, font=F(12))

    # Header bar
    style.configure("AppTitle.TLabel", background=PANEL_BG, foreground=FG, font=F(18, "bold"))
    style.configure("Clock.TLabel", background=PANEL_BG, foreground=FG_MUTED, font=F(12))
    style.configure("Brand.TLabel", background=PANEL_BG, foreground=ACCENT_HOVER, font=F(11, "bold"))

    # Entry
    style.configure(
        "TEntry",
        fieldbackground=SURFACE_2,
        background=SURFACE_2,
        foreground=FG,
        insertcolor=FG,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=8,
        relief="flat",
    )
    style.map(
        "TEntry",
        fieldbackground=[("focus", SURFACE_3)],
        bordercolor=[("focus", ACCENT)],
        lightcolor=[("focus", ACCENT)],
        darkcolor=[("focus", ACCENT)],
    )

    # Labelframes
    style.configure("Lab.TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("Lab.TLabelframe.Label", background=BG, foreground=FG, font=F(13, "bold"))

    # Status buttons — keep the semantic color but flatten the surface so it
    # reads as Linear-style rather than Material-style.
    for status in Status:
        name = f"Status{int(status)}.TButton"
        style.configure(
            name,
            background=status.color,
            foreground=FG,
            font=F(15, "bold"),
            padding=(20, 16),
            borderwidth=0,
            focusthickness=0,
            relief="flat",
        )
        style.map(
            name,
            background=[("active", status.color), ("pressed", status.color)],
            foreground=[("active", FG), ("pressed", FG)],
        )

    # Primary action — brand indigo
    style.configure(
        "Action.TButton",
        background=ACCENT,
        foreground=FG,
        font=F(13, "bold"),
        padding=(18, 10),
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )
    style.map(
        "Action.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_ACTIVE)],
        foreground=[("active", FG), ("pressed", FG)],
    )

    # Ghost/secondary — near-transparent surface with thin border.
    style.configure(
        "Secondary.TButton",
        background=SURFACE_2,
        foreground=FG_BODY,
        font=F(13),
        padding=(18, 10),
        borderwidth=1,
        focusthickness=0,
        relief="flat",
        bordercolor=BORDER,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", SURFACE_3), ("pressed", SURFACE_HOVER)],
        foreground=[("active", FG), ("pressed", FG)],
        bordercolor=[("active", BORDER_STRONG)],
    )

    # Subtle pill-ish demo button
    style.configure(
        "Demo.TButton",
        background=SURFACE_2,
        foreground=FG_BODY,
        font=F(12, "bold"),
        padding=(14, 8),
        borderwidth=1,
        focusthickness=0,
        relief="flat",
        bordercolor=BORDER,
    )
    style.map(
        "Demo.TButton",
        background=[("active", SURFACE_3), ("pressed", SURFACE_HOVER)],
        foreground=[("active", FG), ("pressed", FG)],
        bordercolor=[("active", BORDER_STRONG)],
    )

    # Treeview (log)
    style.configure(
        "Log.Treeview",
        background=PANEL_BG,
        fieldbackground=PANEL_BG,
        foreground=FG_BODY,
        rowheight=34,
        borderwidth=0,
        font=F(12),
    )
    style.configure(
        "Log.Treeview.Heading",
        background=BG,
        foreground=FG_MUTED,
        font=F(11, "bold"),
        padding=(10, 8),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Log.Treeview.Heading",
        background=[("active", BG)],
        foreground=[("active", FG_MUTED)],
    )
    style.map(
        "Log.Treeview",
        background=[("selected", SELECT_BG)],
        foreground=[("selected", FG)],
    )

    # Scrollbars — tone down for dark surface.
    style.configure(
        "Vertical.TScrollbar",
        background=PANEL_BG,
        troughcolor=BG,
        bordercolor=BG,
        arrowcolor=FG_MUTED,
        lightcolor=PANEL_BG,
        darkcolor=PANEL_BG,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", SURFACE_HOVER)],
        arrowcolor=[("active", FG)],
    )

    return style


def _format_timestamp(ts: str | None) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace(" ", "T"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(JST).strftime("%m/%d %H:%M")
    except ValueError:
        return ts.split(".")[0]


class Badge(tk.Label):
    def __init__(self, parent, text: str, color: str, **kw):
        super().__init__(
            parent,
            text=f"  {text}  ",
            bg=color,
            fg=FG,
            font=kw.pop("font", F(11, "bold")),
            padx=kw.pop("padx", 6),
            pady=kw.pop("pady", 3),
            bd=0,
            **kw,
        )


class StatusDot(tk.Canvas):
    """Small round indicator rendered on a dark surface."""

    def __init__(self, parent, color: str, size: int = 10, bg: str = SURFACE):
        super().__init__(parent, width=size, height=size, bg=bg, bd=0, highlightthickness=0)
        self.create_oval(1, 1, size - 1, size - 1, fill=color, outline=color)


class SoftKeyboard(ttk.Frame):
    LETTER_ROWS = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
    SYMBOL_ROWS = ["!@#$%^&*()", "-_=+[]{}", ";:'\",.<>", "/\\`~?|"]
    KATAKANA_ROWS = [
        "アイウエオカキクケコ",
        "サシスセソタチツテト",
        "ナニヌネノハヒフヘホ",
        "マミムメモヤユヨラリ",
        "ルレロワヲンーッ・",
    ]
    KATAKANA_SHIFT_ROWS = [
        "ァィゥェォャュョーヽ",
        "ガギグゲゴザジズゼゾ",
        "ダヂヅデドバビブベボ",
        "パピプペポヴ、。「」",
    ]

    def __init__(
        self,
        parent,
        key_width: int = 4,
        key_height: int = 2,
        key_font_size: int = 12,
        key_padx: int = 2,
        key_pady: int = 2,
        frame_style: str = "App.TFrame",
    ):
        super().__init__(parent, style=frame_style)
        self._target: tk.Entry | None = None
        self._shift = False
        self._mode = "letter"
        self._key_width = key_width
        self._key_height = key_height
        self._key_font_size = key_font_size
        self._key_padx = key_padx
        self._key_pady = key_pady
        self._frame_style = frame_style
        self._build()

    def set_target(self, entry: tk.Entry):
        self._target = entry

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        if self._mode == "symbol":
            rows = self.SYMBOL_ROWS
        elif self._mode == "katakana":
            rows = self.KATAKANA_SHIFT_ROWS if self._shift else self.KATAKANA_ROWS
        else:
            rows = self.LETTER_ROWS
        for row in rows:
            line = ttk.Frame(self, style=self._frame_style)
            line.pack(pady=self._key_pady)
            for ch in row:
                key = ch.upper() if (self._shift and self._mode == "letter" and ch.isalpha()) else ch
                self._key_button(line, key, lambda c=key: self._insert(c)).pack(
                    side="left", padx=self._key_padx
                )

        bottom = ttk.Frame(self, style=self._frame_style)
        bottom.pack(pady=self._key_pady * 2)
        w = self._key_width
        space_w = max(10, w * 3 + 2)
        self._key_button(bottom, "Shift", self._toggle_shift, width=w + 1, active=self._shift).pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "ABC", lambda: self._set_mode("letter"), width=w, active=self._mode == "letter").pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "カナ", lambda: self._set_mode("katakana"), width=w, active=self._mode == "katakana").pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "記号", lambda: self._set_mode("symbol"), width=w, active=self._mode == "symbol").pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "Space", lambda: self._insert(" "), width=space_w).pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "←", self._backspace, width=w).pack(side="left", padx=self._key_padx)
        self._key_button(bottom, "Clear", self._clear, width=w + 1).pack(side="left", padx=self._key_padx)

    def _key_button(self, parent, text, cmd, width=None, active=False):
        if width is None:
            width = self._key_width
        return tk.Button(
            parent,
            text=text,
            width=width,
            height=self._key_height,
            font=F(self._key_font_size),
            bg=ACCENT if active else SURFACE_2,
            fg=FG if active else FG_BODY,
            activebackground=ACCENT_HOVER if active else SURFACE_3,
            activeforeground=FG,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            command=cmd,
        )

    def _insert(self, ch: str):
        if self._target:
            self._target.focus_set()
            self._target.insert(tk.INSERT, ch)

    def _backspace(self):
        if self._target:
            pos = self._target.index(tk.INSERT)
            if pos > 0:
                self._target.delete(pos - 1, pos)

    def _clear(self):
        if self._target:
            self._target.delete(0, tk.END)

    def _toggle_shift(self):
        self._shift = not self._shift
        self._build()

    def _set_mode(self, mode: str):
        if self._mode == mode:
            return
        self._mode = mode
        self._shift = False
        self._build()


class App:
    def __init__(self, db: Database, demo_reader=None):
        self.db = db
        self.root = tk.Tk()
        self.root.title("研究室在室モニター")

        self._screen_w = self.root.winfo_screenwidth()
        self._screen_h = self.root.winfo_screenheight()
        # 画面が小さい場合は情報密度を下げてキーボードを収める
        self._compact = self._screen_w < 900 or self._screen_h < 720

        win_w = min(1280, self._screen_w)
        win_h = min(780, self._screen_h)
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.configure(bg=BG)
        _setup_style(self.root)

        self._active_dialog: tk.Toplevel | None = None
        self._dialog_timer: str | None = None

        self._main = tk.Frame(self.root, bg=BG)
        self._main.pack(fill="both", expand=True)

        self._build_header()
        self._build_body()
        if demo_reader is not None:
            self._build_demo_panel(demo_reader)
        self._tick_clock()
        self.refresh()

    def _build_header(self):
        header = tk.Frame(self._main, bg=PANEL_BG)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        inner = tk.Frame(header, bg=PANEL_BG)
        inner.pack(fill="x", padx=28, pady=18)

        left = tk.Frame(inner, bg=PANEL_BG)
        left.pack(side="left")

        # Brand mark — a small indigo square acts as the logomark.
        mark = tk.Canvas(left, width=14, height=14, bg=PANEL_BG, bd=0, highlightthickness=0)
        mark.create_rectangle(0, 0, 14, 14, fill=ACCENT, outline=ACCENT)
        mark.pack(side="left", padx=(0, 12), pady=4)

        tk.Label(left, text="研究室在室モニター",
                 bg=PANEL_BG, fg=FG, font=F(18, "bold")).pack(side="left")

        right = tk.Frame(inner, bg=PANEL_BG)
        right.pack(side="right")
        self.clock_label = tk.Label(right, text="",
                                    bg=PANEL_BG, fg=FG_MUTED, font=F(12))
        self.clock_label.pack(side="right", padx=(16, 0))

        ttk.Button(
            right, text="手動追加", style="Secondary.TButton",
            command=self._open_manual_dialog,
        ).pack(side="right")

        # Hairline divider placed on its own row so it never overlaps the header.
        divider = tk.Frame(self._main, bg=BORDER_SUBTLE, height=1)
        divider.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_body(self):
        self._main.columnconfigure(0, weight=1, uniform="col")
        self._main.columnconfigure(1, weight=1, uniform="col")
        self._main.rowconfigure(2, weight=1)

        # Left: status
        left_wrap = tk.Frame(self._main, bg=BG)
        left_wrap.grid(row=2, column=0, sticky="nsew", padx=(24, 12), pady=(24, 12))

        left_head = tk.Frame(left_wrap, bg=BG)
        left_head.pack(fill="x", pady=(0, 14))
        tk.Label(left_head, text="在室状況",
                 bg=BG, fg=FG, font=F(14, "bold")).pack(side="left")
        tk.Label(left_head, text="STATUS",
                 bg=BG, fg=FG_SUBTLE, font=(MONO_FONT, 10)).pack(side="right")

        self.status_canvas = tk.Canvas(left_wrap, bg=BG, bd=0, highlightthickness=0)
        self.status_canvas.pack(side="left", fill="both", expand=True)
        self.status_frame = tk.Frame(self.status_canvas, bg=BG)
        self._status_window = self.status_canvas.create_window((0, 0), window=self.status_frame, anchor="nw")

        def _on_config(e):
            self.status_canvas.itemconfigure(self._status_window, width=e.width)
        self.status_canvas.bind("<Configure>", _on_config)
        self.status_frame.bind(
            "<Configure>",
            lambda _e: self.status_canvas.configure(scrollregion=self.status_canvas.bbox("all")),
        )

        status_sb = ttk.Scrollbar(left_wrap, orient="vertical", command=self.status_canvas.yview)
        status_sb.pack(side="right", fill="y")
        self.status_canvas.configure(yscrollcommand=status_sb.set)

        # Right: log
        right_wrap = tk.Frame(self._main, bg=BG)
        right_wrap.grid(row=2, column=1, sticky="nsew", padx=(12, 24), pady=(24, 12))

        right_head = tk.Frame(right_wrap, bg=BG)
        right_head.pack(fill="x", pady=(0, 14))
        tk.Label(right_head, text="ログ",
                 bg=BG, fg=FG, font=F(14, "bold")).pack(side="left")
        tk.Label(right_head, text="ACTIVITY",
                 bg=BG, fg=FG_SUBTLE, font=(MONO_FONT, 10)).pack(side="right")

        # Card container mimicking `rgba(255,255,255,0.02)` + `rgba(255,255,255,0.08)` border.
        tree_wrap = tk.Frame(right_wrap, bg=SURFACE,
                             highlightthickness=1, highlightbackground=BORDER)
        tree_wrap.pack(fill="both", expand=True)
        self.log_tree = ttk.Treeview(
            tree_wrap,
            columns=("time", "name", "status"),
            show="headings",
            style="Log.Treeview",
        )
        self.log_tree.heading("time", text="時刻", anchor="w")
        self.log_tree.heading("name", text="名前", anchor="w")
        self.log_tree.heading("status", text="ステータス", anchor="w")
        self.log_tree.column("time", width=140, anchor="w", stretch=False)
        self.log_tree.column("name", width=160, anchor="w", stretch=True)
        self.log_tree.column("status", width=140, anchor="w", stretch=False)
        for status in Status:
            self.log_tree.tag_configure(f"status{int(status)}",
                                        foreground=status.color,
                                        font=F(12, "bold"))
        self.log_tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)

        log_sb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.log_tree.yview)
        log_sb.pack(side="right", fill="y")
        self.log_tree.configure(yscrollcommand=log_sb.set)

    def _build_demo_panel(self, reader):
        # Hairline top border to separate the demo strip.
        tk.Frame(self._main, bg=BORDER_SUBTLE, height=1).grid(
            row=3, column=0, columnspan=2, sticky="ew"
        )
        panel = tk.Frame(self._main, bg=PANEL_BG)
        panel.grid(row=4, column=0, columnspan=2, sticky="ew")

        inner = tk.Frame(panel, bg=PANEL_BG)
        inner.pack(fill="x", padx=24, pady=12)

        # DEMO pill badge
        pill = tk.Frame(inner, bg=PANEL_BG, highlightthickness=1,
                        highlightbackground=BORDER_STRONG)
        pill.pack(side="left", padx=(0, 14))
        tk.Label(pill, text="  DEMO  ", bg=PANEL_BG, fg=ACCENT_HOVER,
                 font=F(11, "bold")).pack(padx=2, pady=1)

        for name, idm in reader.PRESETS:
            ttk.Button(
                inner, text=name, style="Demo.TButton",
                command=lambda i=idm: reader.simulate_tap(i),
            ).pack(side="left", padx=4)

    def _tick_clock(self):
        self.clock_label.configure(text=datetime.now(JST).strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def refresh(self):
        for w in self.status_frame.winfo_children():
            w.destroy()
        rows = self.db.latest_statuses()
        if not rows:
            empty = tk.Frame(self.status_frame, bg=BG)
            empty.pack(pady=48, fill="x")
            tk.Label(
                empty,
                text="まだユーザーが登録されていません",
                bg=BG, fg=FG,
                font=F(14, "bold"),
            ).pack()
            tk.Label(
                empty,
                text="カードをタッチして登録してください",
                bg=BG, fg=FG_MUTED,
                font=F(12),
            ).pack(pady=(6, 0))
        for row in rows:
            self._render_status_card(row)

        self._enable_touch_scroll(self.status_canvas, self.status_frame)

        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        for log in self.db.recent_logs(100):
            status = Status(log["status"])
            self.log_tree.insert(
                "", tk.END,
                values=(_format_timestamp(log["timestamp"]), log["name"], status.label),
                tags=(f"status{int(status)}",),
            )

    def _render_status_card(self, row):
        status = Status(row["status"]) if row["status"] is not None else None
        accent_color = status.color if status else FG_SUBTLE

        # Card: translucent-feeling surface with hairline border.
        card = tk.Frame(self.status_frame, bg=SURFACE,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 10), padx=2)

        # Thin vertical accent bar (3px) replaces the bolder 6px Material rail.
        accent = tk.Frame(card, bg=accent_color, width=3)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=SURFACE)
        inner.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        top = tk.Frame(inner, bg=SURFACE)
        top.pack(fill="x")

        name_wrap = tk.Frame(top, bg=SURFACE)
        name_wrap.pack(side="left")
        StatusDot(name_wrap, accent_color, size=10, bg=SURFACE).pack(
            side="left", padx=(0, 10), pady=(6, 0)
        )
        tk.Label(
            name_wrap, text=row["name"],
            bg=SURFACE, fg=FG,
            font=F(17, "bold"),
            anchor="w",
        ).pack(side="left")

        Badge(top, status.label if status else "未記録", accent_color).pack(side="right")

        if row["timestamp"]:
            sub = tk.Frame(inner, bg=SURFACE)
            sub.pack(fill="x", pady=(6, 0))
            tk.Label(
                sub, text=f"更新 {_format_timestamp(row['timestamp'])}",
                bg=SURFACE, fg=FG_SUBTLE,
                font=F(11), anchor="e",
            ).pack(side="right")

    def on_card_tapped(self, idm: str):
        self.root.after(0, self._handle_card, idm)

    def _handle_card(self, idm: str):
        if self._active_dialog and self._active_dialog.winfo_exists():
            return
        user = self.db.find_user_by_card(idm)
        if user is None:
            self._open_register_dialog(idm)
        else:
            self._open_status_dialog(user)

    def _open_register_dialog(self, idm: str):
        dlg, body = self._make_dialog("ユーザー登録")
        dlg_w, dlg_h = self._fit_dialog(dlg, 820, 760)
        dlg.minsize(min(460, dlg_w), min(480, dlg_h))

        compact = self._compact or dlg_h < 720
        pad_x = 18 if compact else 28
        pad_top = 14 if compact else 24
        pad_gap = 4 if compact else 6

        btns = ttk.Frame(body, style="App.TFrame", padding=(pad_x, 8, pad_x, 16 if compact else 24))
        btns.pack(side="bottom", fill="x")

        keyboard_wrap = ttk.Frame(body, style="App.TFrame", padding=(pad_x, 8 if compact else 12))
        keyboard_wrap.pack(side="bottom", fill="x")

        scroll_inner, scroll_wrap, scroll_canvas = self._scrollable_area(body)
        scroll_wrap.pack(side="top", fill="both", expand=True)

        header = ttk.Frame(scroll_inner, style="App.TFrame", padding=(pad_x, pad_top, pad_x, pad_gap))
        header.pack(fill="x")
        ttk.Label(header, text="ユーザー登録", style="DialogHeader.TLabel").pack(anchor="w")
        tk.Label(header,
                 text=f"カードID  {idm}",
                 bg=BG, fg=FG_MUTED,
                 font=(MONO_FONT, 12)).pack(anchor="w", pady=(6, 0))

        content = ttk.Frame(scroll_inner, style="App.TFrame", padding=(pad_x, pad_gap, pad_x, pad_gap))
        content.pack(fill="x")

        existing_users = self.db.list_users()
        if existing_users:
            link = tk.Frame(content, bg=SURFACE,
                            highlightthickness=1, highlightbackground=BORDER)
            link.pack(fill="x", pady=(0, 8 if compact else 14))
            link_inner = tk.Frame(link, bg=SURFACE)
            link_inner.pack(fill="x", padx=12 if compact else 18, pady=10 if compact else 16)

            tk.Label(
                link_inner, text="既存ユーザーに紐付け",
                bg=SURFACE, fg=FG, font=F(14, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                link_inner, text="このカードを下のユーザーと紐付けます",
                bg=SURFACE, fg=FG_MUTED, font=F(11),
                anchor="w",
            ).pack(anchor="w", pady=(4, 12))

            list_row = tk.Frame(link_inner, bg=SURFACE)
            list_row.pack(fill="x")
            users_list = tk.Listbox(
                list_row,
                height=min(3 if compact else 5, len(existing_users)),
                font=F(12 if compact else 13),
                bg=SURFACE_2, fg=FG_BODY,
                selectbackground=SELECT_BG, selectforeground=FG,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT, bd=0,
                activestyle="none", exportselection=False,
                relief="flat",
            )
            users_list.pack(side="left", fill="x", expand=True)
            for u in existing_users:
                users_list.insert(tk.END, f"  {u['name']}   {u['student_id']}")
            sb = ttk.Scrollbar(list_row, orient="vertical", command=users_list.yview)
            sb.pack(side="left", fill="y")
            users_list.configure(yscrollcommand=sb.set)

            def link_selected():
                sel = users_list.curselection()
                if not sel:
                    messagebox.showerror("エラー", "ユーザーを選択してください", parent=dlg)
                    return
                user = existing_users[sel[0]]
                self.db.add_card(user["id"], idm)
                self._close_dialog()
                self._open_status_dialog(self.db.find_user_by_card(idm))

            ttk.Button(
                link_inner, text="このユーザーに紐付け",
                style="Action.TButton", command=link_selected,
            ).pack(anchor="e", pady=(14, 0))

        form = tk.Frame(content, bg=SURFACE,
                        highlightthickness=1, highlightbackground=BORDER)
        form.pack(fill="x")
        form_inner = tk.Frame(form, bg=SURFACE)
        form_inner.pack(fill="x", padx=12 if compact else 18, pady=10 if compact else 16)

        tk.Label(
            form_inner, text="新規登録",
            bg=SURFACE, fg=FG, font=F(14, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 8 if compact else 12))

        grid = tk.Frame(form_inner, bg=SURFACE)
        grid.pack(fill="x")
        row_pady = 3 if compact else 6
        tk.Label(grid, text="学籍番号", bg=SURFACE, fg=FG_MUTED,
                 font=F(12)).grid(row=0, column=0, sticky="w", padx=(0, 14), pady=row_pady)
        sid_entry = ttk.Entry(grid, font=F(14 if compact else 15), width=28)
        sid_entry.grid(row=0, column=1, sticky="ew", pady=row_pady)
        tk.Label(grid, text="名前", bg=SURFACE, fg=FG_MUTED,
                 font=F(12)).grid(row=1, column=0, sticky="w", padx=(0, 14), pady=row_pady)
        name_entry = ttk.Entry(grid, font=F(14 if compact else 15), width=28)
        name_entry.grid(row=1, column=1, sticky="ew", pady=row_pady)
        grid.columnconfigure(1, weight=1)

        if compact:
            kb_kwargs = dict(key_width=3, key_height=1, key_font_size=11, key_padx=1, key_pady=1)
        else:
            kb_kwargs = dict(key_width=4, key_height=2, key_font_size=12, key_padx=2, key_pady=2)
        keyboard = SoftKeyboard(keyboard_wrap, **kb_kwargs)
        keyboard.pack()
        keyboard.set_target(sid_entry)
        sid_entry.bind("<FocusIn>", lambda _e: keyboard.set_target(sid_entry))
        name_entry.bind("<FocusIn>", lambda _e: keyboard.set_target(name_entry))
        self._bind_autoscroll_on_focus(scroll_canvas, sid_entry)
        self._bind_autoscroll_on_focus(scroll_canvas, name_entry)
        sid_entry.focus_set()

        def submit():
            sid = sid_entry.get().strip()
            name = name_entry.get().strip()
            if not sid or not name:
                messagebox.showerror("エラー", "学籍番号と名前を入力してください", parent=dlg)
                return
            existing = self.db.find_user_by_student_id(sid)
            if existing:
                self.db.add_card(existing["id"], idm)
                user = existing
            else:
                user_id = self.db.register_user(sid, name)
                self.db.add_card(user_id, idm)
                user = self.db.find_user_by_card(idm)
            self._close_dialog()
            self._open_status_dialog(user)

        ttk.Button(btns, text="新規登録", style="Action.TButton", command=submit).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="キャンセル", style="Secondary.TButton", command=self._close_dialog).pack(side="right")

        self._enable_touch_scroll(scroll_canvas, scroll_inner)

    def _open_manual_dialog(self):
        if self._active_dialog and self._active_dialog.winfo_exists():
            return

        dlg, body = self._make_dialog("手動追加")
        dlg_w, dlg_h = self._fit_dialog(dlg, 1000, 640)
        dlg.minsize(min(780, dlg_w), min(440, dlg_h))

        compact = self._compact or dlg_h < 640 or dlg_w < 900
        pad_x = 16 if compact else 24
        pad_top = 12 if compact else 20

        bottom = ttk.Frame(body, style="App.TFrame",
                           padding=(pad_x, 6, pad_x, 12 if compact else 20))
        bottom.pack(side="bottom", fill="x")
        ttk.Button(bottom, text="キャンセル", style="Secondary.TButton",
                   command=self._close_dialog).pack(side="right")

        header = ttk.Frame(body, style="App.TFrame",
                           padding=(pad_x, pad_top, pad_x, 4))
        header.pack(side="top", fill="x")
        ttk.Label(header, text="手動追加", style="DialogHeader.TLabel").pack(anchor="w")
        tk.Label(header,
                 text="カードを持っていない人向けの登録・更新",
                 bg=BG, fg=FG_MUTED, font=F(12)).pack(anchor="w", pady=(4, 0))

        cols = ttk.Frame(body, style="App.TFrame",
                         padding=(pad_x, 4, pad_x, 4))
        cols.pack(side="top", fill="both", expand=True)
        cols.columnconfigure(0, weight=1, uniform="manualcol")
        cols.columnconfigure(1, weight=1, uniform="manualcol")
        cols.rowconfigure(0, weight=1)

        existing_users = self.db.list_users()

        # 左カラム: 既存ユーザー一覧
        left = tk.Frame(cols, bg=SURFACE,
                        highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_inner = tk.Frame(left, bg=SURFACE)
        left_inner.pack(fill="both", expand=True,
                        padx=10 if compact else 14, pady=10 if compact else 14)

        tk.Label(left_inner, text="既存ユーザー", bg=SURFACE, fg=FG,
                 font=F(14, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left_inner, text="選択してステータスを更新",
                 bg=SURFACE, fg=FG_MUTED, font=F(11),
                 anchor="w").pack(anchor="w", pady=(2, 8))

        if existing_users:
            list_row = tk.Frame(left_inner, bg=SURFACE)
            list_row.pack(fill="both", expand=True)
            users_list = tk.Listbox(
                list_row,
                font=F(12 if compact else 13),
                bg=SURFACE_2, fg=FG_BODY,
                selectbackground=SELECT_BG, selectforeground=FG,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT, bd=0,
                activestyle="none", exportselection=False,
                relief="flat",
            )
            users_list.pack(side="left", fill="both", expand=True)
            for u in existing_users:
                users_list.insert(tk.END, f"  {u['name']}   {u['student_id']}")
            sb = ttk.Scrollbar(list_row, orient="vertical", command=users_list.yview)
            sb.pack(side="left", fill="y")
            users_list.configure(yscrollcommand=sb.set)

            def pick_selected():
                sel = users_list.curselection()
                if not sel:
                    messagebox.showerror("エラー", "ユーザーを選択してください", parent=dlg)
                    return
                user = existing_users[sel[0]]
                self._close_dialog()
                self._open_status_dialog(user)

            ttk.Button(
                left_inner, text="このユーザーを更新",
                style="Action.TButton", command=pick_selected,
            ).pack(fill="x", pady=(10, 0))
        else:
            tk.Label(left_inner, text="登録済みユーザーはいません",
                     bg=SURFACE, fg=FG_MUTED, font=F(12)).pack(expand=True)

        # 右カラム: 新規登録
        right = tk.Frame(cols, bg=SURFACE,
                         highlightthickness=1, highlightbackground=BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_inner = tk.Frame(right, bg=SURFACE)
        right_inner.pack(fill="both", expand=True,
                         padx=10 if compact else 14, pady=10 if compact else 14)

        tk.Label(right_inner, text="新規登録（カードなし）",
                 bg=SURFACE, fg=FG, font=F(14, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(right_inner, text="学籍番号と名前を入力",
                 bg=SURFACE, fg=FG_MUTED, font=F(11),
                 anchor="w").pack(anchor="w", pady=(2, 8))

        grid = tk.Frame(right_inner, bg=SURFACE)
        grid.pack(fill="x")
        row_pady = 3 if compact else 5
        tk.Label(grid, text="学籍番号", bg=SURFACE, fg=FG_MUTED,
                 font=F(12)).grid(row=0, column=0, sticky="w",
                                  padx=(0, 10), pady=row_pady)
        sid_entry = ttk.Entry(grid, font=F(14 if compact else 15))
        sid_entry.grid(row=0, column=1, sticky="ew", pady=row_pady)
        tk.Label(grid, text="名前", bg=SURFACE, fg=FG_MUTED,
                 font=F(12)).grid(row=1, column=0, sticky="w",
                                  padx=(0, 10), pady=row_pady)
        name_entry = ttk.Entry(grid, font=F(14 if compact else 15))
        name_entry.grid(row=1, column=1, sticky="ew", pady=row_pady)
        grid.columnconfigure(1, weight=1)

        kb_holder = tk.Frame(right_inner, bg=SURFACE)
        kb_holder.pack(fill="x", pady=(8, 0))
        if compact:
            kb_kwargs = dict(key_width=3, key_height=1, key_font_size=11,
                             key_padx=1, key_pady=1)
        else:
            kb_kwargs = dict(key_width=4, key_height=2, key_font_size=12,
                             key_padx=2, key_pady=2)
        keyboard = SoftKeyboard(kb_holder, frame_style="Surface.TFrame", **kb_kwargs)
        keyboard.pack()
        keyboard.set_target(sid_entry)
        sid_entry.bind("<FocusIn>", lambda _e: keyboard.set_target(sid_entry))
        name_entry.bind("<FocusIn>", lambda _e: keyboard.set_target(name_entry))
        sid_entry.focus_set()

        def submit():
            sid = sid_entry.get().strip()
            name = name_entry.get().strip()
            if not sid or not name:
                messagebox.showerror("エラー", "学籍番号と名前を入力してください", parent=dlg)
                return
            existing = self.db.find_user_by_student_id(sid)
            if existing:
                user = existing
            else:
                self.db.register_user(sid, name)
                user = self.db.find_user_by_student_id(sid)
            self._close_dialog()
            self._open_status_dialog(user)

        ttk.Button(right_inner, text="新規登録",
                   style="Action.TButton",
                   command=submit).pack(fill="x", pady=(10, 0))

    def _open_status_dialog(self, user):
        dlg, body = self._make_dialog("ステータス選択")
        dlg_w, dlg_h = self._fit_dialog(dlg, 460, 600)
        dlg.minsize(min(360, dlg_w), min(420, dlg_h))

        compact = self._compact or dlg_h < 600
        pad_x = 20 if compact else 32
        pad_top = 16 if compact else 28

        foot = ttk.Frame(body, style="App.TFrame", padding=(pad_x, 8, pad_x, 14 if compact else 24))
        foot.pack(side="bottom", fill="x")

        scroll_inner, scroll_wrap, scroll_canvas = self._scrollable_area(body)
        scroll_wrap.pack(side="top", fill="both", expand=True)

        header = ttk.Frame(scroll_inner, style="App.TFrame", padding=(pad_x, pad_top, pad_x, 8))
        header.pack(fill="x")
        ttk.Label(header, text=user["name"], style="DialogHeader.TLabel").pack(anchor="w")
        tk.Label(header, text=f"学籍番号  {user['student_id']}",
                 bg=BG, fg=FG_MUTED, font=(MONO_FONT, 12)).pack(anchor="w", pady=(6, 0))
        tk.Label(header, text="ステータスを選んでください",
                 bg=BG, fg=FG_SUBTLE, font=F(12)).pack(anchor="w", pady=(8 if compact else 12, 0))

        def choose(status: Status):
            self.db.log_status(user["id"], status)
            self._close_dialog()
            self.refresh()

        btn_wrap = ttk.Frame(scroll_inner, style="App.TFrame", padding=(pad_x, 8, pad_x, 8))
        btn_wrap.pack(fill="both", expand=True)
        for status in Status:
            ttk.Button(
                btn_wrap,
                text=status.label,
                style=f"Status{int(status)}.TButton",
                command=lambda s=status: choose(s),
            ).pack(fill="x", pady=3 if compact else 5)
        ttk.Button(
            foot, text="キャンセル", style="Secondary.TButton",
            command=self._close_dialog,
        ).pack(fill="x")

        self._enable_touch_scroll(scroll_canvas, scroll_inner)

    def _make_dialog(self, title: str, geometry: str = "") -> tuple[tk.Toplevel, ttk.Frame]:
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=BG)
        if geometry:
            dlg.geometry(geometry)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", self._close_dialog)
        body = tk.Frame(dlg, bg=BG)
        body.pack(fill="both", expand=True)
        self._active_dialog = dlg
        self._dialog_timer = dlg.after(DIALOG_TIMEOUT_MS, self._close_dialog)
        return dlg, body

    def _scrollable_area(self, parent) -> tuple[tk.Frame, tk.Frame, tk.Canvas]:
        wrap = tk.Frame(parent, bg=BG)
        canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, bd=0)
        canvas.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        sb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=sb.set)
        inner = tk.Frame(canvas, bg=BG)
        inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(inner_id, width=e.width),
        )
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        canvas.bind("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda _e: canvas.yview_scroll(1, "units"))
        return inner, wrap, canvas

    def _enable_touch_scroll(self, canvas: tk.Canvas, root_widget: tk.Widget,
                              threshold: int = 8):
        """中身のどこをドラッグしてもスクロールできるようにする。
        ドラッグ距離が閾値を超えた時点でクリック動作をキャンセルしスクロールに切り替える。"""
        state = {"start_y": 0, "scrolling": False}

        def on_press(e):
            state["start_y"] = e.y_root
            state["scrolling"] = False
            canvas.scan_mark(e.x_root, e.y_root)

        def on_motion(e):
            if not state["scrolling"]:
                if abs(e.y_root - state["start_y"]) > threshold:
                    state["scrolling"] = True
            if state["scrolling"]:
                canvas.scan_dragto(e.x_root, e.y_root, gain=1)
                return "break"

        def on_release(_e):
            was_scrolling = state["scrolling"]
            state["scrolling"] = False
            if was_scrolling:
                return "break"

        def recurse(w):
            # スクロールバーや Listbox などそれ自身のドラッグ挙動を持つものはスキップ
            if isinstance(w, (ttk.Scrollbar, tk.Scrollbar, tk.Listbox)):
                return
            try:
                w.bind("<ButtonPress-1>", on_press, add="+")
                w.bind("<B1-Motion>", on_motion, add="+")
                w.bind("<ButtonRelease-1>", on_release, add="+")
            except tk.TclError:
                pass
            for c in w.winfo_children():
                recurse(c)

        recurse(root_widget)

    def _bind_autoscroll_on_focus(self, canvas: tk.Canvas, widget: tk.Widget):
        def _scroll_into_view(_e=None):
            canvas.update_idletasks()
            try:
                bbox = canvas.bbox("all")
                if not bbox:
                    return
                total_h = bbox[3] - bbox[1]
                if total_h <= 0:
                    return
                y = widget.winfo_rooty() - canvas.winfo_rooty() + canvas.canvasy(0)
                frac = max(0.0, min(1.0, y / total_h))
                canvas.yview_moveto(frac)
            except tk.TclError:
                pass
        widget.bind("<FocusIn>", _scroll_into_view, add="+")

    def _fit_dialog(self, dlg: tk.Toplevel, desired_w: int, desired_h: int) -> tuple[int, int]:
        """Size dlg to fit the screen (with margin) and center it."""
        h_margin = 24
        # タイトルバー・タスクバー等のウィンドウクローム分を多めに確保
        # (RPi の自動非表示タスクバーやウィンドウ装飾を考慮)
        v_margin = 160
        top_offset = 60
        bottom_reserve = 80
        w = min(desired_w, self._screen_w - h_margin)
        h = min(desired_h, self._screen_h - v_margin)
        x = max(0, (self._screen_w - w) // 2)
        y = max(top_offset, (self._screen_h - h) // 2)
        if y + h > self._screen_h - bottom_reserve:
            y = max(top_offset, self._screen_h - bottom_reserve - h)
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        return w, h

    def _close_dialog(self):
        if self._dialog_timer and self._active_dialog:
            try:
                self._active_dialog.after_cancel(self._dialog_timer)
            except Exception:
                pass
        self._dialog_timer = None
        if self._active_dialog and self._active_dialog.winfo_exists():
            self._active_dialog.destroy()
        self._active_dialog = None

    def run(self):
        self.root.mainloop()
