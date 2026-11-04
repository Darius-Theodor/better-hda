# better-hda

Dein Agent organisiert dein Studium an der Hochschule Darmstadt: Er liest Moodle
(lernen.h-da.de), merkt, was neu ist, holt Material nur bei Bedarf, führt den Stand je Kurs
und schlägt vor, was als Nächstes sinnvoll ist. Mails an Dozenten gehen von deiner
h-da-Adresse, nach Vorschau und Okay. Du kommst, wenn du Zeit hast, sagst „was steht an“ und
fängst an.

## Einrichten

Du brauchst einen Coding-Agenten (Claude Code, Codex oder ein anderer, der Skills versteht).
Sag ihm:

```
Installier npx skills add Darius-Theodor/better-hda -g und richte better-hda für mich ein.
```

Ohne Node: „Klon https://github.com/Darius-Theodor/better-hda nach ~/.claude/skills/better-hda und
richte better-hda für mich ein.“

Dann passiert alles von selbst. Zweimal öffnet sich ein Fenster, in das du deine h-da-Kennung
und dein Passwort tippst: einmal für Moodle, einmal für Mail. Am Ende hast du einen Ordner
`~/hda` mit einem Unterordner je Kurs, einem Semesterstand und einer Anleitung für den
Agenten. Der Skill löscht sich danach selbst; alles Weitere steht im Ordner. Ab dann: Agenten
im Ordner `~/hda` starten und „was steht an“ sagen.

## Was gespeichert wird und wo

- Das Moodle-Passwort wird nur einmal benutzt und nie gespeichert. Daraus entsteht ein Token,
  das nur für Moodle gilt und im Schlüsselbund deines Systems liegt (macOS Schlüsselbund,
  Windows DPAPI-verschlüsselt unter `%APPDATA%\better-hda`, Linux GNOME Keyring/KWallet).
  Widerrufen: Moodle → Profil → Einstellungen → Sicherheitsschlüssel, lokal
  `python3 tools/moodle.py logout`.
- Das Mail-Passwort muss gespeichert werden, weil der Mailserver kein Token kennt. Es liegt am
  selben Ort. Löschen: `python3 tools/mail.py logout`.
- Kursmaterial liegt unter `<kurs>/moodle/files/` und ist per `.gitignore` von Repos
  ausgeschlossen.

## Was better-hda ist und nicht ist

better-hda ist ein privates Projekt eines Studenten und kein Angebot der Hochschule Darmstadt.
Die Scripts nutzen dieselbe Schnittstelle wie die offizielle Moodle-App, mit deinem eigenen
Konto und nur für deine Kurse. Es wird nichts in großen Mengen heruntergeladen und nichts an
Dritte geschickt: Das Script spricht nur mit lernen.h-da.de und, beim Mailen, mit dem Mailserver
der h-da. Für die Nutzung gelten die Regeln der Hochschule, so wie bei jedem anderen Zugang zu
Moodle auch.

## Welches Modell deine Unterlagen sieht

better-hda ist nur der Ordner und die Werkzeuge. Welcher Agent und welches Modell darin
arbeitet, entscheidest du; der Ordner ist an keinen gebunden.

Die h-da stellt allen Studierenden eigene Modelle bereit (siehe ki.h-da.de, Zugang über den
KI-Führerschein der Hochschule). Sie laufen auf Hochschulservern in Deutschland, und mit
OpenCode funktioniert der Ordner damit genauso wie mit jedem anderen Agenten. Für
Vorlesungsfolien, Aufgabenblätter und Forenbeiträge ist das der naheliegende Weg: Das Material
bleibt bei der Hochschule, bei der es ohnehin liegt. Wer einen externen Anbieter nutzt, trägt
dafür selbst die Verantwortung; Kursmaterial ist urheberrechtlich geschützt, und Forenbeiträge
enthalten Namen anderer Leute.

## Danach

- „Stundenplan einrichten“: Der Agent trägt den iCal-Link deines QIS-Stundenplans ein, dann
  kennt er deine Termine ohne Kalender-App.
- „Lernmodus für <kurs> an“: Der Agent erklärt Aufgaben von null, wählt die Lernform und legt
  Lerndokumente an.
- „better-hda aktualisieren“: Scripts und Vorlagen auf den neuesten Stand, deine Daten bleiben.

## Technik

Nur Python-Standardbibliothek, Python 3.9 oder neuer. Moodle wird über den Web-Service der
Moodle-App gelesen (`login/token.php`, Dienst `moodle_mobile_app`), der auf lernen.h-da.de
aktiviert ist. Andere Moodle-Instanzen mit aktiviertem App-Zugang funktionieren über
`moodle_url` in `tools/config.json`; Mail und Stundenplan sind auf die h-da zugeschnitten.
Windows und Linux sind implementiert, aber bisher nur auf macOS getestet.
