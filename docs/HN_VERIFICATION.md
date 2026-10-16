# HN: technische Prüfzuordnung

[Issue #192](https://github.com/venomenon328/picross/issues/192) und
[HN-D01–D05](CLUE_INTERACTION.md) binden das gemeinsame Paket. Ergebnisse und
Originalbelege stehen am finalen Head in Draft-PR #193. Diese Zuordnung ist kein
vorweggenommenes Testergebnis oder persönliche Abnahme.

| Akzeptanz | Aktueller Nachweisweg |
| --- | --- |
| HN-A01 | Bestehende P12-/VS2-Ereignisrouten mit Links: beide Achsen/Richtungen, kontinuierliche Tokenkoordinaten, Marker, .49/.51-Snapgrenzen, monotone Außenanschläge und Nachbarisolation. HN-Probe ergänzt wirkungsloses MMB sowie kurze/volle/Leerfolgen. |
| HN-A02 | `hn192_probe.gd` führt echte Down/Motion/Up-Ereignisse durch die reguläre Hauptszene: Hinweise → Nachbarlinie/Raster/Sidebar, falsches Up, Klick ohne Bewegung, nicht navigierbarer Start, Akkord, Zellbesitz und beide normalen Zelltasten. Vollständiger Snapshotvergleich ohne bestätigte Hinweisanker; keine Zellvorschau/kein Zähler/keine Buttonaktion. ZR-/ZS2-Regressionen bleiben aktiv. |
| HN-A03 | Escape, Fokusverlust, verlorene Freigabe, Akkord, Resize/UI/G/V-/Seiten-/Restorewechsel und frisches Down. Bestehende HF-/VS2-Prozessroundtrips sichern Anfang/Mitte/Ende über temporäre Vollanzeige, Schema-1-Save und echten Neustart einschließlich History/Redo. |
| HN-A04/A05 | Native Hauptszene bei 1280×720/UI125, 1920×1080/UI100, 2560×1440/UI125: Originalframes für Rasterkreuz, Zeile, Spalte, eingefrorenen Drag und vollständige Folge. Tatsächliche Pixel außerhalb der Overlayüberdeckung prüfen vorhandene und ausgeschlossene Bänder. Gegenbild ohne Cursor beweist unveränderte Overlaypixel; sichtbarer Boxklick bleibt konsumiert. HF prüft ruhende Maus bei Geometrie-/Moduswechseln und ungültige Trefferflächen. |
| HN-A06 | Wechsel der Hinweisquelle prüft `rest_draws` und `completion_searches`; absichtlich gekoppelte vollständige Chunkinvalidierung muss denselben Beobachter auslösen. PERF-B prüft den übrigen Ressourcen-/Cache-/Animations-/Session-/PCK-Vertrag. Cursorzustand enthält Session, gültigen Achsenkontext und reale Raster-/Hinweisgeometrie. |
| HN-A07/HN-T01 | Vollständige CI-Diffauswahl, alle ausgewählten Jobs erfolgreich, aktueller Webweg mit Chromium/Firefox/Persistenz und isolierter SSH-/HTTP-Referenz. `hn192_windows_probe.py` lädt den exakt gebundenen CI-Player/Technikbestand frisch, prüft Digests, EXE/PCK und Test-Merge-Eltern, startet beide Windows-EXEs und führt HF/HN am tatsächlichen PCK aus. Originalbilder/Logs werden ohne Profile/Saves separat zugänglich geliefert. Vollständiger getrennter Selbstreview am finalen Head. |

Die HN-Probe nutzt feste synthetische Mono-/Farbfälle mit gemessener realer
Überlaufgeometrie. Enge Komponentenflächen ergänzen die gemeinsame native
Fenstermatrix; keine Bestandsrätselzertifizierung oder neue kartesische Galerie.
`tools/vs2_delivery.py` nimmt alle HN-Originalbilder und den vollständigen Bericht
in die vorhandene technische Product-Lieferung auf. Native Windows-Probe und
Linux-CI bleiben getrennt an Sourcehead, Basis, Checkout, Run und Exporthashes
gebunden. Originalbelege allein auf lokalem Laufwerk erfüllen HN-T01 nicht.

**Vor Merge getrennt offen:** HN-R01 durch unabhängiges technisches/visuelles
Review des finalen Diffs und der Originalbelege; HN-M01 durch den Eigentümer im
isolierten Windows-Profil mit physischer Maus und UI100/125. Zu prüfen: beide
Hinweisachsen links ziehen, Rasterübergang und Abbruch, normale Zellbearbeitung,
einachsige Markierung bei geöffnetem Overlay sowie Hinweisquellenwechsel.
Build, tatsächliche Clientfläche, Windows-/UI-Skalierung und Einzelergebnis
protokollieren. Selbstreview und technische Automation ersetzen diese Gates nicht.
Mergefreigabe, Release und Deployment sind nicht Bestandteil dieser Lieferung.
