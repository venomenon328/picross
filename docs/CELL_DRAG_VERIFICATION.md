# ZR · Umsetzung und Prüfzuordnung

Vertrag: [CELL_DRAG](CELL_DRAG.md), Paket [#143](https://github.com/venomenon328/picross/issues/143),
gemeinsamer [Draft-PR #145](https://github.com/venomenon328/picross/pull/145).
Diese Zuordnung beschreibt die Prüfwege; konkrete Ergebnisse sind im PR an Head,
Basis, tatsächlichen Checkout, Run und Exporthashes gebunden. Kein Merge oder Release.

## Implementierung

`grid_view.gd` hält strenge Start-/Hovertreffer und unbegrenzte Rasterkoordinaten
getrennt. `gesture.gd` wählt die Achse vor dem Clamping; nur der ausdrücklich echte
Starttreffer entriegelt. `board.gd::update_gesture_endpoint()` wird von Motion und
Release benutzt. Die Zeichenschicht erfasst erst danach Vorschau, Änderungsmenge und
Richtung; `finish_gesture()` übernimmt atomar. Fehlende Ursprungstaste in einer
Motion verwirft die Geste. Die bestehende Windows-Ereigniszustellung der gebundenen
Engine wird verwendet; kein neuer nativer Runtimebaustein, Mausmoduswechsel oder Warp.

`gesture_counter.gd` zeichnet in einer eigenen CanvasLayer über Board und Sidebar.
Die aktive Fontressource bleibt gemeinsam. 24×UI Schriftgrad, dünne helle Kontur,
12×UI Abstand und 4×UI innerer Rand sind die gewählte Ausgangsgestaltung. Gemessene
native Glyphenlager plus Kontur/AA bestimmen die vollständige Anzeigehülle. Nur
transiente Cursor-/Darstellungsdaten; kein neues Savefeld oder Historyeintrag.

## Automatisierte Zuordnung

| Kriterien | Aktuelle Prüfung |
| --- | --- |
| ZR-A01/A03/A05 | `zr_cases.gd`: 30×30 und beide Rechtecke, vier Richtungen, Ziele X/1/8, Sprünge, elastischer Rückzug, asymmetrisches Clamping, Gleichstand, echte/projizierte Starttreffer, Vorbelegungsschutz, geometrische 26, atomare History und exaktes Undo/Redo. G1-/GP48-Regressionen bleiben. |
| ZR-A02 | `capture.gd` im bestehenden Axis-Pfad: drei gemeinsame Client-/UI-Konfigurationen, kleiner/großer angebotener Zoom, Subzellbewegung, Sidebar, alle Ränder/Ecken einschließlich Außenposition. Native Glyphenpixel, transparente Ecken/Fläche und vollständige Konturhülle gegen separat gerenderten Untergrund; drei Vollkontexte und sechs unveränderte Randdetails. Diese GPU-Bilder sind keine OS-Zustellungsprüfung. |
| ZR-A04/A07 | `zr_cases.gd`: tatsächlicher Viewport-Ereignisweg, beide Tasten/vier Richtungen, Mouse-Up ohne letztes Motion, finale Miniatur/Änderungen/Effektrichtung An/Aus, Release über Undo ohne Buttonaktion, verlorene Maske ohne Nachholen, frisches Down, valide Schema-1-History ohne transiente Felder. Bestehende ZS2-, H1-, Save-/Recovery-, Prozess-/500-Aktionen- und PCK-Prüfungen nach CI-Policy. |
| ZR-A06 | Separater technischer nativer Windows-Eingabenachweis am gebundenen Export; **offen**, nicht aus SubViewport, Headless-Start, Preflight oder Linux-CI abgeleitet. |

Einige frühere synthetische Motionhelfer lieferten bei gehaltener Taste eine leere
Buttonmaske. Ihre Masken bilden jetzt den tatsächlich gehaltenen Ursprung ab;
bewusst verlorene Masken werden separat auf vollständigen Abbruch geprüft.
Historische Atlanten, Fontbytes, Rendererberichte und Abnahmen bleiben unverändert.

Aktuelle Pflichtauswahl ausschließlich nach [CI-Policy](CI_POLICY.md). Nicht gewählte
Bereiche sind nicht ausgeführt. Erfolgreiche Dokumenttests allein prüfen kein Spiel.

## Technische Windows-Probe ZR-A06 vor Merge

Den im PR gebundenen Product-Export herunterladen, Hashes gegen `product-report.json`
prüfen und EXE/PCK zusammen entpacken. Ausschließlich ein temporäres Profil verwenden,
beispielsweise APPDATA/LOCALAPPDATA nur für den gestarteten Kindprozess setzen.
Keinen echten Benutzerstand kopieren oder globale Einstellungen ändern.

Für links und rechts jeweils getrennt protokollieren:

1. Im Raster beginnen, schnell über Sidebar/Rasterrand und Clientrand ziehen. Bei
   erhaltenem Spielfokus bleibt der Cursor frei/sichtbar; Randzahl und Vorschau
   beschreiben den vollständigen Abschnitt bis zur Rastergrenze.
2. Außerhalb loslassen. Genau ein Commit, vollständiges Undo/Redo, keine Buttonaktion;
   zurückkehren ohne Phantomstart. Native Zustellung des Ups tatsächlich beobachten.
3. Hinaus und mit noch gehaltener Taste zurückkehren; elastischen Rückzug und echten
   Starttreffer mit Achsenneuwahl prüfen, anschließend übernehmen.
4. Separat Fokus verlieren (etwa Alt-Tab), außen loslassen und zurückkehren. Kein
   Commit/Nachholen, keine Vorschau/Zahl oder hängende Erfassung; frisches Down arbeitet.

Quellhead, Basis/Checkout, Run/Artefakt, EXE-/PCK-Hashes, Windows-Version, Renderer,
Bildschirm-/Clientfläche, Windows- und UI-Skalierung sowie jedes Einzelergebnis
festhalten. Sicherer Abbruch bei verlorener Eingabe ist kein Ersatz für Schritt 2.
Eine fehlende reale Zustellungsprobe bleibt ausdrücklich offen.

## Eigentümerprobe ZR-M01 vor Merge

Der Eigentümer prüft am selben gebundenen Windows-Export schnelle linke/rechte
Randzüge, Außenloslassen, sichtbaren Randzähler und Lesbarkeit bei UI100/125 sowie
kleinem/großem angebotenen Rasterzoom. Ergebnis und tatsächliche Metadaten wie oben
festhalten. Technische Bilder ersetzen weder reale Mausbedienung noch Gestaltung.
ZR-M01 und das unabhängige Review des Implementierungsheads sind **offen**.
Der getrennte Selbstreview ersetzt diese Gates nicht; [#24](https://github.com/venomenon328/picross/issues/24)
bleibt die separate längere Spielerprobung.
