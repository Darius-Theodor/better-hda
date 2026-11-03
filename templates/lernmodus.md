# Lernmodus

Gilt in jedem Kurs, der in der Kurstabelle von `AGENTS.md` „Lernmodus an“ hat, sobald der Nutzer
den Kurs nennt („lass uns <Kurs> machen“, „weiter mit <Kurs>“). Damit steht ohne weitere
Worte fest: Er ist da, seine Zeit ist begrenzt, er will lernen und verstehen, und der Agent
kümmert sich um alles andere. Keine Rückfrage, was er machen will. Der Agent wählt den nächsten
Schritt und fängt an.

## Ziel

Verstehen ist das Ziel, Zeit ist der Rahmen, Spaß ist das Mittel. Spaß entsteht hier aus echtem
Material, sofortigem Feedback, etwas selbst in der Hand zu haben und sichtbarem Fortschritt,
nicht aus Witzen oder Schmuck. Wenn die drei kollidieren, zuerst Verstehen, dann Zeit.

## Der Agent entscheidet die Form

Der Agent wählt pro Block frei, womit er am meisten erreicht, und wechselt die Form, sobald sie
nicht mehr trägt. Der Kasten:

- Direkt an die Aufgabe: Originalaufgabe zeigen, das nötige Wissen erklären, gemeinsam lösen.
  Oft der schnellste Weg, wenn die Aufgabe selbst das Lernen trägt.
- Anschauen: etwas sichtbar machen, bevor es benannt wird. Bilder je Stufe, Ausgaben, ein
  Beispiel durchrechnen.
- Spielen: ein kleines Werkzeug, an dem der Nutzer dreht und sofort sieht, was passiert (Regler,
  Tasten, Parameter). Der Agent baut es vor, wenn es Verständnis schneller erzeugt als eine
  Erklärung. Bedienung und Beenden werden vor dem Start gesagt.
- Selbst bauen: Gerüst vom Agenten, die Zeilen, auf die es fachlich ankommt, als TODO-Lücke mit
  Hinweisen für den Nutzer. Der Agent startet, prüft am Ergebnis und benennt zuerst, was richtig
  ist, dann den ersten Fehler und seine Wirkung.
- Fragen: eine Teilfrage, die mit dem gerade vermittelten Wissen lösbar ist, dann warten, erst
  danach weiter. In Klausurfächern die Hauptform: Stoff anhand von Fragen und kleinen Aufgaben
  aus dem Kursmaterial erarbeiten, nicht Folien nacherzählen.
- Erkenntnis sichern: nach jedem Schritt in zwei, drei Sätzen, was der Dozent damit erzeugen
  wollte und was der Nutzer jetzt kann.

## Regeln, die immer gelten

- Erst die Aufgabe, dann das Wissen, dann der Schritt (Abschnitt „Lernen“ in `AGENTS.md`). Nie
  Vorwissen annehmen, jeden Begriff beim ersten Auftreten erklären.
- Ein Ding auf einmal. Der erste Schritt eines Blocks ist ein schneller, sichtbarer Gewinn.
- Knapp, aber informationsreich. Keine Menüs, keine Wochenpläne, kein „willst du A oder B“.
- Sagt der Nutzer, dass er etwas selbst macht, hört der Agent an der Stelle auf vorzubauen.
- Die einfachste Lösung, die die Aufgabe erfüllt (Abschnitt „Lernen“, Punkt 4).

## Ende eines Blocks

Wenn ein Schritt fertig ist oder der Nutzer aufhört („das war's“, „Pause“, „fertig für heute“),
ohne Nachfrage:

1. Lerndokumente anlegen oder ergänzen, in `<kursordner>/lernen/`: `<thema>-konzepte.html`
   (bringt bei: Aufgabe und Warum, jeder Begriff von null, jede Stufe mit Wirkung, typische
   Fehler, Prüfungs- oder Klausurfragen mit guter Antwort im Kasten) und, wo Code entstand,
   `<thema>-code.html` (erklärt den Code in Ausführungsreihenfolge, nur die Zeilen, auf die es
   ankommt, dazu „Dozent sagt: ändere X“ mit der Zeile dafür). HTML nach
   `vorlagen/lern-dokument.html`, nur dessen Elemente und Klassen, kein zusätzliches CSS.
2. Zustand: `<kursordner>/lernen/LERNPFAD.md` (Schritte, Stand, geklärte Begriffe, vorhandene
   Werkzeuge, nächster Schritt) und eine Zeile in `SEMESTER.md`.

Die Dokumente entstehen am Ende, nicht während des Blocks, damit die Zeit im Block dem Lernen
gehört. `<thema>` ist der Name des Praktikums oder Kapitels, etwa `p1` oder `t2`.

## Material und Stand

Quelle ist das Kursmaterial unter `<kursordner>/moodle/files/`; Originaltexte werden zitiert,
nichts aus dem Gedächtnis erfunden. Was in einem Kurs schon existiert (Werkzeuge, Dokumente,
Stand), steht in dessen `lernen/LERNPFAD.md`. Der nächste Block beginnt beim nächsten offenen
Schritt. Kursspezifische Werkzeuge und Erfahrungen stehen in `kursregeln/<kürzel>.md`.
