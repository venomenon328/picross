# KE · Implementierung und technische Prüfbarkeit

Stand: 17.10.2026 · Paket [#233](https://github.com/venomenon328/picross/issues/233),
Draft-[PR #234](https://github.com/venomenon328/picross/pull/234) gegen `main`.
Verbindliches Soll: [Katalogdarstellung](CATALOG_PRESENTATION.md).

## Quellen und Befugnis

Implementierungsbasis `aa5cbeb3812f5fe1f7f5087beed38069240080e8`, vorbereiteter
Branchhead `f629103bc6516ee94bc7bd4f06332427c5b55e11`. Issue/PR einschließlich
Kommentare und Remote-Main wurden vor Umsetzung erneut gelesen/abgeglichen.
Die frühere Vorbereitung ohne Windows-Zugriff ist historisch: diese Umsetzung
arbeitet unter Windows mit dem gebundenen Godot 4.7.2 und NVIDIA RTX 3070.
Der aktuelle Nutzerauftrag autorisiert Implementierung, Commit, Push und
Fortführung des Draft-PR; keinen Merge. Vorhandene fremde lokale Designarchive
gehören nicht zur Änderung.

## Implementierung und feste Nachweise

### KE-N1 nach Review 5558007171

Startstand `d2c66baa60355d2e2a31f77b2952de7084ac885e`, Basis weiterhin
`aa5cbeb3812f5fe1f7f5087beed38069240080e8`. Die Startprüfung umfasst aktuellen
Issue-/PR-/Reviewzugriff, passende Branchidentität, GitHub-Schreib-/Artefaktzugriff,
gebundene Editor-/Templatehashes und einen frischen isolierten nativen Windowsstart
mit Godot 4.7.2, OpenGL und NVIDIA RTX 3070. Die Eigentümerbeauftragung hebt die
frühere reine Vorbereitung für genau KE-N1 auf; Draft und Mergegrenze bleiben.

| Nacharbeit | Implementierung und Regressionsnachweis |
| --- | --- |
| N1-01 / KE-R1-B01 | Beide Recoverypfade erkennen exakt kanonische v2/v3-Snapshots, prüfen den gesamten hergeleiteten v3-Zielcheckout vor Mutation und erlauben nur ihre eigene exakte Zwischenprojektion zur Wiederaufnahme. Feste kleine Altformatinputs prüfen frühe/fortgeschrittene Registrierung, echte Definition-/Notice-/Paketänderung, beide Wiederaufnahmen nach v3-Schreiben und mutationsfreie Ablehnung fremder/nichtkanonischer/gemischter Bytes. Vorhandene v3-Tests bleiben aktiv. |
| N1-02 | Auf das tatsächliche Anzeigemaß mit Lanczos verkleinerte Texturen im gemeinsamen spoilergebundenen Revealpfad; anschließende lineare Anzeige in Katalog und Abschluss. Lokale Polygonkantenglättung für Modus-/Begonnen-Stifte. `ke_graphics.gd` vergleicht native Originalpixel gegen die bisherigen Filter und eingefrorene Stiftprimitive aus dem Starthead: PNG/SVG, alle vier Ansichten, Katalog, laufende EA-Phase, Endbild und Wiederöffnung; Geometrie, Originalhashes, Savebytes und Freigabe der Bildreferenzen werden geprüft. |
| N1-03 | Exakte Zahl-Namen-Skala 1 Sehr leicht bis 5 Sehr schwer, farbige Ziffer und dunkler Name; neutral fehlend ohne Null. Beide Bewertungsarten gleich dargestellt; Worterklärung, Unsicherheit, Spannweite und R4 im Tooltip. Kern-/native Tests prüfen Zuordnung, Textbreiten, längsten Status, Accessibility und UI-Rundlauf. |
| N1-04 / KE-R1-A01 | Finaler sauberer Windows-Quelllauf plus tatsächlich heruntergeladener CI-Spieler mit EXE-/PCK-Prüfung. Der PR liefert einen zugänglichen, revisionsgebundenen Download mit Manifest/Hashes, Logs, nativen Originalausschnitten und JSON-Berichten. Lokale Pfade allein gelten nicht als zugänglicher Nachweis. |
| N1-05 | Normative Quellen, Recoveryanleitung, EA-Bildpfad und dieser Bericht sind konsistent nachgeführt. Finaler Voll-Diff, Selbstreview, CI-/Windowsbindung und Einzelantworten stehen im PR. |

Die früheren lokalen d2c66ba-Belege bleiben historische Angaben; die neue Lieferung
beansprucht keine nachträgliche unabhängige Sichtung dieses alten Archivs. Neue
technische Belege schließen weder KE-R01-Nachreview noch KE-R1-A02/KE-M01 selbst.

Der Eigentümer hat die während der KE-N1-Prüfung gefundene Firefox-Startkorrektur
zusätzlich freigegeben: Beim Reload konnte die sofortige Lockanfrage die noch
belegte Sperre des vorherigen Dokuments als Zweittab ausgeben. Die begrenzt
wartende exklusive Anfrage erhält den Schutz vor parallelem Speicherzugriff;
abgebrochene Anfragen starten nicht nachträglich. Der
[Webvertrag](WEB_HOSTING.md) und die echten Browserproben bilden diese Ergänzung
ab. Fehlversuche des vorangehenden Stands bleiben im PR-Nachweis sichtbar.

| Kriterien | Änderung und technische Probe |
| --- | --- |
| A01/A06 | 228–240 logische Pixel breite Karten mit festen Titel-/Kategorie-/Bild-/Etikett-/Fußbereichen in `catalog_card.gd`; `kat2_probe.gd` prüft alle drei gemeinsamen Grafikfälle, zusätzlich 1920×1080/UI125, tatsächliche Textbreiten, lange Texte, Filter/Seiten, UI-Rundlauf und gleiche Geometrie. |
| A02 | Eigene deterministische Zeichnungen in `catalog_ink.gd`: warmes Papier, ein/drei Stifte, offener Kreis, Ockerstift und grüner Haken. Keine neuen Fremdassets oder Fonts. Native Screenshots für visuelle Prüfung. |
| A03/A08 | `catalog_difficulty.py`, `catalog_difficulty.gd`, `test_catalog_difficulty.py` und `ke_cases.gd`: L1–L5, Schätzung, fehlend, R4, falsche Typen/Methoden/Spannweiten, keine Freitextprojektion, exakte v2/v3-Felder und kanonische Bytes. Bestehende synthetische Adapter-/Registrierungs-/Update-/Recoverytests bleiben aktiv. |
| A04/A05 | Katalogwort „Fertig“, gemeinsame statische Fragezeichnung; native KE-/KK-Routen für Neu, falsche eigene Füllung, X-only, Undo/Redo-only, Abschluss und Reset. Keine Änderung am Miniaturrenderer, Save oder Abschlussmodell. |
| A07 | Gezielte native Modus-/Schwierigkeitspopups einschließlich UI-Wechsel und Klickweitergabe; bestehende KK-Fehler-/Recovery-/Reset- und KAT-2-Prozessneustartfälle. Spoilerfreie zugängliche Kartenbeschriftung. |
| Windows/Web | `ke_windows_probe.py` bindet sauberen Quellhead, offizielle Enginehashes, native KAT-2/KB/KK/KE-Routen und optional den tatsächlichen CI-EXE/PCK. WEB-1 prüft Chromium und Firefox mit isolierter IndexedDB einschließlich passiver Etikettklicks. |

Der Python-Writer erzeugt v3. Der Godot-Loader akzeptiert weiterhin exaktes v2;
der detaillierte Vertrag steht in [CATEGORIES](CATEGORIES.md) und
[ZA1_ADAPTER](ZA1_ADAPTER.md). Nur die Runtimeprojektion ändert sich;
Produktionsregistry, Definitionen, Assets, IDs, Slots, Revisionen und gebundene
Freigaben bleiben bytegleich. Keine Neuzertifizierung realer Rätsel.

## Reproduktion und Ergebnisbindung

Schneller Pfad gemäß Projektprofil: Werkzeugtests und `tools/check_docs.py`.
Fachtests verwenden die vorhandene eigene Pillow-12.3.0-Umgebung.
Die Änderung am Harness wählt nach [CI-Policy](CI_POLICY.md) sämtliche aktuellen
Bereiche aus: docs, production, product einschließlich integration/pilots/visual/
perf_b, preflight und web; abschließend ci-required. Keine historische
PERF-A-/A/B-Reproduktion. Übersprungene Pflichtjobs zählen nicht als Erfolg.

Native Reproduktion aus einem sauberen Checkout des geprüften Heads:

```powershell
python tools/ke_windows_probe.py --head <vollständiger-Commit> --run <CI-Run-ID> --engine <gebundene-console.exe> --cache-dir <P1-Archivcache> --output-dir <neuer-Ausgabeordner>
```

Der Runner isoliert Projekt und Benutzerverzeichnisse. `windows-binding.json`
enthält Quellidentität, Enginehash, echte Phasen, Geräteangabe, Einzelprüfungen,
Artefakthashes und die separate CI-Spielerbindung. Bildausschnitte bleiben native
Pixel ohne Skalierung. KE-/KK-Layouts und Metadatenpopups sind technische
Prüfansichten, keine persönliche Gestaltungsabnahme.

Finalen Head, Basis, CI-Test-Merge, Run, tatsächliche Jobergebnisse und
Windows-Artefaktbindung führt der PR in seinem Abschlussnachweis. Damit muss
kein Commit seinen eigenen Hash enthalten. Ein späterer Diff verlangt erneute
Zuordnung zum dann finalen Head.

## Getrennte Gates

KE-T01 wird erst mit erfolgreicher aktueller CI und nativer Windows-Bindung
geschlossen. Eigener vollständiger Diff-/Selbstreview ist Teil der Lieferung,
aber kein unabhängiger Review. **KE-R01 bleibt für einen separaten Prüfer offen.**
**KE-M01 bleibt für die Eigentümerprobe am benannten Head offen.** Beide sind
vor Merge erforderlich. Die historische KK-Ausnahme gilt nicht für KE.
