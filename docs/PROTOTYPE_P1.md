# P1: Großraster- und Bedienprototyp

## Aktueller Vertrag · Sidebar #65

PR #62 / #61 ist seit 10.10.2026 in main `e323dcf5c83b085144e61707ef98ecab2bfac39b` integriert. Der neue zusammenhängende Stand A+B folgt auf `feat/65-sidebar-frames`; [SL-Umsetzung und Prüfzuordnung](SL65_IMPLEMENTATION.md) ist für die Sidebar maßgeblich. Frühere Draft-/Mergegate-Aussagen zu #62 und dessen V1/N04-Versatz, V3-05/V3-06-Leiste und prozedurale Gruppenfassungen sind historische Paketstände. Sie gelten nicht als aktuelle Bedienanweisung.

Aktuell: genau sechs Aktionen in 2×3 (Füllen/Radieren, Undo/Redo, Minus/Plus), ohne Einpassen-/Arbeitsgrößenaktion oder „Dein Stand“. Drei transparente gezeichnete Rahmen ersetzen die alten Fassungen; Miniatur, Koordinaten, Palette und Werkzeuge teilen die Mittelachse. Die interne Vollsichtgrenze, Optionsansichten G/V, Raster-/Hinweisbudgets und Albumminiaturen bleiben. Nach vollständiger unveränderter Schema-1-Validierung wird `overview=false`; gültiger Zoomwunsch, Inhalt, History/Redo und Recoverygrenzen bleiben erhalten. Neue Saves schreiben Schema 1 mit `overview=false`. SL-R01, persönliche SL-M01 und neue Mergefreigabe bleiben offen; kein Release. Historische Prüfpläne/-berichte bleiben unverändert.

## Aktueller regulärer Stand · VS2 (#61)

**Kombinierter V1/V2/V3-Stand:** N01–N05 und V3-01–07 umgesetzt; [V1](VS2_V1_IMPLEMENTATION.md), [V2](VS2_V2_IMPLEMENTATION.md) und [V3-Umsetzung und Nachweisweg](VS2_V3_IMPLEMENTATION.md). Neues unabhängiges Review, persönliche VS2-M01 und Mergefreigabe bleiben offen.

Der reguläre Start öffnet die Sammlung, auch mit Teil- oder Abschlussständen.
Einstellungen sind dort ohne Rätselöffnung erreichbar. **Rätselansicht** bietet
**Rasteransicht** (Sitzungsdefault) und **Gesamtansicht mit allen Hinweisen**.
Die Wahl bleibt bis zum nächsten Start erhalten. Einpassen ändert den Modus nicht.
Das ganze Raster samt Außenrahmen bleibt bei jedem angebotenen Zoom sichtbar;
Hand-, Raster- und Miniaturverschiebung entfallen auch für bestehende Großfälle.
MMB bewegt ausschließlich eine angefasste überlaufende Hinweiszeile horizontal
oder Hinweisspalte vertikal. Die eigene Miniatur bleibt proportional und passiv.

Mindestreserven werden pro Achse aus tatsächlichen vollständigen Glyphen bestimmt;
Rasteransicht zeigt mindestens min(5,n) zusammenhängende Zahlen auch im Drag.
Erst danach nutzt GF1 freie horizontale Breite für weitere sichere ganze Slots,
ohne Fit-/Schriftverlust. Gesamtansicht reserviert sämtliche Hinweise. 24px bleibt
der gewünschte reguläre Arbeitswert, begrenzt durch den tatsächlichen Fit.
Platzmangel und kleine/kollidierende Hinweise werden transparent behandelt;
50×50/100×100 erhalten keinen versteckten Pan-Ausweg oder Komfortzertifikat.

Neun Inhalte und Schema 1/Appidentität bleiben erhalten. Vollständige Validierung
geht der Normalisierung alter Hand-/Pan-/Zoomwerte voraus. Gültige gewünschte
Arbeitsstufe und aktuelle Fitgröße sind getrennt; Modus wird nicht gespeichert.
Studienkatalog und -speicher werden beim regulären Start nicht verwendet.
Historische Studienquellen bleiben ausschließlich Entwickler-/Referenzbestand;
separate Studienplayer entfallen aus der Standardlieferung.

[Prüfzuordnung](VS2_VERIFICATION.md) und [neutrale Windows-Probe](VS2_OWNER_TRIAL.md)
binden die neue Lieferung. #53/N01–N03 ist über PR #56 auf `fad8853` integriert;
ZS2-M01 und GF-M01/#59 sind historisch bestanden. VS2-M01 und unabhängiges
technisches/visuelles Review des neuen Heads bleiben vor Merge offen. Kein Release.


Stand: 09.10.2026 · Spezifikation 0.23 · P1.4/G1/H1/Z2/GP-48/ZV-50/RP-6/ZS2 integriert; VS2-Lieferung im Draft-PR

## 1. Geltung, Auftrag und Quellen

Paketquelle ist [Issue #5](https://github.com/venomenon328/picross/issues/5). Hier stehen die versionierten P1-Verträge; das Issue führt Auftrag, aktuellen Ausführungsstand, offene Prüfungen und spätere Entscheidungen. Änderungen an diesen Verträgen sind in Datei und Issue-Verweis konsistent nachzuführen, nicht in einer zweiten parallelen Vollspezifikation.

Maßgebliche Grundlagen sind [Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md), [Projektprofil](PROJECT_PROFILE.md) und [lokaler Workflow](dev-rules/WORKFLOW.md); Einstieg bleibt [AGENTS.md](../AGENTS.md). Vor Ausführung die aktuellen Quellen und Issue-Kommentare prüfen.

Die Spezifikationspflege 0.2 wurde über PR #6 gemergt, der technische P1.0-Preflight über PR #13. [P1.1 / Issue #8](https://github.com/venomenon328/picross/issues/8) und [P1.2 / Issue #9](https://github.com/venomenon328/picross/issues/9) wurden über PR #14 als `acc9c51161a18cca17813a8e44c07b2cf074cd44` in `main` integriert. [P1.3 / Issue #11](https://github.com/venomenon328/picross/issues/11) wurde über PR #15 als `efada37100ddfded50c432e70823b3f0dd446436` integriert. [P1.4 / #12](https://github.com/venomenon328/picross/issues/12) wurde nach technischer Gesamtprüfung und bestandener Eigentümerprobe über PR #16 als `95fee5f87a84d4e849c845ce98313144349b3dd8` integriert; der commitgebundene Stand steht im [P1.4-Ergebnisbericht](P1_4_VERIFICATION.md). #17/G1 ist über PR #18 als `6dd33232977127592c2b881f73094658853dbd87` integriert. H1/#19 ergänzt darauf die lösungsunabhängige optionale Erfüllungsmarkierung. Die gezielten realen G1-/H1-Proben sind nicht als bestanden dokumentiert; durch die ausdrücklichen Mergeentscheidungen vom 25.09.2026 sind sie für PR #18 beziehungsweise PR #20 keine verbleibenden Mergegates.

**Ist/Soll:** D-07 bis D-27, Persistenz/Recovery und die integrierte P1.4-Prüfung sind
bis einschließlich PR #16 in `main` integriert. M-01 bis M-04 sowie M-06/M-07 wurden
in #12 am dort gebundenen Stand vom Eigentümer bestätigt; historische Prüfberichte
bleiben Nachweise ihrer jeweiligen Commits. G1/#17, H1/#19 und Z2/#23 sind in
`main` integriert. RP-3/#37 ergänzt F-04 samt eigenen aktuellen technischen und
visuellen Nachweisen; keine gezielte reale Probe wird rückwirkend aus #12 abgeleitet.

**Paketgrenze:** Diese Spezifikation beschreibt den gesamten P1-Vertrag. #8 liefert F-01, Mausstriche, eigene Miniatur, Undo/Redo und Abschluss. #9 ergänzt F-02/F-03, Farben, Zoom/Pan und interaktive Miniaturnavigation. #11 ergänzt lokale Persistenz und Recovery; #12 schließt die integrierte 500-Aktionen-, Windows-, Bedien- und Performanceprüfung ab. #17 ergänzt die Startzell-Rückkehr zur erneuten Achsenwahl; #19/H1 ergänzt die lösungsunabhängige Erfüllungsmarkierung und ihren sitzungsweiten Schalter. Aktuelle [Anleitung](../prototypes/p1/README.md), [P1.4-Ergebnisbericht](P1_4_VERIFICATION.md), [H1-Prüfbericht](H1_VERIFICATION.md), historischer [P1.3-Prüfbericht](P1_3_VERIFICATION.md) und historischer [P1.2-Prüfbericht](P1_2_VERIFICATION.md).

Die P1-Entscheidungen konkretisieren den begrenzten Bedienversuch. Sie legen weder die endgültige Produktengine noch die gesamte Betriebssystemmatrix, Wertung oder Themenwahl fest. Frühere P1-Vorschläge in Issue-Revision 0.1 und Gestaltungskonzept Abschnitt 7 sind innerhalb dieses Scopes abgelöst; globale Produktfragen bleiben offen.

Die [zeichnerische Spieloberfläche](UI_DRAWING_STYLE.md) ergänzt als am 07.10.2026
freigegebener **Sollstand** ZS-D01 bis ZS-D10. [ZS-1/#52](https://github.com/venomenon328/picross/issues/52)
liefert die native Auswahl, [ZS-2/#53](https://github.com/venomenon328/picross/issues/53)
die [reguläre Integration](ZS2_VERIFICATION.md). Die [ZS-1-Studie](ZS1_VERIFICATION.md)
bleibt als isolierter Vergleich ausführbar; ZS-2 verwendet die bestätigte Kombination.

## 2. Bestätigte Entscheidungen und Referenzumgebung

| ID | Entscheidung für P1 | Stand und Grenze |
| --- | --- | --- |
| D-01 | Native Windows-Desktopfassung mit Godot Standard und typisiertem GDScript, Windows-11-Testplattform. | Kein C#/.NET-/Browserparallelweg; keine endgültige Produktstackentscheidung. Versionsbindung in Abschnitt 7. |
| D-02 | Reduzierte Spielprobe: reale Bearbeitung, Abschluss und später Speicherung; keine Sterne-/Fehlerwertung, Live-Fehlerhilfe oder Hypothesen. | Bestätigte Funktionen des späteren Produkts werden nicht gestrichen. |
| D-03A | Elastische Strichvorschau: Rückwärtsziehen verkürzt; Loslassen übernimmt eine atomare Aktion. | Unverändert, auch für die neuen Rücknahmestriche. |
| D-03B | Werkzeug und Modus bleiben je Strich eingefroren; kein Mehrfachtoggle beim Zurückziehen. | GP-01/#48 bindet zusätzlich die ursprüngliche Startzustandskategorie; unbekannter Start schützt Gegenmarkierungen. |
| D-04 | Hintergrundfelder müssen für den Abschluss nicht vollständig ausgekreuzt werden. | Richtige vollständige Füll-/Farbverteilung erforderlich. |
| D-05 | Referenz: Windows 11, 2560×1440, Maus, Ryzen 7 5800X, RTX 3070. | Frühere Nutzerangaben; tatsächliche Fenstergröße und Anzeigeskalierung der Probe noch nicht vollständig protokolliert. |
| D-06 | P1 wird mit Maus umgesetzt und abgenommen. | Tastatur-/Controllerbedienung und M-05 sind kein P1-Scope oder Gate; spätere alternative Produkteingaben bleiben erhalten. |
| D-07 | Größeres Standardfenster, nutzbar bei 1080p und 1440p, ohne automatische Riesenraster. | Fenster-/UI-Größe und Arbeitszoom getrennt; Abschnitt 5.2. |
| D-08 | Gefüllte Zellen bleiben auch an dicken Fünferlinien visuell getrennt. | Kontrast und Zwischenraum für alle vier Farben und Arbeitszoomstufen; keine verschmolzenen L-/Blockformen. |
| D-09 | Normales Werkzeug neutralisiert Füllungen mit links und Leermarkierungen mit rechts. | Grundregel der Rücknahmestriche; die frühere Gegenmarkierungs-Schutzregel ist durch D-15 abgelöst. |
| D-10 | Ergebnisbild darf deutlich detaillierter sein als das abstrahierte Rastermotiv. | Klar erkennbar dasselbe Motiv, keine Pflicht zu identischer Pixelmaske oder Bildauflösung; Abschnitt 5.4. |
| D-11 | An den Rasterrändern stehen keine laufenden Zeilen-/Spaltennummern. | Dort erscheinen ausschließlich Lösungshinweise beziehungsweise deren Überlaufmarker. Koordinaten bleiben separat im Arbeitsbereich sichtbar. |
| D-12 | Hinweise bleiben direkt im Arbeitsbild; keine separate Hinweisansicht. | Regulär passende Folgen werden vollständig gezeichnet. Physischer Überlauf erhält je betroffener Linie einen kompakten Marker und vollständigen farbigen Hover-Tooltip im Arbeitskontext. |
| D-13 | Arbeitszoom hat eine deutlich feinere monotone Stufenfolge. | Gesamtansicht bleibt separat; `+`/Rad hoch vergrößert nur, `−`/Rad runter verkleinert nur oder bleibt am jeweiligen Grenzwert. |
| D-14 | Farbhinweise zeichnen die Zahl selbst in der Rätselfarbe. | A–D-Suffixe sind standardmäßig aus und als optionale Accessibility-Darstellung einschaltbar. |
| D-15 | Links wandelt X direkt in die aktive Farbe, rechts eine Füllung direkt in X um. | GP-01/#48: Gegenmarkierungen nur bei Start auf diesem umzuwandelnden Zustand umwandeln; unbekannter Start schützt Vorbelegungen. Rücknahmestriche bleiben typspezifisch. |
| D-16 | Überlauf kürzt auf Ebene vollständiger einzelner Hinweise. | Ein unter direkter monotoner Draggeometrie und festen Markerplätzen maximal sinnvoller zusammenhängender Ausschnitt bleibt sichtbar; `…` markiert ausschließlich verborgene Präfixe/Suffixe. Tooltip nur ergänzend. |
| D-17 | Spalten- und Zeilenhinweisbereich sind unabhängig pannbar. | Spaltenfolgen nur vertikal, Zeilenfolgen nur horizontal; Rasterzuordnung, Rasteransicht und Spielzustand bleiben unverändert. |
| D-18 | Lösungshinweise zeigen ausschließlich vollständige einzeilige Zahlen in der Rätselfarbe. | Keine A–D-Suffixe, gestapelten Ziffern, Kompaktkästchen oder Umschaltoption; interne Farb-IDs und Mauspalette bleiben. |
| D-19 | Alle Folgen einer Orientierung verwenden ein gemeinsames regelmäßiges Hinweisraster. | Feste Slotmaße, rasterseitige Ausrichtung, ganze eingerastete Schritte und reservierte Markerslots statt variabler Textpackung. |
| D-20 | Jede konkrete Zeile und Spalte besitzt eine eigene Leseposition. | Achse und Linienindex werden am Gestenstart eingefroren; Nachbarfolgen bleiben unverändert. |
| D-21 | 1920×1080 ist primäre Layoutbasis und gewünschte Start-Clientfläche. | Gesamter Fensterrahmen bleibt im Arbeitsbereich; kleinere Fallbacks, stabile Arbeitszellen und getrennte UI-/Rasterskalierung bleiben. |
| D-22 | F-02 erhält wie F-01 ein eigenständiges verfeinertes Abschlussmotiv. | Leuchtturm, Bildaufbau, Proportionen und Farbverteilung bleiben klar zum Raster zugehörig; Rätsellogik bleibt unverändert. |
| D-23 | Nur die angefasste Hinweisfolge folgt während des Drags kontinuierlich der Maus. | Achse und Linie bleiben fest; beim Drop aus den unmittelbar zuvor sichtbaren Positionen derselben Zahlen die geometrisch nächste gültige ganzzahlige Slotlage wählen und erst dann den semantischen Lesezustand bestätigen. Markerwechsel dürfen keine zusätzliche Zahlenverschiebung erzeugen. Abbruch verwirft den temporären Versatz. |
| D-24 | Füllungen und Vorschau belegen geringfügig mehr Zellfläche. | Der kontrastierende Zwischenraum aus D-08 bleibt an normalen und kräftigen Fünferlinien in allen Farben und Arbeitszoomstufen erhalten. |
| D-25 | Die gültige Cursorzeile und -spalte werden im Raster dezent hervorgehoben. | Schnittpunkt nicht doppelt betonen; Inhalte und Linien bleiben lesbar. Ohne Zellgeste verschwindet das Band beim Verlassen der Rasterfläche. |
| D-26 | X und Preview-X werden an angeschnittenen Zellen geometrisch am Rasterviewport geclippt. | Normale X-Geometrie beibehalten, nicht in den sichtbaren Rest verschieben oder eine teilweise sichtbare Zelle pauschal verwerfen. |
| D-27 | Linke und rechte Zellgesten zeigen einen kleinen Live-Zähler der gesamten aktuellen Strichlänge. | Geometrisches gerades Segment inklusive Start/Ende und übersprungener oder vorbesetzter Zellen; elastisches Zurückziehen aktualisiert sofort. Keine Navigation und kein gespeicherter Zustand. |
| D-28 | Die kompakte Standardrasterfläche ist keine Zoom-Clippinggrenze. | Im nicht kompakten Buchlayout wächst der Rasterviewport erst oberhalb 100 % in freie Papierfläche; tatsächliche UI-/Papiergrenzen erzeugen den Ausschnitt. 20×20 bleibt bei 1920×1080/UI 100 % bis einschließlich 150 % vollständig sichtbar. |
| D-29 | Die Spielfläche erhält eine geometrisch präzise, charaktervolle zeichnerische Sprache. | Kräftige kompakte Hinweisziffern, stabile zurückhaltende Textur auf satten Farbflächen, handschriftliche X ohne zusätzliche Rand-UI; Stiftfüllung nach E1 gewählt, Chalkboard und kombinierte Darstellung nach ZS1-M01 bestätigt. |
| D-30 | Die Zellvorschau bleibt statisch und zeigt den Zielzustand heller beziehungsweise transparenter. | Nur wirksame Änderungen des elastischen Abschnitts; Rückzug/Abbruch unmittelbar, keine Animation der laufenden Vorschau. |
| D-31 | Zellanimationen beginnen erst beim tatsächlichen Anwenden des Strichs. | ZS2-E2 plus Tempo-Nacharbeit 09.10.2026: Setzen/Umwandeln gerichtet vom Start zum finalen Ende; Δ = min(12 ms, 180 ms/(m−1)) bei m > 1 wirksamen Zellen, 210 ms je Zelle, maximal 390 ms. Entfernen sofort/120 ms; Modell/History/Save warten nicht. |
| D-32 | Zellanimationen sind einfach abschaltbar. | P1-Ausarbeitungsdefault: aktiv nach App-Start, sitzungsweit, nicht im Rätselsave; Aus beendet Effekte sofort, Vorschau bleibt statisch. |
| D-33 | ZS1-E3 wählt Chalkboard Regular und kompaktere Zeilenhinweisabstände. | ZS-Studie: 26 × UI-Skalierung horizontale Zeilenslots links; vertikale Spaltenslots bleiben 18 × UI. Reguläre Integration in ZS-2. |

D-07 bis D-10 übernehmen die vier Punkte der ersten Nutzer-Mausprobe. D-11 bis D-15
übernehmen den ausdrücklich supersedierenden Sollstand der anschließenden P1.2-Probe.
D-16/D-17 ersetzen die vollständige Ganzfolgen-Ersetzung durch atomare Ausschnitte.
D-18 bis D-22 ersetzen anschließend die optionale A–D-Darstellung, variable
Hinweispackung, gemeinsame Bereichspositionen, den 1600×900-Start und die bloße
F-02-Rasterpräsentation. Soweit ältere D-07-/D-09-/D-14-/D-17- oder
Hinweisformulierungen widersprechen, gelten D-18 bis D-22. D-23 ersetzt ausschließlich
das alte schrittweise Einrasten während des Drags; der bestätigte Zustand bleibt
ein gemeinsamer ganzzahliger Slot.
D-10 präzisiert die bereits im Produkt-/Gestaltungskonzept erlaubte höhere
Detaillierung; es ist keine Freigabe für unabhängige Belohnungsbilder.

2560×1440 bezeichnet die gemeldete Bildschirmauflösung, nicht automatisch logische UI-Pixel oder 100 % Windows-Skalierung. Fehlende Testmetadaten nicht aus Screenshotabmessungen ableiten.

## 3. Ziel, Umfang und Nichtziele

**Untersuchungsfrage:** Kann der Nutzer große klassische und farbige Nonogramme präzise bearbeiten, darin navigieren und später nach Unterbrechung weiterarbeiten, ohne die Orientierung zu verlieren?

### 3.1 Enthalten

- Kleine Album-Testauswahl mit neutraler Kennung, Größe, Rätselart und Bearbeitungsstand. Alle Testfälle direkt zugänglich; keine Freischaltlogik.
- Zellbearbeitung, Farbwahl, Achsenbindung, elastische Vorschau, kontrollierte Rücknahmen sowie Undo/Redo.
- Arbeitsansicht mit unnummerierten, farbigen einzeiligen Hinweisen, atomaren Teilfolgen in einem gemeinsamen Slotraster und eigener Leseposition je Zeile/Spalte, passiver eigener Miniatur, fitbegrenztem Rasterzoom und getrennt skalierbarer Oberfläche.
- Mit #11 ein fortsetzbarer lokaler Arbeitsstand je Testfall einschließlich Ansicht und Undo/Redo.
- Tatsächlicher Abschluss und motivtreue, auch detailliertere Darstellung im Album.
- Tests, Start-/Bedien-/Resetanleitung, Windows-Testartefakte und nachvollziehbare manuelle Erprobung.

### 3.2 Nicht enthalten

Keine Sterneberechnung, Perfektionsanzeige, Fehlerstatistik, Rangliste, Freischaltungen, Bonuslogik, Live-Fehlerhilfe oder Hypothesen. Kein allgemeiner Solver, Produktionseditor, Bildimport, Community-Funktion, Audio, aufwendige Buchanimation, finale A/B-Entscheidung, Verbundraster oder Regionenregeln. Kein Hosting, Steam, Release, Installer, Cloudkonto oder kostenpflichtiger Dienst. Keine Tastatur-/Controllerbedienung, globale Tastenumbelegung oder vollständiges Accessibility-Optionsmenü. Der ausdrücklich vereinbarte Escape-Abbruch bleibt Teil des Mausgestenvertrags.

Die spätere Perfektionsregel „ohne Fehler und ohne Undo“ bleibt erhalten. P1 weist mangels Wertung keinen Durchgang als perfekt aus. Ob direktes Neutralisieren oder Radieren später wertungsrelevante Rücknahmen sind, bleibt offen. D-09 entscheidet Bedienung, nicht Fehlerzählung, Sterne oder Perfektion.

### 3.3 Gestaltung und Spoilergrenze

Warmes, ruhiges handgezeichnetes 2D-Album mit klaren Konturen und Farbflächen. Thematik dezent im Arbeitsbildschirm; das Raster bleibt geometrisch präzise und verwendet die über ZS2 integrierte gezeichnete Darstellung. Keine Buchfalte, Dekoration oder unleserliche Handschrift über Arbeitszellen/Hinweisen. Sammelalbum und Reisealbum bleiben offene Themenalternativen. Der Squeakross-Vergleich ist keine UI- oder Assetvorlage; Details in [Zeichensprache](UI_DRAWING_STYLE.md).

Vor Abschluss weder fertiges Motivbild noch Motivname oder verräterischer Albumplatzhalter. Während des Lösens stets eine Miniatur nur des eigenen Zustands einschließlich Fehlern. Mocks sind Stilreferenzen, keine gültigen Rätseldaten oder vorweggenommenen Produktabnahmen.

## 4. Testdaten und Datenvertrag

| Kennung | Testfall | Zweck und Nachweis |
| --- | --- | --- |
| F-01 | 20×20 monochrom | Grundbedienung, Rücknahmeregression und mit #9 sichtbar detailliertere motivtreue Enthüllung. Bestehende logische Lösung und Hinweise beibehalten. |
| F-02 | 40×40 mit vier Farben | Farbwahl, direkt angrenzende verschiedenfarbige Blöcke, lange Hinweise, vollständiger spielbarer Abschluss und verfeinertes motivtreues Leuchtturmbild. |
| F-03 | Vollständig navigierbares 100×100-Stressraster | Großraster und lange Hinweise, kein statisches Ausschnittbild. Sichtbar „UI-Testdatensatz – Rätselqualität nicht abgenommen“. |
| F-04 | 20×20 monochrom aus realer Bilddatei | RP-3-Dateiimport, unabhängig geprüfter Produktionsnachweis, neuer regulärer Spielablauf und motivtreue eigene SVG-Enthüllung. Neutraler Name vor Abschluss. |

F-01/F-02 dürfen einfach sein, benötigen aber ein erkennbares Motiv, geklärte Herkunft und eine endliche überprüfbare Deduktionsfolge ohne zusätzliche Startfelder oder notwendiges Raten. Eine Lösung oder passende Zahlen allein beweisen das nicht. Kein allgemeiner erklärender Solver beauftragt. F-03 erlaubt keine ungeprüften regulären Produkträtsel.

Randfälle: leere Linie, voller Block, gleichfarbige Blöcke mit notwendigem Abstand, direkt angrenzende verschiedenfarbige Blöcke, lange vollständige Hinweisfolge. Für F-02 keinen monochromen Nachweis ungeprüft wiederverwenden. Die Nachweisprüfung darf Linienmöglichkeiten untersuchen, aber keine Rasterannahmen als Deduktion ausgeben.

Definition und Spielerstand getrennt; P1-intern JSON, keine Datenbank. Stabile ID/Revision, Dimensionen, Palette mit stabilen Farbkennungen, Lösungsmatrix, vollständige Zeilen-/Spaltenhinweise sowie erst nach Abschluss sichtbare Motivdaten. Intern nullbasierte Indizes von oben/links; UI einsbasiert.

Zellen: `unbekannt`, `leer`, `gefüllt(Farbkennung)`. Farbindizes unabhängig von Darstellungsfarben. Hinweise aus Lösung reproduzierbar: gleiche Farben benötigen Abstand, verschiedene dürfen direkt angrenzen. Gespeicherte Hinweise gegen Ableitung prüfen. Dimensionen, Matrixform, Wertebereiche, Versionen und Farbverweise validieren; Leerlinie eindeutig darstellen.

**Abschlussressource ab #9:** Auflösung und Detailgrad unabhängig von den Rätseldimensionen. Der Validator prüft Format/Version, vorhandene und gültige Bilddaten beziehungsweise lokale Ressourcen und Zuordnung zur Definition, nicht pixelidentische Belegung zur Lösung. Motivtreue wird durch visuellen Vergleich geprüft. Fehlende/defekte Ressourcen nicht still durch ein fremdes Bild ersetzen. Geändertes Schema, Fixtures, Loader, Tests, Exportfilter und Dokumentation gemeinsam aktualisieren; Revisions-/Zertifikatbezüge von F-01 konsistent halten. Keine Änderung seiner Lösung nur für eine reichere Illustration. Keine Spielstandmigration aus #11 vorwegnehmen.

## 5. Interaktionsvertrag

### 5.1 Werkzeuge, direkte Umwandlung und Strichgrenzen

Beim normalen Werkzeug bestimmt die Maustaste zusammen mit dem **bestätigten Startzellzustand** einmalig den Aktionsmodus:

[GP-01 / Issue #48](https://github.com/venomenon328/picross/issues/48) ersetzt
für diesen Stand die bisherigen D-15-Setzregeln. Bewertung immer aus dem ursprünglichen
Zellsnapshot; gefüllt ist eine Kategorie unabhängig von der Farb-ID.

| Start / Taste | Unbekannte Zelle | X | Füllung |
| --- | --- | --- | --- |
| Unbekannt / links | Aktive Farbe | Geschützt | Geschützt |
| Unbekannt / rechts | X | Geschützt | Geschützt |
| X / links | Aktive Farbe | Aktive Farbe | Geschützt |
| X / rechts | Unverändert | Unbekannt | Geschützt |
| Gefüllt / links | Unverändert | Geschützt | Unbekannt, auch andere Farben |
| Gefüllt / rechts | X | Geschützt | X, auch andere Farben |

Einzelklicks sind Gesten der Länge eins; bewusste X↔Füllung-Umwandlung bleibt
möglich. Vorhandene Füllungen werden links nicht direkt umgefärbt. Startzustand,
Taste, Modus und aktive Farbe bleiben auch bei Rückzug und G1-Achsenneuwahl fest.

Der explizite Radierer bleibt als Universalwerkzeug: links setzt alle vorhandenen Markierungen auf unbekannt. Rechts folgt weiterhin der Leer-/Leerrücknahme-Regel. Das Hand-Werkzeug entfällt mit VS2. Werkzeug, Aktionsmodus und Setzfarbe bleiben bis zum Ende der Geste eingefroren; keine Neuerkennung pro überfahrener Zelle und kein wiederholtes Umschalten beim Rückwärtsziehen.

Die erste eindeutige Bewegung in eine andere Zelle verriegelt horizontal oder vertikal. Bei diagonalem Gleichstand bleibt nur die Startzelle in der Vorschau, bis eine Richtung dominiert. Trifft die aktive Zellgeste die tatsächliche Startzelle wieder, verkürzt sich die Vorschau auf diese Zelle und die Achse wird ohne Loslassen freigegeben. Die nächste eindeutige Bewegung wählt sie erneut; dies kann innerhalb derselben Geste mehrfach geschehen. Sonst bleibt die Achse fest und der Strich gerade. Eingabesprünge erfassen alle Zwischenzellen des aktuellen Abschnitts, schalten die Achse aber ohne gelieferten Startzelltreffer nicht frei. Ein nur auf die Achse projizierter Endpunkt am Start genügt ebenfalls nicht.

Die elastische Vorschau wird aus dem bestätigten Zustand am Gestenbeginn und dem aktuellen geraden Abschnitt berechnet. Zurückziehen verkürzt auch Rücknahmestriche; außerhalb des Abschnitts erscheint der unveränderte Ausgangszustand wieder. Eine Startüberquerung ohne tatsächlichen Treffer bleibt auf derselben Achse; nach einem Treffer ist eine neue Achsenwahl möglich. Ursprung, Modus, Werkzeug und Setzfarbe bleiben dabei eingefroren. Loslassen übernimmt nur wirksame Änderungen atomar. Beispiel 5→12→9 bearbeitet nur 5–9 nach dem eingefrorenen Modus. Keine Abschlussprüfung aus der Vorschau.

**D-30/D-31, freigegebener ZS-Sollstand:** Während des Ziehens erscheinen nur
wirksame Zielmarkierungen statisch, heller beziehungsweise transparenter. Erst die
tatsächliche Übernahme bei Mouse-Up startet die gerichteten Effekte der wirksam
geänderten Zellen gemäß ZS2-E2; keine Animation in der Vorschau und kein Warten auf ihre
Fertigstellung. Neue wirksame Vorschau hat zellweise Vorrang vor älteren Effekten.
Neutralisierung zeigt bereits unbekannt mit dezenter statischer Vorschaukontur;
keine alte Markierung für einen späteren Löscheffekt wieder einblenden. Vollständige
Prioritäts-/Abbruch-/Lebenszyklusregeln stehen in [ZS-D06 bis D09](UI_DRAWING_STYLE.md).

Während einer linken oder rechten Zellgeste zeigt ein kleiner Zähler am aktuellen
Strichende, am Viewportrand nach innen versetzt, die geometrische Länge des aktuellen
geraden Abschnitts einschließlich Start und Ende. 5→12 zeigt 8, zurück auf 9 zeigt 5,
ein Einzelfeldabschnitt zeigt 1. Vorbelegungen und Eingabesprünge verkürzen den Zähler
nicht. Nach Übernahme oder Abbruch verschwindet er; Navigation zeigt keinen Zähler.

Escape oder Fokusverlust verwirft vollständig. Außerhalb des sichtbaren Rasterbereichs bleibt der letzte gültige Endpunkt stehen. Kein Zeichnen unter UI-Flächen, kein Auto-Scrollen, kein Zoom/Pan während Zellgesten. Werkzeug-/Farbwechsel wirken frühestens in der nächsten Geste. Reguläres Verlassen verwirft eine laufende Vorschau vor einem späteren Speichern.

Ein wirksamer Strich ist ein Undo-Schritt; Redo stellt exakt wieder her. Neue wirksame Änderung nach Undo verwirft den Redo-Zweig; No-ops nicht. Navigation ist keine Zellaktion. Direktes Neutralisieren wird als normale Bearbeitungsaktion rückgängig machbar, ruft nicht heimlich Undo auf und löscht kein bestehendes Undo-verwendet-Merkmal. Keine Wertungsentscheidung daraus ableiten.

### 5.2 Fenster, Zoom, Hinweise und Miniatur

VS2 ersetzt die früheren Pan-/Miniaturverträge. Die aktuellen Regeln stehen oben
und in der nachfolgenden Bedienung; frühere Berichte bleiben historisch.

D-21 präzisiert D-07: 1920×1080 ist die primäre Layoutreferenz und die gewünschte
Clientfläche beim Fensterstart, soweit diese einschließlich des tatsächlichen Rahmens
in den verfügbaren Monitorarbeitsbereich passt. Andernfalls wird die Clientfläche so
begrenzt, dass der ganze Rahmen sichtbar bleibt. Kein Vollbildzwang, Offscreen-Start
oder Eingriff in Windows-Einstellungen. 1280×720 bleibt Mindest-/Fallback-Test,
1600×900 kleinerer Regressionstest und 2560×1440 unterstützte größere Fläche.

Arbeitszoom, UI-/Hinweisskalierung und Fenstergröße sind getrennt. Technischer Ausgangswert: 24 logische Einheiten Zellabstand bei 100 % Arbeitszoom; eine begründete Feinanpassung nach Darstellungstests ist reversibles Implementierungsdetail. Vergrößern/Maximieren des Fensters vergrößert bei gleichem Zoom und UI-Maßstab nicht automatisch die Zellen. Stattdessen mehr Raster zeigen oder kleine Raster mit ruhigen Rändern platzieren. Eine ausdrücklich gewählte Gesamtansicht ist vom Arbeitszoom zu unterscheiden; „Arbeitsgröße“ stellt eine brauchbare Bearbeitungsgröße wieder her.

VS2 löst die frühere D-28-Erlaubnis von Ausschnitten oberhalb 150 % ab.
Mausrad und Zoomknöpfe bleiben monoton und stoppen am aktuellen Fit einschließlich
Außenrahmen. Einpassen erreicht diesen Fit im gewählten Modus; Arbeitsgröße wünscht
24 Pixel. Die gültige Schema-1-Stufenfolge bleibt
`12/14/16/18/20/22/24/26/28/30/32/34/36/40/44/48/54/60/66/72`.
Berechnete Fitwerte können darunter oder dazwischen liegen. Kein Rasterpan,
Hand-Linkszug oder Miniaturklick/-drag; auch 100×100 nutzt nur Vollsicht und kann
als eingeschränkt oder geometrisch nicht bedienbar gemeldet werden. Optionen und
Rückweg bleiben erreichbar. Gemeinsame Draw-/Hit-Geometrie, keine Zell-/Historymutation.

D-08: Füllungen haben zu anderen Füllungen und insbesondere den Fünferlinien einen sichtbar kontrastierenden Zwischenraum. Dunkle Füllung und dunkle Linie dürfen an Kreuzungen nicht zu einer gemeinsamen L-/Blockform verschmelzen. Fünfergruppen bleiben erkennbar; Umrissstärke, Füll-Inset und Renderingreihenfolge gemeinsam abstimmen. Dies gilt für alle vier Farben, Vorschau und die angebotenen Bearbeitungszoomstufen. Eine verdichtete Gesamtansicht ist kein Ersatz für diese Arbeitsansicht. Zeichnung und tatsächliche Trefferflächen bleiben korrekt zugeordnet.

D-24 vergrößert die Füllfläche geringfügig innerhalb dieser Trennungsgrenze. D-25
betont die gültige Cursorzeile und -spalte als dezente Hintergrundbänder nur im
sichtbaren Raster. Die Kreuzung erhält dieselbe Stärke wie jedes Band; Füllungen,
X, Vorschau und Rasterlinien werden darüber gezeichnet. D-26 clippt die normalen
X-Liniensegmente bestätigter und vorläufiger Leermarkierungen am Viewportrand,
auch bei nur teilweise sichtbaren Zellen und Ecken. Wo kein X-Segment den sichtbaren
Rest schneidet, entsteht keine Ersatzmarkierung.

Hinweise beziehen sich stets auf ganze Zeilen/Spalten und sind korrekt zugeordnet,
aber nicht zusätzlich laufend nummeriert. Aktive Linie und die separate Koordinatenanzeige
unterstützen die Orientierung. Sie zeigen nur vollständige einzeilige Zahlen in der
jeweiligen Rätselfarbe; mehrstellige Zahlen bleiben horizontal und ungeteilt. Für P1
gibt es keine A–D-Suffixe, gestapelten Ziffern, Kompaktkästchen oder entsprechende
Umschaltoption. Die internen Farb-IDs bleiben unverändert. Z2 ersetzt die frühere
A–D-beschriftete Mauspalette durch unbeschriftete Originalfarbfelder mit formaler
Auswahlmarkierung; Status und Tooltip nennen die jeweilige Farbnummer.

Alle Zeilenfolgen verwenden dieselben festen horizontalen Hinweisplätze, alle
Spaltenfolgen dieselben festen vertikalen Reihen. Die gemeinsame Slotgeometrie wird
je Orientierung und aktueller Ansicht bestimmt, bleibt von individuellen Zahlenbreiten,
Folgenlängen und Kürzungszuständen unabhängig und ist quer zur Folge exakt der
Rasterzeile/-spalte zugeordnet. Kurze Folgen und `–` stehen rasterseitig rechts
beziehungsweise unten. Bei Überlauf bleibt ein maximal sinnvoller zusammenhängender
Ausschnitt vollständiger Tokens in unveränderter Reihenfolge sichtbar, unter Wahrung
direkter monotoner Draggeometrie und fester Markerplätze. `…` belegt
einen festen Randplatz nur auf tatsächlich verborgenen Seiten. Keine zusätzlichen
sichtbaren Hinweisgitterlinien.

Jede konkrete Zeile und Spalte besitzt eine eigene ganzzahlige bestätigte Leseposition.
Nur die mittlere Taste friert Achse und Linienindex am
Gestenstart ein. Während des Drags bewegt sich nur die angefasste Folge kontinuierlich
entlang ihrer Achse, auch zwischen Slots; beim Loslassen rastet sie auf die nächste
gültige ganzzahlige Position ein. Escape, Fokusverlust oder regulärer Übergang
verwerfen den temporären Versatz und erhalten die letzte bestätigte Position.
Die Eigentümerentscheidung Variante A zu #11/R7 priorisiert den geometrisch nächsten
Snap und direkte monotone Manipulation. Der geometrische Außenanschlag ist selbst
`outer_start`; dort darf ein physisch möglicher Tokenplatz frei bleiben, wenn seine
Belegung die Zahlen entgegen der bisherigen Dragrichtung verschieben würde.
Es gibt keinen zusätzlichen, nur durch Gegenbewegung erreichbaren Randzustand.
Wiederholtes Ziehen mit gleichem Vorzeichen führt vom Rasterende bis zum äußeren
Anfang; der Rückweg verwendet durchgehend das Gegenzeichen. Die Darstellung wird
bereits während des Drags an diesen geometrischen Grenzen begrenzt. Alle Tokens
müssen über die erreichbare Zustandsfolge vollständig lesbar bleiben.
Überfahren benachbarter Linien, des
Rasters oder anderer UI übernimmt keine andere Folge und wird weder Raster-Pan noch
Zellbearbeitung. Leere/kurze Folgen pannen nicht in leeren Raum. Anfang, Mitte und Ende
jeder langen Folge bleiben erreichbar; „Hinweise rasterseitig ausrichten“ setzt alle
Einzelpositionen bewusst zurück.

Die wirkungslosen Raster-/Miniaturnavigationsversuche erhalten sämtliche individuellen Lesepositionen.
Zoom, Resize und UI-Skalierung bewahren denselben gelesenen Bereich soweit möglich,
begrenzen danach gültig und bleiben auf dem gemeinsamen Slotraster. Beim bewussten
Testblattwechsel wird ab P1.3 die individuelle Hinweisansicht des Zielblatts
wiederhergestellt; nur dessen bestätigter Reset initialisiert sie neu.

Während einer Zellgeste ist Hinweisnavigation gesperrt. Freigabe, Escape und
Fokusverlust beenden sie; falsche Tastenfreigabe nicht. Hinweis-Panning verändert
weder Zellen/Preview, History/Undo-Metadatum oder Abschluss noch Rasterzentrum,
Rasterzoom oder Miniaturrahmen. Darüberfahren einer gekürzten Folge zeigt weiterhin
die vollständige farbige Folge als umbrechenden Tooltip im Arbeitsbild. Dieser ist
Ergänzung, nicht der einzige Zugriff; es gibt keinen eigenen Hinweisbildschirm oder
modalen Ersatzdialog. Keine automatische Fehler-/Erfüllungsmarkierung durch
Lösungsvergleich. Manuelles Hinweisabhaken ist nicht erforderlich.

**H1 / [Issue #19](https://github.com/venomenon328/picross/issues/19):** Die optionale,
standardmäßig aktive Erfüllungsmarkierung analysiert ausschließlich vollständige
Linienwerte und deren geordnete Längen-/Farbhinweise. Unbekannt bleibt offen, X ist
leer, eine Füllung legt die Farbe fest. Gleichfarbige Nachbarblöcke benötigen Abstand,
verschiedenfarbige dürfen angrenzen. Ein Hinweis ist genau dann erfüllt, wenn es
mindestens eine kompatible vollständige Linienbelegung gibt, sein Block in allen
solchen Belegungen dasselbe Intervall hat und dieses bereits vollständig in der
richtigen Farbe gesetzt ist. Eindeutig erzwungene, aber noch unbekannte Zellen genügen
nicht. GP-02/#48 unterscheidet jetzt drei Anzeigezustände: normal (offen),
leicht abgeschwächt (eindeutig vollständig gesetzt), durchgestrichen (zusätzlich
beidseitig abgegrenzt). Ein mehrdeutiger Mittelblock bei `3 3` bleibt auch
mit Rand-X normal. Existiert keine kompatible Belegung, bleiben alle Hinweise
dieser Linie unmarkiert. Andere Linien werden unabhängig bewertet.

Keine Verwendung von Lösung, Reveal, Abschluss, Fehlerstatistik, Proof oder kreuzenden
Hinweisen; auch ein gegenüber der Lösung falsch platzierter, linienintern eindeutiger
Block wird markiert. Keine automatischen Zellen oder zusätzliche Widerspruchsanzeige.
Die Markierung folgt `visible_cells()` einschließlich elastischer Vorschau und wird
nach Rückzug, Abbruch, Commit, Undo/Redo, Blattwechsel, Reset, Restore und Recovery
frisch abgeleitet. Die nebenwirkungsfreie Analyse verwendet begrenzte dynamische
Programmierung statt vollständiger Enumeration. Ein Cache hält nur den letzten
Eingang jeder Linie; reine Geometrie-/Hover-/Panänderungen starten keine neue Suche.

Für das Durchstreichen muss jedes Ende unmittelbar an X, den tatsächlichen
Linienrand oder eine vorhandene Füllung mit anderer Farb-ID grenzen. Gemischte
Abgrenzungen sind erlaubt; der andere Farbblock muss nicht selbst vollständig sein.
Unbekannte Nachbarn, entfernte X und Ausschnittränder aus Zoom/Pan zählen nicht.
Die exakte widerspruchsfreie eindeutige Zuordnung bleibt für beide positiven
Zustände erforderlich; keine neue Farb-/Abstandsregel und keine Auskreuzpflicht
für den Rätselabschluss.

Die integrierte GP-03-Baseline zeichnet alle Hinweiszahlen kräftiger mit dem vorhandenen
Plex-Sans-Variationsgewicht 600 bei bisherigem Schriftgrad. Der ZS-Folgevertrag
öffnet gezielt die Hinweisziffern für eine native Auswahl von Form, Gewicht, optischer
Größe und gegebenenfalls bewusst gewählten gemeinsamen Slotmaßen; bis zu dieser
Umsetzung bleibt die Baseline der Iststand. Der gesetzte,
noch offene Block erhält 78 % Deckkraft, die Rätselfarbe und C1-Kontur bleiben
erkennbar. Abgegrenzte Zahlen werden durchgestrichen. Alle drei Zustände behalten
Größe, Slot und Originalindex. Das gilt für beide Achsen, Überlauf,
kontinuierlichen Drag und vollständigen Tooltip. `…` und `–` bleiben unverändert.
Der Schalter „Erfüllte Hinweise markieren“ gilt sitzungsweit für alle Blätter, bleibt
bei Album-/Blattwechsel und Reset erhalten und startet nach App-Neustart wieder an.
Aus zeigt alle Zahlen ohne Abschwächung/Strich, erneutes Einschalten den aktuellen Stand. Schalter und
Analyse erzeugen weder Rasteraktion noch History, `undo_used`, Save/Autosave oder
Abschluss und verändern keine semantische Leseposition. Flags und Option gehören
nicht zum Puzzle-Saveformat; Pflicht-Flush und Recovery bleiben unverändert.

Die stets sichtbare Miniatur enthält nur Spielerzustand und gegebenenfalls dieselbe
Vorschau, keine korrigierte Lösung. Unbekannt/leer/gefüllt unterscheidbar; richtige
Rätselfarben darstellen. Ein Ausschnittrahmen zeigt den Viewport. Klick/Ziehen navigiert
ohne Zellmutation. Die Z2-Mauspalette zeigt unbeschriftete Farbfelder mit stabilen
internen Farb-IDs und unveränderten RGB-Innenflächen. Eckmarkierungen außerhalb
der Farbfläche kennzeichnen die Auswahl; Status und Tooltip nennen „Farbe 1“ bis
„Farbe 4“. Farbwahl aktiviert Füllen, auch nach Radierer. Diese Darstellung
ersetzt die vorläufige A–D-Beschriftung, nicht die Farb-IDs oder Hinweisregeln.
Auswahl/Fokus/Leerzustand dürfen keine zusätzliche Rätselfarbe vortäuschen.
Keine beliebigen Nutzerpaletten.

Layouttests umfassen 1280×720, 1600×900, die primäre 1920×1080-Fläche und 2560×1440
als logische Testflächen. Reale Windows-Bildschirmauflösung, Fenster-/Clientfläche,
Rahmen und Anzeigeskalierung zusätzlich getrennt protokollieren; logische Tests sind
kein Nachweis physischer DPI-Verhältnisse. Keine versteckten Werkzeuge/Hinweise; unter
der Mindestfläche klare Meldung statt beschädigtem Layout.

### 5.3 Alternative Eingaben außerhalb P1

D-06 stellt Tastatur-/Controllerbedienung für P1 zurück. Kein Controllergerät/-Tester und keine entsprechende Abnahme erforderlich. [Issue #10](https://github.com/venomenon328/picross/issues/10) ist für P1 entfallen. Produktweite alternative Eingaben bleiben davon unberührt. Escape ist weiterhin der vereinbarte optionale Abbruchweg einer Mausgeste.

### 5.4 Abschluss und detaillierteres Ergebnisbild

Nach einer übernommenen Aktion gilt das Rätsel genau dann als gelöst, wenn jede Motivzelle in der richtigen Farbe gefüllt ist und jeder Lösungshintergrund unbekannt oder leer markiert ist. Zusatzfüllung, fehlende Füllung, falsche Farbe oder leer markierte Motivzelle verhindern den Abschluss. Keine Fehlermeldung, Prozent-richtig-Anzeige oder korrigierte Miniatur vor dem vollständigen Treffer.

Danach Abschlussansicht „Prototyp ohne Wertung“, Motivname und fertiger Albumeintrag. D-10: Das Ergebnisbild darf höhere Auflösung, feinere Konturen, zusätzliche Oberflächendetails, Schattierungen und kleine passende Motivelemente besitzen. Das Rätsel muss sehr deutlich als Stilisierung dieses Bilds erkennbar bleiben: gleicher Hauptgegenstand, nachvollziehbarer Bildaufbau, wesentliche Formen und Proportionen. Keine unabhängige Belohnungsillustration, aber auch keine Pflicht zu identischen belegten Rasterzellen.

#9 demonstriert diese Richtung an den eigenständigen Ergebnisbildern von F-01 und F-02.
Das positiv bestätigte F-01-Segelboot bleibt die Stil-/Abstraktionsreferenz. F-02 zeigt
denselben Leuchtturmaufbau wie das Raster – Sonne oben links, Turm rechts, Wasser unten
und dieselbe dominante Farbverteilung – mit feineren Architekturkonturen, Laterne,
Turmbändern, Oberflächen- und Wasserdetails. Bloßes Hochskalieren/Umfärben desselben
Pixelbilds genügt für keines der beiden Motive. Lösungen, Hinweise und die 48/80
Deduktionsschritte bleiben logisch unverändert. Eine allgemeine Assetpipeline oder
Pflicht-Neuzeichnung aller späteren Rätsel folgt daraus nicht. F-03 ist auch nach
Solltreffer ausdrücklich technischer Test, kein kuratiertes Rätsel.

## 6. Speicherung und Wiederaufnahme

P1.3 verwendet ausschließlich `user://p1/saves/` mit aus den neun fest registrierten Inhalts-IDs gebildeten Dateinamen. Schema 1 speichert je Blatt Definitions-ID und -Revision, Dimensionen, bestätigte flache Zellmatrix, vollständige wirksame History samt Redo-Zweig/Cursor und bleibendem `undo_used`, Abschlussstatus, Rasterfokus in Zellkoordinaten, gewünschte gültige Arbeitszoomstufe und Einpassen-Flag (overview), aktive Farbe/Werkzeug sowie individuelle semantische `row_clue_reads` und `column_clue_reads`. Nicht gespeichert werden laufende Gesten, Lösung/Reveal, Wertung, Fehlerstatistik, UI-Skalierung, Fenstergeometrie, Miniaturrahmen oder konkrete Hinweis-Slot-Offets.

Vor Anwendung werden Schema, exakte Definition/Revision, Matrix/Palette, jede nichtleere atomare History-Aktion mit eindeutigen Indizes und gültigen Vor-/Nachwerten, das widerspruchsfreie Replay ab unbekanntem Raster einschließlich Redo, Cursor-Matrix-Gleichheit, `undo_used`, Abschluss und View vollständig geprüft. Unbekannte oder unpassende Daten werden weder teilweise geladen noch still migriert. Der Rasterfokus wird bei Resize gültig begrenzt; Hinweis-Offsets werden aus Rasterende, äußerem Anfang oder mittlerem Tokenfenster für die aktuelle Geometrie neu abgeleitet.

Jede wirksame bestätigte Zellaktion und Undo/Redo werden sofort gesichert; Werkzeug/Farbe ebenfalls. Reine Ansicht darf kurz gebündelt werden, wird aber vor Album, Blattwechsel, Beenden und regulärer Window-Close-Anforderung geflusht. Vorschau wird zuerst verworfen. Fehler erscheinen sichtbar und dürfen keinen gesicherten Stand vortäuschen.

Schreiben erfolgt als vollständige Tempfassung im selben Speicherroot mit Flush, Schließen und erneuter Parse-/Vertragsvalidierung. Nur ein gültiges bisheriges Primary wird als genau eine gültige Backupfassung rotiert; erst danach ersetzt der Kandidat das Primary. Ein Abbruch lässt wenigstens die vorherige gültige Fassung ladbar. Ein verwaistes Tempfile wird nicht geladen. Gültiges Primary hat Vorrang; bei fehlendem/defektem Primary wird ein gültiges Backup sichtbar geladen. Defekte oder inkompatible Fassungen werden nicht still überschrieben; das bewusste Übernehmen eines gültigen Backups erlaubt wieder Speichern. Bei gültigem Primary und defektem Backup wird der Primärstand geladen; eine bestätigte Backup-Erneuerung erlaubt wieder Speichern. Ohne gültige Fassung erscheint ein Fehlerzustand. Der bestätigte Reset entfernt ausschließlich Primary, Backup und Temp des ausgewählten Blatts und setzt nur dessen Session zurück.

Tests verwenden ausschließlich eigene temporäre User-Daten; ein echter Zwei-Prozess-Roundtrip gehört zum Produktweg. Dies ist keine Produktmigration oder Zusicherung zukünftiger Save-Kompatibilität. Ein fehlgeschlagener Pflicht-Flush blockiert Album, Blattwechsel, Beenden und Window-Close bis zu einem erfolgreichen Retry. Ein aus gültigem Backup geladener Stand bleibt auch bei fehlendem Primary bis zur bewussten Übernahme schreibgesperrt. Temporäre Hintdrag-Subslots, Hoverbänder und Strichzähler gehören nicht zum Save.
Im Album zeigt jedes ungelöste Blatt ausschließlich seine eigene gespeicherte
Spielerminiatur unter neutralem Blattnamen; nur ein valider abgeschlossener Slot
zeigt die bisherige Motiv-/Abschlussdarstellung.

## 7. Technikbindung und Prüfweg

### 7.1 P1-Technik

Godot Standard **4.7.2-stable** mit typisiertem GDScript, passenden Standard-Exportvorlagen und Windows-x86_64-Testexport. Kein .NET-SDK oder Runtime-Backend. Primärquelle: [offizieller Release](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable). Der gebundene Editor-/Template-/Hash-/CI-Weg ist durch [P1.0](P1_PREFLIGHT.md) nachgewiesen. Kein ungeprüfter Wechsel zu `latest`; Archive vor Verwendung prüfen, nicht einchecken oder global installieren.

Projektpfad `prototypes/p1/`. Eigene Rasterzeichen-/Hit-Test-Komponente, UI-Bausteine für Menüs/Palette/Fokus. Raster-/Aktionsmodell, Ansichtskoordinaten und später Speicherung getrennt testbar. Keine Abstraktionsplattform für hypothetische Engines oder unnötigen Drittanbieterabhängigkeiten. Deutsche UI, keine vollständige Lokalisierungsinfrastruktur.

### 7.2 Ausführbarer Befehlsvertrag

Für Auslöser, Umfang, Größen-/Zeitbudgets und Artefakte gilt ab #63 die
[CI-Policy](CI_POLICY.md). Sie löst die pauschale Wiederholung historischer
Studien und aller früheren Lieferprüfungen ab; die fachlichen Verträge dieser
Spezifikation bleiben bestehen. Aktuelle Regression, technische Abnahme und
historische Nachweise werden getrennt ausgewiesen.

Die folgenden Bestandteile existieren aus #8; #9 erweitert deren tatsächlichen Prüfumfang. `godot` bezeichnet den gebundenen Standard-Editor, unter Windows dessen Konsolenprogramm. Vollständig isolierter Prüfweg in der [Anleitung](../prototypes/p1/README.md).

```sh
godot --version
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
godot --headless --path prototypes/p1 --export-debug "P1 Windows x86_64" build/windows/picross-p1.exe
```

Der Testrunner führt vereinbarte Logikprüfungen aus, gibt Anzahl/Ergebnis aus und endet bei Fehler mit Fehlerstatus. Import-, Start- und Exportfehler sind Fehlschläge. Begrenzte Laufzeiten; isolierter Speicher bei Tests/Smoke. Technischen Start-Smoke und reale GUI-Erprobung trennen.

Exportpreset exakt `P1 Windows x86_64`; vorher passende Templates und `prototypes/p1/build/windows/` anlegen. Exportpfad relativ zum Godot-Projekt. ZIP mit allen Startdateien, Anleitung und Commitkennung; keine Godot-Installation beim Nutzer voraussetzen. Keine Signaturzertifikate, Releases oder Änderung von Windows-Schutzfunktionen beauftragt.

`tools/p1_product.py` und [Produkt-CI](../.github/workflows/p1-product.yml) liefern Import, aktuelle Godot-Tests, kurzen absichtlichen Negativtest, echten Save-Roundtrip, kontrollierten Start und Windows-Export; unter Windows zusätzlich exportierten Start. `--integration`, `--pilots` und `--visual` wählen die nach CI-Policy erforderlichen ergänzenden Wege; bei lokalem Aufruf sind alle standardmäßig aktiv. Der Preflight wird bei Toolchain-/Harnessänderungen und auf manuellen Auftrag ausgeführt. Aktuelle Head-/Basis-/Test-Merge-/Artefaktzuordnung im PR; alte grüne Prüfungen belegen nicht die neuen Funktionen.

## 8. Akzeptanz und Abnahme

### 8.1 Automatisiert durch Implementierer / CI

Die folgende Zuordnung beschreibt die fachlichen Prüfeigenschaften. Die
verbindliche Auswahl pro Änderung, kompakte native Grenzmatrix und abschließende
Erfolgsprüfung stehen in [CI-Policy #63](CI_POLICY.md). Eine deaktivierte
optionale Route wird als nicht zutreffend ausgewiesen, nicht als ausgeführt.

| ID | Prüffall und Erfolg |
| --- | --- |
| A-01 | Definitionen/Hinweise einschließlich Farben, Leerlinien und ungültiger Daten validieren; F-01/F-02 mit Deduktionsfolge, F-03 als Stressfixture. Abschlussressourcen technisch unabhängig von Rasterauflösung prüfen. |
| A-02 | Setz-/Neutralisierungs-/Radiergesten: direkte Füllung↔X-Umwandlung, Achsenbindung und erneute Wahl nur nach tatsächlichem Startzelltreffer, diagonaler Start, Sprünge ohne Starttreffer, elastisches Zurückziehen, gemischte Vorbelegung, Rand/UI, Abbruch und No-op. Nur zum eingefrorenen Modus passende Zellen ändern sich. |
| A-03 | Atomarer Strich, exakte Vorzustände bei Undo/Redo, korrekte Verzweigung; Neutralisieren nicht als versteckten Undo-Aufruf behandeln. |
| A-04 | Gemeinsame Ansichts-/Hit-Test-/Miniaturtransformation bei fitbegrenztem Zoom, negativen Raster-/Miniaturpanversuchen, UI-Skalierung und Resize; echte Mauspfade bewegen nur die konkret gestartete Zeile/Spalte kontinuierlich und rasten beim Drop in gemeinsame Slots ein, einschließlich Abbruch/Grenzen. Navigation mutiert keine Zellen. Zellgröße bleibt bei reinem Resize im Arbeitszoom stabil. |
| A-05 | Mit #11 Speicherung/Recovery ohne stillen Datenverlust oder fremden Zugriff. |
| A-06 | Unkorrigierte eigene Miniatur, keine frühen Motivdaten, richtiger Abschluss mit unbekanntem Hintergrund, kein Abschluss bei Zusatz-/Fehl-/Falschfüllung oder leerer Motivzelle. Detailliertere Ressourcen ändern die Abschlusslogik nicht. |
| A-07 | Import, begrenzter Start/Exit und Windows-Export; vollständige Artefakte/Logs einem konkreten Stand zugeordnet. |

Bestehende Dokumentprüfung zusätzlich: `python3 -m unittest discover -s tools -p 'test_*.py' -v`, `python3 tools/check_docs.py`, vollständiger `git diff --check`. Headless-Prüfungen sind kein Beleg für Lesbarkeit, echte Maussignale oder Windows-Grafikverhalten. Zeichnungs-/Layoutregressionen auch mit tatsächlichen Renderbildern prüfen.

### 8.2 Manuelle Prüfungen am gelieferten Commit/Artefakt

| ID | Szenario | Zuständigkeit |
| --- | --- | --- |
| M-01 | F-01 per Maus setzen/neutralisieren, X↔Füllung direkt umwandeln, zurückziehen, Rücknahmetyp schützen, Radierer/Undo/Redo und Abschluss ohne Auskreuzpflicht. Neuer F-01-Reveal sichtbar detaillierter und eindeutig zugehörig. | Eigentümer |
| M-02 | F-02 mit vier Farben und langen Hinweisen; einzeilige farbige Zahlen ohne Zusatzkennung, gemeinsames Slotraster, mehrere Einzelketten unabhängig pannen, ergänzender Tooltip, Farbwahl, Zelltrennung, direkte Umwandlung und verfeinertes Leuchtturmmotiv klar bedienbar. | Eigentümer |
| M-03 | F-03-Koordinate bearbeiten, bei kleinen Arbeitsstufen echte Hinweiszahlen lesen, mehrere konkrete Zeilen/Spalten unabhängig pannen, Raster nur innerhalb der Vollsichtgrenze zoomen; passive Miniatur/Koordinaten vergleichen. VS2-M01 ersetzt die frühere Panprobe für den neuen Stand. | Eigentümer |
| M-04 | Mit #11 Teilstand schließen, neu starten und samt Historie/Ansicht fortsetzen. | Eigentümer |
| M-05 | Durch D-06 nicht anwendbar: Tastatur/Controller außerhalb P1. | Kein P1-Gate |
| M-06 | 1080p-Startziel beziehungsweise arbeitsbereichbegrenzter Fallback, 1080p/1440p und logische Referenzflächen; tatsächliche Skalierung erfassen. Keine verdeckten Elemente, aufgezwungenen Riesenraster oder verschmolzenen Füll-/Fünferlinien. | Eigentümer |
| M-07 | 100×100 auf der Referenzhardware: keine verlorenen/falschen Aktionen oder wahrnehmbaren Hänger. Im integrierten Paket 500 reproduzierbare Zell-/Navigationsaktionen gegen Sollzustand; Messung und Beobachtung getrennt. | Implementierer / Eigentümer |

Protokoll: tatsächliche Commit-/Artefaktkennung, Betriebssystem, verwendete Eingaben, Fenster-/Bildschirmgröße, reale Skalierung, Szenario und Ergebnis. Hardware-/Skalierungswerte nicht erfinden und keine pauschale FPS-Zusage aus der Referenz ableiten.

### 8.3 Gate-Zeitpunkte und bisherige Mausprobe

Der damalige Gesamt-P1-Vertrag verlangte A-01 bis A-07, Dokumentprüfung sowie M-01 bis
M-04 und M-06/M-07. Diese technische Integration und die reale Eigentümerprobe wurden
in #12 am commitgebundenen PR-#16-Stand abgeschlossen; PR #16 wurde anschließend als
`95fee5f87a84d4e849c845ce98313144349b3dd8` in `main` integriert. M-05 bleibt
nicht anwendbar. Diese Bestätigung gilt für den dort geprüften Stand und wird durch
spätere Änderungen nicht rückwirkend erweitert.

**Historische frühe Mausprobe K-06:** Der Nutzer hatte die angebotene F-01-Spielprobe
auf Artefakt `10719712143` / Head `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`
verwendet und mit Änderungsbedarf zurückgemeldet. Die daraus entstandenen Änderungen
wurden in den späteren P1-Paketen bearbeitet. Dieser historische Befund ist keine
aktuelle offene Gesamt-Abnahme.

G1/#17 ist nach Review R2 und erfolgreichen aktuellen Checks über PR #18 als
`6dd33232977127592c2b881f73094658853dbd87` integriert. Seine gezielte reale
Mausprobe wurde nicht durchgeführt und nicht als bestanden bezeichnet.

Für H1 gelten A-H01 bis A-H07 aus #19 und der
[H1-Prüfbericht mit Eigentümeranleitung](H1_VERIFICATION.md). Die gezielte reale
H1-Probe ist ebenfalls nicht als bestanden dokumentiert. Der Eigentümer hat nach
Review R1 am 25.09.2026 ausdrücklich die B-01-Nacharbeit und den anschließenden Merge
von PR #20 beauftragt; damit ist diese Probe für genau diesen Merge kein verbleibendes
Gate. Der finale kombinierte Head muss die aktuellen technischen Checks einschließlich
der G1-Regressionen bestehen.

## 9. Aktueller Lieferstand

P1.1/P1.2, P1.3, P1.4 und G1/#17 sind über PR #14 bis #18 in `main` integriert.
#12 dokumentiert die bestandene Gesamtprobe seines Stands; PR #18 dokumentiert die
technisch geprüfte Achsenneuwahl. H1/#19 ergänzt auf dieser Basis die
lösungsunabhängige Erfüllungsmarkierung und ist über PR #20 am kombinierten Stand
integriert. Die gezielten realen G1-/H1-Proben bleiben als nicht durchgeführtes
Produktfeedback sichtbar, sind nach den ausdrücklichen Mergeentscheidungen vom
25.09.2026 aber keine Mergegates für PR #18/#20.

Die endgültige Themenwahl, Wertung und Releasefähigkeit bleiben außerhalb dieses
Schritts. Rätselproduktion/Solver und Verbundraster bleiben getrennte Risikostränge.


## 10. Z2: native Bucharbeitsansicht und N1

[#23](https://github.com/venomenon328/picross/issues/23) konkretisiert ausschließlich
I-01 bis I-05 gemäß [GD-01 bis GD-05](Z2_SELECTION.md). Der reguläre Kern,
Appname/Speicherort, Saveformat und Rätseldaten bleiben erhalten. A-Papier,
Montierungen, UI und Raster sind getrennt; C1 konturiert nur Hinweisfarben 2/4.
Fraunces/Plex Sans sind gepinnt und offline gebündelt; VS2-V3 ergänzt das
unveränderte Bakso nur für Arbeits-Blatttitel. Farbwahl aktiviert Füllen.
Acht Arbeitsaktionen, eigene Miniatur, Koordinaten und aktive Farbe/Werkzeug bleiben
auf der Arbeitsseite, Trefferflächen mindestens 44/55 px bei UI 100/125 %.
VS2-V3 ordnet die acht Aktionen senkrecht rechts unter Miniatur/Palette an;
nur diese Leiste scrollt bei Platzmangel. Auswahl und Tooltips bleiben,
dauerhafte Werkzeug-/Farbtexte und numerische Zoomanzeige entfallen.
Bedingte Platzwarnungen stehen getrennt unten; alle vier Zoomaktionen bleiben.

GD-01 bis GD-05 ersetzen für Z2 ausdrücklich die frühere provisorische A–D-Palette,
den alten Sidebaraufbau und die damals offene Arbeitsasset-/Schrift-/C1-/Navigationswahl.
Die unbeschrifteten Originalfarbfelder und die numerischen Status-/Tooltipkennungen
sind in §5.2 beschrieben. Die gesamte Themenwahl Sammelalbum/Reisealbum und die
unveränderten Spiel-/Speicherverträge werden dadurch nicht neu entschieden.

Pfeil und Menü öffnen dieselbe Informationsseite mit Fokus Einstellungen, `?`
deren Hilfe. Rückpfeil erhält denselben bestätigten Arbeitszustand. Laufende Gesten
werden verworfen; ausstehende Ansicht wird über den gemeinsamen Flush gesichert.
Bei Fehler bleibt der Wechsel aus, und nötige Recovery mit Bestätigung ist bereits
auf der Arbeitsseite erreichbar. Verstecken verändert keine Rastergeometrie auf Null.
Bewusste UI-/Hinweisänderungen in N1 werden übernommen, H1 bleibt sitzungsweit.
Linkes Register und bestätigter Einzelreset benutzen das vorhandene Album.

Fünf ausdrücklich gesetzte Referenzzustände, Zwischengrößen und alle bisherigen
Arbeitszoom-/G1-/H1-/Speicherregressionen sind Bestandteil der [Z2-Prüfung](Z2_VERIFICATION.md).
Keine neuen Startzooms oder vorgegebenen Demo-Eingaben. Normale UI-Texte benötigen
mindestens 4,5:1 zum nativen Untergrund; Hinweise und Icons zusätzlich 1:1 beurteilen.
Z2 ist über PR #33 integriert. Z2-M01/M02/M03 sind nicht durchgeführt; der
Eigentümer hob das damalige Gate für diesen Merge auf. Sie sind kein RP-3-Gate.
Z2 ist keine Abnahme von #24 und keine Releasefreigabe.

## 11. RP-3: erster importierter Inhalt

F-04 erweitert die festen Definition-/Save-Registrierungen additiv. Appname,
Speicherroot, Schema 1 und bestehende ID-/Revisionsbindungen bleiben erhalten.
Definitionen werden ausschließlich aus einer festen ID→Ressourcenliste geladen.
Der Adapter liefert Schema 2, Leerwert 0, fortlaufende Palettenwerte 1..N und
passende Hinweise. Erst ein neu unabhängig geprüfter vollständiger Nachweis samt
Endmatrixvergleich erlaubt den Export. Der erste Adapter unterstützt nur
quadratisches Mono und ein lokales SVG unter `res://art/f04.svg`.

Der reguläre Hauptszenenweg wird in isolierten Profilen über echte Viewport-
Ereignisse geprüft: Auswahl, falscher Eintrag/eigene Miniatur, Undo/Redo,
Teilstand, Neustart, Abschluss und erneuter Neustart samt Album. Vor Abschluss
bleiben Name, Reveal und Lösungsausschnitt verborgen. Die [RP-3-Prüfzuordnung](RP3_VERIFICATION.md)
bindet native Renderbilder; F-01/F-02 samt Proofs/Bildern und F-03 bleiben erhalten.
RP-3 ist nach unabhängigem Review R2 über PR #44 integriert; die reale
Eigentümer-Lösung ist RP-6-Gate. Parent #34 bleibt offen; kein Merge/Release.

## 12. GP-48: Gameplay-Vertragsänderung

GP-01 bis GP-03 aus [#48](https://github.com/venomenon328/picross/issues/48)
ersetzen ausschließlich die betroffenen D-15-/H1-Bedien- und Anzeigeregeln in
§§5.1/5.2. Historische Abnahmen bleiben commitgebunden. Rätseldaten, Palette,
Proofs, Appidentität und Save-Schema bleiben erhalten; gespeicherte alte Aktionen
werden als Vor-/Nachwerte replayt, ohne die neue Gestenregel rückwirkend anzuwenden.

[GP-48-Prüfzuordnung](GP48_VERIFICATION.md) und
[gezielte Eigentümerprobe](GP48_OWNER_TRIAL.md) dokumentieren die Lieferung.
Review R1 und GP48-M01 sind für Lieferhead `1127b22c3b472f4af2a872643870549f65798bfc`
abgeschlossen; PR #49 wurde als `add7a7e6aa507d54d6e0e2ac8a3a2c5e2d1d6912`
in `main` integriert. Der kombinierte RP-6-Stand muss diese Regeln regressionsfrei
erhalten. Kein Release folgt daraus.


## 13. RP-6: sechs feste Pilotinhalte

F-04 bleibt byteidentisch einschließlich Revision und SVG. F-05 bis F-09 sind
zusätzliche Schema-2-Definitionen/Save-Slots: 100×100 Mono, 50×50 Farbe,
100×100 Farbe, zweimal 40×40 Farbe. Lokale quadratische PNGs `art/f05.png`
bis `art/f09.png` sind je ID fest gebunden. Adapter v2 prüft Import oder
vollständigen RP-5-Reparaturvertrag; technische Zertifizierung ist keine
redaktionelle Freigabe. Quelle/Palette/Matrix/Proof und Ressourcen stehen im
[Pilotmanifest](../examples/rp6/manifest.json).

Das vorhandene Album erhält ein scrollbar erreichbares Dreispaltenraster; alle
neun Blätter sind auch bei 1280×720/UI 125 % wählbar. Keine neue Progression
oder Albumarchitektur. Appidentität, Save-Schema 1, F-01 bis F-04 und deren
Revisionen bleiben erhalten. Font-/C1-, Maus-, Spoiler- und H1-Verträge gelten
für die neuen Paletten unverändert. Vor Abschluss nur eigene Miniatur, danach
korrekt gebundener Name und Ressource; alle sechs mit isolierter Fortsetzung
und tatsächlichen nativen Renderbildern geprüft.

[RP-6-Nachweise](RP6_VERIFICATION.md) und [neutrale Spielprobe](RP6_OWNER_TRIAL.md).
Unabhängiges technisches/visuelles Review und M01–M04 aus #40 bleiben
Abnahmegates. Eine automatisierte Lösung ersetzt keine Eigentümerprobe.


## 14. ZV-50: nutzbare Rasterfläche beim Zoom

[#50](https://github.com/venomenon328/picross/issues/50) konkretisiert D-28 als
begrenzte Layoutkorrektur auf der integrierten Z2-Arbeitsansicht. Technische
Zuordnung und native Vorher-/Nachherbelege stehen in
[ZV50_VERIFICATION.md](ZV50_VERIFICATION.md); die optionale reale Nachprobe in
[ZV50_OWNER_TRIAL.md](ZV50_OWNER_TRIAL.md). Rätseldaten, Regeln, Save-Schema,
20 Zoomstufen und historische Designpakete bleiben unverändert. PR #51 ist als
`952d68956f93851695234731a6d94e6552c8d54a` in `main` integriert; RP-6 übernimmt
diesen Stand regressionsfrei.

## 15. ZS: zeichnerische Oberfläche und Zellanimationen

Die [freigegebene Detailspezifikation](UI_DRAWING_STYLE.md) konkretisiert D-29 bis
D-32. [ZS-1/#52](https://github.com/venomenon328/picross/issues/52) führt die nach
E1 gewählte Stiftfüllung fort. Neues X und räumlicher Strichaufbau ersetzen die
bisherige gleichförmige Kreuzform und Fade-Animation. Die bestätigte Nacharbeit
vom 09.10.2026 ersetzt 140/80 ms durch 210 ms Setzen/Umwandeln und 120 ms
Entfernen; kurze sichtbare Schraffurzüge bauen die Füllung händisch auf. Zwei Eigentümer-TTFs werden gemäß Eigentümerentscheidung E2 am
gleichen Stand verglichen. Zusätzliche Rand-UI entfällt; Hintergrundarbeit bleibt separat.
[ZS-2/#53](https://github.com/venomenon328/picross/issues/53) integriert genau diese
Auswahl in die reguläre Arbeitsansicht einschließlich abschaltbarer Effekte.

ZS2-E2/N01–N03 ersetzt die gleichzeitigen Starts durch die begrenzte gerichtete
Folge nach D-31/ZS-D07; Schutzlücken bleiben ohne Zeitlücke. Das aktive X schreibt
Zug eins vor Zug zwei ohne vollständige Unterzeichnung. Gegentasten-Down verwirft
die ganze aktive Zellgeste samt Zähler, auch außerhalb des Boards. Nach beiden
Ups erlaubt erst ein frisches Down die nächste Geste. Escape/Fokus dürfen keine
Phantomaktion oder hängende Sperre erzeugen; MMB bleibt ausschließlich Hinweisnavigation.
Die nächste Eingabe liest sofort den bestätigten Zustand. Neue Vorschau oder ein
neuer Zustand derselben Zelle beendet veraltete Effekte; Rückzug spielt sie nicht
erneut ab. Undo/Redo bleiben unmittelbar und ohne eigene Setzanimation. Abschluss,
Seitenwechsel und Speicherung erhalten ihre vorhandenen Regeln; keine neue
Abschlussverzögerung und keine transienten Effekte im Save.

Für den P1-Schalter Zellanimationen gilt als begrenzter Ausarbeitungsdefault der
bestehende sitzungsweite Ansatz: aktiv nach Start, erhalten über Blätter/Reset/Seiten,
keine neue dauerhafte Einstellungsarchitektur. Hinweise analysieren weiterhin den
eigenen logischen Zustand einschließlich statischer Vorschau; die Miniatur zeigt
diesen unmittelbar und unanimiert. Farb-/Gesten-/History-/Save-/Spoiler-/ZV-50-Verträge
bleiben erhalten. Die [isolierte ZS-1-Studie](ZS1_VERIFICATION.md) enthält die
bestätigte Kombination. Die reguläre Integration und ihre weiterhin getrennten
Abnahmegates sind in [ZS2_VERIFICATION.md](ZS2_VERIFICATION.md) dokumentiert.

Aktuelle technische und gezielte reale Gates stehen im jeweiligen Paket. Die
längere Spielerprobung [#24](https://github.com/venomenon328/picross/issues/24) folgt
nach ZS-2 und ersetzt keine davor nötige Prüfung. Historische Abnahmen bleiben
commitgebunden; kein Merge- oder Releaseauftrag aus der Spezifikationsfreigabe.


ZS1-E3 wählt Chalkboard als konkrete Hinweisfont. N07 reduziert in der isolierten
Studie ausschließlich die horizontale Zeilenhinweis-Slotweite auf 26 logische Pixel
bei UI 100 %; Spaltenslots bleiben unverändert. Für PR #55 hat der Eigentümer die
kombinierte Sichtprüfung ausdrücklich auf den gemergten `main`-Stand verlegt
und ihren erfolgreichen Abschluss am 07.10.2026 bestätigt.

## VS-1 · experimentelle Vollsichtprobe (#57)

Der [VS-1-Studienvertrag](VS1_STUDY.md) bindet zehn native Beispiele, aktuell G/V nach VS-E1-R2,
die ausgewählte ZS-1-Zeichenschicht und getrennte Studienfortsetzung.
[Prüfzuordnung](VS1_VERIFICATION.md) und [Eigentümerprobe](VS1_OWNER_TRIAL.md)
trennen technische Lieferung und persönliche Komfortbefunde. [VS-D01](VS1_DECISION.md)
ist strategisch entschieden: reguläres Vollsichtziel 40×40, mindestens 30×30,
geeignete 40×30/50×30, 1080p, bevorzugt G und ergänzend V. Sehr große Rätsel
bleiben mögliche Sonderfälle. PR #58 ist als `c19b3547…` integriert; VS-GF1/#59
liefert zusätzliche Zeilenkapazität aus freier G-Breite bei unverändertem Fit.
Die reguläre P1-Umstellung bleibt separat. VS-M01 ist nicht vollständig persönlich
durchgeführt; GF-M01/#59 ist historisch bestanden; neues unabhängiges VS2-Review und VS2-M01 bleiben vor Merge offen.

VS-E1-R2 aus #57 §11 ersetzt für diese Studie die früheren R-/Hand- und
pauschalen Hinweisreserven. Achsengetrennter tatsächlicher Bedarf, fünf vollständige
zusammenhängende Zahlen auch im Drag und eine harte Raster-Fitgrenze sind aktiv.
Historische Erstlieferung bleibt gebunden; normale P1-Defaults bleiben bestehen.
