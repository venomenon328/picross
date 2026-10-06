# ZV-50 · Zoom-Arbeitsfläche: technische Lieferung

Stand: 06.10.2026 · [Issue #50](https://github.com/venomenon328/picross/issues/50).

## Vertrag und Implementierung

ZV-01 bis ZV-04 trennen die kompakte Standarddarstellung von der maximal nutzbaren
Rasterfläche. Im nicht kompakten Buchlayout bleiben alle bisherigen Geometrien bis
einschließlich 100 % Arbeitszoom unverändert. Erst oberhalb von 24 logischen
Einheiten wächst der Rasterviewport symmetrisch um seinen bisherigen Schwerpunkt
in die tatsächlich freie Papierfläche und wird anschließend an Titel-/Hinweis-,
Miniatur- und Werkzeuggrenzen begrenzt.

Das Board fordert dafür nur bei Zoom-/Arbeitsgröße-/Gesamtansicht-/Restorewechseln
ein Relayout an. Normales Raster-Panning verwendet weiterhin ausschließlich
`view_changed`; dadurch wird kein vollständiges Layout auf jede Pointerbewegung
gekoppelt. Beim Zoomen bleibt ein Mausanker in globalen Koordinaten soweit möglich
unter demselben Rasterpunkt; die sichtbaren +/- Aktionen halten den bisherigen
Rasterfokus in der neuen Viewportmitte. Zellgröße, 20 Arbeitsstufen, Save-Schema,
Spielzustand und Hinweisreads bleiben unverändert.

Bei 1920×1080/UI 100 % bleibt 20×20 bei 100 % exakt 480×480. Die Stufen 26, 28,
30, 32, 34 und 36 sind vollständig sichtbar; 40 ist der erste gezielt geprüfte
Überlauffall und wird durch die echte vertikale Papier-/Werkzeuggrenze begrenzt.
Kleinere Flächen beziehungsweise UI 125 % dürfen früher überlaufen. F-02 behält
bei 100 % seine historische 720×720-Fläche und gewinnt beim ersten Zoomschritt
zusätzlichen Raum; F-03 behält seine bestehende Großraster-Mindestfläche.

## Automatisierte Nachweise

| Kennung | Nachweis |
| --- | --- |
| ZV-A01 | `tests/zv50_cases.gd`: 20×20 100 % unverändert; alle sechs Stufen 26..36 vollständig, letzte Zelle hittable. |
| ZV-A02 | Derselbe Test: 36 vollständig, 40 vertikal begrenzt; Rückzoom stellt die Vollansicht wieder her. |
| ZV-A03 | 1280×720, 1600×900, 1920×1080 und 2560×1440, UI 100/125 %: gewählte Zellgröße bleibt stabil und der Viewport bleibt vor Werkzeugen/im Fenster. |
| ZV-A04 | Pointeranker über die Viewportvergrößerung, F-02-Erweiterung, unveränderte F-03-Mindestfläche sowie alle bestehenden P1/G1/GP48/Save-/Recoveryregressionen. |
| ZV-A05 | `tests/zv50_capture.gd` plus `tools/zv50_review.py`: acht native Vorher-/Nachherpaare gegen `main@add7a7e6…`, darunter 100/133/150/167 %, 720p/UI125, F-02 und F-03; Hash- und Commitbindung im separaten Review-ZIP. |

Der Produktweg führt weiterhin den kompletten regulären Godot-Test, echten
Zwei-Prozess-Roundtrip, 500-Aktionen-Oracle, Negativkontrolle, native Renderstufen,
Z2-/GP48-/RP3-Vergleiche und Windows-Export aus. `docs`, `product`, `preflight`,
`puzzle-production`, `rp4-windows` und `rp5-repair` bleiben am Lieferhead
erforderlich. Tatsächliche Run-/Artefaktkennungen werden im PR dokumentiert.

## Abnahmegrenze

Die [gezielte Eigentümerprobe](ZV50_OWNER_TRIAL.md) bleibt als reproduzierbare
optionale Sicht-/Mausprobe erhalten. Der Eigentümer hat am 06.10.2026 nach der
Vorbereitung ausdrücklich „Setze es bitte selbst um und merge dann.“ beauftragt.
Für genau diesen Merge werden daher die zuvor geplante ZV50-M01-Eigentümerprobe und
eine unabhängige Zweitprüfung als Gate aufgehoben; beide werden **nicht** als
durchgeführt oder bestanden bezeichnet. Technische Checks, echter Diff-Selbstreview
und native Bildsichtung bleiben vor dem Merge erforderlich. Kein Release folgt daraus.
