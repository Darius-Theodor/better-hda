---
name: better-hda
description: Richtet einmalig einen Semesterordner für Studierende der Hochschule Darmstadt ein (Moodle-Zugang über die App-API, Kursordner, Semesterstand, Mail, Anleitung für den Agenten) und entfernt sich danach selbst. Nutzen bei /better-hda, "better-hda einrichten", "richte better-hda ein". Danach läuft alles über die AGENTS.md im Semesterordner, dieser Skill wird nicht mehr gebraucht.
---

# better-hda

Du richtest für den Nutzer einen Semesterordner ein, in dem ein Agent danach das ganze Studium
organisiert: Moodle beobachten, Material gezielt holen, Stand führen, nächsten Schritt
vorschlagen, Mails von der h-da-Adresse senden. Der Nutzer soll sich um nichts kümmern. Er
tippt genau zweimal ein Passwort in ein Fenster, alles andere machst du. Keine Auswahlmenüs,
keine Rückfragen, die eine sinnvolle Vorgabe ersetzen könnten.

Sprache mit dem Nutzer: Deutsch, kurz, in ganzen Sätzen. Sag vor jedem Schritt, der ein
Fenster öffnet oder länger dauert, in einem Satz, was passiert.

## Dateien des Skills

`SKILL_DIR` ist der Ordner dieser Datei (aufgelöst, nicht der Symlink; bei Installation über
`npx skills` meist `~/.agents/skills/better-hda`). Dort:

- `scripts/`: `credentials.py` (Passwortfenster und Schlüsselbund je System), `moodle.py`
  (Moodle-API: login, courses, sync, sections, fetch, news, deadlines), `mail.py` (Versand von
  der h-da-Adresse), `stundenplan.py` (iCal-Link des QIS-Stundenplans lesen). Nur
  Python-Standardbibliothek, Python 3.9 oder neuer.
- `templates/`: `AGENTS.md`, `CLAUDE.md`, `SEMESTER.md`, `config.json`, `courses.json`,
  `lernmodus.md`, `kursregeln.md`, `lern-dokument.html`, `gitignore`.

Alle Befehle unten mit `python3`; auf Windows `python`.

## Modus erkennen

1. Gibt es im Zielordner (Standard `~/hda`) eine `AGENTS.md` mit dem Abschnitt „better-hda“:
   **Aktualisieren** (unten).
2. Sonst: **Einrichtung**.

## Einrichtung

1. **Voraussetzung prüfen.** `python3 --version` (Windows `python --version`). Fehlt Python
   oder ist es älter als 3.9: installieren (macOS `brew install python` oder
   `xcode-select --install`, Windows `winget install Python.Python.3.12`, Debian/Ubuntu
   `sudo apt install python3`). Node wird nach der Installation des Skills nicht mehr gebraucht.
2. **Ordner anlegen.** Zielordner `~/hda` (Windows `%USERPROFILE%\hda`). Existiert er und ist
   nicht leer, einmal fragen, ob er benutzt werden soll; sonst ohne Frage anlegen. Darin:
   `tools/`, `vorlagen/`, `kursregeln/`. Kopieren: `scripts/*` nach `tools/`,
   `templates/config.json` nach `tools/config.json`, `templates/lernmodus.md` nach
   `kursregeln/lernmodus.md`, `templates/kursregeln.md` und `templates/lern-dokument.html`
   nach `vorlagen/`, `templates/gitignore` nach `.gitignore`. `AGENTS.md`, `CLAUDE.md`,
   `SEMESTER.md` und `courses.json` entstehen in den Schritten unten aus den Vorlagen.
3. **Moodle-Login.** Sag dem Nutzer: Es öffnet sich ein Fenster, dort h-da-Kennung und
   Passwort eintippen; das Passwort wird nur einmal benutzt und nie gespeichert, es entsteht
   ein Moodle-Token im Schlüsselbund des Systems. Dann `python3 tools/moodle.py login`
   aus dem Zielordner ausführen und auf das Ende warten. Erfolg heißt „Angemeldet als …“.
   Schlägt das Fenster fehl (kein Fenster möglich), bitte den Nutzer, denselben Befehl selbst
   im Terminal auszuführen (in Claude Code mit vorangestelltem `!`), und warte auf „fertig“.
   Falsches Passwort: einfach noch einmal starten.
4. **Kurse übernehmen.** `python3 tools/moodle.py courses`. Nimm alle Kurse ohne
   „(verborgen)“. Wähle je Kurs ein kurzes, sprechendes Kürzel (Kleinbuchstaben, 2 bis 5
   Zeichen, aus dem Titel) und einen Ordnernamen (Kleinbuchstaben, Unterstriche, keine
   Umlaute). Schreibe `tools/courses.json` nach `templates/courses.json` und lege je Kurs den
   Ordner an. Nenne die Auswahl in einem Satz und mach weiter; der Nutzer kann später Kurse
   streichen („<kurs> raus“: Eintrag aus `courses.json` und Tabelle entfernen, Ordner
   stehen lassen).
5. **Erster Sync.** `python3 tools/moodle.py sync`, dann `python3 tools/moodle.py deadlines`.
   Lies je Kurs `<ordner>/moodle/manifest.json`: Abschnittsbeschreibungen, Label-Texte und
   Ankündigungen enthalten meist Termine, Prüfungsform, Abgaben, Zeitplan, Ansprechpartner,
   Kommunikationskanäle. Lade dabei **keine** Dateien.
6. **Semesterstand und Anleitung schreiben.** `SEMESTER.md` nach `templates/SEMESTER.md`,
   nur Fakten aus Moodle; was Moodle nicht sagt, steht als „offen“. `AGENTS.md` nach
   `templates/AGENTS.md`: Semester (z. B. „WS 2026/27“), Kurstabelle, `<REPO_URL>` durch die
   Quelle dieses Skills ersetzen (steht in `README.md` des Skills). `CLAUDE.md` aus der
   Vorlage. Lernmodus bleibt überall „aus“.
7. **Mail einrichten.** Aus `python3 tools/moodle.py whoami` kommen Name und Kennung. Trage in
   `tools/config.json` unter `mail` ein: `user` = Kennung, `name` = voller Name, `address` =
   `vorname.nachname@stud.h-da.de` aus dem Namen (Kleinbuchstaben, Leerzeichen zu Punkt,
   ä→ae, ö→oe, ü→ue, ß→ss). Sag dem Nutzer: Noch einmal ein Fenster, dasselbe Passwort,
   diesmal für Mail; es wird gespeichert, damit Mails ohne Nachfrage rausgehen. Dann
   `python3 tools/mail.py login`. Scheitert die Anmeldung, frag einmal nach der richtigen
   h-da-Mailadresse, trag sie ein und versuch es erneut; scheitert es wieder, lass Mail aus
   und notiere in `SEMESTER.md` unter Offen: „Mail einrichten: `python3 tools/mail.py login`“.
8. **Skill entfernen.** Der Ordner ist jetzt eigenständig, der Skill würde nur bei jedem
   Sitzungsstart Kontext kosten. Installiert über `npx skills`:
   `npx skills remove better-hda -g -y`; sonst den Skill-Ordner und einen etwaigen Symlink
   darauf in `~/.claude/skills/` oder `~/.codex/skills/` löschen. Ein Satz an den Nutzer dazu.
9. **Abschluss.** Kurze Zusammenfassung: Ordnerpfad, welche Kurse, was aus Moodle schon
   bekannt ist, dass Mail geht (oder offen ist), und dass „Stundenplan einrichten“ und
   „Lernmodus für <kurs> an“ später jederzeit möglich sind. Dann direkt den Einstieg aus der
   neuen `AGENTS.md` ausführen: was ist neu, welcher Block ist jetzt sinnvoll, anfangen.

## Aktualisieren

`scripts/*` nach `tools/` und `templates/kursregeln.md`, `templates/lern-dokument.html` nach
`vorlagen/` kopieren, `templates/lernmodus.md` nach `kursregeln/lernmodus.md` nur, wenn die
Datei dort unverändert zur alten Vorlage ist. `config.json`, `courses.json`, `SEMESTER.md`,
`AGENTS.md`, Kursordner und Kursregeln bleiben unangetastet. Danach Schritt 8 und ein Satz,
was sich geändert hat.

## Regeln

- Nie Zugangsdaten über den Chat abfragen oder in Dateien schreiben. Nur das Fenster der
  Scripts; gespeichert wird das Moodle-Token und das Mail-Passwort im Schlüsselbund des Systems.
- Nie Bulk-Download. Das Manifest ist der Überblick, Dateien kommen später bei Bedarf.
- Kursmaterial nie in ein Git-Repo.
- Nichts erfinden: Termine, Prüfungsformen und Fristen nur aus Moodle oder vom Nutzer.
- Umfragen, Abgaben, Tests und Forenbeiträge nie für den Nutzer absenden.
