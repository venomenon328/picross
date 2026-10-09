# VS2 · reguläre Vollsichtintegration

Auftrag: [#61](https://github.com/venomenon328/picross/issues/61), VS2-01–07 und
VS2-A01–A10. Arbeitsbranch `feat/61-regular-full-view`; tatsächliche Basis
`fad885344874534629365917a2ab6a8d311cd3a7`.
Der [vor Vergleichen gebundene Plan](../examples/vs2/plan.json) wurde auf
`4fa23d2` committed. Keine erneute Korpusproduktion.

Startblocker VS2-D01 ist erledigt: [PR #56](https://github.com/venomenon328/picross/pull/56)
integriert #53 einschließlich ZS2-N01–N03 auf dieser Basis. R3 und positive
ZS2-M01/R1-A01 gelten ausschließlich für den Vorgänger. GF-M01/#59 ist nach
[abschließender Klarstellung](https://github.com/venomenon328/picross/pull/60#issuecomment-6076039228)
bestanden; der Merge ist `24564dfed3bb9844d151f4c4ec055d051232d16f`.
Das breite frühere VS-M01-Protokoll bleibt persönlich unvollständig.

| Akzeptanz | Aktiver Nachweisweg |
| --- | --- |
| A01/A02 | Reguläre Szene; `vs2_tests.gd`, `vs2_roundtrip.gd`, normaler Windows-Downloadstart. Sammlung, eine Optionswahl, Sitzungsdefault und Abbruch. |
| A03 | Native Viewportevents für Raster-MMB, injizierte obsolete Hand und passive Miniatur; unabhängige Hinweisziele samt Bereichsübertritt. P12 prüft Snap/Abbruch/Nachbarn. |
| A04/A05 | `vs2_gf1_tests.gd`: alle Slotgrenzen ±0,01, Null-/Teilbudget, echte Glyphen/C1/Statusstriche und kontinuierliche Grenzen/Intervalle. `vs2_tests.gd`: 304 reguläre Layoutfälle. |
| A06 | Alle neun unveränderten regulären Inhalte plus zehn gebundene technische Fälle über `tests/vs2_scene.gd`; vier Flächen, UI100/125, beide Modi, Ecken, proportional eigene Miniatur. Kein Spielerimport. |
| A07 | G1/GP48/H1 und reguläre ZS2-/N01–N03-Suiten; native X/Schraffur 12/24/36 px und gerichtete 17-Zellen-Welle einschließlich Gegenknopf-Abbruch. |
| A08 | Tatsächlicher alter regulärer Prozess schreibt, neuer Prozess liest; neuer Writer → frischer Reader. Schema-1-Validierung bleibt vollständig; P13/500-Aktionen und Recovery bleiben aktiv. |
| A09 | Normales ZIP ohne Studienplayer/-protokolle; tatsächliche PCK-Inventur und native Downloadprobe. Studienreplays sind separat deklarierter Entwicklerbestand. |
| A10 | Normative Quellen, Hilfe und neutrale [Eigentümeranleitung](VS2_OWNER_TRIAL.md); sechs aktuelle Pflichtjobs am Lieferhead/Test-Merge. |

Speicherabbildung: erst vollständige bestehende Validierung durch SaveStore,
danach `hand → fill`, Mittelpunkt statt altem Pan und tatsächliche Zellgröße
`min(gewünschte gültige Arbeitsstufe, Fit)`. `overview=true` bezeichnet Einpassen;
die gewünschte Arbeitsstufe bleibt separat erhalten. Berechnete Bruchteile werden
nicht in `zoom` geschrieben. Der Ansichtsmodus ist ausschließlich Sitzungseinstellung.
Zellen, vollständige History/Redo, Cursor, `undo_used`, Abschluss, Farbe, Radierer
und semantische Reads bleiben erhalten. Studienroot bleibt unberührt.

Gezielte Umstellung alter Oracles:

| Bisheriger Zweck | VS2-Zuordnung |
| --- | --- |
| P12 Miniatur-/Hand-/Rasterpan | Gleichheitsprüfung von Raster/Zellen/History, MMB nur auf überlaufenden Hinweisen. Zweite unabhängige Linie ebenfalls MMB. |
| P12 Zoomschleifen/Resize und P13 Fehler nach Zoom | Endliche gültige Arbeitswünsche mit Fitgrenze; garantierte ausstehende gültige Werkzeugänderung für Flushfehler. |
| P12 historische Sechs-/Vier-Slot-Snapfälle | Explizite Board-Komponente; unveränderte geometrische Snap-/Richtungsoracles. Neue reguläre Reserven separat mit mindestens fünf Zahlen. |
| 500 Aktionen, zehn entfernte Regionen | Unveränderter unabhängiger Zell-/Historyoracle und alle 500 Aktionen; Mini/Pan jetzt negative View-Oracles, Zoom exakt fitbegrenzt. Mehrprozess-Redo bleibt. |
| Z2 Aktionen/Information/Recovery | Entfernte Handauswahl ersetzt durch Füll-/Radierwahl; negative Raster-/Miniaturtransienten, reale MMB-Hinweise, unveränderte Flush-/Recoverymodalität. |
| ZV50 167%-Clipping/feste Standardbox | Vollständiger Rahmen bei jeder angebotenen Stufe, endliche Zoomversuche, aktueller Fit statt alter festen Box. Native Vorher-/Nachherdaten benennen die Geometrieänderung. |
| ZS2 72px-Schrift-/X-Komponentenprobe | Expliziter Entwicklerzeichner für räumlichen Pixeloracle; angebotene reguläre 12/24/36px-Darstellung und Timing zusätzlich unverändert streng geprüft. |
| Native partielle X-/historische Snapbilder | Explizite Zeichnerkomponente; keine Behauptung eines regulär angebotenen abgeschnittenen Rasters. |
| GP48/ZS2 Bildschirmgleichheit | Identische eigene Zellen/Fachzustände, stabile Statusgeometrie, vollständiger neuer Rahmen und ausgewählter Font; keine falsche Pixelgleichheit bei geändertem Layout. |
| Historische ZS1-/VS1-Vergleichsoberflächen | Gepinnter Entwickler-Replay von Basis `fad8853`, Quellen/Reports klar als Referenz. Neue reguläre Prüfungen laufen zusätzlich. Keine separaten Studienplayer in Standard-CI. |

Historische Manifeste, Pläne, Proofs, Produktionsreihen und Abnahmen bleiben
unverändert. Vollständige Arbeitsrender werden weiter geprüft und nur bei manuellem
Opt-in komplett hochgeladen. Fachoracles, Zertifikate und RP-Reparaturreplays bleiben.

Aktuelle Ausführung und commitgebundene CI-/Downloadnachweise werden im Draft-PR
gebunden: Head, Basis, Test-Merge, Run/Artefakt, EXE-/PCK-/Bild-/Berichtshashes.
Lokale Entwicklungsproben sind noch keine saubere finale Lieferung.
Geometrische Passung bei kleinen oder kollidierenden Glyphen ist kein Komforturteil;
Matrixberichte führen Einschränkungen sichtbar, einschließlich vorhandener Großfälle.

**Offen vor Merge:** unabhängiges technisches und visuelles Review des konkreten
Heads, VS2-M01 am regulären heruntergeladenen Windows-Paket und passende ausdrückliche
oder bedingte Mergefreigabe. Kein Merge, Release, Tag, Branch- oder Benutzerdatenlöschen.
