#!/usr/bin/env bash
# Raspberry Pi (Raspberry Pi OS / Debian) で RC-S380 を使って動かすためのセットアップ。
# 使い方: bash setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "[warn] Linux 以外では udev ルールの設定をスキップします。" >&2
fi

echo "[1/5] apt パッケージを更新・インストールします"
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-tk \
    libusb-1.0-0

echo "[2/5] Python venv を作成します (.venv)"
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ "$(uname -s)" == "Linux" ]]; then
    echo "[3/5] RC-S380 用 udev ルールを設置します"
    UDEV_RULE=/etc/udev/rules.d/99-rcs380.rules
    sudo tee "$UDEV_RULE" >/dev/null <<'EOF'
# Sony RC-S380 (PaSoRi)
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="06c1", GROUP="plugdev", MODE="0664"
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="06c3", GROUP="plugdev", MODE="0664"
EOF

    echo "[4/5] 現在のユーザーを plugdev グループに追加します"
    sudo usermod -aG plugdev "$USER"

    echo "[5/5] udev ルールを再読込します"
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    echo
    echo "完了しました。RC-S380 を挿し直し、ログインし直してから起動してください:"
    echo "    source .venv/bin/activate"
    echo "    python index.py"
else
    echo "[3-5/5] Linux ではないのでスキップしました"
    echo
    echo "デモモードで起動する場合:"
    echo "    source .venv/bin/activate"
    echo "    python index.py --demo"
fi
