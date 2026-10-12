# Qualitätsprüfung r03

ID `pz-3a744ae1b7cb4d38b0ac29d030ef`, Inhalt `content_ready`, redaktionelle Endabnahme offen. Regelwerk `0.4.0`; vollständiger Toolcommit `039f59d9a94ad6c2fea32a900d03d1d3b8a7df4c`. Datum 12.10.2026 (Europe/Berlin). Alle Befunde sind eigene Prüfung; der unabhängige Blockintervall-Prüfer ist algorithmisch unabhängig vom Solver. Ein unabhängiger menschlicher/Agentenreview wird nicht behauptet.

## Eingang, Freigaben und Herkunft

[Integritätsprüfung](audit/input-validation.json): v2-Übergabe, 35/35 Nutzdateien einschließlich Größen, tatsächlicher Inventarhash und beide PNG-Bindungen bestanden. A-r01 und MA-r01 sind PNG/RGB, 1254×1254, ohne Bildmetadaten; Originalbytes bleiben unverändert.

- A-r01: SHA-256 `0a102f0e49cd93f9b2851d9e5d7ba82edb601102055322a1628e806d544a4674`; [menschliche Freigabe](approvals/reveal-A-r01.json), tatsächliche Erklärung in `sources/user-request-r02.txt`.
- MA-r01: SHA-256 `d2cb88764e084cd8afe07449151e439539fce2c1152bc7cfb1d3aac2abcd6a19`; [menschliche Freigabe samt Korridor](approvals/motif-MA-r01.json). Sie fehlte im Eingang und wurde erst auf konkrete Nachfrage im aktuellen Auftrag erteilt. Der UTC-Zeitpunkt ist das unmittelbar danach gelesene Empfangsprotokoll, kein behaupteter genauer Sendezeitstempel.
- [Native Ableitung](motifs/Knoblauch_MA_r01.provenance.json) bindet exakt A-r01, Referenzbild, Prompt, bekannte Einstellungen und getrennte Datei. Die Freigaben stehen in Sidecars; historische Provenienzfelder `approval:null` werden nicht nachträglich umgeschrieben. Kein deterministischer Neugenerierungsnachweis oder unabhängig authentifiziertes historisches Dienstprotokoll behauptet.
- Originalgenerierung auf Nutzerauftrag und native Ableitung; kein Fremdasset. Nutzungsgrundlage dokumentiert, keine unabhängige juristische Prüfung behauptet. Quelle → Abschlussbild → Motiv ist redaktionell/dateibasiert belegt. Ab MA-r01-Bytes werden Normalisierung, Raster, Hinweise und Proofs mit bestehenden Werkzeugen exakt rekonstruiert.

[Quelle/Umgebung](audit/source-and-environment.json): aktuelles Remote-main gelesen, lokale Arbeitskopie zwei Commits älter. Produktion aus externem unverändertem Snapshot bzw. bytegleichen Toolkopien, Python 3.13.14, eigene venv mit Pillow exakt 12.3.0. Keine Repository-/Werkzeugänderung, kein Export oder Veröffentlichung. Zusätzliche Bereichs-AGENTS existieren im Snapshot nicht.

## Vier gezielte Importe

Vor Import [Plan](production/plan-r01.json) und [strikten Entwurf](production/design-r01.json) gespeichert. 40×40, Mono ink `#000000`, Leer `#ffffff`, BOX/area, Crop `[66,40,1240,1214]`, 1174×1174, `fit:exact`, keine Streckung. Nur äußerer Hintergrund bzw. Antialias-Randsaum entfernt; ganze dunkle Motivform, Hals und Wurzeln erhalten. Kein zusätzlicher Randpunkt oder Rahmen. Produktgrenze ≤50 je Achse erfüllt.

| Kandidat | Belegung | Offen | Logik | Redaktionelle Entscheidung |
| --- | ---: | ---: | --- | --- |
| area-96 | 754/1600 (47,125 %) | 10 | geprüfter Fixpunkt | Dünnere, unterbrochene Hals-/Wurzellinien; nicht gewählt. |
| area-128 | 795/1600 (49,6875 %) | 8 | geprüfter Fixpunkt | Bester Kompromiss von weißen Bahnen und Wurzel-/Halsdarstellung; Reparaturreferenz. |
| area-160 | 843/1600 (52,6875 %) | 0 | zertifiziert | Wurzelfächer und auslaufende Trennungen stärker zu massiver Basis verschmolzen. |
| area-192 | 875/1600 (54,6875 %) | 0 | zertifiziert | Stärkste Verdickung, geringste Wurzel-/Negativraumgliederung. |

Alle vier Matrizen unterscheiden sich exakt nach Maßen/Palette/Zellwerten, nicht nur nach Parameterhash. Alle Randprüfungen: links/oben/unten belegt, rechts leer; `(left OR right) AND (top OR bottom)` erfüllt. [Metriken und Matrixvergleich](audit/raster-metrics.json). Vier frische CLI-Nachweisprüfungen und vier erfolgreiche `inspect_candidate`-Rekonstruktionen bestätigen jeweils Status, Datei-/Parameterbindungen, exakte Hinweise und Rasterpixel. Fixpunkt bedeutet kein Unlösbarkeits-/Mehrdeutigkeitsurteil. Belege: `audit/area-*-verify.json` und `audit/area-*-origin-r02.json`; [echte Ansichten](views/candidates-r01.png).

Die ersten vier Origin-Hilfsaufrufe scheiterten vor Prüfung wegen eines von mir falsch angegebenen Modulpfads für Budget. Logs bleiben erhalten; korrigierte frische Aufrufe benutzen `contract.Budget`. Kein Werkzeugfehler und keine verschwiegene erfolgreiche Prüfung des ersten Versuchs.

## Motivgeschützte Reparatur

[Vorabplan](production/repair-plan-r01.json), [vorher geöffnete zulässige Stellen](views/repair-allowed-r01.png): 1597 Zellen hart geschützt, einschließlich gefüllter Hauptformen und wichtiger Leerflächen. Nur drei konkrete lokale Stellen durften verändert werden. Maximal zwei Änderungen; Seed 39; `single-cell`/`seeded-frontier-v1`; 96 kumulative Vorschläge, 16 Bewertungen; Suche 30 s/250000 Linien, Abschluss 10 s/100000 Linien. Keine Lockerung.

Fund nach drei Vorschlägen und drei Bewertungen einschließlich Referenz; Suche 0,489 s, Gesamt 0,610 s auf dieser Umgebung. Zwei nullbasierte Änderungen: `(27,28)` ink→empty verbreitert eine vorhandene weiße Trennung um eine Zelle; `(14,37)` empty→ink verbindet vorhandenen Wurzelast mit erhaltener Spitze. Keine Umgestaltung von Identität, Perspektive, Hauptproportionen, Hals oder wichtigen Innenräumen festgestellt; keine materielle Motivänderung. [Vorher/Nachher/Diff/Schutz](production/repair-r01/view.png). Keine Änderung an A-r01 oder MA-r01.

[Frischer Endnachweis](production/repair-r01/final-proof.json) unter `full-line-mono` v1, Start unknown, search false: solved, 297 informative Schritte, 0 offene Zellen. [Separater frischer CLI-Prüferprozess](audit/final-verify.json) akzeptiert vollständig; [vollständiger RP-5-Replay](audit/repair-replay.json) rekonstruiert Referenz, alle Eltern/Kandidaten/Änderungen, Hinweise, Dateien und geschriebenen Endproof. Ergebnis found/certified/accepted. [Zusatzprüfung](audit/final-checks.json): Hinweise exakt neu extrahiert, alle 1597 geschützten Zellen gleich, Singleton-Enddomains exakt Matrix, gültige Maße/Palette und Randregel. Vollständiger Deduktionsnachweis belegt auch Eindeutigkeit. Endkandidat ist explizit Reparatur, keine Umbenennung als Originalimport.

## Tatsächliche Sichtprüfung

[Direkter Dreifachvergleich](views/final-comparison.png), [verlustfreies Zell-PNG](production/repair-r01/after.png), [ohne Glättung](views/final-nearest.png), [Gitteransicht](views/final-grid.png) wurden tatsächlich geöffnet; zusätzlich alle vier Importbilder und die Reparaturansicht.

| Kriterium | Abschlussbild A-r01 | Motiv MA-r01 | Finales Raster |
| --- | --- | --- | --- |
| Erkennbarkeit | erfüllt: Knoblauch eindeutig | erfüllt: Knolle, Hals, Wurzeln | erfüllt: stilisierte Knolle plausibel; farbige Auflösung macht Knoblauch eindeutig, gemäß Mono-Vertrag zulässig |
| Silhouette/Proportionen | erfüllt: breite gelappte Knolle | erfüllt: aufrecht, Hals nach rechts | erfüllt: breite Grundform und Halsneigung erhalten, zellbedingte Treppen |
| Details/Negativflächen | erfüllt: Schalenlappen, Wurzeln | erfüllt: breite weiße Formtrennungen | erfüllt: dominante Trennbahnen erhalten; schmale Ausläufe teils unterbrochen, Wurzelfächer stark reduziert, keine durchgehend offenen Kanäle behauptet |
| Palette/Mono-Lesbarkeit | erfüllt: Elfenbein/Ocker/Mauve, klare Konturen | erfüllt: klare Schwarz-/Weißflächen | erfüllt: exakt Schwarz/Weiß, keine Ton-in-Ton-Verwechslung; Farbsinnsimulation für Mono nicht erforderlich |
| Serienästhetik | erfüllt: warme ausgearbeitete 2D-Illustration | erfüllt: organische vereinfachte Flächen | erfüllt: klare motivische Zellstilisierung; detaillierte Belohnungsansicht unverändert erhalten |

Die beiden Reparaturen sind im Vergleich lokal und motivverträglich. Größere Detailverluste stammen aus der bereits freigegebenen Mono-Abstraktion und der 40×40-Auflösung, werden nicht durch nachträgliche Reveal-Änderung kaschiert. Eigene Bewertung bleibt von menschlicher Endabnahme getrennt.

Weiche Prüfanlässe: 49,6875 % Belegung, keine leeren Innenzeilen. Spalte x=38 ist leer und Teil des äußeren rechten Hintergrundstreifens zusammen mit x=39, kein innerer Motivschnitt. Bewusst nicht entfernt: freigegebene 40×40, proportionstreuer Crop und gültiger neuer Proof. Sieben orthogonal isolierte Füllzellen: sechs stützen diagonal geführte Hals-/Schulterkonturen; eine auch diagonal isolierte Zelle `(16,39)` bleibt als kleine Wurzelspitze. Sie bewahrt die Vorlage, ist kein neuer motivfremder Punkt und kein Randregeltrick (oben genügt bereits). Diese Warnungen sind begründete weiche Ausnahmen, keine harten Mängel.

## Schwierigkeit und Bearbeitungsumfang

[Bewertung](difficulty.json), Methode `picross-difficulty-0.1`: **L3 – mittel**, plausibel **L2–L4**, `editorial_estimate`, Vertrauen **low**. R1-Überlappungen langer Blöcke bieten viele frühe Fortschritte; die kurzen 1/2/3-Blöcke im Hals verlangen voraussichtlich kombinierte Zuordnungen (R2). Beispiel vor Schritt 126: Zeile 11 `[3,2,3,1,1]` mit mehreren Ankern zwingt Spalten 25 und 27 leer. R2-Notwendigkeit/-Vollständigkeit und mögliche R3-Anteile wurden nicht erschöpfend getrennt. Kein validierter Analysator und kein `instrumented`-Urteil.

[Ausgewählte aktuelle Wissensstände](audit/difficulty-checkpoints.json) zeigen oberhalb der Restaufräumgrenze von 32 offenen Zellen 36/32/26/26/23/27/21/11 gleichzeitig produktive Linien unter Vollprofil. Keine definierte Engstelle beobachtet; Stichproben schließen eine solche nicht vollständig aus. Sequentielle Kleinschritte sind kein Beleg fehlender Alternativen. 297 Proof-Schritte, 1600 Zellen, 795 Füllungen/805 Leerstellen und Maschinenzeiten erhöhen die Stufe nicht automatisch. Lösungszeit null/nicht geschätzt; keine menschlichen Kalibrierungsdaten. Probespiel nicht durchgeführt, optional und kein Gate.

## Abnahme und Zielgrenzen

Inhalt bereit zur menschlichen Endabnahme genau dieser r03-Dateien und des in `handoff.json` gebundenen Inventars. Endabnahme pending; keine Freigabe erfunden. Bestehende Adapter sind fest auf F-04/SVG bzw. F-05 bis F-09 begrenzt. Kein passender Adapter/Runtime-Identifier für dieses neue Rätsel; kein Export versucht und kein historischer Pilot umgewidmet. Gemeinsamer Produktionsindex nicht verfügbar/verifiziert; lokale ID bleibt unverändert, keine globale Reservierung behauptet. Diese Kataloggrenzen verhindern keine redaktionelle Inhaltsabnahme.

Keine Änderungen am Spiel/Repository oder Werkzeug: deshalb keine Integrations-PR/CI-/Godot-/PCK-Tests ausgelöst. Tatsächliche Nachweise dieses Inhalts sind die lokalen frischen Import-/Proof-/Reparaturprüfungen. Keine Linux-RSS-/Benchmarkabnahme behauptet. Aktive Menschenminuten unbekannt; vier historische native Bildaufrufe, kein neuer Bildaufruf; vollständige Zähler in [effort.json](effort.json). Vollständiges ursprüngliches Paket in `history/`; aktuelle Übergabe und nächste Schritte in [handoff.json](handoff.json).
