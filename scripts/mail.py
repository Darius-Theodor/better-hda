#!/usr/bin/env python3
"""Mails von der eigenen h-da-Adresse aus dem Terminal senden.

  mail.py login                        Passwort einmal über ein Fenster abfragen, am Mailserver
                                       prüfen und im Schlüsselbund ablegen.
  mail.py logout                       Passwort lokal löschen.
  mail.py send --to ADRESSE --subject BETREFF [--cc ADRESSE] [--attach DATEI ...] < text.txt
  mail.py send --to ... --subject ... --body "Kurzer Text"

Absender, Benutzername und Server stehen in tools/config.json unter "mail":
  {"address": "vorname.nachname@stud.h-da.de", "user": "stabcdef", "name": "Vorname Nachname",
   "smtp": "smtp.stud.h-da.de", "imap": "imap.stud.h-da.de"}
Versand über SMTP (Port 587, STARTTLS), danach Kopie in den Ordner „Gesendet“ per IMAP, damit
die Mail im Webmail und auf dem Handy wie eine normal gesendete auftaucht.
"""
import argparse
import imaplib
import json
import mimetypes
import os
import smtplib
import sys
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import credentials  # noqa: E402

ROOT = Path(os.environ.get("HDA_ROOT") or Path(__file__).resolve().parent.parent)
CONFIG_PATH = ROOT / "tools" / "config.json"
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
MAIL = CONFIG.get("mail") or {}
ACCOUNT = "mail"


def settings():
    for key in ("address", "user", "name"):
        if not MAIL.get(key):
            sys.exit(f"In tools/config.json fehlt unter \"mail\" der Eintrag \"{key}\".")
    return (MAIL["address"], MAIL["user"], f"{MAIL['name']} <{MAIL['address']}>",
            MAIL.get("smtp", "smtp.stud.h-da.de"), int(MAIL.get("smtp_port", 587)),
            MAIL.get("imap", "imap.stud.h-da.de"))


def password():
    pw = credentials.get(ACCOUNT)
    if not pw:
        sys.exit("Kein Mail-Passwort gespeichert. Zuerst `mail.py login` ausführen.")
    return pw


def smtp_login(host, port, address, pw):
    s = smtplib.SMTP(host, port, timeout=30)
    s.starttls()
    s.login(address, pw)  # h-da: Anmeldename beim Versand ist die Adresse selbst
    return s


def login(args):
    address, user, _, smtp_host, smtp_port, _ = settings()
    pw = credentials.ask_secret(f"h-da-Passwort für Mail ({address}). Wird gespeichert, damit Mails ohne Nachfrage rausgehen.")
    with smtp_login(smtp_host, smtp_port, address, pw):  # erst prüfen, dann speichern
        pass
    where = credentials.set(ACCOUNT, pw)
    print(f"Anmeldung ok, Passwort liegt im {where}.")


def logout(args):
    credentials.delete(ACCOUNT)
    print("Mail-Passwort gelöscht.")


def save_to_sent(msg, user, pw, imap_host):
    with imaplib.IMAP4_SSL(imap_host) as imap:
        imap.login(user, pw)
        _, folders = imap.list()
        sent = next((f.decode().rsplit(' "', 1)[-1].strip('"') for f in folders
                     if b"\\Sent" in f), "Sent")
        imap.append(f'"{sent}"', "\\Seen", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    return sent


def send(args):
    address, user, sender, smtp_host, smtp_port, imap_host = settings()
    body = args.body if args.body is not None else sys.stdin.read()
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(args.to)
    if args.cc:
        msg["Cc"] = ", ".join(args.cc)
    msg["Subject"] = args.subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=address.split("@", 1)[1])
    msg.set_content(body)
    for path in map(Path, args.attach or []):
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)

    pw = password()
    with smtp_login(smtp_host, smtp_port, address, pw) as s:
        s.send_message(msg)
    print(f"Gesendet an {msg['To']}" + (f", Cc {msg['Cc']}" if args.cc else ""))
    try:
        print(f"Kopie in „{save_to_sent(msg, user, pw, imap_host)}“ abgelegt.")
    except Exception as e:  # Versand ist erfolgt, nur die Kopie fehlt
        print(f"Hinweis: Kopie in Gesendet fehlgeschlagen ({e}).")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(fn=login)
    sub.add_parser("logout").set_defaults(fn=logout)
    s = sub.add_parser("send")
    s.add_argument("--to", action="append", required=True)
    s.add_argument("--cc", action="append")
    s.add_argument("--subject", required=True)
    s.add_argument("--body")
    s.add_argument("--attach", action="append")
    s.set_defaults(fn=send)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
