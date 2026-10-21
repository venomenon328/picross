# Zeichnerische Spieloberfläche und Zellanimationen

**HZ · 21.10.2026, HZ-A/B integriert und abgenommen; HZ-C spezifiziert, noch nicht implementiert:**
[Handgezeichnete Bedienoberfläche](HAND_DRAWN_UI.md) ist der Detailvertrag für
Tidy Hand als normale UI-Schrift bei erhaltenen Überschriften, organischere Karten-/Button-/Dropdownrahmen,
vollständig gezeichnete offene Menüs und die gesamte Piktogrammfamilie.
Er ersetzt gezielt Plex-Standardtexte gemäß HZ-A-FONT02
und verstärkt kleine UI-Konturen. Raster, Zellen, Hinweise und die drei großen
SL-Rasterrahmen behalten ihre Verträge; historische Auswahl-/Lieferbelege bleiben.
HZ-A/B sind über [PR #288](https://github.com/venomenon328/picross/pull/288)
und [PR #289](https://github.com/venomenon328/picross/pull/289) integriert und im
geschlossenen [Issue #284](https://github.com/venomenon328/picross/issues/284)
abgenommen. [HZ-C / #294](https://github.com/venomenon328/picross/issues/294)
ergänzt die am 21.10.2026 freigegebene optische Ausrichtung und den begrenzten
Größenvergleich gemäß HZ-D07; diese Spezifikation ist noch nicht implementiert.

**KU / #244, integrierte Ausgangsbasis für HZ:** KU-A und KU-B sind über
PR #254/#255 integriert; [KU-A](KU_VERIFICATION.md) und
[KU-B](KU_B_VERIFICATION.md) behalten ihre getrennten Nachweise.
Die offenen persönlichen Abnahmen auf `main` stehen weiterhin im Issue.
Die Spezifikation wurde am 18.10.2026 freigegeben:
[Katalogdarstellung](CATALOG_PRESENTATION.md) führt in KU-A die gezielte neue
Zeichnung und Anordnung: ein gemeinsamer warmer Papierstreifen mit subtil
unregelmäßiger Kontur, Größe links, gefüllter Schwierigkeitskreis und vollständiger
dunkler Name mittig, größere Stifte rechts. Alle drei Angaben stehen in einer
Zeile ohne Einzelkästchen. Kreise verwenden die fünf bestehenden Farben;
fehlende Einstufung erscheint neutralgrau mit „Nicht eingestuft“. Die sichtbare
Ziffer und sämtliche Schwierigkeitstooltips einschließlich nativer Ersatztooltips
entfallen; Modus- und Resettooltip bleiben. Der dunkle Monostift wird ohne
Farbprobe zentriert, das Farbsymbol bleibt eine aufgefächerte Dreiergruppe.

Entwurfsstarts sind 28–32 logische Pixel für Modussymbole, 12–14 für Kreise und
260–280 für die gemeinsame Kartenbreite. Tatsächliche Volltext-/Symbolmaße und
Abstände bei UI 100/125 % bestimmen das Ergebnis; keine bereits gemessene
Fitgarantie, keine Textkürzung oder Schriftverkleinerung als Breitenersatz.
Der Status steht als Symbol mit „Neu“, „Begonnen“ oder „Gelöst“ rechts in der
Fußzeile neben „Blatt NN“. Die Schriftrolle wird durch HZ erweitert; große proportionale Bildfläche,
lokale Polygon-/Revealglättung, Spoiler-, Reset- und Recoverygrenzen bleiben.
KU-B ergänzt die [Sortierbedienung](CATALOG_SORTING.md) neben dem Kategorienfilter.
Statische Kreise und Stifte verändern weder Zell-/Hinweisrendering noch Animationen.
Paketumfang und spätere Abnahmen stehen im
[Gesamtissue #244](https://github.com/venomenon328/picross/issues/244).

**KE / #233, mit PR #234 integrierte Ausgangsbasis für KU:**
Die damalige [Katalogdarstellung KE-D01–D05](CATALOG_PRESENTATION.md) ergänzte
Papieretikett, Stift-/Statuspiktogramme und ein eigens gezeichnetes Graphitfragezeichen im
Katalogbildraum. KE verwendete Plex für Metadaten und Bakso für Motivüberschriften;
HZ-A-FONT02 ersetzt Standardtexte durch die bereitgestellte Tidy-Hand-Datei
und erhält die bestehenden Überschriftrollen.
Subtil unregelmäßige Konturen, zurückhaltende Schraffur, keine Animation.
Gezielte Modus-/Schwierigkeits-Tooltips hatten den bestehenden Resettooltip ergänzt;
der Ganzkarten-Tooltip blieb entfallen. KE-N1 akzentuierte nur die
Schwierigkeitsziffer in gedecktem Grün–Oliv/Ocker–Rost–Rot; Name und
„Nicht eingestuft“ blieben dunkel. KU-A ersetzt diese Ziffer, Schwierigkeitstooltips,
Monochrom-Farbprobe und Metadaten-/Statusanordnung; historische KE-N1-Belege bleiben
unverändert. Lokale Polygonkantenglättung bleibt für Modusstifte und Begonnen-Stift.
Verdiente Katalog-/Abschlussbilder werden vor linearer Anzeige gezielt auf das
Anzeigemaß verkleinert, ohne globale
Glättung oder Änderung eigener Miniaturen.

**KK / #174** erweitert die vorhandene Bakso-Rolle gezielt um Motivüberschriften
und `???` in Katalogkarten. Feste zweizeilige Titel, begrenzte Metadaten, gleicher
proportionaler Bildraum und feste Fußzeile ersetzen die inhaltsabhängigen KB-Höhen.
Öffnen erfolgt über die Karte, Reset allein oben rechts mit reservierter Fläche,
10 × UI Innenrand und dem gemeinsamen BookButton/reset.svg. Treffer bleiben 44/55 px.
Speicherdiagnose und Backupaktionen nutzen bei Bedarf den festen Bildraum.
Der Kacheltooltip entfällt, auch bei gekürzten Labels; Resettooltip und übrige
Tooltips bleiben. KK änderte keine Font-/Assetbytes oder Zell-/Hinweisgestaltung.
Die anschließende HZ-B-Lieferung hat gezielt die aktive Iconfamilie revidiert,
nicht die Originalfonts.
[Prüfzuordnung](KK_VERIFICATION.md).

**Aktive Hinweisgeometrie HC / #92:** [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md)
ersetzt ausschließlich ältere Chalkboard-/24/18-Aussagen für reguläre Hinweise.
Delight Coffee, zellabhängiger Schriftgrad und gemessene gemeinsame Slots gelten
einschließlich Fit, G/V, Drag/Snap und Status. Normale UI-Fontrollen folgen HZ;
C1 und die spezialisierte Zahlen-/Markerrolle bleiben.

## Zellrendering-Vertrag · PERF

Für Zellbilder, Varianten, Zeitabbildung und spätere Cachearbeit gilt zusätzlich
[CELL_RENDERING, PERF-D01–D08](CELL_RENDERING.md). ZS-D02/03 und V3-02 bestimmen
weiterhin Stiftoptik und Lesbarkeit; die pro Frame berechnete Geometrie und der
exakte frühere 18-px-Pfad sind gemäß PERF-D06 keine Pflichtarchitektur.
[PERF-A](PERF_A_IMPLEMENTATION.md) dokumentiert die historische Mess-/Atlasgrundlage;
aktuelle Regressionen folgen N70-HIST-01 in CELL_RENDERING und CI_POLICY.
[PERF-B / #68](PERF_B_IMPLEMENTATION.md) integriert die gebundenen Atlanten und
getrennte Zeichenebenen. Vorschau, 210/120-ms-Vertrag, atomarer Commit und Miniatur bleiben.

## Aktueller Vertrag · Sidebar #65

PR #62 / #61 ist seit 10.10.2026 in main `e323dcf5c83b085144e61707ef98ecab2bfac39b` integriert. Der zusammenhängende Stand A+B ist über PR #66 in main integriert; [SL-Umsetzung und Prüfzuordnung](SL65_IMPLEMENTATION.md) ist für die Sidebar maßgeblich. Frühere Draft-/Mergegate-Aussagen zu #62 und dessen V1/N04-Versatz, V3-05/V3-06-Leiste und prozedurale Gruppenfassungen sind historische Paketstände. Sie gelten nicht als aktuelle Bedienanweisung.

Aktuell: genau sechs Aktionen in 2×3 (Füllen/Radieren, Undo/Redo, Minus/Plus), ohne Einpassen-/Arbeitsgrößenaktion oder „Dein Stand“. Drei transparente gezeichnete Rahmen ersetzen die alten Fassungen; Miniatur, Koordinaten, Palette und Werkzeuge teilen die Mittelachse. Die interne Vollsichtgrenze, Optionsansichten G/V, Raster-/Hinweisbudgets und Albumminiaturen bleiben. Nach vollständiger unveränderter Schema-1-Validierung wird `overview=false`; gültiger Zoomwunsch, Inhalt, History/Redo und Recoverygrenzen bleiben erhalten. Neue Saves schreiben Schema 1 mit `overview=false`. SL-R02 bestätigt B-01 am Ausgangshead a83ecf5 technisch; kombinierte Nachweise und Eigentümerbestätigung sind im integrierten PR #66 gebunden; kein Release. Historische Prüfpläne/-berichte bleiben unverändert.

Stand: 11.10.2026 · Spezifikation 0.8 · VS2/Sidebar/PERF-A/B integriert

V1-/V2-/V3-Prüfstatusangaben innerhalb der Fachfortschreibung beschreiben ihre
damaligen Paketstände. Die kombinierte Integration/Abnahme steht in PR #62/#66;
sie ist kein erneut offenes Gate. Frühere einleitende Liefermeldungen bleiben im
[gebundenen Vorgänger](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/docs/UI_DRAWING_STYLE.md) erreichbar.

## 1. Auftrag, Quellen und Status

Der Eigentümer hat am 07.10.2026 die besprochene Weiterentwicklung des Buchdesigns
als Spezifikation freigegeben und ihre Übernahme in Issues und Repository-Dokumente
beauftragt. Die Bewegungsregel bleibt verbindlich: Die Vorschau während einer
Zellgeste bleibt statisch und heller beziehungsweise transparenter; Zellanimationen
beginnen erst beim tatsächlichen Anwenden des Strichs. Die frühere Empfehlung,
bereits während des Ziehens zu animieren, ist ausdrücklich verworfen.

Dieses Dokument beschreibt die dauerhaften Gestaltungs- und Darstellungsverträge.
[ZS-1](https://github.com/venomenon328/picross/issues/52) lieferte die native
Vergleichsprobe und konkrete Auswahl, [ZS-2](https://github.com/venomenon328/picross/issues/53)
deren reguläre Integration. Die aktuelle Vollsichtintegration mit VS2-E1 steht in
[Issue #61](https://github.com/venomenon328/picross/issues/61). Die Pakete gehören zu
[Zieldesign #21](https://github.com/venomenon328/picross/issues/21);
[Z3/#24](https://github.com/venomenon328/picross/issues/24) bleibt die anschließende
längere Spielerprobung. Paketstatus, Lieferhead, Nachweise und Abnahme stehen in den
Issues/PRs. Spezifikationsfreigabe ist weder Produktimplementierung noch Mergefreigabe.

Historische ZS-Ausgangsbasis ist main ec99954268f1ad959d9ea779dbbd9e28edf7d8fa
mit integriertem Z2, GP-48, ZV-50 und RP-6. Vor einer späteren Ausführung den dann
aktuellen Stand prüfen. [AGENTS.md](../AGENTS.md),
[lokaler Workflow](dev-rules/WORKFLOW.md), [Projektprofil](PROJECT_PROFILE.md),
[Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md),
[P1-Vertrag](PROTOTYPE_P1.md) und [aktive Z2-Auswahl](Z2_SELECTION.md) bleiben
Pflichtquellen im jeweiligen Geltungsbereich.

[Eigentümerentscheidung ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659)
konkretisiert die Auswahl: Stiftfüllung und kurzes Timing sind gewählt. N01–N06
ersetzen die offene Tinte-/Stiftwahl, frühere Fraunces-Hinweiskandidaten, bloßes Fade
und zusätzliche Rand-UI. R1 bleibt an `4ae4f5a20273808f99d257a3812da86d72307a5f`
gebunden. [Fontinput](ZS1_FONT_INPUT.md): beide Original-TTFs samt Nutzungshinweisen durch
[ZS1-E2](https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344)
für die beauftragte Studienlieferung akzeptiert; zusätzliche Lizenztexte sind kein Startblocker.

[Eigentümerentscheidung ZS1-E3](https://github.com/venomenon328/picross/pull/55#issuecomment-6043750653)
wählt **Chalkboard Regular** als Hinweisfont und reduzierte die gemeinsame horizontale
Slotweite der Zeilenhinweise links vom Raster auf **26 logische Pixel bei UI 100 %**
(UI-skaliert). Die Spaltenhinweise blieben bei 18 logischen Pixeln. Der Eigentümer
hat die Mergefreigabe ausdrücklich vor die kombinierte Sichtprüfung gezogen: Die
visuelle Gesamtprüfung wurde anschließend auf `main@985cf08e` erfolgreich
abgeschlossen und am 07.10.2026 bestätigt; #52 ist abgeschlossen.
Diese 26/18-Werte beschreiben die ZS-/VS2-Erstlieferung. **VS2-V1/N01 verwendet
regulär 24 × UI horizontal und unverändert 18 × UI vertikal.**
Die historische Auswahl und ihre Nachweise werden nicht rückwirkend verändert.

## 2. Ziel und begrenzte Ablösung

Das Spielen soll wie das Bearbeiten eines gezeichneten Rätselbuchs wirken.
Hinweisziffern, Zellmarkierungen, Werkzeuge und Umgebung erhalten eine zusammengehörige
Handschrift. Das Raster bleibt in Modell, Zellzuordnung und Eingabe geometrisch präzise;
seine visuelle Gestaltung darf charaktervoll und spielerisch sein. VS2-E1/N03 erweitert
diese Richtung ausdrücklich auf leicht handgezeichnete Rasterlinien, Miniatur und Palette.
Die frühere pauschale Forderung nach einem sachlichen Raster bedeutet keine sterile
Darstellung und verbietet nicht die hier bestätigten begrenzten Strichabweichungen.

Der bereitgestellte Squeakross-Screenshot dient ausschließlich als Qualitätsvergleich.
Keine Nachbildung seiner Oberfläche, Anordnung, Palette, Figuren oder Zellmotive;
keine Übernahme fremder Assets. Die Vergleichsbilder im Chat sind keine Pflichtassets
oder mathematischen Rätseldaten für die spätere Umsetzung.

Die gewählte A-Buchkomposition bleibt Grundlage. GD-03/GP-03 wurden für die
gezielte Untersuchung der Hinweisziffern geöffnet: Schriftform, Gewicht, optischer
Schriftgrad und gegebenenfalls bewusst gewählte gemeinsame Slotmaße. Seit V3
waren Bakso-Arbeitstitel, sonstige Fraunces-Überschriften und Plex-Sans-Bedientexte
die UI-Grundlage. HZ-D01/D02 löst diese begrenzte Rollenverteilung für normale UI
durch Tidy Hand ab; die C1-Farbkontur bleibt. VS2-E1 erlaubte die begrenzte neue
Flächenverteilung und Scribble-Fassung. HZ wählt keinen neuen Hintergrund, Themen- oder Albumaufbau; HZ-A-FONT02
führt ausschließlich Tidy Hand für Standardtext ein und erhält Überschriften.

[HZ-D07](HAND_DRAWN_UI.md) ergänzt als freigegebener Sollstand optisch ausgewogene
kleine Texte mit stabilen Grundlinien pro Rolle und Größenstufe. Sichtbare
Glyphengrenzen einschließlich Fallback bestimmen weiterhin sichere Textbudgets;
sie begründen kein wortabhängiges vertikales Nachzentrieren. Der Vergleich
korrigierter Größen 14/15 und die konsistente Einbeziehung der Kategorienamen
betreffen die dort benannten Rollen. Keine globale Schrift-, Kontur- oder
Iconänderung und keine Änderung der Hinweis-/Zellgeometrie folgt daraus.

Die Stiftfüllung ist gewählt. Der enge E2-Vergleich enthielt Bakso Daging Regular
und Chalkboard Regular; E3 wählt **Chalkboard Regular**. Bakso Daging und Plex bleiben
nur Vergleichsreferenzen der Studie. Die ausgewählte Erstlieferung verwendet
26 logische Pixel horizontale Zeilenslots und 18 vertikale Spaltenslots bei UI 100 %.
V1 verdichtet nur die Zeilenslots auf 24 × UI; Auswahl und technische Nachweise
stehen in [VS2_V1_IMPLEMENTATION.md](VS2_V1_IMPLEMENTATION.md). Historische Tinte-/Stiftbilder
und R1/R2 bleiben Referenzen ihrer Lieferstände, keine erneut offene Grundsatzwahl.

## 3. Zeichensprache

### ZS-D01: Hinweiszahlen

Kräftige, kompakte Ziffern mit klaren Innenräumen und höherem optischem Flächenanteil
im verfügbaren Platz. Zuerst Form, Gewicht und optische Größe untersuchen; bloßes
Einschalten von Fettdruck reicht als Lieferziel nicht. Die historische Ausgangsfassung
forderte bereits Plex-Sans-Gewicht 600. Dessen sichtbare Wirkung musste nativ
beurteilt werden; die konkrete Chalkboard-Auswahl ist inzwischen bestätigt.

Keine absichtlich schwer lesbare Handschrift, verzogenen Ziffern oder zufälligen
Zeichenabstände. Ein- und mehrstellige tatsächlich vorkommende Zahlen
bleiben horizontal, vollständig und klar unterscheidbar. Alle Folgen einer Orientierung
verwenden gemeinsame regelmäßige Slots. Eine Anpassung ihrer Maße ist nur als
dokumentierte Auswahl zulässig und erhält unabhängige Liniennavigation, vollständige
Erreichbarkeit, Randmarker, geometrischen Snap und semantische gespeicherte Lesepositionen.

Normal, abgeschwächt und zusätzlich ausgekreuzt bleiben dieselben drei GP-48-Zustände.
[HS](CLUE_STATUS.md) zeichnet FILLED und CLOSED gleich blass mit 60 % Zahl-/C1-Deckkraft;
CLOSED erhält zwei stabile handschriftliche Diagonalzüge mit 76 % über das ganze Token.
Farb-IDs, Hinweisreihenfolge und Originalindex sowie die lösungsunabhängige H1/GP-48-
Analyse einschließlich Vorschau bleiben unverändert. Alle Zustände müssen auf beiden
Achsen, im kontinuierlichen Hinweisdrag und im vollständigen Tooltip funktionieren.
HF / #149 verwendet dort unverändert Fraunces 600 als kleinere UI-Überschrift
(gemäß HZ-A-FONT02 erhalten) und unveränderte Delight-Zahlen auf ruhigem
A-Papier mit wiederverwendetem SL-65-Bildrahmen.
Gemeinsame gemessene Zahlen-/X-/C1-/AA-Hüllen und skalierte Innenränder verhindern Überlappung;
Rahmenkanten werden gekachelt, nicht unnötig gedehnt.
Helle Rätselfarben bleiben durch C1 erkennbar; Statuswechsel verändern weder Slot
noch Schriftgröße. Auslassungsmarker und Leerlinienzeichen erhalten keine neue Bedeutung.

**E3 / historische Hinweisgeometrie:** Chalkboard Regular ist gewählt. Die Erstlieferung
verwendet im Buchlayout **26 × UI-Skalierung** horizontal statt der früheren 30 × UI.
Die Spaltenhinweise oberhalb des Rasters bleiben bei **18 × UI-Skalierung**.
**Aktueller V1-Vertrag VS2-E1/N01:** Die horizontalen Abstände betragen **24 × UI**
bei unverändertem Schriftmaßstab. Slotprinzip, Marker-/Drag-/Snap-/Tooltip- und
semantische gespeicherte Lesepositionen bleiben. Die Glyphenpräzisierung in §7
begrenzt den gezielten V1-Abnahmefall, nicht den Bestand großer Regressionsblätter.

### ZS-D02: Gefüllte Zellen

Eine klar erkennbare Grundfläche in der jeweiligen Rätselfarbe trägt wenige
zurückhaltende Schraffur-, Strich- oder Auftragsspuren. Die Textur unterstützt
zusammenhängende Motive und ersetzt die Füllung nicht durch luftige Einzelstriche.
Farben und ihre Zuordnung bleiben eindeutig; keine Änderung von Palette,
Farb-IDs, Lösung oder Definition für den Stil.

Leichte organische Variation liegt innerhalb der Zelle. Varianten bleiben pro Zelle
stabil, auch nach Neuzeichnen, Pan, Zoom und Fortsetzung; kein Flimmern durch neue
Zufallswerte pro Frame. Bei kleinen Zellgrößen und Gesamtansicht wird die Textur
vereinfacht. Der Zustand bleibt ohne Erkennen einzelner Texturstriche ablesbar.

Sichtbare Trennung zu Nachbarfüllungen und Fünferlinien bleibt verpflichtend.
Zeichnung und Effekte sind an der tatsächlichen Zell-/Viewportgeometrie geclippt.
Trefferflächen, Koordinaten, Rastergröße und Rätselfarben werden nicht dekorativ verzerrt.

### ZS-D03: Ausgekreuzte Zellen

Das X besteht aus zwei erkennbaren handschriftlichen Stiftzügen mit begrenzter
Variation in Krümmung, Winkel, Länge und Stärke. Die Variation hängt stabil an
der Zellidentität; Neuzeichnen, Pan, Zoom und Wiederherstellung würfeln nichts neu.
Kreuze bleiben eindeutig, übertönen aber auch auf einem stark ausgekreuzten Blatt
das gefüllte Motiv nicht. Unbekannt, X und Füllung sind im Hauptraster unmittelbar
unterscheidbar. Normale und teilweise sichtbare Zellen verwenden dieselbe Geometrie
mit korrektem Anschnitt; keine Ersatzmarkierung am Viewportrand. N05 ändert nur die
Miniaturprojektion, nicht diesen Hauptraster- oder Zellzustandsvertrag.

### ZS-D04: Buch und funktionale UI ohne zusätzliche Randdekoration

Die zusätzliche Studien-Randdekoration wird nach E1/N05 entfernt. Funktionale
Buchmontierungen, Werkzeuge und Miniaturfassung bleiben erhalten. VS2-E1/N03/N04
erlaubt die stilistische Überarbeitung und begrenzte Verschiebung der vorhandenen
Miniatur-/Palettengruppe, keine zusätzliche dekorative Rand-UI. Eine spätere
Hintergrundbildanpassung ist zurückgestellt, kein aktueller Assetauftrag und kein
Gate für #52/#53. Hintergrund und historische Artworkpakete bleiben unverändert.

Hinweise und Raster erhalten einen ruhigen Untergrund. Dekoration gibt weder
Motivnamen noch eine vorzeitige Skizze der Lösung preis und enthält keine eingebrannten
Bedienattrappen, Fülltexte oder Pseudoschrift. Bei engeren Ansichten beziehungsweise
höherem Zoom tritt sie zugunsten der Arbeitsfläche zurück. ZV-50-Flächennutzung und
die Erreichbarkeit aller bestehenden Werkzeuge werden nicht eingeschränkt.
Historische hashgebundene Designpakete bleiben unverändert; neue Lieferassets sind
gesondert nach Herkunft, Rechten und Version zu dokumentieren.

### ZS-D05: Miniatur – umgesetzter Vertrag VS2-E1/N05

Die Miniatur zeigt unmittelbar nur die eigenen **gefüllten Felder** in ihren
Rätselfarben, einschließlich der aktuellen elastischen Füllvorschau und möglicher
Fehler. Ausgekreuzt und unbekannt haben denselben neutralen Hintergrund; keine X,
Punkte oder anderen Leer-Ersatzzeichen. Diese in V2 umgesetzte Regel ersetzt die frühere visuelle Dreizustandsunterscheidung nur in
Miniaturen. Der Hauptraster-/Spielzustand behält alle drei Zustände.

Die Miniatur bleibt passiv, proportional und unanimiert. Ihre vereinfachten Füllformen
und Fassung passen gemäß N03 zur Scribble-Sprache, ohne dominante Mikroschraffur oder
Zellanimationszwischenbilder. Vorgesehene Füllung wird sofort sichtbar; Vorschau auf
X/Neutralisierung entfernt eine vorherige Füllung nur aus dem Vorschauabbild. Rückzug
oder Abbruch stellt die bestätigten Füllungen wieder her. Dieselbe reine Darstellung
gilt für vorhandene ungelöste Albumminiaturen, ohne neue Albumgestaltung.
Motivname und fertige Illustration erscheinen weiterhin erst nach tatsächlichem Abschluss.

## 4. Statische Vorschau und Animation nach dem Anwenden

### ZS-D06: Vorschauvertrag

Die Vorschau zeigt nur wirksame Änderungen des aktuellen geraden Strichabschnitts.
Füllung oder X erscheinen vollständig, ohne Animation, in der gewählten Endform,
aber heller beziehungsweise transparenter. 56 % bleiben der unveränderte
Ausarbeitungswert; eine neue gesonderte Eigentümerabnahme dafür fehlt.

Bei X-zu-Füllung und Füllung-zu-X zeigt die Vorschau nur den neuen Zielzustand;
die bisherige Gegenmarkierung wird nicht darunter stehen gelassen.
Bei Neutralisierung oder Radieren ist das Ziel unbekannt: Die bisherige Markierung
verschwindet bereits in der Vorschau. Eine dezente statische Vorschaukontur macht
die betroffene Zelle weiterhin sichtbar.

Elastischer Rückzug, echte Startzell-Rückkehr mit Achsenneuwahl und Abbruch
aktualisieren die Vorschau unmittelbar gemäß P1. Entfallene Vorschauänderungen
zeigen sofort den bestätigten Ausgangszustand; keine nachlaufenden Spuren.
Vorschautransparenz ist kein neuer gespeicherter Zell- oder Hypothesenzustand.

### ZS-D07: Commit und gerichtete Effekte (ZS2-E2 plus Nacharbeit 09.10.2026)

Erst das tatsächliche Anwenden bei Mouse-Up startet die kurze Zellanimation.
Einzelklicks bleiben Striche der Länge eins. Maßgeblich ist die bestätigte
[ZS2-E2-Nacharbeit N01–N03](https://github.com/venomenon328/picross/pull/56#issuecomment-6061611805).
Nach sofortigem atomarem Commit beginnen Setzen/Umwandeln vom tatsächlichen
Start zum finalen geraden Abschnittsende; Rückzug und G1-Neuwahl bestimmen diesen
Endabschnitt. Nur die `m` effektiv geänderten Füllungen/X zählen. Für `m > 1` gilt
`Δ = min(12 ms, 180 ms / (m - 1))`, Start der Zelle `i` bei `i × Δ`; bei `m = 1`
ohne Verzögerung. Mikrosekunden werden auf die nächste ganze Zahl gerundet.
Geschützte Felder/No-ops animieren nicht und erzeugen keine Zeitlücken.
Wartende Zellen zeigen bereits das gültige Ziel abgeschwächt; nie alte Gegenmarken.
Die reine Darstellung hat keine Modell-/Save-Callbacks oder Eingabesperre.

Die bestätigte Nacharbeit vom 09.10.2026 verlangt deutlich handschriftliches
Ausfüllen: Füllung baut sich sichtbar entlang aufeinanderfolgender kurzer, leicht
schräger Schraffur-/Füllstriche auf;
das X zeichnet erst den ersten, dann den zweiten Zug. Bloßes globales Fade oder
bewegte Dekorstriche auf schon kräftiger Endfüllung genügen nicht. Bei gestarteten
Füllungen bleibt unbeschriebenes Papier frei; die volle blasse Unterzeichnung entfällt
auch hier. Ruhende Endform und statische Ziehvorschau bleiben erhalten.
Beim gestarteten X bleiben ebenfalls noch nicht geschriebene Zugteile unsichtbar,
damit Zug eins und danach Zug zwei bei normaler Spielgröße sichtbar entstehen.
Die vollständige 56-%-Vorschau beim Ziehen und das abgeschwächte wartende Ziel
bleiben statisch; Endgeometrie, Farben und Clipping bleiben erhalten. Beim Neutralisieren
darf eine zuvor entfernte Füllung oder ein X nicht nochmals als Löschanimation auftauchen;
stattdessen kann die Vorschaukontur oder ein neutraler kurzer Löschhinweis auslaufen.

Die bestätigte Tempo-Nacharbeit ersetzt die historischen 140/80/8/120/260 ms
durch **210 ms insgesamt pro Zelle** für
Setzen/Umwandeln und **120 ms** Entfernen. Teilzüge innerhalb einer Zelle folgen
aufeinander; die beiden X-Züge teilen sich die 210 ms. Die gesamte Setzfolge endet
spätestens nach 390 ms (maximal 180 ms Startspreizung plus 210 ms). Entfernen
beginnt für alle wirksamen Zellen sofort und endet nach 120 ms, ohne Staffelung.

Der Strich wird weiterhin sofort als eine atomare Aktion übernommen.
History, Hinweiszustände, Abschlussprüfung und Sicherung warten nicht auf Effekte.
Die nächste Eingabe bleibt unmittelbar möglich; bestehende P1-Sperren während
einer tatsächlich aktiven Zellgeste werden dadurch weder erweitert noch aufgehoben.

### ZS-D08: Vorrang und Lebenszyklus

| Ereignis | Verbindliches Darstellungsverhalten |
| --- | --- |
| Neue wirksame Vorschau auf noch animierter Zelle | Statische neue Vorschau hat Vorrang; alten Effekt dieser Zelle endgültig beenden. Andere Effekte dürfen weiterlaufen. |
| Rückzug/Abbruch dieser neuen Vorschau | Bestätigten Endzustand sofort zeigen; den zuvor beendeten Effekt nicht wieder starten. |
| Erneuter Commit derselben Zelle | Nur der jüngste bestätigte Zielzustand ist maßgeblich; kein alter Callback darf später Zellen oder Darstellung zurücksetzen. |
| Undo/Redo | Exakten Zustand sofort herstellen, betroffene Effekte beenden; keine eigene neue Setzanimation und keine zusätzliche Eingabesperre. |
| Escape/Fokusverlust/Gegentaste | Vorschau verwerfen und aktive sowie wartende Effekte beenden. Kein Commit oder verspäteter Wiederanlauf. |
| Blattwechsel, Reset, Restore, Album/Informationsseite | Keine Effekte in eine andere Session übertragen, speichern oder beim Wiederöffnen erneut abspielen. Bestehender Abbruch-/Flush-/Recoveryvertrag bleibt. |
| Letzter erfolgreicher Strich | Sofortiger Abschluss-/Speicherpfad; laufende Zelleffekte dürfen enden. EA / #170 übernimmt anschließend ausschließlich die Präsentation (250/650/400/650/200 ms) bis zum vorhandenen Motivbild mit Name und Reset. Kein Warten von Logik oder Sicherung auf das Animationsende; [EA-Prüfzuordnung](EA_VERIFICATION.md). |
| Pan/Zoom/Resize nach Commit | Aktive und wartende Effekte beenden; keine Eingabe- oder Navigationssperre durch Effekte. |

Während einer linken/rechten Zellgeste bricht das Down der jeweils anderen
Taste die gesamte Vorschau samt Zähler ab, auch außerhalb des Boards innerhalb
des Fensters. Beide zugehörigen Ups werden ohne Commit verbraucht; erst nach
Loslassen beider Tasten darf ein frisches Down wieder eine Zellgeste starten.
Erneutes Down/Bewegung bei noch gehaltener Taste bleibt gesperrt; Escape/Fokusverlust
dürfen weder Phantom-Commit noch hängende Sperre erzeugen. Ein falsches Up ohne
vorheriges Gegentasten-Down bleibt gemäß G1 unbeachtlich. Die linke Taste
bewegt gemäß [HN](CLUE_INTERACTION.md) ausschließlich die begonnene überlaufende
Hinweisfolge; MMB navigiert keine Hinweise. Hand- und Rasterpan
entfallen. N04/Zählmöglichkeit ohne Commit ist zurückgestellt.

Animation ist eine transiente Darstellungsschicht. Sie verändert weder Zellen,
History, Hinweislogik, Bewertung noch Saveformat. Effekte sind innerhalb der
jeweiligen Zelle/des Viewports begrenzt; keine springenden Raster oder dauerhaft
bewegten fertigen Markierungen.

### ZS-D09: Abschaltmöglichkeit

Ein einfacher Schalter „Zellanimationen“ schaltet diese Effekte ab.
Ausschalten beendet aktive und wartende Effekte sofort und zeigt den gültigen Endzustand.
Wiedereinschalten wirkt nur auf künftige Strich-Commits; alte Aktionen werden nicht
nachgespielt. Die statische, abgeschwächte Vorschau bleibt unverändert erhalten.

Begrenzter Ausarbeitungsdefault nach bestehendem P1-Vorbild: Der Schalter startet
aktiv und gilt sitzungsweit, auch nach Blattwechsel, Reset und Informationsseite.
Er wird nicht im Rätselsave oder in einem neu eingeführten Einstellungsformat
persistiert und startet nach App-Neustart wieder aktiv. Dies konkretisiert den
begrenzten Prototyp; eine dauerhafte Produkt-Einstellungsarchitektur bleibt separat.
Der Schalter verändert keine Zellen, History, undo_used, Hinweislesepositionen,
Autosaves oder Abschlusslogik. Kein zusätzliches globales Bewegungsmenü oder Zeitregler.

### ZS-D10: Großraster und Nachweise

Der Stil und die Effekte müssen auch an kleinen Zellen, langen Hinweisfolgen,
farbigen 40×40- und 100×100-Rastern sowie stark ausgekreuzten Zuständen funktionieren.
Repräsentative vorhandene Inhalte und der gekennzeichnete F-03-Stressfall bleiben
unverändert. Keine abweichende Rätsellogik oder neue Inhalte zur Erleichterung der Probe.

Technischer Leitfaden: nur laufende visuelle Übergänge verwalten, stabil gezeichnete
Varianten wiederverwenden und den Animationstakt beenden, sobald kein Effekt mehr aktiv ist.
Animationstakte sollen keinen vollständigen UI-/Miniatur-/Analyse-Refresh auslösen.
Die konkrete Umsetzung und Leistung werden nativ gemessen; keine ungeprüfte FPS-Zusage.

Verifikation verbindet Zustands-/Gestenregressionen, gezielte native Bilder zu
bekannten Zeitpunkten, eine kleine Strichsequenz mit Negativkontrollen gegen
gleichmäßiges Fade und falsche X-Zugreihenfolge
und reale schnelle Mauseingaben. Ein Endzustands-Screenshot allein beweist keine
Animation; erfolgreiche Dokumenttests beweisen keine Lesbarkeit oder Eingabeflüssigkeit.

## 5. Lieferpakete und Abnahme

| Paket | Ergebnis | Abhängigkeit und Gate |
| --- | --- | --- |
| ZS-1 | Gewählte Stiftfüllung, neues X und räumlicher Strichaufbau; E2-Fontvergleich, E3-Auswahl Chalkboard und kompaktere 26-px-Zeilenhinweisslots. | PR #55 nach R3 integriert; kombinierte Eigentümersichtprüfung auf main erfolgreich abgeschlossen. |
| ZS-2 | Gewählte Hinweis-/Zellsprache ohne zusätzliche Rand-UI, statische Vorschau, gerichtete Commit-Effekte und Schalter in der regulären Arbeitsansicht. | PR #56 auf `fad8853` integriert, R3 und ZS2-M01 für diesen Vorgänger bestanden. |
| VS2-V1 | Kompakte Zeilenhinweise und ausgewogene Flächenaufteilung einschließlich Miniatur-/Palettenposition. | N01/N02/N04 auf `40829b4` technisch geliefert und in R2 positiv geprüft; V1-Zwischenstand, kombinierte Abnahme offen. |
| VS2-V2 | Subtile Scribble-Linien, Miniatur/Palette und reine Füllminiatur. | N03/N05 umgesetzt; auf der V1-Geometrie, kombinierte technische Nachweise und offene Abnahme im PR. |
| Z3/#24 | Längere reale Spielerprobung der integrierten neuen Fassung und Abschluss der Designphase. | Nach der integrierten Zielansicht; ersetzt keine davor erforderlichen technischen oder gezielten manuellen Gates. |

ZS-1 verwendete insbesondere F-01/20×20 Mono, F-02/40×40 Farbe und F-03/100×100
für identische Vergleiche. ZS-2 ergänzte die vorhandenen regulären großen RP-6-Inhalte,
darunter F-07/100×100 Farbe. Relevante Flächen bleiben 1280×720, 1600×900,
1920×1080 und 2560×1440 sowie UI 100/125 % und kleine/größere Arbeitszoomstufen.
Gezielte Referenzen statt unnötiger vollständiger Kreuzprodukte; verpflichtende
bestehende Regressionen bleiben aktiv.

Der Spielerdownload bleibt schlank. Maßgeblich ist die aktuelle
[CI-Policy #63](CI_POLICY.md): ausgewählte aktuelle Prüfungen und begrenzte technische
Nachweise, kein allgemeiner Full-Evidence-Schalter und keine historischen Importe
im Standardlauf. Head, Basis/Test-Merge, Run und relevante Datei-Hashes binden die
Nachweise. Quellen-/Nachweis-/Sichtprüfung gehört zu jedem Umsetzungspaket.

## 6. Nichtziele

Keine neue Themen-/Kapitelwahl, Progression, Wertung, Fehlerhilfe, Hypothesen,
Rätselproduktion, Audio, Hintergrundbewegung, aufwendige Abschlussinszenierung,
Engine-/Plattformänderung oder globale Accessibility-/Einstellungsplattform.
Keine Integration alter PRs #25/#28 als Voraussetzung, kein verstecktes Übernehmen
ihrer offenen Befunde. Keine Änderung historischer Designartefakte oder Rätselproofs.

ZS1-M01 ist nach Merge von PR #55 auf `main@985cf08e` am 07.10.2026 vom Eigentümer
bestätigt; #52 ist abgeschlossen. Die [reguläre ZS-2-Integration](ZS2_VERIFICATION.md)
ist über PR #56 abgeschlossen. S0 und die technische V1-Lieferung sind abgeschlossen.
V2 ist umgesetzt. Aktuelle kombinierte Nachweise werden commitgebunden im PR geführt.
Unabhängiges Review des kombinierten Heads, VS2-M01 und passende Mergefreigabe bleiben offen.

## 7. VS2-E1 – kompakte, ausgewogene Scribble-Arbeitsansicht

**Status am 10.10.2026: S0 abgeschlossen; V1/N01/N02/N04 technisch geliefert und
in R2 positiv geprüft; V2/N03/N05 umgesetzt.**
Auftrag und Teilpakete stehen in [#61](https://github.com/venomenon328/picross/issues/61).
Aktuelle V1-Produktreferenz ist `40829b43db6509447863c9d27dbb87dcfaf2a988`
auf Basis `d7ec4e1e4a29d82b6979537a33868d57732d3713`; `2c332ad…` bleibt die
historische reguläre Erstlieferung, nicht die spätere V2-Vergleichsbasis.
Die fünf Regeln bilden eine begrenzte Erweiterung bestehender Fachverträge,
keine zweite P1-Vollspezifikation. Technische Lieferung ist keine persönliche Abnahme.

### VS2-N01: engere Zeilenhinweise – V1 geliefert

Die horizontalen Abstände zwischen den Zahlen derselben Zeilenhinweisfolge betragen
regulär **24 × UI statt 26 × UI**. Ein gemeinsamer regelmäßiger Slotabstand bleibt;
keine variable Einzelpackung, keine kleinere Schrift als Ersatz. Chalkboard und dessen
bestehender Schriftmaßstab bleiben, Spaltenslots weiterhin **18 × UI**. Kandidat A
aus dem vorab gebundenen [V1-Plan](../examples/vs2/v1-plan.json) wurde gewählt.
Reale Zahlen **1/11/17/40**, C1/AA, drei Statuszustände, Marker und kontinuierliche
Draggeometrie bilden den gezielten V1-Glyphennachweis.

**Eigentümerpräzisierung vom 10.10.2026:** Der separate
[V1-Plan-Nachtrag](../examples/vs2/v1-plan-amendment.json), versioniert in `a41cf9b`,
nimmt die synthetische Hinweiszahl **100** aus der V1-Abnahme. Ihre dafür erprobte
Sonderbehandlung ist entfernt. Das ersetzt die frühere Aufzählung 1/11/17/40/100
im aktiven V1-Vertrag; der ursprüngliche Plan bleibt als historischer Nachweis unverändert.
Bestehende 100×100- und andere Großfallregressionen bleiben erhalten. Keine neue
Größenvalidierung, Datenmigration oder erneute Sonderbehandlung folgt daraus.

Rasteransicht erhält mindestens min(5,n) zusammenhängende ganze Zahlen auch zwischen
Snaplagen; Gesamtansicht zeigt sämtliche Hinweise. Vollständige Originalzahlen,
monotone direkte Bewegung, geometrischer Drop, Nachbarlinienunabhängigkeit und
semantische Leseanker bleiben. Parameter und technische Belege stehen in
[VS2_V1_IMPLEMENTATION.md](VS2_V1_IMPLEMENTATION.md) und im commitgebundenen PR.

### VS2-N02: ausgewogene belegte Arbeitsfläche – V1 geliefert

Nach der Fit-/Kapazitätsberechnung werden Raster und beide Hinweisflächen als ein
belegter Block bei ausreichender Restbreite weiter Richtung Mitte der nutzbaren
Papierarbeitsfläche platziert. Maßgeblich ist die Fläche ohne sichere Miniatur-/
Palettengruppe und andere Controls, nicht blind die ganze Fenstermitte.
Bei knapper Breite haben vollständige Inhalte und Bedienbarkeit Vorrang.

Reihenfolge: tatsächliche Mindestreserven und Fit, GF1-Zusatzkapazität für vollständige
Zeilen- und Spaltenhinweise aus freier Breite/Höhe (HF / #149), danach Ausgleich des verbleibenden Freiraums. Nicht durch künstliche
leere Hinweisslots, Kürzen sichtbarer Zahlen, kleinere gewählte Zellen oder Schrift
zentrieren. Der Anordnungsschritt darf die gültige Fitgrenze nicht nochmals senken.
Alle Hinweise, Rasterdarstellung, Cursor-/Gestenabbildung und Hit-Tests teilen den
Versatz. Fortschritt, H1-Status oder Hinweisdrag ändern die Anordnung nicht.

F-01 und geeignete VS09-Breitenfälle dienen als reproduzierbare Freiraumbeispiele;
VS08/VS04 und knappe Flächen sichern die Kapazitätsgrenzen. Die Chatbezeichnung
„Analyseausgabe 1“ ist keine eindeutig identifizierte Datei und keine Pflichtquelle.

### VS2-N03: subtile, stabile handgezeichnete Elemente – V2 umgesetzt

Sichtbare Rasterlinien erhalten kleine kontrollierte Abweichungen von vollkommen
gleichmäßiger Strichführung und -stärke. Logische quadratische Zellen, Koordinaten,
Achsenbindung und Trefferflächen bleiben regelmäßig. Gemeinsame Kanten dürfen nicht
auseinanderfallen; Fünfergruppen, Ecken und gefüllte Nachbarzellen bleiben klar.
Der gesamte sichtbare Strichumfang einschließlich Abweichung/AA gehört zum Fit- und
Clippingbudget. Alle vier Rahmenkanten bleiben vollständig sichtbar.

Variation hängt stabil an Raster-/Elementidentitäten, nicht an aktuellen Zellwerten,
Mausposition oder jedem neuen Frame. Neuzeichnen und Fortsetzen würfeln nichts neu.
Bei kleinen Zellen wird sie reduziert, statt Lesbarkeit und Trennung zu verschlechtern.
Keine neue Rasteranimation und keine veränderten ZS-D06–D09-Timings oder Abbruchregeln.

Miniatur samt Fassung und Farbauswahl erhalten dieselbe zurückhaltende Scribble-Sprache.
Miniaturfüllungen bleiben vereinfachte ruhige Farbformen, keine dominante Mikroschraffur.
Palettenfarb-IDs und Originalfarbflächen bleiben eindeutig; Auswahl, Hover und Fokus
müssen erkennbar sein, ohne neue Rätselfarben vorzutäuschen. Die optische Strichkante
verkleinert oder verzerrt keine Hitbox. Die normale UI-Schriftrolle folgt inzwischen
dem freigegebenen HZ-Sollstand; das A-Hintergrundbild bleibt.
„Kleine Vorschau“ bezeichnet hier die Miniatur; die statische Zielvorschau im Raster
bleibt ebenfalls stilistisch konsistent, aber ohne neu eingeführte Bewegung.

### VS2-N04: Miniatur-/Palettengruppe mit Buchrandabstand – V1 geliefert

V1 verschiebt die vorhandene Gruppe im großzügigen Referenzfall um **(−16, +24) × UI**
nach links/unten; knappe Flächen begrenzen den Abwärtsversatz. Fassung, Halterungen,
Beschriftungen und Auswahlmarkierungen werden mitgeführt; sichtbar Abstand zum
oberen/rechten Buchrand, keine angeschnittenen Konturen. Gemeinsam mit N02 bleiben
Raster/Hinweise, Navigation, Koordinaten, Werkzeuge und Save-/Recoverymeldungen frei.
Keine Verkleinerung als Ersatz; Mindesthitflächen von **44/55 px bei UI100/125** bleiben.
Die tatsächlichen neuen Strichränder aus V2 sind erneut gegen diese V1-Anordnung
zu prüfen; V1s alte Pixelbilder nehmen die kombinierte Abnahme nicht vorweg.

### VS2-N05: reine Füllprojektion der Miniaturen – V2 umgesetzt

ZS-D05 ist der neue Miniaturvertrag: ausschließlich eigene Füllungen einschließlich
bereits bestehender Vorschau, keine X/Punkte/Leer-Ersatzzeichen. Unbekannt und X
haben denselben neutralen Miniaturhintergrund. Zwei Stände mit identischen Füllungen
und unterschiedlichen X/unbekannt ergeben dasselbe Miniaturbild.

Der logische Zellzustand, X im Hauptraster, History/Redo, H1/GP-48, Speicherformat
und Abschluss ändern sich nicht. Eigene fehlerhafte Füllungen bleiben sichtbar.
Füllung↔X-/Neutralisierungsvorschau, Rückzug, Abbruch, Undo/Redo und Neustart müssen
die reine Projektion unmittelbar erhalten; keine Lösungskorrektur und kein früher Reveal.
Vorhandene ungelöste Albumminiaturen folgen derselben Projektion; keine neue Album-UI.

### Geltung gegenüber älteren Fachtexten und Abnahme

Die ausdrückliche Eigentümerfreigabe ersetzt gezielt D-33/ZS1-E3 als unveränderliche
horizontale 26er-Zielweite und die frühere linke Anordnung/Positionierung durch V1.
Die Ablösung ausschließlich mathematisch gerader sichtbarer Rasterstriche, der
bisherigen Miniatur-/Palettenfassung und der Dreizustandsdarstellung in Miniaturen
ist mit **V2 umgesetzt**. Dies gilt entsprechend für
[Produktdefinition](PRODUCT_DEFINITION.md) §§3.3/5,
[Gestaltungskonzept](DESIGN_CONCEPT.md) §§2/4.1/4.4/5.1,
[P1](PROTOTYPE_P1.md) D-29/D-33 und §5.2 sowie die betroffenen Z2-Auswahlpassagen.
Deren nicht ersetzte Regeln bleiben verbindlich; **logische Regelmäßigkeit,
Präzision und die drei Spielzustände sind ausdrücklich nicht abgelöst**.

Historische Pläne, Proofs, Asset-/Fonthashes, Bilder, Abnahmen und Reports bleiben
unverändert. Der separate V1-Nachtrag und die aktuelle Statuskonsolidierung ändern
keine historischen Ergebnisdaten. R1 gilt für `2c332ad`, R2 für `40829b4`; keiner
nimmt V2 oder die persönliche kombinierte Abnahme vorweg. Bei V2 sind Bedienhilfe
und betroffene Pixel-/Strichoracles konsistent nachzuführen.

V1/NA01/NA02/NA04 ist historisch technisch geprüft. Der neue [V2-Prüfweg](VS2_V2_IMPLEMENTATION.md)
prüft NA03/NA05 und die kombinierte Regression; tatsächliche Laufresultate stehen im PR. Aktuelle Nachweiszuordnung steht in [VS2_VERIFICATION.md](VS2_VERIFICATION.md),
Vorbereitung und Auftrag in #61. Der eigene [endliche V2-Plan](../examples/vs2/v2-plan.json)
wurde vor Vergleichen in `75b640c` versioniert; ursprüngliche VS2-/V1-Pläne bleiben erhalten. Beide Teilpakete bleiben
in PR #62, mit kombinierter technischer/visueller Prüfung und VS2-M01 vor einem
gesondert freizugebenden Merge.

## 8. VS2-E2 / V3 – gezielte reguläre Fortschreibung

Auftrag: [#61](https://github.com/venomenon328/picross/issues/61), Vorbereitung
V3-S1–S5 und VS2-E2-Nachtrag in [PR #62](https://github.com/venomenon328/picross/pull/62#issuecomment-6099894860).
V3-01–07 ist umgesetzt auf Basis des vorbereiteten kombinierten V1/V2-Heads
`e2547016cef7cfe400a77fb09f22c872306de22a`. Der eigene endliche
[V3-Prüfplan](../examples/vs2/v3-plan.json) wurde vor Vergleichen in `502883c`
versioniert. [Umsetzung und Prüfzuordnung](VS2_V3_IMPLEMENTATION.md).

Die folgende Tabelle erhält den damaligen V3-Umfang. Insbesondere V3-07 ist für
die aktuellen Schriftrollen durch HC/KB/KK und den freigegebenen HZ-Sollstand
fortgeschrieben; HZ behauptet keine rückwirkende V3-Lieferung.

| Regel | Damaliger verbindlicher V3-Umfang |
| --- | --- |
| V3-01 | Rasterlinien etwas stärker handgezeichnet als V2, stabil je Linie. Tatsächliche Abweichung, Strichbreite und AA bleiben im vorhandenen Rahmenbudget; keine weitere Fitverkleinerung. Kleine Zellen vereinfachen; Rahmen, Fünfergruppen und Zelltreffer bleiben eindeutig. |
| V3-02 | Drei organische helle Stiftzüge variieren in Lage, Enden, Neigung, Abständen und Krümmung stabil je Zelle. Satte Originalfarbe und Trennung bleiben. Zielvorschau, wartende Ziele und letzter Animationsdurchgang teilen dieselbe Endtextur. Unter 18px oder bei Einpassen ruhige vereinfachte Fläche. X, 210/120-ms-Timing, Startabstände und History bleiben. |
| V3-03 | Hilfe, Menü und Informationszugang bewegen sich gemeinsam um (−20,+12) × UI; erreichbare Originalhitflächen, sicherer Abstand zu Titel, Miniatur und Papierkante. |
| V3-04 | Dauerhafte Werkzeug-/Farbtextzeile samt Platzbedarf entfällt. Auswahlmarkierungen, Tooltips, Farberhalt und Bedienfunktion bleiben. |
| V3-05 | Numerische Zoomanzeige entfällt. Verkleinern, Vergrößern, Einpassen und Arbeitsgröße bleiben; wahrheitsgemäße nichtnumerische Platz-/Hinweiswarnungen erscheinen bei Bedarf getrennt unten. |
| V3-06 | Acht Werkzeuge in genau dieser Reihenfolge rechts unter Miniatur/Palette: Füllen, Radieren, Undo, Redo, Minus, Plus, Einpassen, Arbeitsgröße. Eine Spalte, 44/55px bei UI100/125, Gruppen 2/2/4. Nur bei knapper Höhe scrollt die Werkzeugleiste mit sichtbarem Balken. Gezeichnete Controls und Treffer clippen an derselben Grenze; Rad dort verändert weder Raster noch Zellen. Keine alten unteren Werkzeugmulden. |
| V3-07 | Unverändertes Bakso Daging ausschließlich für den Arbeits-Blatttitel. Aktive reguläre Ressource und Nutzungshinweise, keine Freigabe des Studienpfads. Originalbytes bleiben; Fraunces in Sammlung/Information, Plex-UI und Chalkboard-Hinweise erhalten. Im realen Titel fehlt nur `·`; dafür explizites gebündeltes Plex, keine Systemfontsuche. |

V1s 24/18-Slots, Schriftmaßstab, GF1 und Reihenfolge Fit → Kapazität → Translation
bleiben. V2s reine eigene Füllminiatur einschließlich Vorschau bleibt. Keine
Änderung an Modell, Rätseln, Saveformat, atomarer History, H1/GP48, X oder Reveal.
Die aktuelle CI-Policy gilt einschließlich kompakter Bildauswahl und Budgets;
historische Pläne/Manifeste und persönliche Abnahmen bleiben commitgebunden.
