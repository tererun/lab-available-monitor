import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from db import Database
from models import Status


DIALOG_TIMEOUT_MS = 60000

BG = "#f3f4f6"
PANEL_BG = "#ffffff"
BORDER = "#e5e7eb"
FG = "#111827"
MUTED_FG = "#6b7280"
HEADER_BG = "#1e293b"
HEADER_FG = "#f8fafc"
HEADER_SUB_FG = "#94a3b8"
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
SECONDARY = "#6b7280"
SECONDARY_HOVER = "#4b5563"
DEMO_BG = "#fef3c7"
DEMO_FG = "#92400e"
HOVER_BG = "#f9fafb"


def _setup_style(root: tk.Misc) -> ttk.Style:
    style = ttk.Style(root)
    for theme in ("clam", "alt", "default"):
        if theme in style.theme_names():
            style.theme_use(theme)
            break

    # Frames
    style.configure("App.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL_BG)
    style.configure("Card.TFrame", background=PANEL_BG, relief="flat")
    style.configure("Header.TFrame", background=HEADER_BG)
    style.configure("Demo.TFrame", background=DEMO_BG)
    style.configure("Section.TFrame", background=BG)

    # Labels
    style.configure("App.TLabel", background=BG, foreground=FG, font=("Helvetica", 12))
    style.configure("Panel.TLabel", background=PANEL_BG, foreground=FG, font=("Helvetica", 13))
    style.configure("Muted.TLabel", background=BG, foreground=MUTED_FG, font=("Helvetica", 12))
    style.configure("PanelMuted.TLabel", background=PANEL_BG, foreground=MUTED_FG, font=("Helvetica", 11))
    style.configure("SectionTitle.TLabel", background=BG, foreground=FG, font=("Helvetica", 14, "bold"))
    style.configure("PanelSectionTitle.TLabel", background=PANEL_BG, foreground=FG, font=("Helvetica", 13, "bold"))
    style.configure("CardName.TLabel", background=PANEL_BG, foreground=FG, font=("Helvetica", 16, "bold"))
    style.configure("CardSub.TLabel", background=PANEL_BG, foreground=MUTED_FG, font=("Helvetica", 11))
    style.configure("Dialog.TLabel", background=BG, foreground=FG, font=("Helvetica", 14, "bold"))
    style.configure("DialogHeader.TLabel", background=BG, foreground=FG, font=("Helvetica", 20, "bold"))
    style.configure("AppTitle.TLabel", background=HEADER_BG, foreground=HEADER_FG, font=("Helvetica", 18, "bold"))
    style.configure("Clock.TLabel", background=HEADER_BG, foreground=HEADER_SUB_FG, font=("Helvetica", 12))
    style.configure("Demo.TLabel", background=DEMO_BG, foreground=DEMO_FG, font=("Helvetica", 11, "bold"))

    # Entries
    style.configure(
        "TEntry",
        fieldbackground=PANEL_BG,
        foreground=FG,
        insertcolor=FG,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=6,
    )

    # LabelFrames
    style.configure("Lab.TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("Lab.TLabelframe.Label", background=BG, foreground=FG, font=("Helvetica", 13, "bold"))

    # Status buttons
    for status in Status:
        name = f"Status{int(status)}.TButton"
        style.configure(
            name,
            background=status.color,
            foreground="white",
            font=("Helvetica", 14, "bold"),
            padding=(20, 14),
            borderwidth=0,
            focusthickness=0,
        )
        style.map(
            name,
            background=[("active", status.color), ("pressed", status.color)],
            foreground=[("active", "white"), ("pressed", "white")],
        )

    # Action buttons
    style.configure(
        "Action.TButton",
        background=ACCENT,
        foreground="white",
        font=("Helvetica", 13, "bold"),
        padding=(18, 10),
        borderwidth=0,
    )
    style.map(
        "Action.TButton",
        background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )
    style.configure(
        "Secondary.TButton",
        background=SECONDARY,
        foreground="white",
        font=("Helvetica", 13),
        padding=(18, 10),
        borderwidth=0,
    )
    style.map(
        "Secondary.TButton",
        background=[("active", SECONDARY_HOVER), ("pressed", SECONDARY_HOVER)],
        foreground=[("active", "white"), ("pressed", "white")],
    )
    style.configure(
        "Demo.TButton",
        background=PANEL_BG,
        foreground=DEMO_FG,
        font=("Helvetica", 12, "bold"),
        padding=(12, 8),
        borderwidth=1,
        bordercolor=DEMO_FG,
    )
    style.map(
        "Demo.TButton",
        background=[("active", "#fde68a"), ("pressed", "#fde68a")],
    )

    # Treeview (log)
    style.configure(
        "Log.Treeview",
        background=PANEL_BG,
        fieldbackground=PANEL_BG,
        foreground=FG,
        rowheight=32,
        borderwidth=0,
        font=("Helvetica", 12),
    )
    style.configure(
        "Log.Treeview.Heading",
        background=BG,
        foreground=MUTED_FG,
        font=("Helvetica", 11, "bold"),
        padding=(8, 6),
        relief="flat",
        borderwidth=0,
    )
    style.map(
        "Log.Treeview",
        background=[("selected", "#e0f2fe")],
        foreground=[("selected", FG)],
    )

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=BG, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED_FG)

    return style


def _format_timestamp(ts: str | None) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace(" ", "T"))
        return dt.strftime("%m/%d %H:%M")
    except ValueError:
        return ts.split(".")[0]


class Badge(tk.Label):
    def __init__(self, parent, text: str, color: str, **kw):
        super().__init__(
            parent,
            text=f" {text} ",
            bg=color,
            fg="white",
            font=kw.pop("font", ("Helvetica", 11, "bold")),
            padx=kw.pop("padx", 8),
            pady=kw.pop("pady", 3),
            bd=0,
            **kw,
        )


class SoftKeyboard(ttk.Frame):
    LETTER_ROWS = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
    SYMBOL_ROWS = ["!@#$%^&*()", "-_=+[]{}", ";:'\",.<>", "/\\`~?|"]

    def __init__(self, parent):
        super().__init__(parent, style="App.TFrame")
        self._target: tk.Entry | None = None
        self._shift = False
        self._symbol = False
        self._build()

    def set_target(self, entry: tk.Entry):
        self._target = entry

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        rows = self.SYMBOL_ROWS if self._symbol else self.LETTER_ROWS
        for row in rows:
            line = ttk.Frame(self, style="App.TFrame")
            line.pack(pady=2)
            for ch in row:
                key = ch.upper() if (self._shift and ch.isalpha()) else ch
                self._key_button(line, key, lambda c=key: self._insert(c)).pack(
                    side="left", padx=2
                )

        bottom = ttk.Frame(self, style="App.TFrame")
        bottom.pack(pady=4)
        self._key_button(bottom, "Shift", self._toggle_shift, width=6, active=self._shift).pack(side="left", padx=2)
        self._key_button(bottom, "ABC" if self._symbol else "記号", self._toggle_symbol, width=6).pack(side="left", padx=2)
        self._key_button(bottom, "Space", lambda: self._insert(" "), width=20).pack(side="left", padx=2)
        self._key_button(bottom, "←", self._backspace, width=6).pack(side="left", padx=2)
        self._key_button(bottom, "Clear", self._clear, width=6).pack(side="left", padx=2)

    def _key_button(self, parent, text, cmd, width=4, active=False):
        return tk.Button(
            parent,
            text=text,
            width=width,
            height=2,
            font=("Helvetica", 12),
            bg="#fde68a" if active else PANEL_BG,
            fg=FG,
            activebackground="#fef3c7",
            activeforeground=FG,
            relief="flat",
            bd=1,
            highlightthickness=0,
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

    def _toggle_symbol(self):
        self._symbol = not self._symbol
        self._build()


class App:
    def __init__(self, db: Database, demo_reader=None):
        self.db = db
        self.root = tk.Tk()
        self.root.title("研究室在室モニター")
        self.root.geometry("1280x780")
        self.root.configure(bg=BG)
        _setup_style(self.root)

        self._active_dialog: tk.Toplevel | None = None
        self._dialog_timer: str | None = None

        self._main = ttk.Frame(self.root, style="App.TFrame")
        self._main.pack(fill="both", expand=True)

        self._build_header()
        self._build_body()
        if demo_reader is not None:
            self._build_demo_panel(demo_reader)
        self._tick_clock()
        self.refresh()

    def _build_header(self):
        header = ttk.Frame(self._main, style="Header.TFrame", padding=(24, 16))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(header, text="研究室在室モニター", style="AppTitle.TLabel").pack(side="left")
        self.clock_label = ttk.Label(header, text="", style="Clock.TLabel")
        self.clock_label.pack(side="right")

    def _build_body(self):
        self._main.columnconfigure(0, weight=1, uniform="col")
        self._main.columnconfigure(1, weight=1, uniform="col")
        self._main.rowconfigure(1, weight=1)

        # Left: status
        left_wrap = ttk.Frame(self._main, style="App.TFrame", padding=(16, 16, 8, 8))
        left_wrap.grid(row=1, column=0, sticky="nsew")
        ttk.Label(left_wrap, text="在室状況", style="SectionTitle.TLabel").pack(anchor="w", pady=(0, 10))

        self.status_canvas = tk.Canvas(left_wrap, bg=BG, bd=0, highlightthickness=0)
        self.status_canvas.pack(side="left", fill="both", expand=True)
        self.status_frame = ttk.Frame(self.status_canvas, style="App.TFrame")
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
        right_wrap = ttk.Frame(self._main, style="App.TFrame", padding=(8, 16, 16, 8))
        right_wrap.grid(row=1, column=1, sticky="nsew")
        ttk.Label(right_wrap, text="ログ", style="SectionTitle.TLabel").pack(anchor="w", pady=(0, 10))

        tree_wrap = ttk.Frame(right_wrap, style="Panel.TFrame")
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
        self.log_tree.column("status", width=120, anchor="w", stretch=False)
        for status in Status:
            self.log_tree.tag_configure(f"status{int(status)}", foreground=status.color, font=("Helvetica", 12, "bold"))
        self.log_tree.pack(side="left", fill="both", expand=True)

        log_sb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.log_tree.yview)
        log_sb.pack(side="right", fill="y")
        self.log_tree.configure(yscrollcommand=log_sb.set)

    def _build_demo_panel(self, reader):
        panel = ttk.Frame(self._main, style="Demo.TFrame", padding=(20, 10))
        panel.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(panel, text="DEMO", style="Demo.TLabel").pack(side="left", padx=(0, 16))
        for name, idm in reader.PRESETS:
            ttk.Button(
                panel, text=name, style="Demo.TButton",
                command=lambda i=idm: reader.simulate_tap(i),
            ).pack(side="left", padx=4)

    def _tick_clock(self):
        self.clock_label.configure(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    def refresh(self):
        for w in self.status_frame.winfo_children():
            w.destroy()
        rows = self.db.latest_statuses()
        if not rows:
            ttk.Label(
                self.status_frame,
                text="まだユーザーが登録されていません。\nカードをタッチして登録してください。",
                style="Muted.TLabel", justify="center",
            ).pack(pady=40)
        for row in rows:
            self._render_status_card(row)

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

        card = tk.Frame(self.status_frame, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 10), padx=2)

        accent_color = status.color if status else "#d1d5db"
        accent = tk.Frame(card, bg=accent_color, width=6)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(card, bg=PANEL_BG)
        inner.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        top = tk.Frame(inner, bg=PANEL_BG)
        top.pack(fill="x")
        tk.Label(
            top, text=row["name"],
            bg=PANEL_BG, fg=FG,
            font=("Helvetica", 16, "bold"),
            anchor="w",
        ).pack(side="left")
        Badge(top, status.label if status else "未記録", accent_color).pack(side="right")

        sub = tk.Frame(inner, bg=PANEL_BG)
        sub.pack(fill="x", pady=(6, 0))
        tk.Label(
            sub, text=f"学籍番号: {row['student_id']}",
            bg=PANEL_BG, fg=MUTED_FG,
            font=("Helvetica", 11), anchor="w",
        ).pack(side="left")
        if row["timestamp"]:
            tk.Label(
                sub, text=f"更新: {_format_timestamp(row['timestamp'])}",
                bg=PANEL_BG, fg=MUTED_FG,
                font=("Helvetica", 11), anchor="e",
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
        dlg.minsize(820, 760)

        header = ttk.Frame(body, style="App.TFrame", padding=(24, 20, 24, 6))
        header.pack(fill="x")
        ttk.Label(header, text="ユーザー登録", style="DialogHeader.TLabel").pack(anchor="w")
        ttk.Label(header, text=f"カードID: {idm}", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        content = ttk.Frame(body, style="App.TFrame", padding=(24, 6, 24, 6))
        content.pack(fill="x")

        existing_users = self.db.list_users()
        if existing_users:
            link = tk.Frame(content, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
            link.pack(fill="x", pady=(0, 12))
            link_inner = tk.Frame(link, bg=PANEL_BG)
            link_inner.pack(fill="x", padx=16, pady=14)

            tk.Label(
                link_inner, text="既存ユーザーに紐付け",
                bg=PANEL_BG, fg=FG, font=("Helvetica", 13, "bold"),
                anchor="w",
            ).pack(anchor="w")
            tk.Label(
                link_inner, text="このカードを下のユーザーと紐付けます",
                bg=PANEL_BG, fg=MUTED_FG, font=("Helvetica", 11),
                anchor="w",
            ).pack(anchor="w", pady=(2, 10))

            list_row = tk.Frame(link_inner, bg=PANEL_BG)
            list_row.pack(fill="x")
            users_list = tk.Listbox(
                list_row,
                height=min(5, len(existing_users)),
                font=("Helvetica", 13),
                bg=PANEL_BG, fg=FG,
                selectbackground="#dbeafe", selectforeground=FG,
                highlightthickness=1, highlightbackground=BORDER, bd=0,
                activestyle="none", exportselection=False,
            )
            users_list.pack(side="left", fill="x", expand=True)
            for u in existing_users:
                users_list.insert(tk.END, f"  {u['name']}  —  {u['student_id']}")
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
            ).pack(anchor="e", pady=(12, 0))

        form = tk.Frame(content, bg=PANEL_BG, highlightthickness=1, highlightbackground=BORDER)
        form.pack(fill="x")
        form_inner = tk.Frame(form, bg=PANEL_BG)
        form_inner.pack(fill="x", padx=16, pady=14)

        tk.Label(
            form_inner, text="新規登録",
            bg=PANEL_BG, fg=FG, font=("Helvetica", 13, "bold"),
            anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        grid = tk.Frame(form_inner, bg=PANEL_BG)
        grid.pack(fill="x")
        tk.Label(grid, text="学籍番号", bg=PANEL_BG, fg=FG, font=("Helvetica", 12)).grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=6
        )
        sid_entry = ttk.Entry(grid, font=("Helvetica", 15), width=28)
        sid_entry.grid(row=0, column=1, sticky="ew", pady=6)
        tk.Label(grid, text="名前", bg=PANEL_BG, fg=FG, font=("Helvetica", 12)).grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=6
        )
        name_entry = ttk.Entry(grid, font=("Helvetica", 15), width=28)
        name_entry.grid(row=1, column=1, sticky="ew", pady=6)
        grid.columnconfigure(1, weight=1)

        keyboard_wrap = ttk.Frame(body, style="App.TFrame", padding=(24, 10))
        keyboard_wrap.pack(fill="x")
        keyboard = SoftKeyboard(keyboard_wrap)
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
                self.db.add_card(existing["id"], idm)
                user = existing
            else:
                user_id = self.db.register_user(sid, name)
                self.db.add_card(user_id, idm)
                user = self.db.find_user_by_card(idm)
            self._close_dialog()
            self._open_status_dialog(user)

        btns = ttk.Frame(body, style="App.TFrame", padding=(24, 8, 24, 20))
        btns.pack(fill="x")
        ttk.Button(btns, text="新規登録", style="Action.TButton", command=submit).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="キャンセル", style="Secondary.TButton", command=self._close_dialog).pack(side="right")

    def _open_status_dialog(self, user):
        dlg, body = self._make_dialog("ステータス選択")
        dlg.minsize(440, 580)

        header = ttk.Frame(body, style="App.TFrame", padding=(28, 24, 28, 8))
        header.pack(fill="x")
        ttk.Label(header, text=user["name"], style="DialogHeader.TLabel").pack(anchor="w")
        ttk.Label(header, text=f"学籍番号: {user['student_id']}", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(header, text="ステータスを選んでください", style="Muted.TLabel").pack(anchor="w", pady=(10, 0))

        def choose(status: Status):
            self.db.log_status(user["id"], status)
            self._close_dialog()
            self.refresh()

        btn_wrap = ttk.Frame(body, style="App.TFrame", padding=(28, 8, 28, 8))
        btn_wrap.pack(fill="both", expand=True)
        for status in Status:
            ttk.Button(
                btn_wrap,
                text=status.label,
                style=f"Status{int(status)}.TButton",
                command=lambda s=status: choose(s),
            ).pack(fill="x", pady=5)

        foot = ttk.Frame(body, style="App.TFrame", padding=(28, 8, 28, 20))
        foot.pack(fill="x")
        ttk.Button(
            foot, text="キャンセル", style="Secondary.TButton",
            command=self._close_dialog,
        ).pack(fill="x")

    def _make_dialog(self, title: str, geometry: str = "") -> tuple[tk.Toplevel, ttk.Frame]:
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=BG)
        if geometry:
            dlg.geometry(geometry)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.protocol("WM_DELETE_WINDOW", self._close_dialog)
        body = ttk.Frame(dlg, style="App.TFrame")
        body.pack(fill="both", expand=True)
        self._active_dialog = dlg
        self._dialog_timer = dlg.after(DIALOG_TIMEOUT_MS, self._close_dialog)
        return dlg, body

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
