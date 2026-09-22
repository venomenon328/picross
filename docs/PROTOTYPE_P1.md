# P1: Großraster- und Bedienprototyp

Stand: 22.09.2026 · Spezifikation 0.2 · Entscheidungen bestätigt, technische Startprüfung noch offen

## 1. Geltung, Auftrag und Quellen

Paketquelle ist [Issue #5](https://github.com/venomenon328/picross/issues/5). Dieses Dokument übernimmt dessen Spezifikationsentwurf 0.1 und die anschließenden Nutzerantworten. Hier stehen die versionierten P1-Verträge; das Issue führt Auftrag, aktuellen Ausführungsstand, offene Prüfungen und spätere Entscheidungen. Änderungen an diesen Verträgen sind in Datei und Issue-Verweis konsistent nachzuführen, nicht in einer zweiten parallelen Vollspezifikation.

Maßgebliche Grundlagen sind [Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md), [Projektprofil](PROJECT_PROFILE.md) und [lokaler Workflow](dev-rules/WORKFLOW.md); Einstieg bleibt [AGENTS.md](../AGENTS.md). Geprüfte Ausgangsbasis dieser Spezifikation: `main` / `5e610126737460dc0290c8360294daca72e6eb9c`. Vor Ausführung die aktuellen Quellen und Issue-Kommentare prüfen.

Der Auftrag „Bitte ergänze die Spezifikation im Repo und merge“ erlaubt die Dokumentation der beantworteten Fragen und deren Merge. Er ist kein Auftrag, den Prototyp zu implementieren oder einen späteren Produkt-PR zu mergen. Issue #5 bleibt bis zur tatsächlichen Lieferung und Abnahme offen.

Die P1-Entscheidungen konkretisieren den begrenzten Bedienversuch. Sie legen weder die endgültige Produktengine noch die gesamte Betriebssystemmatrix, Wertung oder Themenwahl fest. Frühere als offen beziehungsweise vorgeschlagen bezeichnete P1-Alternativen in Issue-Revision 0.1 und Gestaltungskonzept Abschnitt 7 sind insoweit durch die folgenden Entscheidungen abgelöst; globale Produktfragen bleiben außerhalb dieser P1-Grenze offen.

## 2. Bestätigte Entscheidungen und Referenzumgebung

| ID | Entscheidung für P1 | Stand und Grenze |
| --- | --- | --- |
| D-01 | Native Windows-Desktopfassung mit Godot 4; Testplattform Windows 11. Der angenommene Godot-Vorschlag verwendet typisiertes GDScript, nicht C#/.NET und nicht den Browseransatz. | Godot/Windows ausdrücklich bestätigt. Die konkrete Versionsbindung ist eine technische P1-Konkretisierung in Abschnitt 7, keine endgültige Produktstackentscheidung. |
| D-02 | Reduzierte Spielprobe: reale Bearbeitung, Abschluss und Speicherung; keine Sterne-/Fehlerwertung, Live-Fehlerhilfe oder Hypothesen. | Bestätigt. Bestätigte Funktionen des späteren Produkts werden dadurch nicht gestrichen. |
| D-03A | Elastische Strichvorschau: Rückwärtsziehen verkürzt den noch nicht übernommenen Abschnitt; Loslassen übernimmt ihn als eine Aktion. | Bestätigt. Keine bleibende Farbspur außerhalb des zuletzt gewählten Abschnitts. |
| D-03B | Vorhandene Einträge schützen: Füllen/Leermarkieren verändern nur unbekannte Zellen; bewusste Korrektur durch Radieren und erneutes Setzen. | Bestätigt. Die spätere Wertung des Radierens ist damit nicht entschieden. |
| D-04 | Leere Felder müssen nicht vollständig ausgekreuzt werden. Die korrekte vollständige Füll-/Farbverteilung reicht zum Abschluss. | Die Antwort „Nein“ bezieht sich auf die Pflicht zum Markieren sämtlicher Leerfelder. |
| D-05 | Referenztest: Windows 11, 2560×1440, Maussteuerung, AMD Ryzen 7 5800X, NVIDIA GeForce RTX 3070. | Diese Angaben sind bestätigt. Anzeigeskalierung, Controllergerät und Controller-Tester wurden nicht genannt. Keine Werte dafür erfinden. |

Der Nutzer testet primär mit der Maus. Daraus folgt weder, dass er keinen Controller besitzt, noch eine Streichung der bereits vorgesehenen Tastatur-/Controlleralternative. Der echte Controllerprüfweg bleibt vor der Implementierungsfreigabe abzustimmen; ein Maus- oder emulierter Test weist ihn nicht nach. Die reale Windows-Anzeigeskalierung ist spätestens im Testprotokoll zu erfassen. 2560×1440 bezeichnet zunächst die gemeldete Bildschirmauflösung, nicht automatisch logische UI-Pixel oder 100 % Skalierung.

## 3. Ziel, Umfang und Nichtziele

**Untersuchungsfrage:** Kann der Nutzer große klassische und farbige Nonogramme präzise bearbeiten, darin navigieren und nach Unterbrechung weiterarbeiten, ohne die Orientierung zu verlieren?

P1 ist ein zusammenhängender Bedienversuch, kein vollständiges Spiel und kein Sammelpaket für alle Risikoprototypen.

### 3.1 Enthalten

- Kleine Album-Testauswahl mit neutraler Eintragsnummer, Größe, Rätselart und Bearbeitungsstand. Alle P1-Testfälle direkt zugänglich; keine Freischaltlogik.
- Tatsächliche Zellbearbeitung, Farbwahl, Achsenbindung, elastische Vorschau, Schutz bestehender Einträge sowie Undo/Redo.
- Große Arbeitsansicht mit zugeordneten Hinweisen, Linienfokus, interaktiver Miniatur, Zoom/Pan und getrennt skalierbarer Oberfläche.
- Ein lokaler fortsetzbarer Arbeitsstand je Testfall einschließlich des vereinbarten Ansichts- und Undo-/Redo-Zustands.
- Einfacher, tatsächlicher Abschluss und motivtreue Darstellung im Album für die spielbaren Testfälle.
- Automatisierte Prüfungen, Start-/Bedien-/Resetanleitung, Windows-Testartefakt und nachvollziehbare manuelle Erprobung.

### 3.2 Nicht enthalten

Keine Sterneberechnung, Perfektionsanzeige, Fehlerstatistik, Rangliste, Freischaltungen, Bonuslogik, Live-Fehlerhilfe oder Hypothesen. Kein allgemeiner Solver, Produktionseditor, Bildimport, Community-Funktion, Audio, aufwendige Buchanimation, finale A/B-Entscheidung, Verbundraster oder Regionenregeln. Kein Hosting, Steam, Release, Installer, Cloudkonto oder kostenpflichtiger Dienst. Keine globale Tastenumbelegung und kein vollständiges Accessibility-Optionsmenü; klare Fokusführung, skalierbare Schrift und Alternativen zum Mausziehen gehören dennoch zur Untersuchung.

Die bestätigte spätere Perfektionsregel „ohne Fehler und ohne Undo“ bleibt erhalten. P1 darf mangels Wertung keinen Durchgang als perfekt ausweisen. Eine Bearbeitungshistorie ist kein vollständiges Ergebnislogbuch. Hypothesen und die Wertungswirkung manueller Korrekturen bleiben globale offene Fragen; für P1 sind sie keine Voraussetzung.

### 3.3 Gestaltung und Spoilergrenze

Warmes, ruhiges handgezeichnetes 2D-Album mit klaren Konturen und ruhigen Farbflächen. Im Arbeitsbildschirm bleibt die Thematik dezent erkennbar, das Raster selbst präzise. Keine Buchfalte durch das Raster, keine unleserlichen handschriftlichen Hinweisziffern und keine dekorativen Objekte über Arbeitszellen. Die Themenalternativen Sammelalbum und Reisealbum bleiben offen.

Vor tatsächlichem Abschluss weder fertiges Motivbild noch Motivname oder verräterischer Albumplatzhalter. Die während des Lösens stets sichtbare Miniatur zeigt ausschließlich den eigenen Stand einschließlich Fehlern. M-01 aus dem Gestaltungsgespräch ist eine Stilreferenz, keine Vorlage für gültige Rasterdaten, Lösungsvorschauen oder Sterneskalen.

## 4. Testdaten und Datenvertrag

| Kennung | Testfall | Zweck und Nachweis |
| --- | --- | --- |
| F-01 | 20×20 monochrom mit erkennbarem Motiv | Vollständiger Ablauf, Grundbedienung und zugehörige Kolorierung. Eigener oder geklärt nutzbarer Datensatz mit dokumentierter Deduktionsfolge. |
| F-02 | 40×40 mit vier Farben | Farbwahl, direkt angrenzende verschiedenfarbige Blöcke und lange Hinweise. Ebenfalls nachvollziehbare Deduktionsfolge für den spielbaren Fall. |
| F-03 | Vollständig navigierbares 100×100-Stressraster | Großraster, lange Hinweisfolgen und Performance; kein statisches Ausschnittbild. Kennzeichnung „UI-Testdatensatz – Rätselqualität nicht abgenommen“. |

F-01/F-02 dürfen einfach sein. Eine endliche prüfbare Lösungsbegründung für diese Fixtures genügt; ein allgemeiner erklärender Solver ist nicht beauftragt. Eine bekannte Lösung oder passende Zahlen allein belegen keine deduktive Lösbarkeit. Fehlenden Nachweis nicht durch vorgegebene Startzellen, notwendiges Raten oder eine fingierte Qualitätsfreigabe ersetzen. F-03 ist keine Ausnahmegenehmigung für ungeprüfte reguläre Produkträtsel.

Zusätzliche automatisierte Randfälle: leere Linie, ein voller Block, gleichfarbige Blöcke mit notwendiger Leerzelle, direkt angrenzende verschiedenfarbige Blöcke und eine gültige Hinweisfolge, die deutlich länger als der normale Hinweisbereich ist. Lange Hinweise nicht künstlich kürzen.

Definition und Spielstand sind getrennt. Für P1 JSON als Austauschformat, keine Datenbank. Definition: stabile ID/Revision, Breite/Höhe, Palette mit stabilen Farbkennungen, Lösungsmatrix, vollständige Zeilen-/Spaltenhinweise, erst nach Abschluss sichtbarer Name und Abschlussbild. P1-interner Vertrag, noch kein endgültiges Produktionsformat. Zeilen/Spalten werden intern nullbasiert von oben beziehungsweise links gezählt; UI-Koordinaten werden einsbasiert angezeigt.

Zellzustände: `unbekannt`, `leer`, `gefüllt(Farbkennung)`. Leer und unbekannt sind unterscheidbar. Farbindizes sind unabhängig von der dargestellten Palette. Hinweise müssen aus der Lösung reproduzierbar sein: Blöcke gleicher Farbe brauchen mindestens eine Leerzelle Abstand; verschiedenfarbige dürfen direkt aneinandergrenzen. Gespeicherte Hinweise gegen Ableitung prüfen. Dimensionen, Matrixform, Wertebereiche, Versionen und Farbverweise vor Verwendung validieren. Eine leere Hinweisfolge bedeutet eine vollständig leere Linie und benötigt eine eindeutige UI-Darstellung.

## 5. Interaktionsvertrag

### 5.1 Werkzeuge und Strichgrenzen

Linke Maustaste setzt die aktive Farbe; rechte Maustaste markiert leer. Bei gewähltem Radierwerkzeug setzt die linke Taste auf unbekannt zurück; rechte Taste bleibt Leermarkierung. Beim gewählten Hand-Werkzeug dient die linke Taste dem Verschieben, nicht der Zellbearbeitung. Es gibt kein implizites Durchschalten aller Zellzustände durch wiederholtes Überfahren.

Füllen/Leermarkieren ändern nur unbekannte Zellen. Identische Einträge bleiben unverändert, abweichende vorhandene Einträge werden übersprungen. Radieren setzt vorhandene Einträge gezielt auf unbekannt; auch als gerader Strich. Keine automatische Prüfung, ob der übersprungene oder radierte Eintrag richtig war.

Werkzeug und Farbe werden am Gestenbeginn festgehalten. Die erste eindeutige Bewegung vom Start in eine andere Zelle legt die horizontale oder vertikale Achse fest; ab dann bleibt sie bis zum Ende gebunden. Bei einem genau diagonalen Gleichstand bleibt zunächst nur die Startzelle in der Vorschau; bei eindeutiger dominanter Richtung wird die Achse verriegelt. Zwischenzellen eines Eingabesprungs werden innerhalb des geraden Abschnitts lückenlos berücksichtigt.

Die Vorschau zeigt nur den Abschnitt zwischen Start und aktuell auf die Achse projiziertem Endpunkt. Rückwärtsbewegung verkürzt ihn, Überqueren des Starts bleibt auf derselben Achse. Erst Loslassen übernimmt die wirksamen Änderungen atomar. Beispiel: Start Spalte 5, ziehen bis 12, zurück bis 9, loslassen ergibt nur 5–9; geschützte Vorbelegungen darin bleiben bestehen. Eine Abschlussprüfung findet erst nach Übernahme statt, nie aus der Vorschau.

Escape oder Fokusverlust verwirft die unbestätigte Vorschau vollständig. Außerhalb des sichtbaren Rasterbereichs bleibt der letzte gültige Endpunkt stehen; kein Zeichnen unter Werkzeugen und kein automatisches Scrollen während des Strichs. Zoom/Pan sind während der Geste gesperrt. Werkzeug-/Farbwechsel wirken frühestens auf die nächste Geste. Beim regulären Verlassen wird eine laufende Vorschau verworfen, bevor der bestätigte Stand gespeichert wird.

Eine wirksame zusammenhängende Aktion ist ein Undo-Schritt. Redo stellt die Änderung exakt wieder her. Eine neue wirksame Änderung nach Undo verwirft den Redo-Zweig. No-ops erzeugen keinen Historieneintrag; Navigation ist keine Zellaktion. Fehlerfreiheit oder Sterne werden daraus in P1 nicht abgeleitet. Die spätere Wertung von Radieren, Vorschauabbruch und No-ops wird nicht vorentschieden.

### 5.2 Zoom, Hinweise und Miniatur

Mausrad zoomt mit möglichst stabiler Rasterposition unter dem Zeiger. Mittlere Maustaste oder Hand-Werkzeug verschieben. Sichtbare Zoomknöpfe, Gesamtansicht und Rückkehr zur Arbeitsgröße bieten Alternativen. Die Rasteransicht muss bei 100×100 tatsächlich unterschiedliche Bereiche zugänglich machen, nicht nur ein verkleinertes Bild anzeigen.

Hinweise bleiben den sichtbaren Zeilen-/Spaltenindizes zugeordnet; aktive Linie und Koordinaten unterstützen die Orientierung. Sie beschreiben stets die ganze Linie. Bei Platzmangel den Überlauf eindeutig kennzeichnen und eine vollständig lesbare Fokusansicht anbieten, erreichbar mit Maus, Tastatur und Controller. Keine versteckt abgeschnittenen Hinweise und keine Verkleinerung bis zur Unlesbarkeit. Großrasterzoom und UI-/Hinweisschriftgröße sind nicht zwangsläufig gekoppelt.

Keine automatische Fehler- oder Erfüllungsmarkierung durch Vergleich mit der Lösung. Manuelles beziehungsweise komplexes automatisches Abhaken von Hinweisen ist in P1 nicht erforderlich.

Die Miniatur wird nur aus Spielerzustand und gegebenenfalls derselben aktiven Vorschau erzeugt. Unbekannt, leer und gefüllt bleiben unterscheidbar; keine korrigierte oder vorweggenommene Lösung. Ein Ausschnittrahmen zeigt den sichtbaren Bereich. Klick und Ziehen navigieren, ändern aber keine Zellen.

Vier Rätselfarben sind über Palette und alternative Aktionen erreichbar, mit zusätzlicher stabiler Symbol-/Buchstabenkennung. Auswahl, Fokus und Leerzustand dürfen keine weitere Rätselfarbe vortäuschen. Für P1 eine geprüfte Palette statt beliebiger benutzerdefinierter Paletten.

Layoutprüfungen: 1280×720 und 1920×1080 als logische Referenzflächen plus die tatsächliche 2560×1440-Testumgebung. Physische Auflösung, Fenstergröße und Skalierung getrennt protokollieren. Kleinere Fenster dürfen eine eindeutige Mindestgrößenmeldung statt eines beschädigten Layouts zeigen. Kein Rückschluss auf 100 % Windows-Skalierung aus den Hardwareangaben.

### 5.3 Tastatur und Controller

Maussteuerung ist die bestätigte primäre Nutzerprobe. Der aus dem Entwurf übernommene Alternativpfad arbeitet mit einem sichtbaren Zellcursor, nicht mit einem simulierten Mauszeiger: Cursorbewegung, Füllen, Leer, Radieren, Farbwechsel, Undo/Redo, Zoom/Pan, vollständige Hinweisansicht und Album/Zurück. Zentrale Aktionszuordnung und sichtbare Belegungshinweise. Texteingaben oder Schaltflächenfokus lösen keine Rasteraktionen aus.

Einzelzellen lassen sich ohne anhaltendes Gedrückthalten bearbeiten. Für Linien wird zusätzlich Start/Ende ausdrücklich bestätigt; dieselbe Achsenbindung und Aktionsgrenze gelten. Controllertrennung beziehungsweise Fokusverlust verwirft unbestätigte Eingaben sicher. Keine unerwartete Fortsetzung nach Wiederverbinden. Konkrete Tastenbelegung ist innerhalb dieser Grenzen ein reversibles Implementierungsdetail und muss mit der Lieferung dokumentiert werden.

Der echte Controller-Hardwaretest ist noch nicht zugeordnet. Er wird weder aus „Maussteuerung“ heraus als entfallen gewertet noch durch Tastaturemulation als bestanden erklärt. Vor der Implementierungsfreigabe Gerät/Tester bestimmen oder einen abweichenden Gate-Zeitpunkt ausdrücklich vereinbaren.

### 5.4 Abschluss ohne Pflicht zum Auskreuzen

Nach einer übernommenen Aktion ist das Rätsel genau dann gelöst, wenn jede in der Lösung gefüllte Zelle im Spielerstand mit der richtigen Farbe gefüllt ist und jede in der Lösung leere Zelle entweder unbekannt oder leer markiert ist. Zusätzliche Füllung, fehlende Füllung oder falsche Farbe verhindern den Abschluss. Auch eine fälschlich leer markierte Motivzelle verhindert ihn.

Es müssen nicht alle Hintergrundfelder mit Kreuzen versehen werden. Vor dem vollständigen Treffer weder Fehlermeldung noch Prozent-richtig-Anzeige oder korrigierte Miniatur. Beim Treffer einfache Abschlussansicht mit Hinweis „Prototyp ohne Wertung“. Monochrom: das erarbeitete Motiv und seine eindeutig zugehörige farbige Repräsentation; optional höhere Auflösung, keine unabhängige Belohnungsillustration. Erst danach Motivname und fertiger Albumeintrag. F-03 bleibt als technischer Stresstest gekennzeichnet, auch bei gefülltem Sollzustand.

## 6. Speicherung und Wiederaufnahme

Isolierter P1-Speicherbereich, keine fremden Spielstände, Cloudkonten oder Repositorydateien. Pro Puzzle speichern: Definitions-ID/Revision, Zellmatrix, wirksame Undo-/Redo-Aktionen, Undo-verwendet-Merkmal als Metadatum ohne Perfektionsaussage, Zoom/Ausschnitt, aktive Farbe/Werkzeug, Cursor und Abschlussstatus. Keine Hypothesenfelder. Redo oder Speichern/Fortsetzen löschen das Undo-verwendet-Merkmal nicht. Das ist keine vollständige Fehlerhistorie und keine Zusicherung späterer Produktspielstandkompatibilität.

Nach übernommenen Zellaktionen sowie beim Verlassen sichern. Ansichtsänderungen dürfen zusammengefasst gespeichert werden, müssen aber vor regulärem Schließen berücksichtigt sein. Keine halb ausgeführten Striche speichern. Bei Schreibfehler klar warnen und nicht fälschlich „gespeichert“ anzeigen.

Die neue Fassung erst vollständig schreiben und validieren, dann die gültige Fassung ersetzen; vorige gültige Fassung erhalten. Nach unterbrochenem Schreiben niemals eine halbe Matrix laden. Defekte, unbekannt versionierte oder zur Definition inkompatible Daten nicht stillschweigend überschreiben. Erklärung und bewussten Neustart anbieten. Ein Neustart betrifft nur den gewählten P1-Teststand und erfordert Bestätigung; er entscheidet keine spätere Wiederholungs-/Wertungsregel.

Bei geänderter Fenstergröße den gespeicherten Rasterfokus sinnvoll erhalten und den Ausschnitt gültig begrenzen. Automatisierte Speicher-/Fehlertests verwenden ausschließlich eigene temporäre Daten. Der spätere Testlauf darf keine Nutzerspielstände lesen oder verändern.

## 7. Technikbindung und vorgesehener Prüfweg

### 7.1 P1-Technik

Godot Standard mit typisiertem GDScript, Windows-x86_64-Testexport, kein .NET-SDK und kein Runtime-Backend. Als reproduzierbare P1-Ausgangsversion wird **Godot 4.7.2-stable** festgelegt. Editor und Exportvorlagen müssen exakt zusammenpassen. Diese Versionskonkretisierung erfolgte bei der Spezifikationspflege anhand des offiziellen Releases; sie ist keine Behauptung einer bereits installierten oder getesteten Laufzeit.

Primärquelle: [offizieller Release 4.7.2-stable](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable), Release-Metadaten am 22.09.2026 abgerufen, `draft=false`, `prerelease=false`, veröffentlicht am 18.08.2026. Unterschiedlich gecachte allgemeine Downloadseiten sind kein Grund, ungeprüft eine andere Version oder `latest` zu verwenden. Downloads bei der Einrichtung über den genannten Release beziehen, konkrete Assetnamen und SHA-256-Werte im Implementierungspaket festhalten und die heruntergeladenen Dateien vor Verwendung prüfen. Kein Herunterladen oder Einchecken von Engine-Binärdateien in diesem Dokumentpaket.

Vorgesehener Projektpfad: `prototypes/p1/`. Eigene Zeichen-/Hit-Test-Komponente für das Raster, keine Pflicht zu einer Schaltfläche pro Zelle. Menü, Palette und Fokusbereiche nutzen die UI-Bausteine. Raster-/Aktionsmodell, Ansichtskoordinaten und Speicherung getrennt testbar halten. Keine Abstraktionsplattform für hypothetische Engines und keine neue Drittanbieterabhängigkeit ohne begründeten Bedarf. Deutsche UI-Beschriftung; keine vollständige Lokalisierungsinfrastruktur.

### 7.2 Befehlsvertrag für das spätere Implementierungspaket

Die folgenden Pfade, Testskripte und Exportpresets sind **zu liefernde Bestandteile**, noch keine existierenden Dateien oder ausgeführten Tests. `godot` bezeichnet den oben gebundenen Standard-Editor im jeweiligen Ausführungspfad, unter Windows entsprechend dessen Konsolenprogramm. Keine Installation an einem erfundenen Nutzerpfad voraussetzen.

```sh
godot --version
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
godot --headless --path prototypes/p1 --export-debug "P1 Windows x86_64" build/windows/picross-p1.exe
```

Der Testrunner muss alle vereinbarten Logikprüfungen ausführen, Anzahl/Ergebnis ausgeben und bei einem Fehlschlag mit einem Fehlerstatus enden. Import-, Start- und Exportfehler sind ebenfalls als Fehlschläge zu behandeln; ein bloßer Prozessstart zählt nicht als erfolgreicher Test. Für jede CI-Phase begrenzte Laufzeit vorsehen. Start-Smoke und GUI-Erprobung getrennt ausweisen. Speicherzugriff des Testrunners und eines Start-Smokes isolieren.

Das Exportpreset wird exakt `P1 Windows x86_64` genannt. Passende Exportvorlagen vorher installieren; das Zielverzeichnis `prototypes/p1/build/windows/` vor Export anlegen. Der Exportpfad ist relativ zum Godot-Projekt, nicht zum Repository-Root. Testartefakt als ZIP mit sämtlichen zum Start nötigen Dateien, Kurz-Anleitung und Commitkennung; keine Engineinstallation beim Nutzer für die exportierte Spielprobe voraussetzen. Keine Signaturzertifikate, Releaseveröffentlichung oder Änderung von Windows-Schutzfunktionen beauftragt.

Diese Bedienung der CLI ist anhand der offiziellen [Kommandozeilendokumentation](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html) und [Windows-Exportdokumentation](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_windows.html) am 22.09.2026 geprüft. Die Befehle wurden noch nicht an einem P1-Projekt ausgeführt. Vor Implementierungsstart sind Runtime-/Exportvorlagenzugriff und der konkrete CI-Ausführungsweg zu verifizieren. Die neuen Produktjobs und tatsächlich ausführbaren Befehle werden zusammen mit der Implementierung im Projektprofil ergänzt; die jetzige Dokument-CI bleibt unverändert.

## 8. Akzeptanz und Abnahme

### 8.1 Automatisiert durch Implementierer / CI

| ID | Prüffall und Erfolg |
| --- | --- |
| A-01 | Definitionen validieren und Hinweise ableiten, einschließlich Farbtrennung, Leerlinien, Dimensionen und ungültiger Werte. F-01/F-02 mit überprüfter Deduktionsfolge; F-03 als Stressfixture gekennzeichnet. |
| A-02 | Horizontale/vertikale Gesten, diagonaler Start, Eingabesprung, elastisches Zurückziehen, Vorbelegung, Rand, Fokusverlust, Escape und No-op: nur zulässige Zellen ändern sich. |
| A-03 | Ein Strich ist atomar; Undo/Redo stellt alle betroffenen Vorzustände exakt wieder her, Redo-Verzweigung korrekt. |
| A-04 | Hit-Tests und Miniaturnavigation bei unterschiedlichen Ausschnitten, Zoom-/UI-Skalierungen adressieren die richtige Rasterkoordinate; Navigation verändert keine Zellen. |
| A-05 | Speichern/Laden von Zellen, Historie und Ansicht; korrupte Daten, unbekannte Version, Definitionskonflikt und Schreibfehler ohne stillen Verlust oder fremden Datenzugriff. |
| A-06 | Miniatur zeigt auch falsche Spielereinträge unverändert; kein Motiv-/Namensspoiler oder Live-Fehlerhinweis. Abschluss mit unbekanntem Hintergrund erfolgreich, bei Zusatzfüllung, fehlender Füllung, falscher Farbe oder leer markierter Motivzelle nicht. |
| A-07 | Import, kontrollierter Start-Smoke, Beenden und Windows-Export erfolgreich; Logs und startbares Artefakt dem konkreten Commit zugeordnet. |

Bestehende Dokumentprüfung bleibt zusätzlich erforderlich: `python3 -m unittest discover -s tools -p 'test_*.py' -v`, `python3 tools/check_docs.py`, vollständiger `git diff --check`. Sie ersetzt keine Produktprüfung. Headless-Prüfungen sind kein Nachweis visueller Lesbarkeit, realer Hardwareeingaben oder Windows-Grafikverhalten.

### 8.2 Manuelle Prüfungen am gelieferten Commit/Artefakt

| ID | Szenario und erwartetes Ergebnis | Zuständigkeit |
| --- | --- | --- |
| M-01 | F-01 mit Maus bearbeiten, rückwärts verkürzen, Vorbelegungen schützen, gezielt korrigieren und ohne vollständiges Auskreuzen abschließen. Bild/Name erst bei tatsächlichem Abschluss. | Eigentümer |
| M-02 | F-02 mit allen vier Farben und langen Hinweisen bearbeiten; Werkzeuge, Fokus und Farben unterscheidbar; vollständige Hinweise zugänglich. | Eigentümer |
| M-03 | In F-03 notierte Koordinate bearbeiten, stark zoomen, weit verschieben und über Miniatur/Koordinaten zurückfinden. Kein Orientierungsverlust durch falsch zugeordnete Hinweise. | Eigentümer |
| M-04 | Teilstand schließen, Anwendung neu starten und fortsetzen; Zellen, Undo/Redo, Farbe/Werkzeug und relevanter Ausschnitt wiederhergestellt. | Eigentümer |
| M-05 | Kernablauf ohne Maus mit Tastatur und mit echtem Controller, Fokuswechsel und Controllertrennung prüfen. Emulation ist kein Hardwaretest. | Tastaturprobe durch Eigentümer; Controllergerät/Tester noch zu benennen. |
| M-06 | Logische Referenzlayouts und reale 2560×1440-Umgebung samt tatsächlicher Windows-Skalierung prüfen; keine verdeckten Bedienelemente/abgeschnittenen Hinweise. | Eigentümer |
| M-07 | Wiederholte Eingaben, Pan und Zoom im 100×100-Raster auf Ryzen 7 5800X / RTX 3070 unter Win 11: keine verlorenen/falsch zugeordneten Aktionen und keine wahrnehmbaren Hänger. Reproduzierbaren Ablauf mit 500 Zell-/Navigationsaktionen gegen Sollzustand prüfen; Messungen und Beobachtungen getrennt dokumentieren. | Implementierer für reproduzierbaren Ablauf, Eigentümer für reale Bedienprobe. |

Protokoll: Commit/Artefaktkennung, Betriebssystem, CPU/GPU, Fenster- und Bildschirmgröße, reale Skalierung, tatsächlich verwendete Eingabegeräte, Szenario, Ergebnis und Abweichungen. RAM, Treiberversion, Bildwiederholrate oder Skalierungswert nicht erfinden. Keine pauschale FPS-Zusage allein aus der Hardwareliste.

### 8.3 Gate-Zeitpunkte

Vor Merge der späteren P1-Implementierung sind A-01 bis A-07, die Dokumentprüfung und die manuellen Szenarien M-01 bis M-07 nachzuweisen. Der noch nicht organisierte Controllerteil M-05 bleibt als offener Prüfweg sichtbar; vor Implementierungsfreigabe Gerät/Tester zuordnen oder eine Abweichung ausdrücklich vereinbaren. In dieser Dokumentation wurde keine nachträgliche Gate-Verschiebung beschlossen.

Der jetzige Merge betrifft nur die Spezifikation und unterliegt der Dokumentprüfung sowie dem inhaltlichen Review. Noch ausstehende Produkt-/Hardwareprüfungen blockieren diesen Dokumentmerge nicht und dürfen dabei nicht als bestanden dargestellt werden. Eine schlecht bedienbare, technisch startende Fassung benötigt Auswertung/Nacharbeit, keine fingierte UX-Abnahme.

## 9. Startprüfung, Lieferung und offene Restpunkte

D-01 bis D-04 sind beantwortet; D-05 enthält die bestätigte Maus-Testhardware. Noch offen sind die tatsächliche Windows-Skalierung als Prüfmetadatum, der Controllerprüfweg sowie die technische Startverifikation mit heruntergeladenem Editor, passenden Exportvorlagen, verifizierten Assetprüfsummen und konkret verfügbarem CI-/Ausführungsweg. Version und Befehlsvertrag sind bereits festgelegt, deren erfolgreiche Ausführung ist noch nicht belegt. Deshalb keine uneingeschränkte technische Startbereitschaft behaupten.

Bei einem Implementierungsauftrag diese Restpunkte gezielt prüfen und den aktuellen Issue-/Branchstand verwenden. Ein neuer Implementierungsbranch würde gemäß Workflow vom dann aktuellen `main` abzweigen. Kein Prototypcode, keine produktbezogenen Tests und kein Exportartefakt entstehen durch dieses Dokumentpaket. Ausführungsweg und gegebenenfalls Modellwahl erst für die noch ausstehende Umsetzung nach [MODEL_SELECTION.md](dev-rules/MODEL_SELECTION.md) beurteilen; nicht rückblickend für die erledigte Spezifikationspflege.

Lieferung des späteren P1-Pakets: Quellcode, Fixtures mit Herkunft und Nachweisen, Tests, Start-/Bedien-/Resetanleitung, Windows-Testartefakt und kurzer Ergebnisbericht. Keine vollständige Progression, finale Themenwahl oder Releasefähigkeit behaupten. Rätselproduktion/Solver und Verbundraster bleiben gesonderte frühe Risikostränge; P1 übernimmt sie nicht stillschweigend.
