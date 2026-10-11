# Zellrendering: Sprite-Atlanten und getrennte Aktualisierung

Stand: 11.10.2026 · Spezifikation 0.1 · fachlich freigegeben, noch nicht implementiert

## Geltung, Befund und Paketstand

Der Eigentümer hat die besprochene Sprite-/Caching-Lösung am 11.10.2026 als
Spezifikation freigegeben. Dieses Dokument enthält die dauerhaften technischen
Entscheidungen; Lieferumfang und Status stehen in [PERF-A / #67](https://github.com/venomenon328/picross/issues/67)
und [PERF-B / #68](https://github.com/venomenon328/picross/issues/68).
Es ergänzt [Zeichensprache und Bewegung](UI_DRAWING_STYLE.md),
[P1](PROTOTYPE_P1.md), [Projektprofil](PROJECT_PROFILE.md) und
[Sidebarintegration](SL65_IMPLEMENTATION.md). Bei Zellrendering, Spriteherstellung,
Cache-/Invalidierungsarbeit und der Performance-Nacharbeit vollständig lesen.

Ausgangsbasis der Spezifikation ist `a83ecf5db0800d198bb870932bf0365341aabb28`
in [PR #66](https://github.com/venomenon328/picross/pull/66), Basis
`e323dcf5c83b085144e61707ef98ecab2bfac39b`. Das ist kein unveränderlicher
Ausführungshead; vor Umsetzung den dann aktuellen Stand prüfen.

**Eigentümerbefund PERF-01:** Auf einem weit ausgefüllten farbigen F-02 / 40×40
laufen Cursor-Hervorhebung und Mehrzellenanimationen ab einer Zoomstufe nach.
Herauszoomen stellt laut Bericht die Flüssigkeit wieder her, normal wie maximiert.
Die Gegenprobe mit abgeschalteten Zellanimationen lässt den Cursor-Nachlauf
weiterhin spürbar bestehen. Eine eventuell geringere Stärke ist ausdrücklich
unsicher und kein gemessener Vorteil.
[Analyse und Quellbindung](https://github.com/venomenon328/picross/pull/66#issuecomment-6107584932).

Die Umschaltung auf detaillierte Füllgeometrie bei 18 Pixeln und das wiederholte
Neuzeichnen ruhender Markierungen sind eine passende Hypothese, noch kein
abschließend profilierter Engpass. Die fraglichen Rendererdateien waren schon
in der integrierten Basis vorhanden; ein Einfluss der neu normalisierten
`overview=false`-Ansicht ist separat zu vergleichen. Standbilder belegen weder
Latenz noch FPS. Die konkrete Eigentümer-EXE ist aus ihnen nicht eindeutig gebunden.

**Abgrenzung:** SL-R01/B-01 ist nach [SL-R02](https://github.com/venomenon328/picross/pull/66#pullrequestreview-5482654673)
am genannten Ausgangshead technisch behoben. Das nimmt diese Performancearbeit
nicht ab. Persönliche SL-M01 und neue PERF-M01 bleiben offen. Weder Atlanten noch
neue Caches, Shader oder Messprogramme sind mit dieser Dokumentation geliefert.

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

Füllung baut kurze Schraffurzüge räumlich auf. X schreibt erst den ersten und dann
den zweiten Zug. Unbeschriebenes Papier bleibt während des aktiven Aufbaus frei;
kein globales Fade, keine bloß bewegten Striche auf schon voller Füllung und keine
alte Gegenmarkierung unter dem neuen Ziel. Endbild, Vorschau und ruhende Zelle
wechseln nicht zwischen verschiedenen Formen. Bei Entfernen bleibt das bisherige
neutrale Auslaufen erlaubt; die bereits entfernte Füllung oder das X erscheint
nicht erneut als Löschanimation.

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

**Ausarbeitungsparameter, keine ungeprüften Produktkonstanten:** etwa 16 Füllvarianten
und 16–24 Zeitbilder je Variante sind die erste Vergleichskonfiguration. Konkrete
Anzahl, X-Varianten, Auflösung und Atlasaufteilung werden in PERF-A anhand realer
Einzelzellen, größerer Farbflächen, Bewegung und Speicherbedarf begründet gewählt.
Kein pauschales Zufallsversprechen, dass benachbarte Zellen niemals gleich aussehen;
auffällige periodische Muster sind visuell zu prüfen. Eine erhebliche gestalterische
Abweichung benötigt eine Entscheidung, kein heimliches Herabsetzen der Qualität.

## PERF-D03: Farbe, Zellinnenfläche und Skalierung

Die Bilder sind farbneutral. Die jeweilige Rätselfarbe wird bei der Darstellung
angewendet; nicht jede komplette Animation für jede Farbe getrennt speichern.
Die bestehende satte Grundfarbe, dunklere Kontur und helle Stiftspuren müssen
getrennt korrekt abbildbar sein, etwa über neutrale Masken/Kanäle und ein kleines
geteiltes Material. Ein einfacher Grauwert-Tint darf keine unerwünschte
Farbverschiebung oder fehlende helle Akzente erzeugen. Format und Material sind
technische Details, aber native Farb-/Alpha-Prüfungen verpflichtend.

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

## PERF-D04: Zeit, Vorschauvorrang und Daten bleiben getrennt

Bildindex aus vergangener Zeit bestimmen, nicht pro gerendertem Bild blind
weiterzählen. Ausgelassene Renderbilder dürfen die Animation nicht verlängern.
Mehr Zwischenbilder sind kein Ersatz für einen flüssigen Renderpfad.

Unverändert gelten ZS-D06–D09:

- Statische abgeschwächte Vorschau mit dem bestehenden 56-%-Wert; Animation erst
  nach sofortigem atomarem Commit. Keine zusätzliche Eingabesperre.
- Setzen/Umwandeln 210 ms je Zelle. Bei `m > 1` wirksamen Setzzellen gilt
  `Delta = min(12 ms, 180 ms / (m - 1))`, bei einer Zelle null; vom tatsächlichen
  Gestenstart zum finalen Abschnittsende. No-ops/geschützte Felder erzeugen keine
  Zeitlücken. Höchstens 390 ms Gesamtfolge. Entfernen sofort und ungestaffelt 120 ms.
- Modell, History, H1/GP48, Save und Abschluss warten nicht auf Bildfolgen.
  Die nächste Eingabe hat Vorrang; kein Animationscallback darf alte Daten herstellen.
- Neue wirksame Vorschau auf einer animierten Zelle beendet deren alten Effekt
  endgültig. Rückzug/Abbruch startet ihn nicht erneut. Umwandlungen verstecken
  die vorherige Markierung auch in einem Cache vollständig.
- Undo/Redo stellt den exakten Stand sofort her. Escape, Fokusverlust, Gegentaste,
  Blattwechsel, Reset, Restore, Informations-/Albumwechsel sowie Zoom/Resize
  behandeln aktive und wartende Effekte nach dem bisherigen Lebenszyklus.
- Ausschalten beendet Effekte sofort und zeigt gültige Endbilder. Einschalten
  betrifft nur künftige Commits. Sitzungsschalter und Save-Schema bleiben wie bisher.

Die Miniatur verwendet weiterhin die vereinfachte, passive, **unanimierte eigene
Füllprojektion**, einschließlich statischer Vorschau. Weder X noch Zwischenbilder,
Lösungskorrekturen oder ein Motivspoiler gelangen in Arbeits-/Albumminiaturen.

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

Bevorzugter erster Herstellungsweg: den bisherigen Stiftzeichner mit gepinntem
Quellstand, festen Identitäten und Zeitpunkten offline ausrendern. Dadurch wird
zuerst der Darstellungsweg statt gleichzeitig die ganze Gestaltung gewechselt.
Gespeicherte Originale, Derivate, Parameter und Herkunft erhalten eine eigene
Bindung. Keine Modell-API und kein Live-Bildgenerator im regulären Spiel.

Das Verbot bloß rasterisierter geometrischer Platzhalter aus #65 betrifft die
**Sidebarrahmen**. Es verbietet nicht das hier ausdrücklich freigegebene Vorabrendern
bestehender **Zellmarkierungen**. Die Rahmenassets und ihre Herkunft werden durch
PERF weder ersetzt noch rückwirkend umgedeutet.

Das neue Manifest bindet mindestens Quell-/Renderfassung, Herstellerparameter,
Varianten-/Framezuordnung, Zeitabbildung, Bildmaße, sichere Innenflächen, Alpha-Hüllen,
Datei-/Pixelhashes und erforderliche Nutzungshinweise. Farb- und Importparameter
gehören zur Prüfung der tatsächlich geladenen Bilder. Im Spielerexport liegen nur
benötigte aktive Laufzeitressourcen, keine Generatoren, historischen Renderer,
Vergleichsgalerien oder Diagnosescripte. Bestehende historische Quellen dürfen für
Entwicklerprüfungen erhalten bleiben.

**Begrenzte technische Ablösung:** ZS-D02/03 und V3-02 bleiben für Stiftoptik,
Variantenstabilität und Lesbarkeit maßgeblich. Die vorherige pro Frame berechnete
Geometrie und deren exakter 18-Pixel-Umschaltpfad sind keine Pflichtarchitektur.
Sie werden durch den gebundenen Bildbestand und dessen skalierte Darstellungsstufen
ersetzt. Endvarianten dürfen aus einem endlichen geprüften Bestand stammen; eine
pixelidentische Reproduktion sämtlicher früher algorithmisch erzeugter Zellbilder
ist nicht verlangt. Innerhalb der neuen Fassung sind End-/Vorschauidentität und
Neustartstabilität dagegen verpflichtend. ZS-D10 wird durch PERF-D05/D07 konkretisiert.

Historische Pläne, Originalbilder, Font-/Rätseldaten, Proofs und frühere Abnahmen
bleiben unverändert. Abgelöste aktuelle Strich-/Pixeloracles gezielt durch
vergleichbar aussagekräftige Prüfungen ersetzen; übrige Regressionen nicht entfernen.

## PERF-D07: Nachweis am tatsächlichen Lastfall

PERF-A fixiert einen reproduzierbaren dicht gefüllten eigenen F02-Stand und dünne
Kontrollzustände, die Eingabesequenzen und den Messplan **vor** dem optimierten
Vergleich. Kein stiller Zugriff auf echte Benutzersaves. Ein synthetisch angenäherter
Laststand wird als solcher bezeichnet und verändert keine Originaldefinition/Proofs.

Native Windows-Vergleiche verwenden dieselbe Maschine und dokumentieren Quellhead,
Basis/Checkout, Export, Treiber/Renderer, Clientfläche normal/maximiert, Monitor-,
Windows- und UI-Skalierung. Gewünschte Zoomstufe und wirksames Zellmaß getrennt
angeben. 16/18/20 px plus ein höherer erreichbarer Wert sind die gezielten
Schwellenfälle; nicht erreichbare Werte werden mit tatsächlichem Fit ausgewiesen,
nicht durch eine versteckte Erweiterung der angebotenen Geometrie erzwungen.

Hover ohne aktive Animation sowie längere Füll-/X-Striche mit Effekten an/aus
messen. F02 dünn/dicht, beide Ansichten, UI100/125 und die beiden Fensterzustände
sinnvoll kombinieren. Bestehende 100×100-Fälle sind ergänzende Regressionen bei
ihrem realen Fit, kein Ersatz für den dicht belegten detaillierten 40×40-Fall.

Zu dokumentieren sind Wiederholungen/Warm-up, Framezeitverteilungen statt nur
Mittelwerte, CPU-Zeichenaufbau und verfügbare Render-/Eingabedaten, aktive Effektzahl,
Invalidierungen und Speicherverhalten. CPU-Dauer, GPU-Dauer und sichtbare Latenz
nicht gleichsetzen. Nicht messbare Größen offen kennzeichnen. Eventuelle technische
Zeitgrenzen vor dem Vergleich anhand des Messplans fixieren; keine nachträgliche
Lockerung und keine unbelegte universelle FPS-Zusage. Ein anderer real gemessener
Engpass wird zusätzlich benannt, nicht passend zur Hypothese verschwiegen.

Strukturelle Tests prüfen den fehlenden Vollwiederaufbau bei Hover/Animation;
gezielte native Zeitbilder und Echtzeitsequenzen prüfen Schraffur, X-Reihenfolge,
Endformidentität, Farbe, Fugen und Prioritätswechsel. Gegenproben erkennen falsche
Varianten, alte Unterzeichnungen, bloßes Fade, Cachefehler und Vollinvalidierung.
Ein einzelner Endzustands-Screenshot oder die reine Dateiexistenz genügt nicht.

Die [aktuelle CI-Policy](CI_POLICY.md) bleibt maßgeblich: vollständige Diffauswahl,
erfolgreiche ausgewählte Jobs und `ci-required`, kompakte statt pauschaler
Screenshotmatrix, höchstens 20 MB technische und 75 MB gesamte Artefaktdaten.
Die Laufzeitpakete brauchen frische reguläre Windows-EXE-Starts und Prüfung der
tatsächlich exportierten PCK-Ressourcen am Lieferhead. Alte Messungen, Renderer-
und Reviewstände sind keine Nachweise für die neue Integration.

## PERF-D08: Pakete, Integration und Abnahme

| Paket | Eigenes Ergebnis | Abhängigkeit |
| --- | --- | --- |
| [PERF-A / #67](https://github.com/venomenon328/picross/issues/67) | Reproduzierbare Ausgangslast und Messplan; geprüfte deterministische Atlanten samt Herstellungs-/Ressourcenvertrag, eigener Sicht-/Negativprüfung und Dokumentation | Vorhandener kombinierter Quellstand; noch kein neuer regulärer Renderer |
| [PERF-B / #68](https://github.com/venomenon328/picross/issues/68) | Reguläre Atlasdarstellung, getrennte Aktualisierung, korrekte Cache-/Effektlebenszyklen, aktuelle native Vorher-/Nachherprüfung und Windows-Lieferung | Gebundene Ergebnisse von A |

Keine getrennte spätere Testphase: Tests und notwendige Dokumentation gehören
jeweils zum Paket. A allein behebt PERF-01 nicht. Keine künstliche weitere
Aufspaltung in eine Reihe von Sprite-, Hover-, Shader- und Test-PRs.

Solange #66 offen ist, sollen A und B als zwei kenntliche, separat beauftragbare
Pakete auf dessen bestehendem Branch/PR geliefert werden. Diese ausdrücklich
beschriebene Ausnahme vom Ein-Paket-pro-PR-Standard hält das neue Eigentümerfeedback
und die abschließende Probe am selben vollständigen Spielerstand zusammen. Die
Spezifikationspflege kann in einem reinen Dokumentations-PR auf dieser Basis liegen;
dessen Quelle muss vor einer Umsetzung übernommen bzw. verbindlich gelesen werden.
Weder der Dokumentations-PR noch A begründen einen vorzeitigen Produktmerge.
Bei verändertem Branch-/Integrationsstand die Zuordnung vor Umsetzung erneut prüfen.

**Vor dem kombinierten Merge erforderlich:** aktuelle technische Nachweise,
getrennter Selbstreview, unabhängiges technisches/visuelles Review und persönliche
**PERF-M01**: kein spürbarer Cursor-Nachlauf im berichteten dichten 40×40-Fall,
flüssiger räumlicher Aufbau an der bisherigen Zoomschwelle, auch Gegenprobe mit
ausgeschalteten Effekten. Sichtprobe beurteilt Variation auf größeren Flächen,
Schärfe/Fugen und unveränderte Sidebar. PERF-M01 kann zusammen mit der offenen
SL-M01 erfolgen; keine neue vollständige Rätsellösung ist verlangt. Die gesonderte
Eigentümer-Mergefreigabe bleibt nötig. Die längere Erprobung #24 ersetzt kein Gate.

Keine neuen Motive, Spielregeln, Wertung, Eingabemodi, Hintergründe, Fonts oder
Sidebarbilder; kein Engine-/Plattformwechsel, Saveformatwechsel, allgemeines
Grafikframework oder Release. **Spezifiziert** ist nicht **umgesetzt**, und
**technisch geprüft** ist nicht **persönlich abgenommen**.
