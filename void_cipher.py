import os
import base64
import hashlib
import secrets
import tkinter as tk
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305, AESGCM

ZWS = '\u200B'
ZWNJ = '\u200C'
ZWJ = '\u200D'

AAD = b"voidwing_v2_core"
STATIC_SALT = b"voidwing_salt_v2_core"

BG = "#0A0A0A"
CARD = "#141414"
FIELD = "#0F0F0F"
FG = "#E0E0E0"
MUTED = "#666666"
ACCENT = "#00FF66"
ACCENT_DIM = "#00B347"
NEON = "#00E5FF"
ERROR = "#FF3333"
BTN_BG = "#1A1A1A"
FONT = ("Consolas", 11)
FONT_BOLD = ("Consolas", 11, "bold")
FONT_TITLE = ("Consolas", 13, "bold")
FONT_SMALL = ("Consolas", 9)

_WORD_POOL = (
    "system", "kernel", "module", "service", "process", "thread", "buffer",
    "stream", "packet", "frame", "layer", "protocol", "network", "channel",
    "signal", "node", "link", "route", "mesh", "grid", "core", "shell",
    "cache", "block", "chain", "hash", "cipher", "vector", "matrix", "token",
    "scope", "phase", "state", "runtime", "compiler", "debugger", "exploit",
    "payload", "sandbox", "override", "bypass", "gateway", "proxy", "cluster",
    "daemon", "uplink", "downlink", "latency", "firewall", "backdoor",
    "rootkit", "overflow", "injector", "fingerprint", "handshake", "tunnel",
    "encrypt", "decrypt", "archive", "snapshot", "telemetry", "beacon",
)


def _generate_cover_text():
    n = secrets.choice(range(6, 11))
    words = [secrets.choice(_WORD_POOL) for _ in range(n)]
    return ' '.join(words).capitalize() + '.'


def derive_key_from_password(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), STATIC_SALT, 100000, dklen=96)


def cascade_encrypt(plain_text, key_96bytes):
    if len(key_96bytes) != 96:
        raise ValueError("Key must be exactly 96 bytes")
    k1, k2, k3 = key_96bytes[:32], key_96bytes[32:64], key_96bytes[64:]
    data = plain_text.encode() if isinstance(plain_text, str) else plain_text

    n1 = os.urandom(12)
    ct1 = ChaCha20Poly1305(k1).encrypt(n1, data, AAD)
    layer1 = n1 + ct1

    n2 = os.urandom(12)
    ct2 = AESGCM(k2).encrypt(n2, layer1, AAD)
    layer2 = n2 + ct2

    n3 = os.urandom(12)
    ct3 = ChaCha20Poly1305(k3).encrypt(n3, layer2, AAD)
    layer3 = n3 + ct3

    return base64.b64encode(layer3).decode()


def cascade_decrypt(b64_text, key_96bytes):
    if len(key_96bytes) != 96:
        raise ValueError("Key must be exactly 96 bytes")
    k1, k2, k3 = key_96bytes[:32], key_96bytes[32:64], key_96bytes[64:]
    raw = base64.b64decode(b64_text)

    layer2 = ChaCha20Poly1305(k3).decrypt(raw[:12], raw[12:], AAD)
    layer1 = AESGCM(k2).decrypt(layer2[:12], layer2[12:], AAD)
    plaintext = ChaCha20Poly1305(k1).decrypt(layer1[:12], layer1[12:], AAD)

    return plaintext.decode()


def _extract_invisible(text):
    return ''.join(c for c in text if c in (ZWS, ZWNJ, ZWJ))


def _spread_invisible(invisible, cover_text):
    words = cover_text.split()
    n = len(words)
    if n == 0:
        return invisible
    chunk_size = len(invisible) // n
    chunks = []
    idx = 0
    for i in range(n):
        if i == n - 1:
            chunks.append(invisible[idx:])
        else:
            chunks.append(invisible[idx:idx + chunk_size])
            idx += chunk_size
    return ' '.join(w + c for w, c in zip(words, chunks))


def zero_width_encode(crypto_b64, cover_text=None):
    if cover_text is None:
        cover_text = _generate_cover_text()

    parts = []
    for ch in crypto_b64:
        bits = format(ord(ch), '08b')
        parts.append(''.join(ZWS if b == '0' else ZWNJ for b in bits))
    invisible = ZWJ.join(parts)

    return _spread_invisible(invisible, cover_text)


def zero_width_decode(stego_text):
    invisible = _extract_invisible(stego_text).strip(ZWJ)
    if not invisible:
        return ''
    groups = [g for g in invisible.split(ZWJ) if g]
    chars = []
    for group in groups:
        bits = ''.join('0' if c == ZWS else '1' for c in group)
        chars.append(chr(int(bits, 2)))
    return ''.join(chars)


def recover_stego(stego_text, new_cover):
    invisible = _extract_invisible(stego_text)
    return _spread_invisible(invisible, new_cover)


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=160, height=38,
                 bg=ACCENT, fg=BG, hover=ACCENT_DIM, radius=10, font=FONT_BOLD,
                 outline_color=None):
        super().__init__(parent, width=width, height=height, bg=parent['bg'],
                         highlightthickness=0, bd=0)
        self.command = command
        self.bg_color = bg
        self.fg_color = fg
        self.hover_color = hover
        self.radius = radius
        self.text_str = text
        self.font = font
        self.outline_color = outline_color
        self._draw(bg, False)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _draw(self, color, hover_state):
        self.delete('all')
        w = int(self['width'])
        h = int(self['height'])
        r = self.radius
        if hover_state and self.outline_color:
            self.create_round_rect(0, 0, w, h, r, fill='', outline=self.outline_color, width=2)
            self.create_round_rect(3, 3, w - 3, h - 3, r, fill=color, outline='')
        else:
            self.create_round_rect(2, 2, w - 2, h - 2, r, fill=color, outline='')
        self.create_text(w // 2, h // 2, text=self.text_str,
                         fill=self.fg_color, font=self.font)

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2,
            x1 + r, y2, x1, y2, x1, y2 - r,
            x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, _):
        self._draw(self.hover_color, True)

    def _on_leave(self, _):
        self._draw(self.bg_color, False)

    def _on_click(self, _):
        if self.command:
            self.command()


class VoidCipherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VOIDWING INFRASTRUCTURE // PURE RAM CASCADE ENFORCER v3.5")
        self.root.configure(bg=BG)
        self.root.minsize(960, 680)
        self.root.resizable(True, True)

        self._build_header()
        self._build_key_protocol()
        self._build_triple_vault()
        self._build_enforcer()
        self._build_status()

    def _card(self, parent, **pack_kwargs):
        card = tk.Frame(parent, bg=CARD, relief=tk.FLAT, bd=0)
        card.pack(**pack_kwargs)
        return card

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, padx=20, pady=(16, 4))
        tk.Label(header, text="◆ VOIDWING", bg=BG, fg=ACCENT,
                 font=("Consolas", 16, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="PURE RAM CASCADE ENFORCER v3.5", bg=BG, fg=MUTED,
                 font=FONT_SMALL).pack(side=tk.LEFT, padx=10, pady=(6, 0))

    def _build_key_protocol(self):
        card = self._card(self.root, fill=tk.X, padx=20, pady=(8, 8))
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(inner, text="KEY PROTOCOL", bg=CARD, fg=ACCENT,
                 font=FONT_TITLE).pack(anchor=tk.W)

        row = tk.Frame(inner, bg=CARD)
        row.pack(fill=tk.X, pady=(8, 0))

        tk.Label(row, text="MASTER PASSPHRASE", bg=CARD, fg=MUTED,
                 font=FONT).pack(side=tk.LEFT)
        self.pwd_entry = tk.Entry(row, show="●", bg=FIELD, fg=FG,
                                  insertbackground=FG, relief=tk.FLAT,
                                  font=FONT, bd=6)
        self.pwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

    def _build_text_field(self, parent, label_text, height=8, readonly=False):
        tk.Label(parent, text=label_text, bg=CARD, fg=ACCENT,
                 font=FONT_BOLD).pack(anchor=tk.W, pady=(4, 4))
        txt = tk.Text(parent, height=height, bg=FIELD, fg=FG,
                      insertbackground=FG, relief=tk.FLAT, font=FONT,
                      bd=6, wrap=tk.WORD, padx=15, pady=12)
        txt.pack(fill=tk.BOTH, expand=True)
        if readonly:
            txt.configure(state=tk.DISABLED)
        return txt

    def _build_triple_vault(self):
        card = self._card(self.root, fill=tk.BOTH, expand=True,
                          padx=20, pady=(4, 8))
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        tk.Label(inner, text="THE TRIPLE VAULT", bg=CARD, fg=ACCENT,
                 font=FONT_TITLE).pack(anchor=tk.W)

        vault = tk.Frame(inner, bg=CARD)
        vault.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        vault.grid_columnconfigure(0, weight=1, uniform='vault')
        vault.grid_columnconfigure(1, weight=1, uniform='vault')
        vault.grid_columnconfigure(2, weight=1, uniform='vault')
        vault.grid_rowconfigure(0, weight=1)

        f1 = tk.Frame(vault, bg=CARD)
        f1.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        f2 = tk.Frame(vault, bg=CARD)
        f2.grid(row=0, column=1, sticky='nsew', padx=6)
        f3 = tk.Frame(vault, bg=CARD)
        f3.grid(row=0, column=2, sticky='nsew', padx=(6, 0))

        self.field_a = self._build_text_field(f1, "[1] SOURCE INPUT\n(Payload / Ciphertext)", height=10)
        self.field_b = self._build_text_field(f2, "[2] COVER TEXT\n(Stego Package)", height=10)
        self.field_c = self._build_text_field(f3, "[3] FINAL OUTPUT\n(Decrypted Result)", height=10, readonly=True)

        clip_frame = tk.Frame(f2, bg=CARD)
        clip_frame.pack(fill=tk.X, pady=(6, 0))

        btn_copy = tk.Button(clip_frame, text="COPY PACKAGE", command=self.on_copy,
                             bg=BTN_BG, fg=FG, activebackground=ACCENT_DIM, activeforeground=BG,
                             relief=tk.FLAT, font=FONT_SMALL, bd=0, padx=8, pady=4)
        btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        btn_paste = tk.Button(clip_frame, text="PASTE FROM CLIPBOARD", command=self.on_paste,
                              bg=BTN_BG, fg=FG, activebackground=ACCENT_DIM, activeforeground=BG,
                              relief=tk.FLAT, font=FONT_SMALL, bd=0, padx=8, pady=4)
        btn_paste.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

    def _build_enforcer(self):
        card = self._card(self.root, fill=tk.X, padx=20, pady=(4, 8))
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill=tk.X, padx=16, pady=12)

        tk.Label(inner, text="THE ENFORCER CORE", bg=CARD, fg=ACCENT,
                 font=FONT_TITLE).pack(anchor=tk.W)

        row = tk.Frame(inner, bg=CARD)
        row.pack(fill=tk.X, pady=(8, 0))

        self.enc_btn = RoundedButton(row, "ENCODE DATA", self.on_encrypt,
                                     width=180, height=40, bg=ACCENT, fg=BG,
                                     hover=ACCENT_DIM, outline_color=NEON)
        self.enc_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.dec_btn = RoundedButton(row, "DECODE PACKAGE", self.on_decrypt,
                                     width=180, height=40, bg=ACCENT, fg=BG,
                                     hover=ACCENT_DIM, outline_color=NEON)
        self.dec_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        self.rec_btn = RoundedButton(row, "REWRAP COVER", self.on_recover,
                                     width=160, height=40, bg=ACCENT, fg=BG,
                                     hover=ACCENT_DIM, outline_color=NEON)
        self.rec_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        self.clr_btn = RoundedButton(row, "WIPE ALL FIELDS", self.on_clear,
                                     width=140, height=40, bg=CARD, fg=ERROR,
                                     hover="#2A1A1A", outline_color=ERROR)
        self.clr_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

    def _build_status(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill=tk.X, padx=20, pady=(0, 14))
        self.status = tk.Label(bar, text="[+] SECURE RUNTIME READY", bg=BG, fg=MUTED,
                               font=FONT_SMALL, anchor=tk.W)
        self.status.pack(fill=tk.X)

    def _set_status(self, msg, is_error=False):
        prefix = "[-]" if is_error else "[*]"
        self.status.configure(text=f"{prefix} {msg}", fg=ERROR if is_error else ACCENT)

    def _read_field(self, txt):
        return txt.get("1.0", tk.END).strip()

    def _write_field(self, txt, content, readonly=False):
        if readonly:
            txt.configure(state=tk.NORMAL)
        txt.delete("1.0", tk.END)
        txt.insert("1.0", content)
        if readonly:
            txt.configure(state=tk.DISABLED)

    def _get_key(self):
        pwd = self.pwd_entry.get().strip()
        if not pwd:
            self._set_status("ACCESS DENIED: PASSWORD BLANK", True)
            return None
        return derive_key_from_password(pwd)

    def on_copy(self):
        content = self._read_field(self.field_b)
        if not content:
            self._set_status("FIELD [2] EMPTY: NOTHING TO COPY", True)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        self._set_status("COMPLETED: PACKAGE COPIED TO CLIPBOARD")

    def on_paste(self):
        try:
            content = self.root.clipboard_get()
        except tk.TclError:
            self._set_status("CLIPBOARD EMPTY", True)
            return
        self._write_field(self.field_b, content)
        self._set_status("COMPLETED: PASTED FROM CLIPBOARD")

    def on_encrypt(self):
        payload = self._read_field(self.field_a)
        if not payload:
            self._set_status("FIELD [1] EMPTY: NOTHING TO ENCODE", True)
            return
        key = self._get_key()
        if key is None:
            return
        try:
            cover = self._read_field(self.field_b) or None
            encrypted = cascade_encrypt(payload, key)
            stego = zero_width_encode(encrypted, cover)
            self._write_field(self.field_b, stego)
            self._set_status(f"COMPLETED: ENCODED {len(stego)} CHARS | PAYLOAD: {len(encrypted)} B64")
        except Exception as e:
            self._set_status(f"ENCRYPTION ERROR: {e}", True)

    def on_decrypt(self):
        stego_input = self._read_field(self.field_b)
        if not stego_input:
            self._set_status("FIELD [2] EMPTY: NOTHING TO DECODE", True)
            return
        key = self._get_key()
        if key is None:
            return
        try:
            recovered_b64 = zero_width_decode(stego_input)
            if not recovered_b64:
                self._set_status("NO STEGO BITS DETECTED IN STREAM", True)
                return
            plaintext = cascade_decrypt(recovered_b64, key)
            self._write_field(self.field_c, plaintext, readonly=True)
            self._set_status("COMPLETED: DECODED SUCCESSFULLY")
        except Exception as e:
            self._set_status(f"DECRYPTION ERROR: {e}", True)

    def on_recover(self):
        old_stego = self._read_field(self.field_b)
        if not old_stego:
            self._set_status("FIELD [2] EMPTY: NO STEGO PACKAGE", True)
            return
        new_cover = self._read_field(self.field_a)
        if not new_cover:
            self._set_status("FIELD [1] EMPTY: ENTER NEW COVER TEXT", True)
            return
        try:
            recovered = recover_stego(old_stego, new_cover)
            self._write_field(self.field_b, recovered)
            self._set_status("COMPLETED: DATA REWRAPPED")
        except Exception as e:
            self._set_status(f"REWRAP ERROR: {e}", True)

    def on_clear(self):
        self._write_field(self.field_a, "")
        self._write_field(self.field_b, "")
        self._write_field(self.field_c, "", readonly=True)
        self._set_status("COMPLETED: ALL FIELDS WIPED")


if __name__ == '__main__':
    root = tk.Tk()
    app = VoidCipherGUI(root)
    root.mainloop()