import os
import threading
import time
from abc import ABC, abstractmethod
from typing import Callable

DEBUG = os.environ.get("NFC_DEBUG") == "1"


def _log(msg: str):
    if DEBUG:
        print(f"[nfc] {msg}", flush=True)


TagHandler = Callable[[str], None]


class CardReader(ABC):
    """DIで差し替え可能なカードリーダーの抽象基底クラス。"""

    def __init__(self):
        self._handlers: list[TagHandler] = []

    def on_tag(self, handler: TagHandler) -> TagHandler:
        self._handlers.append(handler)
        return handler

    def _dispatch(self, idm: str):
        for h in self._handlers:
            try:
                h(idm)
            except Exception as e:
                print(f"タグハンドラエラー: {e}")

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...


SUICA_SENSF_REQ = bytearray.fromhex("0000030000")
READ_COOLDOWN = 1.5


class NFCReader(CardReader):
    """nfcpy 経由の実機リーダー。Express Card (Apple Pay Suica) 対応。"""

    def __init__(self, device: str = "usb"):
        super().__init__()
        self._device = device
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        import nfc
        import nfc.clf

        while not self._stop.is_set():
            try:
                clf = nfc.ContactlessFrontend(self._device)
                _log(f"clf opened: {clf}")
            except OSError as e:
                print(f"NFCリーダーに接続できません: {e}")
                self._stop.wait(2)
                continue
            try:
                self._poll_until_tap(clf, nfc)
            finally:
                try:
                    clf.close()
                    _log("clf closed")
                except Exception as e:
                    _log(f"clf close error: {e}")
            self._stop.wait(0.3)

    def _poll_until_tap(self, clf, nfc_mod):
        """1タップ検出したら return し、呼び出し側で clf を開き直させる。"""
        while not self._stop.is_set():
            target = nfc_mod.clf.RemoteTarget("212F")
            target.sensf_req = SUICA_SENSF_REQ
            try:
                res = clf.sense(target, iterations=3, interval=0.1)
            except nfc_mod.clf.CommunicationError as e:
                _log(f"CommunicationError: {e}")
                continue
            except Exception as e:
                print(f"sense エラー: {e}")
                return

            if res is None or res.sensf_res is None:
                continue

            idm = res.sensf_res[1:9].hex().upper()
            _log(f"tag detected: {idm}")
            self._dispatch(idm)
            return


class DemoReader(CardReader):
    """UIのデモボタンから simulate_tap(idm) で発火するダミーリーダー。"""

    PRESETS: list[tuple[str, str]] = [
        ("デモカード A", "0123456789ABCDEF"),
        ("デモカード B", "FEDCBA9876543210"),
        ("デモカード C", "1122334455667788"),
        ("未登録カード", "AABBCCDDEEFF0011"),
    ]

    def start(self):
        pass

    def stop(self):
        pass

    def simulate_tap(self, idm: str):
        self._dispatch(idm)
