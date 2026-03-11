import caldav
import os
import keyring
import locale
from datetime import datetime, timedelta

def get_language():
    lang = locale.getdefaultlocale()[0]
    return "de" if lang and lang.startswith("de") else "en"

LANG = get_language()

TEXTS = {
    "de": {
        "no_events": "Du hast diese Woche keine Termine.",
        "one_event": "Du hast diese Woche einen Termin:",
        "many_events": "Du hast diese Woche {} Termine:",
        "error_password": "Fehler: Kein Passwort im Keyring gefunden.\nBitte einmalig speichern mit:\npython3 -c \"import keyring; keyring.set_password('nextcloud', 'EMAIL', 'PASSWORT')\"",
        "error": "Fehler: {}",
        "no_calendars": "Keine Kalender gefunden!",
    },
    "en": {
        "no_events": "You have no appointments this week.",
        "one_event": "You have one appointment this week:",
        "many_events": "You have {} appointments this week:",
        "error_password": "Error: No password found in keyring.\nPlease store it once with:\npython3 -c \"import keyring; keyring.set_password('nextcloud', 'EMAIL', 'PASSWORD')\"",
        "error": "Error: {}",
        "no_calendars": "No calendars found!",
    }
}

T = TEXTS[LANG]

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextcloud_display.txt")

def check_calendar():
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
        now = datetime.now()
        tage_bis_sonntag = 6 - now.weekday()
        wochen_ende = now + timedelta(days=tage_bis_sonntag)
        wochen_ende = wochen_ende.replace(hour=23, minute=59, second=59)
        events = my_calendar.date_search(start=now, end=wochen_ende, expand=True)
        anzahl = len(events)

        lines = []
        if anzahl == 0:
            lines.append(T["no_events"])
        elif anzahl == 1:
            lines.append(T["one_event"])
        else:
            lines.append(T["many_events"].format(anzahl))

        events.sort(key=lambda x: x.vobject_instance.vevent.dtstart.value)
        for event in events:
            vcal = event.vobject_instance.vevent
            summary = vcal.summary.value
            start_time = vcal.dtstart.value
            if not isinstance(start_time, datetime):
                start_time = datetime.combine(start_time, datetime.min.time())

            formatierte_zeit = start_time.strftime("%a, %d.%m. %H:%M")
            lines.append(f"• {formatierte_zeit}: {summary}")
            lines.append("")

        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(lines))

    except Exception as e:
        with open(OUTPUT_FILE, "w") as f:
            f.write(T["error"].format(e))

if __name__ == "__main__":
    check_calendar()
