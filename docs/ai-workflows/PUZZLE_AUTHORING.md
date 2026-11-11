# Picross: Regeln für die KI-gestützte Rätselproduktion

**Version 0.6.0 · Dokumentrevision 48 · 11.11.2026**

HP-W1 aus [#560](https://github.com/venomenon328/picross/issues/560#issuecomment-6747196307)
spezifiziert den **versionierten Hintergrundweg außerhalb des aktiven Defaults** in
[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md).
[HP-W2](https://github.com/venomenon328/picross/issues/560#issuecomment-6748799473)
liefert dessen eigenständige Arbeits-/Entscheidungs-/Ableitungsformen sowie die
lokale API/CLI `describe/derive/verify`. PB-H ergänzt den explizit gewählten
Paketbau und die lesende Inhaltsprüfung nach dem vollständigen
[0.7.0-Vorschausnapshot](PUZZLE_AUTHORING_0_7_0_PREVIEW.md). HP-I1a ergänzt sichere
äußere Fortschreibung vorhandener Auswahl/Ableitung/Endfreigabe und prüfbaren
Export v6. HP-I1b1 ergänzt zielgebundene Erstregistrierung, kompakte aktive
Source/Receipt, Recovery und ersten Produktionsabschluss. HP-I1b2 ergänzt den
eigenständigen Hintergrundwechsel und revisionsgenauen Abschluss, HP-I1c die
erlaubte Raster-/Revealneubindung vorhandener Hintergrundziele. HP-I2 regelt
Runtime v6, papiergebundene Darstellung, begrenztes Bedarfsladen und isolierten
Profilimport. Eine echte true-Capability setzt diesen funktionierenden und
technisch abgenommenen Weg voraus; synthetische kompatible Ziele belegen nur
den Werkzeugweg. Diese Dokumentrevision führt den Unterstützungsstand nach;
der aktive Produktionsweg bleibt **0.6.0**
mit seinen bisherigen Formaten, Freigaben und ZA-1-Prüfungen. Version **0.7.0**
wird ausdrücklich opt-in verwendet. Ihre verpflichtende Gesamtaktivierung wird
erst anhand des tatsächlich unterstützten vollständigen Einzelwegs in #560
festgestellt; ein true-Flag allein stellt den Default nicht um. Neue Daten
nicht in alte Hüllen schreiben und versiegelte Originale nicht umetikettieren.

PB-A aus [#489](https://github.com/venomenon328/picross/issues/489#issuecomment-6745424504)
ergänzt den lokalen deterministischen Paketbuilder nach §6.1. Bestehende
Freigabe-, Phasen- und ZA-1-Verträge bleiben erhalten.
[PB-H](https://github.com/venomenon328/picross/issues/489#issuecomment-6751071312)
unterstützt daneben Bauauftrag v2, Handoff v3, Record v2 und Sheet-Update v3
für den ausdrücklich gewählten 0.7.0-Vorschaustand.
[BA-A / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6779908657)
ergänzt die lokale serielle Verarbeitung ausdrücklich ausgewählter vorbereiteter
Jobs mit vorhandenen Fachwerkzeugen nach [PRODUCTION_BATCH](../PRODUCTION_BATCH.md).
Der Runner erhält vorhandene Entscheidungen, führt keine Bildwahl aus und endet
spätestens am lokalen Paketbau. Seine technischen Zustände erteilen keine
Inhaltsfreigabe. [BA-B / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6782256272)
ergänzt separat die serielle Integration bereits vollständig vorbereiteter und
tatsächlich autorisierter Jobs nach §8. Die vier Aufträge, Inhaltsfreigaben und
Sheetbedienung bleiben erhalten.
[MJ-A / #490](https://github.com/venomenon328/picross/issues/490#issuecomment-6774440064)
ergänzt den regulären Mehrjob-Arbeitsbereich sowie Update v3, Sitzung v5 und
Auftrag v4 nach [Hintergrundvertrag §7.5](../PUZZLE_BACKGROUNDS.md#75-mj-a-mehrjob-arbeitsbereich-und-sichere-übernahme).
Neue Jobs bleiben im Default bei 0.6.0/Sitzung v4; der Hintergrundweg ist opt-in.
MJ-B ergänzt den eigenständigen Hintergrundwechsel im Sheet nach Hintergrundvertrag §7.6.

Der aktive Produktionsweg aus P-B2 / [#488](https://github.com/venomenon328/picross/issues/488) gilt weiter:
Neue Produktionen verwenden im Default **0.6.0**, automatische frühe Palettendiagnosen und
die frische finale [ZA-1-v5-Prüfung](../ZA1_ADAPTER.md#p-b2--authoring-060-und-additive-palettengeneration-v5).
Die unveränderte Farbregel bindet weiterhin Normrevision 4; F05 bleibt eine
visuell angenommene synthetische Referenz mit negativen Messwerten, keine
Produktionsausnahme. Messung, visuelle Urteile und konkrete Eigentümerausnahme
werden getrennt geprüft. Altpakete 0.4.0/0.4.1/0.5.0 samt ihren damaligen
Snapshots und v1–v4-Exporten behalten ihre Semantik; neue Arbeit nicht als
Legacy deklarieren. Bei Wiederaufnahme den tatsächlichen gebundenen Regelstand
erhalten, materielle Neuproduktion als neue Revision unter dem ausdrücklich
gewählten Regelstand führen; ohne Wahl des Hintergrundwegs bleibt dies 0.6.0.
Q-A-Sichtung, Sheet v2, Paarprofile, feste manuelle Ableitungen und alle
Proof-/Herkunfts-/Bild-/Motiv-/Endfreigaben sowie RI-Guards bleiben erhalten.
Regelwerksversion, Dokumentrevision, Datei-SHA-256 und tatsächlicher Commit
binden den verwendeten Stand; keine Umetikettierung versiegelter Originale.

- [SD2-Integration](../SD2_INTEGRATION.md) regelt Methodenwahl, Analyse/Import,
  Metadaten-Rebind und kontrollierte Registrierung. Der Produktionsdefault 0.4
  wurde mit [SD2-D](../SD2_D_ADOPTION.md) integriert; alte 0.1–0.3-Bindungen bleiben
  nach ihrem eigenen Vertrag lesbar. Diese Regelwerkpflege bewertet keine Inhalte neu.
- [Abschlussbildtransparenz](../REVEAL_TRANSPARENCY.md) regelt neue Bilder und
  getrennte Bildrevisionen. Frühere AT-B-Freigaben bleiben an ihren konkreten
  Dateien und Belegen gebunden, keine erneut offene Bestandsproduktion.
- Sheet-Übergabe v2 bietet Bild-/Rasteroptionen (§4.5/§7). Das
  [Offline-Sheet](Picross_Raetselproduktion_Cheat-Sheet.html) übernimmt ihre Bindungen
  gemeinsam; Auswahl/Empfehlung sind keine Freigabe. Handoff v2 und Inventar v1 bleiben; 0.6.0 ergänzt die
  Paletten-/Sichtbindung und verwendet ausschließlich ZA-1 v5.
- Paarprofile benötigen mindestens Authoring 0.5.0, neu 0.6.0; versiegelte 0.4.x-Pakete behalten
  ihren Linienvertrag. [SD](../PUZZLE_DIFFICULTY.md) und
  [SD-C1](../SD_CATALOG.md) bleiben kompatible Fachquellen bei Schwierigkeitsarbeit.

**Zielpfad:** `docs/ai-workflows/PUZZLE_AUTHORING.md` im Repository `venomenon328/picross`.

Diese Arbeitsanweisung regelt die Erstellung neuer Rätsel vom Motivauftrag über das zuerst freigegebene Abschlussbild bis zur geprüften Integration ins Spiel. **MUSS** bezeichnet eine Pflicht, **SOLL** den begründet abweichbaren Standard, **DARF** eine Option.

**Geltungsgrenze:** Die ausdrücklich als „Zukünftiger Hintergrundweg“ bezeichneten
Ergänzungen spezifizieren den Sollablauf nach dessen versionierter Einführung.
HP-W2 erlaubt die eigenständige technische Vorbereitung nach §6.3; PB-H
sichert sie in eigenen 0.7.0-Paketformen und prüft deren fällige Inhaltsgates
lesend. HP-I1a führt äußere Records höchstens bis `editorially_approved` und
exportiert v6 mit `integration_ready/catalog_ready/registered=false`.
HP-I1b1 prüft Bereitschaft frisch außerhalb dieser Originale am Ziel; fehlende
oder false-Capability blockiert vor Mutation. HP-I2 trennt die tatsächlich
abgenommene Runtimefähigkeit vom unveränderten Produktionsdefault. MJ-A führt
den regulären Hintergrundweg im Offline-Sheet; der eigene spätere Änderungsjob
folgt MJ-B nach Hintergrundvertrag §7.6. Keine Pflicht des bestehenden 0.6.0-Wegs wird geändert. Für beauftragte
Hintergrundarbeit den zentralen Hintergrundvertrag einschließlich seines aktuellen Unterstützungsstands
vollständig lesen; nur tatsächlich verfügbare Teilfähigkeiten verwenden.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_QUALITY.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`. Vor Paarlinienprüfung oder Übergabe eines Paarprofilpakets zusätzlich `docs/PAIRED_LINES.md` vollständig lesen.
2. Zu Beginn Kategorienquelle, Arbeitsindex und Runtime-Registry lesen; Bestandsrätsel nicht einzeln laden oder nachprüfen. Kategorie nach Auftrag oder prägendem Hauptgegenstand gemäß [Kategorienvertrag](../CATEGORIES.md) zuordnen und in Briefing/Record führen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Aktuelle Dateien und tatsächlich benötigte Fähigkeiten prüfen, keine historischen PR-Statuslisten abarbeiten. Abgeschlossene Lieferungen sind keine erneut offenen Voraussetzungen; nur eine konkrete aktuelle Lücke verfolgen.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API einbauen. Produktionsaufträge mit Repositoryablage erlauben ausschließlich die beauftragte Paketsicherung samt Index; ein Integrationsauftrag erlaubt zusätzlich Abschnitt 8 und die anschließende Bereinigung nach Abschnitt 9. Ablage-/Integrationsmerge braucht den passenden ausdrücklichen oder bedingten Auftrag. Für den zugehörigen Cleanup gilt die Eigentümerfreigabe in Abschnitt 9. Werkzeugänderungen und Veröffentlichung bleiben getrennte Befugnisse. Bereits erteilte passende Aufträge nicht erneut erfragen.
6. **Menschliches Probespielen ist optional und kein Freigabekriterium.** Ein großer Rätselbestand darf ohne Probespiele entstehen. Verpflichtend bleiben die Abschlussbildfreigabe, die Freigabe der daraus abgeleiteten Motivvorlage, die technische Prüfung und die abschließende redaktionelle Abnahme. Spätere Spielerfahrungen dienen der Verbesserung und Kalibrierung.

**Projektlokale Ausnahme zur Modellauswahl:** Normale Produktionsaufträge nach
diesem Regelwerk (1–4 einschließlich Korrektur und Wiederaufnahme) erzeugen keine
Modell-, Reasoning-, Eigenumsetzungs- oder sonstige Ausführungsempfehlung.
`docs/dev-rules/MODEL_SELECTION.md` und `MODEL_CATALOG.md` dafür nicht laden;
keine dafür veranlasste Recherche zu Modellen, Preisen oder Clientverfügbarkeit.
Der Nutzer wählt seine Oberfläche und Einstellungen selbst. Die Prüfung der
tatsächlich nötigen Bild-, Datei-, Repository- und Werkzeugfähigkeiten bleibt
Pflicht; konkrete Zugriffsblocker benennen. Separat beauftragte Entwicklungsarbeit
an Werkzeugen, Spiel oder CI folgt weiterhin dem allgemeinen Entwicklungsworkflow.

### Prüfungen gehören zur Produktion, nicht zur CI

- Sämtliche rätselbezogenen Prüfungen – Lösbarkeit, Eindeutigkeit, unabhängiger Proof, Herkunft, Reparatur, Gestaltung und Zielintegration – MUSS die KI für die jeweilige neue/geänderte Revision im Produktionsauftrag durchführen und dateigebunden belegen. Unveränderte, passend gebundene Nachweise wiederverwenden; erforderliche Neuprüfungen nach Abschnitt 4.4 bleiben Pflicht.
- **Keine rätselspezifischen Unit-Tests, Test-Snapshots, CI-Falllisten oder dauerhaften Replayjobs anlegen.** Ein neues Rätsel darf weder den allgemeinen Testbestand noch einen CI-Korpus erweitern. Prüfscripte für den konkreten Auftrag nur temporär außerhalb der Test-Discovery ausführen; Ergebnisse ins Paket, keine CI-Anbindung.
- Für jeden Inhalts-/Ablage-/Cleanup-PR einen aktuellen `.ci/package.json` nach [CI_WORKFLOW_V2](../CI_WORKFLOW_V2.md) führen; vorhandenes Inhaltsissue/Paket verwenden oder den neuen Auftrag dort erfassen. Reine Inhalte wählen begründet `modules=[]` und `evidence.mode=none`. Der allgemeine Kern prüft Quellen-/Planintegrität; reine Rätselproduktion einschließlich Ablage, Integration und Datenbereinigung bleibt ohne Player-Build. Das gilt auch im Main-Nachlauf. Keine rätselspezifischen Solver-/Proof-Replays, vollständigen Fachtests oder nativen Funktions-/Rendermatrizen ergänzen; unveränderte Bestandsrätsel nicht erneut prüfen.
- Code-, Tool-, gemeinsame UI-/Asset- und CI-Änderungen sind separate Entwicklungsarbeit mit den passenden allgemeinen Regressionen an einem festen technischen Testbestand. Nicht zur vermeintlichen Absicherung eines neuen Rätsels Code ändern oder den CI-Umfang manuell auf `all` erweitern.

## 2. Abschlussbild zuerst, danach Abstraktion

### 2.1 Eingaben und Konfiguration

Zulässiger Input: Motivtext beliebiger Ausführlichkeit und/oder Ausgangsbild; optional Breite × Höhe (ungefähr/fest), Mono/Farbe, gewünschte Vordergrundfarbzahl (ungefähr/genau) und weitere Einschränkungen. Eine verlinkte oder angezeigte Bildvorschau ersetzt keine gespeicherte Quelldatei.

Die KI MUSS Hauptmotiv, unverzichtbare Merkmale, erlaubte Umgestaltung und Einschränkungen erfassen. Fehlende reversible Details sinnvoll ergänzen. Nur wesentliche offene Produktentscheidungen beim Nutzer erfragen, jeweils mit Empfehlung und Konsequenzen.

Der erste gestalterische Schritt ist immer die Erstellung mehrerer **farbiger, detaillierter Abschlussbilder** aus dem Input. Noch keine abstrahierte Motivvorlage, Zellmatrix oder Hinweise erzeugen. Fehlende Rastermaße oder ein offener Rätselmodus blockieren diese Bildauswahl nicht. Die spätere Darstellbarkeit bei der Komposition berücksichtigen, ohne das Abschlussbild vorzeitig auf Zellniveau zu vereinfachen. Auch ein eigenes Ausgangsbild ist zunächst Referenz und keine automatisch freigegebene Abschlussbilddatei.

Wenn Größe oder Farbmodus offen sind, nach der Abschlussbildfreigabe **2–3 konkrete Konfigurationen** vergleichen und eine empfehlen. Motivtreue, Darstellbarkeit, erwartetes Lösbarkeitsrisiko und Spielgefühl getrennt begründen. Auch ungefähre Wunschmaße dürfen hinterfragt werden; feste Grenzen nicht eigenmächtig überschreiten. Rechtecke gleichberechtigt berücksichtigen.

- Reguläre Rätsel: **Breite ≤ 50 und Höhe ≤ 50**. Ein weiter gefasstes technisches Werkzeuglimit ist keine Produktfreigabe.
- Klein (längste Achse ≤ 20): dominante Silhouette und wenige Binnenformen. Mittel (21–35): charakteristische Details und Negativflächen. Groß (36–50): gegliederte zusätzliche Details, keine bloße Vergrößerung. Diese Arbeitsklassen bestimmen keine Schwierigkeit.
- **Acht Vordergrundfarben plus Leer sind die technische Obergrenze, kein Produktionsziel.** Die kleinste Palette empfehlen, die Identität, wichtige Flächen und Lesbarkeit angemessen erhält; gewöhnlicher Ausgangspunkt sind Mono oder 2–4 Farben. 5–8 sind mit konkretem motivischem Nutzen zulässig. Keine zusätzlichen Farben allein wegen Verfügbarkeit, Größe, Solvererfolg oder künstlich höherer Schwierigkeit.
- Farbzahl bezeichnet die tatsächlich in der Matrix verwendeten Vordergrund-IDs; `EMPTY` zählt nicht, auch Weiß kann eine Vordergrundfarbe sein. Unbenutzte Paletteinträge, nahezu gleiche Schattierungen und dekorative Einzelzellen erfüllen keinen Farbwunsch. Vor Versiegelung Palette auf tatsächlich nötige Einträge reduzieren und nötige Neuprüfungen aus 4.4 ausführen.
- Eine **genaue** Farbzahl ist eine feste Vorgabe; bei Konflikt mit Motivqualität oder Nachweis vor Abweichung eine begründete Alternative vorlegen. **Ungefähr** ist ein Ziel: Abweichung begründen und im vorgeschlagenen, später freizugebenden Parameterkorridor konkretisieren; kein stilles Ausweiten auf acht. Mono verwendet genau eine Vordergrundfarbe; widersprüchliche Eingaben vor der betroffenen Abstraktion klären.
- Bei offener Farbzahl in Auftrag 2 die empfohlene Palette und eine sinnvoll reduzierte Alternative gegenüberstellen. Jede zusätzliche Farbe benötigt eine benannte Funktion, etwa die Trennung charakteristischer Bauteile. Bei 5–8 Farben ausdrücklich erklären, welcher erkennbare Verlust durch weitere Zusammenlegung entsteht. Varianten mit verschiedener Farbzahl in die vorhandene Kandidatenauswahl integrieren, keine zusätzliche Vollmatrix verlangen. Unverzichtbare Farbtrennungen nicht mechanisch reduzieren. Das Abschlussbild bleibt immer farbig, detailliert und unabhängig von der Rasterfarbzahl.
- Größe, Seitenverhältnis und Palette müssen zum Motiv passen. Vor dem Nachweis keine Lösbarkeit versprechen.

Spätere Formularwünsche dürfen einen bereits freigegebenen Parameterkorridor nicht
stillschweigend ändern. Widersprüche vor Produktion/Integration klären; die konkret
vorgelegte Fassung und ihre tatsächliche Freigabe bleiben maßgeblich.

### 2.2 Darstellungen auseinanderhalten

| Darstellung | Zweck und Bindung |
| --- | --- |
| Ursprungsidee / Bildquelle | Auftrag oder Referenz; Original, Herkunft und Nutzungsgrundlage erhalten. |
| Abschlussbild | Zuerst erzeugte farbige, detaillierte Illustration; nach ausdrücklicher menschlicher Auswahl/Freigabe verbindliche gestalterische Referenz für alle folgenden Darstellungen und spätere Belohnungsansicht. |
| Motivvorlage | Aus genau dem freigegebenen Abschlussbild abgeleitete, vereinfachte, gespeicherte Illustration für den gewählten Rastermodus; eigene menschliche Freigabe vor der Rasterproduktion. |
| Lösungsraster | Exakte diskrete Zellmatrix aus der Motivvorlage; alleinige Grundlage für Hinweise und Logiknachweis. |
| Hintergrundzeichnung (zukünftiger Weg) | Eigenständige Kontextillustration mit eigener Bildrevision und tatsächlicher Auswahl; weder Abschlussbild noch Motivvorlage oder Quelle für Lösungszellen. |

Verbindliche Richtung: **Input → Abschlussbild → freigegebene Abstraktion → Lösungsraster**. Diese drei Darstellungen müssen motivisch zusammenpassen, nicht pixelidentisch sein. Abschlussbild und Motivvorlage als getrennte Dateien und Revisionen führen; das detaillierte Original niemals mit seiner vereinfachten Ableitung überschreiben. Der zukünftige Hintergrund hat einen Kontextbezug, gehört aber nicht zu dieser Ableitungskette.

### 2.3 Styleguide

**Vorgeben:** ruhige, warme, handgezeichnete 2D-Illustration; klare Silhouette; klare, charaktervolle Proportionen; sauber geführte Konturen; zusammenhängende, ausreichend kräftige Farbflächen; charakteristische Innenräume; ruhiger Hintergrund. Das Abschlussbild MUSS eine ausgearbeitete farbige Illustration mit sauberer Binnenzeichnung, motivgerechten Oberflächendetails und zurückhaltender Schattierung sein. Detailliert bedeutet weder fotorealistisch noch überladen. Seine Hauptformen müssen später abstrahierbar bleiben; eine vergrößerte Zellgrafik oder bloß kolorierte Silhouette genügt nicht. Details müssen Erkennbarkeit oder Ausdruck unterstützen. Die gemeinsame Identität entsteht durch Form-, Kontur- und Flächenbehandlung, nicht durch eine für alle Motive identische Palette.

**Transparenter Bildgrund nach [AT](../REVEAL_TRANSPARENCY.md):** Der freigegebene
Sollstandard ersetzt neutrale weiße, cremefarbene oder andersfarbige Bildflächen
um das Motiv durch echte PNG-Transparenz. Tatsächliche Aussparungen, etwa ein
Henkelinnenraum, werden ebenso freigestellt. Weiße und helle Motivbestandteile,
feine Konturen, charakteristische Details und Proportionen bleiben erhalten;
keine globale Farb-/Helligkeitsschlüsselung. Saubere teiltransparente Randpixel
dürfen keine hellen Säume auf dem Papiergrund erzeugen. Die Ausgabe bleibt eine
ausgearbeitete farbige Illustration, auch bei monochromem Rätsel.

Szenische Bilder werden motivbezogen behandelt: prägende Gegenstände, ihre
Beziehungen und notwendige Umgebung bewahren, die transparente Außenfläche
beziehungsweise Vignette bewusst gestalten und die konkrete Fassung vorlegen.
Eine Szene ist keine pauschale Ausnahme für einen opaken Bildkasten; Himmel,
Boden oder Nebenmotive werden zugleich nicht blind entfernt. Geänderte
Kompositionen und materielle Motivänderungen benötigen die dazugehörige erneute
Freigabe. Großansicht und tatsächliche Kataloggröße auf dem Papiergrund gemeinsam
prüfen. Transparenz des Abschlussbilds ändert weder den Leerwert des Rasters
noch weiße Vordergrundfarben einer Farbmatrix.

**Vermeiden:** Fotorealismus/3D-Look als Stilgrundlage, Skizzenrauschen, ausgefranste Doppelkonturen, entscheidende Haarlinien, überladene Hintergründe, schwache Ton-in-Ton-Trennung, zufällige Kleinstflächen, anatomische Artefakte, Schrift/Wasserzeichen und Dekoration allein zum Füllen freier Zellen.

**Bei Abschlussbild, Motivvorlage, Raster und Hinweisansicht prüfen:** Der
[Qualitätsvertrag §§2–4](../PUZZLE_QUALITY.md) führt die verbindlichen
Einzelkriterien, Herkunft, Methoden/Prüfzeitpunkte und die Trennung von
unabdingbaren Voraussetzungen und redaktionell abweichbaren Zielen.
Je Kriterium `erfüllt`, `Warnung`, `nicht erfüllt` oder `nicht geprüft` mit
Begründung und konkreter Datei-/Revisionsbindung dokumentieren. Keine gute
Gesamtnote darf ein negatives Einzelkriterium verdecken. Historische Berichte
behalten ihre damaligen Ergebniswörter und Bindungen.

Im Raster nur diskrete Werte, keine Zwischenfarben oder Textur als Zellzustand. Farbige Raster müssen selbst erkennbar sein; bei Mono darf das Abschlussbild zusätzliche Klarheit schaffen. Bei der Abstraktion diese Details gezielt reduzieren, zusammenfassen oder weglassen, ohne Identität, Perspektive, Hauptproportionen und wichtige Negativflächen des Abschlussbilds zu verändern. Das Abschlussbild nicht nachträglich zur Rechtfertigung eines abweichenden Rasters umgestalten.

### 2.4 Abschlussbildauswahl und Abstraktionsfreigabe

1. Standardmäßig **drei sinnvoll unterschiedliche Abschlussbilder** erzeugen. Komposition, Pose oder Farbgebung variieren; Stil, Detailanspruch und Auftrag bewahren. Bei bindender Referenz (`faithful`) Identität und geschützte Geometrie erhalten; freie Interpretation (`free`) ausdrücklich festhalten. Eine ausdrückliche Vorgabe darf die Variantenanzahl reduzieren.
2. Native Bildgenerierung verwenden. Jede Variante als tatsächliche Einzeldatei speichern und zeigen; eine Kontaktübersicht ist nur Auswahlhilfe. Ohne verfügbare Bildfunktion den Bildschritt als blockiert melden; Konzepte oder behauptete Dateien ersetzen keine Abschlussbildauswahl.
3. Der Mensch wählt und korrigiert. **Vor jeder Abstraktion MUSS das konkrete Abschlussbild ausdrücklich freigegeben sein**, gebunden an Datei, Revision/Hash und zu bewahrende Merkmale. Eine Auswahl mit Korrekturwunsch ist noch keine Freigabe der korrigierten Fassung.
4. Danach geeignete Rasterkonfiguration empfehlen und aus den gespeicherten Bytes des freigegebenen Abschlussbilds eine Motivvorlage ableiten. Standardmäßig eine gezielte Abstraktion für die empfohlene Konfiguration erstellen; zusätzliche Varianten nur bei einem konkreten Darstellungs-/Detailkonflikt. Abschlussbild und Abstraktion nebeneinander vorlegen und Detailverluste benennen.
5. **Vor jeder eigentlichen Rasterproduktion MUSS die konkrete abstrahierte Motivdatei freigegeben sein**, einschließlich Revision/Hash, Abschlussbildbezug, Motivinvarianten und zulässiger Größen-/Modus-/Crop-Varianten. Die Abschlussbildfreigabe ersetzt diese Abstraktionsfreigabe nicht. Schweigen oder unverbindliches Interesse ist keine Freigabe.

Korrekturen nur an der gewählten Darstellung durchführen, zu bewahrende Merkmale nennen und eine neue Revision speichern. Nach zwei erfolglosen Runden Ursache und geänderten Plan vorlegen. Ist die Abstraktion ungeeignet, zunächst Vereinfachung, Größe oder Rasterpalette korrigieren. Ein anderes Abschlussbild benötigt erneut die ausdrückliche Bildfreigabe; es darf nicht stillschweigend an technische Fehlschläge angepasst werden.

### 2.5 Zukünftiger Hintergrundweg: Briefing und drei Kontextzeichnungen

Nach [PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) wird in Auftrag 1 bei
feststehender Motivrichtung zusätzlich das Hintergrundbriefing erfasst:
geeigneter Kontext, geschützte Merkmale und tatsächliche Eigentümervorgaben.
Die Abschlussbildauswahl bleibt unverändert; keine Kreuzmatrix aus Reveal- und
Hintergrundvarianten erzeugen. Offene Briefingideen sind keine Bildfreigabe.

In Auftrag 2 nach der tatsächlichen Abschlussbildfreigabe **drei inhaltlich
unterschiedliche Hintergrundkandidaten** mit ImageGen erzeugen und als drei
gespeicherte Einzelbilder zusammen mit der Motivvorlage isoliert vorlegen.
Auflösungs-/Formatvarianten desselben Bilds zählen nicht als verschiedene
Kontexte. Keine selbständige Reduzierung auf einen Favoriten; nur eine
ausdrückliche Eigentümervorgabe darf die anfängliche Anzahl im Einzelfall ändern.
Ein endgültiges Raster wird für Erzeugung oder Auswahl nicht benötigt.

Die Zeichnungen zeigen Umfeld oder Kontext, nicht den konkreten zu erratenden
Gegenstand, seine Lösungssilhouette, Rasterkopie oder den Motivnamen. Sie hängen
nicht vom Spielerfortschritt ab. Indirekte Hinweise durch Kontext bleiben möglich;
keine universelle Spoilerfreiheit behaupten. Helle neutralgraue Graphitstriche,
offene Konturen, sparsame Schraffur und echte Transparenz auch zwischen Strichen
folgen dem eigenen Hintergrundteil des [Qualitätsvertrags](../PUZZLE_QUALITY.md).
Der zentrale Hintergrundvertrag bindet die transparente 4:1-Leinwand und das
gemeinsame Ableitungsprofil; keine individuellen Offsets, Crops oder Masken.

Isolierte Bilder sind die Auswahlgrundlage. Keine Kandidaten-Testintegration,
Buch-Composites, Spielstarts oder zusätzliche persönliche Buchabnahme verlangen.
Die bestehenden AT-/Reveal- und Raster-/Hinweissichtungen bleiben eigenständig;
deren Ansichtsanforderungen werden nicht auf Hintergrundkandidaten übertragen.

## 3. Standardablauf: vier Aufträge

Ein Auftrag umfasst sämtliche nötigen Arbeiten bis zur nächsten menschlichen Freigabe. Prüfung, Schwierigkeit, Bericht, Verschlankung und Dateisicherung sind Teilaufgaben, keine zusätzlichen Dialogphasen. Keine routinemäßigen Rückfragen zum Weiterarbeiten, Packen, Prüfen oder Registrieren. Nur fehlende Freigaben, materielle Motivänderungen, wesentliche Entscheidungen oder konkrete Blocker unterbrechen den Ablauf.

Die folgende Phasen-/Ausgabetabelle beschreibt den **aktiven 0.6.0-Weg**.

| Auftrag | Akteur und verbindliche Arbeit | Ausgabe / Stopp |
| --- | --- | --- |
| **1 · Abschlussbildauswahl** | Bildfähige KI erfasst Text/Bild, liest Quellen und erzeugt drei Abschlussbilder nach Abschnitt 2. | `brief_ready` → `reveal_review`: Einzeldateien, kurzer Vergleich, gesicherte Übergabe mit allen Abschlussbildoptionen; auf menschliche Auswahl/Freigabe warten. |
| **2 · Abschlussbildfreigabe und Abstraktion** | KI bindet die tatsächliche Freigabe, empfiehlt bei offenen Angaben 2–3 Konfigurationen und erstellt unmittelbar die Abstraktion für ihre Empfehlung. Keine zusätzliche Konfigurationsrunde, sofern keine feste Grenze verletzt wird. | `reveal_approved` → `motif_review`: Bildvergleich, Detailverluste, eindeutiger vorgeschlagener Parameterkorridor, gesichertes Produktionspaket und Sheet-Daten; auf Motivfreigabe warten. |
| **3 · Motivfreigabe und Produktion** | Codex protokolliert die menschliche Freigabe der Motivdatei samt Parameterkorridor; führt Abschnitte 4–7 einschließlich Variantenvergleich, Profilprüfung nach 4.2.1, begrenzter Reparatur, technischer und visueller Prüfung sowie Schwierigkeit aus. | `motif_approved` → `raster_review` → bei freigabefähigem Ergebnis `content_ready`: vorzugsweise 2–3 geprüfte Rasterangebote nach §4.5, echte Ansichten, Abschlussbild, kompakter Vergleich und je Angebot ein geprüftes Paket. Ohne vollständigen Kandidaten die brauchbaren Sichtungsentwürfe nach §4.5 zeigen. Menschliche Auswahl/Endabnahme offen; keine Spielregistrierung. |
| **4 · Endabnahme und Integration** | Codex bindet die menschliche Endabnahme separat und führt Abschnitte 8–9 aus. | `editorially_approved` → `catalog_ready` → `registered`: Integrationsbelege und PR; bei passendem Mergeauftrag Main-Merge, anschließend geprüfte Bereinigung samt eigenem Merge. Ohne Integrationsmerge beim PR stoppen. |

Standardarbeitsteilung: ChatGPT für 1–2, Codex für 3–4. Eine Umgebung darf beides übernehmen, wenn sie die tatsächlichen Bild-, Datei-, Repository- und Werkzeugfähigkeiten besitzt. Diese Oberflächenzuordnung löst keine Modell- oder Ausführungsempfehlung aus (§1); keine Modell-API einbauen. Ein zusätzlicher Mergeauftrag ist nur ohne vorherige passende Freigabe nötig; Korrekturrunden und echte Zugriffsprobleme können weitere Nachrichten erfordern.

**Übergabe ohne Zusatzauftrag:** An jedem Stopp Abschnitt 6 ausführen und ID, Revision, Bild-/Paketpfad, Hashbindung, Branch/Commit sowie nächsten erlaubten Auftrag nennen. Nach Auftrag 2 müssen beide Bilddateien, Abschlussbildfreigabe, Invarianten und vorgeschlagene Parameter bereits verfügbar sein; die noch offene Motivfreigabe erteilt der Mensch direkt in Auftrag 3. Bei beauftragter Repositoryablage automatisch committen/pushen und denselben passenden Draft-PR fortführen. Ohne Schreibzugriff ein schlankes Dateiübergabepaket liefern; Codex übernimmt es bei Auftrag 3. Ohne Lesezugriff erforderliche Quellen einmalig bereitstellen lassen, nicht Fähigkeiten vortäuschen. Bei Chatwechsel den gespeicherten Stand statt impliziter Chatkenntnis verwenden.

Freigaben müssen eindeutig die vorgelegten Dateien/Revisionen beziehungsweise das Paketinventar benennen. Hashes selbst aus diesen Dateien ermitteln; der Mensch muss sie nicht abtippen. Akteur, Zeitpunkt und tatsächliche Erklärung protokollieren, niemals eine Freigabe selbst erteilen. Korrekturwünsche erzeugen eine neue Vorlage zur Freigabe; Rücksprünge nach Abschnitt 4.4. `blocked`, `rejected` und `superseded` brauchen Grund und Revision. `registered` bezeichnet den geprüften Checkout, erst der nachgewiesene Merge die Integration auf `main`; Release bleibt separat.

### Zukünftiger Hintergrundweg in denselben vier Aufträgen

Diese Ergänzung gilt nach der Einführung von 0.7.0 und erzeugt keine zusätzliche
Standardphase. Zustände, Gates und ihre geschlossenen Datenformen stehen in
[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md).

| Vorhandener Auftrag | Zusätzliche Hintergrundarbeit / Entscheidung |
| --- | --- |
| **1 · Abschlussbildauswahl** | Bei feststehender Motivrichtung Kontext und Hintergrundbriefing nach §2.5 sichern; Abschlussbilder weiterhin eigenständig auswählen. |
| **2 · Abschlussbildfreigabe und Abstraktion** | Nach tatsächlicher Abschlussbildfreigabe drei gespeicherte Kontextzeichnungen zusammen mit der Motivvorlage isoliert vorlegen; Auswahl offen führen. |
| **3 · Motivfreigabe und Produktion** | Hintergrundwahl möglichst im selben Eigentümerauftrag wie die Motivfreigabe an die konkrete Datei/Revision binden. Gewählte Bildrevision über Rastervarianten hinweg erhalten. Ohne Wahl bereits autorisierte unabhängige Rasterarbeit fortsetzen und sichern. |
| **4 · Endabnahme und Integration** | Eine noch offene Hintergrundwahl darf mit der bestehenden Endabnahme gebündelt werden. Erst dann das konkret gewählte und gültig abgeleitete Bild oder die ausdrücklich erklärte Leerentscheidung gemeinsam mit dem endabgenommenen Rätsel über den unterstützten #561-Weg integrieren. |

Technische Rasterreife, offene Bildentscheidung, vollständige Hintergrundbereitschaft
und Integrationsberechtigung sind getrennte Aussagen. Eine Auswahlvorlage bei
bereits fertig geprüftem Raster ist noch keine vollständige Integrationsbereitschaft.
Eine fehlende Wahl wird weder zur Empfehlungsauswahl noch zu „bewusst leer“ ergänzt;
sie blockiert nur die davon abhängigen Schritte. Die heutigen 0.6.0-Zustände werden
dafür nicht umgedeutet: Bei `content_ready` bleiben die bisherigen ZA-1-Gates und
allein die noch offene menschliche Endabnahme maßgeblich.

Eine eindeutige frühere Auswahl zur Verwendung derselben unveränderten Datei
genügt als Hintergrundentscheidung; keine zweite Bildbestätigung verlangen.
Die gesonderte Endabnahme und tatsächliche Integrationsbefugnis bleiben erforderlich.
Eine späte Entscheidung an einem versiegelten Rasterpaket nach §6.3 außen binden;
die konkrete vorgelegte Raster-/Bildfassung muss im finalen Auftrag eindeutig sein.

## 4. Rasterproduktion und technische Pflichtprüfung

**Zukünftiger Hintergrundweg:** Die folgenden Import-, Logik-, Paletten- und
Rasterprüfungen behalten ihren eigenen Gegenstand. Hintergründe liefern keine
Zellwerte und werden nicht über Solvererfolg freigegeben. Eine offene Hintergrundwahl
stoppt bereits autorisierte unabhängige Rasterarbeit nicht; technische Rasterreife
allein erfüllt die künftigen Hintergrund-/Integrationsgates aus
[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) jedoch nicht. Für 0.6.0 bleiben die
nachfolgenden `content_ready`-Anforderungen unverändert.

### 4.1 Import und Rastervarianten

1. Von der **freigegebenen gespeicherten Motivvorlage** ausgehen; ihre Ableitung aus dem freigegebenen Abschlussbilds anhand der Dateien, Hashes und dokumentierten Bearbeitung prüfen. Das Abschlussbild nicht als austauschbare nachträgliche Illustration behandeln. Originalbytes, SHA-256, Normalisierung, Rechte, Parameter und Toolversion erhalten. Während der Produktion beginnt die deterministische Prüfung bei Bildbytes, nicht beim Prompt. Nach finaler Integration besteht keine dauerhafte Wiederholbarkeitspflicht (Abschnitt 9).
2. Striktes bestehendes Designformat verwenden; aktuelle Format-/Ressourcengrenzen der README einhalten. Redaktionelle Zusatzfelder in Begleitdateien speichern. Crop-Koordinaten und Seitenverhältnis beachten; nicht stillschweigend strecken.
3. Zunächst **vier gezielte Rasterkandidaten**, mit begründeter Zusatzhypothese höchstens sechs pro Runde erzeugen. Innerhalb der Motivfreigabe beispielsweise zwei Größen mit zwei sinnvollen Parametrierungen vergleichen. Keine blinde Kreuzprodukt-Suche.
4. Unterschiedliche globale Maße, Crops oder Paletten benötigen getrennte Designs. Beim vorhandenen farbigen `area`-Pfad ist der Schwellenwert wirkungslos; reine Schwellenvarianten sind dort keine unterschiedlichen Ansätze. Mono-Schwellen anhand des Bilds wählen.
5. Verfahren mit zwangsläufig leeren Außenkanten, insbesondere der entsprechend implementierte `contour`-Pfad, nicht unverändert als reguläres Ergebnis übernehmen. Standard ist ein mit der Randregel kompatibler Import, derzeit `area`.
6. Gleiche Raster durch exakten Vergleich von Maßen, Palette und Zellwerten erkennen. Kandidatenhashes binden auch Parameter und sind kein reiner Matrixvergleich. Alle Entstehungswege und Ablehnungsgründe erhalten.
7. Echte Raster als verlustfreie Kleinvorschau, vergrößert ohne Glättung und mit Gitter prüfen. Nicht automatisch den ersten logisch erfolgreichen Kandidaten auswählen.

### 4.2 Harte Kriterien

Ein freigabefähiger Kandidat MUSS sämtliche folgenden Bedingungen erfüllen:

- Gültige Maße, Zellwerte, Palette und Formate gemäß Projekt-/Zielvertrag; regulär höchstens 50 je Achse.
- Vordergrundfarbzahl automatisch als `len({v für v in allen Zellen, wenn v != EMPTY})` zählen; sie muss zur endgültigen Palette, zur genauen Nutzervorgabe (falls gesetzt) und zum freigegebenen Parameterkorridor passen. Wunsch, Istzahl und Palettenrollen im Bericht führen; bloße Paletteinträge zählen nicht als Verwendung.
- Hinweise deterministisch aus der exakten Matrix berechnet; geltende Farbregeln eingehalten. Gleichfarbige aufeinanderfolgende Blöcke benötigen mindestens eine Leerzelle, verschiedenfarbige dürfen sich berühren.
- Vollständige deduktive Lösung vom unbekannten Start, ohne vorgefüllte Zellen, notwendiges Raten, Suchannahmen oder Motivwissen.
- Vollständiger Nachweis unter benanntem Solverprofil; unabhängiger Prüfer akzeptiert ihn. Endzustand entspricht exakt dem Kandidaten.
- Herkunftskette Input → freigegebenes Abschlussbild → freigegebene Motivvorlage redaktionell/dateibasiert gebunden; Motivvorlage → Normalisierung → Matrix → Hinweise deterministisch rekonstruiert und sämtliche Datei-/Parameterbindungen geprüft; bei Reparatur zusätzlich Referenz, Plan und Replay.
- Neue Randregel erfüllt:

```text
filled(y,x) := G[y][x] != EMPTY

left   := irgendeine gefüllte Zelle in Spalte 0
right  := irgendeine gefüllte Zelle in Spalte W-1
top    := irgendeine gefüllte Zelle in Zeile 0
bottom := irgendeine gefüllte Zelle in Zeile H-1

gültig := (left OR right) AND (top OR bottom)
```

Jede Vordergrundfarbe zählt als gefüllt. **Nicht alle vier Kanten müssen belegt sein.** Die Formel gilt auch bei Breite/Höhe 1; ein vollständig leeres Raster scheitert. Keine motivfremden Randpixel oder Rahmenlinien nur zum Bestehen der Prüfung hinzufügen.

Eine ausdrücklich erteilte menschliche Ausnahme für eine konkrete Endrevision
darf nach dem [ZA-1-v2-Autorisierungsvertrag](../ZA1_ADAPTER.md) extern an
Originalpaket, Handoff, Inventar, Auswahl und Endfreigabe gebunden werden. Die
verletzte Randregel bleibt als solche im Original und Prüfbericht sichtbar;
keine pauschale Lockerung und kein einfaches `pass`-Flag. Alle anderen
Inhalts-/Nachweisgates bleiben erforderlich. Die menschliche Entscheidung und
eine gegebenenfalls beauftragte Werkzeugerweiterung sind getrennt zu protokollieren.

Ein vollständig gültiger deduktiver Nachweis belegt auch Eindeutigkeit. `stalled` belegt weder Mehrdeutigkeit noch Unlösbarkeit; `aborted` ist ein Abbruch. Exitcode 0 oder ein erzeugtes Importbündel allein ist keine Zertifizierung. Ein generiertes Zahlenbild oder eine KI-Erfolgsaussage ist niemals ein Nachweis.

Die separate [Eindeutigkeitsdiagnose](../PUZZLE_PRODUCTION.md#55-separate-eindeutigkeitsdiagnose-139-paket-a)
aus #139/A untersucht Hinweise zusätzlich auf `unique`, `multiple`, `no_solution`
oder `unknown`. Sie sucht intern und liefert eigene dateigebundene Lösungszeugen.
`unknown` nach genau einer Lösung bestätigt keine Eindeutigkeit. `check-diagnosis`
prüft Dateibindungen und Zeugen, replayt aber keine vollständige Suche.
`unique` hebt `stalled` nicht als Produktionshindernis auf, erzeugt keine Freigabe
und verändert keine Schwierigkeitsbewertung. Die neue Methode 0.2 folgt ausschließlich
dem unabhängig belegten Deduktionsbedarf aus Abschnitt 5.

Das [Paarlinienprofil](../PAIRED_LINES.md) ist als zusätzliches Deduktionsprofil
zugelassen. Seine ausdrückliche Auswahl, Produktionsbindung und Grenzen folgen
Abschnitt 4.2.1. Ein unvollständiger Paarfixpunkt bleibt ohne Freigabe;
Budgetende ist kein Fixpunkt. Alte 0.4.x-Snapshots legitimieren diese Profile nicht.

Die Logik separat in einem frischen Prüferprozess verifizieren. Herkunft zusätzlich mit der vorhandenen Rekonstruktionsprüfung prüfen, beispielsweise `inspect_candidate` beziehungsweise Reparaturverifikation/passendem Export. Nur tatsächlich vorhandene Befehle/API-Funktionen verwenden. Zeit-/Zeilenbudgets je Befehl aus der README übernehmen; fehlgeschlagene Versuche nicht nachträglich umetikettieren.

#### 4.2.1 Profilwahl und Produktionsnachweise

1. **Linienlogik als Ausgangspunkt:** Den zur Mono-/Farbsemantik passenden
   `full-line-mono`-/`full-line-color`-Nachweis auswerten. Ein vollständig
   unabhängig bestätigtes Ergebnis genügt; kein zusätzlicher Paar- oder
   Eindeutigkeitssuchlauf als Routinepflicht für bereits gelöste Kandidaten.
2. **Vor rein logikbedingter Rasteränderung:** Bei einem visuell tragfähigen
   Kandidaten mit unabhängig bestätigtem Linienfixpunkt `stalled` SOLL zunächst
   das passende Paarlinienprofil am unveränderten Raster geprüft werden.
   Eine begründete Abweichung, etwa eine ausdrücklich auf einfachere Techniken
   begrenzte Vorgabe oder ein dokumentierter Ressourcenblocker, festhalten.
   Die bereits zugelassene Profilwahl verlangt keine neue Grundsatzfreigabe;
   Vorgaben zu Motiv, Parametern und Schwierigkeit bleiben wirksam. Die Prüfung
   einer unveränderten Matrix zählt nicht als zusätzliche Rastervariante.
   Bereits durch zwei geprüfte Lösungen belegtes `multiple` direkt nach 4.4
   bearbeiten; ein stärkeres korrektes Deduktionsprofil beseitigt keine Mehrdeutigkeit.
3. **Ausdrücklich und vor dem Lauf binden:** Profil-ID und Zeit-/Linien-/Paarbudgets
   dokumentieren. Bei `import-image` ausdrücklich `--profile paired-lines-mono`
   beziehungsweise `--profile paired-lines-color` und die vorgesehenen Paarbudgets
   verwenden; die Standardaufrufe bleiben Linienlogik. Für einen vorhandenen
   Direktimport dieselbe freigegebene Quelle mit demselben Design in ein neues
   Ausgabeziel importieren und Matrix-/Logikgleichheit kontrollieren. Ein isoliertes
   `solve --profile ...` ist ein Logiknachweis, noch kein exportfähiges Produktionsbündel.
   Niemals nur den Proof in einem alten Manifest austauschen.
4. **Beide Nachweise prüfen:** Der Paarproduktionslauf erzeugt zusätzlich den
   eigenen `full-line-*`-Baselineproof und die Assessmentdatei. Baseline und
   Paarproof derselben Logik in einem frischen unabhängigen Prüferprozess prüfen,
   etwa gemeinsam mit `assess --input ... --proof ... --baseline ...` gemäß
   [Werkzeuganleitung](../../tools/puzzle_production/README.md). Das ersetzt nicht
   Herkunftsrekonstruktion, Endmatrixvergleich und Prüfung der gebundenen
   Produktionsdateien. `assess` erzeugt `picross-quality-report-v1`; dieser
   Zusatzbericht ersetzt weder `picross-deduction-assessment-v1` noch
   `difficulty.json` oder eine menschliche Freigabe.
5. **Ergebnis statt Profilname werten:** Nur eine verifizierte `stalled`-Baseline
   und ein vollständiger verifizierter Paarproof belegen R4 nach Abschnitt 5.
   Eine `aborted`-Baseline, ein unvollständiger Paarproof oder eine bloße
   Eindeutigkeitsmeldung genügen nicht. Bei `stalled`/`aborted` den betroffenen
   Profilnamen, offene Zellen, tatsächlich verbrauchte Budgets und Endgrund
   berichten; keine absolute Aussage, das Rätsel verlange grundsätzlich Raten.
   Budgets nicht nachträglich zur Herstellung eines Erfolgs umdeuten.
6. **Kandidat und Weitergabe:** Importmanifest v2 beziehungsweise Reparaturplan,
   -verlauf und -manifest v2 sowie die passenden versionierten manuellen
   Ableitungen aus [PAIRED_LINES](../PAIRED_LINES.md) verwenden. Die exakte
   `certification` durch alle betroffenen Stufen und `candidate.certification`
   im Handoff führen. Eine Paarreferenz darf nicht in einen alten Ableitungsvertrag
   zurückfallen. Quelle, Motivschutz, Bildfreigaben und Endabnahme bleiben Pflicht.
   Bleibt kein freigabefähiger Kandidat, nach 4.4 innerhalb der bestehenden
   Befugnisse weiterarbeiten oder den konkreten Blocker dokumentieren.

Die separate Diagnose A ist bei einer konkreten offenen Eindeutigkeitsfrage
optional. Sie ersetzt keinen der beiden Deduktionsnachweise und ist keine
Voraussetzung, um das zugelassene Paarprofil auszuwählen. Ihre eigene Suche
und die unabhängige Prüfung ihrer Lösungszeugen bleiben als solche bezeichnet.
Keine zusätzlichen CI-Fälle oder erneute Prüfung unveränderter Bestandsrätsel.

### 4.3 Redaktionelle Kriterien

Verbindliche Referenz ist [PUZZLE_QUALITY §§2–4](../PUZZLE_QUALITY.md):
Flächennutzung, zusammenhängende Hauptformen, Perspektive/Proportionen, Details
und Negativräume, Farbrollen, tatsächliche Raster-/Hinweisansicht und
Abschlussbildkonsistenz getrennt beurteilen. Mono und Farbe behalten ihre
unterschiedlichen Erkennbarkeitsziele. Ein Auge darf eine Einzelzelle sein;
ein Henkel braucht einen Innenraum. Leere Innenstreifen nicht mechanisch entfernen.

Belegungsanteile unter 15 % oder über 85 %, isolierte Einzelzellen und vollständig
leere Innenlinien bleiben **nur Prüfanlässe**, keine automatischen Ablehnungen.
Motivischen Nutzen beziehungsweise Mangel begründen; Form oder Erkennbarkeit
nicht zugunsten einer Kennzahl verschlechtern. Alle tatsächlich verwendeten
Vordergrundfarbpaare betrachten, auch seltene und unbenachbarte Farben. Kleine
Zell-/Hinweisgrößen auf aktuellem Papier mit Kontur/Schraffur sowie normale,
abgeschwächte und ausgekreuzte Hinweise prüfen; Farbsinnsimulation, soweit
verfügbar, ergänzt dies. [Qualitätsvertrag §8](../PUZZLE_QUALITY.md#8-p-a-v01-freigegebene-regel-für-paarweise-farbunterscheidbarkeit)
enthält die **fachlich freigegebene Regel** `picross-palette-separation-1`
für paarweisen Oklab-Ausschluss, Warnzone und getrennte visuelle Beurteilung.
**Aktiv unter Authoring 0.6.0:** RP-3 prüft die konkrete Matrix vor dem
Solver, RP-5 jede Bewertung und feste manuelle Wege die rekonstruierte Matrix
vor dem Endproof-Replay. Negative Entwürfe bleiben zur Diagnose sichtbar.
`check-palette --candidate <vorhandene-*-candidate.json>` bleibt als zusätzliche
lesende Diagnose verfügbar, ersetzt aber kein finales Gate. Nach jeder Änderung
Matrix, IDs/RGB/Nutzung und Regelbindung frisch rekonstruieren; Rücksprünge nach
§4.4 bleiben Pflicht. Ein reiner Palettenentwurf ohne Nutzung ist vorläufig.

Vor `content_ready` das geschriebene Paket mit ZA-1 inspizieren: Der Adapter
erzeugt selbst den aktuellen vollständigen Pflichtbefund und prüft alle Paare
frisch. Ein optional inventarisierter `palette_assessment={file,sha256}` wird
zusätzlich frisch verifiziert. Farbpakete führen `palette_review={file,sha256}`
auf den inventarisierten `picross-palette-visual-review-v1`-Record mit einzeln
gebundenen Q-R04/Q-H01/Q-H02-Urteilen und tatsächlichen Ansichten. Exakte Felder,
Hashes und Bedienung stehen in [ZA-1 P-B2](../ZA1_ADAPTER.md#p-b2--authoring-060-und-additive-palettengeneration-v5)
und der [CLI-Anleitung](../../tools/puzzle_production/README.md#p-b2-automatische-frühdiagnose-und-finale-palettengates).
Fehlende Sichtung, `nicht geprüft` oder stale/falsche Reports erlauben keine
Freigabe. Positiver S-Wert allein erfüllt keine visuellen Kriterien; bei Warnung
oder negativem Sichturteil muss eine konkrete Annahme nach Qualitätsvertrag §6
mit ursprünglichem Urteil, Akteur, UTC, Wortlaut, Begründung und Beleg vorliegen.

Ein negativer technischer Befund bleibt negativ. Für eine tatsächliche Übernahme
braucht es den äußeren `picross-palette-editorial-exception-v1`-Record mit allen
negativen Paaren, exakten S/RGB/IDs, Kandidaten-/Revisions-/Istmatrix-/Quell-/
Regel-/Handoff-/Inventar-/Paketbindung und echter Endfreigabe. Diesen Record nur
außerhalb versiegelter Originale führen und ausdrücklich mit `--palette-exception`
übergeben; vorhandene manuelle Autorisierungen bleiben zusätzlich nötig.
Die Ausnahme heilt ausschließlich den Palettenredaktionsblocker, niemals Proof,
Rechte/Herkunft, Bild-/Motiv-/Endabnahme, feste Parameter, Difficulty oder Randregel.
Fehlende Freigabe bleibt ein Blocker. Bei null qualifizierten Kandidaten §4.5
mit echten Bild-/Rasterlinks, Defiziten/Korrekturen und `Raster-Optionen=[]` nutzen.

Die [F05-Referenzeinordnung nach B-01](../PUZZLE_QUALITY.md#831-b-01-gebundenes-eigentümer-teilfeedback-und-referenzeinordnung)
trennt positives Eigentümer-Teilfeedback von weiterhin negativen Paarmessungen.
Sie ist keine Produktionsausnahme und darf weder als `pass` noch als Freigabe
eines realen Kandidaten übernommen werden. Dafür bleiben §6 des Qualitätsvertrags
und der geprüfte P-B2-Ausnahmeweg maßgeblich. Die F05-Referenzannahme
benötigt keine zusätzliche pauschale Eigentümerausnahme.

Für einen konkreten redaktionellen Mangel gilt der externe, revisionsgebundene
[Einzelfallprozess aus Qualitätsvertrag §6](../PUZZLE_QUALITY.md).
Eine begründete Annahme bleibt getrennt vom negativen Einzelbefund und ersetzt
keine technische Prüfung, Herkunft/Rechte oder tatsächliche Freigaben.

### 4.4 Reparaturen und Änderungen

**Aktiver Reparaturauftrag:** Wenn kein visuell tragfähiger Kandidat vollständig
zertifiziert ist, MUSS Codex gezielte Verbesserungen versuchen, bevor es die
Produktion allein wegen `stalled` oder belegtem `multiple` zurückgibt. Bereits
geeignete Kandidaten brauchen keine Reparatur. Ein Suchurteil `unique` genügt nicht.

Nur visuell tragfähige Kandidaten reparieren. Sind schon die Hauptformen ungeeignet,
zunächst Abstraktion/Größe/Palette nach 2.4 überarbeiten und nötige Freigaben einholen.

1. Ursache trennen: `stalled` betrifft das benannte Profil; Profilwahl nach 4.2.1
   ausschöpfen. Bei offener Mehrdeutigkeitsfrage darf `diagnose` helfen; für
   `multiple` beide Zeugen prüfen und ihre Differenzbereiche auswerten. `no_solution`
   oder `contradiction` bei aus derselben Matrix abgeleiteten Hinweisen ist zunächst
   ein Eingangs-/Werkzeugwiderspruch: Matrix, Hinweise und Dateibindung abgleichen,
   keinen Bildfehler daraus erfinden. `unknown`/`aborted` verlangt Ressourcenanalyse,
   keine Behauptung der Unlösbarkeit. Werkzeugfehler separat melden.
2. **Standard: bis zu zwei gezielte Reparaturrunden**, bei Erfolg sofort stoppen.
   Runde 1 bearbeitet den besten geeigneten Kandidaten. Offene Domains, betroffene
   Kreuzlinien und gegebenenfalls Zeugenunterschiede bestimmen die zulässigen
   Regionen. Motivisch plausible Kontur-, Flächen- oder Negativraumkorrekturen
   begründen; kein Rauschpixel, Zusatzrahmen oder neue Farbe nur als Logikanker.
3. Vor jedem Lauf einen bestehenden RP-5-Plan speichern: unveränderte Referenz,
   Schutzmaske für wichtige gefüllte **und leere** Zellen, Operatoren, Seed und
   Änderungs-/Such-/Abschlussbudgets. Runde 1 standardmäßig höchstens zwei
   geänderte Positionen, bis zu 64 bewertete Kandidaten und 512 Vorschläge.
   Zeit-/Linien-/Paarbudgets passend zur gemessenen Referenz innerhalb der
   Werkzeuggrenzen festlegen; frische Abschlussprüfung separat reservieren.
   Kleinere Suchbudgets nur mit konkretem Grund, nicht als Alibiversuch.
4. Ohne brauchbaren Fund eine **andere begründete Hypothese** prüfen: andere
   geeignete Referenz oder andere motivisch zulässige Änderungsregion. Runde 2
   darf bis zu 128 Kandidaten/1024 Vorschläge nutzen. Ein höheres Zellbudget nur
   vorab motivbezogen begründen; Schutzmerkmale und Freigabekorridor bleiben hart.
   Nicht bloß denselben Lauf wiederholen oder alte Abbrüche umwerten. Ressourcen-
   oder Replaygrenzen können kleinere Runden erfordern; tatsächliche Reichweite
   und Abbruchgrund berichten. Ein früher Stopp ist nur bei Erfolg, fehlendem
   zulässigem Änderungsraum, materieller Motivänderung oder konkretem technischen
   Blocker zulässig. Dann den erforderlichen nächsten Schritt nennen.
5. RP-5 priorisiert offene Zellen und ihre Umgebung, durchsucht aber nur begrenzt
   Einzellokaländerungen; es optimiert nicht selbst anhand der Diagnosezeugen.
   Codex legt daraus Hypothese und Maske fest. Reicht das nicht, eine konkrete
   lokale Formkorrektur oder andere Abstraktion/Größe/Palette vorschlagen und nur
   innerhalb vorhandener Befugnisse umsetzen. Feste manuelle Ableitungen brauchen
   den tatsächlich unterstützten ZA-1-Vertrag und dessen gesonderte Autorisierung;
   keine freie Matrixmanipulation als regulären Import ausgeben. Materielle
   Änderungen vor Fortsetzung erneut zur Motivfreigabe vorlegen.

Für jede Runde genügen Hypothese, Referenz-/Plankennung, tatsächliche Kandidaten-/
Änderungszahl, Endgrund und Auswahlentscheidung im bestehenden Entscheidungsprotokoll.
Kein Erfolg nach begrenzter Suche ist zulässig, aber kein Beweis, dass eine Reparatur
unmöglich wäre. Bei Paarprofilen muss bereits der Plan die versionierte
`certification` binden; neue Hinweise brauchen eigene Baseline und Endnachweis.

Referenz, Ergebnis und markierten Zell-Diff vergleichen. `found` allein genügt nicht: Endnachweis, unabhängige Prüfung, Replay und redaktionelle Bewertung sind erforderlich. Bei schlechter Ausgangsform zuerst Abstraktion/Größe/Rasterpalette korrigieren; die freigegebene Abschlussbildreferenz dabei erhalten.

| Änderung | Erforderliche Wiederholung |
| --- | --- |
| Zellwert oder Rastermaß, auch nur eine Zelle | Neue Revision, Hinweise, vollständiger Logiknachweis, unabhängige Prüfung und Rasterbewertung |
| Quelle, Crop, Palette oder Importparameter | Neuer gebundener Import und vollständige Prüfung |
| Materielle Motivänderung | Zusätzlich erneute ausdrückliche menschliche Motivfreigabe |
| Abschlussbild geändert | Neue Bildrevision und menschliche Abschlussbildfreigabe; Ableitung, Motiv-/Rasterkonsistenz und Endabnahme erneut prüfen. Materielle Änderungen setzen abhängige Motivfreigaben zurück. Kein neuer Logiklauf allein für eine Bildänderung bei nachweislich unverändertem Raster/Logikeingang; nötige Rasteränderungen vollständig neu nachweisen |
| Nur Schwierigkeit/Kategorie/Metadaten | Keine neue Bild-/Rasterproduktion und keine neue Bild-/Endfreigabe allein wegen Kategorieänderung. Metadaten bei versiegelten Paketen außen ergänzen, neue Exportbindung separat aufzeichnen. Bewertungs-/Metadatenrevision; unveränderte Matrix-/Nachweisbindung erhalten |
| Erstmals Paarprofil bei unveränderter Matrix | Neue ausdrücklich profilierte Produktionsbindung, eigener Baseline-/Paarproof und Assessment; keine geänderten Rasterwerte oder umetikettierten Altproofs. Bereits versiegelte Originale erhalten; die neue Lieferung als neue Revision mit echter Regelwerksbindung 0.6.0 führen. Bildfreigaben nur bei unverändertem Gegenstand passend wiederverwenden; Endfreigabe muss das tatsächlich gelieferte Handoff/Inventar binden. |

Eine reine Freistellung ist nach [AT](../REVEAL_TRANSPARENCY.md) eine neue
Bildrevision mit tatsächlicher Abschlussbildfreigabe und erneut geprüfter
Motiv-/Rasterkonsistenz sowie Endabnahme. Die Spezifikationsfreigabe nimmt die
noch nicht erzeugten Bildbytes nicht ab. Originale Bildfreigaben, Handoffs,
Inventare und Integrationsbelege bleiben unverändert; die neue aktive Bildfassung
wird außen gebunden. Bei unveränderten Definitionen samt Runtime-Revision,
Raster und Logikeingang entsteht allein daraus weder neue Rasterproduktion noch
Logik-/Proof-/Schwierigkeitsanalyse. Identität, Ressourcenpfade, Slots, Rating
und Hinzugefügt-Daten bleiben erhalten. Materielle Änderungen bleiben von den
zusätzlichen Freigaben der obigen Tabelle erfasst.

Materiell sind Änderungen an Identität, Pose, charakteristischen Proportionen, wichtigen Innenräumen, Gesichtszügen oder ausdrücklich geschützten Merkmalen. Eine einzelne Zelle kann materiell sein. Auch das Abschneiden ausschließlich leerer Außenlinien verändert das Rastermaß und benötigt neue Nachweise. Manuelle Ableitungen offen kennzeichnen, nicht als unveränderten Originalimport ausgeben.

**Zukünftiger Hintergrundweg – gezielte Bildrevision:** Eine materielle Änderung
an Hintergrundillustration, Komposition oder Transparenz benötigt eine neue
Bildrevision und erneute Auswahl genau der geänderten Fassung; ihre abhängigen
Ableitungen werden ungültig. Bei Ablehnung Grund und nächsten Korrekturschritt
sichern, keine automatische Leerentscheidung treffen. Unveränderte andere
Bilder und Rasterfreigaben bleiben passend gebunden. Die im Hintergrundvertrag
vereinbarte deterministische Größenableitung und unveränderter Pakettransport
brauchen keine erneute kreative Auswahl. Reine Rastergeometrie-/Palettenänderung
erzeugt keine Buchabnahme und keine neue Dreierauswahl; tatsächlich geänderten
Motivkontext gezielt gegen Briefing und gewähltes Bild beurteilen. Reiner
Hintergrundersatz ändert keine Lösungs-, Hinweis-, Paletten-, Schwierigkeits- oder
Saveidentität und erfordert keine unveränderten Logiknachweise. Für die spätere
Bildoperation gelten §8 und der dann unterstützte #561-Vertrag, nicht der
bestehende AT-Abschlussbild- oder Rasterersatzbefehl.

### 4.5 Geprüfte Raster zur menschlichen Auswahl

Aus den ohnehin erzeugten Kandidaten SOLL Auftrag 3 **zwei bis drei sinnvoll
unterschiedliche, vollständig geprüfte Raster** zur Endabnahme vorlegen. Alle
angebotenen Varianten müssen den freigegebenen Parameterkorridor sowie §§4–5
erfüllen: eigene vollständige technische Prüfung, visuelle Bewertung,
Bildkonsistenz und gebundene Schwierigkeit; eine ausdrücklich angenommene
redaktionelle Abweichung folgt [Qualitätsvertrag §6](../PUZZLE_QUALITY.md) und
bleibt als solche sichtbar. Gleiche Matrizen mit anderer Kennung
oder nur anderem Solverprofil sind keine zusätzlichen Angebote. Auswahl und
Empfehlung der KI getrennt benennen; die endgültige Wahl trifft der Mensch.

Die vorhandenen Kandidaten- und Reparaturbudgets werden nicht zur Erfüllung einer
Quote erweitert. Bei nur einem freigabefähigen Ergebnis eine Option anbieten.
Bei keinem MUSS die KI nach [Qualitätsvertrag §5](../PUZZLE_QUALITY.md) zwei bis
drei möglichst unterschiedliche beste brauchbare vorliegende Entwürfe zeigen,
sofern vorhanden; bei nur einem diesen. Weitere sinnvolle Entwürfe im Protokoll
auffindbar halten. Jede Sichtungsansicht nennt stabile ID/Revision, tatsächliches
Raster und Abschlussbild mit echten Bild-/Dateilinks, technische Prüfungen/Lücken,
maßgebliche Qualitätsdefizite und Korrekturmöglichkeiten sowie den Status
`Sichtungsentwurf – nicht integrationsbereit`. Auch technisch nicht zertifizierte
Entwürfe dürfen zur Diagnose betrachtet werden. Ohne brauchbaren Entwurf den
konkreten Nichtfund und nächsten Korrekturschritt nennen, keine Dateien erfinden.

Sichtungsentwürfe sind keine Integrationsoptionen: `Raster-Optionen=[]`, kein
`content_ready`; tatsächlichen Stand als `raster_review` beziehungsweise `blocked`
mit Grund führen. Eine mögliche gezielte redaktionelle Annahme nach
[Qualitätsvertrag §6](../PUZZLE_QUALITY.md) bleibt extern an Kandidat, Palette,
Inventar und Regelstand gebunden. Erst nach zulässiger Korrektur beziehungsweise
dokumentierter Einzelfallentscheidung und vollständigen aktuellen technischen
Prüfungen darf ein Kandidat im bestehenden gültigen Auswahlweg erscheinen.
Fehlende Proofs oder unklare Rechte bleiben Blocker. Empfehlung und Auswahl
erteilen keine automatische Freigabe.

Jedes Angebot erhält eine im Auftrag stabile ID (etwa `R-A-r03`), eine kurze
Beschreibung seiner Unterschiede, Maße/Modus/Istfarbzahl, Schwierigkeit und echte
Rasteransichten. Vor der Ausgabe wird **je Raster eine eigene kollisionsfreie
Paketrevision derselben Rätsel-ID** nach §6 gesichert, beispielsweise `r03`, `r04`
und `r05`. Jede Revision bleibt ein bestehendes Einzelkandidatenpaket mit genau
einem `handoff.candidate`, vollständigen benötigten Inputs und eigenem Inventar.
Alle angebotenen ZIPs auf dem geschriebenen Stand nach §6.1 prüfen; keine neue
Mehrfachkandidaten-Hülle im Adapter und keine Alternativen-ZIPs ineinander packen.
Der gemeinsame Vergleich darf Beleglinks nutzen, ersetzt aber keinen Paketeingang.

Die Sheet-Option bindet genau das jeweilige Paket samt Revision, Originalinventar,
Quelle und Bild-/Rasterbezügen. Auftrag 4 übernimmt ausschließlich die ausdrücklich
gewählte Option; Auswahl-ID und Paketbindungen im Auftrag abgleichen, dann die
bestehende Endfreigabe extern an dieses Originalpaket binden. Keine automatische
Wahl der ersten/empfohlenen oder vermeintlich neuesten Revision über den Index.
Kein Neuversiegeln beim Wechsel im Sheet. Nicht gewählte Angebote bleiben bis zur
finalen Integration erhalten; §9 regelt anschließend die Bereinigung.

**Zukünftiger Hintergrundweg:** Eine einzige Hintergrundauswahl derselben
unveränderten Bildrevision kann zu den motivisch passenden Rasterangeboten
gehören; Rasterversuche erzeugen keine Reveal×Raster×Hintergrund-Kreuzmatrix.
Bei noch offener Bildentscheidung die Angebote ausdrücklich als technisch
rasterreif mit offener Hintergrundwahl kennzeichnen und nach dem künftigen
Bereitschaftsvertrag sichern. Das ist kein heutiges 0.6.0-`content_ready`-Paket
mit zusätzlichem unbeachtetem Blocker und keine Hintergrundoption im Sheet v2.
Für spätere Auswahl und gemeinsame Endabnahme die Originalpakete unverändert
erhalten und die tatsächliche Entscheidung extern nach §6.3 binden.

## 5. Schwierigkeit L1–L5

**Zukünftiger Hintergrundweg:** Hintergrundstatus und Bildauswahl fließen nicht
in die Schwierigkeit ein. Bei ausschließlich geänderter Hintergrundrevision
bleiben passende unveränderte Analyse-/Proofbindungen erhalten; kein neuer
Solver- oder Schwierigkeitslauf allein wegen dieser Bildarbeit. Für tatsächliche
Logik-/Paletten-/Rasteränderungen gelten weiterhin die eigenen Nachweispflichten
aus §4 und den nachfolgenden Bewertungsverträgen.

### 5.1 Historische Produktionsmethoden 0.1 und 0.2

**Logische Schwierigkeit, Rastergröße, Bearbeitungsumfang und Lösungszeit getrennt angeben.** Große Matrizen oder viele Eingaben sind nicht automatisch schwierig. Sterne-/Fehlerbewertung im Spiel bleibt unabhängig.

Für neue Paarprofilbewertungen `picross-difficulty-0.2` verwenden; reine Linienfälle
dürfen weiterhin nach 0.1 bewertet werden. Alte Bewertungen nicht überschreiben
oder als rückwirkende 0.2-Berechnung ausgeben. Den Lösungsverlauf anhand von
Hinweisen und bisher bewiesenen Domains beurteilen. Profilverwendung allein
beweist keine Notwendigkeit seiner stärksten Technik.

| Technik | Bedeutung |
| --- | --- |
| R0 | Direkte Voll-/Leerbelegung, vollständige Packung, Restleerfelder nach eindeutig abgeschlossenen Blöcken |
| R1 | Überlappungen sowie Grenzen/Verlängerungen eindeutig zugeordneter Blöcke |
| R2 | Kombinierte Zuordnung mehrerer Blöcke/Segmente; mehrere Anker, Trennungen oder Farbregeln zusammenführen |
| R3 | Allgemeine vollständige Zeilenunterstützung, komplexe Alternativen und partielle Farbdomänen, soweit nicht durch R0–R2 erklärt |
| R4 (0.2) | Notwendige gemeinsame Paarlinienlogik gemäß B-D01, belegt durch separat verifizierten unvollständigen Linienfixpunkt und vollständigen Paarproof derselben Logik |

| Stufe | Einstufungskriterium |
| --- | --- |
| **L1 – sehr leicht** | R0 reicht vollständig. |
| **L2 – leicht** | R1 erforderlich, R0+R1 reichen. |
| **L3 – mittel** | R2 erforderlich und ausreichend; keine definierte Engstelle beobachtet. |
| **L4 – schwer** | R2 mit Engstelle oder R3 ohne Engstelle. |
| **L5 – sehr schwer** | R3 mit Engstelle oder unter 0.2 notwendige R4; diese zusätzlich ausdrücklich als „linienübergreifend / besonders hoher logischer Anspruch“ kennzeichnen. Keine L6-Stufe. |

**Vorläufige Engstellendefinition:** mindestens drei aufeinanderfolgende informative R2/R3-Schritte; jeweils höchstens zwei produktive Linien und höchstens vier Zellen mit Domänenänderung pro Schritt. Ein Schritt ist eine Regelanwendung an einer Linie einschließlich ihrer begründeten Änderungen. Restaufräumen ignorieren, sobald höchstens `max(5, ceil(0.02 × W × H))` Zellen mehrdeutig bleiben. Die Schwellen gehören zur Methodenversion, nicht zum mathematischen Lösbarkeitsvertrag.

Vorgehen:

1. Stärkste belegte Technik und typische Engstellen anhand eines nachvollziehbaren Lösungsverlaufs bestimmen. Gleichzeitig mögliche Fortschritte und deren räumliche Verteilung berücksichtigen; aus einem sequentiellen Proof nicht ungeprüft auf fehlende Alternativen schließen.
2. Hinweisstruktur und Farbabhängigkeiten dokumentieren. Farbzahl, Schrittzahl, Laufzeit und Zellzahl dürfen die Stufe nicht allein erhöhen. Lange einfache Fortschrittsketten bleiben einfach.
3. Ohne validierten Bewertungsanalysator `editorial_estimate` verwenden: Hauptstufe, plausiblen Bereich, konkrete Begründung und Vertrauen angeben. Eine begründete KI-Einstufung **genügt ohne menschliches Probespiel**. Nicht erschöpfend geprüfte Techniknotwendigkeit/Engstellen als unsicher kennzeichnen.
4. `instrumented` nur bei tatsächlich vorhandener geprüfter Instrumentierung verwenden. Diese muss schwächere Regelfamilien bis zum Fixpunkt testen, Fortschrittsmöglichkeiten erfassen und einen festgelegten Bewertungsweg verwenden. Keine solche Fähigkeit erfinden.
5. Vertrauen: `low` bei KI-Schätzung/ungeklärten Technikgrenzen; `medium` bei vollständig überprüfter Bewertung ohne belastbare menschliche Kalibrierung; `high` erst mit validierter Methode und passenden Vergleichsdaten. Geringes Vertrauen oder fehlende Kalibrierung ist kein Abnahmeblocker; eine unbegründete Stufenzahl ist unvollständig.
6. Lösungszeit ohne belastbare Daten als `null`/„nicht geschätzt“ ausgeben. Optionale spätere Versuche mit Erfahrungsgruppe, aktiver Zeit, Hilfen, Abbruch und getrennten Urteilen zu Logik/Arbeitsumfang erfassen. Darauf Methode und Zeitprognosen versioniert kalibrieren; Produktion nicht auf diesen Datensatz warten lassen.

Für R4 lautet `assessment_type=instrumented`, `confidence=medium`, Stufe und
plausibler Bereich L5. Das belegt nur R4-Notwendigkeit, keinen vollständigen
R0–R3-Analysator und keine menschliche Kalibrierung. `evidence` referenziert die
inventarisierte Assessmentdatei; `profile_hash` bindet den geprüften Paarproof,
`logical_demand` enthält die obige Kennzeichnung. ZA-1 prüft Baseline und stärkeren
Proof frisch. Ohne notwendigen R4 bleiben die R0–R3-Kriterien und Schätzgrenzen.

Stagniert das gewählte Profil, ist das Rätsel nicht freigabefähig; es bekommt
keine zusätzliche Stufe. Neue Bewertung unveränderter Hinweise braucht keine
Bild-/Rasterproduktion; ein erstmals beanspruchter stärkerer Technikbedarf
verlangt die dazugehörigen neuen Nachweise. Ein Abbruch oder bloß verwendeter
Paarschritt belegt keine Notwendigkeit. Keine Aussage über sämtliche denkbaren Regeln.

### 5.2 Aktueller zusätzlicher Integrationsstandard SD

Ab SD-C1 ersetzt [SD](../PUZZLE_DIFFICULTY.md) die freie neue
Schätzung durch den zentralen ausdrücklich manuellen Analyseweg nach finaler
Deduktionsprüfung. Ein passend gebundener vollständiger Bericht wird bei der
Integration wiederverwendet. Gleiche Methodenversion und Eingabe bestimmen
dieselbe Bewertung für neue Rätsel und ausgewählte Bestandsrätsel. Abbruch oder fehlende
Analyse darf nicht durch eine unbegründete Stufe oder ersatzweise 5 verdeckt werden.

Vor redaktioneller Endfreigabe erzeugt `catalog_analysis candidate` aus endgültiger
Matrix, Design und normalisierter Logik einen ausdrücklich vorläufigen Schema-2-Input
mit derselben Farbabbildung wie ZA-1. `analyze` beziehungsweise `import` prüft das
volle Bundle; passende R4-Baseline-/Paarproofs ausdrücklich angeben, kein Routinepaarlauf.
Nach Endfreigabe/Export bindet `rebind` die tatsächlichen Definitionsbytes bei
identischer ID/Logik/Matrix; ursprüngliches `rating.source` bleibt erhalten.
Befehle und Budgets: [Werkzeuganleitung](../../tools/puzzle_production/README.md).

R0–R3-Instrumentierung, synchrone Wellen, Engstellen und begrenzter Größenbeitrag
folgen dem eigenen Bewertungsvertrag; vollständige R0-Fälle bleiben auch groß
sehr leicht. R4 behält seinen unabhängigen Baseline-/Paarbeleg. Zahlen und
Übergänge werden vor Bestandsanwendung an unabhängigen synthetischen Referenzen
gebunden. Der reale Katalog bestimmt keine Skalenenden, muss nicht alle Stufen
besetzen und darf weder direkt noch als Kopie automatisierter Testbestand werden.

Neue aktive Bewertungen liegen außerhalb versiegelter Originalpakete und ändern
keine alten Schätzungen, Handoffs, Inventare oder Freigaben. Eine reine Neubewertung
braucht keine neue Bild-/Rasterproduktion oder Motiv-/Endfreigabe. Ohne geänderte
Logik lösen Titel, Kategorie oder Reveal keinen erneuten Analyselauf aus.
Menschliches Probespielen bleibt optional; geprüfte synthetische Referenzen
begründen keine Behauptung empirischer menschlicher Kalibrierung.

## 6. Dateien, Übergabe und Wiederaufnahme

§§6.1–6.2 beschreiben die heute unterstützte Ablage und Übergabe unter 0.6.0.
Für den noch nicht aktivierten Hintergrundweg gilt zusätzlich §6.3 mit den
neuen Formen des zentralen Hintergrundvertrags; alte Hüllen bleiben unverändert.

### 6.1 Repositoryablage während der laufenden Produktion

Die folgenden Aufbewahrungs- und Replaypflichten gelten bis zur finalen Integration. Danach löst Abschnitt 9 sie ab.

- Zuerst `content/authoring/index.json` und die Runtime-Registry `content/registry.json` lesen. Stabile motivneutrale ID gemäß ZA-1 vergeben; ID, Revision und Pfad auf Kollision prüfen. Bei Wiederaufnahme das verzeichnete Paket am angegebenen Branch/Commit selbst laden; keinen erneuten Upload verlangen, wenn die Bytes zugänglich sind. Mehrdeutige Auswahl klären, fehlenden Binärzugriff konkret melden.
- Ablage: `content/authoring/<puzzle_id>/<revision>/package.zip`. Daneben `handoff.json` als bytegleiche lesbare Kopie, `record.json` und gegebenenfalls die separate `approval.json`. Ein Paket pro Phasenübergabe, Freigabevorlage oder Chatwechsel; keine ZIPs nach jedem Toolaufruf. Bereits vorgelegte Revisionen niemals überschreiben. Neue Inhalte erhalten eine neue Revision; identische Bytes werden wiederverwendet.
- Für diese Übergabe keine zusätzliche Codex-Handoff-Markdowndatei oder duplizierte Folgeauftragsdatei erzeugen, beilegen oder separat verlinken. Das technische `handoff.json`, Inventar, Parameter, Freigaben und Belege bleiben nach diesem Abschnitt vollständig erforderlich. Vorhandene versiegelte Pakete mit einer früher ergänzten Markdowndatei behalten ihre Bytes und Bindungen; diese Straffung beauftragt keine nachträgliche Bereinigung.
- `content/authoring/index.json` ist der von der KI gepflegte Arbeitsindex, **keine Runtime-Registry**. Pro ID/Revision: relativer Recordpfad. `record.json` führt zusätzlich `category_id`, sobald die Motivzuordnung feststeht (bei offenem Briefing ausdrücklich `null`; alte Records ohne Feld bleiben lesbar). Spätestens vor kategorisiertem Export ist eine gültige Zuordnung Pflicht. `record.json` führt Format `picross-authoring-record-v1`, ID/Revision, Phasenstatus, Paketpfad/-größe/-SHA-256, Handoffpfad/-SHA-256, Inventarhash (oder ausdrücklich noch offen), Abschlussfreigabepfad/-hash oder `null`, Maße/Modus/Schwierigkeit soweit bekannt, Blocker, nächsten erlaubten Schritt und Integrationsbeleg oder `null`. Branch/Commit der Sicherung in der Übergabe nennen; noch nicht gemergte Ablage nicht als `main` ausgeben. Paket, Handoffkopie und Index gemeinsam committen/pushen, sobald dieser Umfang beauftragt ist; Merge gemäß Entwicklungsworkflow.
- UTF-8-Markdown/JSON, bestehende Matrix-/Proofverträge und verlustfreie Bilder verwenden. Quellenbytes, Herkunft/Nutzungsgrundlage, tatsächliche Bildprompts/-einstellungen (`not_exposed` wenn unbekannt), ausgewählte Bilder, Freigaben, Parameter und Nachweise behalten. Ungeklärte Nutzungsrechte blockieren die Katalogfreigabe. Versuchshypothese, Auswahl-/Ablehnungsgrund, Bildaufrufe, Überarbeitungsrunden, Import-/Reparaturversuche und aktive Menschenminuten getrennt erfassen; unbekannte Werte als `null` führen.
- Vor einer Auswahl alle noch angebotenen Bildvarianten behalten. Nach der Auswahl verworfene ungebundene Bildvarianten nur in ihrer früheren Repositoryrevision belassen; im aktuellen Paket reichen Entscheidung, Hash und genauer früherer Fundort. Keine alten ZIPs in neue ZIPs einbetten. Allgemeine Projekt-/Workflowdokumente und Toolquellen über Repositorycommit/Pfad referenzieren, nicht pro Rätsel kopieren. Ausnahme: den von ZA-1 verlangten, hashgebundenen Regelwerks-Snapshot mitführen.
- Vollständige erforderliche RP-3-/RP-5-Bündel unverändert behalten: Original-/Normalisierungsbild, Design, sämtliche manifestgebundenen Kandidaten, Eltern, Masken, Logik, Proofs und Vergleichsdateien. Bei Paarprofilen gehören auch sämtliche manifestgebundenen Baselineproofs und Assessmentdateien dazu, einschließlich Kandidaten- und frischer Abschlussnachweise einer Reparatur. Auch HTML oder ein verworfener Kandidat ist Pflicht, wenn ein Manifest/Replay ihn bindet. Finale echte Rasteransicht, Bildvergleich, Schwierigkeit, Qualitätsbericht und Belege aller Freigaben/Gates behalten.
- Ungebundene doppelte Berichte, stdout/stderr-Kopien, eingebettete Bildgalerien, temporäre Ansichten, Caches und vollständige Chat-/Repoarchive weglassen. Relevante Fehlversuche als kurze strukturierte Einträge erhalten. Dateien nicht allein anhand der Endung löschen; alle benötigten technischen **und redaktionellen** Referenzen nachverfolgen. HTML/Code aus Paketen nicht ausführen.
- Ein neues Paket vor Inventarisierung verschlanken. Bereits versiegelte Pakete ausschließlich als deklarierte Teilkopie nach `picross-authoring-derivation-v1` ableiten: Originalhandoff/-inventar und ihre Hashes unverändert, Original-ZIP-Hash binden, tatsächlich enthaltene Dateien vollständig hashen. Weglassungen und Grund im äußeren Record dokumentieren. Keine erfundene neue Vollkopie, keine stillschweigende Neuversiegelung oder Umschreibung alter Freigaben. Nachweisbündel nicht intern kürzen. Das Original nicht destruktiv ersetzen.
- Inventar und Handoff ohne Selbstreferenz nach ZA-1 binden; Datei-SHA-256 und kanonische Vertrags-Hashes unterscheiden. Nach Versiegelung spätere Endfreigabe und Integrationsstatus ausschließlich in separater Freigabe/Record führen; das Originalhandoff dafür nicht ändern.
- Vor Ablage ZIP sicher öffnen, Dateimenge/Hashes und Handoffkopie prüfen. Ab `content_ready` zusätzlich ZA-1 `inspect` auf dem **geschriebenen ZIP** ausführen; fehlende Endabnahme darf als einziger entsprechender Blocker bleiben. Frühere Bildphasen sind noch kein ZA-1-Eingang: deren vorhandene Dateibindungen/Freigaben prüfen, keine Adapterzertifizierung behaupten. Der lokale [PB-A-Builder](../../tools/puzzle_production/README.md#pb-a-deterministischer-authoring-paketbau) übernimmt diese Schritte aus einem expliziten hashgebundenen Bauauftrag: `python -m tools.puzzle_production.authoring_builder build --request <request.json> --source-root <quellen> --output-root <arbeitsordner> [--publish-to <checkout>]`. Er sichert neue unversiegelte 0.6.0-Revisionen, erhält offene Entscheidungen und aktualisiert auf ausdrückliche Zielwahl nur den Authoringindex. Kein Git-Commit, keine Freigabe oder Registrierung. Bereits versiegelte Originale weiter unverändert lesen beziehungsweise nur nach dem bestehenden Teilkopievertrag ableiten.
- BA-A verwendet den vorhandenen Builder ausschließlich mit `target=local` und `publish_to=None`. Der vollständige Bauauftrag, seine Quellen-, Regelwerks- und Freigabebindungen bleiben unverändert; fehlt der Auftrag, wartet die Stufe mit `waiting_input`. Ein ausdrücklich fortgeschriebener Plan darf den tatsächlichen Auftrag ergänzen. Der Runner erzeugt keinen Request und ersetzt keine fehlende Erklärung. `package`, `handoff` und `record` verweisen auf die wirklichen Builderdateien; `sheet_update` ist dessen unveränderte `sheet`-Projektion im technischen Runnerresultat, keine zusätzliche Builderdatei. Lokaler Bau belegt weder Repositorysicherung noch Endabnahme oder Integration.
- `content/authoring/` bleibt außerhalb des Spiels. Nach Integration erzeugt ZA-1 die offline prüfbare Kopie unter `content/packages/<id>/<revision>/`; dieser Ort ist kein manuell zu befüllender Eingang. Keine zusätzlichen Voll-ZIPs dort erzeugen. Alte Produktionsstände über feste Git-Commits referenzieren; Bis zur finalen Integration keine gebundenen Nachweise löschen. Danach ist Abschnitt 9 Pflicht; keine LFS-Umstellung oder Git-Historienbereinigung.

### 6.2 Übergabedatensatz

Die KI MUSS einen aktuellen Übergabedatensatz in diesem Begleitformat führen. Er ersetzt keine Werkzeugeingabe. Platzhalter/`null` sind keine Nachweise. Im Paket bleiben alle Pfade relativ; technische Prüfinputs müssen darin vollständig vorliegen. Der äußere Repositoryrecord verwendet repositoryrelative Pfade. Historische Vergleichsreferenzen dürfen auf genaue frühere Commits zeigen; sie ersetzen keinen Replayinput.

```yaml
format: picross-authoring-handoff-v2
rulebook: {version: "0.6.0", file: "<Regelwerk>", sha256: null}
puzzle_id: "<stabile ID>"
revision: "<Paketrevision>"
repo_commit: "<vollständige tatsächlich gelesene SHA>"
state: brief_ready
brief: "<Datei mit Auftrag, Invarianten, Grenzen und Herkunft>"
approved_parameters: []
reveal: {file: null, sha256: null, approval: null}
motif: {file: null, sha256: null, derived_from_reveal_sha256: null, approval: null}
candidate: {bundle: null, variant: null, proof: null, verification: null, certification: null}
palette_review: null # 0.6.0: inventarisierter Sichtrecord bei Farbe vor content_ready
palette_assessment: null # optionaler gespeicherter Befund, immer frisch nachgeprüft
origin_verification: null
repair: {reference: null, plan: null, replay: null}
inventory: {file: null, sha256: null}
difficulty: null
report: null
decisions: "<Varianten-/Entscheidungsprotokoll>"
effort: "<Aufwandsprotokoll>"
gates:
  reveal_approval: pending
  motif: pending
  provenance: pending
  logic: pending
  frame: pending
  visual: pending
  difficulty: pending
  reveal_consistency: pending
  final_editorial: pending
  target_export: pending
playtest: {status: not_performed, evidence: null} # Information, kein Gate
blockers: []
next_action: "<nächster erlaubter Schritt>"
authorization: "<tatsächlich erteilter Arbeitsumfang>"
```

Bei einem Paarprofilkandidaten `candidate.certification` vor Versiegelung durch
exakt `{profile, max_pair_work, max_pair_records}` aus dem geprüften
Produktionsmanifest beziehungsweise Plan ersetzen; keine frei abweichenden
Budgetangaben. `difficulty` verweist auf die Datei nach Abschnitt 5. Deren
`evidence` ist genau die zugehörige inventarisierte Assessmentdatei neben dem
gewählten Proof: beim Import `<variant>-assessment.json`, bei einer Reparatur
`final-assessment.json`, bei fester Mono-Entfernung `certificate/assessment.json`
unter dem jeweiligen Bundlepfad. Zugehörige Baseline und Paarproof mitführen.
Frühe Bildphasen benötigen diese noch nicht entstandenen Dateien nicht.

Gates verwenden `pending|pass|fail|blocked`. Jedes `pass` braucht einen konkreten Beleg im Bericht/Inventar. Fehlende Probespiele sind kein Blocker und benötigen keinen Ausnahmeentscheid. Menschliche Freigaben müssen Gegenstand/Hash, Akteur, UTC-Zeitpunkt und tatsächliche Erklärung enthalten.

Beim Übergang aus v1 fehlende Abschlussbildfreigabe oder Ableitungsbindung ausdrücklich als offen erfassen; niemals aus einer alten Motivfreigabe erfinden.

Nach Chatwechsel zuerst den Repositoryindex auflösen, dann Regelwerk, Übergabe, Pflichtquellen, Freigaben und referenzierte Dateien lesen; Hashes prüfen. Nur den nächsten autorisierten Schritt fortsetzen. Fehlenden Gesprächskontext nicht erfinden, gültige Freigaben nicht unnötig erneut einholen und den Toolstand nicht heimlich wechseln.

Für lokale BA-A-Arbeitsstände gelten zusätzlich die geschlossenen Plan-/Checkpoint-
und Budgetregeln aus [PRODUCTION_BATCH](../PRODUCTION_BATCH.md). Wiederaufnahme
prüft die tatsächlichen Originale fachlich frisch; ein gespeicherter Erfolg oder
Dateihash allein genügt nicht. Verbrauchte Versuche bleiben auch nach Unterbrechung
und Planfortschreibung erhalten. `status` zeigt nur den historischen, nicht frisch
fachlich geprüften Stand. Offene Entscheidungen blockieren ihre abhängigen Stufen;
bereits autorisierte unabhängige Arbeit darf weiterlaufen. `completed` bezeichnet
den erledigten technischen Schritt, niemals automatisch `content_ready` oder eine
menschliche Endabnahme. Reine Hintergrundänderungen entwerten keine unveränderten
Logik-/Proof-/Difficultyartefakte. Finale Fortschreibung und Integration bleiben
außerhalb dieses Runners.

### 6.3 Zukünftiger Hintergrundweg: Sicherung, Auswahl und Wiederaufnahme

[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) definiert die geschlossenen
Arbeits-, Entscheidungs- und Ableitungsformen sowie deren azyklische Hashbindungen.
Für den vollständigen Weg sind Authoring **0.7.0**, Handoff **v3**, Record **v2**
und Sheet-Update **v3** vorgesehen; Inventar **v1** und Arbeitsindex **v1** bleiben.
PB-H unterstützt diese neuen Paketformen und ihre lesende Inhaltsprüfung
ausschließlich mit dem vollständigen [0.7.0-Vorschausnapshot](PUZZLE_AUTHORING_0_7_0_PREVIEW.md);
der aktive 0.6.0-Default bleibt erhalten. MJ-A transportiert beide Wege getrennt. `raster_ready`
erfüllt alle bisherigen Inhaltsgarantien bei noch offener Hintergrundbereitschaft;
`content_ready` verlangt zusätzlich gültige Wahl, Rechte/Sichturteile und frisch
geprüfte Ableitung beziehungsweise ausdrückliches `none`. Endfreigabe v2 wird
als bereits vorhandener, exakt gebundener Beleg gelesen. HP-I1a ergänzt den
sicheren äußeren Finalizer nach Hintergrundvertrag §7.4 und den
[v6-Export](../ZA1_ADAPTER.md#hp-i1a--äußere-endabnahme-und-export-v6).
Original-ZIP, Handoff, Inventar und frühere Gates bleiben unverändert; der neue
Record/Sheet-Stand reicht höchstens bis `editorially_approved`. HP-I1b1 ergänzt
zielgebundene Erstintegration und deren Abschluss. Die echte Capability folgt
dem HP-I2-Runtime-/Abnahmevertrag. HP-I1b2 liefert späteren Ersatz nach dem
eigenen Requestvertrag, HP-I1c die erlaubte Raster-/Revealneubindung bestehender
Hintergrundziele. MJ-A führt den regulären Sheetweg; der spätere eigenständige
Hintergrundänderungsjob folgt MJ-B nach Hintergrundvertrag §7.6.
HP-W2 unterstützt die eigenständigen Arbeits-/Entscheidungs-/Auftrags-/
Befundformen nach Hintergrundvertrag §§3–4 sowie `describe/derive/verify`.
Beauftragte frühe Bildarbeit darf damit als vorbereitet gesichert, eine tatsächlich
gewählte Datei abgeleitet und der Befund frisch lesend geprüft werden; ausdrücklich
`none` liefert nur einen Nullbefund. [Lokale Aufrufe und Grenzen](../../tools/puzzle_production/README.md#hp-w2-eigenständige-hintergrundableitung).
Die eigenständige Ableitung erzeugt weder einen gültigen Altformeingang noch
eine finale ZA-1-Zulassung und ersetzt keine offenen Rechte-/Sichturteile. Nur die tatsächlich unterstützte
Einführungsmatrix anwenden.

Während einer offenen Auswahl müssen alle drei tatsächlich angebotenen
Einzelbilder mit ihrem Arbeitsstand gespeichert und erreichbar sein. Pfade,
Bildrevisionen, Originalbytes/-hashes, Herkunft/Rechte und tatsächlich bekannte
Generierungsdaten binden; Unbekanntes ausdrücklich unbekannt lassen. Eine
Vorschau, ein Prompt oder ein Dateiname ersetzt keine gesicherte Originaldatei.
Ausstehend, vorgelegt, abgelehnt, konkret gewählt und ausdrücklich bewusst leer
nach dem zentralen Vertrag unterscheiden. Legacy ist eine Einordnung alter
Verträge, kein Zustand für neue Arbeit. Deklarierte fehlende, defekte,
inkonsistente oder nicht unterstützte Daten sind Fehler und niemals „leer“.

Eine tatsächliche Auswahl darf vor dem endgültigen Raster oder erst zusammen
mit dessen Endabnahme erfolgen. An einem bereits versiegelten Kandidatenpaket
wird sie **außerhalb des Originals** an dessen unveränderte Paket-, Handoff- und
Inventarbytes sowie den genauen Hintergrundarbeitsstand gebunden. Die finale
Endfreigabe bindet das wirklich vorgelegte Rasterpaket und die konkrete
Auswahl-/Leerentscheidung samt erforderlicher Ableitung. Keine früheren Handoffs,
Inventare, Freigaben oder Original-ZIPs nachträglich ändern und keine neue
Versiegelung als angeblich identisches Original ausgeben. Eine passende frühere
Auswahl unveränderter Bildbytes wiederverwenden; der Mensch muss keine Hashes
abtippen und nicht dasselbe Bild erneut bestätigen.

Bei Wiederaufnahme zuerst den genauen Arbeits-/Paketstand und alle externen
Entscheidungen samt Bildbytes prüfen. Unabhängige bereits autorisierte Rasterarbeit
darf bei offener Bildwahl weiterlaufen; das fehlende Hintergrundgate bleibt
sichtbar. Nach Ablehnung oder materiellem Korrekturwunsch nur die betroffene neue
Bildfassung erneut vorlegen, ungültige Ableitungen nach §4.4 ersetzen. Reiner
späterer Hintergrundersatz ist ein eigener Bildauftrag mit Bindung an die aktive
Integration; abgeschlossene Rasterproduktion dafür nicht rekonstruieren.
Während laufender Arbeit erforderliche Originale erhalten; Erhalt und Ende der
Arbeitsdateien folgen §9 und dem Hintergrundvertrag, nicht einem Dauerarchiv.

## 7. Freigaben und Abschlussausgabe

Die KI MUSS zuerst die farbigen detaillierten Abschlussbildvarianten zur Auswahl und die gewählte Dateirevision zur ausdrücklichen Freigabe vorlegen. Zur anschließenden Motivfreigabe MUSS sie Abschlussbild und daraus abgeleitete Motivdatei, ihre Revisionen, den Parameterkorridor und die zu bewahrenden Merkmale gemeinsam zeigen. Zur Endabnahme MUSS sie das tatsächliche finale Raster, das Abschlussbild, alle Pflichtprüfungen und offene Abweichungen vorlegen. Eine gültige Freigabe bezieht sich auf genau diese Dateien beziehungsweise das gebundene Paketinventar.

Den Abschlussbericht auf eine kompakte Seite plus Beleglinks begrenzen. Er MUSS enthalten:

- ID, Revision, Status, Datum, Regelwerksversion, Toolcommit und Inventarhash.
- Abschlussbildfreigabe, Abstraktionsfreigabe und Endabnahme mit Beleg beziehungsweise ausdrücklich offenem Status.
- Gewählten Kandidaten, wesentliche Ablehnungsgründe und echte Raster-/Abschlussbilddateien.
- Maße, Zellzahl, Modus, Palette; Motivqualität, Änderungen, Reparaturdiff und begründete weiche Ausnahmen.
- Gewünschte und tatsächlich verwendete Farbzahl, Funktion der Farben und begründete Abweichung; Ergebnis beziehungsweise konkreter Entfallgrund der Reparaturrunden.
- Ergebnisse und Dateibelege für Produktmaße, Randregel, Herkunft, Hinweise, vollständigen Nachweis unter benanntem Profil, unabhängige Prüfung und Endmatrixgleichheit. Bei Paarprofilen Baseline-/Paarstatus und Assessmentbindung getrennt nennen; eine optionale Suchdiagnose nicht als Deduktionsnachweis ausgeben.
- Schwierigkeit L1–L5, plausiblen Bereich, Methode, Vertrauen und Technik-/Engstellenbegründung; getrennt Bearbeitungsumfang und belastbare Zeitdaten oder „nicht geschätzt“.
- Nutzungsgrundlage, tatsächlichen Zieladapter-/Exportstatus, KI-Durchläufe und aktive Menschenzeit oder „nicht erfasst“.
- Offene Blocker und nächsten erlaubten Schritt. Vorhandene menschliche Spieldaten optional ergänzen; ihr Fehlen ist kein Blocker.

Keine Ergebnis- oder Freigabefelder ohne Beleg als erfüllt ausgeben. Inhaltsfreigabe, Katalogfähigkeit und tatsächliche Integration getrennt halten. Ein unpassender oder fehlender Exportadapter darf nicht durch Umwidmung bestehender Pilotdefinitionen ersetzt werden.

Bei einer Sichtung ohne freigabefähiges Angebot die echten Ansichten und Defizite
nach [Qualitätsvertrag §5](../PUZZLE_QUALITY.md) direkt im Chat zeigen; die
Sheet-Rasteroptionsliste bleibt leer. Redaktionell akzeptierte Abweichungen nach
[Qualitätsvertrag §6](../PUZZLE_QUALITY.md) bleiben im Bericht negativ
beziehungsweise als Warnung sichtbar und werden
separat als menschliche Entscheidung belegt, niemals als bestandener Test.

### Einheitliche Chatübergabe

Jede Phasenabschluss-, Korrektur-, Wiederaufnahme- oder Blockermeldung verwendet
genau diese Reihenfolge; kurze Arbeitsfortschrittsmeldungen benötigen keinen Datensatz:

1. **Ergebnis:** höchstens drei knappe Punkte zu Ergebnis, wesentlichen Änderungen
   und offenen Blockern. Die für die Freigabe nötigen echten Bilder und Datei-/PR-
   Links unmittelbar dabei zeigen; technische Details bleiben in den Paketbelegen.
2. **Sheet-Daten:** genau ein kopierbarer JSON-Block nach folgendem Format. Dieselben
   Bezeichnungen wie im Cheat-Sheet verwenden, alle Schlüssel ausgeben; unbekannte
   Werte sind `null`, nicht vorhandene Optionslisten `[]`. Keine Platzhalter oder
   erfundenen Hashes. Dies ist eine
   Bedienhilfe aus den bestehenden Dateien, kein zusätzlicher Nachweisvertrag und
   keine eigene Pflichtdatei im ZIP. Der Import erteilt keine Freigabe.
3. **Nächster Schritt:** denselben Auftragsnamen wie im JSON nennen und in einem
   Satz die noch erforderliche menschliche Auswahl/Freigabe oder Blockerbehebung.
   Ohne echten Stopp bereits autorisierte Arbeiten selbst fortsetzen.

Damit ist die Chatübergabe vollständig. Keine zusätzliche Handoff-Markdowndatei
und keinen weiteren kopierbaren Folgeauftrag ausgeben, auch nicht nach Auftrag 2.
Der Nutzer übernimmt die Sheet-Daten und erzeugt den gewählten Folgeauftrag im
Cheat-Sheet; dessen Kopier-/Exportfunktionen bleiben der reguläre Bedienweg.
Keine Modell-, Reasoning- oder Ausführungsempfehlung anfügen und keine dafür
veranlasste Modellrecherche durchführen (§1). Die technische Übergabe nach §6
und die menschlichen Freigaben werden dadurch nicht ersetzt oder verkürzt.

```json
{
  "format": "picross-cheatsheet-update-v2",
  "Motiv": null,
  "Rasterbreite": null,
  "Rasterhöhe": null,
  "Größenvorgabe": "Ungefähr",
  "Rätselmodus": "KI empfiehlt",
  "Farbanzahl": null,
  "Farbvorgabe": "Ungefähr",
  "Verwendete Farben": null,
  "Rätsel-ID": null,
  "Paketrevision": null,
  "Paketpfad": null,
  "Abschlussbild": null,
  "Abschlussbild-Optionen": [],
  "Rastervariante": null,
  "Raster-Optionen": [],
  "Motivvorlage": null,
  "Parameterkorridor": null,
  "Inventar-SHA-256": null,
  "Quellbranch / Commit": null,
  "PR": null,
  "Produktionsstatus": null,
  "Nächster Schritt": "1 · Abschlussbilder erzeugen"
}
```

`Größenvorgabe`: `Ungefähr|Fest`; `Rätselmodus`: `KI empfiehlt|Monochrom|Farbig`;
`Farbvorgabe`: `Ungefähr|Genau`. Maße und Farbzahlen sind Ganzzahlen oder `null`.
`Farbanzahl` bleibt der Nutzerwunsch, bei offener Vorgabe `null`; `Verwendete Farben`
wird erst an einer tatsächlichen Matrix gezählt. Konkrete Empfehlung/Istmaße und
Modus samt zulässigen Varianten stehen im `Parameterkorridor`; seine Bestätigung
folgt weiterhin der echten Motivfreigabe. Ohne Abschlussbildoptionen enthalten die
Bildfelder eindeutigen Pfad und Dateirevision; bei noch offener Auswahl `null`.
Mit Abschlussbildoptionen enthält `Abschlussbild` dagegen die ausgewählte
Options-ID oder `null`; das Sheet setzt daraus Dateipfad, ID und Hash ein. `Inventar-SHA-256` enthält nur
den 64-stelligen Hash des Originalinventars, keinen ZIP-, Matrix- oder Logikhash.
`Quellbranch / Commit` ist ein tatsächlich erreichbarer Paketstand, bevorzugt eine
volle Commit-SHA; ungesicherte lokale Arbeit als `null` plus Blocker berichten.
Der Paketstand ist vom Stand des zu lesenden Regelwerks zu unterscheiden.
Der PB-A-Builder leitet seine Sheet-Ausgabe aus demselben äußeren Record ab.
Ein erfolgreicher lokaler Bau oder Indexeintrag belegt noch keinen Git-Sicherungs-
commit; bis zur tatsächlichen Sicherung bleibt dieses Feld ausdrücklich `null`.
Sein `repo_commit` bindet ausschließlich den zuvor gelesenen Quellenstand.

`Nächster Schritt` verwendet genau einen dieser Namen: `1 · Abschlussbilder erzeugen`,
`2 · Bild freigeben & abstrahieren`, `3 · Motiv freigeben & produzieren`,
`4 · Abnehmen & ins Spiel integrieren`, `Korrigieren oder Fehler beheben`,
`Gespeicherte Arbeit fortsetzen`, `Merge freigeben` oder `Abgeschlossen`.
Nach bereits beauftragtem Integrationsmerge ist erst nach Abschnitt 9
`Abgeschlossen` zulässig. Dann auf den erhaltenen Integrationsdatensatz statt
auf gelöschte ZIPs verweisen, `Paketpfad` und entfernte Bild-/Parameterreferenzen
auf `null` setzen; Reveal und Runtime-Inhalte bleiben erreichbar.

### Optionslisten im Sheet-Format v2

Beide Optionslisten und ihre Auswahlfelder sind Pflicht; v1 bleibt im Cheat-Sheet als
Alteingang ohne Optionslisten lesbar. Jede Liste enthält höchstens 20 Einträge.
IDs sind innerhalb ihrer Liste eindeutig, höchstens 64 Zeichen lang und bestehen
aus Buchstaben, Ziffern, Bindestrich oder Unterstrich, beginnend mit einem
Buchstaben/einer Ziffer. Groß-/Kleinschreibung ist maßgeblich. Eine Auswahl muss
auf genau einen Eintrag zeigen. Unbekannte Felder oder unvollständige Einträge
werden vor einer Übernahme abgewiesen; keine stillschweigende erste Auswahl.

**Abschlussbild-Optionen:** Nach Auftrag 1 alle tatsächlich angebotenen Dateien
aufführen. Je Eintrag genau `ID`, `Beschreibung`, `Datei` und `SHA-256` ausgeben.
`Datei` ist der sichere paketrelative Pfad, `SHA-256` der berechnete Dateihash;
`Beschreibung` benennt den sichtbaren Unterschied und darf eine Empfehlung
kennzeichnen. Der gemeinsame Paket-/Quellstand steht in den bisherigen Feldern.
`Abschlussbild` bleibt bei neuer Auswahlvorlage `null`, auch bei Empfehlung oder
nur einer Option. Erst eine bereits tatsächlich getroffene menschliche Auswahl
darf als ID übernommen werden; sie ersetzt weiterhin keine Bildfreigabe.

**Raster-Optionen:** Nach Auftrag 3 alle freigabefähigen Angebote aus §4.5 mit
folgenden Feldern ausgeben. Sämtliche Felder sind Pflicht; nur `PR` darf `null`
sein. Keine beispielhaften Hashes oder nicht existierenden Pfade in echten Daten.
Sichtungsentwürfe bleiben außerhalb dieser Liste und werden nicht als
`content_ready` angeboten; ihre Ansicht erfolgt mit echten Links im Chat nach
[Qualitätsvertrag §5](../PUZZLE_QUALITY.md). Das v2-Format bleibt unverändert.

| Feld je Rasteroption | Bedeutung |
| --- | --- |
| `ID`, `Beschreibung` | Stabile Auswahlkennung, sichtbare Unterschiede/Empfehlung |
| `Rasterdatei` | Sicherer paketrelativer Pfad der echten Rasteransicht |
| `Kandidat` | Eindeutiger Bundle-/Variantbezug des einen Handoffkandidaten |
| `Schwierigkeit` | Gebundene Stufe, zum Beispiel `L3 – mittel`; Bericht im Paket |
| `Paketrevision`, `Paketpfad` | Eigene Revision und repositoryrelatives `content/authoring/<Rätsel-ID>/<Paketrevision>/package.zip` |
| `Inventar-SHA-256` | Berechneter 64-stelliger SHA-256 des zugehörigen Originalinventars |
| `Quellbranch / Commit`, `PR` | Tatsächlich zugänglicher Paketstand und gegebenenfalls dessen PR |
| `Rasterbreite`, `Rasterhöhe` | Tatsächliche ganzzahlige Maße 1–50 |
| `Rätselmodus`, `Verwendete Farben` | `Monochrom`/`Farbig`, tatsächliche Vordergrundfarbzahl 1–8; Mono genau 1 |
| `Abschlussbild`, `Motivvorlage`, `Parameterkorridor` | Konkrete Bild-/Dateirevisionen und für dieses Ergebnis geltende Motivfreigabe |

Alle Rasteroptionen gehören zur gemeinsamen `Rätsel-ID`; Paketpfade und
Revisionen dürfen nicht kollidieren. Angaben müssen zur Größen-/Farbvorgabe und
Motivfreigabe passen. Unterschiede zwischen Varianten sind nur innerhalb des
bereits freigegebenen Korridors erlaubt. Die KI bestätigt dies anhand der
Paketquellen; die Formularvalidierung ersetzt diese Prüfung nicht.
`Rastervariante` ist die menschlich ausgewählte ID oder `null`, niemals die
bloße Empfehlung. Bei neuen Rasterangeboten bleiben die variantenspezifischen
Kopffelder (`Paketrevision`, `Paketpfad`, `Inventar-SHA-256`, `Quellbranch / Commit`,
`PR`, Maße/Modus/Istfarbzahl und Bild-/Parameterbezüge) ohne ausdrückliche Auswahl
`null`; die jeweiligen Werte stehen vollständig in jeder Option. Nutzerwünsche
und Motivgrenzen stehen zusätzlich im Auftrag/Briefing; die Optionsmaße sind Istwerte.
Bei bereits getroffener Auswahl müssen diese Kopffelder exakt zur Option passen.

Abschlussbild- und Rasteroptionslisten dürfen nicht gleichzeitig befüllt sein.
Nach Abschlussbildfreigabe wird nur deren konkrete Datei weitergegeben; der
spätere Rasterdialog bietet keinen unbemerkten Wechsel des freigegebenen Bildes.
Bei neuen Bildfassungen gelten unverändert die Rücksprünge/Freigaben aus §4.4.

Das Sheet zeigt die Auswahl mit Beschreibung und Dateireferenz. Wechsel eines
Rasters übernimmt alle zugehörigen Bindungen gemeinsam; Einzelbearbeitung dieser
Felder ist bei Optionslisten gesperrt. Solange keine Auswahl getroffen wurde,
sind die davon abhängigen Freigabeaufträge gesperrt. Auftrag 2 nennt Datei, ID
und Hash; Auftrag 4 nennt Raster-ID/Kandidat/Ansicht und das passende Paket samt
Inventarhash. Import, Dropdownwechsel, Sitzung und ZIP-Export erteilen keine
Freigabe und ändern kein Repository. Erst das tatsächliche Absenden des passenden
Freigabeauftrags ist eine menschliche Erklärung.

Sitzungen v3/v4 und Auftragsexporte erhalten Listen und Auswahl. Import eines alten
v1-Blocks/Records oder einer alten Sitzung entfernt nur im ausdrücklich gewählten
Zieljob vorherige neue Options-/Hintergrunddaten nach dessen Altvertrag; die
Joboptionen bleiben erhalten. Reset leert nur den aktiven Job. Fehlerhafte Daten
dürfen keinen Teilstand übernehmen.
Die HTML-Datei bleibt offline ohne automatische Bild-/Repositoryabrufe. Bilder
stehen im Chat beziehungsweise Paket; Pfade im Dropdown sind keine Behauptung,
dass das Sheet die Bytes oder Proofs selbst geprüft hätte. Nach Produktionsabschluss
werden Optionslisten geleert, statt auf entfernte Arbeitsdateien zu verweisen.

Bei Pflege des Cheat-Sheets beide eingebetteten Regelwerksnapshots und ihre
Versions-/Revisionsanzeigen bytegleich mit den jeweiligen Markdownquellen halten:
0.6.0/docrev48 und 0.7.0/docrev9. Jeder Auftrag verwendet den zum Job passenden Stand.
Der Regelwerk-Stand ist unabhängig vom Paketstand; ein noch nicht gemergter Workflow
muss über den tatsächlichen Arbeitsbranch/Commit erreichbar benannt werden.

### Mehrere unabhängige Produktionsjobs

MJ-A führt eine geordnete Sammlung mit stabilen lokalen Jobkennungen, auch vor
Vergabe einer Rätsel-ID. Die Übersicht zeigt Motiv, Rätsel-ID, Produktionsstatus,
nächsten Schritt und Hintergrundstatus getrennt. Blocker stammen ausschließlich
aus einem passend gebundenen importierten Record; andernfalls steht dort
„nicht mitgeliefert“. Die Anzeige erfindet keine technische Prüfung oder Freigabe.

Vor jedem Jobwechsel den aktuellen Formularstand im Arbeitsspeicher sichern.
„Neuer Job“ beginnt mit persönlichen Voreinstellungen; Reset und Entfernen
betreffen ausschließlich den gewählten Job. Jobs werden nicht automatisch dauerhaft
gespeichert. Einzelne Sitzungen bleiben nutzbar, die vollständige manuelle Sicherung
verwendet `picross-cheatsheet-workspace-v2` (v1 bleibt für reguläre Jobs lesbar) nach
[Hintergrundvertrag §7.5](../PUZZLE_BACKGROUNDS.md#75-mj-a-mehrjob-arbeitsbereich-und-sichere-übernahme).
Sie erhält Reihenfolge, aktiven Job, Sitzungen, Joboptionen und passende Records.
Der Sammlungsimport ersetzt nach ausdrücklicher Vorschau die ganze Sammlung;
Abbrechen oder fehlerhafte Daten ändern keinen Job.

Vor Einzelimporten vorhandenen Zieljob oder neuen Job ausdrücklich bestimmen.
Die Vorschau zeigt Ziel, Rätsel-ID, Revision, ersetzte Daten und relevante
Joboptionen. Eine bisher leere Rätsel-ID darf eine noch freie ID erhalten;
unterschiedliche nichtleere Rätsel-IDs werden nicht vermischt. Neue Revisionen
ersetzen nur nach ausdrücklicher Bestätigung den gewählten Job. Hintergrundbindungen
und Paketvarianten werden gemeinsam übernommen. Eine Änderung maßgeblicher
Bindungen verwirft den dazu nicht mehr passenden Anzeige-Record.

Nach §9 bleiben der tatsächliche Integrationscommit und kompakte Abschlussbezüge
sichtbar. Bereinigte Paket-ZIPs, Arbeitsbilder oder Proofs werden weder als verfügbar
angeboten noch rekonstruiert. Der Arbeitsbereich bleibt offline: keine automatischen
Bild-/Repositoryabrufe, Batchaufträge oder Modell-API.

### Persönliche Einstellungen und lokale Codex-Arbeit

Das Offline-Sheet trennt persönliche Globals, Voreinstellungen und Jobdaten.
Arbeitswurzel (`workspaceRoot`), Bereinigungsoption (`cleanupMode`) und Farbschema
(`theme`) gelten persönlich für alle Jobs. `repoSave`, `mergeMode`, `ruleSource`,
`rulePath` und `ruleRef` gehören zum einzelnen Job; neue Jobs erhalten dafür die
persönlichen Voreinstellungen. Jobwechsel, Jobbearbeitung und Produktionsimporte
ändern diese Voreinstellungen nicht. Keine fremde Arbeitswurzel oder
Bereinigungsbefugnis aus Sitzungen, Records oder Sammlungen übernehmen.

Persönliche Einstellungen können im Browser gespeichert werden. Ein anderer Browser,
ein geänderter Dateipfad oder gelöschte Browserdaten können einen Einstellungsimport
erfordern. Fehlender oder gesperrter Browserspeicher wird sichtbar gemeldet; das
Sheet bleibt mit manueller Eingabe und Sicherung nutzbar. Produktionsdaten und
Bildbytes werden nicht automatisch dauerhaft gespeichert.

Die gesonderte Sicherung `picross-cheatsheet-settings-v1` enthält genau `format`,
`settings` und `theme`. `settings` enthält genau die Zeichenketten `workspaceRoot`,
`cleanupMode` (`on|off`), `ruleSource` (`repo|attachment`), `rulePath`, `ruleRef`,
`repoSave` (`repo|local`) und `mergeMode` (`merge|draft`); `theme` ist
`system|light|dark`. Eine leere Arbeitswurzel bezeichnet noch fehlendes Setup.
Nichtleere Wurzeln müssen absolute Windows-, UNC- oder POSIX-Verzeichnispfade
ohne Steuerzeichen oder Punkt-/Elternsegmente sein. Vor einem Einstellungsimport
alle Werte prüfen und die neue Wurzel samt Freigabeoptionen ausdrücklich zur
Bestätigung zeigen; kein Teilimport bei ungültigen Daten.

Neue Jobs verwenden standardmäßig `picross-cheatsheet-session-v4`: dieselbe
äußere Hülle wie v3, aber `fields` enthält ausschließlich Rätseldaten. Alte Sitzungen
v1–v3 bleiben ladbar und werden ohne Wechsel ihrer Fachsemantik nach v4 normalisiert;
ihre früheren persönlichen Einstellungen und Ablage-/Mergeoptionen werden nicht
übernommen. Im Zieljob bleiben die vorhandenen Joboptionen erhalten. Bewusste Wahl
des Hintergrundwegs oder sichtbarer Import v3/v5 aktiviert den 0.7.0-/v5-Weg.
Ein Konflikt zwischen gewähltem Weg und erhaltenem Regelpfad sperrt Prompt und
ZIP, bis der Nutzer einen kompatiblen Stand ausdrücklich wählt; das gilt auch für
einen Alteingang mit erhaltenem 0.7.0-Pfad. Kein stiller Regelwechsel.
Eine Sitzung ist weder Einstellungsbackup noch Produktionspaket oder Freigabe.

Auftragsexporte verwenden `picross-authoring-request-v3`; zusätzlich zu den
bisherigen Metadaten, Rätseldaten, Varianten und Bildbezügen enthält `execution`
die tatsächliche `surface`, `local_workspace_root` (Zeichenkette oder `null`) und
`cleanup_own_local_work` (Boolean). Die Freigabe ergibt sich weiterhin allein aus
dem ausdrücklich abgesendeten Auftrag, nicht aus importierten Ergebnisdaten.
Der 0.7.0-Weg verwendet Auftrag v4 mit `background` nach §7.3 des
Hintergrundvertrags. Alte Produktionsformate und Updates v1/v2 bleiben unverändert.

Jeder Prompt verlangt aktuelle `AGENTS.md` und Pflichtquellen sowie
[WORKSPACE](../dev-rules/WORKSPACE.md). Standardregelstand ist `main`, ein bewusst
beauftragter Arbeitsbranch kann eingestellt werden. Der Anhang ist ein datierter
Snapshot; bei widersprüchlichem Stand vor dem betroffenen Schritt klären, keine
alten Regeln stillschweigend vorziehen. Das Sheet selbst ruft keine Quellen ab.

Codex-Aufträge (3, 4, Merge sowie technische Korrektur/Wiederaufnahme) benötigen
eine gültige absolute Arbeitswurzel; sonst bleiben Kopieren und ZIP-Export
gesperrt. Neue eigene Checkouts, Worktrees, Downloads und temporäre Prozessdaten
gehören in einen eigenen Auftragsunterordner darunter. Ist die Wurzel in der
ausführenden Umgebung nicht erreichbar oder liegt ein benötigter bestehender
Checkout außerhalb, den Konflikt vor der betroffenen Dateiarbeit melden; keinen
Ausweichpfad wählen und keine fremden Daten verschieben oder löschen.
Die Bildschritte in ChatGPT Work bleiben ohne lokale Codex-Wurzel ausführbar;
deren Cloud-Arbeitsablage macht einen Windows-Pfad nicht zugänglich. Das Sheet
übermittelt eine Arbeitsanweisung, setzt keine Dateisystemsandbox und verändert
keine Zugriffsrechte.

Die standardmäßig aktive lokale Bereinigungsoption beauftragt die Entfernung
eigener gesicherter entbehrlicher Arbeitsdaten gemäß WORKSPACE. Noch benötigte
Produktions-/Freigabe-/Reviewdateien, Benutzerdaten, Benutzercheckout und die
Arbeitswurzel selbst bleiben erhalten. Restpfade und Gründe im Ergebnis nennen.
Diese Option ist vom Produktionsabschluss nach §9 getrennt; auch ausgeschaltete
lokale Bereinigung hebt den dort beauftragten Nachintegrationsabschluss nicht auf.
Reine Rätselproduktion bleibt gemäß §1 ohne Player-Build und ohne eigene CI-Replays.

### Ausdrücklich gewählter Hintergrundweg: verlustfreier Transport

Die drei Teile Ergebnis, Sheet-Daten und nächster Schritt bleiben erhalten.
Die obigen v2-Beispiele gelten für den 0.6.0-Weg. Hintergrundtragende Daten verwenden
Update v3, Sitzung v5 und Auftrag v4 nach
[PUZZLE_BACKGROUNDS §§7.3–7.5](../PUZZLE_BACKGROUNDS.md).
Keine Hintergrunddaten in Freitext oder scheinbar kompatiblen v1-Records/v2-Updates
verstecken. Ein vollständiges Update v3 ist unmittelbar ladbar; Record v2 erfordert
seine tatsächliche passende v3-Projektion aus Builder oder Finalizer. Der Import
prüft beide zusammen atomar und erfindet keine Manifest-, Status- oder Optionsdaten.

Nach Auftrag 2 drei tatsächliche Hintergrunddateien gemeinsam mit der Motivvorlage
isoliert zeigen, jeweils mit stabiler Kennung und Revision. Das Sheet führt kompakte
Datei-/Hashreferenzen und die ausdrückliche Auswahlabsicht; der eigene Bildanhang für
Abschlussbild, Motivvorlage oder Raster bleibt davon getrennt. Unbekannt, offen,
abgelehnt und tatsächlich `none` sind verschiedene Zustände. Ohne ausdrückliche
Wahl keinen ersten Kandidaten und keine Leerentscheidung einsetzen.

Im Ergebnis Hintergrundstatus, tatsächliche Entscheidung oder offene Wahl,
technische Ableitungsbefunde und visuelles Urteil getrennt nennen. Eine frühe
bewusste Leerabsicht nennt im abgesendeten Auftrag den Verzicht auf die drei
Hintergrundkandidaten. Eine spätere offene Wahl kann im selben Auftrag wie die
Endabnahme gebunden werden; der Auftrag nennt das konkrete Rasterpaket und die
gewählte Bildfassung beziehungsweise ausdrückliche Leerentscheidung. Eine bereits
gültige unveränderte Entscheidung braucht keine zweite Routinebestätigung.
Technische Prüfung, Endabnahme und Integrationsauftrag bleiben erforderlich;
Kandidaten werden nicht zur Auswahl ins Buch integriert.

### MJ-B: Hintergrundrevision im Offline-Sheet

Der eigene Bedienweg nach [Hintergrundvertrag §7.6](../PUZZLE_BACKGROUNDS.md#76-mj-b-eigenständige-hintergrundrevision-im-sheet)
führt Entwurf, Originalrequest und gemeldeten Abschluss getrennt von Rasterjobs.
Die geschlossene Sitzung `picross-background-adoption-session-v1` enthält exakt
`format,fields,request_text,completion`; Felder, Grenzen und Querverbindungen
sind vollständig in §7.6 D02/D06 festgelegt. Sammlung v2 erlaubt beide Familien,
v1 ausschließlich reguläre Jobs. Globale eindeutige Rätsel-ID bleibt erforderlich.
Jobfamilienwechsel ist ein ausdrücklich bestätigter vollständiger Ersatz; vorher
Sitzung oder Sammlung sichern. Andere Jobs und persönliche Defaults bleiben erhalten.

„Neuer Hintergrundwechsel“ wählt für diesen Job sichtbar den 0.7-Previewpfad.
Originalrequest aus Datei oder exakt erhaltenem JSON-Text prüfen, Vorschau bewusst
übernehmen oder verwerfen. Request/target/background/authorization bleiben
schreibgeschützt. Das Sheet prüft Form, kanonische Originalbytes und innere Refs,
keine Payloaddateien, Rechte, Source, Capability oder aktuelle Zielbereitschaft.
`test_only` bleibt sichtbar. Neue materielle Wünsche sperren die Adoption alter
Bytes; identischer Reimport hebt sie nicht auf. Rücknahme erfolgt ausdrücklich.

Die eigenen Schritte `prepare,rework,resume,adopt,complete` folgen §7.6 D04.
Bild-/Auswahlaufträge laufen in ChatGPT Work; technische Aufträge benötigen eine
gültige Codex-Arbeitswurzel. Fehlende Mindestangaben sperren adopt/complete.
Ergebnis nennt tatsächliche Dateien/PR, Stand und nächsten Schritt; ein echter
Request wird unverändert als record.json geliefert. Kein Raster-Sheet-Update
oder konkurrierendes Ergebnisformat für diese Familie erzwingen.

Auftragsexport `picross-background-adoption-sheet-request-v1` und ZIP folgen D05:
Originaltext bytegleich als original-request.json, Prompt, brief.json, Dateiinventar
und bei Anhang genau der 0.7-Snapshot. Referenzierte Payloaddateien werden nicht
mitgeliefert; die vollständige Arbeitsrevision muss am ausdrücklich genannten
Quellstand oder separat erreichbar sein. Kein Dummy-ZIP oder Buchtesteinbau.

„Abschluss melden“ benötigt vollständigen gemeldeten Maincommit und konkreten
HTTPS-Berichtslink. Es leitet nur die kompakte historische Bindung aus dem
Originalrequest ab, leert dessen vollständige Arbeitsliste sowie Briefing/Wunsch
und behauptet keine selbst geprüfte Mainintegration. Revisionsgenaues Retirement
bleibt Aufgabe des vorhandenen HP-I1b2-/§9-Wegs. Neue Arbeit erfordert ausdrücklich
einen neuen Entwurf/Arbeitsstand; alte historische Quellen sind keine heutige Source.

## 8. Abgenommenes Paket ins Spiel integrieren

### BA-B: mehrere vorbereitete Einzelintegrationen

Bei ausdrücklichem Integrationsauftrag darf der getrennte
[BA-B-Runner](../PRODUCTION_BATCH.md) vollständig vorbereitete Jobs seriell
übernehmen. `register` verwendet Originalpaket, tatsächliche Endfreigabe und
sämtliche benötigten äußeren Belege über `export → frischer plan → register`.
Ein vorheriger Finalizerlauf oder zusätzlicher Repository-Store ist keine neue
Voraussetzung für bereits passende lokale Eingänge. `background_adopt` verwendet
den vollständigen unveränderten HP-I1b2-Request samt Arbeitsdateien über
`store → frischer plan → adopt`. Der Hintergrundweg bleibt ausdrücklich opt-in;
keine Bildwahl, Endabnahme oder neue Autorisierung aus einem Batchflag ableiten.

Plan, exakte Eingangs-/Auftragsbytes, Phasenbudgets und Versuche bleiben gebunden.
`validate` prüft lesend die Vorbereitung, `run` führt aus, `resume` prüft frisch,
`status` zeigt ausschließlich den historischen Stand mit `fresh=false`.
[CLI und API](../../tools/puzzle_production/README.md#ba-b-autorisierte-serielle-einzelintegration)
verlangen ausdrücklich benannte Quellen-, Werkzeug-, Ziel- und Arbeitswurzeln.
Bei der Wiederaufnahme sind drei Fälle getrennt:

| Belegter Stand | Zulässige frische Prüfung |
| --- | --- |
| Registrierung publiziert, Batchabschluss noch ungebucht | Lesendes natives `registration(apply=False)` muss den vollständig eigenen No-op bestätigen; kein zweiter Writer. |
| Bildadoption publiziert, Batchabschluss noch ungebucht | Ursprüngliches Planbundle mit nativem `adopt(..., no_op_only=True)` vollständig prüfen; jeder erforderliche Schreibschritt bleibt gesperrt. |
| Erfolg gebucht, danach weitere Jobs erfolgreich | Heutigen Gesamtkatalog einmal vollständig prüfen und erreichte Jobbindungen abgleichen; den inzwischen stale Bildplan nicht erneut adoptieren. |

Der erste ungeklärte Fehler, offene Journal-/Stagingrest oder unsichere
Abschluss stoppt alle folgenden Jobs; erfolgreiche frühere Übernahmen bleiben.
Nötige native Recovery gesondert im bestehenden autorisierten Weg ausführen,
danach frisch wiederaufnehmen. Kein automatischer Retry, Batchrollback oder
Nachfüllen verbrauchter Versuche. RI-/Authoring-/Bildbudgets bleiben getrennt;
ein Batch erzeugt weder Solver-/Difficultyarbeit noch zusätzliche Routineprüfungen.

`completed` bestätigt den aktuell geprüften Zielcheckout. Originalfalse-Felder
und historische Freigaben werden nicht umgeschrieben. Arbeitsrecord, Diffprüfung,
Commit/Push/Draft-PR, CI und gegebenenfalls autorisierter Merge folgen weiter
diesem §8; der Main-gebundene Abschluss folgt §9. Der Runner selbst führt weder
Gitaktionen noch Retirement oder Raster-/Revealupdates aus.

**Zukünftiger Hintergrundweg:** Die nachstehende ausführbare 0.6.0-/ZA-1-Route
wird durch diesen Solltext nicht um neue Eingangsfelder oder Befehle erweitert.
Der separate opt-in HP-I1a-Weg nach dem 0.7.0-Vorschausnapshot liefert äußere
Endabnahme und prüfbaren Export v6; dessen gespeicherte `integration_ready`,
`catalog_ready` und `registered` bleiben false. HP-I1b1 führt die anschließende
frische zielbezogene Prüfung, erste Registrierung und deren Abschluss ein.
`game/data/background-capability.json` ist die echte Zielfähigkeit;
fehlende/false-Capability sperrt Hintergrundplanung/-registrierung vor Mutation.
Nur HP-I2 mit tatsächlicher Runtime und technischer Abnahme erlaubt true.
Synthetische kompatible Ziele sind keine Spieler-/Produktionsabnahme.
Ein Capabilitywechsel macht ältere daran gebundene Pläne stale und schaltet
offene Altjournale nicht frei; deren Sperren und regulären Recoveryweg erhalten.
0.6.0 bleibt Default, der gesonderte 0.7.0-Weg opt-in. Die verpflichtende
Gesamtaktivierung wird anhand des konkreten Einzelwegs in #560 abgeglichen,
nicht allein aus der Runtimefähigkeit oder pauschal aus dem Abschluss von #490.
Erst der tatsächlich unterstützte #561-Weg übernimmt in Auftrag 4 gemeinsam mit
dem endabgenommenen Rätsel **ausschließlich die konkret gewählte, gültig
abgeleitete Auslieferungsdatei oder die ausdrücklich erklärte Leerentscheidung**.
Vorher müssen technische Rasterreife, vollständige Hintergrundbereitschaft,
echte Endabnahme und Integrationsbefugnis gemäß
[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) belegt sein. Eine Auswahlvorlage
oder gesicherte frühe Bildarbeit ist keine Integrationsberechtigung.

Nur die gewählte Datei ableiten/integrieren; keine Kandidatenprobe im Spiel und
keine zusätzliche Buchabnahme. Bewusst leer braucht keine Runtime-Nulltextur.
Die finale Prüfung bindet unverändertes Originalpaket, tatsächliche externe
Auswahl/Endabnahme und gültige Ableitung. Herkunft, Palette, Paarprofil,
Schwierigkeit, bisherige Reveal-/Motivgates und Recoverygarantien bleiben
erhalten. Eine spätere reine Hintergrundersetzung nutzt nur den dafür
eingeführten Bildweg aus #561 und erhält Lösungs-/Saveidentität; sie ist keine
`plan-update`-/`update`- oder `catalog_reveal`-Operation. Rasterupdate und
Revealadoption vorhandener Hintergrundziele verwenden die geschlossenen
HP-I1c-Bindungen nach Hintergrundvertrag §12; keine ungeprüfte Übernahme einer
alten Bild-/Kontextfreigabe. Legacy-Erstnachrüstung bleibt gesperrt.

RI-A-V01 zu [#478](https://github.com/venomenon328/picross/issues/478) liefert
seit PR #484 auf main die [operativen CLI-/API-Grenzen](../ZA1_ADAPTER.md#ri--zeitbudget-und-diagnose-neuer-registrierungen).
Neue Registrierung: `register --publication-seconds S --recovery-seconds S`,
jeweils Default 1800 s; Warnung einmal ab 300 s. Ausdrückliche
`recover-registration --recovery-seconds S` verwendet den eigenständigen
Registrierungsrahmen nur nach sicherer Journalzuordnung. Andere Operationen
behalten ihre bisherigen Grenzen. `export`/`plan` erhalten keine neuen
mutierenden Budgetoptionen. Positive endliche Werte vor dem Lauf festlegen;
bei Fristablauf Diagnose und Journalzustand prüfen, keinen Lock manuell entfernen.
Die vier Befehle liefern `operation_diagnostics` im einzelnen JSON-Ergebnis
und optional `--operation-report <neue-externe-datei>`; Fortschritt steht auf
stderr. Phasenzeiten sind inklusive und nicht zu summieren. Der getrennte
[RI-A-T01-Nachweis](../RI_A_VERIFICATION.md) benennt reale Messungen und offene
Abnahmen; eine längere Schutzfrist beweist weder Beschleunigung noch Integration.

RI-B-V01 zu [#479](https://github.com/venomenon328/picross/issues/479) ergänzt
auf seinem Arbeitsbranch die rein interne Wiederverwendung tatsächlich geprüfter
neuer Paketbytes innerhalb eines mutierenden `register`-Aufrufs. Eingangsprüfung
und unabhängiger Staging-Replay bleiben vollständig; spätere Paketnachprüfungen
kontrollieren frisch Inventar, Bytes und Bindungen. Getrennte CLI-Aufrufe teilen
keinen Prüfbeweis. Der Ablauf `export → plan → register`, tatsächliche Freigaben,
lesender Plan und ausdrückliche Registrierungsautorisierung bleiben erhalten.
Kein neuer Schalter, persistenter Prüfcache oder zusätzlicher Freigabeschritt.
Durch B bleiben globale Guards und Recovery unverändert; Recovery prüft ohne
B-Kontext. [RI-B-T01](../RI_B_VERIFICATION.md) nennt seine gebundenen Nachweise und
offene Gates; die Branchlieferung ist keine Merge- oder Inhaltsfreigabe.

RI-C-F01 / RI-C-V01 zu [#480](https://github.com/venomenon328/picross/issues/480)
ordnet ausschließlich bei mutierender Erstregistrierung v6 und ihrer Recovery
die vollständigen Quellenprüfungen festen Phasengrenzen zu; unmittelbar betroffene
Ziele, Journal, Eltern und Temps werden zusätzlich frisch lokal geprüft.
Runtime bleibt letztes Datenziel. Fremde unbeteiligte Quellen werden spätestens
an der nächsten vollständigen Grenze erkannt, unsicherer Rollback erhält das
Journal. [SD-Catalog](../SD_CATALOG.md#ri-c--phasengrenzen-für-erstregistrierung-v6)
führt die genaue Erkennungs-/Recoverygarantie, [RI-C-T01](../RI_C_VERIFICATION.md)
die Nachweise. Auftragsfolge, Freigaben, CLI und Budgets bleiben unverändert;
kein neuer Produktionsfreigabeschritt und keine pauschale Laufzeitzusage.

Voraussetzungen: tatsächlicher Integrationsauftrag, unverändertes `content_ready`-Paket mit vollständigen Inhaltsgates und gesonderte menschliche Endfreigabe nach [ZA-1](../ZA1_ADAPTER.md). Die Freigabe bindet Originalhandoff, Inventar, Endkandidat, Matrix-/Logikhash und Abschlussbild; ein `pass`-Flag genügt nicht. Die Archivablage selbst erteilt keine Endabnahme. Probespielen bleibt optional.

Dieser reguläre Export-/Registrierungsablauf wird durch
[AT](../REVEAL_TRANSPARENCY.md) nicht zu einem Bildersatzbefehl. Bestandsbilder
werden erst nach AT-A über dessen zusätzlichen eng begrenzten Bildupdateweg
übernommen; `plan-update`/`update` bleiben Rasterersatz. Neue Bildfreigaben und
aktive Bildhashes werden dabei außerhalb der unveränderten Altbelege geführt,
ohne Definitions-/Save-Revisionserhöhung. Der gemeinsame Quellen-/Recoveryweg
muss auch bei späterer Registrierung oder Rasterarbeit eine bestehende aktive
freigegebene Bildfassung erhalten und prüfen.

Der integrierte AT-A-P01-Stand schließt die exakten
[Quellen-/Freigabeverträge](../ZA1_ADAPTER.md),
[Folgeoperationen](../CATEGORIES.md), [Journale/Recovery](../SD_CATALOG.md) und
[CLI](../../tools/puzzle_production/README.md).
Die neue tatsächliche Bildfreigabe bindet ID, Bildrevision, damalige Definition,
Vorgänger-/Neubildhash, vollständige Zielnotice, Akteur, UTC und Erklärung samt
Bildannahme, Motiv-/Rasterkonsistenz und Endabnahme. Herkunft/Nutzungsgrundlage
und alle bisherigen Noticebytes bleiben erhalten; nötige Attribution wird
angehängt. Kein erfundenes Freigabeprotokoll und kein Ersatz durch die
Spezifikationsfreigabe. Materielle Änderungen folgen weiter Abschnitt 4.4.
Der eigene `catalog_reveal plan/adopt`-Weg gehört zur ausschließlichen
[AT-A-Umsetzung](../AT_A_VERIFICATION.md), die nach qualifiziertem AT-A-R01
über PR #263 integriert ist; historische Nachweise bleiben dort gebunden.
AT-B-V01 endete vor Plan/Adopt. Die anschließende tatsächliche Eigentümerabnahme
und der AT-B-F01-Übernahmeauftrag erlauben jetzt diese weiteren AT-B-Schritte.

Ab SD-C1 zusätzlich den nach §5.2 vollständig geprüften 0.3-Input übernehmen
beziehungsweise passend neu binden. Die aktuelle
Paket-/Exportbindung wird dadurch nicht rückwirkend geändert.

Paarprofilpakete verlangen mindestens Regelwerksbindung 0.5.0, neu 0.6.0, passende
`candidate.certification` und Schwierigkeit 0.2 mit den gebundenen Nachweisen.
ZA-1 erzeugt dafür `picross-target-inspection-v4` und `picross-target-export-v4`.
Unter 0.6.0 verwendet auch dieser Weg ausschließlich Inspektion/Export v5 samt
Palettengate. Diese Exportversion ist von menschlichen Änderungsautorisierungen
zu unterscheiden; sie erteilt selbst keine Ausnahme oder Freigabe.

Manuelle Ableitungen benötigen den passenden externen ZA-1-Autorisierungsvertrag
(v1–v6) und die tatsächliche Erklärung für die konkrete Auswahl. Originalhandoff,
Inventar und ursprüngliche Freigaben unverändert lassen; feste Edits, Schutzmasken,
Herkunft und Endproof frisch prüfen. Historische `blocked`-/`raster_review`-Eingänge,
späte Motivannahme oder eine Randregel-Ausnahme sind ausschließlich unter den
jeweils ausdrücklich zugelassenen Bedingungen aus [ZA-1](../ZA1_ADAPTER.md) möglich.
Keine pauschale Ausnahme aus einem manuellen Quelltyp oder einem neuen Solver ableiten.

ZA-1-v5 erlaubt bei einer bereits freigegebenen Motivvorlage eine ausdrücklich
autorisierte feste Farbkorrektur aus einem unabhängig bestätigten ursprünglichen
`stalled`-Direktimport. Das vollständige Endzertifikat bleibt Pflicht. Die
Originalbasis wird nicht als vollständig gelöst umetikettiert; v1–v4 behalten
ihre bisherigen Anforderungen. Ein neuer Metadatenstand kann die tatsächliche
Endabnahme aufnehmen, ohne versiegelte frühere Originale zu verändern.

ZA-1-v6 ergänzt die ausdrücklich nachträglich angenommene monochrome
Pixelvorlage eines manuellen Neuentwurfs. Der separate Eigentümerauftrag bindet
Originalpaket, konkrete Motivdatei, vorgeschlagene Parameter und Endabnahme.
Historische Revealbelege werden nur über ihren geprüften Ablagepräfix aufgelöst;
ihre Originalbytes bleiben erhalten. Vollständiger RP-3-Pixelimport und
unabhängiger Endproof sind Pflicht, alle anderen Inhaltsgates und die Randregel
bleiben bestehen. Keine Umdeutung zu einem Import aus einer älteren Motivdatei.

Codex MUSS den aktuellen Entwicklungsworkflow und ZA-1 vollständig lesen und dann:

1. Paket über `content/authoring/index.json` laden; ZIP-, Handoff-, Inventar- und Freigabebindung kontrollieren. Aktuellen `main` und vorhandene Arbeit prüfen, isolierten Arbeitsbranch verwenden. Keine fremden Änderungen aufnehmen.
2. Vorliegende Produktionsbelege und echte Endfreigabe zuordnen. Kein zusätzliches routinemäßiges `inspect`: Der nachfolgende `export` prüft Eingang/Freigabe frisch und verifiziert seine geschriebenen Ausgaben selbst. Nur `technical=true` und `editorial_approved=true` erlauben den Export; Fehler stoppen. `inspect` separat nur zur Diagnose einer konkreten Lücke. Aktuelle Ergebnisse außen führen, versiegelte Originale nicht ändern.
3. Produktions-ID unverändert als Runtime-ID verwenden. Motivname, kollisionsfreien Dateistamm/Save-Slot und numerische Runtime-Revision explizit wählen; bei neuen IDs gewöhnlich Revision 1. F01…F09 nicht umwidmen. ZA-1 unterstützt 1…50 pro Achse, Rechtecke, Mono und höchstens acht Vordergrundfarben; Paketrevision und Runtime-Revision bleiben getrennt.
4. Kategorie-ID im äußeren Record und in der aktuellen Kategorienquelle abgleichen. `export` mit Paket, Endfreigabe, Name, Runtime-Revision, Stem, Slot sowie `--category-id <id> --categories content/categories.json` in ein neues temporäres Ziel ausführen. Erfolgsbericht und `inspection.json` binden; kein zusätzlicher Routineaufruf von `verify-export`. Ein bereits passend gebundener kategorisierter Export darf direkt dem Plan dienen. Kategorienlose Altexporte neu kategorisiert exportieren. Autorisierte manuelle Ableitungen benötigen weiterhin den gesonderten ZA-1-Vertrag samt tatsächlicher Autorisierung. Neue 0.6.0-Pakete verwenden ausschließlich Export v5, bei Bedarf zusätzlich mit manueller Autorisierung und Paarnachweis. Historische Linienprofile verwenden v2/v3, Paarprofile v4. Keine automatische Ausnahme und keine manuelle Änderung der Exportversion. Das freigegebene Abschlussbild bleibt der bytegebundene Reveal. Matrix, Hinweise und Assets nicht manuell umschreiben.
5. `plan --export <export> --checkout <arbeitscheckout> --difficulty <checked.json>` ausführen, Kategorie-ID/aktuellen Anzeigenamen, konkrete Add-/Replace-Pfade und Registryänderungen auf Scope, Kollisionen und unveränderte Bestandsinhalte prüfen. Der Integrationsauftrag erlaubt anschließend `register` mit denselben Eingängen; keine zusätzliche routinemäßige Bestätigung verlangen. Ohne Auftrag beim Plan stoppen. Kein handgeschriebener Registryeintrag als Ersatz.
   Bei ausdrücklich beauftragtem Ersatz einer bestehenden Fassung stattdessen
   `plan-update` → `update` mit demselben Erwartungshash der bisherigen Definition
   und `--difficulty <checked.json>` nach [ZA-1](../ZA1_ADAPTER.md) verwenden.
   Nur bei gleicher ID/Logik/Matrix ist `--rebind-difficulty` ohne Analyse zulässig.
   Höhere Runtime-Revision, neue Paketrevision;
   feste Identität/Slot/Kategorie und Revealbytes erhalten. Alte Saves bleiben
   unberührt und gelten bei anderer Runtime-Revision als inkompatibel.
6. Tatsächliche Definition/Reveal/Nutzungshinweise, `content/registry.json`, deren Runtime-Projektion und die Prüfkopie unter `content/packages/…` kontrollieren, einschließlich Kategorienprojektion und eindeutiger Zuordnung im Katalog. Identischer Wiederholungsaufruf darf `no-op` sein; Konflikte nicht überschreiben. Bei offenem Registrierungsjournal nur den dokumentierten Recoverypfad verwenden.
7. **Für reine Rätselinhalte genügt die Adapter-/Dateiprüfung aus 4–6.** Keine obligatorischen Godot-Spielstarts, Teilstand-/Neustart-, Undo-/Save-, Abschluss-/Album-, Render- oder Windows-/PCK-Funktionsproben je Rätsel; keinen zusätzlichen Product-Harness oder manuellen Buildauftrag automatisch starten. Auch im allgemeinen PR-/Main-Kern bleibt reine Rätselproduktion ohne Player-Build. Die visuelle Raster-/Abschlussbildprüfung gehört bereits zur Produktion. Nur bei konkretem Befund eine gezielte zusätzliche Probe mit benanntem Zweck ausführen, isoliert von echten Saves. Allgemeine Spiel-/Exportregressionen gehören zu relevanten Codeänderungen. Keine zusätzlich manuell gestarteten Bestands-Replays, `check-registry`-/`sync-runtime`-Vollprüfungen oder wiederholten `register`-Aufrufe zur Bestätigung; interne Adapterprüfungen unverändert lassen. Nicht ausgeführte native Prüfungen als `nicht erforderlich: reine Inhaltsintegration` vermerken, niemals als bestanden.
8. Arbeitsrecord mit einmaligen Registrierungs-/Prüfbelegen aktualisieren, vollständigen Diff separat selbst prüfen, committen/pushen und Draft-PR mit Head/Basis/Checks/offenen Gates erstellen. Den aktuellen Paketplan gegenüber der PR-Basis ändern und reine Inhalte mit begründeter leerer Zusatzmodulliste führen. `docs` und `ci-required` ohne Player-Build müssen am tatsächlichen Head/Test-Merge erfolgreich sein. Das alte `content_only=true` ist kein Haupt-CI-Vertrag mehr. Keine vollständige Testsuite zusätzlich wiederholen; notwendige Codeänderungen getrennt beauftragen, nichts am Gate vorbeischleusen. Nur mit passender ausdrücklicher Mergefreigabe nach bestandenen Pflichtprüfungen mergen; danach tatsächlichen Main-/Mergecommit prüfen. Erst dann „im Spiel auf main integriert“ melden; kein Release/Deployment ableiten.

Das Endergebnis nennt Paketfundort/-hash, Freigabebeleg, Runtime-ID/Revision/Slot, Export-/Registrierungs- und Dateiprüfbelege, gegebenenfalls begründete Zusatzprobe, PR/Head und Main-Mergecommit. Bei Fehlern den letzten belegten Zustand und nächsten erlaubten Schritt nennen; keine unvollständige Integration als Erfolg melden.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: **Ein fertiggestelltes und final auf `main`
integriertes Rätsel muss nicht erneut produzierbar sein.** Produktionsunterlagen
sind Arbeitsmaterial, kein dauerhaft wachsender Spiel- oder CI-Bestand.

1. Tatsächliche Endabnahme und Merge nachweisen; `registered` auf einem Draftbranch
   allein genügt nicht. `origin/main` aktualisieren und den vollständigen enthaltenen
   Commit nennen. Offene Nacharbeit oder neuere Arbeitsstände derselben ID zuerst
   klären; fremde/offene Produktionen erhalten.
2. Nach dem Merge in einem eigenen kleinen Cleanup-Diff ausführen:

   ```sh
   python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <vollstaendige-main-SHA> --puzzle-id <pz-ID>
   ```

   Mehrere bestätigte IDs können mit wiederholtem `--puzzle-id` zusammengefasst
   werden. Der Befehl prüft Main-Abstammung und unveränderte Integrations-/Arbeitsbytes,
   entfernt die Authoringrevisionen samt Indexeinträgen und ersetzt das Produktionspaket
   durch einen kompakten Integrationsdatensatz. Kein Solver, Proof- oder Bildreplay.
3. Dauerhaft bleiben Runtime-Definition samt Matrix/Hinweisen, Abschlussbild,
   Nutzungshinweise/Lizenzen, ID/Runtime-Revision/Save-Slot, Kategorie und relevante
   Schwierigkeitsmetadaten. Der kleine Integrationsdatensatz bindet diese Daten,
   den ursprünglichen Exporthash und den bestätigten Main-Commit.
   Nach AT-A bleiben zusätzlich die maßgebliche aktive Bildbindung und ihre
   Herkunfts-/Freigabebelege erhalten. Cleanup darf weder die aktuelle Bildfassung
   auf ihren historischen Vorgänger zurücksetzen noch alte Integrationsbelege
   zur Behauptung einer nachträglichen Bildfreigabe umschreiben.
   Ab SD-C1 bleiben zusätzlich die kompakte aktive Bewertung und kompakte Berichte,
   ihre Eingangsbindungen und der gebundene Methoden-/Referenzstand außerhalb
   versiegelter Produktion erhalten. SD-D09/D10 ermöglichen daraus die manuelle
   Neubewertung; alte Produktionsdateien oder ein Produktions-Replay sind dafür
   nicht allgemein vorgeschrieben.
4. Entfernt werden Quellen-/Abstraktionsbilder, verworfene Varianten, Prompts,
   ZIPs, duplizierte Exporte, Proofs, Reparaturspuren, Galerien und Zwischenberichte.
   Keine Kopien in einem neuen Archivordner, in Builds oder CI-Artefakten aufheben.
   Ein Commit-/PR-Verweis genügt für den Entscheidungsverlauf; Git-Historie bleibt
   unangetastet. Fortbestehende Nutzungsrechte/Attributionen dürfen nicht verloren gehen.
5. Diff und unveränderte Runtime-Dateien kontrollieren; Cleanup committen/pushen,
   separat selbst prüfen und nach erfolgreichen Pflichtchecks **unmittelbar mergen**.
   Eigentümerfreigabe vom 15.10.2026: Dieser eng begrenzte Nachintegrations-Cleanup
   ist einschließlich Merge beauftragt, auch wenn der vorausgehende Integrations-PR
   zunächst als Draft vorgelegt wurde. Kein weiterer Routineprompt, kein dauerhaft
   offener Cleanup-Draft. Vor dem tatsächlichen Integrationsmerge nichts bereinigen;
   bei Blocker genau diesen melden. Reine Datenbereinigung führt einen eigenen aktualisierten Paketplan mit
   begründet `modules=[]`; der allgemeine Quellen-/Plankern bleibt Pflicht, ohne Player-Build und
   ohne rätselspezifische Tests. Danach Main-Commit
   und erhaltene Runtime-Dateien nachweisen.

Spätere echte Rätseländerungen sind ein neuer Produktionsauftrag. Fehlende alte
Arbeitsdateien sind kein Defekt und rechtfertigen keine Wiederherstellungspflicht.
Neue Exporte werden weiterhin vollständig geprüft; Bestandsregistrierung und
Kategorienpflege verwenden nach Abschluss nur noch die kompakte Integrationsbindung.

### Abschluss nachträglicher Bildrevisionen · CI2 vom 26.10.2026

Die freigegebene [CI2-Spezifikation](../CI_SLIMMING.md) /
[CI2-E / #417](https://github.com/venomenon328/picross/issues/417) ergänzt den Abschlussvertrag
für spätere Abschlussbilder bereits integrierter Rätsel. Eine bereits bereinigte
Rasterproduktion befreit spätere Bildarbeit nicht von ihrem eigenen Abschluss und
verlangt keine erneute Rasterproduktion. CI2-E implementiert dafür den eigenen
revisionsgenauen Abschlussweg; [T01](../CI2_E_VERIFICATION.md) bindet die Lieferung.

1. Für die abzuschließende Bildrevision tatsächliche Bildfreigaben, aktive Bildbindung
   und enthaltenen Main-Commit prüfen; offene neuere Arbeit derselben ID erhalten.
2. Nach abgeschlossener Integration die zugehörigen Bildarbeitsrevisionen einschließlich
   Quellen, Prompts, Varianten, ZIP-/Rohkopien und erledigter Authoringindexeinträge entfernen.
   Gebundene historische Verweise ersetzen dauerhafte Kopien der Arbeits- und Reviewdaten.
3. Aktuelle Bilddatei, Nutzungshinweise, Herkunfts-/Freigabemetadaten und aktive Bildrevision
   bleiben erhalten. Definitionsbytes, Runtime-Revision, Save-Slot, Registrierung und aktive
   Bewertungen bleiben unverändert. Ein bereits versiegelter ursprünglicher Integrationsbeleg
   wird weder neu erzeugt noch zur nachträglichen Bildfreigabe umgeschrieben.
4. `retire-reveal-production` unterstützt vorhandene `picross-integrated-content-v1`-
   Datensätze und belässt auch vollständige ursprüngliche Pakete unverändert:

   ```sh
   python -m tools.puzzle_production.target_adapter retire-reveal-production --checkout . --integrated-commit <vollstaendige-main-SHA> --authoring-revision <pz-ID> <Authoringrevision>
   ```

   `--authoring-revision ID REVISION` ist für jede abzuschließende Revision ausdrücklich
   zu wiederholen. Kein impliziter ID-Gesamtabbau. Zuvor `origin/main` aktualisieren.
   Der enthaltene Main-Stand muss Record, finale Freigabe und exakt aktuelle Bildquelle
   binden; offene Journale, fremde Bytes, Teilentfernung und betroffene Indexänderungen
   blockieren vor Löschung. Neuere/offene Geschwisterrevisionen bleiben unangetastet.
   Wiederholung mit demselben Main-Beleg nach vollständiger Entfernung ist ein echter
   No-op, auch ohne alte Pakete. `retire-production` bleibt der ursprüngliche Raster-
   Abschlussweg; kein Solver, keine Rekonstruktion oder Änderung alter Receipts.
5. Abnahme verwendet einen begrenzten Datei-/Referenzvergleich und den unveränderten
   aktiven Datenbestand. Kein Solver-, Bild-, Katalog- oder Spielerreplay allein für
   diese Bereinigung; aktive Leser und Rechtebindungen bleiben vorher geprüft.

Die frühere eng begrenzte Freigabe zum Nachintegrations-Cleanup einschließlich Merge
in Schritt 5 bleibt bestehen. Werkzeug-/CI-Codepakete erben keine frühere
Cleanup-Mergefreigabe. Historische CI2-E-Aufträge sind keine heutige Freigabe oder Sperre.

### Zukünftiger Hintergrundweg: Abschluss der Bildarbeit

Der Lebenszyklus aus [PUZZLE_BACKGROUNDS §10](../PUZZLE_BACKGROUNDS.md#10-hp-i1b1--erste-registrierung-und-kompakter-produktionsabschluss)
ergänzt §9 für HP-I1b1-Erstintegration: `retire-production` erzeugt Receipt v2
und erhält die aktive kompakte Hintergrundsource samt echten Freigabe-/Rechte-
und Ableitungsbindungen, PNG/none/Notice und ursprünglichem Exportanker.
Mainbeleg bleibt getrennt im Receipt. Vor Löschung alle gewählten IDs/Bytes
gegen tatsächlichen Main-Stand prüfen; offene/neuere/fremde Arbeit erhalten
oder bei nicht trennbarem ID-Baum vor Mutation blockieren. Nach Abschluss sind
alte innere Refs historische Identitäten, keine Pflicht zu erneutem Dateizugriff.
HP-I1b2 ergänzt späteren Ersatz und seinen revisionsgenauen Abschluss;
`retire-reveal-production` wird dadurch kein Hintergrundabschlusswriter.

Bis zur Auswahl bleiben die drei Einzeldateien erreichbar; bis zur tatsächlichen
finalen Integration alle noch benötigten Arbeits-, Rechte- und Auswahlbindungen
erhalten. Nach bestätigter Endabnahme und Integration auf `main` die zugehörige
abgeschlossene Hintergrundarbeit gezielt entfernen: verworfene Kandidaten,
Prompts, Quellen-/Ableitungskopien, ZIPs und vorübergehende Diagnose-/Reviewdaten.
Offene neuere Bildrevisionen und fremde Arbeit bleiben erhalten. Kein zusätzliches
Kandidatenarchiv, keine Wiederherstellung abgeschlossener Rasterproduktion und
kein Solver-/Bild-/Buchreplay allein für den Abschluss.

Dauerhaft bleiben das aktive Auslieferungsasset beziehungsweise die ausdrücklich
gebundene Leerentscheidung, Rechte/Attribution, aktive Bildrevision und kompakte
Auswahl-/Ableitungs-/Integrationsbindungen mit bestätigtem Main-Stand. Historische
Originalbelege nicht umschreiben, die aktive Bildfassung nicht zurücksetzen.
Ein späterer reiner Hintergrundersatz erhält seinen eigenen revisionsgenauen
Abschluss nach denselben Grenzen; offene Geschwisterrevisionen nicht mitlöschen.

### HP-I1b2: eigene Hintergrundrevision und ihr Abschluss

[Hintergrundvertrag §11](../PUZZLE_BACKGROUNDS.md#11-hp-i1b2--eigenständiger-hintergrundwechsel)
definiert den unveränderlichen `picross-background-adoption-request-v1` als
eigenen Arbeitsrecord. Tatsächliche Auswahl/Entfernung und Zielautorisierung
aufzeichnen, keine neue Rasterfreigabe oder Dummy-ZIP. Kontext aus bytegleicher
aktueller Source und aktuellem freigegebenem Reveal sichern; ursprüngliche
Revealautorität bleibt in initial erhalten. MJ-B führt die eigene Sheetbedienung nach Hintergrundvertrag §7.6: Der Request
bleibt unveränderlich, reguläre Rasterjobs verwenden weiterhin MJ-A.
Eigene Arbeitsrevision über `catalog_background_change store` samt Index sichern,
danach `plan` und autorisiertes `adopt` gemäß Werkzeuganleitung. Fehlende oder
false-Capability blockiert den Zielweg; kein Override. Vorhandene Freigaben
nicht erneut abfragen. HP-I1c liefert die erlaubte Raster-/Revealneubindung
vorhandener Hintergrundziele nach seinem eigenen Vertrag.

Nach bestätigter Mainintegration `target_adapter retire-background-production
--checkout <checkout> --integrated-commit <vollständige-main-SHA>
--authoring-revision <pz-ID> <revision>` verwenden. origin/main vorher aktualisieren.
Nur explizit gewählte, vollständig belegte Revisionen/Indexzeilen entfernen;
neuere Arbeit und aktuelles PNG/none/Notice/Receipt unverändert erhalten.
Eine frühere tatsächlich integrierte, inzwischen abgelöste Revision darf mit
ihrem historischen Mainbeleg abgeschlossen werden. Ganze bereits entfernte
Revision plus Indexzeile ergibt nach frischer Prüfung No-op, Teilreste nicht.
Kein ursprüngliches Raster-ZIP rekonstruieren, kein Solver-/Buchreplay.
Der Befehl liefert einen lokalen Diff, keinen automatischen Commit/Merge.
