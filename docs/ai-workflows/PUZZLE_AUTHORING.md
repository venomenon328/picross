# Picross: Regeln für die KI-gestützte Rätselproduktion

**SD2-C · 26.10.2026, nach separatem R01 über PR #410 integriert:** Der vor Code versionierte
[Integrationsvertrag](../SD2_INTEGRATION.md) ergänzt den Schwierigkeitsweg um
explizite Methodenwahl und neue geschlossene Hüllen. Beide Freezes bleiben;
der reale Produktionsdefault ist durch [SD2-D-F01/T01](../SD2_D_ADOPTION.md)
auf dem Arbeitsbranch ausdrücklich 0.4. Vorläufiger Kandidat, explizite
Analyse/Import, Metadaten-Rebind auf den fertigen Export und kontrollierte
Registrierung bleiben getrennte Schritte. Aktivierung und echte
Bestandsumstellung im echten Katalog sind in diesem C-Auftrag ausgeschlossen.
Der [synthetische T01-Nachweis](../SD2_C_VERIFICATION.md) bindet neue und
geänderte Logik, historische Rebinds und die gemeinsame Transaktion.

**Version 0.5.0 · Dokumentrevision 23 · 22.10.2026**

Paarlinienprofile und Schwierigkeit 0.2 benötigen Version 0.5.0. Alte versiegelte
0.4.x-Pakete behalten ihren Linienvertrag; sie werden nicht umetikettiert.
Dokumentrevision, Datei-SHA-256 und Repositorycommit binden den verwendeten Snapshot.

**AT · Abschlussbildtransparenz, Umsetzungsvorbereitung V4 vom 19.10.2026; AT-A integriert:**
[AT](../REVEAL_TRANSPARENCY.md) ergänzt den transparenten Abschlussbildstandard
und einen getrennten nachvollziehbaren Bildupdateweg. AT-A liefert dessen
Technik und synthetische Regressionen; AT-B stellt danach den gebundenen Bestand
mit tatsächlichen Bildfreigaben um. Version 0.5.0 bleibt erhalten; alte versiegelte
Snapshots und ihre Freigaben werden nicht umgeschrieben. Diese Dokumentrevision
startet keine Bildbearbeitung, Raster-/Logikproduktion oder Integration.
Der getrennte [AT-B-V01-Auftrag](../AT_B_VERIFICATION.md) lieferte alle 26
gebundenen Bilder in eigenen `at-b-r01`-Ablagen zunächst als `reveal_review`.
Die anschließende [Eigentümerabnahme](../AT_B_OWNER_APPROVAL.md) erlaubt AT-B-F01
mit kontrollierter Übernahme und AT-B-T01. Versiegelte ZIPs, Inventare und
Handoffs behalten Dokumentrevision 21 und ihren damaligen Zustand. Die spätere
Freigabe steht nach §6.1 separat; nur der äußere Record führt `registered`
für den geprüften Arbeitsbranch. Paketrevision und aktive AT-Bildrevision 1
sind verschieden; keine Rasterproduktion oder neue ZA-1-Adapterabnahme.

**SD / [#235](https://github.com/venomenon328/picross/issues/235), SD-C1 nach R2 integriert:**
Für Schwierigkeitsarbeit zusätzlich [Rätselschwierigkeit](../PUZZLE_DIFFICULTY.md)
und [SD-C1](../SD_CATALOG.md) vollständig lesen. §5.2/§8 binden den externen
0.3-Input für neue Registrierung und logikrelevante Updates. Authoring 0.5.0,
versiegelte Pakete und historische 0.1-/0.2-Produktionsbindungen bleiben erhalten.
SD-C2 hat nach bestandenem Vor-Übernahme-Review gemäß SD-C2-F01 die
[26 Bestandsbewertungen kontrolliert übernommen](../SD_CATALOG.md), einschließlich
echtem Wiederholungs-No-op. Separates qualifiziertes finales Datenreview und Merge bleiben offen.

**Zielpfad:** `docs/ai-workflows/PUZZLE_AUTHORING.md` im Repository `venomenon328/picross`.

Diese Arbeitsanweisung regelt die Erstellung neuer Rätsel vom Motivauftrag über das zuerst freigegebene Abschlussbild bis zur geprüften Integration ins Spiel. **MUSS** bezeichnet eine Pflicht, **SOLL** den begründet abweichbaren Standard, **DARF** eine Option.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`. Vor Paarlinienprüfung oder Übergabe eines Paarprofilpakets zusätzlich `docs/PAIRED_LINES.md` vollständig lesen.
2. Zu Beginn Kategorienquelle, Arbeitsindex und Runtime-Registry lesen; Bestandsrätsel nicht einzeln laden oder nachprüfen. Kategorie nach Auftrag oder prägendem Hauptgegenstand gemäß [Kategorienvertrag](../CATEGORIES.md) zuordnen und in Briefing/Record führen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Aktuelle Dateien und tatsächlich benötigte Fähigkeiten prüfen, keine historischen PR-Statuslisten abarbeiten. Abgeschlossene Lieferungen sind keine erneut offenen Voraussetzungen; nur eine konkrete aktuelle Lücke verfolgen.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API einbauen. Produktionsaufträge mit Repositoryablage erlauben ausschließlich die beauftragte Paketsicherung samt Index; ein Integrationsauftrag erlaubt zusätzlich Abschnitt 8 und die anschließende Bereinigung nach Abschnitt 9. Ablage-/Integrationsmerge braucht den passenden ausdrücklichen oder bedingten Auftrag. Für den zugehörigen Cleanup gilt die Eigentümerfreigabe in Abschnitt 9. Werkzeugänderungen und Veröffentlichung bleiben getrennte Befugnisse. Bereits erteilte passende Aufträge nicht erneut erfragen.
6. **Menschliches Probespielen ist optional und kein Freigabekriterium.** Ein großer Rätselbestand darf ohne Probespiele entstehen. Verpflichtend bleiben die Abschlussbildfreigabe, die Freigabe der daraus abgeleiteten Motivvorlage, die technische Prüfung und die abschließende redaktionelle Abnahme. Spätere Spielerfahrungen dienen der Verbesserung und Kalibrierung.

### Prüfungen gehören zur Produktion, nicht zur CI

- Sämtliche rätselbezogenen Prüfungen – Lösbarkeit, Eindeutigkeit, unabhängiger Proof, Herkunft, Reparatur, Gestaltung und Zielintegration – MUSS die KI für die jeweilige neue/geänderte Revision im Produktionsauftrag durchführen und dateigebunden belegen. Unveränderte, passend gebundene Nachweise wiederverwenden; erforderliche Neuprüfungen nach Abschnitt 4.4 bleiben Pflicht.
- **Keine rätselspezifischen Unit-Tests, Test-Snapshots, CI-Falllisten oder dauerhaften Replayjobs anlegen.** Ein neues Rätsel darf weder den allgemeinen Testbestand noch einen CI-Korpus erweitern. Prüfscripte für den konkreten Auftrag nur temporär außerhalb der Test-Discovery ausführen; Ergebnisse ins Paket, keine CI-Anbindung.
- Bei reinen Inhaltsänderungen den automatischen schlanken Inhaltspfad aus [CI_POLICY](../CI_POLICY.md) verwenden. Er prüft Änderungspfade und reguläre Dateimodi, keine Rätselqualität. Kein Solver/Proof-Replay, Unit-Testlauf, Godot-Start, Funktions-/Render-/Performancetest oder Spielerexport in dieser CI. Auch unveränderte Bestandsrätsel nicht erneut prüfen.
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

Verbindliche Richtung: **Input → Abschlussbild → freigegebene Abstraktion → Lösungsraster**. Alle Darstellungen müssen motivisch zusammenpassen, nicht pixelidentisch sein. Abschlussbild und Motivvorlage als getrennte Dateien und Revisionen führen; das detaillierte Original niemals mit seiner vereinfachten Ableitung überschreiben.

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

**Bei Abschlussbild, Motivvorlage und Raster prüfen:** Erkennbarkeit; Silhouette/Proportionen; wichtige Details und Negativräume; Palette beziehungsweise Mono-Lesbarkeit; Serienästhetik. Jedes Kriterium als `erfüllt`, `Korrektur nötig` oder `verfehlt` mit kurzer Begründung dokumentieren. Eine gute Gesamtnote darf einen beschädigten Identitätskern nicht verdecken.

Im Raster nur diskrete Werte, keine Zwischenfarben oder Textur als Zellzustand. Farbige Raster müssen selbst erkennbar sein; bei Mono darf das Abschlussbild zusätzliche Klarheit schaffen. Bei der Abstraktion diese Details gezielt reduzieren, zusammenfassen oder weglassen, ohne Identität, Perspektive, Hauptproportionen und wichtige Negativflächen des Abschlussbilds zu verändern. Das Abschlussbild nicht nachträglich zur Rechtfertigung eines abweichenden Rasters umgestalten.

### 2.4 Abschlussbildauswahl und Abstraktionsfreigabe

1. Standardmäßig **drei sinnvoll unterschiedliche Abschlussbilder** erzeugen. Komposition, Pose oder Farbgebung variieren; Stil, Detailanspruch und Auftrag bewahren. Bei bindender Referenz (`faithful`) Identität und geschützte Geometrie erhalten; freie Interpretation (`free`) ausdrücklich festhalten. Eine ausdrückliche Vorgabe darf die Variantenanzahl reduzieren.
2. Native Bildgenerierung verwenden. Jede Variante als tatsächliche Einzeldatei speichern und zeigen; eine Kontaktübersicht ist nur Auswahlhilfe. Ohne verfügbare Bildfunktion den Bildschritt als blockiert melden; Konzepte oder behauptete Dateien ersetzen keine Abschlussbildauswahl.
3. Der Mensch wählt und korrigiert. **Vor jeder Abstraktion MUSS das konkrete Abschlussbild ausdrücklich freigegeben sein**, gebunden an Datei, Revision/Hash und zu bewahrende Merkmale. Eine Auswahl mit Korrekturwunsch ist noch keine Freigabe der korrigierten Fassung.
4. Danach geeignete Rasterkonfiguration empfehlen und aus den gespeicherten Bytes des freigegebenen Abschlussbilds eine Motivvorlage ableiten. Standardmäßig eine gezielte Abstraktion für die empfohlene Konfiguration erstellen; zusätzliche Varianten nur bei einem konkreten Darstellungs-/Detailkonflikt. Abschlussbild und Abstraktion nebeneinander vorlegen und Detailverluste benennen.
5. **Vor jeder eigentlichen Rasterproduktion MUSS die konkrete abstrahierte Motivdatei freigegeben sein**, einschließlich Revision/Hash, Abschlussbildbezug, Motivinvarianten und zulässiger Größen-/Modus-/Crop-Varianten. Die Abschlussbildfreigabe ersetzt diese Abstraktionsfreigabe nicht. Schweigen oder unverbindliches Interesse ist keine Freigabe.

Korrekturen nur an der gewählten Darstellung durchführen, zu bewahrende Merkmale nennen und eine neue Revision speichern. Nach zwei erfolglosen Runden Ursache und geänderten Plan vorlegen. Ist die Abstraktion ungeeignet, zunächst Vereinfachung, Größe oder Rasterpalette korrigieren. Ein anderes Abschlussbild benötigt erneut die ausdrückliche Bildfreigabe; es darf nicht stillschweigend an technische Fehlschläge angepasst werden.

## 3. Standardablauf: vier Aufträge

Ein Auftrag umfasst sämtliche nötigen Arbeiten bis zur nächsten menschlichen Freigabe. Prüfung, Schwierigkeit, Bericht, Verschlankung und Dateisicherung sind Teilaufgaben, keine zusätzlichen Dialogphasen. Keine routinemäßigen Rückfragen zum Weiterarbeiten, Packen, Prüfen oder Registrieren. Nur fehlende Freigaben, materielle Motivänderungen, wesentliche Entscheidungen oder konkrete Blocker unterbrechen den Ablauf.

| Auftrag | Akteur und verbindliche Arbeit | Ausgabe / Stopp |
| --- | --- | --- |
| **1 · Abschlussbildauswahl** | Bildfähige KI erfasst Text/Bild, liest Quellen und erzeugt drei Abschlussbilder nach Abschnitt 2. | `brief_ready` → `reveal_review`: Einzeldateien, kurzer Vergleich, gesicherte Übergabe; auf menschliche Abschlussbildfreigabe warten. |
| **2 · Abschlussbildfreigabe und Abstraktion** | KI bindet die tatsächliche Freigabe, empfiehlt bei offenen Angaben 2–3 Konfigurationen und erstellt unmittelbar die Abstraktion für ihre Empfehlung. Keine zusätzliche Konfigurationsrunde, sofern keine feste Grenze verletzt wird. | `reveal_approved` → `motif_review`: Bildvergleich, Detailverluste, eindeutiger vorgeschlagener Parameterkorridor und vollständige Dateiübergabe für Codex; auf Motivfreigabe warten. |
| **3 · Motivfreigabe und Produktion** | Codex protokolliert die menschliche Freigabe der Motivdatei samt Parameterkorridor; führt Abschnitte 4–7 einschließlich Variantenwahl, Profilprüfung nach 4.2.1, begrenzter Reparatur, technischer und visueller Prüfung sowie Schwierigkeit aus. | `motif_approved` → `raster_review` → `content_ready`: echtes Endraster, Abschlussbild, kompakter Bericht und geprüftes Paket zur Endabnahme. Keine Spielregistrierung. |
| **4 · Endabnahme und Integration** | Codex bindet die menschliche Endabnahme separat und führt Abschnitte 8–9 aus. | `editorially_approved` → `catalog_ready` → `registered`: Integrationsbelege und PR; bei passendem Mergeauftrag Main-Merge, anschließend geprüfte Bereinigung samt eigenem Merge. Ohne Integrationsmerge beim PR stoppen. |

Standardarbeitsteilung: ChatGPT für 1–2, Codex für 3–4. Eine Umgebung darf beides übernehmen, wenn sie die tatsächlichen Bild-, Datei-, Repository- und Werkzeugfähigkeiten besitzt. Modell/Reasoning wählt der Nutzer in der Oberfläche; keine Modell-API einbauen. Ein zusätzlicher Mergeauftrag ist nur ohne vorherige passende Freigabe nötig; Korrekturrunden und echte Zugriffsprobleme können weitere Nachrichten erfordern.

**Übergabe ohne Zusatzauftrag:** An jedem Stopp Abschnitt 6 ausführen und ID, Revision, Bild-/Paketpfad, Hashbindung, Branch/Commit sowie nächsten erlaubten Auftrag nennen. Nach Auftrag 2 müssen beide Bilddateien, Abschlussbildfreigabe, Invarianten und vorgeschlagene Parameter bereits verfügbar sein; die noch offene Motivfreigabe erteilt der Mensch direkt in Auftrag 3. Bei beauftragter Repositoryablage automatisch committen/pushen und denselben passenden Draft-PR fortführen. Ohne Schreibzugriff ein schlankes Dateiübergabepaket liefern; Codex übernimmt es bei Auftrag 3. Ohne Lesezugriff erforderliche Quellen einmalig bereitstellen lassen, nicht Fähigkeiten vortäuschen. Bei Chatwechsel den gespeicherten Stand statt impliziter Chatkenntnis verwenden.

Freigaben müssen eindeutig die vorgelegten Dateien/Revisionen beziehungsweise das Paketinventar benennen. Hashes selbst aus diesen Dateien ermitteln; der Mensch muss sie nicht abtippen. Akteur, Zeitpunkt und tatsächliche Erklärung protokollieren, niemals eine Freigabe selbst erteilen. Korrekturwünsche erzeugen eine neue Vorlage zur Freigabe; Rücksprünge nach Abschnitt 4.4. `blocked`, `rejected` und `superseded` brauchen Grund und Revision. `registered` bezeichnet den geprüften Checkout, erst der nachgewiesene Merge die Integration auf `main`; Release bleibt separat.

## 4. Rasterproduktion und technische Pflichtprüfung

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

Flächennutzung, Hauptformen, Proportionen, Innenräume, isolierte Zellen, leere Innenzeilen/-spalten, Detaildichte und Farbunterscheidbarkeit prüfen. Ein Auge darf eine Einzelzelle sein; ein Henkel braucht einen Innenraum. Leere Innenstreifen nicht mechanisch entfernen.

Belegungsanteile unter 15 % oder über 85 %, isolierte Einzelzellen und vollständig leere Innenlinien **nur als Prüfanlass** markieren. Das sind redaktionelle Warnschwellen, keine harten Qualitätsgrenzen. Abweichungen sind bei motivischem Nutzen zulässig und kurz zu begründen. Nicht zugunsten einer Kennzahl Form oder Erkennbarkeit verschlechtern. Farben auch in kleiner Darstellung und, soweit verfügbar, mit Farbsinnsimulation kontrollieren; keine unbeschlossene Farbmetrik als Pflichtgrenze ausgeben.

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
| Erstmals Paarprofil bei unveränderter Matrix | Neue ausdrücklich profilierte Produktionsbindung, eigener Baseline-/Paarproof und Assessment; keine geänderten Rasterwerte oder umetikettierten Altproofs. Bereits versiegelte Originale erhalten; die neue Lieferung als neue Revision mit echter Regelwerksbindung 0.5.0 führen. Bildfreigaben nur bei unverändertem Gegenstand passend wiederverwenden; Endfreigabe muss das tatsächlich gelieferte Handoff/Inventar binden. |

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

## 5. Schwierigkeit L1–L5

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

Die folgenden Aufbewahrungs- und Replaypflichten gelten bis zur finalen Integration. Danach löst Abschnitt 9 sie ab.

- Zuerst `content/authoring/index.json` und die Runtime-Registry `content/registry.json` lesen. Stabile motivneutrale ID gemäß ZA-1 vergeben; ID, Revision und Pfad auf Kollision prüfen. Bei Wiederaufnahme das verzeichnete Paket am angegebenen Branch/Commit selbst laden; keinen erneuten Upload verlangen, wenn die Bytes zugänglich sind. Mehrdeutige Auswahl klären, fehlenden Binärzugriff konkret melden.
- Ablage: `content/authoring/<puzzle_id>/<revision>/package.zip`. Daneben `handoff.json` als bytegleiche lesbare Kopie, `record.json` und gegebenenfalls die separate `approval.json`. Ein Paket pro Phasenübergabe, Freigabevorlage oder Chatwechsel; keine ZIPs nach jedem Toolaufruf. Bereits vorgelegte Revisionen niemals überschreiben. Neue Inhalte erhalten eine neue Revision; identische Bytes werden wiederverwendet.
- `content/authoring/index.json` ist der von der KI gepflegte Arbeitsindex, **keine Runtime-Registry**. Pro ID/Revision: relativer Recordpfad. `record.json` führt zusätzlich `category_id`, sobald die Motivzuordnung feststeht (bei offenem Briefing ausdrücklich `null`; alte Records ohne Feld bleiben lesbar). Spätestens vor kategorisiertem Export ist eine gültige Zuordnung Pflicht. `record.json` führt Format `picross-authoring-record-v1`, ID/Revision, Phasenstatus, Paketpfad/-größe/-SHA-256, Handoffpfad/-SHA-256, Inventarhash (oder ausdrücklich noch offen), Abschlussfreigabepfad/-hash oder `null`, Maße/Modus/Schwierigkeit soweit bekannt, Blocker, nächsten erlaubten Schritt und Integrationsbeleg oder `null`. Branch/Commit der Sicherung in der Übergabe nennen; noch nicht gemergte Ablage nicht als `main` ausgeben. Paket, Handoffkopie und Index gemeinsam committen/pushen, sobald dieser Umfang beauftragt ist; Merge gemäß Entwicklungsworkflow.
- UTF-8-Markdown/JSON, bestehende Matrix-/Proofverträge und verlustfreie Bilder verwenden. Quellenbytes, Herkunft/Nutzungsgrundlage, tatsächliche Bildprompts/-einstellungen (`not_exposed` wenn unbekannt), ausgewählte Bilder, Freigaben, Parameter und Nachweise behalten. Ungeklärte Nutzungsrechte blockieren die Katalogfreigabe. Versuchshypothese, Auswahl-/Ablehnungsgrund, Bildaufrufe, Überarbeitungsrunden, Import-/Reparaturversuche und aktive Menschenminuten getrennt erfassen; unbekannte Werte als `null` führen.
- Vor einer Auswahl alle noch angebotenen Bildvarianten behalten. Nach der Auswahl verworfene ungebundene Bildvarianten nur in ihrer früheren Repositoryrevision belassen; im aktuellen Paket reichen Entscheidung, Hash und genauer früherer Fundort. Keine alten ZIPs in neue ZIPs einbetten. Allgemeine Projekt-/Workflowdokumente und Toolquellen über Repositorycommit/Pfad referenzieren, nicht pro Rätsel kopieren. Ausnahme: den von ZA-1 verlangten, hashgebundenen Regelwerks-Snapshot mitführen.
- Vollständige erforderliche RP-3-/RP-5-Bündel unverändert behalten: Original-/Normalisierungsbild, Design, sämtliche manifestgebundenen Kandidaten, Eltern, Masken, Logik, Proofs und Vergleichsdateien. Bei Paarprofilen gehören auch sämtliche manifestgebundenen Baselineproofs und Assessmentdateien dazu, einschließlich Kandidaten- und frischer Abschlussnachweise einer Reparatur. Auch HTML oder ein verworfener Kandidat ist Pflicht, wenn ein Manifest/Replay ihn bindet. Finale echte Rasteransicht, Bildvergleich, Schwierigkeit, Qualitätsbericht und Belege aller Freigaben/Gates behalten.
- Ungebundene doppelte Berichte, stdout/stderr-Kopien, eingebettete Bildgalerien, temporäre Ansichten, Caches und vollständige Chat-/Repoarchive weglassen. Relevante Fehlversuche als kurze strukturierte Einträge erhalten. Dateien nicht allein anhand der Endung löschen; alle benötigten technischen **und redaktionellen** Referenzen nachverfolgen. HTML/Code aus Paketen nicht ausführen.
- Ein neues Paket vor Inventarisierung verschlanken. Bereits versiegelte Pakete ausschließlich als deklarierte Teilkopie nach `picross-authoring-derivation-v1` ableiten: Originalhandoff/-inventar und ihre Hashes unverändert, Original-ZIP-Hash binden, tatsächlich enthaltene Dateien vollständig hashen. Weglassungen und Grund im äußeren Record dokumentieren. Keine erfundene neue Vollkopie, keine stillschweigende Neuversiegelung oder Umschreibung alter Freigaben. Nachweisbündel nicht intern kürzen. Das Original nicht destruktiv ersetzen.
- Inventar und Handoff ohne Selbstreferenz nach ZA-1 binden; Datei-SHA-256 und kanonische Vertrags-Hashes unterscheiden. Nach Versiegelung spätere Endfreigabe und Integrationsstatus ausschließlich in separater Freigabe/Record führen; das Originalhandoff dafür nicht ändern.
- Vor Ablage ZIP sicher öffnen, Dateimenge/Hashes und Handoffkopie prüfen. Ab `content_ready` zusätzlich ZA-1 `inspect` auf dem **geschriebenen ZIP** ausführen; fehlende Endabnahme darf als einziger entsprechender Blocker bleiben. Frühere Bildphasen sind noch kein ZA-1-Eingang: deren vorhandene Dateibindungen/Freigaben prüfen, keine Adapterzertifizierung behaupten. Für das Packen gibt es derzeit keinen eigenen CLI-Befehl; Standard-ZIP-Werkzeuge und vorhandene APIs benutzen, keinen Befehl erfinden.
- `content/authoring/` bleibt außerhalb des Spiels. Nach Integration erzeugt ZA-1 die offline prüfbare Kopie unter `content/packages/<id>/<revision>/`; dieser Ort ist kein manuell zu befüllender Eingang. Keine zusätzlichen Voll-ZIPs dort erzeugen. Alte Produktionsstände über feste Git-Commits referenzieren; Bis zur finalen Integration keine gebundenen Nachweise löschen. Danach ist Abschnitt 9 Pflicht; keine LFS-Umstellung oder Git-Historienbereinigung.

### 6.2 Übergabedatensatz

Die KI MUSS einen aktuellen Übergabedatensatz in diesem Begleitformat führen. Er ersetzt keine Werkzeugeingabe. Platzhalter/`null` sind keine Nachweise. Im Paket bleiben alle Pfade relativ; technische Prüfinputs müssen darin vollständig vorliegen. Der äußere Repositoryrecord verwendet repositoryrelative Pfade. Historische Vergleichsreferenzen dürfen auf genaue frühere Commits zeigen; sie ersetzen keinen Replayinput.

```yaml
format: picross-authoring-handoff-v2
rulebook: {version: "0.5.0", file: "<Regelwerk>", sha256: null}
puzzle_id: "<stabile ID>"
revision: "<Paketrevision>"
repo_commit: "<vollständige tatsächlich gelesene SHA>"
state: brief_ready
brief: "<Datei mit Auftrag, Invarianten, Grenzen und Herkunft>"
approved_parameters: []
reveal: {file: null, sha256: null, approval: null}
motif: {file: null, sha256: null, derived_from_reveal_sha256: null, approval: null}
candidate: {bundle: null, variant: null, proof: null, verification: null, certification: null}
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

### Einheitliche Chatübergabe

Jede Phasenabschluss-, Korrektur-, Wiederaufnahme- oder Blockermeldung verwendet
genau diese Reihenfolge; kurze Arbeitsfortschrittsmeldungen benötigen keinen Datensatz:

1. **Ergebnis:** höchstens drei knappe Punkte zu Ergebnis, wesentlichen Änderungen
   und offenen Blockern. Die für die Freigabe nötigen echten Bilder und Datei-/PR-
   Links unmittelbar dabei zeigen; technische Details bleiben in den Paketbelegen.
2. **Sheet-Daten:** genau ein kopierbarer JSON-Block nach folgendem Format. Dieselben
   Bezeichnungen wie im Cheat-Sheet verwenden, alle Schlüssel ausgeben; unbekannte
   Werte sind `null`. Keine Platzhalter oder erfundenen Hashes. Dies ist eine
   Bedienhilfe aus den bestehenden Dateien, kein zusätzlicher Nachweisvertrag und
   keine eigene Pflichtdatei im ZIP. Der Import erteilt keine Freigabe.
3. **Nächster Schritt:** denselben Auftragsnamen wie im JSON nennen und in einem
   Satz die noch erforderliche menschliche Auswahl/Freigabe oder Blockerbehebung.
   Ohne echten Stopp bereits autorisierte Arbeiten selbst fortsetzen.

```json
{
  "format": "picross-cheatsheet-update-v1",
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
folgt weiterhin der echten Motivfreigabe. Bildfelder enthalten eindeutigen Pfad
und Dateirevision; bei noch offener Auswahl `null`. `Inventar-SHA-256` enthält nur
den 64-stelligen Hash des Originalinventars, keinen ZIP-, Matrix- oder Logikhash.
`Quellbranch / Commit` ist ein tatsächlich erreichbarer Paketstand, bevorzugt eine
volle Commit-SHA; ungesicherte lokale Arbeit als `null` plus Blocker berichten.
Der Paketstand ist vom Stand des zu lesenden Regelwerks zu unterscheiden.

`Nächster Schritt` verwendet genau einen dieser Namen: `1 · Abschlussbilder erzeugen`,
`2 · Bild freigeben & abstrahieren`, `3 · Motiv freigeben & produzieren`,
`4 · Abnehmen & ins Spiel integrieren`, `Korrigieren oder Fehler beheben`,
`Gespeicherte Arbeit fortsetzen`, `Merge freigeben` oder `Abgeschlossen`.
Nach bereits beauftragtem Integrationsmerge ist erst nach Abschnitt 9
`Abgeschlossen` zulässig. Dann auf den erhaltenen Integrationsdatensatz statt
auf gelöschte ZIPs verweisen, `Paketpfad` und entfernte Bild-/Parameterreferenzen
auf `null` setzen; Reveal und Runtime-Inhalte bleiben erreichbar.

## 8. Abgenommenes Paket ins Spiel integrieren

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

Paarprofilpakete verlangen die tatsächliche Regelwerksbindung 0.5.0, passende
`candidate.certification` und Schwierigkeit 0.2 mit den gebundenen Nachweisen.
ZA-1 erzeugt dafür `picross-target-inspection-v4` und `picross-target-export-v4`.
Diese Exportversion ist von den Versionen menschlicher Änderungsautorisierungen
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
4. Kategorie-ID im äußeren Record und in der aktuellen Kategorienquelle abgleichen. `export` mit Paket, Endfreigabe, Name, Runtime-Revision, Stem, Slot sowie `--category-id <id> --categories content/categories.json` in ein neues temporäres Ziel ausführen. Erfolgsbericht und `inspection.json` binden; kein zusätzlicher Routineaufruf von `verify-export`. Ein bereits passend gebundener kategorisierter Export darf direkt dem Plan dienen. Kategorienlose Altexporte neu kategorisiert exportieren. Autorisierte manuelle Ableitungen benötigen weiterhin den gesonderten ZA-1-Vertrag samt tatsächlicher Autorisierung. Linienprofile verwenden Direkt-/Reparaturexport v2 beziehungsweise manuellen Export v3; Paarprofile verwenden auch bei manuellen Ableitungen Export v4. Keine automatische Ausnahme und keine manuelle Änderung der Exportversion. Das freigegebene Abschlussbild bleibt der bytegebundene Reveal. Matrix, Hinweise und Assets nicht manuell umschreiben.
5. `plan --export <export> --checkout <arbeitscheckout> --difficulty <checked.json>` ausführen, Kategorie-ID/aktuellen Anzeigenamen, konkrete Add-/Replace-Pfade und Registryänderungen auf Scope, Kollisionen und unveränderte Bestandsinhalte prüfen. Der Integrationsauftrag erlaubt anschließend `register` mit denselben Eingängen; keine zusätzliche routinemäßige Bestätigung verlangen. Ohne Auftrag beim Plan stoppen. Kein handgeschriebener Registryeintrag als Ersatz.
   Bei ausdrücklich beauftragtem Ersatz einer bestehenden Fassung stattdessen
   `plan-update` → `update` mit demselben Erwartungshash der bisherigen Definition
   und `--difficulty <checked.json>` nach [ZA-1](../ZA1_ADAPTER.md) verwenden.
   Nur bei gleicher ID/Logik/Matrix ist `--rebind-difficulty` ohne Analyse zulässig.
   Höhere Runtime-Revision, neue Paketrevision;
   feste Identität/Slot/Kategorie und Revealbytes erhalten. Alte Saves bleiben
   unberührt und gelten bei anderer Runtime-Revision als inkompatibel.
6. Tatsächliche Definition/Reveal/Nutzungshinweise, `content/registry.json`, deren Runtime-Projektion und die Prüfkopie unter `content/packages/…` kontrollieren, einschließlich Kategorienprojektion und eindeutiger Zuordnung im Katalog. Identischer Wiederholungsaufruf darf `no-op` sein; Konflikte nicht überschreiben. Bei offenem Registrierungsjournal nur den dokumentierten Recoverypfad verwenden.
7. **Für reine Rätselinhalte genügt die Adapter-/Dateiprüfung aus 4–6.** Keine obligatorischen Godot-Spielstarts, Teilstand-/Neustart-, Undo-/Save-, Abschluss-/Album-, Render- oder Windows-/PCK-Tests je Rätsel; keinen Product-Harness und keinen Buildauftrag automatisch starten. Die visuelle Raster-/Abschlussbildprüfung gehört bereits zur Produktion. Nur bei konkretem Befund eine gezielte zusätzliche Probe mit benanntem Zweck ausführen, isoliert von echten Saves. Allgemeine Spiel-/Exportregressionen gehören zu relevanten Codeänderungen. Keine zusätzlich manuell gestarteten Bestands-Replays, `check-registry`-/`sync-runtime`-Vollprüfungen oder wiederholten `register`-Aufrufe zur Bestätigung; interne Adapterprüfungen unverändert lassen. Nicht ausgeführte native Prüfungen als `nicht erforderlich: reine Inhaltsintegration` vermerken, niemals als bestanden.
8. Arbeitsrecord mit einmaligen Registrierungs-/Prüfbelegen aktualisieren, vollständigen Diff separat selbst prüfen, committen/pushen und Draft-PR mit Head/Basis/Checks/offenen Gates erstellen. Reine Rätseldateien müssen im Auswahlbericht `content_only=true` ergeben; dann sind nur `docs` (Pfad-/Dateimodusprüfung) und `ci-required` Pflicht. Keine vollständige Testsuite zusätzlich lokal oder per CI wiederholen. Bei unerwartet breiter Auswahl die tatsächlich geänderten Pfade prüfen; notwendige Codeänderungen getrennt behandeln, nichts am Gate vorbeischleusen. Nur mit passender ausdrücklicher Mergefreigabe nach bestandenen Pflichtprüfungen mergen; danach tatsächlichen Main-/Mergecommit prüfen. Erst dann „im Spiel auf main integriert“ melden; kein Release/Deployment ableiten.

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
   bei Blocker genau diesen melden. Reine Datenbereinigung nutzt den schlanken
   Inhaltspfad, ohne Spielerbuild oder rätselspezifische Tests. Danach Main-Commit
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
verlangt keine erneute Rasterproduktion. Diese Ergänzung ist ein Sollvertrag;
eine passende CLI-Erweiterung ist damit noch nicht implementiert.

1. Für die abzuschließende Bildrevision tatsächliche Bildfreigaben, aktive Bildbindung
   und enthaltenen Main-Commit prüfen; offene neuere Arbeit derselben ID erhalten.
2. Nach abgeschlossener Integration die zugehörigen Bildarbeitsrevisionen einschließlich
   Quellen, Prompts, Varianten, ZIP-/Rohkopien und erledigter Authoringindexeinträge entfernen.
   Gebundene historische Verweise ersetzen dauerhafte Kopien der Arbeits- und Reviewdaten.
3. Aktuelle Bilddatei, Nutzungshinweise, Herkunfts-/Freigabemetadaten und aktive Bildrevision
   bleiben erhalten. Definitionsbytes, Runtime-Revision, Save-Slot, Registrierung und aktive
   Bewertungen bleiben unverändert. Ein bereits versiegelter ursprünglicher Integrationsbeleg
   wird weder neu erzeugt noch zur nachträglichen Bildfreigabe umgeschrieben.
4. Der künftige Abschlussweg muss vorhandene `picross-integrated-content-v1`-Datensätze
   ausdrücklich unterstützen. Der gegenwärtige `retire-production`-Pfad bricht dort mit
   `Production already retired` ab. Erneute Rasterproduktion, Wiederherstellung alter Pakete
   oder Umgehung der Bindungsprüfungen sind keine Ersatzlösung. Die konkrete CLI wird erst
   mit ihrer Implementierung dokumentiert.
5. Abnahme verwendet einen begrenzten Datei-/Referenzvergleich und den unveränderten
   aktiven Datenbestand. Kein Solver-, Bild-, Katalog- oder Spielerreplay allein für
   diese Bereinigung; aktive Leser und Rechtebindungen bleiben vorher geprüft.

Die frühere eng begrenzte Freigabe zum Nachintegrations-Cleanup einschließlich Merge
in Schritt 5 bleibt bestehen. Der aktuelle CI2-Spezifikationsauftrag führt selbst
weder Cleanup noch Implementierung oder Merge aus. Er erweitert die frühere Freigabe
nicht auf Werkzeug-/CI-Codepakete; deren Umsetzung und Merge benötigen ihren eigenen Auftrag.
