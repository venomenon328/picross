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
