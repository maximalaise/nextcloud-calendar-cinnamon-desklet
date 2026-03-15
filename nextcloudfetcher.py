import caldav
import os
import keyring
import locale
import urllib.request
import json
from datetime import datetime, timedelta

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def get_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            if config.get("view") not in ["week", "day"]:
                config["view"] = "week"
            return config
    except:
        return {"view": "week"}

def get_language():
    lang = locale.getdefaultlocale()[0]
    return "de" if lang and lang.startswith("de") else "en"

LANG = get_language()

TEXTS = {
    "de": {
        "no_events": "Du hast diese Woche keine Termine.",
        "one_event": "Du hast diese Woche einen Termin:",
        "many_events": "Du hast diese Woche {} Termine:",
        "no_events_day": "Du hast heute keine Termine.",
        "one_event_day": "Du hast heute einen Termin:",
        "many_events_day": "Du hast heute {} Termine:",
        "no_events_tomorrow": "Du hast morgen keine Termine.",
        "one_event_tomorrow": "Du hast morgen einen Termin:",
        "many_events_tomorrow": "Du hast morgen {} Termine:",
        "no_events_next_week": "Du hast nächste Woche keine Termine.",
        "one_event_next_week": "Du hast nächste Woche einen Termin:",
        "many_events_next_week": "Du hast nächste Woche {} Termine:",
        "error_password": "Fehler: Kein Passwort im Keyring gefunden.\nBitte einmalig speichern mit:\npython3 -c \"import keyring; keyring.set_password('nextcloud', 'EMAIL', 'PASSWORT')\"",
        "error": "Fehler: {}",
        "no_calendars": "Keine Kalender gefunden!",
    },
    "en": {
        "no_events": "You have no appointments this week.",
        "one_event": "You have one appointment this week:",
        "many_events": "You have {} appointments this week:",
        "no_events_day": "You have no appointments today.",
        "one_event_day": "You have one appointment today:",
        "many_events_day": "You have {} appointments today:",
        "no_events_tomorrow": "You have no appointments tomorrow.",
        "one_event_tomorrow": "You have one appointment tomorrow:",
        "many_events_tomorrow": "You have {} appointments tomorrow:",
        "no_events_next_week": "You have no appointments next week.",
        "one_event_next_week": "You have one appointment next week:",
        "many_events_next_week": "You have {} appointments next week:",
        "error_password": "Error: No password found in keyring.\nPlease store it once with:\npython3 -c \"import keyring; keyring.set_password('nextcloud', 'EMAIL', 'PASSWORD')\"",
        "error": "Error: {}",
        "no_calendars": "No calendars found!",
    }
}

T = TEXTS[LANG]

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextcloud_display.txt")
SWITCH_HOUR = 20

def is_connected():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
        return True
    except:
        return False

def check_calendar():
    if not is_connected():
        return

    URL = keyring.get_password("nextcloud", "url")
    USERNAME = keyring.get_password("nextcloud", "username")
    PASSWORD = keyring.get_password("nextcloud", USERNAME)

    if not URL or not USERNAME or not PASSWORD:
        with open(OUTPUT_FILE, "w") as f:
            f.write(T["error_password"])
        return

    try:
        client = caldav.DAVClient(url=URL, username=USERNAME, password=PASSWORD, ssl_verify_cert=True)
        principal = client.principal()
        calendars = principal.calendars()

        if not calendars:
            with open(OUTPUT_FILE, "w") as f:
                f.write(T["no_calendars"])
            return

        my_calendar = calendars[0]
        config = get_config()
        now = datetime.now()
        looking_ahead = False

        if config["view"] == "day":
            if now.hour >= SWITCH_HOUR:
                # Nach 20 Uhr – morgige Termine laden
                start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                end = start.replace(hour=23, minute=59, second=59)
                looking_ahead = True
            else:
                start = now
                end = now.replace(hour=23, minute=59, second=59)
        else:  # week
            is_sunday_evening = now.weekday() == 6 and now.hour >= SWITCH_HOUR
            if is_sunday_evening:
                # Sonntag nach 20 Uhr – nächste Woche laden
                start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0)
                end = start + timedelta(days=6)
                end = end.replace(hour=23, minute=59, second=59)
                looking_ahead = True
            else:
                start = now
                tage_bis_sonntag = 6 - now.weekday()
                end = now + timedelta(days=tage_bis_sonntag)
                end = end.replace(hour=23, minute=59, second=59)

        events = my_calendar.date_search(start=start, end=end, expand=True)
        anzahl = len(events)

        lines = []
        if config["view"] == "day":
            if looking_ahead:
                if anzahl == 0:
                    lines.append(T["no_events_tomorrow"])
                elif anzahl == 1:
                    lines.append(T["one_event_tomorrow"])
                else:
                    lines.append(T["many_events_tomorrow"].format(anzahl))
            else:
                if anzahl == 0:
                    lines.append(T["no_events_day"])
                elif anzahl == 1:
                    lines.append(T["one_event_day"])
                else:
                    lines.append(T["many_events_day"].format(anzahl))
        else:  # week
            if looking_ahead:
                if anzahl == 0:
                    lines.append(T["no_events_next_week"])
                elif anzahl == 1:
                    lines.append(T["one_event_next_week"])
                else:
                    lines.append(T["many_events_next_week"].format(anzahl))
            else:
                if anzahl == 0:
                    lines.append(T["no_events"])
                elif anzahl == 1:
                    lines.append(T["one_event"])
                else:
                    lines.append(T["many_events"].format(anzahl))

        events.sort(key=lambda x: x.vobject_instance.vevent.dtstart.value)
        for i, event in enumerate(events):
            vcal = event.vobject_instance.vevent
            summary = vcal.summary.value
            start_time = vcal.dtstart.value
            if not isinstance(start_time, datetime):
                start_time = datetime.combine(start_time, datetime.min.time())

            formatierte_zeit = start_time.strftime("%a, %d.%m. %H:%M")
            lines.append(f"• {formatierte_zeit}: {summary}")
            if i < len(events) - 1:
                lines.append("")

        if LANG == "de":
            zeitstempel = "##Zuletzt aktualisiert: " + datetime.now().strftime("%H:%M")
        else:
            zeitstempel = "##Last updated: " + datetime.now().strftime("%H:%M")
        lines.append("")
        lines.append(zeitstempel)

        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(lines))

    except Exception as e:
        with open(OUTPUT_FILE, "w") as f:
            f.write(T["error"].format(e))

if __name__ == "__main__":
    check_calendar()
