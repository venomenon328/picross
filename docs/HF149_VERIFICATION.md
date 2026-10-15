# HF / #149 · Prüfzuordnung

Ein gemeinsames Paket auf `fix/149-hinweisflaeche-overlay`, eigener Draft-PR gegen
`main`. Fachvertrag: [Hinweistypografie](CLUE_TYPOGRAPHY.md), Umfang und Gates:
[Issue #149](https://github.com/venomenon328/picross/issues/149). Konkrete Resultate,
Head, Basis, Test-Merge und Actions-Run stehen im PR, nicht als vorweggenommene Abnahme.

| Akzeptanz | Aktueller Nachweisweg |
| --- | --- |
| HF-A01/A02 | `hf149_probe.gd`: beide Achsen, 30×35 und 50×50 mit acht Farben, UI100/125, keine/partielle/vollständige Reserve und jeweils −0,01/0/+0,01 Pixel an ausgewählten Slotgrenzen. `hf149_verify.py` rekonstruiert das freie Budget unabhängig und verwirft eine ausgelassene passende Kapazität. Bestehende GF1-Schwellen und VS2/V1-RID-Oracles prüfen Fit, nächsten Hundertstelkandidaten, Font und Slots weiter. |
| HF-A03/A04 | Vier Rasterecken, unveränderte Komposition bei Zellzustandswechseln; bestehende VS2-/V1-/G1-/H1- und Eingaberouten sichern G/V, unabhängige Achsendrags, Marker, Originalindizes, Farben, nächste Snaplage und Variante A einschließlich kontinuierlicher Zwischenlagen. |
| HF-A05 | Separate HF-Schreib-/Leseprozesse: beide Achsen mit Rasterende/Mitte/Außenanfang, schmal → vollständig, G→V→G, normaler Schema-1-Writer bei Vollanzeige, frischer Slotreader mit vollständiger Validierung und Rückkehr zu denselben schmalen Fenstern samt echtem Redo. Reguläre VS2- und P1-Prozessroundtrips erhalten Blattwechsel und Recoveryabdeckung. |
| HF-A06 | Echte Hauptszene bei 1280×720/UI125, 1920×1080/UI100, 2560×1440/UI125. Kleine/große Zoomwünsche, beide Achsen, echte drei H1-Zustände, alle acht Originalfarben, ein- und mehrzeilige Boxen. Vollständig passende Linien werden ausdrücklich als solche geprüft und öffnen kein Overlay. Native Originalausschnitte plus wenige Szenenkontexte, Text-/Abstands-/Innenrandmessungen und unabhängige Negativkontrollen gegen Überlappung und falsche Font. Klickschutz und ruhende Maus bei G→V werden gezielt geprüft; bestehende echte Ereignisrouten bleiben aktiv. |
| HF-A07/T01 | Product integriert HF in den aktuellen Visualpfad, liefert Bilder/Messdaten und separate PCK. Nach erfolgreicher finaler CI: frisch heruntergeladenen Windows-Player regulär starten, dieselbe externe HF-Probe gegen dessen PCK ausführen, EXE/PCK und tatsächlich geladene Font-/Rahmenressourcen binden. Getrennter vollständiger Selbstreview im Draft-PR. |

Die HF-Probe benutzt ausschließlich temporäre synthetische Definitionen und Profile.
Kein Produktionsrätsel wird zur Fixture; Runtimebestand und Font-/Bildbytes bleiben
unverändert. `clue_overlay.gd` verwendet ein ruhiges 128×128-Papierstück bei (700,400)
aus dem gebundenen A-Arbeitsasset und `frame-preview.png` aus SL-65. Die Herkunft
und Nutzungshinweise dieser unveränderten Ressourcen gelten weiterhin; dies ist
technische Wiederverwendung, keine neue Assetabnahme. Rahmenränder werden mit
halber UI-Skalierung, festen Ecken und gekachelten Kanten gezeichnet; 28×UI Textinset
liegt innerhalb der sicheren Fläche des ursprünglichen `frames.json`.

`HF149_OUTPUT` bezeichnet eine leere technische Ablage. `HF149_STAGE=write` und
danach `read` wählen zwei frische headless Prozesse; ohne Stage laufen Geometrie
und native Bilder. `capture` ist nur die kurze Entwicklungsroute ohne Grenzmatrix.
Für Exportproben das lokale Skript als externen `--script`-Pfad und die gelieferte
PCK als `--main-pack` verwenden. Testskripte werden nicht in den Spieler exportiert.
`tools/hf149_windows_probe.py --head <SHA> --run <Run-ID> --engine <gebundene
Konsolen-EXE> --cache-dir <Archivcache> --output-dir <neue Ablage>` prüft den
frischen Actions-Download, beide EXEs und dieselben drei Prozesse gegen die PCK.
Geladene Delight-/Fraunces-Bytes und Rahmen-/Papierpixel müssen den lokalen
unveränderten Quellen entsprechen. Zwei zusätzliche 30×35-Szenen zeigen den
gemeldeten Wechsel zwischen kleinem vollständigem und größerem gekürztem Hinweis.

HF-R01 (unabhängiges technisches/visuelles Review) und HF-M01 (gezielte persönliche
Windows-Probe durch den Eigentümer bei UI100/125) bleiben vor Merge separate Gates.
Technische Sichtung und Selbstreview ersetzen sie nicht. Kein Merge oder Release.
