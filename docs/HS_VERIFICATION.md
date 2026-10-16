# HS / #186 · technische Prüfzuordnung

Fachvertrag: [CLUE_STATUS](CLUE_STATUS.md), Typografie: [HC/HF](CLUE_TYPOGRAPHY.md).
Ein Paket auf `feat/186-hinweisstatus`, Draft-PR #187 gegen `main`, ohne vorgeschalteten
Dokumentationsmerge. Tatsächliche Resultate, Head/Basis/Checkout, Run und Artefakte
stehen im PR. Diese Zuordnung behauptet keinen noch fehlenden Prüferfolg.

| Akzeptanz | Nachweisweg |
| --- | --- |
| HS-A01/A02 | `hs186_capture.gd` zeichnet über den produktiven Zahlen-/X-Pfad: 12 native Panels, drei gemeinsame Fenster/UI-Konfigurationen, Zellen 16/24/40 und 23,37 px, beide Achsen, Mono/dunkle/helle Farben, `1/11/17/23/40/50`, dichte Nachbarn sowie `…/–`. Fünf Original-PNGs je Panel: OPEN, FILLED, CLOSED, CLOSED ohne X und X allein. `hs186_verify.py` prüft identische positive Zahlen/C1, isolierte 60-%-Pixel, sichtbare zwei Diagonalen und unmarkierte Marker. Gegenproben erkennen eine volle CLOSED-Zahl, fehlendes X und fehlende Abschwächung. |
| HS-A02/A03 | Redraw, Zoom-Rundweg und neue Session müssen bytegleiche CLOSED-Pixel liefern. `hs186_cases.gd` prüft Varianten über ursprüngliche Identität, beide Züge einschließlich Dicke/C1/AA und statusunabhängige Overlaypositionen/-umbrüche. Native Pixel dürfen die reservierten Hüllen nicht verlassen; dichte Nachbarhüllen bleiben disjunkt. Bestehende HC-/VS2-/HF-Tests prüfen größte Fontgrade, Slots, G/V, Marker, kontinuierlichen Drag/Snap, Fit, semantische Anker und Tooltiprahmen weiter. |
| HS-A04 | Unveränderte H1-/GP48-Tests prüfen eindeutige Zuordnung, Widerspruch/Mehrdeutigkeit, echte Ränder, X, andere Farben, unbekannte Nachbarn, Vorschau/Rückzug/Abbruch, Undo/Redo und Sitzungsschalter. Kern-/Prozess-/Save-/Recoveryregressionen bleiben aktiv. Kein Erkennungscode geändert. |
| HS-A05 | Web verwendet denselben vollständigen Kandidatenpfad wie nativ; die unbewiesene alte `strike_width`-Vorablehnung entfällt. Gezielte positive/negative Fontkandidaten einschließlich Bruchzellmaß und nächstem nicht passenden Grad; unabhängige RID-Rekonstruktion in `vs2_v1_verify.py`. Browser-CI prüft Chromium/Firefox, kleine 5×5, Persistenz und isolierte SSH/HTTP-Referenz. Acht temporäre Größenatlanten bleiben unverändert begrenzt. |
| HS-A06/T01 | Product integriert die HS-Originalbilder/-Berichte in den vorhandenen Visualweg. Nach finaler Pflicht-CI lädt `hs186_windows_probe.py` Spieler und Technik frisch herunter, prüft GitHub-/Dateihashes und Head/Basis/Checkout/Run, startet echte Windows-EXE/PCK isoliert und führt HF sowie dieselbe HS-Probe extern gegen die ausgelieferte PCK aus. Native Renderer-/DPI-/Skalierungswerte und Fontbytes werden protokolliert. Vollständiger Diff und getrennter Selbstreview im PR. |

`HS186_OUTPUT` bezeichnet eine leere technische Ablage. Kein Produktionsrätsel wird
als neue Testfixture verwendet. Die native Swatch ist selbständig synthetisch und
läuft auch extern gegen eine PCK ohne mitgelieferte Tests. Für frische Actions-Belege:

```powershell
python tools/hs186_windows_probe.py --head <SHA> --run <Run-ID> --engine <gebundene-Konsolen-EXE> --cache-dir <Archivcache> --output-dir <neue-Ablage>
```

Endparameter: beide positiven Zahlen/C1 60 %, X 76 %, Breiten
`max(1, fs/18) × 1,08` beziehungsweise `× 0,96`. C1-Farbzuordnung bleibt.
Die Mittellinien sind um maximalen Stift-/C1-Radius plus 0,5 px eingerückt, damit
1 px natives Polyline-AA ohne unnötige Slotvergrößerung eingeschlossen bleibt.
Die unabhängige Rekonstruktion verwendet native RID-Glyphen-/Vorschubdaten;
kein reservierter alter Querstrich bleibt im Overlay oder Fit.

HS-R01 (unabhängiges technisches/visuelles Review) und HS-M01 (Eigentümerprobe bei
kleinem/mittlerem/größerem Zoom, UI100/125, Mono/Farbe und Vollhinweis) bleiben
**vor Merge** separate Gates. Der Implementierer dokumentiert seine native Sichtung,
ohne sie als Eigentümerabnahme auszugeben. Fehlende technische Belege bleiben
ausdrücklich offen. Kein Merge, Release oder Deployment durch diese Lieferung.
