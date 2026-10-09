# VS2 · reguläre Vollsichtintegration

## Aktueller Nachweisstand und Folgespezifikation VS2-E1

Auftrag: [#61](https://github.com/venomenon328/picross/issues/61), VS2-01–07 und
VS2-A01–A10, jetzt ergänzt um die **noch nicht implementierte** VS2-E1-Nacharbeit
N01–N05 / VS2-NA01–NA05. Arbeitsbranch `feat/61-regular-full-view`, Draft-PR #62.
Erstlieferhead `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`, tatsächliche Basis
`fad885344874534629365917a2ab6a8d311cd3a7`.
Der [vor den Erstvergleichen gebundene Plan](../examples/vs2/plan.json) wurde auf
`4fa23d2` committed. Keine erneute Korpusproduktion und kein rückwirkendes Ändern
dieses Plans durch die neue Spezifikation.

[Review R1](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5472592800)
ist für den Erstlieferhead und den damaligen Vertrag abgeschlossen, ohne B-Befund.
Die dortigen sechs erfolgreichen Jobs und nativen Nachweise bleiben an diesen
Stand gebunden. Die jüngere Eigentümerkritik und anschließende Spezifikationsfreigabe
sind **neue bestätigte Produktnacharbeit**, keine rückwirkenden technischen R1-Fehler.
VS2-M01 hat Rückmeldung mit Änderungsbedarf; keine vollständige positive Abnahme.

Startblocker VS2-D01 ist erledigt: [PR #56](https://github.com/venomenon328/picross/pull/56)
integriert #53 einschließlich ZS2-N01–N03 auf dieser Basis. R3 und positive
ZS2-M01/R1-A01 gelten ausschließlich für den Vorgänger. GF-M01/#59 ist nach
[abschließender Klarstellung](https://github.com/venomenon328/picross/pull/60#issuecomment-6076039228)
bestanden; der Merge ist `24564dfed3bb9844d151f4c4ec055d051232d16f`.
Das breite frühere VS-M01-Protokoll bleibt persönlich unvollständig.

## Basisprüfung A01–A10

Die folgende Zuordnung beschreibt die Erstlieferung und bleibt im nicht durch
VS2-E1 ausdrücklich abgelösten Umfang Regressionspflicht. Keine alte Zahl oder
Abnahme belegt automatisch den späteren neuen Head.

| Akzeptanz | Anschluss der Erstlieferung / erhaltener Prüfzweck |
| --- | --- |
| A01/A02 | Reguläre Szene; `vs2_tests.gd`, `vs2_roundtrip.gd`, normaler Windows-Downloadstart. Sammlung, eine Optionswahl, Sitzungsdefault und Abbruch. |
| A03 | Native Viewportevents für Raster-MMB, injizierte obsolete Hand und passive Miniatur; unabhängige Hinweisziele samt Bereichsübertritt. P12 prüft Snap/Abbruch/Nachbarn. |
| A04/A05 | `vs2_gf1_tests.gd`: alle Slotgrenzen ±0,01, Null-/Teilbudget, echte Glyphen/C1/Statusstriche und kontinuierliche Grenzen/Intervalle. `vs2_tests.gd`: 304 reguläre Layoutfälle der Erstlieferung. |
| A06 | Alle neun unveränderten regulären Inhalte plus zehn gebundene technische Fälle über `tests/vs2_scene.gd`; vier Flächen, UI100/125, beide Modi. Zusätzliche echte Eckklicks mit exaktem Undo/Redo, normalem Writer und proportionalem Reveal für alle fünf Dimensionen. Kein Spielerimport. |
| A07 | G1/GP48/H1 und reguläre ZS2-/N01–N03-Suiten; native X/Schraffur 12/24/36 px und gerichtete 17-Zellen-Welle einschließlich Gegenknopf-Abbruch. |
| A08 | Tatsächlicher alter regulärer Prozess schreibt, neuer Prozess liest; neuer Writer → frischer Reader. Schema-1-Validierung bleibt vollständig; P13/500-Aktionen und Recovery bleiben aktiv. |
| A09 | Normales ZIP ohne Studienplayer/-protokolle; tatsächliche PCK-Inventur und native Downloadprobe. Studienreplays sind separat deklarierter Entwicklerbestand. |
| A10 | Normative Quellen, Hilfe und neutrale [Eigentümeranleitung](VS2_OWNER_TRIAL.md); sechs aktuelle Pflichtjobs am jeweiligen Lieferhead/Test-Merge. |

Speicherabbildung: erst vollständige bestehende Validierung durch SaveStore,
danach `hand → fill`, Mittelpunkt statt altem Pan und tatsächliche Zellgröße
`min(gewünschte gültige Arbeitsstufe, Fit)`. `overview=true` bezeichnet Einpassen;
die gewünschte Arbeitsstufe bleibt separat erhalten. Berechnete Bruchteile werden
nicht in `zoom` geschrieben. Der Ansichtsmodus ist ausschließlich Sitzungseinstellung.
Zellen, vollständige History/Redo, Cursor, `undo_used`, Abschluss, Farbe, Radierer
und semantische Reads bleiben erhalten. Studienroot bleibt unberührt. Die zusätzliche
Layoutverschiebung N02 ist keine neue gespeicherte Panposition; N05 keine Zellmigration.

## Neue Kriterien VS2-NA01–NA05 · geplant, noch nicht ausgeführt

Dauerhafter Vertrag: [UI_DRAWING_STYLE.md, VS2-E1](UI_DRAWING_STYLE.md).
VS2-V1 umfasst N01/N02/N04; VS2-V2 N03/N05. Tests und Dokumentation gehören zu
beiden Teilpaketen; das gemeinsame Ergebnis bleibt in PR #62. Vor neuen Vergleichen
einen separaten endlichen Nacharbeitsplan mit tatsächlicher Basis, konkreten
Abstands-/Strichparametern und gezielten Bildern binden. Keine Wiederholung der
abgeschlossenen VS-Korpusproduktion und kein Umschreiben alter Manifeste.

| Akzeptanz | Später nachzuweisender Erfolg / Gegencheck |
| --- | --- |
| VS2-NA01 | Horizontaler Zeilenpitch gegenüber 26 × UI sichtbar enger bei gleichem Fontmaßstab; vertikal weiterhin 18 × UI. Reale 1/11/17/40/100, C1/AA, drei Zustände und Marker bleiben vollständig, kollisionsfrei und in gemeinsamen Slots. Rasteransicht min(5,n) auch über kontinuierliche Übergänge; Gesamtansicht alle Hinweise; Snap, monotone Bewegung und Leseanker erhalten. |
| VS2-NA02 | F-01 und geeigneter VS09-Breitenfall nutzen verbleibenden Raum für ausgewogenere Position des ganzen Raster-/Hinweisblocks. Vorher-/Nachherrechtecke und freie Randbudgets belegen die Verschiebung. VS08/VS04 plus knapper Fall sichern die GF1-Kapazität und unveränderten Lesemaßstab; Zentrierung erzeugt keine Leer-Slots, weitere Fitverkleinerung, fehlenden Zahlen oder instabile Rückkopplung. Reale Ecken-/Hinweis-/Gestentreffer folgen dem gemeinsamen Versatz. |
| VS2-NA03 | Native 1:1-Bilder von Raster, Miniaturfassung und Palette zeigen subtile Scribble-Wirkung. Stabile identitätsgebundene Striche über Neuzeichnen/Seiten/Neustart; kleine Zellen, Fünferkreuzungen, dunkle Füllungen und vier volle Rahmenkanten lesbar. Tatsächlicher Strich-/AA-Umfang passt, logische Zellen/Hit-Tests bleiben unverändert. ZS2-Timing, Vorschau und Gegentastenabbruch bleiben. |
| VS2-NA04 | Miniatur/Palette mit Fassung/Beschriftung in großzügiger Referenz etwas nach unten/links, sichtbar Abstand zum Buchrand. Vier Flächen, UI100/125, beide Ansichten und Save-/Recoverymeldung ohne Überdeckung; sichere Hitflächen und Rückwege. Keine bloße Verkleinerung als Ersatz. |
| VS2-NA05 | Identische Füllungen bei abweichenden X/unbekannt ergeben identische Miniaturpixel. Positive Farb-/Fehlerfüllungen, Vorschau Füllung↔X/Neutralisierung, Rückzug/Abbruch, Undo/Redo, Neustart und vorhandene Albumminiaturen prüfen. Keine X/Punkte/Leer-Ersatzzeichen; X im Hauptraster, Save und History sowie H1/Abschluss unverändert. Keine Lösungskorrektur oder früher Reveal. |

Vier logische Flächen: 1280×720, 1600×900, 1920×1080, 2560×1440; UI100/125,
beide Ansichten, angebotene kleine Arbeitsstufen und Einpassen. F-01/20×20 ist
ein konkret gebundener repräsentativer Leerraumfall; die Chatbezeichnung
„Analyseausgabe 1“ ist keine sicher zugeordnete Datei-ID und wird nicht als solche
behauptet. VS04/VS08/VS09 ergänzen Hinweislast und Rechtecke. Große Bestandsfälle
bleiben einschließlich negativer Befunde erhalten.

Bei geändertem Rasterstrich gezielte Pixeloracles auf den tatsächlichen gezeichneten
Umfang umstellen, nicht einfach sämtliche Rahmenprüfungen entfernen. Bei neuem
Zeilenpitch bisherige 26er-Oracles einzeln auf die gewählten gemeinsamen Slots abbilden.
Miniaturoracles nur für die bewusste X/unbekannt-Projektion ersetzen; eigene Füllungen,
Vorschau, Farben und Spoilerfreiheit bleiben streng. Neue Oracles und dokumentierte
Negativkontrollen gehören in den tatsächlich ausgeführten Produktharness.

## Bereits zugeordnete Oracleänderungen der VS2-Erstlieferung

| Bisheriger Zweck | VS2-Zuordnung |
| --- | --- |
| P12 Miniatur-/Hand-/Rasterpan | Gleichheitsprüfung von Raster/Zellen/History, MMB nur auf überlaufenden Hinweisen. Zweite unabhängige Linie ebenfalls MMB. |
| P12 Zoomschleifen/Resize und P13 Fehler nach Zoom | Endliche gültige Arbeitswünsche mit Fitgrenze; garantierte ausstehende gültige Werkzeugänderung für Flushfehler. |
| P12 historische Sechs-/Vier-Slot-Snapfälle | Explizite Board-Komponente; unveränderte geometrische Snap-/Richtungsoracles. Neue reguläre Reserven separat mit mindestens fünf Zahlen. |
| 500 Aktionen, zehn entfernte Regionen | Unveränderter unabhängiger Zell-/Historyoracle und alle 500 Aktionen; Mini/Pan jetzt negative View-Oracles, Zoom exakt fitbegrenzt. Mehrprozess-Redo bleibt. |
| Z2 Aktionen/Information/Recovery | Entfernte Handauswahl ersetzt durch Füll-/Radierwahl; negative Raster-/Miniaturtransienten, reale MMB-Hinweise, unveränderte Flush-/Recoverymodalität. |
| Z2 native feste Rasterboxen/F02-Hinweisdrag | Vollständige Bounds samt Außenstift und unabhängig berechneter Zellumfang im verfügbaren Board; 14,7px-C1-Drag auf tatsächlich überlaufender F03-Folge. Pending-Werkzeugänderung erzwingt beide Flushfehler trotz wirkungslosem Zoom am Fit. Kontrast-, Tooltip- und Abschlussoracles bleiben streng. |
| RP6 native Miniatur bei nicht zeichnungsfähigem Kleinflächen-Fit | Identischen eigenen Fehlerblock zuvor durch reguläre Mausaktionen auf gültiger Fläche vorbereiten; kleine Fläche zeigt denselben Stand passiv und muss Zell-/Historyeingaben ablehnen. Tatsächlicher Miniaturpixel, alle zehn Bilder je Pilot, Einzel-Undo, Abschluss-/Spoiler- und Erreichbarkeitsprüfungen bleiben. |
| ZV50 167%-Clipping/feste Standardbox | Vollständiger Rahmen bei jeder angebotenen Stufe, endliche Zoomversuche, aktueller Fit statt alter festen Box. Native Vorher-/Nachherdaten benennen die Geometrieänderung. |
| ZS2 72px-Schrift-/X-Komponentenprobe | Expliziter Entwicklerzeichner für räumlichen Pixeloracle; angebotene reguläre 12/24/36px-Darstellung und Timing zusätzlich unverändert streng geprüft. |
| Native partielle X-/historische Snapbilder | Explizite Zeichnerkomponente; keine Behauptung eines regulär angebotenen abgeschnittenen Rasters. |
| Zelltrennung über sämtliche alten Arbeitsstufen | Explizite Komponente des ausgewählten regulären Zeichners bei historischen Stress-Pitches; Komponenten-Pan nur im Testaufbau, kein produktiver Eingabeweg. |
| Exhaustive historische H1-Off/On-Pixelpaare auf Großrastern | Unveränderter strenger Replay auf Basis `fad8853`, separat als `h1-reference-native` gebunden. `vs2_h1_cases.gd` ergänzt 16 neue reguläre Off/On-Paare über vier Flächen, beide UI-Skalen und beide Modi mit demselben unabhängigen Pixeloracle; GP48 prüft zusätzlich alle drei Statusbilder. |
| ZS-Schriftbreite bei winzigem Fit | Reguläre Glyphenüberschneidung verlangt eine echte Platz-/Engewarnung und bleibt als Einschränkung im Bericht sichtbar; historische Komponentenproben behalten ihre strenge Passungsprüfung. |
| GP48/ZS2 Bildschirmgleichheit | Identische eigene Zellen/Fachzustände, stabile Statusgeometrie, vollständiger neuer Rahmen und ausgewählter Font; keine falsche Pixelgleichheit bei geändertem Layout. |
| Historische ZS1-/VS1-Vergleichsoberflächen | Gepinnter Entwickler-Replay von Basis `fad8853`, Quellen/Reports klar als Referenz. Neue reguläre Prüfungen laufen zusätzlich. Keine separaten Studienplayer in Standard-CI. |

Historische Manifeste, Pläne, Proofs, Produktionsreihen und Abnahmen bleiben
unverändert. Vollständige Arbeitsrender werden weiter geprüft und nur bei manuellem
Opt-in komplett hochgeladen. Fachoracles, Zertifikate und RP-Reparaturreplays bleiben.

## Lieferung, Windows-Nachweis und Gates

Aktuelle Ausführung und commitgebundene CI-/Downloadnachweise werden im Draft-PR
gebunden: Head, Basis, Test-Merge, Run/Artefakt, EXE-/PCK-/Bild-/Berichtshashes.
Lokale Entwicklungsproben sind noch keine saubere finale Lieferung.
Die reproduzierbare Downloadprobe ist `tools/vs2_windows_probe.py` mit vollständigem
`--head`, erfolgreichem Produkt-`--run`, neuem externem `--output-dir`, gepinntem
`--engine` und verifiziertem `--cache-dir`. Sie startet beide regulären EXEs ohne
Argumente mit frischem, teilgespieltem und abgeschlossenem Profil. Der tatsächliche
alte Writer stammt aus PR #56, Run `37921979562`, Head `8b762dd9aaf976361cba44e3b25004e09edde348`.
Externe Skripte prüfen anschließend das heruntergeladene eingebettete PCK einschließlich
Ressourceninventur, normalen/maximierten Clientflächen, DPI und UI100/125. SHA-256
bindet auch den externen Diagnosehelfer `tests/vs2_measurements.gd`; dieser wird
zusammen mit sämtlichen Testskripten vom regulären Export ausgeschlossen. Die
PCK-Probe prüft zusätzlich das Fehlen der alten Diagnosemethode im regulären Board.
SHA-256 bindet GitHub-Artefakt, inneres ZIP, EXE-Paar, eingebettetes PCK, Prüfscripte und Bilder.
Die spätere E1-Lieferung ergänzt dieselbe tatsächliche PCK-Probe um N01–N05;
ein Quellskripttest allein belegt die ausgelieferte neue Darstellung nicht.

Die automatisierte Mausereignisprobe ersetzt weder persönliche Bedienabnahme noch Review.
Geometrische Passung bei kleinen oder kollidierenden Glyphen ist kein Komforturteil;
Matrixberichte führen Einschränkungen sichtbar, einschließlich vorhandener Großfälle.
Die sechs Pflichtjobs bleiben `docs`, `product`, `preflight`, `puzzle-production`,
`rp4-windows` und `rp5-repair`. Alte grüne Läufe sind keine neuen E1-Nachweise.

**Offen vor Merge:** N01–N05 beider Teilpakete, aktuelle technische Nachweise,
unabhängiges technisches/visuelles Review des neuen kombinierten Heads, positive
VS2-M01 am regulären heruntergeladenen Windows-Paket und passende ausdrückliche
oder bedingte Mergefreigabe. Das ursprüngliche R1 bleibt historisch abgeschlossen.
Kein Merge, Release, Tag, Branch- oder Benutzerdatenlöschen durch diese Spezifikationspflege.
