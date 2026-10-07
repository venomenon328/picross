# ZS-1 · Prüfzuordnung nach E1–E3 und Liefergrenze

Stand: 07.10.2026 · bestehender Branch `feat/52-native-drawing-study`, Draft-PR #55

Basis `ec99954268f1ad959d9ea779dbbd9e28edf7d8fa`, Ausgangs-/R1-Head
`4ae4f5a20273808f99d257a3812da86d72307a5f`. Maßgeblich sind
[ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659),
[#52](https://github.com/venomenon328/picross/issues/52) und
[ZS-D01–D10](UI_DRAWING_STYLE.md). Neue Head-/Basis-/Test-Merge-/Run- und
Downloadbindungen stehen im PR und den maschinenlesbaren Artefaktberichten.
R1 bleibt historisch; neue Selbstprüfung ist keine unabhängige Zweitprüfung.

**N01–N06:** Die isolierte Studie enthält die gewählte Stiftfüllung, neues X,
räumlichen Strichaufbau und beide Original-TTFs. [ZS1-E2](https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344)
akzeptiert die vorhandenen Nutzungshinweise für die Kandidatenlieferung;
[Fontinput](ZS1_FONT_INPUT.md) dokumentiert diese Grundlage und die genauen Bytes.
Abschließende Eigentümerbestätigung und unabhängiges Review bleiben getrennte Gates.


**E3/N07:** Chalkboard Regular ist gewählt. Die Studienfassung reduziert nur die
gemeinsame horizontale Slotweite der Zeilenhinweise im Buchlayout von 30 auf
**26 logische Pixel bei UI 100 %**; UI 125 % ergibt 32,5 Pixel. Die vertikalen
Spaltenslots bleiben 18 beziehungsweise 22,5 Pixel. Die kombinierte reale Sichtprüfung
wurde vom Eigentümer ausdrücklich auf den gemergten `main`-Stand verschoben.

| Kriterium | Aktueller Nachweis / Grenze |
| --- | --- |
| A01 | 14 native Situationen je Plex-Baseline, Bakso/Stift und Chalkboard/Stift: 42 Bilder auf identischen eigenen F-01/F-02/F-03-Ständen. Bisherige reguläre Boardpixel gegen 14 echte Main-Archivbilder geprüft. Kandidaten zeigen unterschiedliche Hinweis-Pixel bei identischen Zellbildern (zwölf Fälle ohne überlagernden Tooltip). |
| A02 | Unveränderte echte Hinweise mit drei Zuständen auf beiden Achsen, C1, unabhängiger Hinweisdrag/Tooltip und beschriftete Ziffernprobe. Chalkboard ist gewählt; Ziffern bleiben nativ, Plex nur für `…`/`–`. N07 prüft 26×UI-Zeilenhinweisslots gegen Glyphenbreite/Marker/Überlauf; Spaltenslots bleiben 18×UI. |
| A03 | 1920×1080, 1280×720/UI125, 1600×900, 2560×1440; 12/24/36/72er-Zellen und F-01 bei 150 %. Gleiche Geometrie/Spielstände. Keine zusätzliche Studien-Rand-UI. |
| A04 | Echtzeitfolge mit statischer Vorschau, 20 parallelen Commits, zweiter Geste vor Effektende, Umwandlung und pixelgleichem Endzustand bei Aus. Zusätzlich sieben native 72-px-Zellausschnitte bei kontrollierten 0/21/49/70/98/119/140 ms: räumlicher Füllfortschritt, Zug eins vor Zug zwei. Bildprüfer lehnt aus diesen Bildern erzeugtes globales Fade und umgekehrte X-Reihenfolge ab. |
| A05 | Unveränderter Gesten-/Session-/Savekern; Normal-Sentinel vor/nach Studienlauf bytegleich. Echter Commit/Save im eigenen Root, Originaldaten/Proofs/Assets unverändert. Gesamter Produktweg mit Zwei-Prozess-, 500-Aktionen-, Recoveryregressionen sowie sechs aktuelle CI-Jobs erforderlich. |
| A06 | Schlankes Windows-ZIP, eigener nativer Vergleich und separates kleines Strichaufbau-ZIP. Identitätsbericht mit Head/Dirty/Basis/Test-Merge/Run, EXE-/Bildhashes, vorhandenem Fontmanifest/OFL sowie separaten Quellen-/Nutzungshinweisen und E2 für beide Studienfonts. Export-Smoke prüft die eingebetteten Kandidatenbytes gegen die Originalhashes. |

`zs1_tests.gd` prüft stabile und begrenzte X-Pfade sowie die echten GUI-Ereigniswege:
Parallelstart, Priorität, Rückzug, Abbruch, Schutz/No-op, Radieren ohne Rückkehr alter
Markierungen, Undo/Redo, Schalter ohne Save/Replay, Fokus, Zoom/Resize, Seiten-/
Blattwechsel/Reset und sofortigen gespeicherten Abschluss. Die neue Matrix führt
diese Fälle für beide Fonts mit gewählter Stiftgestaltung aus. Unabhängiger Font-/
Stilwechsel erhält History, Savebytes und semantische Hinweislesepositionen.
Die frühere Tinte entfällt begründet durch E1. Reguläre P1-Regressionen bleiben vollständig.

Die kontrollierte Uhr wird nur im Capture gesetzt. Dieselbe Produktionszeichenfunktion
zeichnet die Zwischenstände; das ist ein Geometrienachweis, keine behauptete reale
Aufnahmefrequenz. Die getrennte Echtzeitfolge und F-03-Lastmessung verwenden die
normale monotone Uhr. Zeichenzeiten, 100-Zellen-Eingabe inklusive synchronem Save
und Frameabstände bleiben getrennt von realer Maus-/DPI-Abnahme.

## Reproduktion und Artefakte

```powershell
$zs1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $zs1Cache --output-dir artifacts/zs1-product
```

Isolierte Pillow-12.3.0-Umgebung, gepinnte Godot-4.7.2-Toolchain und vollständige
Git-Historie nach Projektprofil; Linux zusätzlich Xvfb/Mesa. Der Produktharness
verwendet temporäre Projekt-/Profilpfade, keine normalen Saves. Die sechs Jobs
`docs`, `product`, `preflight`, `puzzle-production`, `rp4-windows`, `rp5-repair`
bleiben verpflichtend. Lokale Entwicklungsläufe ersetzen die aktuellen CI nicht.

- `zs1-windows-study-<Head>`: `picross-zs1-windows-x86_64.zip`, EXE-Paar,
  Eigentümeranleitung, Identität, Fontstatus und Lizenzen der enthaltenen Fonts.
- `zs1-review-<Head>`: `picross-zs1-review.zip`, 42 native Vergleiche,
  drei Ziffernproben, Fontidentitäten/-metriken und HTML-Index.
- `zs1-strokes-<Head>`: `picross-zs1-strokes.zip`, sieben kontrollierte native
  Strichbilder, getrennte Echtzeitfolge, Zeit-/Hashbindung und HTML-Index.

Die Indizes sind Nachweisgalerien, keine Browserimplementierung des Spiels.
PNG bei 100 % prüfen. Vollrender-Sammelupload bleibt manuelles Opt-in.
Reguläre Hauptszene und Standardzeichner bleiben erhalten; regulärer Export
schließt `study/*` aus. Nur der Studienexport verwendet die getrennte Hauptszene
und Appidentität. Beide Eigentümer-TTFs sind ausschließlich im Studienexport enthalten.

## Abnahme und Historie

Die Erstlieferung mit 117 Studienprüfungen, 42 Vergleichen und zwei Fade-Zeitfolgen
bleibt ausschließlich an R1/`4ae4f5a` gebunden. Die fontunabhängige E1-Lieferung `9df51f0`
mit 720 Studienprüfungen und 28 Ansichten bleibt ebenfalls historisch.
Die aktuelle lokale Studienprüfung umfasst 1057 Assertions und 42 Ansichten
unter Windows/OpenGL/RTX 3070. Aktuelle finale CI-/Download-/Sichtprüfung und
der getrennte Selbstreview werden mit Headbindung im PR dokumentiert; frühere
grüne Läufe werden nicht als Prüfung des neuen Heads ausgegeben.

**Mergeentscheidung E3:** Chalkboard, Stift und Timing sind gewählt. Nach N07
müssen die aktuellen technischen Checks und ein commitbezogener Prüfschritt den
neuen Head abdecken. Der Eigentümer hat PR #55 anschließend zum Merge freigegeben
und die kombinierte reale Sichtprüfung auf `main` verschoben. Diese Nachprüfung
bleibt vor #53 offen und wird nicht als bestanden umgedeutet. #52 bleibt dafür
vorerst offen; #53 ist nicht implementiert.
Keine Hintergrundproduktion oder Veröffentlichung.
