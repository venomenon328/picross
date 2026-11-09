# Picross: Regeln für die KI-gestützte Rätselproduktion · 0.7.0-Vorschaustand

**Version 0.7.0 · Dokumentrevision 2 · 09.11.2026**

**Explizit wählbarer Vorbereitungsstand, kein aktiver Produktionsdefault.**
[PB-H / #489](https://github.com/venomenon328/picross/issues/489#issuecomment-6751071312)
unterstützt neue Hintergrundpakete nach diesem vollständigen Snapshot. Er
übernimmt die Inhalts-, Freigabe-, Herkunfts-, Proof-, Paar-, Paletten-,
Parameter-, Rand- und Difficultygarantien von Authoring 0.6.0 und ergänzt die
Hintergrundarbeit mit eigenen geschlossenen Formen und getrennten Phasen.
Der kanonische [aktive Authoringweg](PUZZLE_AUTHORING.md) und das
[Offline-Sheet](Picross_Raetselproduktion_Cheat-Sheet.html) bleiben **0.6.0 /
Dokumentrevision 41**. Dieser Snapshot ersetzt ihren Default nicht und wird
nicht als aktiver Anhang in das Sheet eingebettet.

**Zielpfad:** `docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md` im Repository
`venomenon328/picross`. Ein neuer 0.7.0-Bauauftrag bindet die vollständigen Bytes
dieser Datei, Version 0.7.0, Dokumentrevision 2 und den tatsächlich gelesenen
Quellencommit. Eine umbenannte oder nur im Header geänderte 0.6.0-Datei ist
kein 0.7.0-Snapshot. Bereits versiegelte Originale behalten ihre eigenen Bytes,
Versionen und damaligen Nachweise; kein Versionsdowngrade für neue Arbeit.

[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) ist die vollständig zu lesende
Fachquelle für Typen, Datei-/Hashbindungen, Hintergrundqualität und Einführung.
HP-W2 liefert `describe/derive/verify`; PB-H liefert Bauauftrag v2, Handoff v3,
Record v2, Bauresultat v2, Sheet-Update v3 sowie die lesende Prüfung geschriebener
Raster-/Inhaltspakete. [HP-I1a](https://github.com/venomenon328/picross/issues/561#issuecomment-6752672149)
ergänzt sichere äußere Fortschreibung und den vollständig prüfbaren Export v6.
Inventar v1, Arbeitsindex v1 und die technischen
RP-/Proof-/Difficultyformen behalten ihre bisherigen Verträge.

**Geltungsgrenze:** PB-H baut `brief_ready`, `reveal_review`, `motif_review`,
`motif_approved`, `raster_review`, `raster_ready` und `content_ready`. HP-I1a
konsumiert vorhandene tatsächliche Auswahl/Ableitung und gegebenenfalls
Endfreigabe v2 für die äußere Record-/Sheetfortschreibung; v6-Export benötigt
alle Inhaltsgates und Endfreigabe. Höchste Phase ist `editorially_approved`,
`integration_ready`, `catalog_ready` und `registered` bleiben false.
Registry/Receipt, Erstintegration, Hintergrundersatz, Recovery und Bereinigung
benötigen HP-I1b; die Runtime benötigt HP-I2.
Neue UI-Import-/Sitzungs-/Auftragsformen folgen in #490. Der vollständige
Einzelweg ist noch nicht aktiviert. Eine vorhandene Endfreigabe v2 darf rein
lesend auf ihre unveränderten Originalbindungen geprüft werden; kein neuer
finaler Originalzustand wird gebaut und keine fehlende Erklärung erzeugt.

Neue 0.7.0-Arbeit übernimmt automatische frühe Palettendiagnosen und die
vollständige frische Inhaltsprüfung des Endstands. Die unveränderte Farbregel
bindet Normrevision 4; F05 bleibt eine synthetische visuell angenommene Referenz
mit negativen Messwerten, keine Produktionsausnahme. Messung, echte Sichturteile
und konkrete Eigentümerausnahme werden getrennt geprüft. Der lesende Bericht
ist `picross-authoring-content-inspection-v1`, kein v5-Altexport. Die bisherigen
v1–v5-Export-/Registrierungswege bleiben für neue Hintergrunddaten geschlossen.
V6 verwendet denselben Inhaltsweg und alle geerbten Gates; alte volle und
Quick-/Metadaten-/direkte API-Verbraucher sperren ihn vor produktiver Mutation.

[SD2-Integration](../SD2_INTEGRATION.md), [SD2-D](../SD2_D_ADOPTION.md),
[Abschlussbildtransparenz](../REVEAL_TRANSPARENCY.md), [SD](../PUZZLE_DIFFICULTY.md)
und [SD-C1](../SD_CATALOG.md) behalten ihre Zuständigkeiten. Produktionsdefault
für Difficulty bleibt Methode 0.4; alte 0.1–0.3-Bindungen behalten ihre eigene
Semantik. Historische Bildfreigaben werden nicht zu neu erteilten Freigaben.
Q-A-Sichtung, Paarprofile, feste manuelle Ableitungen und die RI-Guards bleiben
für ihre Gegenstände erhalten. Diese Version bewertet keinen Bestand neu.

Diese Arbeitsanweisung führt die vier bestehenden Aufträge mit den verfügbaren
0.7.0-Vorbereitungsfähigkeiten. **MUSS** bezeichnet eine Pflicht, **SOLL** den
begründet abweichbaren Standard, **DARF** eine Option.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_QUALITY.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`; für diesen Vorschaustand außerdem `docs/PUZZLE_BACKGROUNDS.md` und die PB-H-/HP-I1a-Abschnitte in `docs/ZA1_ADAPTER.md`. Vor Paarlinienprüfung oder Übergabe eines Paarprofilpakets zusätzlich `docs/PAIRED_LINES.md` vollständig lesen.
2. Zu Beginn Kategorienquelle, Arbeitsindex und Runtime-Registry lesen; Bestandsrätsel nicht einzeln laden oder nachprüfen. Kategorie nach Auftrag oder prägendem Hauptgegenstand gemäß [Kategorienvertrag](../CATEGORIES.md) zuordnen und in Briefing/Record führen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Aktuelle Dateien und tatsächlich benötigte Fähigkeiten prüfen, keine historischen PR-Statuslisten abarbeiten. Abgeschlossene Lieferungen sind keine erneut offenen Voraussetzungen; nur eine konkrete aktuelle Lücke verfolgen.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API einbauen. Produktionsaufträge mit Repositoryablage erlauben ausschließlich die beauftragte Paketsicherung samt Index; ein Integrationsauftrag ist erst nach Lieferung der in Abschnitt 8 benannten Fähigkeiten ausführbar. Abschnitt 9 führt die fortbestehenden Abschlussgarantien; der passende neue Writer bleibt Voraussetzung. Ablage-/Integrationsmerge braucht den passenden ausdrücklichen oder bedingten Auftrag. Für den zugehörigen Cleanup gilt die Eigentümerfreigabe in Abschnitt 9. Werkzeugänderungen und Veröffentlichung bleiben getrennte Befugnisse. Bereits erteilte passende Aufträge nicht erneut erfragen.
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
| Hintergrundzeichnung (0.7.0) | Eigenständige Kontextillustration mit eigener Bildrevision und tatsächlicher Auswahl; weder Abschlussbild noch Motivvorlage oder Quelle für Lösungszellen. |

Verbindliche Richtung: **Input → Abschlussbild → freigegebene Abstraktion → Lösungsraster**. Diese drei Darstellungen müssen motivisch zusammenpassen, nicht pixelidentisch sein. Abschlussbild und Motivvorlage als getrennte Dateien und Revisionen führen; das detaillierte Original niemals mit seiner vereinfachten Ableitung überschreiben. Der Hintergrund hat einen Kontextbezug, gehört aber nicht zu dieser Ableitungskette.

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

### 2.5 Hintergrundarbeit: Briefing und drei Kontextzeichnungen

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

Die folgende Tabelle führt die vier Aufträge für den **explizit gewählten
0.7.0-Vorschaustand**. Noch fehlende Integrationsfähigkeiten begrenzen Auftrag 4;
sie ändern keine tatsächliche Freigabe oder Inhaltsgarantie.

| Auftrag | Akteur und verbindliche Arbeit | Ausgabe / Stopp |
| --- | --- | --- |
| **1 · Abschlussbildauswahl** | Bildfähige KI erfasst Text/Bild, liest Quellen, erzeugt drei Abschlussbilder und führt das Hintergrundbriefing nach Abschnitt 2. | `brief_ready` → `reveal_review`: Einzeldateien, Hintergrund-Arbeitsmanifest mit ehrlichem offenen Kontext, Vergleich und gesicherte Übergabe; auf Abschlussbildauswahl/Freigabe warten. |
| **2 · Abschlussbildfreigabe und Abstraktion** | KI bindet die tatsächliche Freigabe, empfiehlt bei offenen Angaben 2–3 Konfigurationen und erstellt unmittelbar die Abstraktion. Nach Reveal-Freigabe drei gespeicherte Kontextzeichnungen erzeugen und isoliert zusammen mit der Motivvorlage zeigen; ausdrücklichen frühen Verzicht belegen. | `motif_review`: Bildvergleich, Detailverluste, Parameterkorridor, vollständige Hintergrundangebote und gesichertes Paket; auf Motivfreigabe und möglichst gebündelte Hintergrundwahl warten. Keine zusätzliche Konfigurationsrunde. |
| **3 · Motivfreigabe und Produktion** | Codex bindet Motiv-/Parameterfreigabe und eine tatsächlich erklärte Hintergrundwahl; führt Abschnitte 4–7 einschließlich Profilprüfung, begrenzter Reparatur, technischer/visueller Prüfung und Difficulty aus. Offene Hintergrundwahl stoppt unabhängige autorisierte Rasterarbeit nicht. | `motif_approved` → `raster_review` → vollständig geprüftes `raster_ready`, bei zusätzlich vollständigem Hintergrund `content_ready`: vorzugsweise 2–3 geprüfte Rasterangebote, echte Ansichten und je ein geprüftes Paket. Hintergrundstatus getrennt nennen. Menschliche Rasterwahl/Endabnahme bleibt offen; keine Registrierung. |
| **4 · Endabnahme und Integration** | Noch offene Hintergrundwahl darf mit der Endabnahme gebündelt werden. Vorhandene tatsächliche Entscheidung, geprüfte Ableitung und Endfreigabe v2 mit HP-I1a außen sichern; nach vollständiger Prüfung v6 exportieren. | Original unverändert, Record höchstens `editorially_approved`; `integration_ready/catalog_ready/registered=false`. Fehlenden HP-I1b/I2-Anschluss als Blocker führen. Registrierung und erst danach Abschluss bleiben von tatsächlich gelieferter Integration nach §§8–9 abhängig. |

Standardarbeitsteilung: ChatGPT für 1–2, Codex für 3–4. Eine Umgebung darf beides übernehmen, wenn sie die tatsächlichen Bild-, Datei-, Repository- und Werkzeugfähigkeiten besitzt. Diese Oberflächenzuordnung löst keine Modell- oder Ausführungsempfehlung aus (§1); keine Modell-API einbauen. Ein zusätzlicher Mergeauftrag ist nur ohne vorherige passende Freigabe nötig; Korrekturrunden und echte Zugriffsprobleme können weitere Nachrichten erfordern.

**Übergabe ohne Zusatzauftrag:** An jedem Stopp Abschnitt 6 ausführen und ID, Revision, Bild-/Paketpfad, Hashbindung, Branch/Commit sowie nächsten erlaubten Auftrag nennen. Nach Auftrag 2 müssen beide Bilddateien, Abschlussbildfreigabe, Invarianten und vorgeschlagene Parameter bereits verfügbar sein; die noch offene Motivfreigabe erteilt der Mensch direkt in Auftrag 3. Bei beauftragter Repositoryablage automatisch committen/pushen und denselben passenden Draft-PR fortführen. Ohne Schreibzugriff ein schlankes Dateiübergabepaket liefern; Codex übernimmt es bei Auftrag 3. Ohne Lesezugriff erforderliche Quellen einmalig bereitstellen lassen, nicht Fähigkeiten vortäuschen. Bei Chatwechsel den gespeicherten Stand statt impliziter Chatkenntnis verwenden.

Freigaben müssen eindeutig die vorgelegten Dateien/Revisionen beziehungsweise das Paketinventar benennen. Hashes selbst aus diesen Dateien ermitteln; der Mensch muss sie nicht abtippen. Akteur, Zeitpunkt und tatsächliche Erklärung protokollieren, niemals eine Freigabe selbst erteilen. Korrekturwünsche erzeugen eine neue Vorlage zur Freigabe; Rücksprünge nach Abschnitt 4.4. `blocked`, `rejected` und `superseded` brauchen Grund und Revision. `registered` bezeichnet den geprüften Checkout, erst der nachgewiesene Merge die Integration auf `main`; Release bleibt separat.

### Hintergrundentscheidungen in denselben vier Aufträgen

Diese verbindliche Ergänzung erzeugt keine zusätzliche Standardphase. Zustände, Gates und ihre geschlossenen Datenformen stehen in
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
sie blockiert nur die davon abhängigen Schritte. `raster_ready` verlangt alle
bisherigen 0.6.0-Inhaltsgarantien; nur Hintergrundbereitschaft und Endabnahme
dürfen fehlen. `content_ready` verlangt zusätzlich gültige Wahl, Rechte,
Q-HG-Urteile und frische Ableitung beziehungsweise ausdrückliches `none`.
Die alte 0.6.0-Bedeutung wird dadurch nicht geändert.

Eine eindeutige frühere Auswahl zur Verwendung derselben unveränderten Datei
genügt als Hintergrundentscheidung; keine zweite Bildbestätigung verlangen.
Die gesonderte Endabnahme und tatsächliche Integrationsbefugnis bleiben erforderlich.
Eine späte Entscheidung an einem versiegelten Rasterpaket benötigt den
sicheren äußeren HP-I1a-Writer nach §6.3; bereits vorhandene Belege sind lesbar;
die konkrete vorgelegte Raster-/Bildfassung muss im finalen Auftrag eindeutig sein.

## 4. Rasterproduktion und technische Pflichtprüfung

**Hintergrund und Raster:** Die folgenden Import-, Logik-, Paletten- und
Rasterprüfungen behalten ihren eigenen Gegenstand. Hintergründe liefern keine
Zellwerte und werden nicht über Solvererfolg freigegeben. Eine offene Hintergrundwahl
stoppt bereits autorisierte unabhängige Rasterarbeit nicht; technische Rasterreife
allein erfüllt die künftigen Hintergrund-/Integrationsgates aus
[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) jedoch nicht. Sämtliche folgenden
Inhaltsanforderungen sind schon für `raster_ready` fällig; `content_ready`
verlangt zusätzlich Hintergrundbereitschaft. Eine neue Version umgeht kein
Paletten-, Proof-, Paar-, Herkunfts-, Parameter-, Rand- oder Difficultygate.

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
**Aus Authoring 0.6.0 vollständig übernommen:** RP-3 prüft die konkrete Matrix vor dem
Solver, RP-5 jede Bewertung und feste manuelle Wege die rekonstruierte Matrix
vor dem Endproof-Replay. Negative Entwürfe bleiben zur Diagnose sichtbar.
`check-palette --candidate <vorhandene-*-candidate.json>` bleibt als zusätzliche
lesende Diagnose verfügbar, ersetzt aber kein finales Gate. Nach jeder Änderung
Matrix, IDs/RGB/Nutzung und Regelbindung frisch rekonstruieren; Rücksprünge nach
§4.4 bleiben Pflicht. Ein reiner Palettenentwurf ohne Nutzung ist vorläufig.

Vor `raster_ready` oder `content_ready` das geschriebene Paket mit der
explizit zugelassenen lesenden ZA-1-Inhaltsprüfung inspizieren: Der Adapter
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
außerhalb versiegelter Originale erhalten und im 0.7.0-Leseweg ausdrücklich
als `palette_exception` beziehungsweise als vorhandene äußere Builderdatei
übergeben; vorhandene manuelle Autorisierungen bleiben zusätzlich nötig. Der
0.6.0-CLI-Schalter allein eröffnet keinen 0.7.0-Exportweg; HP-I1a verlangt den
ausdrücklichen Hintergrund-Opt-in und die vollständige v6-Prüfung nach §8.
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
| Erstmals Paarprofil bei unveränderter Matrix | Neue ausdrücklich profilierte Produktionsbindung, eigener Baseline-/Paarproof und Assessment; keine geänderten Rasterwerte oder umetikettierten Altproofs. Bereits versiegelte Originale erhalten; die neue Lieferung als neue Revision mit echter Regelwerksbindung 0.7.0 führen. Bildfreigaben nur bei unverändertem Gegenstand passend wiederverwenden; Endfreigabe muss das tatsächlich gelieferte Handoff/Inventar binden. |

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

**Gezielte Hintergrundrevision:** Eine materielle Änderung
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

Sichtungsentwürfe sind keine geprüften Rasteroptionen: `Raster-Optionen=[]`,
weder `raster_ready` noch `content_ready`; tatsächlichen Stand als `raster_review` beziehungsweise `blocked`
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
gewählte Option; Auswahl-ID und Paketbindungen im Auftrag abgleichen. Eine
bereits vorhandene Endfreigabe muss extern genau dieses Originalpaket binden;
PB-H liest sie, HP-I1a schreibt die geprüften äußeren Bindungen sicher fort. Keine automatische
Wahl der ersten/empfohlenen oder vermeintlich neuesten Revision über den Index.
Kein Neuversiegeln beim Wechsel im Sheet. Nicht gewählte Angebote bleiben bis zur
finalen Integration erhalten; §9 regelt anschließend die Bereinigung.

**Hintergrund über Rastervarianten hinweg:** Eine einzige Hintergrundauswahl derselben
unveränderten Bildrevision kann zu den motivisch passenden Rasterangeboten
gehören; Rasterversuche erzeugen keine Reveal×Raster×Hintergrund-Kreuzmatrix.
Bei noch offener Bildentscheidung die Angebote ausdrücklich als technisch
rasterreif mit offener Hintergrundwahl kennzeichnen und nach diesem
Bereitschaftsvertrag als `raster_ready` sichern. Die zusätzlichen Bindungen
werden in Record v2 und Sheet-Update v3 geführt; das aktive Sheet-v2-UI
unterstützt diesen neuen Transport noch nicht.
Für spätere Auswahl und gemeinsame Endabnahme die Originalpakete unverändert
erhalten; vorhandene tatsächliche äußere Entscheidungen nach §6.3 lesen,
sichere Fortschreibung mit HP-I1a nach Hintergrundvertrag §7.4 ausführen.

## 5. Schwierigkeit L1–L5

**Unveränderte Difficultygrenze:** Hintergrundstatus und Bildauswahl fließen nicht
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

§§6.1–6.4 beschreiben die PB-H-Ablage für explizite 0.7.0-Revisionen.
Die bestehenden Sicherungs-/Publikationsgarantien bleiben erhalten; neue
Hintergrundformen werden ausschließlich in ihren eigenen Hüllen geführt.
Spätere äußere Fortschreibung und finale Integration bleiben getrennte Fähigkeiten.

### 6.1 Repositoryablage während der laufenden Produktion

Die folgenden Aufbewahrungs- und Replaypflichten gelten bis zur finalen Integration. Danach löst Abschnitt 9 sie ab.

- Zuerst `content/authoring/index.json` und die Runtime-Registry `content/registry.json` lesen. Stabile motivneutrale ID gemäß ZA-1 vergeben; ID, Revision und Pfad auf Kollision prüfen. Bei Wiederaufnahme das verzeichnete Paket am angegebenen Branch/Commit selbst laden; keinen erneuten Upload verlangen, wenn die Bytes zugänglich sind. Mehrdeutige Auswahl klären, fehlenden Binärzugriff konkret melden.
- Ablage: `content/authoring/<puzzle_id>/<revision>/package.zip`. Daneben `handoff.json` als bytegleiche lesbare Kopie, `record.json` und gegebenenfalls die separate `approval.json`. Ein Paket pro Phasenübergabe, Freigabevorlage oder Chatwechsel; keine ZIPs nach jedem Toolaufruf. Bereits vorgelegte Revisionen niemals überschreiben. Neue Inhalte erhalten eine neue Revision; identische Bytes werden wiederverwendet.
- Für diese Übergabe keine zusätzliche Codex-Handoff-Markdowndatei oder duplizierte Folgeauftragsdatei erzeugen, beilegen oder separat verlinken. Das technische `handoff.json`, Inventar, Parameter, Freigaben und Belege bleiben nach diesem Abschnitt vollständig erforderlich. Vorhandene versiegelte Pakete mit einer früher ergänzten Markdowndatei behalten ihre Bytes und Bindungen; diese Straffung beauftragt keine nachträgliche Bereinigung.
- `content/authoring/index.json` ist der von der KI gepflegte Arbeitsindex, **keine Runtime-Registry**. Pro ID/Revision: relativer Recordpfad. `record.json` führt zusätzlich `category_id`, sobald die Motivzuordnung feststeht (bei offenem Briefing ausdrücklich `null`; alte Records ohne Feld bleiben lesbar). Spätestens vor kategorisiertem Export ist eine gültige Zuordnung Pflicht. `record.json` führt Format `picross-authoring-record-v2` mit `background` nach §6.4, ID/Revision, Phasenstatus, Paketpfad/-größe/-SHA-256, Handoffpfad/-SHA-256, Inventarhash (oder ausdrücklich noch offen), Abschlussfreigabepfad/-hash oder `null`, Maße/Modus/Schwierigkeit soweit bekannt, Blocker, nächsten erlaubten Schritt und Integrationsbeleg oder `null`. Branch/Commit der Sicherung in der Übergabe nennen; noch nicht gemergte Ablage nicht als `main` ausgeben. Paket, Handoffkopie und Index gemeinsam committen/pushen, sobald dieser Umfang beauftragt ist; Merge gemäß Entwicklungsworkflow.
- UTF-8-Markdown/JSON, bestehende Matrix-/Proofverträge und verlustfreie Bilder verwenden. Quellenbytes, Herkunft/Nutzungsgrundlage, tatsächliche Bildprompts/-einstellungen (`not_exposed` wenn unbekannt), ausgewählte Bilder, Freigaben, Parameter und Nachweise behalten. Ungeklärte Nutzungsrechte blockieren die Katalogfreigabe. Versuchshypothese, Auswahl-/Ablehnungsgrund, Bildaufrufe, Überarbeitungsrunden, Import-/Reparaturversuche und aktive Menschenminuten getrennt erfassen; unbekannte Werte als `null` führen.
- Vor einer Auswahl alle noch angebotenen Bildvarianten behalten. Nach der Auswahl verworfene ungebundene Bildvarianten nur in ihrer früheren Repositoryrevision belassen; im aktuellen Paket reichen Entscheidung, Hash und genauer früherer Fundort. Keine alten ZIPs in neue ZIPs einbetten. Allgemeine Projekt-/Workflowdokumente und Toolquellen über Repositorycommit/Pfad referenzieren, nicht pro Rätsel kopieren. Ausnahme: den von ZA-1 verlangten, hashgebundenen Regelwerks-Snapshot mitführen.
- Vollständige erforderliche RP-3-/RP-5-Bündel unverändert behalten: Original-/Normalisierungsbild, Design, sämtliche manifestgebundenen Kandidaten, Eltern, Masken, Logik, Proofs und Vergleichsdateien. Bei Paarprofilen gehören auch sämtliche manifestgebundenen Baselineproofs und Assessmentdateien dazu, einschließlich Kandidaten- und frischer Abschlussnachweise einer Reparatur. Auch HTML oder ein verworfener Kandidat ist Pflicht, wenn ein Manifest/Replay ihn bindet. Finale echte Rasteransicht, Bildvergleich, Schwierigkeit, Qualitätsbericht und Belege aller Freigaben/Gates behalten.
- Ungebundene doppelte Berichte, stdout/stderr-Kopien, eingebettete Bildgalerien, temporäre Ansichten, Caches und vollständige Chat-/Repoarchive weglassen. Relevante Fehlversuche als kurze strukturierte Einträge erhalten. Dateien nicht allein anhand der Endung löschen; alle benötigten technischen **und redaktionellen** Referenzen nachverfolgen. HTML/Code aus Paketen nicht ausführen.
- Ein neues Paket vor Inventarisierung verschlanken. Bereits versiegelte Pakete ausschließlich als deklarierte Teilkopie nach `picross-authoring-derivation-v1` ableiten: Originalhandoff/-inventar und ihre Hashes unverändert, Original-ZIP-Hash binden, tatsächlich enthaltene Dateien vollständig hashen. Weglassungen und Grund im äußeren Record dokumentieren. Keine erfundene neue Vollkopie, keine stillschweigende Neuversiegelung oder Umschreibung alter Freigaben. Nachweisbündel nicht intern kürzen. Das Original nicht destruktiv ersetzen.
- Inventar und Handoff ohne Selbstreferenz nach ZA-1 binden; Datei-SHA-256 und kanonische Vertrags-Hashes unterscheiden. Nach Versiegelung spätere Endfreigabe und Integrationsstatus ausschließlich in separater Freigabe/Record führen; das Originalhandoff dafür nicht ändern.
- Vor Ablage ZIP sicher öffnen, Dateimenge/Hashes und bytegleiche Handoffkopie prüfen. Ab `raster_ready` und bei `content_ready` die vollständige lesende Inhaltsprüfung auf dem **geschriebenen ZIP** ausführen. Nur die phasengemäß offene Hintergrundbereitschaft und finale Endabnahme dürfen als entsprechende Blocker bleiben. Frühe Bildphasen erhalten ihre fällige Datei-/Freigabeprüfung; kein behauptetes Inhaltszertifikat. Der lokale [PB-H-Builder](../../tools/puzzle_production/README.md#pb-h-hintergrundpakete-und-lesende-inhaltsprüfung) übernimmt dies aus dem expliziten hashgebundenen Bauauftrag v2: `python -m tools.puzzle_production.authoring_builder build --request <request-v2.json> --source-root <quellen> --output-root <arbeitsordner> [--publish-to <checkout>] [--history-repo <lokaler-checkout>]`. Er sichert nur neue unversiegelte Revisionen bis `content_ready`, erhält offene Entscheidungen und aktualisiert bei ausdrücklicher Zielwahl den Authoringindex. Kein Gitcommit, keine Freigabe oder Registrierung. Bereits versiegelte Originale bleiben unverändert; keine erneute Bauversiegelung.
- `content/authoring/` bleibt außerhalb des Spiels. Erst nach Lieferung der neuen Integrationsfähigkeit erzeugt ZA-1 die offline prüfbare Kopie unter `content/packages/<id>/<revision>/`; dieser Ort ist kein manuell zu befüllender Eingang. Keine zusätzlichen Voll-ZIPs dort erzeugen. Alte Produktionsstände über feste Git-Commits referenzieren; Bis zur finalen Integration keine gebundenen Nachweise löschen. Danach ist Abschnitt 9 Pflicht; keine LFS-Umstellung oder Git-Historienbereinigung.

### 6.2 Übergabedatensatz

Die KI MUSS einen aktuellen Übergabedatensatz in diesem Begleitformat führen. Er ersetzt keine Werkzeugeingabe. Platzhalter/`null` sind keine Nachweise. Im Paket bleiben alle Pfade relativ; technische Prüfinputs müssen darin vollständig vorliegen. Der äußere Repositoryrecord verwendet repositoryrelative Pfade. Historische Vergleichsreferenzen dürfen auf genaue frühere Commits zeigen; sie ersetzen keinen Replayinput.

```yaml
format: picross-authoring-handoff-v3
rulebook: {version: "0.7.0", file: "<vollständiger 0.7.0-Vorschausnapshot>", sha256: null}
puzzle_id: "<stabile ID>"
revision: "<Paketrevision>"
repo_commit: "<vollständige tatsächlich gelesene SHA>"
state: brief_ready
brief: "<Datei mit Auftrag, Invarianten, Grenzen und Herkunft>"
approved_parameters: []
reveal: {file: null, sha256: null, approval: null}
motif: {file: null, sha256: null, derived_from_reveal_sha256: null, approval: null}
candidate: {bundle: null, variant: null, proof: null, verification: null, certification: null}
palette_review: null # inventarisierter Sichtrecord bei Farbe vor raster_ready/content_ready
palette_assessment: null # optionaler gespeicherter Befund, immer frisch nachgeprüft
origin_verification: null
repair: {reference: null, plan: null, replay: null}
inventory: {file: null, sha256: null}
difficulty: null
report: null
decisions: "<Varianten-/Entscheidungsprotokoll>"
effort: "<Aufwandsprotokoll>"
background:
  manifest: {storage: package, root: "<Manifestarbeitswurzel>", ref: {file: "<Manifestpfad>", sha256: null, bytes: null}}
  decision: null
  derivation: null
  history: null
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
  background_choice: pending
  background_asset: pending
gate_evidence:
  reveal_approval: null
  motif: null
  provenance: null
  logic: null
  frame: null
  visual: null
  difficulty: null
  reveal_consistency: null
  final_editorial: null
  target_export: null
  background_choice: null
  background_asset: null
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

### 6.3 Hintergrundarbeit: Sicherung, Auswahl und Wiederaufnahme

[PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) definiert die geschlossenen
Arbeits-, Entscheidungs- und Ableitungsformen sowie deren azyklische Hashbindungen.
PB-H unterstützt Handoff **v3**, Record **v2**, Bauauftrag/Bauresultat **v2**
und Sheet-Update **v3**; Inventar **v1** und Arbeitsindex **v1** bleiben.
HP-W2 liefert die eigenständigen Arbeits-/Entscheidungs-/Auftrags-/Befundformen
und `describe/derive/verify`. Die gewählte Datei wird nach dem festen gemeinsamen
Profil abgeleitet; ausdrücklich `none` liefert nur einen Nullbefund. Der Builder
prüft deklarierte Ableitungen mit den tatsächlichen Quellen und Tool-/Codec-
Bindungen frisch. Ungeklärte Rechte oder fehlende Q-HG-Urteile werden dadurch
nicht zu positiven Belegen. [Lokale Aufrufe und Grenzen](../../tools/puzzle_production/README.md#pb-h-hintergrundpakete-und-lesende-inhaltsprüfung).
HP-I1a unterstützt die sichere äußere Fortschreibung unten; neue Sheetbedienung
bleibt #490. Die enge lesende HP-W2-Regel aus Hintergrundvertrag §4.3 erhält
originale Producer-/Request-/Befundbytes und vergleicht aktuelle vollständige
Modul-/Codec-/Profilbindung; nur ein anderer Git-HEAD/Dirtyzustand bei identischen
ausführbaren Bytes verlangt keine neue Ableitung. `derive/reused` bleibt streng
an den vollständigen aktuellen Toolhash gebunden. Ein inkompatibler eingebetteter
Altbefund bleibt prüfpflichtig und blockiert auch bei neuer äußerer Ableitung.

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
mit dessen Endabnahme erfolgen. HP-I1a konsumiert die bereits tatsächlich
aufgezeichneten passenden Belege mit dem sicheren Finalizer; PB-H liest sie.
An einem bereits
versiegelten Kandidatenpaket wird die Entscheidung **außerhalb des Originals** an dessen unveränderte Paket-, Handoff- und
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

**Sichere äußere Fortschreibung:**

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <request.json> --source-root <neue-dateien> --output-root <authoring-root> [--history-repo <checkout>]
```

Der Befehl verwendet den geschlossenen Finalizerauftrag nach Hintergrundvertrag §7.4.
Er bindet den erwarteten Record v2 als `Ref`, einen neuen Sidecarordner derselben
Authoringrevision, vollständige Hintergrundbindung, genau vier explizite
Autorisierungsrefs/null und exakt die neuen Nutzdateien. Keine menschliche
Erklärung erzeugen und keine gültige Autorisierung still entfernen. Das
Originalmanifest bleibt dieselbe Identität; materielle Bildänderung braucht
eine neue reguläre Revision.

Unter demselben Authoringlock werden Sidecardateien vollständig geprüft und
ohne Ersetzen publiziert, danach der Record atomar zuletzt. `operation.json`
bindet exakte Vorher-/Nachherrecords und Dateien; derselbe Request setzt einen
vollständigen unverreferenzierten Rest fort oder liefert nach Recordcommit einen
Byte-/mtime-No-op. Ein HP-W2-Befund braucht seinen eigenen exakten Unterordner.
Index v1 und Originalbytes bleiben erhalten. Die geprüften Autorisierungsorte
stehen eng in `record.verification.authorizations`; keine neuen Record-
Top-Level-Felder. Resultat v1 liefert tatsächlichen Record v2 und Sheet-Update v3
oder konkreten Fehler/Restpfad. Fehlende Integration und ungesicherter Gitstand
bleiben sichtbar; keine Registrierung, Git-Schreiboperation oder Bereinigung.

### 6.4 Geschlossene 0.7.0-Formen und fällige Lesegates

Die folgenden Feldmengen und Deltas sind vollständig. Die Feldtypen, Grenzen
und konkreten Querverweise aus Hintergrundvertrag §§3–7 sind verbindlich;
alle dortigen Pflicht- und Nullfelder ausgeben. Unbekannte Felder oder Formate
sind Fehler. Ein technischer Quellpfad ist keine beliebig zu suchende Datei.

| Form | Vollständiger Generationseingang beziehungsweise Delta |
| --- | --- |
| `picross-authoring-build-request-v2` | Exakt `format,handoff,document_revision,files,target,category_id,reveal_options,external`; Handoff v3/0.7.0, positive zum Snapshot passende Dokumentrevision. `files` je exakt `{path,source,sha256,bytes}`. `target=local` oder `repository`; letzteres nur mit explizitem Publikationscheckout. |
| `picross-authoring-handoff-v3` | Sämtliche bisherigen Handoff-v2-Pflicht-/Optionalfelder mit unveränderten Typ-/Nullregeln, passende 0.7.0-Regelbindung und zusätzlich `background`. Exakt zwölf Gates und gleichnamige `gate_evidence`; Originalendfreigabe und Export bleiben offen. Keine Hintergrunddaten unter `editorial`. |
| `picross-authoring-record-v2` | Bestehender vollständiger PB-A-Record plus `background`; geprüfter Zustand und tatsächlicher Prüfungsumfang, offene Blocker und nächster Schritt bleiben sichtbar. Ein Bau ist kein Git-Sicherungscommit. |
| `picross-authoring-build-result-v2` | Erfolg exakt `format,status,directory,indexed,record,sheet,files`; Fehler exakt `format,status,message,remaining,next_action`. Verschachtelt Record v2/Update v3. |
| `picross-authoring-finalize-request-v1` | Exakt `format,record,sidecar_root,background,authorizations,files`; vollständige Typ-/Pfad-/Null-/Wiederaufnahmeregeln in Hintergrundvertrag §7.4. |
| `picross-authoring-finalization-v1` | Exakt `format,request_sha256,record,before,after,files`; operative Sidecarbindung mit bytegenauen Vorher-/Nachherrecords, keine neue Freigabe. |
| `picross-authoring-finalize-result-v1` | Erfolg exakt `format,status,record,sheet,operation`; Fehler exakt `format,status,message,remaining,next_action`. Status-/Restregeln nach Hintergrundvertrag §7.4. |
| Unverändert | `picross-authoring-file-inventory-v1`, `picross-authoring-index-v1`, bestehende RP-/Proof-/Difficultyformen. Die Authoring-Teilkopie `picross-authoring-derivation-v1` ist keine HP-W2-Hintergrundableitung. |

Der Record führt weiterhin `puzzle_id,revision,state,category_id,
build_request_sha256,repo_commit,document_revision,rulebook,package,handoff,
inventory_sha256,final_editorial_approval,width,height,mode,used_colors,difficulty,
verification,blockers,next_action,next_step,integration,source_commit,pr,reveal,
motif,reveal_options,parameters` plus `format,background`. Seine finale
Freigabereferenz ist bei 0.7.0 v2. `external` bleibt exakt auf die optionalen
Namen `approval.json`, `manual-authorization.json`, `owner-override.json` und
`palette-exception.json` begrenzt; kein neuer freier Sidecarmechanismus.

`BackgroundBinding` ist genau `{manifest,decision,derivation,history}`.
`manifest` ist ein `StoredRef`, Entscheidung/Ableitung jeweils `StoredRef|null`.
`StoredRef` ist genau `{storage,root,ref}` mit `storage=package|external`,
`root` als sichere relative Wurzel oder `.`, `ref={file,sha256,bytes}`.
Im Originalhandoff sind alle drei StoredRefs ausschließlich `package`.
`history` ist null oder exakt `{commit,storage,path,root}`; `commit` ist die
vollständige vorhandene Git-SHA, `storage=directory|package`. Die äußere Wurzel
lokalisiert Bytes; innere `Ref.file`-Pfade, Originalbytes und Hashes bleiben
unverändert. Entscheidungsevidenz und Vorgänger beziehen sich auf die
Entscheidungswurzel, Manifest-/Kandidatenrefs auf die Manifestarbeitswurzel,
PNG und Befund auf den gemeinsamen Ausgabeordner. Norm-/Toolquellpfade sind
keine Payloadreferenzen. Keine implizite Rootsuche oder globale Zusammenführung.

Die ausführbaren Hintergrundformen sind:

| Form | Pflichtfelder |
| --- | --- |
| `picross-background-work-v1` | `format,puzzle_id,job_id,revision,created_utc,context,briefing,candidate_policy,presentation,candidates,test_only` |
| `picross-background-decision-v1` | `format,puzzle_id,job_id,revision,background_revision,manifest,outcome,candidate_id,original,profile,actor,timestamp_utc,statement,evidence,presented_package,previous_decision,carried_from,accepted_deviations,test_only` |
| `picross-background-derive-request-v1` | `format,manifest,decision,source,profile,expected_tool_sha256,output` |
| `picross-background-derivation-v1` | `format,request_sha256,request,puzzle_id,job_id,background_revision,manifest,decision,outcome,candidate_id,source,profile,profile_sha256,tool,tool_sha256,output,diagnostics,test_only` |

`C(x)` ist strikt kanonisches JSON nach Hintergrundvertrag §3 (UTF-8,
sortierte Schlüssel, keine nichtendlichen Zahlen, kein abschließendes LF im
Hashinput); `H(x)=SHA256(C(x))`. Die gespeicherte kanonische JSON-Datei endet
mit LF und hat daher einen eigenen Datei-SHA-256. Dateihashes niemals mit
Request-/Profil-/Toolobjekthashes verwechseln.

Der Befund erhält den vollständigen ursprünglichen Request unverändert;
Manifest/Entscheidung/Quelle/Profil und erwarteter Toolhash müssen exakt zu
seinen wiederholten Bindungen passen. Bei `selected` ist `output` der Ref auf
`background.png`, bei `none` null. `diagnostics` ist exakt
`{source,output,upscaled}`; bei none alle null, sonst tatsächliche Bilddiagnosen.
Eine Bilddiagnose ist `{format,mode,width,height,alpha}` mit
`alpha={min,max,transparent_pixels,partial_pixels,opaque_pixels}`. Das feste
Profil erzeugt 2304×576 RGBA/sRGB, proportionalen Fit mit gemeinsamem unteren
mittigen Anker und transparentem Rest. Alpha-Zählung ersetzt kein Q-HG04-Urteil.

Das Arbeitsmanifest enthält `context={summary,protected_features,
excluded_subjects,reveal,reveal_approval}`, `candidate_policy={count,exception}`
und `presentation={status,evidence}`. Ohne tatsächliche Vorlage bleibt
`status=pending`; `offered` bindet die reale Vorlage. Standard `count=3`,
abweisende Vorgabe nur mit gebundener tatsächlicher Eigentümererklärung.
Jeder Kandidat enthält `id,revision,description,original,provenance,generation,
review`. `provenance` führt `author,source,usage_basis,rights_status,attribution,
evidence`; `generation` führt `tool,model,prompt,parameters,seed,unknown`.
Herkunft/Rechte, bekannte Generierungsdaten und Q-HG01–04 bleiben
unverfälscht, Unbekanntes ausdrücklich offen. Ein Reviewurteil bindet
`result,reason,method,norm,actor,timestamp_utc,evidence`; zugelassene Ergebnisse
sind `erfüllt`, `Warnung`, `nicht erfüllt`, `nicht geprüft`. Dateidiagnosen sind
keine visuellen Urteile. Abweichungen brauchen die konkrete zulässige Annahme;
unabdingbare Voraussetzungen bleiben bindend.

`outcome=selected` bindet genau einen angebotenen Kandidaten, seine Originalbytes
und das feste Profil. `none` bindet eine tatsächliche ausdrückliche Leerentscheidung;
vor Kandidatenproduktion zusätzlich den erklärten Verzicht auf die Dreierzahl.
`rejected` ist keine Annahme. Ohne Entscheidung ist der abgeleitete Status
`pending` oder `offered`; bei abgelehnter Vorlage bleibt er `rejected`.
Entscheidungsvorgänger sind azyklisch und erhalten Puzzle-/Job-/`test_only`-
Identität. `carried_from` überträgt ausschließlich administrativ neu verpackte
unveränderte Gegenstände mit unveränderten tatsächlichen Humanfeldern;
materielle Bild-/Kontext-/Profiländerung macht alte Wahl/Ableitung ungültig.

Vor Auswahl sind sämtliche angebotenen Originale und Belege enthalten. Nach
Auswahl darf der aktuelle Transport ausschließlich verworfene Kandidatendateien
weglassen, wenn die exakte frühere identische Manifestrevision mit diesen Bytes
über `history` lesbar bleibt. Der explizite API-Parameter `history_repo` /
CLI-Schalter `--history-repo <checkout>` ist dabei rein lesender lokaler
Gitkontext; kein Requestfeld, kein Fetch/Checkout. Ohne diesen erreichbaren
Kontext alle angebotenen Dateien behalten; verlangte Weglassungen sind sonst
Fehler. Aktive Quelle, Entscheidung, Rechte-/Sichtbelege und Ableitung können
niemals durch History ersetzt werden. Sichere Pfade, Casefold-/Windowsaliase,
Datei-/Ordnerkonflikte, Links und Größenlimits gelten für die vollständige Menge.

Ein verschachtelter, gebundener Hintergrundbefund `derivation.json` bleibt mit
seinem Ausgabeordner unverändert erhalten. Root-Authoring-Teilkopie, eingebettete
ZIPs und Neuversiegelung sind ausgeschlossen. Deklarierte Ableitungen werden
mit HP-W2 `verify` frisch geprüft; fehlende Bereitschaft bleibt offen, falsche
oder veraltete deklarierte Bindungen werden zurückgewiesen. Kein stilles
Re-Derive, Ersetzen des Codecstands oder automatisches Beschaffen von Dateien.

Bei Gate `pass` zeigt `background_choice` genau auf die Entscheidungsdatei,
`background_asset` genau auf den Befund (`root` plus innerer Ref-Pfad); bei
anderen Gatewerten ist der jeweilige Beleg null. `background_asset=pass`
verlangt zusätzlich geklärte Rechte, gültige Q-HG-Urteile und die frisch geprüfte
Ableitung. Alle bisherigen Inhaltsgates aus Abschnitten 4–5 bleiben schon vor
`raster_ready` vollständig fällig. `content_ready` verlangt beide neuen Gates
auf `pass`. Spätere äußere Belege schreiben diese Originalgates nicht um.

Öffentliche Leseschnittstelle: `authoring_package.open_package(path,
allow_background=True, history_repo=..., external_root=...)`, danach
`target_adapter.inspect(package, ..., allow_background=True)`. Die Prüfung
verwendet den vollständigen bestehenden Inhaltsweg; kein vorübergehendes
Umetikettieren auf 0.6.0. Ihr Bericht
`picross-authoring-content-inspection-v1` führt `original_state`, frisch
geprüften `effective_state` und stets `integration_ready=false`. Nur tatsächlich
ausgeführte Prüfungen werden im Record als solche geführt. HP-I1a öffnet
inspect/export nur mit ausdrücklichem `--allow-background` und erforderlichen
`--external-root`-/`--history-repo`-Wurzeln. Defaultreader und alte
Export-/Registrierungswriter akzeptieren diese neue Generation nicht automatisch.

Eine schon vorhandene `picross-editorial-approval-v2` wird nur gelesen. Sie hat
sämtliche bisherigen v1-Felder `format,actor,timestamp_utc,statement,puzzle_id,
revision,handoff_sha256,inventory_sha256,selection,test_only` plus
`original_zip_sha256` und `background`. Letzteres ist exakt
`{manifest,decision,derivation,outcome,candidate_id,original,output,profile_sha256}`;
`selection` bindet weiterhin `variant,matrix_hash,logic_hash,reveal`.
Alle Bindungen müssen zum unveränderten Original-ZIP und den tatsächlich
vorliegenden Dateien passen. Kein Erzeugen, Neudatieren oder Umbinden einer
Freigabe durch Builder oder Finalizer. HP-I1a ergänzt sichere äußere
Fortschreibung und v6-Export; Registry/Integration folgt HP-I1b, Runtime HP-I2.

Die bisherigen Publikationsgarantien gelten unverändert: eigene temporäre
Revision, deterministische Bytes/ZIP-Metadaten, frische sichere Extraktion,
bytegleiche äußere Handoffkopie, kooperativer Lock, exakter No-op, echte
Kollision statt Überschreiben, vollständige Revision vor atomarem Indexwechsel.
Ein Abbruch zwischen Revision und Index meldet die vollständige unindexierte
Revision als Rest; keine behauptete gemeinsame Transaktion. Eigene entbehrliche
Stages nach dem bestehenden Besitz-/Lockvertrag entfernen, fremde Arbeit erhalten.

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
Für den Vorschauweg die v3-Daten aus dem Paket/Record weitergeben. Das aktuelle
Offline-Sheet unterstützt diesen Import noch nicht; bis #490 keinen v2-Datensatz
mit verlorenen Hintergrundbindungen erzeugen und keine neue Sheetfähigkeit behaupten.
Keine Modell-, Reasoning- oder Ausführungsempfehlung anfügen und keine dafür
veranlasste Modellrecherche durchführen (§1). Die technische Übergabe nach §6
und die menschlichen Freigaben werden dadurch nicht ersetzt oder verkürzt.

```json
{
  "format": "picross-cheatsheet-update-v3",
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
  "Hintergrunddaten": null,
  "Hintergrundstatus": null,
  "Hintergrund-Optionen": [],
  "Hintergrundauswahl": null,
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
Der PB-H-Builder leitet seine Sheet-Ausgabe aus demselben äußeren Record ab.
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

### Optionslisten im Sheet-Format v3

Abschlussbild- und Rasteroptionsliste samt Auswahlfeldern bleiben Pflicht.
Die zusätzliche Hintergrundliste und ihre vier Felder folgen unten. Alte
v1/v2-Updates behalten ihre Semantik; das heutige UI ist weiterhin ein Altreader. Jede Liste enthält höchstens 20 Einträge.
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
`raster_ready` oder `content_ready` angeboten; ihre Ansicht erfolgt mit echten
Links im Chat nach [Qualitätsvertrag §5](../PUZZLE_QUALITY.md). V3-Rasteroptionen
führen zusätzlich genau `Hintergrunddaten` und `Produktionsstatus`; Status ist
`raster_ready|content_ready`, Bindung gehört zur eigenen Paketrevision.

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
| `Hintergrunddaten`, `Produktionsstatus` | Exakte Hintergrundbindung dieser Paketrevision; `raster_ready` oder `content_ready` |

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

Der in #490 zu liefernde neue Sheetweg muss die Auswahl mit Beschreibung und Dateireferenz zeigen; die folgenden UI-Regeln sind bis dahin ein Implementierungsvertrag. Wechsel eines
Rasters übernimmt alle zugehörigen Bindungen gemeinsam; Einzelbearbeitung dieser
Felder ist bei Optionslisten gesperrt. Solange keine Auswahl getroffen wurde,
sind die davon abhängigen Freigabeaufträge gesperrt. Auftrag 2 nennt Datei, ID
und Hash; Auftrag 4 nennt Raster-ID/Kandidat/Ansicht und das passende Paket samt
Inventarhash. Import, Dropdownwechsel, Sitzung und ZIP-Export erteilen keine
Freigabe und ändern kein Repository. Erst das tatsächliche Absenden des passenden
Freigabeauftrags ist eine menschliche Erklärung.

Für diesen Vorschauweg sind Sitzung v5 und Auftrag v4 nach Hintergrundvertrag §7.3 vorgesehen; erst #490 liefert ihren verlustfreien UI-Transport. Die alten Sitzungen v3/v4 und Auftragsexporte erhalten ausschließlich ihre bisherigen Listen und Auswahl. Import eines alten
v1-Blocks/Records oder einer alten Sitzung entfernt vorherige Optionsdaten;
Reset leert sie ebenfalls. Fehlerhafte Daten dürfen keinen Teilstand übernehmen.
Die HTML-Datei bleibt offline ohne automatische Bild-/Repositoryabrufe. Bilder
stehen im Chat beziehungsweise Paket; Pfade im Dropdown sind keine Behauptung,
dass das Sheet die Bytes oder Proofs selbst geprüft hätte. Nach Produktionsabschluss
werden Optionslisten geleert, statt auf entfernte Arbeitsdateien zu verweisen.

Der eingebettete aktive Sheet-Snapshot und seine Anzeige bleiben bei
`PUZZLE_AUTHORING.md` 0.6.0/docrev40; dieser 0.7.0-Vorschausnapshot hat seinen
eigenen Pfad und wird nicht ungeprüft als UI-Default eingebettet. Der
Regelwerk-Stand ist unabhängig vom Paketstand; ein noch nicht gemergter Workflow
muss über den tatsächlichen Arbeitsbranch/Commit erreichbar benannt werden.

### Bestehende persönliche Einstellungen und lokale Codex-Arbeit

Das bestehende Offline-Sheet trennt persönliche Einstellungen von Rätseldaten.
Arbeitswurzel, Bereinigungsoption, Regelquelle/-pfad/-stand, Ablage-/Mergeoption
und Farbschema werden im Browser gespeichert. Ein anderer Browser, ein geänderter
Dateipfad oder gelöschte Browserdaten können einen Einstellungsimport erfordern.
Fehlender oder gesperrter Browserspeicher wird sichtbar gemeldet; das Sheet bleibt
mit manueller Eingabe und Sicherung nutzbar. Produktionsdaten und Bildbytes werden
nicht automatisch dauerhaft gespeichert.

Die gesonderte Sicherung `picross-cheatsheet-settings-v1` enthält genau `format`,
`settings` und `theme`. `settings` enthält genau die Zeichenketten `workspaceRoot`,
`cleanupMode` (`on|off`), `ruleSource` (`repo|attachment`), `rulePath`, `ruleRef`,
`repoSave` (`repo|local`) und `mergeMode` (`merge|draft`); `theme` ist
`system|light|dark`. Eine leere Arbeitswurzel bezeichnet noch fehlendes Setup.
Nichtleere Wurzeln müssen absolute Windows-, UNC- oder POSIX-Verzeichnispfade
ohne Steuerzeichen oder Punkt-/Elternsegmente sein. Vor einem Einstellungsimport
alle Werte prüfen und die neue Wurzel samt Freigabeoptionen ausdrücklich zur
Bestätigung zeigen; kein Teilimport bei ungültigen Daten.

Neue Produktionssitzungen verwenden `picross-cheatsheet-session-v4`: dieselbe
äußere Hülle wie v3, aber `fields` enthält ausschließlich Rätseldaten. Alte
Sitzungen v1–v3 bleiben ladbar; darin enthaltene persönliche Einstellungen und
Ablage-/Mergeoptionen werden bewusst nicht übernommen. Auch Sheet-Updates und
Records ändern diese Einstellungen nicht. „Neues Rätsel“ entfernt Produktionsdaten,
Optionslisten und Bildanhang, erhält aber alle persönlichen Einstellungen.
Eine Sitzung ist weder Einstellungsbackup noch Produktionspaket oder Freigabe.

Der aktive 0.6.0-Sheetweg verwendet `picross-authoring-request-v3`; zusätzlich zu den
bisherigen Metadaten, Rätseldaten, Varianten und Bildbezügen enthält `execution`
die tatsächliche `surface`, `local_workspace_root` (Zeichenkette oder `null`) und
`cleanup_own_local_work` (Boolean). Die Freigabe ergibt sich weiterhin allein aus
dem ausdrücklich abgesendeten Auftrag, nicht aus importierten Ergebnisdaten.
Die alten Produktions-/Sheetformen bleiben unverändert. Die 0.7.0-Generation
verwendet die neuen Formen aus §6.4 und dem folgenden Abschnitt; ihr UI-Import
und Auftragsexport werden erst in #490 implementiert.

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

### Hintergrunddaten im Update v3 und Grenze des aktuellen Sheets

Die vier zusätzlichen Pflichtfelder sind `Hintergrunddaten:BackgroundBinding|null`,
`Hintergrundstatus:pending|offered|rejected|selected|none|legacy|null`,
`Hintergrund-Optionen:[]` und `Hintergrundauswahl:ID|none|null`.
Bei neuem noch nicht zugeordnetem Auftrag sind Bindung/Status/Auswahl null und
Optionen leer; `legacy` gilt ausschließlich für einen tatsächlich alten Eingang.
Ein gebautes 0.7.0-Paket besitzt stets eine Hintergrundbindung. Die Optionen
enthalten je exakt `ID,Beschreibung,Datei,SHA-256,Bildrevision`, geordnet wie das
gebundene offered-Manifest; `Datei` ist relativ zu dessen Arbeitswurzel.

| Geprüfter Status | Optionen und Auswahl im erzeugten Update |
| --- | --- |
| `pending` | Manifest vorhanden, Entscheidung/Ableitung null; Optionen `[]`, Auswahl null. |
| `offered` | Sämtliche angebotenen Kandidaten, Entscheidung/Ableitung null; Auswahl null. |
| `rejected` | Gebundene rejected-Entscheidung, Ableitung null; Optionen nach Manifestpräsentation, Auswahl null. |
| `selected` | Vollständige offered-Optionen, tatsächliche Entscheidung und passend oder noch offen gebundene Ableitung; Auswahl genau die gewählte Kandidaten-ID. |
| `none` | Tatsächliche Leerentscheidung, Optionen nach Manifestpräsentation, Ableitung passend oder noch offen; Auswahl `none`. |

Bei pending-Präsentation sind Optionen immer leer. Nach Auswahl dürfen verworfene
Optionen über überprüfte History erreichbar sein; ihre Projektion behauptet keine
lokal vorhandenen Originale. `none` ist reserviert, keine Kandidaten-ID.
Ein Wechsel benötigt die tatsächlichen Originale erreichbar. Empfehlungen bleiben
ohne Auswahl; Hintergrundoptionen erzeugen kein Kreuzprodukt mit Rastervarianten.
Abschlussbild-/Rasteroptionen bleiben gegenseitig ausgeschlossen.

Nach Auftrag 2 drei tatsächliche Hintergrunddateien gemeinsam mit der Motivvorlage
isoliert zeigen. Status, menschliche Entscheidung, technische Ableitung und
visuelle Urteile getrennt nennen. Eine echte frühere Wahl derselben unveränderten
Datei bleibt gültig; keine zusätzliche Routinebestätigung. Eine späte Wahl darf
mit Endabnahme gebündelt werden, benötigt aber die tatsächliche Raster-/Bildbindung
und den sicheren äußeren HP-I1a-Writer. Die bereits vorhandene Endfreigabe v2
wird geprüft und unverändert gebunden.

Die geplante Sitzung v5 hat exakt `format,choices,fields,filter,image,background`,
der geplante Auftrag v4 exakt `format,execution,created_at,rulebook,fields,choices,
input_image,note,requested_step,prompt_file,background`. `background` ist jeweils
`{binding,status,options,selection}`; nur `selection` darf als neue Formularabsicht
abweichen. Die tatsächliche historische Entscheidung wird dadurch nicht geändert.
Rasterwechsel muss seine Paket-/Hintergrundbindungen gemeinsam übernehmen.
Unbekannte Generation/Felder, widersprüchliche Nullwerte oder unvollständige
Optionen verwerfen den gesamten Import atomar. Diese neuen UI-Reader/-Writer,
Sitzungs-/Auftragsexporte und Promptfunktionen gehören **#490**; PB-H liefert
nur Record v2 und die daraus korrekt abgeleitete Update-v3-Ausgabe. Das aktuelle
Offline-Sheet erhält ausschließlich den aktiven 0.6.0-Snapshot samt Revision.

## 8. Endabnahme, Export und verbleibende Integration

**0.7.0-Grenze:** HP-I1a liefert äußere Endabnahme und v6-Export, keinen
Registrierungs-/Integrationswriter und keine Runtime. Höchste effektive Phase
ist `editorially_approved`; `integration_ready/catalog_ready/registered=false`.
Die nachfolgend vollständig erhaltenen 0.6.0-/ZA-1-Verfahren dokumentieren die
geerbten Integrationsgarantien und ihre bestehenden Werkzeuge. Sie sind für
diesen neuen 0.7.0-Eingang **nicht ausführbar**, bis HP-I1b/I2 die dazugehörigen
Writer und Runtime tatsächlich liefern. Keine alten Befehle mit einer neuen
Versionshülle umgehen.
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
heutige `plan-update`-/`update`- oder `catalog_reveal`-Operation.

### HP-I1a: vorhandene Endabnahme sichern und v6 exportieren

Nach tatsächlicher Auswahl und Endabnahme die Belege gemäß §6.3 außen sichern.
Ein gültiges `none` bleibt eine explizite Entscheidung samt Nullbefund; fehlende
Dateien oder ausstehende Antworten sind kein `none`. Die ursprünglichen
Paket-/Handoff-/Inventarbytes und Inhaltsnachweise bleiben erhalten. Eine neue
Auswahl auf derselben Vorlage bindet ihren wirklichen Vorgänger; ein anderes
Manifest oder materiell geändertes Bild benötigt eine reguläre neue Revision.

`target_adapter inspect/export` ausdrücklich mit `--allow-background`, bei
äußeren Belegen `--external-root <wurzel>` und erforderlichenfalls
`--history-repo <checkout>` verwenden. Vor Export Kategorie und alle bisherigen
Inhaltsgates sowie tatsächliche Endfreigabe v2 prüfen. Die geschlossene
[v6-Generation](../ZA1_ADAPTER.md#hp-i1a--äußere-endabnahme-und-export-v6)
transportiert das unveränderte `input/package.zip`, benötigte äußere Dateien
mit unveränderten inneren Pfaden und die vollständige Freigabebindung.
Ausschließlich ausgewähltes PNG und passende Notice liegen zusätzlich im
Runtimebaum; bei `none` keine Nulltextur. Keine Änderung von Logikdefinition,
Runtime-Rätselrevision oder Saveidentität.

Kompakte Historyeingänge werden beim Export lokal exakt geprüft. Nur tatsächlich
fehlende inaktive Kandidatenrefs dürfen nach dem ZA-1-Vertrag ausdrücklich
supplementiert werden; Original- und aktuelle Außensicht getrennt auswerten.
Aktive Dateien sind regulär erforderlich, Supplemente ersetzen keine aktive
Quelle oder Freigabe. Der Export wird vor Veröffentlichung vollständig frisch
verifiziert; `verify-export` prüft ihn danach ohne ursprünglichen Quellcheckout
oder Historyroot mit kompatibler tatsächlicher Modul-/Codec-/Profilbindung.
Ein inkompatibler alter Befund im unveränderten Original bleibt ein Blocker;
alte Freigaben/Requests nicht umschreiben. Keine beliebige spätere
Werkzeugportabilität behaupten.

`picross-target-inspection-v6` trennt Original-/Effektivstatus, technische und
redaktionelle Bereitschaft vom fehlenden Integrationsanschluss. Nur die frische
Exportprüfung erlaubt `export_verified=true`; es gibt keine zusätzliche Phase.
Keine Registry-, Plan-, Register-, Update-, Sync- oder Cleanupoperation mit v6
starten. Diese Verbraucher müssen v6 vor Mutation zurückweisen. Arbeitsbindungen
bis zum späteren unterstützten Abschluss erhalten; keine vorgezogene Bereinigung.

### Geerbter 0.6.0-Referenzweg · kein 0.7.0-Integrationsaufruf

Alle folgenden Kommandos in Abschnitt 8 beziehen sich ausschließlich auf ihre
bisherigen unterstützten Eingänge. Ihre Vorbedingungen bleiben auch für den
künftigen 0.7.0-Weg erforderlich; sie ersetzen dessen fehlende Writer nicht.

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

**0.7.0-Grenze:** Die folgenden Aufbewahrungs-, Eigentums- und Abschlussgarantien
bleiben erhalten. HP-I1a liefert weder Integration noch einen neuen Abschlusswriter.
Die bestehenden `retire-production`-/`retire-reveal-production`-Befehle sind
keine unterstützten Befehle für neue Hintergrundpakete. Erst tatsächlich
integrierte 0.7.0-Inhalte mit dem passenden HP-I1b-Abschlussweg dürfen nach diesen
Regeln bereinigt werden. Bis dahin alle benötigten aktiven Arbeitsbindungen erhalten.

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

### Späterer Hintergrundabschluss nach HP-I1b

Der Lebenszyklus aus [PUZZLE_BACKGROUNDS](../PUZZLE_BACKGROUNDS.md) ergänzt §9
nach Einführung der passenden Abschlussfähigkeit. Die heutigen
`retire-production`-/`retire-reveal-production`-Befehle erhalten dadurch keine
behauptete Unterstützung neuer Hintergrundformen. Keine gebundenen Originale
mit einem ungeeigneten alten Reader bereinigen.

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
