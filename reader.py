import threading
import time
from abc import ABC, abstractmethod
from typing import Callable


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
        import nfc.tag

        while not self._stop.is_set():
            try:
                clf = nfc.ContactlessFrontend(self._device)
            except OSError as e:
                print(f"NFCリーダーに接続できません: {e}")
                self._stop.wait(2)
                continue
            try:
                self._poll(clf, nfc)
            finally:
                clf.close()

    def _poll(self, clf, nfc_mod):
        card_present = False
        last_dispatch = 0.0
        while not self._stop.is_set():
            target = nfc_mod.clf.RemoteTarget("212F")
            target.sensf_req = SUICA_SENSF_REQ
            try:
                res = clf.sense(target, iterations=3, interval=0.1)
            except nfc_mod.clf.CommunicationError:
                continue
            except Exception as e:
                print(f"sense エラー: {e}")
                self._stop.wait(0.5)
                continue

            if res is None or res.sensf_res is None:
                card_present = False
                continue

            if card_present:
                continue

            now = time.monotonic()
            if (now - last_dispatch) < READ_COOLDOWN:
                continue

            idm = res.sensf_res[1:9].hex().upper()
            card_present = True
            last_dispatch = now
            self._dispatch(idm)


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
