#!/usr/bin/env python3
"""Zugangsdaten für better-hda: Passwortfenster und sichere Ablage, je nach System.

Wird von moodle.py und mail.py importiert, nicht direkt aufgerufen.

  ask_secret(prompt)            Passwort über ein Systemfenster abfragen (verdeckte Eingabe).
  ask_text(prompt, default)     Sichtbare Eingabe über ein Systemfenster (z. B. Benutzername).
  get(account)                  Gespeichertes Geheimnis lesen, None wenn keins da ist.
  set(account, secret)          Geheimnis speichern.
  delete(account)               Geheimnis löschen.

Ablage je System: macOS Schlüsselbund (Dienst „better-hda“), Windows DPAPI-verschlüsselte
Datei unter %APPDATA%\\better-hda, Linux secret-tool (GNOME Keyring / KWallet). Fehlt auf
Linux secret-tool, landet das Geheimnis in einer Datei unter ~/.config/better-hda mit
Rechten 600. Fenster: macOS osascript, Windows PowerShell (Get-Credential), Linux zenity;
ohne Fenster bleibt die Terminaleingabe, wenn ein Terminal da ist.
"""
import getpass
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

SERVICE = "better-hda"
SYSTEM = platform.system()  # Darwin, Windows, Linux
TITLE = "better-hda"

if SYSTEM == "Windows":
    FILE_DIR = Path(os.environ.get("APPDATA", Path.home())) / "better-hda"
else:
    FILE_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "better-hda"


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# --- Eingabefenster ------------------------------------------------------------

def _terminal(prompt, hidden):
    if not sys.stdin.isatty():
        sys.exit("Kein Eingabefenster möglich und kein Terminal. Bitte den Befehl selbst in einem "
                 "Terminal ausführen (in Claude Code mit vorangestelltem `!`).")
    return getpass.getpass(prompt + ": ") if hidden else input(prompt + ": ")


def _dialog(prompt, hidden, default=""):
    if SYSTEM == "Darwin":
        hide = " with hidden answer" if hidden else ""
        script = (f'tell application "System Events" to activate\n'
                  f'text returned of (display dialog "{prompt}" default answer "{default}"'
                  f'{hide} with title "{TITLE}" buttons {{"Abbrechen", "OK"}} default button "OK"'
                  f' cancel button "Abbrechen")')
        r = _run(["osascript", "-e", script])
        if r.returncode != 0:
            sys.exit("Eingabe abgebrochen.")
        return r.stdout.rstrip("\n")
    if SYSTEM == "Windows":
        env = dict(os.environ, BH_PROMPT=prompt, BH_DEFAULT=default or "Benutzername")
        if hidden:
            ps = ("$c = Get-Credential -UserName $env:BH_DEFAULT -Message $env:BH_PROMPT; "
                  "if ($c) { $c.GetNetworkCredential().Password }")
        else:
            ps = ("Add-Type -AssemblyName Microsoft.VisualBasic; "
                  "[Microsoft.VisualBasic.Interaction]::InputBox($env:BH_PROMPT, 'better-hda', $env:BH_DEFAULT)")
        r = _run(["powershell.exe", "-NoProfile", "-Command", ps], env=env)
        if r.returncode != 0 or not r.stdout.strip():
            sys.exit("Eingabe abgebrochen.")
        return r.stdout.rstrip("\r\n")
    if shutil.which("zenity"):
        cmd = ["zenity", f"--title={TITLE}", f"--text={prompt}"]
        cmd += ["--password"] if hidden else ["--entry", f"--entry-text={default}"]
        r = _run(cmd)
        if r.returncode != 0:
            sys.exit("Eingabe abgebrochen.")
        return r.stdout.rstrip("\n")
    return _terminal(prompt, hidden)


def ask_secret(prompt):
    value = _dialog(prompt, hidden=True)
    if not value:
        sys.exit("Leere Eingabe, abgebrochen.")
    return value


def ask_text(prompt, default=""):
    value = _dialog(prompt, hidden=False, default=default)
    if not value:
        sys.exit("Leere Eingabe, abgebrochen.")
    return value


# --- Ablage --------------------------------------------------------------------

def _file(account):
    return FILE_DIR / account


def _file_set(account, secret):
    FILE_DIR.mkdir(parents=True, exist_ok=True)
    p = _file(account)
    p.write_text(secret)
    try:
        os.chmod(FILE_DIR, 0o700)
        os.chmod(p, 0o600)
    except OSError:
        pass


def _file_get(account):
    p = _file(account)
    return p.read_text().strip() if p.exists() else None


def get(account):
    if SYSTEM == "Darwin":
        r = _run(["security", "find-generic-password", "-s", SERVICE, "-a", account, "-w"])
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    if SYSTEM == "Windows":
        enc = _file_get(account)
        if not enc:
            return None
        ps = ("$s = ConvertTo-SecureString $env:BH_ENC; "
              "[Runtime.InteropServices.Marshal]::PtrToStringAuto("
              "[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))")
        r = _run(["powershell.exe", "-NoProfile", "-Command", ps], env=dict(os.environ, BH_ENC=enc))
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    if shutil.which("secret-tool"):
        r = _run(["secret-tool", "lookup", "service", SERVICE, "account", account])
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return _file_get(account)


def set(account, secret):
    if SYSTEM == "Darwin":
        _run(["security", "add-generic-password", "-a", account, "-s", SERVICE, "-w", secret, "-U"],
             check=True)
        return "macOS-Schlüsselbund"
    if SYSTEM == "Windows":
        ps = "ConvertFrom-SecureString (ConvertTo-SecureString -String $env:BH_SECRET -AsPlainText -Force)"
        r = _run(["powershell.exe", "-NoProfile", "-Command", ps], env=dict(os.environ, BH_SECRET=secret))
        if r.returncode != 0 or not r.stdout.strip():
            sys.exit(f"Verschlüsseln fehlgeschlagen: {r.stderr.strip()}")
        _file_set(account, r.stdout.strip())
        return f"verschlüsselte Datei unter {FILE_DIR}"
    if shutil.which("secret-tool"):
        r = subprocess.run(["secret-tool", "store", f"--label={TITLE} {account}", "service", SERVICE,
                            "account", account], input=secret, text=True, capture_output=True)
        if r.returncode == 0:
            return "Schlüsselbund (secret-tool)"
    _file_set(account, secret)
    return f"Datei unter {FILE_DIR} (Rechte 600; secret-tool fehlt)"


def delete(account):
    if SYSTEM == "Darwin":
        _run(["security", "delete-generic-password", "-s", SERVICE, "-a", account])
    elif SYSTEM == "Linux" and shutil.which("secret-tool"):
        _run(["secret-tool", "clear", "service", SERVICE, "account", account])
    p = _file(account)
    if p.exists():
        p.unlink()
