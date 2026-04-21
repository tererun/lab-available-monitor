#!/usr/bin/env bash
# Raspberry Pi (Raspberry Pi OS / Debian) で RC-S380 を使って動かすためのセットアップ。
# 使い方: bash setup.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "[warn] Linux 以外では udev ルールの設定をスキップします。" >&2
fi

echo "[1/6] apt パッケージを更新・インストールします"
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    python3-tk \
    libusb-1.0-0

echo "[2/6] Python venv を作成します (.venv)"
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ "$(uname -s)" == "Linux" ]]; then
    echo "[3/6] RC-S380 用 udev ルールを設置します"
    UDEV_RULE=/etc/udev/rules.d/99-rcs380.rules
    sudo tee "$UDEV_RULE" >/dev/null <<'EOF'
# Sony RC-S380 (PaSoRi)
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="06c1", GROUP="plugdev", MODE="0664"
SUBSYSTEM=="usb", ATTRS{idVendor}=="054c", ATTRS{idProduct}=="06c3", GROUP="plugdev", MODE="0664"
EOF

    echo "[4/6] 現在のユーザーを plugdev グループに追加します"
    sudo usermod -aG plugdev "$USER"

    echo "[5/6] udev ルールを再読込します"
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    echo "[6/6] 自動起動 (systemd --user + XDG autostart) を設定します"
    SERVICE_DIR="$HOME/.config/systemd/user"
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$SERVICE_DIR" "$AUTOSTART_DIR"

    cat > "$SERVICE_DIR/lab-monitor.service" <<EOF
[Unit]
Description=Lab Available Monitor
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/index.py
Restart=always
RestartSec=3
EOF

    # デスクトップセッションが起動した後、環境変数 (DISPLAY / WAYLAND_DISPLAY 等)
    # を user systemd に取り込んでからサービスを起動する。
    cat > "$AUTOSTART_DIR/lab-monitor.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Lab Available Monitor
Exec=/bin/sh -c "systemctl --user import-environment DISPLAY XAUTHORITY WAYLAND_DISPLAY XDG_SESSION_TYPE; systemctl --user restart lab-monitor.service"
X-GNOME-Autostart-enabled=true
EOF

    systemctl --user daemon-reload 2>/dev/null || true

    echo
    echo "完了しました。以下を行ってから再起動してください:"
    echo "  - RC-S380 を挿し直す"
    echo "  - sudo raspi-config で Desktop Autologin を有効化 (未設定なら)"
    echo
    echo "手動起動 / デバッグ:"
    echo "    source .venv/bin/activate && python index.py"
    echo
    echo "自動起動を一時停止したい場合:"
    echo "    systemctl --user stop lab-monitor.service       # 今すぐ停止"
    echo "    rm ~/.config/autostart/lab-monitor.desktop      # 次回ログインから無効化"
    echo
    echo "ログ確認:"
    echo "    journalctl --user -u lab-monitor.service -f"
else
    echo "[3-6/6] Linux ではないのでスキップしました"
    echo
    echo "デモモードで起動する場合:"
    echo "    source .venv/bin/activate"
    echo "    python index.py --demo"
fi
