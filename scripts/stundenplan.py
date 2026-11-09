#!/usr/bin/env python3
"""Stundenplan aus einem iCal-Link (QIS-Export) lesen, ohne Kalender-App.

  stundenplan.py set <url-oder-datei>   iCal-Quelle in tools/config.json eintragen
  stundenplan.py [--tage N]             Termine der nächsten N Tage (Standard 7), Ortszeit

Der iCal-Link kommt aus dem Stundenplan in QIS/my.h-da.de („Kalender abonnieren“ bzw.
„iCal-Export“). Zeiten im Export sind meist UTC; Ausgabe in Europe/Berlin.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(os.environ.get("HDA_ROOT") or Path(__file__).resolve().parent.parent)
CONFIG_PATH = ROOT / "tools" / "config.json"
try:
    LOCAL = ZoneInfo("Europe/Berlin")
except ZoneInfoNotFoundError:  # Windows bringt keine Zeitzonendaten mit
    sys.exit("Zeitzonendaten fehlen. Einmal `python -m pip install tzdata` ausführen.")
WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def load_config():
    return json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}


def read_ics(source):
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source, timeout=60) as r:
            return r.read().decode("utf-8", errors="replace")
    return Path(source).read_text(encoding="utf-8", errors="replace")


def unfold(text):
    lines = []
    for raw in text.splitlines():
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def parse_time(value, params):
    """DTSTART/DTEND-Wert nach datetime in Ortszeit; ganztägige Daten bleiben date."""
    if params.get("VALUE") == "DATE" or len(value) == 8:
        return dt.date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    t = dt.datetime.strptime(value.rstrip("Z"), "%Y%m%dT%H%M%S")
    if value.endswith("Z"):
        return t.replace(tzinfo=dt.timezone.utc).astimezone(LOCAL)
    tz = params.get("TZID")
    try:
        return t.replace(tzinfo=ZoneInfo(tz) if tz else LOCAL).astimezone(LOCAL)
    except Exception:
        return t.replace(tzinfo=LOCAL)


def parse_events(text):
    events, cur = [], None
    for line in unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT":
            if cur is not None and "DTSTART" in cur:
                events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            head, value = line.split(":", 1)
            name, *plist = head.split(";")
            params = dict(p.split("=", 1) for p in plist if "=" in p)
            if name in ("DTSTART", "DTEND"):
                cur[name] = parse_time(value, params)
            elif name in ("SUMMARY", "LOCATION", "DESCRIPTION", "RRULE"):
                cur[name] = value.replace("\\,", ",").replace("\\n", " ").replace("\\;", ";")
            elif name == "EXDATE":
                cur.setdefault("EXDATE", []).append(parse_time(value, params))
    return events


def expand(ev, start, end):
    """Einzeltermin oder einfache Wochenregel (FREQ=WEEKLY) in den Zeitraum auflösen."""
    first = ev["DTSTART"]
    dur = (ev["DTEND"] - first) if "DTEND" in ev else dt.timedelta(hours=1)
    rule = dict(p.split("=", 1) for p in ev.get("RRULE", "").split(";") if "=" in p)
    ex = {e.date() if isinstance(e, dt.datetime) else e for e in ev.get("EXDATE", [])}
    if rule.get("FREQ") not in ("WEEKLY", "DAILY"):
        return [(first, first + dur)]
    step = dt.timedelta(days=(7 if rule["FREQ"] == "WEEKLY" else 1) * int(rule.get("INTERVAL", 1)))
    until = parse_time(rule["UNTIL"], {}) if "UNTIL" in rule else None
    count = int(rule["COUNT"]) if "COUNT" in rule else None
    out, t, n = [], first, 0
    while t <= end and (count is None or n < count):
        if until is not None and t > (until if isinstance(until, dt.datetime) else dt.datetime.combine(until, dt.time.max, tzinfo=LOCAL)):
            break
        if t + dur >= start and (t.date() if isinstance(t, dt.datetime) else t) not in ex:
            out.append((t, t + dur))
        t += step
        n += 1
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("set"); s.add_argument("source")
    p.add_argument("--tage", type=int, default=7)
    args = p.parse_args()
    cfg = load_config()
    if args.cmd == "set":
        cfg["stundenplan_ics"] = args.source
        CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        print(f"Stundenplan-Quelle gespeichert: {args.source}")
        return
    source = cfg.get("stundenplan_ics")
    if not source:
        sys.exit("Keine Stundenplan-Quelle. Zuerst `stundenplan.py set <ical-link>`.")
    now = dt.datetime.now(LOCAL)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + dt.timedelta(days=args.tage)
    rows = []
    for ev in parse_events(read_ics(source)):
        for a, b in expand(ev, start, end):
            if isinstance(a, dt.date) and not isinstance(a, dt.datetime):
                if start.date() <= a < end.date():
                    rows.append((dt.datetime.combine(a, dt.time.min, tzinfo=LOCAL), "ganztägig", ev))
            elif start <= a < end:
                rows.append((a, f"{a:%H:%M}–{b:%H:%M}", ev))
    if not rows:
        print(f"Keine Termine in den nächsten {args.tage} Tagen.")
    last = None
    for a, span, ev in sorted(rows, key=lambda r: r[0]):
        day = f"{WEEKDAYS[a.weekday()]} {a:%d.%m.}"
        print(("" if day == last else f"\n{day}\n") + f"  {span:<13} {ev.get('SUMMARY', '?')}"
              + (f"  ({ev['LOCATION']})" if ev.get("LOCATION") else ""))
        last = day


if __name__ == "__main__":
    main()
