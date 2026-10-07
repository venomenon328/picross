# ZS-1 · Prüfzuordnung nach E1 und Liefergrenze

Stand: 07.10.2026 · bestehender Branch `feat/52-native-drawing-study`, Draft-PR #55

Basis `ec99954268f1ad959d9ea779dbbd9e28edf7d8fa`, Ausgangs-/R1-Head
`4ae4f5a20273808f99d257a3812da86d72307a5f`. Maßgeblich sind
[ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659),
[#52](https://github.com/venomenon328/picross/issues/52) und
[ZS-D01–D10](UI_DRAWING_STYLE.md). Neue Head-/Basis-/Test-Merge-/Run- und
Downloadbindungen stehen im PR und den maschinenlesbaren Artefaktberichten.
R1 bleibt historisch; neue Selbstprüfung ist keine unabhängige Zweitprüfung.

**Teillieferung:** N01/N02/N04/N05 und unabhängige N06-Nachweise umgesetzt.
N03 und der davon abhängige vollständige A01/A02/A06-/N06-Abschluss sind blockiert:
[beide TTFs und Originalquellen vorhanden, konkrete Rechtebelege fehlen](ZS1_FONT_INPUT.md).
Keine Kandidatenfontbytes verteilt, kein vollständiger Abschluss mit Platzhaltern.
Plex ist ausdrücklich bisherige Referenz und kein angebotener Ersatzkandidat.

| Kriterium | Aktueller Nachweis / Grenze |
| --- | --- |
| A01 | 14 native Situationen je bisherige Baseline und gewählter Stift: 28 Bilder auf identischen eigenen F-01/F-02/F-03-Ständen. Bisherige reguläre Boardpixel zusätzlich gegen 14 echte Main-Archivbilder geprüft. Der Zweifontvergleich fehlt. |
| A02 | Unveränderte echte Hinweise mit drei Zuständen auf beiden Achsen, C1, unabhängiger Hinweisdrag/Tooltip und beschriftete Ziffernprobe. Aktuell nur Plex-Referenz; Metriken/Glyphen/Fallbacks beider Kandidaten nicht als geprüft behauptet. |
| A03 | 1920×1080, 1280×720/UI125, 1600×900, 2560×1440; 12/24/36/72er-Zellen und F-01 bei 150 %. Gleiche Geometrie/Spielstände. Keine zusätzliche Studien-Rand-UI. |
| A04 | Echtzeitfolge mit statischer Vorschau, 20 parallelen Commits, zweiter Geste vor Effektende, Umwandlung und pixelgleichem Endzustand bei Aus. Zusätzlich sieben native 72-px-Zellausschnitte bei kontrollierten 0/21/49/70/98/119/140 ms: räumlicher Füllfortschritt, Zug eins vor Zug zwei. Bildprüfer lehnt aus diesen Bildern erzeugtes globales Fade und umgekehrte X-Reihenfolge ab. |
| A05 | Unveränderter Gesten-/Session-/Savekern; Normal-Sentinel vor/nach Studienlauf bytegleich. Echter Commit/Save im eigenen Root, Originaldaten/Proofs/Assets unverändert. Gesamter Produktweg mit Zwei-Prozess-, 500-Aktionen-, Recoveryregressionen sowie sechs aktuelle CI-Jobs erforderlich. |
| A06 | Schlankes Windows-ZIP, eigener nativer Vergleich und separates kleines Strichaufbau-ZIP. Identitätsbericht mit Head/Dirty/Basis/Test-Merge/Run, EXE-/Bildhashes, vorhandenem Fontmanifest/OFL und ausdrücklich blockiertem Eigentümerfontinput. Vollständige Kandidatenlieferung offen. |

`zs1_tests.gd` prüft stabile und begrenzte X-Pfade sowie die echten GUI-Ereigniswege:
Parallelstart, Priorität, Rückzug, Abbruch, Schutz/No-op, Radieren ohne Rückkehr alter
Markierungen, Undo/Redo, Schalter ohne Save/Replay, Fokus, Zoom/Resize, Seiten-/
Blattwechsel/Reset und sofortigen gespeicherten Abschluss. Die neue Matrix führt
diese Fälle einmal für die gewählte Stiftgestaltung aus; die frühere Duplikation
für Tinte entfällt begründet durch E1. Reguläre P1-Regressionen bleiben vollständig.

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
- `zs1-review-<Head>`: `picross-zs1-review.zip`, 28 native Vergleiche,
  Referenzziffernproben und HTML-Index. Kein Zweifontnachweis.
- `zs1-strokes-<Head>`: `picross-zs1-strokes.zip`, sieben kontrollierte native
  Strichbilder, getrennte Echtzeitfolge, Zeit-/Hashbindung und HTML-Index.

Die Indizes sind Nachweisgalerien, keine Browserimplementierung des Spiels.
PNG bei 100 % prüfen. Vollrender-Sammelupload bleibt manuelles Opt-in.
Reguläre Hauptszene und Standardzeichner bleiben erhalten; regulärer Export
schließt `study/*` aus. Nur der Studienexport verwendet die getrennte Hauptszene
und Appidentität. Die beiden Eigentümer-TTFs sind in keinem Export enthalten.

## Abnahme und Historie

Die Erstlieferung mit 117 Studienprüfungen, 42 Vergleichen und zwei Fade-Zeitfolgen
bleibt ausschließlich an R1/`4ae4f5a` gebunden. Der neue Entwicklungsstand bestand
lokal 720 Studienprüfungen, 28 native Ansichten und die gezielten Strichpixelprüfungen
unter Windows/OpenGL/RTX 3070. Zusätzlich bestanden 70 Python-Prüfungen (eine weitere
plattformbedingt übersprungen) und die Dokumentprüfung eines sauberen Quellsnapshots.
Aktuelle finale CI-/Download-/Sichtprüfung und der
getrennte Selbstreview werden nach Abschluss im PR dokumentiert; diese lokalen
Angaben behaupten keine Prüfung eines noch nicht benannten Lieferheads.

**Vor Merge offen:** Fontrechte und vollständiger Kandidatenvergleich, fehlende
abhängige Akzeptanznachweise, abschließende [ZS1-M01](ZS1_OWNER_TRIAL.md),
unabhängiges technisches/visuelles Review des neuen Heads und ausdrückliche
Mergefreigabe. Stift/Timing sind gewählt; M01 ist keine noch unbeantwortete Probe.
#52 bleibt offen, #53 nicht implementiert, #54 nicht gemergt/geschlossen.
Keine Hintergrundproduktion oder Veröffentlichung.
