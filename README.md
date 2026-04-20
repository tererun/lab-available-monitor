# 研究室在室モニター

Raspberry Pi + RC-S380 (PaSoRi) + Suica / Apple Pay Suica で、研究室メンバーの在室状況を表示・記録する Tkinter アプリ。

## 必要なもの

- Raspberry Pi (Raspberry Pi OS / Debian 系)
- Sony RC-S380 (PaSoRi) USB NFC リーダー
- Suica, PASMO などの FeliCa カード、または Apple Pay Suica (Express Transit 設定済み)

## セットアップ (Raspberry Pi)

```bash
git clone <this-repo> lab-available-monitor
cd lab-available-monitor
bash setup.sh
```

`setup.sh` が行うこと:

- `python3-tk` `libusb-1.0-0` など apt パッケージのインストール
- `.venv/` に Python 仮想環境を作成し `nfcpy` をインストール
- RC-S380 を非 root で叩けるように `/etc/udev/rules.d/99-rcs380.rules` を設置
- 実行ユーザーを `plugdev` グループへ追加

実行後、**一度ログアウト→ログインし直す** (グループ反映のため) こと。RC-S380 も挿し直してください。

## 起動

```bash
source .venv/bin/activate
python index.py
```

### オプション

| フラグ | 説明 | 既定値 |
| --- | --- | --- |
| `--demo` | リーダー不要のデモモード。UI にダミーカードボタンが出る | off |
| `--device` | nfcpy のデバイス指定 | `usb` |
| `--db` | SQLite ファイルパス | `lab.db` |

デバッグログ (NFC 検出状況) を出したい場合は `NFC_DEBUG=1` を付けて起動:

```bash
NFC_DEBUG=1 python index.py
```

## 使い方

1. カードをリーダーにかざす
2. 未登録カードなら登録ダイアログ (既存ユーザーへの紐付け / 新規登録)
3. 登録済みならステータス選択ダイアログ (在室 / 帰宅 / 講義 / 学内(M棟) / 学内(その他))
4. 左側の在室一覧と右側のログに即時反映

1 ユーザーに複数カードを紐付け可能。

## 開発 (macOS 等でのデモ)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python index.py --demo
```

> macOS の場合、システム標準 Tk 8.5 はダークモードで UI が壊れるため、
> Homebrew の `python-tk@3.13` (Tk 9.x) を入れた Python で起動してください。
> 例: `/opt/homebrew/bin/python3.13 index.py --demo`

## 構成

- `index.py` — エントリポイント (CLI 引数、DI)
- `ui.py` — Tkinter UI
- `reader.py` — `CardReader` 抽象 + `NFCReader` (nfcpy) + `DemoReader`
- `db.py` — SQLite ラッパ
- `models.py` — `Status` 列挙型
- `setup.sh` — Raspberry Pi セットアップスクリプト
