# HZ-A · Schrift und Textlayout

Auftrag: [#284](https://github.com/venomenon328/picross/issues/284), ausschließlich
HZ-A-A01–A05 und HZ-A-T01. Arbeitsbranch `feat/284-ui-schrift`, Ziel `main`,
Ausgangsbasis `862d2e5a939af81f0462536aa930d86eb7fffffb`.
Dokumentationsintegration `a09d5dede15b8abc1540a5c65cc4729c666220b4` ist enthalten.
Die aktuelle Head-/Base-/Checkout-/Run-/Versuchsbindung und das technische
Ergebnis werden im eigenen Draft-PR und im Issue geführt. Dieses Dokument allein
behauptet keinen erfolgreichen CI-Lauf.

## Umsetzung

Die Eigentümerentscheidung HZ-A-FONT02 ersetzt Bakso als geplante Standardschrift
durch das unveränderte Tidy Hand aus dem bereitgestellten ZIP. Quelle, Autor,
Nutzungshinweis und beide Hashes stehen in
[NOTICE.txt](../game/art/drawing/tidy-hand/NOTICE.txt). `z2_resources.verify()`
prüft TTF und Hinweis; Windows-/Web-Spieler und PCK liefern ihn mit.
Die ursprünglichen Bakso-, Fraunces-, Plex- und Delight-Dateien bleiben erhalten.

`ui_text.gd` hält eine private Tidy-Instanz mit ausschließlich lokalem Plex-Fallback.
Tidy liefert insbesondere ß, Umlaute, Mittelpunkt und die echte U+2026-Ellipse;
Plex liefert fehlende Multiplikations-/Anführungs-/Strich-/Pfeilzeichen.
Die normalen Controls, native Menüs und direkte Textzeichnung verwenden diese
Ressource. Bestehende Überschriften einschließlich nativer Dialogtitel und
Vollhinweis-Überschrift behalten ihre Ressourcen. Bakso-Motivtitel behalten ihren
bisherigen Dreipunkt-Auslassungsweg.

Shaping, Fallback-RIDs, sichtbare Glyphenhüllen, Zeilenhöhen und Label-Innenränder
bestimmen die Textbudgets. Die gemeinsame Kartenbreite berücksichtigt alle
zulässigen Größenwerte 1–50 und vollständige Schwierigkeits-/Statusangaben.
Bildraum, Resetrechteck, Zwei-Zeilen-Motivtitel und passive Klickwege bleiben.
„Sortieren nach“ kann in schmalen Fenstern innerhalb der Kopfzeile umbrechen.
Lange Kategorien bleiben im nativen vertikalen Menü auswählbar; vollständig
umgebrochene Tooltips zeigen auch 128 Zeichen lange Namen. Native Dialogtexte
brechen innerhalb einer begrenzten Breite um.

Keine neuen Rahmen, Dropdown-Grafiken oder Icons: HZ-B bleibt separat.
Keine Änderung von Definitionen, Katalogwerten, IDs, Saves, Sortier-/Präferenz-
semantik, Spoilern, Reset-/Recoveryzielen oder HC/HF/HN-Geometrie.

## Ausführbare Nachweise

- `hz_cases.gd`: originale Bytes, lokale Glyphen-RIDs, positives und negatives
  Ellipsenpixelorakel, native automatische Auslassung bei allen verwendeten
  Größen und skalierter Zeichenvorrat; Bestandteil der Core-Regressionssuite.
- `hz_native.gd` im bestehenden KAT-2-Modus `kk`: drei Pflichtkonfigurationen,
  vollständige Kartenmetadaten, 256 synthetische Kategorien mit langen Namen,
  echtes Scrollen/Anklicken, Tooltips, Hilfe, native Dialoge und unveränderte Saves.
  15 zusätzliche Originalbilder stehen im verpflichtenden nativen Inventar.
- `HZ-A-W01`: echte Chromium-Menü-/Hilfebedienung und gemessene Metadaten in
  denselben drei Konfigurationen; sechs zusätzliche Pflichtbilder. Alle bisherigen
  Browserfälle bleiben erhalten, insgesamt 31 Szenarien in fünf Gruppen.
- `hz_windows_probe.py --head <SHA> --run <RUN> --engine <EXE> --cache-dir <CACHE>
  --output-dir <NEUER-ORDNER>`: verlangt sauberen gelieferten Head, prüft die
  konkreten CI-Artefaktdigests und sämtlichen nativen Pflichtdateien, startet die
  tatsächliche Windows-EXE ohne Testargumente und erfasst ausschließlich deren
  eigenes HWND. `hz_pack.gd` prüft Original-UI/-Fonts des heruntergeladenen PCK
  mit sechs externen synthetischen Definitionen. Anschließend laufen sämtliche
  KAT-2-Modi nativ mit isolierten Projekten und Profilen.
- `test_z2_delivery.py`: positive Ressourcenprüfung und negative Gegenproben
  für veränderte TTF beziehungsweise fehlenden Nutzungshinweis.

Keine echten Saves oder wachsenden Katalogreplays. Der reguläre EXE-Start
beobachtet nur den Startkatalog; synthetische Bedienprüfungen sind davon getrennt.
Die Pflicht-CI folgt dem vollständigen Diff: gemeinsame UI/Ressourcen und
Prüfharness wählen alle sieben nativen und alle fünf Chromium-Gruppen.
`docs`, `ci-required` und weitere tatsächlich ausgewählte Fach-/Toolchainjobs
müssen erfolgreich sein; übersprungene Pflicht ist kein Erfolg.

## Übergabe und offene Gates

Vollständiger Diffcheck und davon getrenntes Selbstreview werden am gelieferten
Head im Draft-PR dokumentiert. Originalbelege bleiben an ihren tatsächlichen
Checkout und Producer-Versuch gebunden. Ein neuer Head braucht eine neue
technische Bindung; ältere Entwicklungsläufe ersetzen sie nicht.

HZ-A-R01 bleibt ein **separater qualifizierter Review**; HZ-A-M01 bleibt die
**persönliche Eigentümerabnahme**. Kein Merge, Deployment oder Issue-Abschluss.
