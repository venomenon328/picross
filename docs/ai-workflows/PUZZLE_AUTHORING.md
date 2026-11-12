# Picross: Regeln für die KI-gestützte Rätselproduktion

**Version 0.8.0 · Dokumentrevision 3 · 12.11.2026**

Neue Produktionen verwenden den fünfstufigen lokalen Produktionsassistenten.
Maßgeblich: [PW-B / #578](https://github.com/venomenon328/picross/issues/578#issuecomment-6799208194),
[Produktionsarbeitsbereich](../PRODUCTION_WORKSPACE.md) und der geschlossene
[0.8-Datenvertrag](../PW_B_CONTRACT.md). Die Reihenfolge ist verbindlich:
Abschlussbilder → Motivvorlage → Rasterangebote → Kontextzeichnungen → Integration.
Hintergrundarbeit beginnt erst nach der ausdrücklich erklärten Wahl eines
vollständig qualifizierten Rasters. In den Schritten 1–3 keine Hintergrundangebote,
keine Hintergrundbriefings und keine vorgezogenen Hintergrundblocker erzeugen.

Der [0.7-Vorschausnapshot](PUZZLE_AUTHORING_0_7_0_PREVIEW.md) ist historisch.
Bereits integrierte Inhalte, Saves, versiegelte Originale und ihre damaligen
Freigaben bleiben unverändert. Bestehende WIP müssen weder migriert noch im
neuen Assistenten importiert werden. Normale Produktionsaufträge erlauben keine
Werkzeugentwicklung oder neuen Solver-/Bildalgorithmen.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_QUALITY.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`. Vor Paarlinienprüfung oder Übergabe eines Paarprofilpakets zusätzlich `docs/PAIRED_LINES.md` vollständig lesen.
2. Zu Beginn Kategorienquelle, Arbeitsindex und Runtime-Registry lesen; Bestandsrätsel nicht einzeln laden oder nachprüfen. Kategorie nach Auftrag oder prägendem Hauptgegenstand gemäß [Kategorienvertrag](../CATEGORIES.md) zuordnen und in Briefing/Record führen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Aktuelle Dateien und tatsächlich benötigte Fähigkeiten prüfen, keine historischen PR-Statuslisten abarbeiten. Abgeschlossene Lieferungen sind keine erneut offenen Voraussetzungen; nur eine konkrete aktuelle Lücke verfolgen.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API einbauen. Produktionsaufträge mit Repositoryablage erlauben ausschließlich die beauftragte Paketsicherung samt Index; ein Integrationsauftrag erlaubt zusätzlich Abschnitt 8 und die anschließende Bereinigung nach Abschnitt 9. Ablage-/Integrationsmerge braucht den passenden ausdrücklichen oder bedingten Auftrag. Für den zugehörigen Cleanup gilt die Eigentümerfreigabe in Abschnitt 9. Werkzeugänderungen und Veröffentlichung bleiben getrennte Befugnisse. Bereits erteilte passende Aufträge nicht erneut erfragen.
6. **Menschliches Probespielen ist optional und kein Freigabekriterium.** Ein großer Rätselbestand darf ohne Probespiele entstehen. Verpflichtend bleiben die Abschlussbildfreigabe, die Freigabe der daraus abgeleiteten Motivvorlage, die technische Prüfung und die abschließende redaktionelle Abnahme. Spätere Spielerfahrungen dienen der Verbesserung und Kalibrierung.

**Projektlokale Ausnahme zur Modellauswahl:** Normale Produktionsaufträge nach
diesem Regelwerk (1–5 einschließlich Korrektur und Wiederaufnahme) erzeugen keine
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

Frühe Breiten-/Höhenwünsche sind unabhängig: keine, nur eine oder beide Achsen.
Exakt/ungefähr gilt für ausgefüllte Achsen; offene Achsen passend zum Motiv bestimmen.
Eine ausdrücklich aufgehobene Breite lässt die weiterhin gültige Höhe bestehen
und umgekehrt. Leeren allein hebt keine veröffentlichte Vorgabe auf. Keine 0,
angenommene Quadratseite oder Wiederherstellung eines aufgehobenen Altwerts.
Diese Wünsche verbindlich im veröffentlichten Motivbriefing der Übergabe führen;
die spätere konkrete Matrix besitzt zwei Maße. Bestehende geschlossene Formate
und historische Freigaben bleiben unverändert.

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

## 3. Standardablauf: fünf Aufträge

| Schritt | Eingang und Arbeit | Übergabe und echte Entscheidung |
| --- | --- | --- |
| 1 · Abschlussbilder | Tatsächliches Motivbriefing, optional eigene Eingangsdatei. Drei unterschiedliche echte detaillierte farbige Abschlussbilder erzeugen. Keine erfundene ID oder Gitquelle beim neuen Briefing. | `reveal_review`, erreichbare Originaldateien; Mensch wählt und gibt die konkrete unveränderte Fassung frei. |
| 2 · Motivvorlage | Erst nach echter Revealfreigabe dessen gespeicherte Bytes abstrahieren; sinnvollen Größen-/Modus-/Farbenkorridor empfehlen. | `motif_review`, Reveal/Motiv nebeneinander, Verluste und Parameter erklären; echte Motiv-/Parameterfreigabe abwarten. |
| 3 · Rasterangebote | Erst nach Motivfreigabe begrenzte Varianten-/Reparatursuche nach §§4–5. Proof, Eindeutigkeit durch vollständige Deduktion, Qualität, Palette, Schwierigkeit und Herkunft prüfen. | Qualifizierte Einzelrevisionen `raster_ready`; brauchbare Entwürfe getrennt `raster_review`. Keine automatische Auswahl. |
| 4 · Kontextzeichnungen | Ausdrückliche Wahl einer qualifizierten Rasteroption am festen veröffentlichten Quellcommit erfassen. Danach drei echte unterschiedliche isolierte Kontextbilder erzeugen. | `background_review`; wählen, gezielt korrigieren oder ausdrücklich none. Erst vollständige Bereitschaft erlaubt `content_ready`. |
| 5 · Integration | Tatsächliche vollständige Endabnahme, gültiger Rasterstand und ausgewähltes abgeleitetes Bild beziehungsweise ausdrückliches none. | Finalizer → Export → frischer Plan → autorisiertes Register. Git/Draft-PR und bestätigter Mainmerge getrennt nach §8. |

Ein Klick oder kopierter Text ist nur eine lokale Absicht. Erst der tatsächlich
gesendete Auftrag erklärt eine Entscheidung; erst zurückgelieferte Gitdaten
bestätigen den erreichten Stand. Der Assistent führt keine Modellaufrufe oder
Projektwriter aus. Aufträge gehen an ChatGPT/Codex mit erreichbaren festen Gitquellen.
Fehlt Bild-/Repositoryzugriff, die konkrete Lücke melden, keine Platzhalterproduktion.

Korrektur und Wiederaufnahme binden denselben Job, die wirkliche Quelle und
betroffene Darstellungen. Nur abhängige Entscheidungen invalidieren. Materielle
Bildänderungen erhalten neue Revisionen und tatsächliche Freigaben; reine
Hintergrundkorrekturen erzwingen keine unveränderte Logik-/Difficultyproduktion.

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
mit echten Bild-/Rasterlinks, Defiziten/Korrekturen und keine qualifizierten Rasterangebote nutzen.

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

Sichtungsentwürfe sind keine Integrationsoptionen: keine qualifizierten Rasterangebote, kein
`raster_ready`; tatsächlichen Stand als `raster_review` beziehungsweise `blocked`
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

Die automatisch erzeugte workspace.json bindet jedes qualifizierte Angebot
an dessen Einzelrecord, Paketrevision, Originalinventar, Bilder und Quellcommit.
Schritt 4 beginnt ausschließlich mit der tatsächlichen Wahl einer solchen Option.
Die neue Hintergrundrevision trägt eine `picross-raster-selection-v1`-Datei nach
[PW-B-Vertrag](../PW_B_CONTRACT.md); Originalrevisionen bleiben bytegleich.
Nicht gewählte Angebote bleiben bis zur bestätigten Mainintegration erreichbar.
Empfehlung, erster Listeneintrag und höchste Revisionsnummer sind keine Auswahl.

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

### 6.1 Repositoryablage während der laufenden Produktion

Ein neuer Job erhält durch den Produktionsakteur eine neue `pz-…`-ID und genau
einen stabilen Branch `content/pw/<puzzle_id>` von main. Alle weiteren Phasen,
Varianten, Korrekturen und Wiederaufnahmen bleiben auf diesem Branch. Vorher
aktuellen Index und Kollisionen prüfen; keine fremde Arbeit überschreiben.

Jede Übergabe besteht aus einer neuen vollständigen Revision unter
`content/authoring/<puzzle_id>/<revision>/`, indexiert in
`content/authoring/index.json`. Den echten unversiegelten Request v3 mit
Handoff v4, tatsächlichem 0.8-Snapshot und expliziter Dateiliste erstellen:

```text
python -m tools.puzzle_production.authoring_builder build --request <request-v3.json> --source-root <vorbereitete-dateien> --output-root <eigene-arbeitswurzel> --publish-to <produktionscheckout> --history-repo <produktionscheckout>
```

Der Builder validiert Dateien, erzeugt Inventar v1, geschriebenes Original-ZIP,
bytegleiche Handoffkopie, Record v3 und automatisch die geprüfte workspace.json.
Der gemeinsame [Ansichtsübergabeschritt](../PRODUCTION_CURRENT_VIEW.md) setzt
zusätzlich `content/authoring/<puzzle_id>/current-view.json` auf genau diese
Übergabe. Er ist keine Bild-/Rasterwahl. Finalizer und Completion ziehen auch
bei In-place-Fortschreibung die tatsächlichen Hash-/Bytebindungen nach.
Er verwendet unveränderte Proof-/Paletten-/Herkunftsprüfer. Frühphasen sind keine
Inhaltszertifikate; `raster_ready` und spätere Inhaltsphasen werden frisch geprüft.
`presentation={title,raster_offers}` nennt nur tatsächliche Angebote; zusätzliche
Rasteroptionen referenzieren ihre bereits gesicherten qualifizierten Einzelrecords.
Keine manuell erfundene Assetgalerie. Der Dienst schreibt diese Dateien nicht.

Danach vollständige benötigte Originale einschließlich sichtbarer Alternativen,
Index, Projektion und aktuellen Ansichtsverweis committen und pushen. Remotezugriff auf feste Commit-/Dateipfade
prüfen. Den Sicherungscommit erst nach Erfolg melden; `repo_commit` ist lediglich
die gelesene Herkunft. Lokale Pfade/localhost und ungesicherte SHAs sind keine
Cloudübergabe. Neue Quellen erst ausdrücklich im Assistenten laden; laufende
Ansichten bleiben bis dahin am alten Snapshot. Beim Job-/Quellwechsel lokale
Auswahlabsichten verwerfen. Defekte/missing Bilder nicht als Angebote ersetzen.

### 6.2 Übergabedatensatz

Der vollständige geschlossene Vertrag für Request v3, Handoff v4, Record v3,
Resultat v3, Rasterwahl, Inspektion v2 und Projektion v2 steht in
[PW-B_CONTRACT](../PW_B_CONTRACT.md). Frühes `background=null` ist keine
Leerentscheidung. Beide Hintergrundgates sind pending und ihre Belege null.
Nur `background_review` und `content_ready` besitzen Hintergrundarbeit und
die konkrete qualifizierte Rasterwahl. `registered` wird erst aus einer
wirklich abgeschlossenen Registrierung berichtet; Main erst nach bestätigtem Merge.

Inventar v1, Index v1 und unveränderte technische Bilder-/Proofs-/Freigaben
beibehalten. Historische Source-/Export-/Runtimeformate weder umetikettieren noch
neu versiegeln. Unsichere Restpfade, Quellenkonflikte oder unvollständige
Publikationen offen melden; nur identische vollständig geprüfte eigene Wiederholung
ist No-op. Keine pauschale Locklöschung oder verdeckte automatische Recovery.

### 6.3 Hintergrundarbeit in Schritt 4

Nach tatsächlicher Rasterwahl Kontextbriefing erfassen, drei inhaltlich
unterschiedliche echte ImageGen-Originale erzeugen und isoliert vorlegen.
Die [Bildqualität](../PUZZLE_QUALITY.md#9-hintergrundzeichnungen-je-rätsel--noch-nicht-aktivierter-sollweg)
und [HP-W2-Verträge](../PUZZLE_BACKGROUNDS.md) gelten weiterhin: helle neutrale
Graphitzeichnung, transparente Freiräume, proportionaler gemeinsamer 4:1-Fit,
kein Rätselsubjekt, keine Lösungssilhouette, Rasterkopie oder eingebrannte UI.
Indirekte Kontexthinweise sind möglich; keine universelle Spoilerfreiheit zusagen.
Nur eine tatsächliche dokumentierte Eigentümerentscheidung erlaubt eine andere
anfängliche Anzahl oder einen frühen Kandidatenverzicht. Fehlende Bilder sind kein none.

Auswahl/none als bestehende Hintergrundentscheidung v1 binden. Rechte und
isolierte Q-HG-Sichturteile bleiben getrennt von Dateidiagnosen. Nur ausgewähltes
Original nach HP-W2 ableiten, bei none den echten Nullbefund prüfen. Keine
Kandidaten-Testintegration, Buchvorschau oder zusätzliche persönliche Buchabnahme.
Geänderte kreative Bytes benötigen eine neue Entscheidung; unveränderter
Transport und feste deterministische Ableitung keine neue kreative Wahl.

## 7. Freigaben und Abschlussausgabe

Bild-, Motiv-/Parameter-, Rasterwahl-, Hintergrund- und finale redaktionelle
Entscheidungen stammen aus tatsächlichen menschlichen Erklärungen. Software prüft
Aufzeichnungen und Bytes, authentifiziert keine Menschen und ergänzt kein Schweigen.
Bei Korrekturwünschen nicht die noch gar nicht vorhandene geänderte Fassung freigeben.

Jede Chatübergabe nennt kurz erreichte Phase, maßgebliche feste Quelle, tatsächlich
ausgeführte Prüfungen, offene Entscheidung und nächsten Schritt. Echte Bild-/Dateilinks
und stabile Angebotskennungen bereitstellen. Keine technische JSON-Sammlung zum
manuellen Einfügen in ein zweites Sheet; der Assistent liest die veröffentlichten
Originaldaten automatisch. Normale Produktion verwendet weiterhin ihr eigenes
Abschlussformat, nicht das Entwicklungs-HANDOFF-JSON.

Persönliche Arbeitswurzel, Bereinigung und Merge bleiben ausdrücklich gewählte
Auftragsoptionen. Keine Übernahme solcher Befugnisse aus Record oder Projektion.
Neue lokale Briefingentwürfe dürfen unabhängig gespeichert werden; sie behaupten
keine Produktions-ID, Quelle oder Freigabe. Gesicherte Jobs und Revisionen bleiben
über Git nach Neustart wiederauffindbar. Ausdrückliche spätere Hintergrundrevisionen
verwenden den vorhandenen HP-I1b2-Auftrag; kein Import alter Sheet-Sitzungen nötig.

## 8. Abgenommenes Paket ins Spiel integrieren

Schritt 5 setzt vollständige gültige Raster-/Hintergrundbereitschaft und die echte
Endfreigabe v2 am unveränderten Original-ZIP voraus. Fehlende Freigaben sind keine
technische Kleinigkeit. Über den Finalizer v2 vorhandene äußere Entscheidung,
Ableitung und Endfreigabe nachtragen; Originale bleiben bytegleich. Atomare
Recordfortschreibung und geprüfte Projektion verwenden denselben gebundenen Stand.

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <finalize-v2.json> --source-root <neue-belege> --output-root <produktionscheckout> --history-repo <produktionscheckout>
python -m tools.puzzle_production.target_adapter export --allow-background --input <original-package.zip> --external-root <produktionscheckout> --approval <echte-endfreigabe.json> --name <motivname> --runtime-revision 1 --stem <stamm> --save-slot <slot> --category-id <kategorie> --categories content/categories.json --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter plan --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
python -m tools.puzzle_production.target_adapter register --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
```

Die gültige 0.4-Difficultybindung nach §5 und gegebenenfalls das ausdrücklich
gewählte Rebind verwenden. Nur die gewählte Lieferung übernehmen. Ein Export v6
prüft vollständig vor Veröffentlichung; der frische lesende Plan geht jeder
autorisierenden Registrierung voraus. Register prüft selbst erneut und benutzt
keinen fremden Plan als Vertrauenscache. Gespeicherte false-Readinessfelder bleiben
historisch; Zielbereitschaft und registrierter Checkout werden frisch ermittelt.

[RI](../PUZZLE_INTEGRATION.md), [ZA-1](../ZA1_ADAPTER.md) und die bestehenden
Katalogguards bleiben vollständig: sichere Pfade/Namespaces/Dateitypen, aktuelle
Quellen, Capability, Provenienz, Bilder, Palette, Proofs, Kategorie, Difficulty,
IDs/Slots und test_only. Keine Registry-/Runtime-/Saveänderung als Abkürzung.
Export/Plan/Eingangsprüfung behalten ihre fachlichen Grenzen. Registrierung und
deren Recovery besitzen getrennte 1800-s-Schutzrahmen und eine 300-s-Warnung;
ein äußerer Ablauf darf Recovery nicht auf verbrauchte Restzeit beschränken.
Unterbrechung, Rollback, offene Recovery und dauerhafter Abschluss getrennt melden.
Bei unklaren/fremden Bytes Dateien und Journal erhalten, nicht Lock oder Gates umgehen.

Der bereits vorhandene BA-B-Runner bleibt für ausdrücklich vorbereitete passende
Einzelintegrationen nutzbar; 0.8.0 wird als neue native Originalgeneration gelesen,
seine Mengen-, Budget- und Publikationsgrenzen bleiben unverändert.
Kein neuer Batchauftrag, versteckter Solverlauf oder neues Hintergrundregister.

Nach erfolgreicher tatsächlicher Registrierung relevanten Diff und Lieferbytes
prüfen und den Registrierungsstand committen. Mit
`python -m tools.production_workspace.projector --repository <checkout> --complete-record <recordpfad> --integration-commit <volle-SHA>`
den tatsächlichen Abschluss binden und die Projektion automatisch fortschreiben.
Record, Projektion und aktuellen Ansichtsverweis anschließend committen/pushen; Draft-PR im beauftragten
Umfang erstellen. Reine Produktion
erhält CI-Kern ohne Windowsbau und ohne neue rätselspezifische Tests. Merge nur bei
ausdrücklicher passender Befugnis, aktuellem unabhängigen Review und allen Gates.
Ein lokaler Registryerfolg ist kein Mainabschluss. Main erst am bestätigten
Mergecommit melden. Danach revisionsgenaue Bereinigung nach §9.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: **Ein fertiggestelltes und final auf `main`
integriertes Rätsel muss nicht erneut produzierbar sein.** Produktionsunterlagen
sind Arbeitsmaterial, kein dauerhaft wachsender Spiel- oder CI-Bestand.

1. Tatsächliche Endabnahme und Merge nachweisen; `registered` auf einem Draftbranch
   allein genügt nicht. `origin/main` aktualisieren und den vollständigen enthaltenen
   Commit nennen. Offene Nacharbeit oder neuere Arbeitsstände derselben ID zuerst
   klären; fremde/offene Produktionen erhalten.
2. Nach dem Merge in einem eigenen kleinen Cleanup-Diff ausführen:

   Den [abgeschlossenen Ansichtsverweis](../PRODUCTION_CURRENT_VIEW.md) nach
   frischem Abgleich mit Revision und Mainbeleg zuerst entfernen. Ein Verweis
   auf neuere/offene Arbeit bleibt erhalten; dann vor dem ID-Abschluss klären.

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

### Abschluss der Hintergrundarbeit

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
Revealautorität bleibt in initial erhalten. Der eigene Folgeauftrag nach
Hintergrundvertrag §7.6 bleibt unveränderlich; die dortige frühere Sheetbedienung
ist kein paralleler Assistent. Reguläre neue Rasterjobs folgen den fünf Schritten
dieses Dokuments. Folgeaufträge müssen die aktuelle integrierte Herkunft lesen.
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
