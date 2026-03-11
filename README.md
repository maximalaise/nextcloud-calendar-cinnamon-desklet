# Nextcloud Calendar Desklet for Cinnamon

A Cinnamon desklet for Linux Mint that displays your upcoming appointments from a Nextcloud calendar directly on your desktop.

🌍 **Language support:** The desklet automatically detects your system language and displays in English or German.

---

## Preview

The desklet shows all appointments for the current week with date and time. A click opens the GNOME Calendar app. Data is automatically refreshed every 15 minutes.

---

## Requirements

- Linux Mint with Cinnamon Desktop
- Nextcloud instance with calendar (CalDAV)
- A Nextcloud **app password** (not your main password!)
- Python 3

---

## Installation

### 1. Download the desklet

```bash
git clone https://github.com/YOUR-USERNAME/nextcloud-calendar-desklet.git \
  ~/.local/share/cinnamon/desklets/nextcloud-calendar@YOUR-USERNAME
```

### 2. Run setup

```bash
cd ~/.local/share/cinnamon/desklets/nextcloud-calendar@YOUR-USERNAME
chmod +x setup.sh
./setup.sh
```

The setup script:
- installs all dependencies (`python3-caldav`, `python3-keyring`)
- securely stores your credentials in the GNOME Keyring
- tests the connection to your Nextcloud
- sets up a systemd timer for automatic updates every 15 minutes

### 3. Add the desklet

Right-click on the desktop → **Desklets** → **Nextcloud Calendar** → Add to desktop

---

## Creating an app password

Never use your Nextcloud main password. Create an app password instead:

1. Open Nextcloud → click your profile picture (top right)
2. **Settings** → **Security**
3. Enter a name under "App passwords" (e.g. "Linux Desklet")
4. Click **Create**
5. Copy the displayed password – it is only shown once!

> **Tip:** Disable "Allow filesystem access" for the app password – the desklet only needs CalDAV access.

---

## Storing credentials manually

If you prefer not to use the setup script:

```bash
python3 -c "import keyring; keyring.set_password('nextcloud', 'url', 'https://YOUR-NEXTCLOUD/remote.php/dav/')"
python3 -c "import keyring; keyring.set_password('nextcloud', 'username', 'your@email.com')"
python3 -c "import keyring; keyring.set_password('nextcloud', 'your@email.com', 'YOUR-APP-PASSWORD')"
```

---

## Project structure

```
nextcloud-calendar@YOUR-USERNAME/
├── desklet.js              # Cinnamon desklet
├── stylesheet.css          # Styling
├── metadata.json           # Desklet metadata
├── nextcloudfetcher.py     # Fetches appointments from Nextcloud
├── setup.sh                # Setup script
├── .gitignore
├── LICENSE
└── README.md
```

---

## Dependencies

| Package | Install |
|---------|---------|
| python3-caldav | `sudo apt install python3-caldav` |
| python3-keyring | `sudo apt install python3-keyring` |

---

## License

This is free and unencumbered software released into the public domain – see [LICENSE](LICENSE).
