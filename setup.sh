#!/bin/bash

echo "=== Nextcloud Calendar Desklet – Setup ==="
echo ""

# Abhängigkeiten prüfen und installieren
echo "📦 Prüfe Abhängigkeiten..."
if ! python3 -c "import caldav" 2>/dev/null; then
    echo "  → Installiere python3-caldav..."
    sudo apt install -y python3-caldav
else
    echo "  ✓ python3-caldav bereits installiert"
fi

if ! python3 -c "import keyring" 2>/dev/null; then
    echo "  → Installiere python3-keyring..."
    sudo apt install -y python3-keyring
else
    echo "  ✓ python3-keyring bereits installiert"
fi

echo ""
echo "🔐 Zugangsdaten eingeben (werden verschlüsselt im GNOME-Keyring gespeichert):"
echo ""

read -p "Nextcloud CalDAV URL (z.B. https://meine-nextcloud.de/remote.php/dav/): " url
read -p "Benutzername (E-Mail): " username
read -sp "App-Passwort (aus Nextcloud → Einstellungen → Sicherheit → App-Passwörter): " password
echo ""

# Im Keyring speichern
python3 -c "
import keyring
keyring.set_password('nextcloud', 'url', '$url')
keyring.set_password('nextcloud', 'username', '$username')
keyring.set_password('nextcloud', '$username', '$password')
print('✓ Zugangsdaten gespeichert')
"

echo ""
echo "📁 Setze Dateiberechtigungen..."
chmod 600 "$(dirname "$0")/nextcloudfetcher.py" 2>/dev/null && echo "  ✓ nextcloudfetcher.py gesichert" || echo "  ⚠ nextcloudfetcher.py nicht gefunden"

echo ""
echo "🧪 Teste Verbindung..."
python3 "$(dirname "$0")/nextcloudfetcher.py"

if [ -f "$(dirname "$0")/nextcloud_display.txt" ]; then
    echo ""
    echo "✓ Verbindung erfolgreich! Inhalt der Ausgabedatei:"
    echo "---"
    cat "$(dirname "$0")/nextcloud_display.txt"
    echo "---"
else
    echo "⚠ Ausgabedatei wurde nicht erstellt – bitte Zugangsdaten prüfen."
fi

echo ""
echo "⏱ Richte automatischen Timer ein (alle 15 Minuten)..."

mkdir -p ~/.config/systemd/user

SCRIPT_PATH="$(realpath "$(dirname "$0")/nextcloudfetcher.py")"

cat > ~/.config/systemd/user/nextcloud-calendar.service << EOF
[Unit]
Description=Nextcloud Calendar Fetcher

[Service]
ExecStart=python3 $SCRIPT_PATH
EOF

cat > ~/.config/systemd/user/nextcloud-calendar.timer << EOF
[Unit]
Description=Nextcloud Calendar Fetcher Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
EOF

systemctl --user enable nextcloud-calendar.timer
systemctl --user start nextcloud-calendar.timer

echo "  ✓ Timer aktiv – Script läuft ab jetzt alle 15 Minuten"
echo ""
echo "=== Setup abgeschlossen! ==="
echo "Starte Cinnamon neu oder füge das Desklet manuell hinzu:"
echo "  Rechtsklick auf Desktop → Desklets → Nextcloud Calendar"
