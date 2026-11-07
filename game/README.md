# picross: Spiel- und Entwicklungsanleitung

## Zuletzt bearbeitetes Rätsel

Im rechten Katalogkopf öffnet „Zuletzt bearbeitetes Rätsel fortsetzen“ den zuletzt
wirksam bearbeiteten, erfolgreich gespeicherten begonnenen Stand, auch außerhalb der
aktuellen Filter. Eigene Füllungen erscheinen in einer verkleinerten Vorschau.
Ohne passenden Stand oder nach Abschluss/Reset ist das Panel verborgen. Öffnen oder
Ändern der Ansicht allein setzt keinen Merker; echtes Undo/Redo schon. Ein neuer Start
zeigt weiterhin den Katalog. Der separate `user://p1/recent-puzzle.json` ändert keine
Slotdatei. Fehler des Merkers haben im Katalog einen eigenen Retry; Save-/Backupfehler
und deren bewusste Reparatur bleiben davon getrennt. Windows verwendet für atomaren
Metadatenaustausch das mitgelieferte Windows PowerShell/.NET; dessen Ausfall verhindert
nur die Aktualisierung des Merkers.

**Buchintegration B-B / #493, #498:** Windows und Web starten den regulären
Rätselkatalog als räumliches Buch. Kurzes Blättern
dauert 0,85 Sekunden; drei einzelne Blätter führen in insgesamt drei Sekunden
zur großen rechten Arbeitsseite mit Bindung links. Überarbeitete Papiertextur,
sichtbare Buchkante, ruhende Wölbung und transparente Controls erhalten die
Arbeitsbudgets. N03 revidiert Leder-/Randanschlüsse sowie Hover und leere
Tooltips bei erhaltenen sinnvollen Hilfen. N04 ergänzt ein eigenes Tischbild,
saubere innere Enden und sichere Fußbereiche auch bei 16:10. Bis zu zwölf Karten
stehen zuerst links, weitere rechts; jede Hälfte scrollt unabhängig.
Der linke Pfeil im rechten Arbeitskopf führt in 1,8 Sekunden zum vorherigen
Katalogkontext mit beiden Scrollständen zurück. Daneben öffnen Menü und Fragezeichen
Einstellungen links beziehungsweise Hilfe rechts in naher Ansicht. Zwischen
beiden Seiten wird nur gepannt; die beschriftete Rückkehr führt zum ursprünglichen
Katalog oder Rätsel. Bewusst geänderte Einstellungen bleiben erhalten.
Bearbeitung und Sortierauswahl werden über die bisherigen Speicherwege gesichert.
Bei einem Speicherfehler bleibt die Anwendung mit einer sichtbaren Wiederholung
offen; notwendige Backupübernahme verlangt weiterhin Bestätigung. Die
[historische Studie](../docs/BOOK_STUDY.md) ist aus dem aktiven Tree entfernt.
Der kurze Prüfeinstieg `tools/book_lifecycle.py` verwendet den regulären Root
mit synthetischen Daten und isolierten Speicherpfaden. [B-B-Vertrag](../docs/BOOK_INTEGRATION.md) und
[Prüfstand](../docs/B_B_VERIFICATION.md) binden die Integration; unabhängige und
persönliche Abnahmen bleiben gesondert.

**Kleine Texte und Ausrichtung (HZ-C):** Kategorien, Kartenmetadaten, Status,
Auswahllisten und kleine Papiertextbuttons verwenden eine gemeinsame etwas
größere Textrolle. Beim Wechsel von Werten bleibt die Grundlinie ruhig;
„Blatt NN“ behält seine bisherige Größe. UI100/125 skaliert die zugehörigen
Abstände und Textbudgets gemeinsam. [HZ-C-Prüfstand](../docs/HZ_C_VERIFICATION.md).

**Schrift und Lesbarkeit (PANG-A):** Normale Texte, Auswahlen, Hilfen und Tooltips
verwenden Pangolin Regular. Bestehende Überschriften und Delight-Coffee-Hinweiszahlen
bleiben unverändert. UI 100/125 % ändert Schrift und Textabstände gemeinsam;
bei schmalen Fenstern darf „Sortieren nach“ innerhalb der Kopfzeile umbrechen.
Lange Kategorien bleiben über vollständig umgebrochene Tooltips lesbar; die
native Auswahlliste scrollt vertikal. Pangolin und die lokale Plex-Ergänzung
stehen offline bereit; die Original-OFL und Herkunft liegen unter
`licenses/pangolin/` im Spielerpaket. [HZ](../docs/HAND_DRAWN_UI.md) bindet die Schriftrollen und Nachweise.

**Rahmen, Menüs und Symbole (HZ-B):** Karten und kleine Papierbuttons haben
ruhende handgezeichnete Konturen. Dropdowns öffnen auf opakem Papier; ein Haken
markiert die aktuelle Auswahl unabhängig von der angefahrenen Zeile.
Pfeile, Werkzeuge und Checkboxen gehören zur selben gezeichneten Familie.
Maus, Tastatur, Fokus und Scrollen bleiben wie gewohnt bedienbar.
[HZ-B-Lieferung und Prüfstand](../docs/HZ_B_VERIFICATION.md).

**Scrollleisten (SBR-A):** Buchseiten und lange Auswahllisten verwenden dieselben
graphitgrauen, diagonal handschraffierten Leisten mit hellem Griff und hellen
Dreieckspfeilen. Rad, Griffziehen, Spur- und Pfeilklicks bleiben die gewohnten
nativen Scrollaktionen. Leisten erscheinen nur bei Bedarf; UI100/125 skaliert
ihre Darstellung und Trefferbreite gemeinsam. [Stilvertrag](../docs/HAND_DRAWN_UI.md).

Die kompakten Katalogkacheln bleiben gleich groß, auch nach Abschluss oder Reset.
Oben steht der verdiente Motivname, vorher `???`, in derselben Bakso-Schrift wie
„Rätselkatalog“. Lange Namen nutzen zwei Zeilen, danach eine Auslassung. Darunter
steht in „Alle Rätsel“ die Kategorie; bei Filterung bleibt dieser Platz reserviert.
Neue Rätsel zeigen ein gezeichnetes Fragezeichen. Begonnene zeigen nur eigene
Füllungen, auch falsche. X und unbekannte Zellen bleiben neutral. Ein begonnener
Stand ohne Füllzellen, etwa nach Undo, zeigt eine leere Vorschau ohne Fragezeichen. Erst ein
gültiger Abschluss zeigt Motivname und farbiges Abschlussbild.

Der gemeinsame Papierstreifen unter dem Bild zeigt in einer Zeile links die
Größe, in der Mitte einen gefüllten Schwierigkeitskreis mit vollständigem Namen
und rechts den Modus: einen dunklen Stift für Mono, drei gefächerte Stifte für Farbe.
Die Stufen heißen „Sehr leicht“, „Leicht“, „Mittel“, „Schwer“ und „Sehr schwer“.
Ohne Einstufung erscheint ein neutralgrauer Kreis mit „Nicht eingestuft“.
Die Schwierigkeit hat keinen Tooltip. Der Modus erklärt sich beim Darüberfahren
mit der Maus. Ein Klick auf den Streifen öffnet das zugehörige Blatt.

In der festen Fußzeile steht links „Blatt NN“, rechts der Status mit Symbol:
offener Kreis und „Neu“, kleiner Stift und „Begonnen“, Haken und „Gelöst“.
Auch die Fußzeile öffnet dasselbe Blatt. Alle Karten einer Ansicht verwenden
identische, anhand der vollständigen Metadaten gemessene Breiten. Bei wenig Platz
erscheinen weniger Spalten; Schrift und Bildraum werden dafür nicht verkleinert.
Jede Buchhälfte zeigt höchstens zwölf Karten in bis zu drei Spalten. Bei
2560×1440/UI100 passen drei Spalten, bei 1920×1080/UI100 zwei; höhere UI-Skalierung
oder weniger Papierfläche kann die Zahl weiter begrenzen. Jede Zeile, auch eine
letzte mit nur einer oder zwei Karten, steht für sich mittig auf ihrer Hälfte.
Beide Hälften scrollen unabhängig und behalten ihre Position beim Umbruch
innerhalb der jeweils erreichbaren Grenzen.
Verdiente Reveals und Stiftsymbole bleiben lokal geglättet.
Aktueller Vertrag: [Kataloggestaltung](../docs/CATALOG_PRESENTATION.md).

Die Karte öffnet oder setzt ihr Blatt fort; gelöste Blätter öffnen die Endansicht.
Oben rechts steht bei bearbeiteten Blättern der Neustartpfeil mit „Rätsel zurücksetzen“.
Er verlangt Bestätigung; Abbrechen erhält den Stand. Bei gültigem leerem Stand ist
er verborgen, bei Speicher-/Recoveryproblemen bleibt er erreichbar. Ungültige Saves
sperren Öffnen und zeigen „Ungültig“. Speicherhinweise und „Backup übernehmen“ /
„Backup erneuern“ stehen im Bildraum, bei langen Diagnosen dort scrollbar.
Die Karte selbst hat keinen Tooltip; gezielte Modus- und
Resettooltips skalieren bei UI100/125 mit.

Zusätzlich gibt es den [WEB-1-Browserentwicklungsweg](../docs/WEB_HOSTING.md):
statischer Export für Chromium/Firefox mit Maus und dauerhaftem Browserspeicher.
Die Kopfzeile zeigt Build und tatsächlichen Speicherstatus. Bei Speicherfehler
offen lassen und erneut versuchen. Nur ein schreibender Tab je Origin ist erlaubt.
Build, SSH-Update, Rollback, Hostingvoraussetzungen und Speichergrenzen stehen in
der verlinkten Anleitung. Persönliche Webprobe und Live-Deployment bleiben separat.

Die Entwicklungsfassung enthält die [Kategorienprojektion nach KAT-1](../docs/CATEGORIES.md). Das Spiel startet im Rätselkatalog mit „Alle Rätsel“. Die scrollbare Kategorienauswahl enthält auch leere Kategorien; je Seite erscheinen höchstens 24 Karten. Eine Karte öffnet oder setzt genau ihr Blatt fort. Zurückkehren erhält Kategorie, Seite und Scrollposition; ein Neustart beginnt wieder bei „Alle Rätsel“, Seite 1. Einstellungen/Info und Beenden sind direkt erreichbar.

Direkt neben der Kategorie steht „Sortieren nach“: Kategorie, Größe,
Schwierigkeit oder Hinzugefügt. Der Pfeil wechselt auf- und absteigend.
Kategorie folgt der redaktionellen Reihenfolge, Größe der Zellanzahl. Bei einem
neuen Kriterium beginnt die Richtung aufsteigend; „Hinzugefügt“ zeigt zuerst die
neuesten Rätsel. Ohne Datum oder Einstufung steht ein Blatt immer hinten.
Gleichstände behalten ihre feste Blattreihenfolge; Blattnummern ändern sich nicht.

**Filter** rechts neben Sortierauswahl und Richtungspfeil öffnet die zusätzlichen
Auswahlen: **Status**
(Alle, Noch offen, Neu, Begonnen, Gelöst), **Modus** (Alle, Monochrom, Farbe),
**Schwierigkeit von/bis** (Sehr leicht bis Sehr schwer) sowie die nebeneinanderliegenden Felder
**Maximale Breite** und **Maximale Höhe**.
Alle aktiven Filter gelten gemeinsam. Grenzen sind einschließlich; gleiche
Schwierigkeitsgrenzen wählen eine Stufe. Ohne Spanne bleiben nicht eingestufte
Rätsel sichtbar; mit einer Grenze erscheinen nur passende eingestufte Rätsel.
Beide Maßgrenzen funktionieren unabhängig: jeweils leer oder eine ganze Zellzahl
von 1 bis 99. Gemeinsam müssen beide passen; Breite ≤20/Höhe ≤30 erlaubt
20×30, aber nicht 30×20. **Übernehmen** wendet gültige Eingaben gemeinsam an.
Die Schwierigkeitslisten bieten nur miteinander verträgliche Stufen an:
Minimum ≤ Maximum; nötigenfalls folgt die andere Grenze automatisch. Dafür
erscheint keine Fehlermeldung. Ungültige Breiten-/Höhenwerte werden angezeigt und
verändern die letzte gültige Auswahl nicht. **Schließen** verwirft den Entwurf. Der Panelinhalt scrollt bei
knapper Höhe; das Fenster bleibt ohne unnötigen vertikalen Leerraum am Inhalt
bemessen. Übernehmen / Zurücksetzen / Schließen stehen gleich groß in einer Zeile.
Breite/Höhe schließen jeweils rechtsbündig unter Von/Bis ab. **Zurücksetzen** setzt auch die Kategorie auf Alle und
behält die Sortierung; diese Aktion befindet sich nur im Filterfenster.
Von/Bis stehen wie Breite/Höhe nebeneinander. Fehlermeldungen stehen oben rechts
über Sortieren/Filter in einer festen, bei Bedarf scrollbaren Kopfbereichsfläche;
sie verschieben keine Kacheln oder Katalogcontrols. Entwurfsfehler stehen oben im
Filterfenster. Die Trefferzahl steht über dem rechten Buchteil;
keine passenden Treffer und Katalogladefehler sind getrennt beschriftet.
Ungültige Saves zählen nicht als Neu oder Noch offen; unter Alle bleiben ihre
Reset-/Diagnosewege erhalten. Speicherfehler bleiben auch außerhalb der Treffer
sichtbar. Abschluss und Reset aktualisieren die Liste und begrenzen die Seite.
Alle Filter gelten ausschließlich in der Sitzung; ein neuer Prozess startet
unbeschränkt. Es wird keine zusätzliche Einstellung gespeichert.

Die Sortierung bleibt lokal nach einem Neustart erhalten. Filter, Seite und
Scrollposition gelten für die laufende Sitzung; die Rückkehr aus einem Rätsel
behält sie. Ein tatsächlicher Filter- oder Sortierwechsel beginnt auf Seite 1.
„Sortierung konnte nicht gespeichert werden“ betrifft nur diese Auswahl:
„Erneut versuchen“ wiederholt die Speicherung, ohne Spielstände zurückzusetzen.
Im Browser muss der Schreibvorgang bestätigt sein, bevor der Tab geschlossen wird.

Karten zeigen „Neu“, „Begonnen“ (auch mit ausschließlich Redohistorie) oder „Gelöst“. Begonnene Vorschauen zeigen nur eigene Füllungen, ohne Korrekturen; Name und Motivbild erscheinen erst nach gültigem Abschluss. Ein leerer automatisch angelegter Save bleibt „Neu“. Reset und Backupaktionen gehören zur jeweiligen Karte und verlangen weiterhin Bestätigung. Ein gültiger leerer Bestand und ein Katalogladefehler haben unterschiedliche Anzeigen. Kategorienänderungen verändern keine Rätseldefinition, Revision oder Spielstände.

Der reguläre Spielbestand folgt `content/registry.json` und enthält ausschließlich
freigegebene Workflow-Inhalte, aktuell elf Rätsel. Weitere Inhalte werden über den
[ZA-1-Adapter](../docs/ZA1_ADAPTER.md) registriert. Historische Prototypen F-01 bis
F-09 sind seit #114 nicht mehr Bestandteil des Spielerangebots oder Exports.

Das reguläre Projekt liegt unter `game/`. Sidebar, Vollsicht, Stift-/Atlasdarstellung
und Save/Recovery sind integriert. Dies ist eine unsignierte Entwicklungsfassung,
kein Release.

Sammlungsstart, passive eigene Füllminiatur, unabhängige lange Hinweise und sechs
Sidebaraktionen in 2×3 bleiben aktiv. Das Raster samt Rahmen bleibt innerhalb
der angebotenen Fitgrenze sichtbar. „Rätselansicht“ bietet Rasteransicht und
Gesamtansicht mit allen Hinweisen; ein Sitzungswechsel ändert keine Spielstände.
Fonts, Bilder und Spieldaten liegen offline in `picross-p1.pck`; Lizenzen/Nutzungshinweise liegen im ZIP.

## Aktuellen main-Player per GitHub Actions erzeugen

Unter [GitHub Actions](https://github.com/venomenon328/picross/actions/workflows/build-main-player.yml)
den Workflow **Build playable main (Windows x64)** öffnen und über
**Run workflow** starten. Die Action checkt immer das dann aktuelle `main`
aus, unabhängig von der im Startdialog angezeigten Branch-Auswahl.
Nach erfolgreichem Lauf unter **Artifacts** das eine
`picross-main-windows-x86_64-<Commit>`-Artefakt herunterladen. Das erhaltene
ZIP **einmal** entpacken und direkt `picross-p1.exe` starten; es enthält
kein weiteres ZIP. Die Commitkennung steht auch in `README.txt`.
Das Artefakt wird 14 Tage aufbewahrt.

Diese Action erstellt ausschließlich den unsignierten Windows-Debugplayer
aus dem regulären Spielbestand. Sie startet weder die Product-Testmatrix
noch ein Release/Deployment; ein tatsächlicher Windows-GUI-Start wird auf dem
Linux-Runner nicht geprüft. Der separate CI-Playerexport bleibt unverändert.

## Windows starten

Das vollständige ZIP entpacken und `picross-p1.exe` starten. Die EXE und
`picross-p1.pck` müssen im selben Ordner bleiben. Keine Godot-Installation
nötig. `picross-p1.console.exe` zeigt technische Ausgaben. Dies ist eine unsignierte
Debug-Spielprobe, kein Release/Installer. Die Quellcommitkennung steht im beigefügten
README.txt. Ausschließlich das **Product-CI-Artefakt** enthält zusätzlich
`product-report.json` mit Head, getestetem Checkout/Test-Merge, Basis, CI-Lauf,
Engine-/Archivhashes, EXE-Hashes und Prüfphasen (Artefaktlink im PR). Der manuelle
main-Player hat bewusst keinen solchen Prüfbericht; sein Link steht im Actions-Lauf.

Godot löst `user://p1/saves/` im projektbezogenen User-Data-Verzeichnis auf.
Unter Windows liegt dieses standardmäßig unter
`%APPDATA%\Godot\app_userdata\picross · P1\p1\saves\` (bei benutzerdefiniertem
Godot-Datenpfad entsprechend dort). Dateinamen folgen dem jeweiligen Registry-Slot:
`<slot>.json`, `<slot>.bak` und `<slot>.tmp`. Vorhandene alte `f01`…`f09`-Dateien
bleiben unbenutzt auf Datenträger; sie werden weder migriert noch gelöscht.
Tests verwenden nur eigene temporäre Profile; das ZIP enthält keine
Spielstände.

Fehlendes oder beschädigtes Primary mit gültigem Backup wird sichtbar als Recovery geladen;
normales Speichern bleibt bis zur bewussten Übernahme gesperrt.
„Backup zum Speichern übernehmen“ fragt vor dem Ersetzen des Primary nach.
Bei gültigem Primary und defektem Backup bleibt der Primärstand lesbar;
„Backup erneuern“ fragt vor dem Ersatz des beschädigten Backups nach.
Ohne gültige Fassung erscheint ein Fehler. „Arbeitsstand zurücksetzen“ fragt
ebenfalls nach und entfernt ausschließlich Primary, Backup und Temp des
ausgewählten Blatts. Die anderen Blätter bleiben erhalten.
Scheitert ein verpflichtender Save, bleibt die aktuelle Ansicht offen und zeigt
den Fehler. Album, Blattwechsel und reguläres Beenden gelingen nach einem
erfolgreichen Retry.

Unter **Einstellungen → Anzeige** bietet Windows **Fenster**, **Rahmenloses Fenster**
und **Exklusives Vollbild**. Fenster lassen sich verschieben; Größe und Maximieren
sind gesperrt. Die Fenstergröße ist aus 1280×720, 1366×768, 1600×900, 1920×1080,
1920×1200, 2560×1440, 2560×1600 und 3840×2160 wählbar, soweit der gesamte Rahmen
in den aktuellen Monitorarbeitsbereich passt. Nicht passende Größen sind deaktiviert.
Vollbild verwendet die aktuelle Desktopauflösung, zeigt diese lesbar an und erhält
den letzten Fensterpreset für die Rückkehr. Die Windows-Desktopauflösung wird nicht geändert.

Die Einstellungen zeigen zwei handgezeichnete Gruppen **Anzeige** und
**Rätselansicht**, mittig auf der linken Buchseite. Feldname und Auswahl stehen
nebeneinander. Nur **Fenstergröße** und **Rätselansicht** haben ein Fragezeichen,
das beim Darüberfahren oder Tastaturfokus erklärt; die Fenstergrößenhilfe bleibt auch im Vollbild
erreichbar. **UI-Skalierung** bietet **100 %** und **125 %** für die laufende Sitzung.
Anzeigemodus und UI-Skalierung nutzen ohne Fragezeichen die volle Zeilenbreite.
Die drei großen Seitentitel **Rätselkatalog**, **Hilfe** und **Einstellungen** sind
offen schraffierte Graphit-Schriftzugbilder der freigegebenen V2-rev1-Familie; die beiden Einstellungsgruppen behalten ihre
Bakso-Überschriften. Die Titel stehen fest über dem scrollbaren Inhalt.
Der untere Button **Zurück** auf Einstellungen und Hilfe kehrt zum Besuchsursprung
zurück. Tooltip und Zugänglichkeitsname erläutern das jeweilige Katalog-/Rätselziel.
Der Wechsel zwischen Hilfe und Einstellungen steht daneben ebenfalls fest unten.
Bei knapper Höhe bleibt der Inhalt durch vertikales Scrollen erreichbar.
Beenden steht im Katalog; auch das normale Fensterschließen sichert den Stand. Das deaktivierte Größenfeld
zeigt im Vollbild die Desktopauflösung; im Fenster den gewählten Preset.

Jede Änderung wird sofort für **15 Sekunden** ausprobiert. **Beibehalten** speichert;
**Abbrechen**, Escape oder Ablauf stellt die vorherige funktionierende Anzeige wieder her.
Alt-Tab bestätigt nichts. Bei nicht verfügbarem Modus oder verändertem Monitor hilft
ein sichtbarer Fallback; er überschreibt die gespeicherte Auswahl erst nach ausdrücklicher
Bestätigung. Speicherfehler werden angezeigt und nehmen die Vorschau zurück.
Die eigene Datei `user://p1/display-preference.json` mit `.tmp`/`.bak` ist unabhängig
von Rätselsaves und Katalogsortierung; eine unterbrochene Ersetzung lädt die gültige
vorherige Fassung. Der Browser behält seine eigene Fenstersteuerung ohne diese Optionen.

Startziel ist ein vollständig passendes 1920×1080-Fenster, andernfalls ein kleinerer
Preset oder rahmenloses Vollbild. Unter 1280×720 erscheint die bestehende Mindestflächenmeldung.
720p bleibt ein begrenzter Fallback, 1080p das Komfortziel. Mehr Fensterfläche
zeigt mehr Raster oder ruhige Ränder; sie vergrößert die Arbeitszellen nicht automatisch.
Die angebotenen Zoomstufen halten das gesamte Raster samt Rahmen innerhalb
der tatsächlichen Fenster-/Hinweis-/UI-Grenzen.

## Spielerhilfe im Buch

Das Fragezeichen öffnet die rechte Informationsseite. Vier beschriftete Bereiche
sind direkt erreichbar: **Spielprinzip**, **Farbige Rätsel**, **Bedienung** und
**Lösungstipps**. Die Hilfe funktioniert auch ohne geöffnetes Rätsel. Sie erklärt
Begriffe vor ihrer Verwendung und zeigt passive Beispiele mit denselben Zahlen,
Stiftfüllungen, Rasterlinien und X wie das Spiel.

Die Beispiele zeigen eine vollständig bestimmte Siebenerzeile, ein schrittweises
5×5-Lehrbild, die Überlappung eines Fünferblocks in sieben Feldern und den
Unterschied zwischen gleich- und verschiedenfarbigen Nachbarblöcken. Drei kurze
Lösungstipps sind freiwillige Vertiefung. Die Bedienübersicht verbindet Eingabe,
vorhandenes Symbol und Wirkung; die Anzeigenlegende erklärt auch Hinweiszustände,
Leerlinienzeichen und Überlaufmarker. Diese Markierungen bestätigen keine Lösung.

Jeder neue Besuch beginnt bei Spielprinzip, jede Kapitelwahl oben. Zwischen Hilfe
und Einstellungen bleiben das Hilfekapitel und seine Lesestelle erhalten. Der
beschriftete Rückweg unten führt zum gebundenen Katalog oder Rätsel zurück.
Die Beispiele lassen sich nicht bearbeiten und erzeugen keine Spielaktion.

## Bearbeiten und zurücknehmen

- Links: unbekannt → aktive Farbe, Füllung → unbekannt, X → aktive Farbe.
- Rechts: unbekannt → X, X → unbekannt, Füllung → X.
- Auf unbekannt gestartete Setzstriche verändern nur unbekannte Zellen und schützen
  alle vorhandenen Füllungen und X. Links setzt die aktive Farbe, rechts X.
  Nur ein auf X gestarteter linker Strich wandelt unbekannte/X-Zellen in Farbe;
  nur ein auf Füllung gestarteter rechter Strich unbekannte/Füllungen in X.
  Ein auf Füllung gestarteter
  linker Rücknahmestrich entfernt nur Füllungen, ein auf X gestarteter rechter nur X.
  Eine andersfarbige Füllung wird links neutralisiert, nicht direkt umgefärbt.
- Ursprünglicher Startzustand, Modus und Farbe stehen für die gesamte Geste fest. Die erste eindeutige Bewegung
  bindet die Achse; bei diagonalem Gleichstand bleibt zunächst nur die Startzelle.
- Zurückziehen verkürzt die Vorschau. 5→12→9 übernimmt nur 5–9 als eine Aktion.
  Trifft der Zeiger die Startzelle tatsächlich wieder, zeigt die Vorschau nur diese
  Zelle und die nächste eindeutige Bewegung darf eine neue Achse wählen, auch mehrfach
  ohne Loslassen. Ohne diesen Treffer bleibt die Achse beim Überqueren gebunden;
  eine bloße Projektion oder ein Eingabesprung reicht nicht.
- Ein kleiner Live-Zähler zeigt während linker/rechter Zellgesten die gesamte
  geometrische Länge inklusive beider Endfelder: 5→12 zeigt 8, zurück auf 9 zeigt 5.
  Vorbelegte oder übersprungene Zellen zählen mit. Ab Länge 2 folgt die dunkle Zahl
  mit heller Kontur dem tatsächlichen Zeiger, auch über der Seitenleiste; bei Länge 1,
  Abbruch oder Drop verschwindet sie. Ihre UI-skalierte Größe bleibt beim Rasterzoom
  gleich. Kein Kasten; am Fensterrand bleibt die vollständige Zahl innen sichtbar.
- Begonnene Striche folgen der Maus entlang ihrer Achse bis zum gültigen Rasterrand,
  auch über anderen Bedienelementen. Spalte 5→rechts hinaus bei 30 Spalten ergibt
  26 Felder bis Spalte 30. Loslassen wertet seine eigene letzte Position aus und
  übernimmt genau einen Strich; ein darunterliegender Button wird dabei nicht geklickt.
  Der sichtbare Zeiger bleibt frei. Bei erhaltenem Spielfokus ist auch Loslassen
  außerhalb der Fensterclientfläche möglich. Technischer Windows-Nachweis und noch
  offene Eigentümerprobe sind getrennt in der [Prüfzuordnung](../docs/CELL_DRAG_VERIFICATION.md)
  und PR #145 gebunden; diese Anleitung ist keine persönliche Abnahme.
  Esc, Fokusverlust, verlorene Tastenzuordnung oder Albumwechsel verwerfen den Strich
  vollständig. Rückkehr startet keine Geste ohne frischen Tastendruck. Kein Auto-Scrollen.
- Radierer links neutralisiert alle Markierungen; rechts gilt die Kreuzregel.
  Rückgängig/Wiederholen stellt ganze Striche mit exakten Vorzuständen wieder her.
- Bei Farbrätseln: Farbe über die unbeschrifteten Farbfelder in den Originalfarben wählen.
  Eckmarkierungen zeigen die Auswahl; Status und Tooltip nennen „Farbe 1“ bis „Farbe 4“.
  Farbwahl aktiviert Füllen, auch nach Radierer. Die frühere A–D-Beschriftung
  der Mauspalette entfällt; Lösungshinweise zeigen weiterhin nur die Zahl in ihrer Farbe.
  Gleiche Farbblöcke brauchen Abstand; verschiedene dürfen angrenzen.
- Etwas größere Füllflächen bleiben durch Zwischenräume und Rasterlinien getrennt.
  Im Raster sind Cursorzeile und -spalte dezent hinterlegt. Über Zeilenhinweisen
  bleibt nur die Zeile, über Spaltenhinweisen nur die Spalte markiert, auch bei
  vollständigen Folgen und geöffnetem Vollhinweis. Während Hinweisdrag bleibt
  ausschließlich seine Quellenlinie markiert. Angeschnittene
  X und Preview-X werden am sichtbaren Rasterrand geometrisch abgeschnitten.

## Navigieren und Hinweise lesen

- Offene Hinweise bleiben kräftig. Eindeutig vollständig gesetzte Zahlen werden
  deutlich blasser; sind ihre Blöcke zusätzlich an beiden Enden abgegrenzt, bleibt
  die Zahl gleich blass und erhält ein handschriftliches X über die ganze Zahl.
  X, echter Linienrand und direkt andere Füllfarbe begrenzen; unbekannte Nachbarn
  nicht. Beide Achsen und der vollständige Tooltip zeigen dieselben Zustände.
  „Erfüllte Hinweise markieren“ gilt für die Sitzung: Aus zeigt normale Zahlen,
  An den aktuellen Stand. Nur eigene sichtbare Zellen einschließlich Vorschau und
  die vollständige Linie zählen, kein Lösungsvergleich. `…` und `–` bleiben unmarkiert.
- Mausrad und −/+ zoomen monoton bis zur vollständigen Raster-Fitgrenze samt Rahmen.
  Die gewünschte gültige Arbeitsstufe bleibt separat vom berechneten Fitwert erhalten.
  Minus/Plus und Mausrad ändern die benannte Rätselansicht nicht.
- Raster-MMB und frühere Handrouten verschieben oder bearbeiten nichts.
- Die eigene Miniatur bleibt passiv: nur eigene Füllungen in Originalfarben,
  einschließlich Fehlern und statischer Strichvorschau. X und unbekannt erscheinen
  gleich neutral, auch in vorhandenen ungelösten Albumminiaturen.
- Während Zellgesten sind Zoom und Navigation gesperrt. Navigation ändert keine Zellen
  oder Undo-Historie. Pro Blatt bleiben Bearbeitung/History und Ansicht beim
  Blattwechsel und regulären App-Neustart erhalten.
- Am Raster stehen ausschließlich die Lösungshinweise, ohne laufende Zeilen-/
  Spaltennummern oder A–D-Zusätze. „–“ ist eine leere Linie. Alle Zeilen nutzen dieselben
  waagerechten Slots, alle Spalten dieselben senkrechten Slots; das rasternächste Ende
  liegt an derselben Kante. Bei Überlauf bleibt ein zusammenhängender Ausschnitt
  vollständiger Zahlen sichtbar. `…` links/oben markiert einen verborgenen Anfang,
  rechts/unten ein verborgenes Ende; mittlere Ausschnitte dürfen beide Marker haben.
  Zahlen werden nie geteilt; bestätigte Lesepositionen liegen in ganzen Slots.
- Die linke Taste im oberen Hinweisbereich verschiebt nur die
  beim Start angefasste Spaltenfolge vertikal. Dieselbe Geste im linken Hinweisbereich
  verschiebt nur die angefasste Zeilenfolge horizontal. Während des Ziehens folgt
  sie der Maus flüssig zwischen den Slots. `…` zeigt dabei auf der jeweiligen Seite
  die aktuell verborgenen Zahlen an; erst beim Loslassen rastet die Folge anhand
  der zuvor sichtbaren Zahlen auf die geometrisch nächste gültige Slotlage ein.
  Ein Markerwechsel verschiebt Zahlen dabei nicht zusätzlich. Nachbarlinien
  behalten ihre eigene Position. Ziel, Linie und Achse bleiben auch beim Überqueren anderer Bereiche
  eingefroren. Raster, Miniatur, Zellen und Undo/Redo ändern sich nicht. `Esc` oder
  Fokusverlust oder ein regulärer Übergang verwirft den temporären Versatz.
  MMB navigiert keine Hinweise. Ein Hinweisdrag wird auch über Raster oder Buttons
  nicht zur Zell- oder Buttonaktion. Verlorene Freigabe oder ein Tastenakkord
  verwirft den Versatz; nach dem Loslassen beginnt erst ein frischer Druck eine Geste.
  Weiteres Ziehen in derselben Richtung führt bis zum äußeren Anfang; zurück
  geht es durchgehend in Gegenrichtung. Am Anschlag bleibt die Folge stehen.
  Dort darf ein Platz frei bleiben, damit die Zahlen beim Einrasten nicht
  zurückspringen. Alle Zahlen bleiben über die Folge der Lesepositionen erreichbar.
- Freie Breite und Höhe zeigen nach dem Fit zusätzliche vollständige Zeilen- und
  Spaltenhinweise, ohne kleinere Zellen dafür zu erzwingen. Passende Folgen haben
  keine Auslassungsmarker und lassen sich nicht in Leerraum verschieben.
- Darüberfahren einer gekürzten Folge zeigt weiterhin den vollständigen farbigen
  Hinweis mit Umbruch direkt über dem Arbeitsbild: unverändert kleine Fraunces-Überschrift,
  gut lesbare Delight-Zahlen und ruhiges Papier mit gezeichnetem Rahmen.
  Die Overlaylesegröße folgt der UI-Skalierung unabhängig vom Rasterzoom. Das ist ein Zusatzweg; Anfang,
  Mitte und Ende bleiben auch durch Hinweis-Panning erreichbar. Eine separate
  Hinweisansicht gibt es nicht.
- UI 100/125 % vergrößert die Oberfläche. Delight-Coffee-Hinweisziffern und ihre
  gemeinsamen Zeilen-/Spaltenplätze passen sich dem tatsächlichen Zellmaß an:
  kompakt bei kleinem Zoom, größer beim Hineinzoomen, innerhalb der Fitgrenze.
  Geänderte Slotkapazitäten erhalten je konkrete Folge die semantische Leseposition:
  äußerer Anfang und rasterseitiges Ende bleiben am gewählten Rand verankert,
  mittlere Ausschnitte behalten den gelesenen Tokenbereich mit größtmöglicher
  Überdeckung. Das gilt auch bei Arbeitszoom und Resize; alle Zustände bleiben
  in ganzen Slots eingerastet. Vorübergehende Vollanzeige bewahrt die Anker auch
  beim Speichern und Neustart; beim Verengen kehrt derselbe Lesebereich zurück.
  Die UI-Skalierung, Rätselansicht und H1 stehen auf der Informationsseite.
  Ihr Öffnen erhält die individuellen Hinweislesepositionen; ein manueller
  Hinweisrücksetzbefehl wird nicht angeboten.
  `?` führt direkt zur scrollbar erreichbaren Bedienhilfe rechts; das Menü
  öffnet die Einstellungen links. Der Pfeil im Arbeitskopf führt zum Katalog.
  Auch bei 1280×720/UI 125 % bleiben Werkzeuge,
  eigene Miniatur und Hinweiszugriff auf der Arbeitsseite. Der Rückpfeil führt
  auf den Informationsseiten zum jeweiligen erhaltenen Ursprung zurück.

Für den Abschluss genügen alle richtigen Füllungen ohne Zusatzfüllungen.
Hintergrund muss nicht vollständig ausgekreuzt sein. Name und Ergebnisbild erscheinen
erst nach bestätigtem Abschluss. Die registrierte Definition bindet Motivname und
freigegebenes Ergebnisbild; vorher bleibt nur die eigene Füllminiatur sichtbar.
Beim neuen Abschluss treten Raster, Hinweise und Werkzeuge zurück. Deine Füllungen bewegen sich zur Papiermitte, werden zu lückenlosen Farbflächen und gehen in das fertige Bild über. Die Folge dauert etwa 2,15 Sekunden. Die Speicherung erfolgt unmittelbar beim letzten Zug; etwaige Speicherfehler bleiben sichtbar. Danach erscheinen Motivname und „Rätsel zurücksetzen“. Der Titel bleibt „Blatt NN · W × H“, der Buchreiter führt zur Sammlung.

Bereits gelöste Blätter öffnen direkt das fertige Bild. Fenster- oder UI-Größenänderung und Fokusverlust beenden eine laufende Enthüllung; sie wird danach nicht wiederholt. Bestätigtes Zurücksetzen unter dem Bild öffnet dasselbe Blatt leer. Abbrechen erhält den Stand. Der Reset einer Katalogkarte bleibt im Katalog. Nach erneutem Lösen läuft die Enthüllung wieder.

Die früheren 100×100-Blätter werden nicht mehr angeboten.

## Entwicklung und technische Prüfung

Regulärer Entwicklerstart im Repository-Root mit Godot Standard 4.7.2-stable:

```sh
godot --headless --path game --import
godot --path game
```

Direkter Entwicklerstart verwendet das normale Profil. Isolierte technische Prüfungen
verwenden den Harness mit temporärem synthetischem Katalog und separater
Python-/Pillow-Umgebung nach der [Werkzeuganleitung](../tools/puzzle_production/README.md).
Die benötigte Gruppe ausdrücklich wählen, zum Beispiel für die kurze Historyroute:

```powershell
$gameCache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $gameCache --output-dir artifacts/p1-history --groups history
```

Arbeits-/Cachepfade bei vorgegebener Arbeitswurzel darunter anlegen. Der Harness
prüft offizielle Archive/Hashes und isoliert Projekte und Benutzerprofile.
Linux-Renderprüfung benötigt Xvfb/Mesa. Gruppen und aktueller Umfang stehen im
[nativen Vertrag](../docs/CI_C_NATIVE_GROUPS.md). Ohne `--groups` läuft lokal die
vollständige Vereinigung; die alten Erweiterungsflags bleiben kompatibel, sind
aber kein Anlass für routinemäßige Vollprüfungen.

`history` prüft 17 Kommandos, vier Transaktionen und zwei echte Spielprozesse samt
unabhängigem Orakel. Die alte 500er-Route wird nicht als Stressdefault fortgeführt.
`adapters` verwendet vier feste synthetische Muster, keine Bestands-Rezertifizierung.
`graphics` prüft die aktuellen ausgewählten Pixel-/Animations-/Atlasverträge.
`export` prüft Windows-/PCK-Ausgabe und auf Windows auch tatsächliche EXE-Starts.
Nicht ausgeführte Bereiche sind kein erfolgreicher Nachweis.

Die [Package-CI](../docs/CI_WORKFLOW_V2.md) liefert bei Entwicklungsänderungen den regulären Windows-
Download und startet nur begründet gewählte Zusatzmodule. Reine Dokumente und
reine Rätselproduktion bleiben ohne Player-Build, auch im Main-Nachlauf. Der Kern-Windowsbau ist kein voller Product-Harnesslauf
und keine erneute Rätselprüfung. Das Spielerpaket enthält Startdateien, Anleitung
und Lizenzen; technische Reports, Logs, Bilder und Studienpakete gehören nicht hinein.
Technische Originale werden im Lauf geprüft und entfernt; Upload nur mit aktuellem
Zweck und Ablauf. Zehn Minuten sind ein weiches Ziel, keine globale Höchstlaufzeit.
Historische Hersteller-/A/B-Programme und Liefergalerien werden nicht reproduziert.
Keine automatisierte Prüfung ersetzt eine persönliche Maus-/Komfortprobe.

Aktuelle Verträge und Pflichtquellen: [Projektprofil](../docs/PROJECT_PROFILE.md).
Historische Studien, alte Abnahmen und Quellenbindungen:
[Bestandsinventar](../docs/DEVELOPMENT_ARCHIVE.md). Die ursprüngliche Anleitung ist
[am Stand vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/prototypes/p1/README.md) erreichbar.
Historische Prüferdokumente mit Motivspoiler: [F01](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/game/F01_PROOF.md), [F02/F03](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/game/F02_PROOF.md).
