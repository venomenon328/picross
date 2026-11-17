# Zellrendering · Atlasressourcen und getrennte Aktualisierung

## Geltung und Zuständigkeit

Dieser Vertrag besitzt Ressourcen-, Varianten-, Farb-/Alpha-, Skalierungs- und
Cachegrenzen des regulären Zellrenderers. Die Regeln im aktuellen Git-Stand
sind der Fachvertrag. Konkrete Messungen, Review und persönliche Wahrnehmung
werden am jeweiligen Produkt-Head im Issue/PR nachgewiesen.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Sichtbare Stift-/X-Optik, Vorschau und Animationstiming | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md) |
| Spielzustand, Eingabe, History und Save | [P1](PROTOTYPE_P1.md) |
| Cursor-/Hinweiskontext | [CLUE_INTERACTION](CLUE_INTERACTION.md) |
| Aktuelle Atlasdaten, Ressourcenbytes und Hashes | [cell_atlas_reference.json](../../tools/cell_atlas_reference.json) |
| Gewählte Prüfungen und akzeptierte Lücken | [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md) |

## N70-HIST-01 · Aktive Referenz statt Herstellungsreplay

Die aktuelle Ressourcenreferenz ist von historischen Herstellerarchiven
unabhängig. Alte Atlasherstellung, A-/B-Ausgangsmessungen und Vergleiche werden
nicht für neue Arbeit rekonstruiert. Aktive Ressourcen, Renderingverträge und
begründete Regressionen bleiben prüfbar. Frühere PERF-A/B-Lieferungen sind
historische Nachweise, keine zusätzlichen aktuellen Gatelisten.

## PERF-D01: Gemeinsamer bildbasierter Markierungsbestand

Die reguläre Darstellung von Füllungen und X verwendet vorbereitete transparente
Sprite-/Atlasressourcen für Animation **und** ruhende Markierungen. Nur die aktive
Animation auszutauschen, während fertige Füllungen beim Hover weiter geometrisch
neu aufgebaut werden, erfüllt das Ziel nicht.

| Darstellungszustand | Gemeinsame Bildquelle |
| --- | --- |
| Statische Ziehvorschau | Endbild der gewählten Variante, gemäß ZS-D06 abgeschwächt |
| Noch wartendes Ziel eines übernommenen Strichs | Dasselbe abgeschwächte Endbild, bis der aktive Schreibvorgang beginnt |
| Aktive Schreibanimation | Zeitabhängiges Zwischenbild dieser Variante ohne volle Unterzeichnung |
| Ruhende Markierung | Exakt deren Endbild, mit dem vereinbarten Endfarb-/Deckungsverhalten |

Schraffuraufbau, Reihenfolge der X-Züge, freie unbeschriebene Flächen und
Neutralisierung folgen [ZS-D02/D03/D06/D07](UI_DRAWING_STYLE.md). Endbild,
Vorschau und ruhende Zelle wechseln nicht zwischen verschiedenen Formen.

## PERF-D02: Stabile Varianten statt Neuwürfeln

Mehrere Varianten unterscheiden sich auch im **fertigen** Aussehen: leichte
Kontur-, Schraffurwinkel-, Lage- und Strichunterschiede bei gleicher Lesbarkeit.
Verschiedene Animationen zum identischen Endquadrat genügen nicht. Die gemeinsame
Stiftoptik, ruhige geschlossene Grundfläche und sichtbare Zelltrennung bleiben.

Die Auswahl wird aus stabiler Rätsel-/Zellidentität und dokumentierter Renderfassung
abgeleitet. Innerhalb derselben Fassung bleibt sie nach Neuzeichnen, Farbwechsel,
Zoom, Undo/Redo und Neustart identisch. Nicht aus Uhrzeit, Mausposition, aktuellem
Fortschritt oder jedem neuen Frame würfeln. Füllfarbe und Variantenidentität sind
getrennt. Eine neue Variante wird nicht in jedem Save gespeichert; das Schema
bleibt unverändert. Bei späterem Austausch des Variantenbestands dessen Version
und sichtbare Auswirkung dokumentieren, statt alte Pixelgleichheit zu behaupten.

Die aktive Renderfassung `pencil-atlas-1` verwendet 16 Varianten und 24
Zeitbilder je Variante für Füllung und X, verteilt auf je drei Detailstufen.
Diese aktuellen Werte und Bildmaße sind in `tools/cell_atlas_reference.json`
gebunden.
Kein pauschales Zufallsversprechen, dass benachbarte Zellen niemals gleich aussehen;
auffällige periodische Muster sind visuell zu prüfen. Eine erhebliche gestalterische
Abweichung benötigt eine Entscheidung, kein heimliches Herabsetzen der Qualität.

## PERF-D03: Farbe, Zellinnenfläche und Skalierung

Die Bilder sind farbneutral. Die jeweilige Rätselfarbe wird bei der Darstellung
angewendet; nicht jede komplette Animation für jede Farbe getrennt speichern.
Die bestehende satte Grundfarbe, dunklere Kontur und helle Stiftspuren müssen
getrennt korrekt abbildbar sein, etwa über neutrale Masken/Kanäle und ein kleines
geteiltes Material. Ein einfacher Grauwert-Tint darf keine unerwünschte
Farbverschiebung oder fehlende helle Akzente erzeugen. Format und Material sind technische Details; Farb-/Alpha-Verhalten muss
am tatsächlich geladenen Renderer prüfbar sein.

Bilder werden in die tatsächlichen Zellinnenflächen abgebildet. Logische Zellen,
präzise Treffer, Fugen, Fünferlinien und Clipping bleiben unverändert. Nicht das
vollständige Zellrechteck samt transparentem Padding beliebig skalieren und dabei
die bisherige Trennung verlieren. Bildauflösung und sichere Innenbereiche sind
auf kleine, mittlere, größte tatsächlich angebotene und nichtganzzahlige
Fitgrößen auszulegen. Eine klar zugeordnete vereinfachte Kleindarstellung ist
zulässig; keine Rückkehr zum teuren Vollaufbau ab derselben Schwelle.

Atlasränder, Transparenz, Filterung und gegebenenfalls Auflösungsstufen müssen
Nachbarframe-Einstreuungen, Säume und zugelaufene Fugen verhindern. Zwischenbilder
und Endbild derselben Darstellungsstufe passen zusammen. Keine harte neue
Zoomsperre, kleinere Hinweisfont oder geringere Raster-/Hinweiskapazität zur
Kaschierung des Performanceproblems.

### PERF-A2 / PERF-B: Vertrag der Renderfassung `pencil-atlas-1`

Die folgenden Parameter gehören zur aktiven Renderfassung. Sie konkretisieren
PERF-D02/D03; sie schreiben keinen historischen Hersteller oder früheren
prozeduralen Zeichner als aktuelle Architektur vor. Datei-, Pixel- und Importhashes
bleiben ausschließlich in der oben verlinkten Ressourcenreferenz gebunden.

| Tatsächliches Zellmaß | Detailstufe | Logische Referenzkante | Bildkante ohne Atlaspadding |
| --- | --- | --- | --- |
| `< 18 px` | `small` | 16 px | 32 px |
| `18 px` bis einschließlich `36 px` | `medium` | 24 px | 64 px |
| `> 36 px` | `large` | 72 px | 96 px |

Die sechs RGBA8-Atlanten sind neutrale Koeffizientenmasken. R trägt den Anteil
der Rätselfarbe einschließlich dunkler Kontur, G die weißen Stiftspuren und A
die Deckung. Das gemeinsame Material bildet
`Ausgabe.rgb = Rätselfarbe.rgb × Maske.r + Maske.g` und
`Ausgabe.a = Darstellungsalpha × Maske.a`. Eine bloße Grauwertmultiplikation
erhält diese Farbwirkung nicht.

Die Füllinnenfläche wird auf die tatsächliche Zelle mit **2 px Abstand je Rand**
abgebildet; das X verwendet die gesamte Zellbox. Transparenter Rand der Quelle
und 2 px Atlaspadding je Seite dürfen diese Fuge nicht mitskalieren. Bei einer
Innenkante von höchstens null Pixeln entfällt die Füllung; das X wird weiterhin
maßstäblich gezeichnet. Kleine Füllungen verwenden bewusst die einfache
Rechteckform. Verlustloser Import, lineare Filterung, kein Repeat, keine Mipmaps
und keine nachträgliche Alpharanderweiterung erhalten die Masken und Framegrenzen.

Die Variantenidentität ist der SHA-256 der UTF-8-Zeichenfolge
`Renderfassung\nRätsel-ID\nRevision\nx\ny`, ohne abschließenden Zeilenumbruch;
Revision und Zellkoordinaten sind dezimale Ganzzahlen. Die ersten acht
Hexadezimalstellen als vorzeichenloses 32-Bit-Wort modulo Variantenanzahl wählen
die Variante. Zoom, Farbe, History und Uhrzeit sind keine Hashbestandteile.

Zeitbild 23 ist das Endbild. Für verstrichene Mikrosekunden `t` und die nach
[ZS-D07](UI_DRAWING_STYLE.md#zs-d07-commit-und-gerichtete-effekte) festgelegte
Setz-/Umwandlungsdauer `D` in Mikrosekunden gilt
`frame = clamp(floor(max(0, t) × 23 / D), 0, 23)`. Die Dauer in der
Ressourcenreferenz muss dieser Darstellungsnorm entsprechen; sie ist kein
zusätzlicher Timingparameter. Ruhende Markierung, Vorschau und wartendes Ziel
verwenden dasselbe Endbild ihrer Variante.

## PERF-D04: Zeit, Vorschauvorrang und Daten bleiben getrennt

Der Bildindex wird aus vergangener Zeit bestimmt; nicht pro gerendertem Bild
blind weiterzählen. Ausgelassene Renderbilder verlängern die Animation nicht.
Mehr Zwischenbilder ersetzen keinen flüssigen Renderpfad.

Vorschautransparenz, Startfolge, Dauer, Abbruch-/Vorrangregeln und Sitzungsschalter
stehen ausschließlich in [ZS-D06–D09](UI_DRAWING_STYLE.md). Der Renderer folgt
sofort dem bestätigten Modell und darf weder auf Effekte warten noch durch alte
Callbacks Daten herstellen. Umwandlungen verstecken Gegenmarkierungen auch in
Caches vollständig. Neue Vorschau beendet überholte Effekte dauerhaft.
Miniaturen verwenden die eigene vereinfachte Füllprojektion aus ZS-D05 und keine
Animationszwischenbilder.

## PERF-D05: Unabhängige Ebenen und begrenzter Wiederaufbau

Drei getrennt aktualisierbare Verantwortungen sind verbindlich:

1. Ruhende Füllungen und X.
2. Statische Gestenvorschau und aktive Übergänge.
3. Cursor-Hervorhebung der aktuellen Zeile/Spalte.

Die konkrete Zahl der Canvas-Objekte, ein begrenzter Chunkcache oder die
Wiederverwendung nativer Zeichenbefehle sind Implementierungsdetails. Ein riesiges
Gesamtraster-Bitmap und ein eigener permanent laufender Animationsknoten/Timer
pro Zelle sind keine Vorgaben. Gemeinsamer Atlas, geteilte Ressourcen und ein auf
aktive Effekte begrenzter Ablauf sind die vorgesehene Richtung.

**Reine Cursorbewegung darf nicht den gesamten ruhenden Markierungsbestand im
Skript neu aufbauen. Ein Animationstakt darf nicht alle fertigen Füllungen/X
geometrisch neu berechnen.** Auch Raster-/Hinweis-, UI-, Miniatur- und Analysepfade
sind auf unnötige Invalidierung zu prüfen. Ein Atlas allein beweist diese Trennung
nicht; die strukturelle Gegenprobe muss eine absichtlich wieder gekoppelte
Vollinvalidierung erkennen können.

Die Ebenenreihenfolge erhält die heutige Lesbarkeit: Markierungen, Hervorhebung,
Raster/Fünferlinien, Hinweise und Vorschau verdecken einander nicht unzulässig.
Betroffene Cachebereiche werden bei Commit, Umwandlung/Vorschau, Rückzug/Abbruch,
Undo/Redo und Änderungen von Ansicht, Zoom, UI-Skalierung oder Session korrekt
aktualisiert. Beim Sprung in den Endzustand darf kein altes Bild darunter bleiben.
Kleine gezielte Aktualisierungen bei echten Zustandswechseln sind zulässig;
verlangt wird keine kostenlose Darstellung oder das Ausbleiben sämtlicher GPU-Arbeit.

Texturen und Materialien werden geteilt, nicht pro Hover neu erzeugt oder geladen.
Cachegröße und Ressourcenlebensdauer sind begrenzt; wiederholte Zoom-/Blattwechsel
führen nicht zu stetigem Speicherwachstum. Im Ruhezustand endet der Effekttakt.
Caches sind transiente Darstellung, keine Save-/Historydaten.

## PERF-D06: Offlineherstellung, Ressourcen und gezielte Ablösung

Die sechs fertigen PNGs unter `game/art/cells/` bleiben unverändert. Ihre
Herstellung aus dem früheren Stiftzeichner ist historisch abgeschlossen und im
[Entwicklungsarchiv](../history/README.md) commitgebunden erreichbar. Kein
Generator, alter Zeichner oder Herstellerarchiv ist Voraussetzung aktueller Tests.
Keine Modell-API und kein Live-Bildgenerator im regulären Spiel.

Das Verbot bloß rasterisierter geometrischer Platzhalter aus #65 betrifft die
**Sidebarrahmen**. Es verbietet nicht das hier ausdrücklich freigegebene Vorabrendern
bestehender **Zellmarkierungen**. Die Rahmenassets und ihre Herkunft werden durch
PERF weder ersetzt noch rückwirkend umgedeutet.

Die aktuelle Ressourcenreferenz bindet Renderfassung, Varianten-/Frameanzahl,
Zeitparameter, Bildmaße, Datei-/Pixelhashes, dekodiertes Speicherbudget und Imports.
Farb-/Alpha-/Innenflächen-/Filterverträge werden am tatsächlich geladenen Renderer
geprüft. Nutzungshinweise bleiben erhalten. Im Spielerexport liegen nur benötigte
aktive Laufzeitressourcen, keine Generatoren, historischen Renderer, Vergleichs-
galerien oder Diagnosescripte. Historische Quellen liegen im gebundenen Archiv.

**Begrenzte technische Ablösung:** ZS-D02/03 und V3-02 bleiben für Stiftoptik,
Variantenstabilität und Lesbarkeit maßgeblich. Die vorherige pro Frame berechnete
Geometrie und deren exakter 18-Pixel-Umschaltpfad sind keine Pflichtarchitektur.
Sie werden durch den gebundenen Bildbestand und dessen skalierte Darstellungsstufen
ersetzt. Endvarianten dürfen aus einem endlichen geprüften Bestand stammen; eine
pixelidentische Reproduktion sämtlicher früher algorithmisch erzeugter Zellbilder
ist nicht verlangt. Innerhalb der neuen Fassung sind End-/Vorschauidentität und
Neustartstabilität dagegen verpflichtend. ZS-D10 wird durch PERF-D05/D07 konkretisiert.

Historische Pläne, Originalbilder, Font-/Rätseldaten, Proofs und frühere Abnahmen
bleiben unverändert. Änderungen an Regressionen folgen dem aktuellen Paket-/Modulvertrag;
explizit akzeptierte Abdeckungslücken sind dort maßgeblich.

## PERF-D07: Nachweis am tatsächlichen Lastfall

Renderer-/Cacheänderungen benötigen zum tatsächlichen Risiko passende
commitgebundene Messungen. Ein dichter synthetischer Farbstand wird als echte
Transaktion aufgebaut; keine echten Nutzersaves. Historische F02-/100×100-Proben
sind Vergleichsbelege und keine aktuelle Pflichtmatrix. Fitgrenzen werden für
Messungen nicht erweitert; Zoomwunsch und tatsächliches Zellmaß bleiben getrennt.

Ein Messplan nennt Last, Zoom-/Detailübergänge, Hover ohne Animation, längere
Füll-/X-Striche mit Effekten an/aus, Wiederholungen/Warm-up, Framezeitverteilungen,
CPU-Zeichenaufbau, verfügbare Render-/Eingabedaten, Effektzahl, Invalidierungen und
Speicherverhalten. CPU-/GPU-Dauer und sichtbare Latenz sind verschiedene Größen.
Nicht messbare Werte bleiben als solche ausgewiesen. Etwaige technische
Zeitgrenzen werden vor dem Vergleich festgelegt; keine nachträgliche Lockerung
oder unbelegte allgemeine FPS-Zusage. Ein abweichender realer Engpass wird benannt.

Strukturelle Gegenproben müssen eine wieder gekoppelte Vollinvalidierung erkennen
können. Native Zeitbilder bzw. Echtzeitsequenzen können Schraffur, X-Reihenfolge,
Endformidentität, Farbe, Fugen und Prioritätswechsel nachweisen. Dateiexistenz oder
ein einzelnes Endbild genügen dafür nicht. Bei gewählter nativer Windowsprüfung
werden Head/Basis/Checkout, tatsächlicher Export/PCK, Treiber/Renderer,
Clientfläche und Skalierung gebunden.

Aktuelle Modulauswahl und Wiederholungsumfang folgen [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md)
und [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md). Die dort ausdrücklich akzeptierten
kleineren Stichproben behaupten keine gleiche Abdeckung historischer Vollmatrizen.

## PERF-D08: Integration und Abnahme

PERF-A / #67, PERF-B / #68 und N70-HIST-01 bezeichnen ihre ursprünglichen
Entscheidungen. Technische Messung und persönliche Wahrnehmung von Cursor-
Nachlauf, flüssigem Aufbau, Variation, Schärfe/Fugen sind getrennte Nachweise.
Aktuelle Gates folgen dem konkreten Auftrag und Issue-/PR-Stand; frühere
Sonderpaket-/Mergefolgen werden nicht erneut als Arbeitsanweisung geführt.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#67](https://github.com/venomenon328/picross/issues/67), [#68](https://github.com/venomenon328/picross/issues/68), [PR #66](https://github.com/venomenon328/picross/pull/66) und [N70-HIST-01 / PR #71](https://github.com/venomenon328/picross/pull/71#issuecomment-6111613992).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CELL_RENDERING.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
