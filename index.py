import argparse

from db import Database
from reader import CardReader, DemoReader, NFCReader
from ui import App


def main():
    parser = argparse.ArgumentParser(description="研究室在室モニター")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="デモモード (NFCリーダー不要・UIに疑似タップボタン表示)",
    )
    parser.add_argument("--device", default="usb", help="nfcpyのデバイス指定")
    parser.add_argument("--db", default="lab.db", help="SQLiteファイルパス")
    args = parser.parse_args()

    db = Database(args.db)
    db.connect()

    reader: CardReader
    if args.demo:
        reader = DemoReader()
    else:
        reader = NFCReader(device=args.device)

    app = App(db, demo_reader=reader if args.demo else None)

    @reader.on_tag
    def handle_tag(idm: str):
        app.on_card_tapped(idm)

    reader.start()

    try:
        app.run()
    finally:
        reader.stop()
        db.close()


if __name__ == "__main__":
    main()
