# RP-6 · Eigentümer-Spielprobe (offen)

Diese Anleitung enthält keine Motivnamen oder Lösungen. Die technischen
Paaransichten und `rp6-review` erst nach der Spielprobe ansehen.
Automatisierte Eingaben zählen nicht als echte Lösungsprobe.

## Benannten Windows-Stand starten

1. Im Draft-PR den direkt verlinkten Actions-Download
   `picross-p1-player-<Quellcommit>` laden. Dieses **schlanke Spielerartefakt**
   enthält ausschließlich die eigentliche `picross-p1-windows-x86_64.zip`;
   den großen technischen Evidenzdownload mit `renders/`, Logs und Replays
   ausdrücklich **nicht** für die Eigentümerprobe verwenden. Actions-Digest und
   Quellcommit müssen mit dem PR-Beleg übereinstimmen.
2. Die SHA-256 der enthaltenen `picross-p1-windows-x86_64.zip` mit dem PR-Beleg
   vergleichen und diese ZIP in einen neuen Ordner entpacken. Sie enthält keine
   Teststände oder Entwicklungsrender.
3. Im entpackten Ordner PowerShell öffnen und `./rp6-owner.ps1 -Trial meine-probe`
   ausführen. Der Launcher prüft den EXE-Hash gegen den Produktreport, zeigt den
   Quellcommit und verwendet ein eigenes temporäres Profil. Falls die lokale
   Skriptrichtlinie den Start blockiert, zunächst diesen Befund melden; keine
   globale Richtlinienänderung nötig. Keine vorhandenen normalen Saves ersetzen.
4. Für Fortsetzung denselben Ordner, Commit und `-Trial`-Namen verwenden. Nach
   normalem Beenden wieder mit demselben Befehl starten. `-Status` zeigt nur den
   Prüfpfad und Dateidaten. Temporäre Dateien können vom System bereinigt werden;
   vor längerer Pause nach geschlossenem Spiel den angezeigten Prüfstand sichern.
5. Im Album öffnet ein Klick ein Blatt; die Auswahl ist scrollbar. UI 100/125 %
   und Hilfe stehen im Menü. Links füllen, rechts X, Rad zoomen, Hand/mittlere
   Taste verschieben. Undo/Redo bleiben erhalten. Die kleine Vorschau zeigt nur
   eigene Einträge. Zum Abschluss genügen richtige Füllungen ohne Zusatzfüllung;
   leere Felder müssen nicht vollständig mit X markiert sein.

## Vor Beginn ausfüllen

Verantwortlicher: ____ · Datum: ____ · Quellcommit: ____ · getesteter Checkout: ____
Run/Artefaktlink: ____ · ZIP-SHA-256: ____ · EXE-SHA-256: ____
Windows-Version: ____ · Bildschirm: ____ · Windows-Skalierung: ____
Clientfläche: ____ · UI-Skalierung: ____ · Maus: ____ · Prüfpfad: ____

- **M02:** Blatt F-04 Revision 1 vollständig lösen und eines der neuen Farbblätter
  F-06/F-08/F-09 Revision 1 auswählen: ____. Auswahl vor Beginn notieren.
- **M03:** Bevorzugt F-07 Revision 1. Vor Beginn ausdrücklich festlegen:
  vollständige Lösung oder konkrete Teilprobe ____. Vorschlag: zwei Sitzungen
  zu je 45 Minuten mit echtem Beenden/Neustart dazwischen. Dieser Vorschlag ist
  noch keine Eigentümerentscheidung. Erwartete Beobachtungen: Lesbarkeit langer
  Hinweise, Navigation, eigene Miniatur, Arbeitsmenge und sichere Fortsetzung.
  Eine Teilprobe darf später nicht als vollständige Lösung bezeichnet werden.

## Je Rätsel und Sitzung protokollieren

Blatt/Revision: ____ · Start/Ende/Dauer: ____ · vereinbarter Umfang: ____
Verwendete logische Techniken (konkret): ____ · geraten/steckengeblieben: ____
Gefühlter Anspruch: ____ · unnötige Arbeit/Wiederholungen: ____
Hinweise/Farben/Bedienung/Erkennbarkeit: ____ · Abweichung oder Fehler: ____
Eigener Stand vor Beenden: ____ · tatsächliche Fortsetzung nach Neustart: ____
Tatsächlicher Abschluss (ja/nein) und Beobachtung: ____ · Beleg: ____

## M04 · spätere Eigentümerentscheidung

Erst nach den tatsächlichen Proben und der getrennten Produktionsbilanz:
für welche Eingangsklassen/Größen weiterarbeiten, wo nacharbeiten, welche Regeln
oder Produktionsoberfläche separat spezifizieren? Entscheidung und Begründung: ____
Nicht erreichte Ziele/offene Befunde: ____ · verantwortlicher Eigentümer/Datum: ____

M02, M03 und M04 sind nicht durchgeführt. Redaktionelle Gesamtfreigabe und
unabhängiges Review bleiben getrennte Gates. Kein Merge, Release oder Abschluss
von Parent #34 folgt aus diesen vorbereiteten Unterlagen.
