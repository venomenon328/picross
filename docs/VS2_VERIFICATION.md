# VS2 · reguläre Vollsichtintegration

## Aktueller Nachweisstand · S0 erledigt, V1 technisch geliefert, V2 offen

Stand: 10.10.2026 · R2-B01-Quellenkonsistenz.

[V1-S0 ist abgeschlossen](VS2_V1_S0.md). Lauf `38048159384` auf
`32befbf336013d8fee29fb6ec61981cc867d1b12`, Test-Merge
`38760faec3a1ba01756fc2ff869864a119ee5854`, bestand vor den Layoutänderungen
vollständig einschließlich aktueller VS2-Prüfungen und `ci-required`.
Die ausdrückliche Übernahme der [CI-Policy #63](CI_POLICY.md) repariert nicht
rückwirkend den alten SIGSEGV; dessen Diagnose bleibt historisch gebunden.

**V1/N01/N02/N04 und NA01/NA02/NA04 sind auf `40829b43db6509447863c9d27dbb87dcfaf2a988`
technisch geliefert.** Basis `d7ec4e1e4a29d82b6979537a33868d57732d3713`,
Test-Merge `99362c34a187337e0e92cac8f71c831a08e7f7a4`, erfolgreicher
[Lauf 38053346260](https://github.com/venomenon328/picross/actions/runs/38053346260).
[Review R2](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5479141642)
prüfte V1-Code und verfügbare native Bilder positiv; sein Dokumentationsbefund
R2-B01 wird durch die konsistenten aktiven Status-/Glyphenangaben nachgeführt.
[Implementierung und Prüfweg](VS2_V1_IMPLEMENTATION.md) sowie der PR binden die
304 Matrixfälle, 80 V1-Fokusfälle, sechs Glyphenstreifen, Negativkontrollen und die
native Implementiererprobe des heruntergeladenen Windows-Pakets. Diese alten
Zahlen sind keine neuen Testläufe der reinen Dokumentationsnacharbeit.

**V2/N03/N05, NA03/NA05 und die kombinierte Abnahme bleiben offen.**
Arbeitsbranch `feat/61-regular-full-view`, [Draft-PR #62](https://github.com/venomenon328/picross/pull/62),
Auftrag [#61](https://github.com/venomenon328/picross/issues/61). Die aktuelle
Dokumentationskorrektur implementiert V2 nicht und erteilt keine Mergefreigabe.

Der [vor den Erstvergleichen gebundene Plan](../examples/vs2/plan.json) wurde auf
`4fa23d2` committed. Der separate [V1-Plan](../examples/vs2/v1-plan.json) wurde
vor Layoutarbeit in `06f695f` versioniert. **Eigentümerpräzisierung vom 10.10.2026:**
Der [separate Nachtrag](../examples/vs2/v1-plan-amendment.json) aus `a41cf9b`
nimmt die synthetische Hinweiszahl 100 aus der V1-Abnahme; maßgeblich sind reale
1/11/17/40 ohne die dafür erprobte Sonderbehandlung. Der ursprüngliche Plan und
bestehende Großfallregressionen bleiben unverändert, keine neue Größenvalidierung.

Die historische Erstlieferung `2c332ad688315bfa851f7c0d8642d2ab4ac3709c` auf
`fad885344874534629365917a2ab6a8d311cd3a7` und
[Review R1](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5472592800)
bleiben an ihren damaligen Vertrag gebunden. VS2-E1 ist bestätigte Produktnacharbeit,
keine rückwirkende Umwertung von R1. VS2-M01 hat Rückmeldung mit Änderungsbedarf;
eine vollständige positive persönliche Abnahme liegt nicht vor.

Startblocker VS2-D01 ist erledigt: [PR #56](https://github.com/venomenon328/picross/pull/56)
integriert #53 einschließlich ZS2-N01–N03 auf der historischen Produktbasis.
R3 und positive ZS2-M01/R1-A01 gelten ausschließlich für diesen Vorgänger.
GF-M01/#59 ist nach [abschließender Klarstellung](https://github.com/venomenon328/picross/pull/60#issuecomment-6076039228)
bestanden; der Merge ist `24564dfed3bb9844d151f4c4ec055d051232d16f`.
Das breite frühere VS-M01-Protokoll bleibt persönlich unvollständig und wird
nicht zum neuen Startblocker für V2.

## Basisprüfung A01–A10

Die folgende Zuordnung beschreibt die Erstlieferung und bleibt im nicht durch
VS2-E1 ausdrücklich abgelösten Umfang Regressionspflicht. Keine alte Zahl oder
Abnahme belegt automatisch den späteren neuen Head. Für Auswahl, historische
Vergleichsimporte und Artefaktgrenzen gilt die aktuelle CI-Policy, nicht der
überholte pauschale Vollumfang der Erstlieferung.

| Akzeptanz | Anschluss der Erstlieferung / erhaltener Prüfzweck |
| --- | --- |
| A01/A02 | Reguläre Szene; `vs2_tests.gd`, `vs2_roundtrip.gd`, normaler Windows-Downloadstart. Sammlung, eine Optionswahl, Sitzungsdefault und Abbruch. |
| A03 | Native Viewportevents für Raster-MMB, injizierte obsolete Hand und passive Miniatur; unabhängige Hinweisziele samt Bereichsübertritt. P12 prüft Snap/Abbruch/Nachbarn. |
| A04/A05 | `vs2_gf1_tests.gd`: alle Slotgrenzen ±0,01, Null-/Teilbudget, echte Glyphen/C1/Statusstriche und kontinuierliche Grenzen/Intervalle. `vs2_tests.gd`: 304 reguläre Layoutfälle der Erstlieferung. |
| A06 | Alle neun unveränderten regulären Inhalte plus zehn gebundene technische Fälle über `tests/vs2_scene.gd`; vier Flächen, UI100/125, beide Modi. Zusätzliche echte Eckklicks mit exaktem Undo/Redo, normalem Writer und proportionalem Reveal für alle fünf Dimensionen. Kein Spielerimport. |
| A07 | G1/GP48/H1 und reguläre ZS2-/N01–N03-Suiten; native X/Schraffur 12/24/36 px und gerichtete 17-Zellen-Welle einschließlich Gegenknopf-Abbruch. |
| A08 | Tatsächlicher alter regulärer Prozess schreibt, neuer Prozess liest; neuer Writer → frischer Reader. Schema-1-Validierung bleibt vollständig; P13/500-Aktionen und Recovery bleiben aktiv. |
| A09 | Normales ZIP ohne Studienplayer/-protokolle; tatsächliche PCK-Inventur und native Downloadprobe. Studienreplays sind separat deklarierter Entwicklerbestand. |
| A10 | Normative Quellen, Hilfe und neutrale [Eigentümeranleitung](VS2_OWNER_TRIAL.md); aktuelle ausgewählte Jobs und `ci-required` am jeweiligen Lieferhead/Test-Merge. |

Speicherabbildung: erst vollständige bestehende Validierung durch SaveStore,
danach `hand → fill`, Mittelpunkt statt altem Pan und tatsächliche Zellgröße
`min(gewünschte gültige Arbeitsstufe, Fit)`. `overview=true` bezeichnet Einpassen;
die gewünschte Arbeitsstufe bleibt separat erhalten. Berechnete Bruchteile werden
nicht in `zoom` geschrieben. Der Ansichtsmodus ist ausschließlich Sitzungseinstellung.
Zellen, vollständige History/Redo, Cursor, `undo_used`, Abschluss, Farbe, Radierer
und semantische Reads bleiben erhalten. Studienroot bleibt unberührt. Die zusätzliche
Layoutverschiebung N02 ist keine neue gespeicherte Panposition; N05 keine Zellmigration.

## Kriterien VS2-NA01–NA05 · V1 geprüft, V2 und kombinierte Wiederprüfung offen

Dauerhafter Vertrag: [UI_DRAWING_STYLE.md, VS2-E1](UI_DRAWING_STYLE.md).
VS2-V1 umfasst N01/N02/N04; VS2-V2 N03/N05. Tests und Dokumentation gehören zu
beiden Teilpaketen; das gemeinsame Ergebnis bleibt in PR #62. Vor V2-Vergleichen
einen eigenen endlichen Nacharbeitsplan auf dem tatsächlichen V1-Produktstand mit
konkreten Strichparametern, Erfolgskriterien und gezielten Bildern binden. Keine
Wiederholung der abgeschlossenen VS-Korpusproduktion und kein Umschreiben alter
VS2-/V1-Pläne oder Manifeste.

| Akzeptanz | Erfolg / Gegencheck und tatsächlicher Status |
| --- | --- |
| VS2-NA01 | Auf `40829b4` technisch geprüft: 24 × UI horizontal statt 26, gleicher Fontmaßstab; vertikal 18 × UI. Reale 1/11/17/40 gemäß Eigentümernachtrag, C1/AA, drei Zustände und Marker vollständig und kollisionsfrei. Rasteransicht min(5,n) auch über kontinuierliche Übergänge; Gesamtansicht alle Hinweise; Snap, monotone Bewegung und Leseanker. Im kombinierten V2-Stand erhalten und erneut regressionsprüfen. |
| VS2-NA02 | Auf `40829b4` technisch geprüft: F-01 und geeigneter VS09-Breitenfall ausgewogener samt beiden Hinweis-/Rastertreffern; gemessene Belegungs-/Randbudgets. VS08/VS04 und knappe Fälle sichern GF1, Lesemaßstab und Fit. Keine Leer-Slots, zusätzliche Fitverkleinerung, fehlenden Zahlen oder Rückkopplung. V2-Strichumfang erneut gegen diese Anordnung prüfen. |
| VS2-NA03 | Offen, V2: native 1:1-Bilder von Raster, Miniaturfassung und Palette mit subtiler Scribble-Wirkung. Stabile identitätsgebundene Striche über Neuzeichnen/Seiten/Neustart; kleine Zellen, Fünferkreuzungen, dunkle Füllungen und vier volle Rahmenkanten lesbar. Tatsächlicher Strich-/AA-Umfang passt, logische Zellen/Hit-Tests unverändert. ZS2-Timing, Vorschau und Gegentastenabbruch bleiben. |
| VS2-NA04 | Auf `40829b4` technisch geprüft: ganze Gruppe großzügig (−16,+24) × UI, begrenzter Abwärtsversatz auf knappen Flächen; Buchrandabstand, vier Flächen, UI100/125, G/V und echte Save-/Recoveryzustände ohne Überdeckung. 44/55-px-Trefferflächen/Rückwege erhalten, keine bloße Verkleinerung. Neue V2-Fassungen erneut gegen diese Grenzen prüfen. |
| VS2-NA05 | Offen, V2: identische Füllungen bei abweichenden X/unbekannt ergeben identische Miniaturpixel. Positive Farb-/Fehlerfüllungen, Vorschau Füllung↔X/Neutralisierung, Rückzug/Abbruch, Undo/Redo, Neustart und vorhandene Albumminiaturen prüfen. Keine X/Punkte/Leer-Ersatzzeichen; X im Hauptraster, Save und History sowie H1/Abschluss unverändert. Keine Lösungskorrektur oder früher Reveal. |

Vier logische Flächen: 1280×720, 1600×900, 1920×1080, 2560×1440; UI100/125,
beide Ansichten, angebotene kleine Arbeitsstufen und Einpassen. F-01/20×20 ist
ein konkret gebundener repräsentativer Leerraumfall; die Chatbezeichnung
„Analyseausgabe 1“ ist keine sicher zugeordnete Datei-ID und wird nicht als solche
behauptet. VS04/VS08/VS09 ergänzen Hinweislast und Rechtecke. Große Bestandsfälle
bleiben einschließlich negativer Befunde erhalten.

Bei geändertem Rasterstrich gezielte Pixeloracles auf den tatsächlichen gezeichneten
Umfang umstellen, nicht einfach sämtliche Rahmenprüfungen entfernen. V1s regulären
24er-Pitch und seine Nachweise erhalten; historische 26er-Komponenten bleiben getrennt.
Miniaturoracles nur für die bewusste X/unbekannt-Projektion ersetzen; eigene Füllungen,
Vorschau, Farben und Spoilerfreiheit bleiben streng. Neue Oracles und dokumentierte
Negativkontrollen gehören in den tatsächlich ausgeführten Produktharness.

## Historische Oraclezuordnung der VS2-Erstlieferung

Die folgende Tabelle bewahrt die damalige Zuordnung. Sie fordert keine historische
Galerieproduktion im aktuellen Standardlauf; #63 ersetzt deren Erzeugungs- und
Uploadweg, nicht die weiterhin relevanten aktuellen Fachoracles.

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
unverändert. Aktuell gelten Änderungsauswahl, begrenzte technische Evidenz und
`ci-required`; historische Vergleiche nur als eigener ausdrücklicher Diagnoseauftrag.
Fachoracles, Zertifikate und relevante RP-Reparaturreplays bleiben.

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
V1 hat diese tatsächliche PCK-Probe um N01/N02/N04 ergänzt. V2 muss N03/N05 am
neuen heruntergeladenen kombinierten Paket nachweisen; ein Quellskripttest allein
belegt die ausgelieferte neue Darstellung nicht.

Die automatisierte Mausereignisprobe ersetzt weder persönliche Bedienabnahme noch Review.
Geometrische Passung bei kleinen oder kollidierenden Glyphen ist kein Komforturteil;
Matrixberichte führen Einschränkungen sichtbar, einschließlich vorhandener Großfälle.
Die übernommene [CI-Policy #63](CI_POLICY.md) verlangt Änderungsauswahl und
`ci-required`. Für den breiten PR auf `40829b4` waren alle sechs Fachjobs gewählt:
`docs`, `product`, `preflight`, `puzzle-production`, `rp4-windows`, `rp5-repair`.
Für neue Heads ist die tatsächliche Auswahl verbindlich. Alte grüne Läufe sind
keine neuen V2-Nachweise; reine Dokumentchecks beweisen keine Produktänderung.

**Offen vor Merge:** V2/N03/N05 und kombinierte aktuelle technische Nachweise,
unabhängiges technisches/visuelles Review des neuen kombinierten Heads, positive
VS2-M01 am regulären heruntergeladenen Windows-Paket und passende ausdrückliche
oder bedingte Mergefreigabe. R1 und der technische V1-Anteil von R2 bleiben
commitgebunden; die R2-B01-Dokumentationskorrektur wird im PR separat nachgeprüft.
Kein Merge, Release, Tag, Branch- oder Benutzerdatenlöschen durch diese Nacharbeit.
