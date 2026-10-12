# Picross: Regeln für die KI-gestützte Rätselproduktion

**Version 0.4.1 · Dokumentrevision 4 · 12.10.2026**

Die kompatible ZA-1-Vertragsversion bleibt 0.4.1; Dokumentrevision, Datei-SHA-256 und Repositorycommit identifizieren diese ergänzte Arbeitsanweisung.

**Zielpfad:** `docs/ai-workflows/PUZZLE_AUTHORING.md` im Repository `venomenon328/picross`.

Diese Arbeitsanweisung regelt die Erstellung neuer Rätsel vom Motivauftrag über das zuerst freigegebene Abschlussbild bis zur geprüften Integration ins Spiel. **MUSS** bezeichnet eine Pflicht, **SOLL** den begründet abweichbaren Standard, **DARF** eine Option.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`.
2. Zu Beginn `content/categories.json`, `content/authoring/index.json` und den registrierten Fundus lesen. Kategorie aus dem Auftrag übernehmen oder nach dem prägenden Hauptgegenstand begründet redaktionell zuordnen; nur wesentliche Motivkonflikte klären. [Kategorienvertrag](../CATEGORIES.md) beachten. Kategorie in Briefing und äußerem Record führen; Mengenbalance ist keine Quote. Einschlägige aktuelle Eigentümerentscheidungen berücksichtigen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Beschluss, implementierte Funktion und eigene Annahme unterscheiden; offene PRs nicht als verfügbare Implementierung behandeln.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API einbauen. Produktionsaufträge mit Repositoryablage erlauben ausschließlich die beauftragte Paketsicherung samt Index; ein Integrationsauftrag erlaubt zusätzlich den Ablauf in Abschnitt 8. Werkzeugänderungen, Merge und Veröffentlichung sind jeweils getrennte Befugnisse nach Entwicklungsworkflow. Bereits erteilte passende Aufträge nicht erneut erfragen.
6. **Menschliches Probespielen ist optional und kein Freigabekriterium.** Ein großer Rätselbestand darf ohne Probespiele entstehen. Verpflichtend bleiben die Abschlussbildfreigabe, die Freigabe der daraus abgeleiteten Motivvorlage, die technische Prüfung und die abschließende redaktionelle Abnahme. Spätere Spielerfahrungen dienen der Verbesserung und Kalibrierung.

### Prüfungen gehören zur Produktion, nicht zur CI

- Sämtliche rätselbezogenen Prüfungen – Lösbarkeit, Eindeutigkeit, unabhängiger Proof, Herkunft, Reparatur, Gestaltung und Zielintegration – MUSS die KI für die jeweilige neue/geänderte Revision im Produktionsauftrag durchführen und dateigebunden belegen. Unveränderte, passend gebundene Nachweise wiederverwenden; erforderliche Neuprüfungen nach Abschnitt 4.4 bleiben Pflicht.
- **Keine rätselspezifischen Unit-Tests, Test-Snapshots, CI-Falllisten oder dauerhaften Replayjobs anlegen.** Ein neues Rätsel darf weder den allgemeinen Testbestand noch einen CI-Korpus erweitern. Prüfscripte für den konkreten Auftrag nur temporär außerhalb der Test-Discovery ausführen; Ergebnisse ins Paket, keine CI-Anbindung.
- Bei reinen Inhaltsänderungen den automatischen schlanken Inhaltspfad aus [CI_POLICY](../CI_POLICY.md) verwenden. Er prüft Änderungspfade und reguläre Dateimodi, keine Rätselqualität. Kein Solver/Proof-Replay, Unit-Testlauf, Godot-Start, Funktions-/Render-/Performancetest oder Spielerexport in dieser CI. Auch unveränderte Bestandsrätsel nicht erneut prüfen.
- Code-, Tool-, gemeinsame UI-/Asset- und CI-Änderungen sind separate Entwicklungsarbeit mit den passenden allgemeinen Regressionen an einem festen technischen Testbestand. Nicht zur vermeintlichen Absicherung eines neuen Rätsels Code ändern oder den CI-Umfang manuell auf `all` erweitern.

## 2. Abschlussbild zuerst, danach Abstraktion

### 2.1 Eingaben und Konfiguration

Zulässiger Input: Motivtext beliebiger Ausführlichkeit und/oder Ausgangsbild; optional ungefähre Breite × Höhe, Mono/Farbe und weitere Einschränkungen. Eine verlinkte oder angezeigte Bildvorschau ersetzt keine gespeicherte Quelldatei.

Die KI MUSS Hauptmotiv, unverzichtbare Merkmale, erlaubte Umgestaltung und Einschränkungen erfassen. Fehlende reversible Details sinnvoll ergänzen. Nur wesentliche offene Produktentscheidungen beim Nutzer erfragen, jeweils mit Empfehlung und Konsequenzen.

Der erste gestalterische Schritt ist immer die Erstellung mehrerer **farbiger, detaillierter Abschlussbilder** aus dem Input. Noch keine abstrahierte Motivvorlage, Zellmatrix oder Hinweise erzeugen. Fehlende Rastermaße oder ein offener Rätselmodus blockieren diese Bildauswahl nicht. Die spätere Darstellbarkeit bei der Komposition berücksichtigen, ohne das Abschlussbild vorzeitig auf Zellniveau zu vereinfachen. Auch ein eigenes Ausgangsbild ist zunächst Referenz und keine automatisch freigegebene Abschlussbilddatei.

Wenn Größe oder Farbmodus offen sind, nach der Abschlussbildfreigabe **2–3 konkrete Konfigurationen** vergleichen und eine empfehlen. Motivtreue, Darstellbarkeit, erwartetes Lösbarkeitsrisiko und Spielgefühl getrennt begründen. Auch ungefähre Wunschmaße dürfen hinterfragt werden; feste Grenzen nicht eigenmächtig überschreiten. Rechtecke gleichberechtigt berücksichtigen.

- Reguläre Rätsel: **Breite ≤ 50 und Höhe ≤ 50**. Ein weiter gefasstes technisches Werkzeuglimit ist keine Produktfreigabe.
- Klein (längste Achse ≤ 20): dominante Silhouette und wenige Binnenformen. Mittel (21–35): charakteristische Details und Negativflächen. Groß (36–50): gegliederte zusätzliche Details, keine bloße Vergrößerung. Diese Arbeitsklassen bestimmen keine Schwierigkeit.
- Für das Lösungsraster Mono oder gewöhnlich 2–4 Vordergrundfarben empfehlen; mehr Rasterfarben nur mit motivischem Nutzen und nachgewiesener Zielunterstützung. Das Abschlussbild bleibt auch bei einem monochromen Rätsel farbig; seine Farbigkeit und Detailtiefe sind nicht auf die Rasterpalette begrenzt.
- Größe, Seitenverhältnis und Palette müssen zum Motiv passen. Vor dem Nachweis keine Lösbarkeit versprechen.

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

## 3. Produktionsablauf und Zustände

| Phase / Zustand | Akteur und Arbeit | Ausgabe und Freigabebedingung | Fehlerpfad |
| --- | --- | --- | --- |
| `brief_ready` | KI liest Quellen, prüft Umgebung und erfasst den Input | Briefing, Quellen-/Toolstand, Plan für Abschlussbildvarianten | Fehlenden Zugang oder wesentliche Entscheidung klären |
| `reveal_review` | Bildfähige KI erzeugt farbige detaillierte Abschlussbilder; Mensch wählt/korrigiert | Tatsächliche Einzeldateien, Vergleich und Rechteangaben | Gezielte Abschlussbildrevision |
| `reveal_approved` | Mensch gibt genau eine Abschlussbildrevision ausdrücklich frei | Dateigebundene Referenz und geschützte Merkmale | Ohne Freigabe keine Abstraktion |
| `motif_review` | Bildfähige KI empfiehlt Rasterkonfiguration und abstrahiert die freigegebene Referenz | Gespeicherte Motivvorlage, Abschlussbildbezug und direkter Vergleich | Abstraktion korrigieren; bei nötiger Referenzänderung zurück zur Bildfreigabe |
| `motif_approved` | Mensch erteilt ausdrückliche Freigabe; KI protokolliert sie | Dateigebundene Abstraktionsfreigabe und Parameterkorridor | Ohne Freigabe keine Rasterproduktion |
| `raster_review` | Codex/werkzeugfähige KI importiert; deterministische Werkzeuge erzeugen Matrix, Hinweise und Nachweise | Variantenbündel, echte Rasteransichten, automatische und visuelle Befunde | Parameterkorrektur, begrenzte Reparatur oder neue Motivvorlage |
| `content_ready` | KI und Werkzeuge prüfen Endkandidat, Herkunft, Logik, Gestaltung, Schwierigkeit und Übereinstimmung mit dem freigegebenen Abschlussbild | Vollständiges Inhaltspaket ohne harte Mängel | Betroffene Prüfung/Phase wiederholen |
| `editorially_approved` | Mensch nimmt genau die vorgelegte Paketrevision redaktionell ab | Gebundene Endfreigabe; kein Probespiel erforderlich | Konkrete Korrektur mit passenden Rücksprüngen |
| `catalog_ready` | Codex prüft ZA-1-Export und Registrierungsplan | Schriftlicher Exportnachweis und konfliktfreier Plan | Endfreigabe/Quelle/Mapping korrigieren |
| `registered` | Codex registriert nach Integrationsauftrag im Arbeitsbranch | Runtimeassets, beide Registrydateien und Prüfkopie; einmalige Integrationsprüfung und schlanke Inhalts-CI gemäß Abschnitt 8 | Fehler beheben; bei unterbrochener Registrierung kontrollierte Recovery |

`blocked`, `rejected` und `superseded` benötigen einen konkreten Grund und eine betroffene Revision. `registered` bezeichnet zunächst den geprüften Checkout; erst der nachgewiesene Merge macht den Inhalt auf `main` verfügbar. Katalogfähigkeit, Checkoutregistrierung, Main-Integration und Release getrennt berichten. Fehlt ein passender Export, darf ein vollständig geprüftes Paket bei `editorially_approved` verbleiben; keine Pilot-ID für ein neues Rätsel wiederverwenden.

Freigaben enthalten Akteur, Zeitpunkt, tatsächliche Erklärung, Gegenstand und Hashbindung. Die KI darf menschliche Freigaben protokollieren, nicht selbst erteilen.

## 4. Rasterproduktion und technische Pflichtprüfung

### 4.1 Import und Rastervarianten

1. Von der **freigegebenen gespeicherten Motivvorlage** ausgehen; ihre Ableitung aus dem freigegebenen Abschlussbild anhand der Dateien, Hashes und dokumentierten Bearbeitung prüfen. Das Abschlussbild nicht als austauschbare nachträgliche Illustration behandeln. Originalbytes, SHA-256, Normalisierung, Rechte, Parameter und Toolversion erhalten. Die deterministische Reproduktion beginnt bei Bildbytes, nicht beim Prompt.
2. Striktes bestehendes Designformat verwenden; aktuelle Format-/Ressourcengrenzen der README einhalten. Redaktionelle Zusatzfelder in Begleitdateien speichern. Crop-Koordinaten und Seitenverhältnis beachten; nicht stillschweigend strecken.
3. Zunächst **vier gezielte Rasterkandidaten**, mit begründeter Zusatzhypothese höchstens sechs pro Runde erzeugen. Innerhalb der Motivfreigabe beispielsweise zwei Größen mit zwei sinnvollen Parametrierungen vergleichen. Keine blinde Kreuzprodukt-Suche.
4. Unterschiedliche globale Maße, Crops oder Paletten benötigen getrennte Designs. Beim vorhandenen farbigen `area`-Pfad ist der Schwellenwert wirkungslos; reine Schwellenvarianten sind dort keine unterschiedlichen Ansätze. Mono-Schwellen anhand des Bilds wählen.
5. Verfahren mit zwangsläufig leeren Außenkanten, insbesondere der entsprechend implementierte `contour`-Pfad, nicht unverändert als reguläres Ergebnis übernehmen. Standard ist ein mit der Randregel kompatibler Import, derzeit `area`.
6. Gleiche Raster durch exakten Vergleich von Maßen, Palette und Zellwerten erkennen. Kandidatenhashes binden auch Parameter und sind kein reiner Matrixvergleich. Alle Entstehungswege und Ablehnungsgründe erhalten.
7. Echte Raster als verlustfreie Kleinvorschau, vergrößert ohne Glättung und mit Gitter prüfen. Nicht automatisch den ersten logisch erfolgreichen Kandidaten auswählen.

### 4.2 Harte Kriterien

Ein freigabefähiger Kandidat MUSS sämtliche folgenden Bedingungen erfüllen:

- Gültige Maße, Zellwerte, Palette und Formate gemäß Projekt-/Zielvertrag; regulär höchstens 50 je Achse.
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

Ein vollständig gültiger deduktiver Nachweis belegt auch Eindeutigkeit. `stalled` belegt weder Mehrdeutigkeit noch Unlösbarkeit; `aborted` ist ein Abbruch. Exitcode 0 oder ein erzeugtes Importbündel allein ist keine Zertifizierung. Ein generiertes Zahlenbild oder eine KI-Erfolgsaussage ist niemals ein Nachweis.

Die Logik separat in einem frischen Prüferprozess verifizieren. Herkunft zusätzlich mit der vorhandenen Rekonstruktionsprüfung prüfen, beispielsweise `inspect_candidate` beziehungsweise Reparaturverifikation/passendem Export. Nur tatsächlich vorhandene Befehle/API-Funktionen verwenden. Zeit-/Zeilenbudgets je Befehl aus der README übernehmen; fehlgeschlagene Versuche nicht nachträglich umetikettieren.

### 4.3 Redaktionelle Kriterien

Flächennutzung, Hauptformen, Proportionen, Innenräume, isolierte Zellen, leere Innenzeilen/-spalten, Detaildichte und Farbunterscheidbarkeit prüfen. Ein Auge darf eine Einzelzelle sein; ein Henkel braucht einen Innenraum. Leere Innenstreifen nicht mechanisch entfernen.

Belegungsanteile unter 15 % oder über 85 %, isolierte Einzelzellen und vollständig leere Innenlinien **nur als Prüfanlass** markieren. Das sind redaktionelle Warnschwellen, keine harten Qualitätsgrenzen. Abweichungen sind bei motivischem Nutzen zulässig und kurz zu begründen. Nicht zugunsten einer Kennzahl Form oder Erkennbarkeit verschlechtern. Farben auch in kleiner Darstellung und, soweit verfügbar, mit Farbsinnsimulation kontrollieren; keine unbeschlossene Farbmetrik als Pflichtgrenze ausgeben.

### 4.4 Reparaturen und Änderungen

Reparatur nur an visuell tragfähigen Kandidaten und mit vorab gespeichertem bestehenden Reparaturplan: Referenz, Schutzmaske, Operatoren, Seed und Budgets. Wichtige gefüllte **und leere** Positionen schützen. Erster Versuch standardmäßig höchstens zwei Zellpositionen ändern, bei empfindlichen Motiven weniger. Höhere Grenzen brauchen vorab eine motivbezogene Begründung; keine nachträgliche Budgetlockerung.

Referenz, Ergebnis und markierten Zell-Diff vergleichen. `found` allein genügt nicht: Endnachweis, unabhängige Prüfung, Replay und redaktionelle Bewertung sind erforderlich. Bei schlechter Ausgangsform zuerst Abstraktion/Größe/Rasterpalette korrigieren; die freigegebene Abschlussbildreferenz dabei erhalten.

| Änderung | Erforderliche Wiederholung |
| --- | --- |
| Zellwert oder Rastermaß, auch nur eine Zelle | Neue Revision, Hinweise, vollständiger Logiknachweis, unabhängige Prüfung und Rasterbewertung |
| Quelle, Crop, Palette oder Importparameter | Neuer gebundener Import und vollständige Prüfung |
| Materielle Motivänderung | Zusätzlich erneute ausdrückliche menschliche Motivfreigabe |
| Abschlussbild geändert | Neue Bildrevision und menschliche Abschlussbildfreigabe; Ableitung, Motiv-/Rasterkonsistenz und Endabnahme erneut prüfen. Materielle Änderungen setzen abhängige Motivfreigaben zurück. Kein neuer Logiklauf allein für eine Bildänderung bei nachweislich unverändertem Raster/Logikeingang; nötige Rasteränderungen vollständig neu nachweisen |
| Nur Schwierigkeit/Kategorie/Metadaten | Keine neue Bild-/Rasterproduktion und keine neue Bild-/Endfreigabe allein wegen Kategorieänderung. Metadaten bei versiegelten Paketen außen ergänzen, neue Exportbindung separat aufzeichnen. Bewertungs-/Metadatenrevision; unveränderte Matrix-/Nachweisbindung erhalten |

Materiell sind Änderungen an Identität, Pose, charakteristischen Proportionen, wichtigen Innenräumen, Gesichtszügen oder ausdrücklich geschützten Merkmalen. Eine einzelne Zelle kann materiell sein. Auch das Abschneiden ausschließlich leerer Außenlinien verändert das Rastermaß und benötigt neue Nachweise. Manuelle Ableitungen offen kennzeichnen, nicht als unveränderten Originalimport ausgeben.

## 5. Schwierigkeit L1–L5

**Logische Schwierigkeit, Rastergröße, Bearbeitungsumfang und Lösungszeit getrennt angeben.** Große Matrizen oder viele Eingaben sind nicht automatisch schwierig. Sterne-/Fehlerbewertung im Spiel bleibt unabhängig.

Bewertungsmethode `picross-difficulty-0.1` verwenden. Den Lösungsverlauf anhand von Hinweisen und jeweiligem Wissensstand beurteilen, ohne versteckte Lösung als Schlussgrund. Das vollständige Solverprofil beweist Lösbarkeit, nicht die Notwendigkeit seiner stärksten Technik.

| Technik | Bedeutung |
| --- | --- |
| R0 | Direkte Voll-/Leerbelegung, vollständige Packung, Restleerfelder nach eindeutig abgeschlossenen Blöcken |
| R1 | Überlappungen sowie Grenzen/Verlängerungen eindeutig zugeordneter Blöcke |
| R2 | Kombinierte Zuordnung mehrerer Blöcke/Segmente; mehrere Anker, Trennungen oder Farbregeln zusammenführen |
| R3 | Allgemeine vollständige Zeilenunterstützung, komplexe Alternativen und partielle Farbdomänen, soweit nicht durch R0–R2 erklärt |

| Stufe | Einstufungskriterium |
| --- | --- |
| **L1 – sehr leicht** | R0 reicht vollständig. |
| **L2 – leicht** | R1 erforderlich, R0+R1 reichen. |
| **L3 – mittel** | R2 erforderlich und ausreichend; keine definierte Engstelle beobachtet. |
| **L4 – schwer** | R2 mit Engstelle oder R3 ohne Engstelle. |
| **L5 – sehr schwer** | R3 mit Engstelle. |

**Vorläufige Engstellendefinition:** mindestens drei aufeinanderfolgende informative R2/R3-Schritte; jeweils höchstens zwei produktive Linien und höchstens vier Zellen mit Domänenänderung pro Schritt. Ein Schritt ist eine Regelanwendung an einer Linie einschließlich ihrer begründeten Änderungen. Restaufräumen ignorieren, sobald höchstens `max(5, ceil(0.02 × W × H))` Zellen mehrdeutig bleiben. Die Schwellen gehören zur Methodenversion, nicht zum mathematischen Lösbarkeitsvertrag.

Vorgehen:

1. Stärkste belegte Technik und typische Engstellen anhand eines nachvollziehbaren Lösungsverlaufs bestimmen. Gleichzeitig mögliche Fortschritte und deren räumliche Verteilung berücksichtigen; aus einem sequentiellen Proof nicht ungeprüft auf fehlende Alternativen schließen.
2. Hinweisstruktur und Farbabhängigkeiten dokumentieren. Farbzahl, Schrittzahl, Laufzeit und Zellzahl dürfen die Stufe nicht allein erhöhen. Lange einfache Fortschrittsketten bleiben einfach.
3. Ohne validierten Bewertungsanalysator `editorial_estimate` verwenden: Hauptstufe, plausiblen Bereich, konkrete Begründung und Vertrauen angeben. Eine begründete KI-Einstufung **genügt ohne menschliches Probespiel**. Nicht erschöpfend geprüfte Techniknotwendigkeit/Engstellen als unsicher kennzeichnen.
4. `instrumented` nur bei tatsächlich vorhandener geprüfter Instrumentierung verwenden. Diese muss schwächere Regelfamilien bis zum Fixpunkt testen, Fortschrittsmöglichkeiten erfassen und einen festgelegten Bewertungsweg verwenden. Keine solche Fähigkeit erfinden.
5. Vertrauen: `low` bei KI-Schätzung/ungeklärten Technikgrenzen; `medium` bei vollständig überprüfter Bewertung ohne belastbare menschliche Kalibrierung; `high` erst mit validierter Methode und passenden Vergleichsdaten. Geringes Vertrauen oder fehlende Kalibrierung ist kein Abnahmeblocker; eine unbegründete Stufenzahl ist unvollständig.
6. Lösungszeit ohne belastbare Daten als `null`/„nicht geschätzt“ ausgeben. Optionale spätere Versuche mit Erfahrungsgruppe, aktiver Zeit, Hilfen, Abbruch und getrennten Urteilen zu Logik/Arbeitsumfang erfassen. Darauf Methode und Zeitprognosen versioniert kalibrieren; Produktion nicht auf diesen Datensatz warten lassen.

Stagniert das zulässige technische Vollprofil, ist das Rätsel nicht freigabefähig; es bekommt keine zusätzliche Schwierigkeitsstufe. Neue Bewertungen bei unverändertem Raster benötigen keinen neuen Logiknachweis.

## 6. Dateien, Übergabe und Wiederaufnahme

### 6.1 Repositoryablage und schlanke Pakete

- Zuerst `content/authoring/index.json` und die Runtime-Registry `content/registry.json` lesen. Stabile motivneutrale ID gemäß ZA-1 vergeben; ID, Revision und Pfad auf Kollision prüfen. Bei Wiederaufnahme das verzeichnete Paket am angegebenen Branch/Commit selbst laden; keinen erneuten Upload verlangen, wenn die Bytes zugänglich sind. Mehrdeutige Auswahl klären, fehlenden Binärzugriff konkret melden.
- Ablage: `content/authoring/<puzzle_id>/<revision>/package.zip`. Daneben `handoff.json` als bytegleiche lesbare Kopie, `record.json` und gegebenenfalls die separate `approval.json`. Ein Paket pro Phasenübergabe, Freigabevorlage oder Chatwechsel; keine ZIPs nach jedem Toolaufruf. Bereits vorgelegte Revisionen niemals überschreiben. Neue Inhalte erhalten eine neue Revision; identische Bytes werden wiederverwendet.
- `content/authoring/index.json` ist der von der KI gepflegte Arbeitsindex, **keine Runtime-Registry**. Pro ID/Revision: relativer Recordpfad. `record.json` führt zusätzlich `category_id`, sobald die Motivzuordnung feststeht (bei offenem Briefing ausdrücklich `null`; alte Records ohne Feld bleiben lesbar). Spätestens vor kategorisiertem Export ist eine gültige Zuordnung Pflicht. `record.json` führt Format `picross-authoring-record-v1`, ID/Revision, Phasenstatus, Paketpfad/-größe/-SHA-256, Handoffpfad/-SHA-256, Inventarhash (oder ausdrücklich noch offen), Abschlussfreigabepfad/-hash oder `null`, Maße/Modus/Schwierigkeit soweit bekannt, Blocker, nächsten erlaubten Schritt und Integrationsbeleg oder `null`. Branch/Commit der Sicherung in der Übergabe nennen; noch nicht gemergte Ablage nicht als `main` ausgeben. Paket, Handoffkopie und Index gemeinsam committen/pushen, sobald dieser Umfang beauftragt ist; Merge gemäß Entwicklungsworkflow.
- UTF-8-Markdown/JSON, bestehende Matrix-/Proofverträge und verlustfreie Bilder verwenden. Quellenbytes, Herkunft/Nutzungsgrundlage, tatsächliche Bildprompts/-einstellungen (`not_exposed` wenn unbekannt), ausgewählte Bilder, Freigaben, Parameter und Nachweise behalten. Ungeklärte Nutzungsrechte blockieren die Katalogfreigabe. Versuchshypothese, Auswahl-/Ablehnungsgrund, Bildaufrufe, Überarbeitungsrunden, Import-/Reparaturversuche und aktive Menschenminuten getrennt erfassen; unbekannte Werte als `null` führen.
- Vor einer Auswahl alle noch angebotenen Bildvarianten behalten. Nach der Auswahl verworfene ungebundene Bildvarianten nur in ihrer früheren Repositoryrevision belassen; im aktuellen Paket reichen Entscheidung, Hash und genauer früherer Fundort. Keine alten ZIPs in neue ZIPs einbetten. Allgemeine Projekt-/Workflowdokumente und Toolquellen über Repositorycommit/Pfad referenzieren, nicht pro Rätsel kopieren. Ausnahme: den von ZA-1 verlangten, hashgebundenen Regelwerks-Snapshot mitführen.
- Vollständige erforderliche RP-3-/RP-5-Bündel unverändert behalten: Original-/Normalisierungsbild, Design, sämtliche manifestgebundenen Kandidaten, Eltern, Masken, Logik, Proofs und Vergleichsdateien. Auch HTML oder ein verworfener Kandidat ist Pflicht, wenn ein Manifest/Replay ihn bindet. Finale echte Rasteransicht, Bildvergleich, Schwierigkeit, Qualitätsbericht und Belege aller Freigaben/Gates behalten.
- Ungebundene doppelte Berichte, stdout/stderr-Kopien, eingebettete Bildgalerien, temporäre Ansichten, Caches und vollständige Chat-/Repoarchive weglassen. Relevante Fehlversuche als kurze strukturierte Einträge erhalten. Dateien nicht allein anhand der Endung löschen; alle benötigten technischen **und redaktionellen** Referenzen nachverfolgen. HTML/Code aus Paketen nicht ausführen.
- Ein neues Paket vor Inventarisierung verschlanken. Bereits versiegelte Pakete ausschließlich als deklarierte Teilkopie nach `picross-authoring-derivation-v1` ableiten: Originalhandoff/-inventar und ihre Hashes unverändert, Original-ZIP-Hash binden, tatsächlich enthaltene Dateien vollständig hashen. Weglassungen und Grund im äußeren Record dokumentieren. Keine erfundene neue Vollkopie, keine stillschweigende Neuversiegelung oder Umschreibung alter Freigaben. Nachweisbündel nicht intern kürzen. Das Original nicht destruktiv ersetzen.
- Inventar und Handoff ohne Selbstreferenz nach ZA-1 binden; Datei-SHA-256 und kanonische Vertrags-Hashes unterscheiden. Nach Versiegelung spätere Endfreigabe und Integrationsstatus ausschließlich in separater Freigabe/Record führen; das Originalhandoff dafür nicht ändern.
- Vor Ablage ZIP sicher öffnen, Dateimenge/Hashes und Handoffkopie prüfen. Ab `content_ready` zusätzlich ZA-1 `inspect` auf dem **geschriebenen ZIP** ausführen; fehlende Endabnahme darf als einziger entsprechender Blocker bleiben. Frühere Bildphasen sind noch kein ZA-1-Eingang: deren vorhandene Dateibindungen/Freigaben prüfen, keine Adapterzertifizierung behaupten. Für das Packen gibt es derzeit keinen eigenen CLI-Befehl; Standard-ZIP-Werkzeuge und vorhandene APIs benutzen, keinen Befehl erfinden.
- `content/authoring/` bleibt außerhalb des Spiels. Nach Integration erzeugt ZA-1 die offline prüfbare Kopie unter `content/packages/<id>/<revision>/`; dieser Ort ist kein manuell zu befüllender Eingang. Keine zusätzlichen Voll-ZIPs dort erzeugen. Alte Produktionsstände über feste Git-Commits referenzieren; keine automatischen Löschungen, LFS-Umstellung oder Historienbereinigung. Größenwachstum messen, nicht durch Weglassen von Proofs lösen.

### 6.2 Übergabedatensatz

Die KI MUSS einen aktuellen Übergabedatensatz in diesem Begleitformat führen. Er ersetzt keine Werkzeugeingabe. Platzhalter/`null` sind keine Nachweise. Im Paket bleiben alle Pfade relativ; technische Prüfinputs müssen darin vollständig vorliegen. Der äußere Repositoryrecord verwendet repositoryrelative Pfade. Historische Vergleichsreferenzen dürfen auf genaue frühere Commits zeigen; sie ersetzen keinen Replayinput.

```yaml
format: picross-authoring-handoff-v2
rulebook: {version: "0.4.1", file: "<Regelwerk>", sha256: null}
puzzle_id: "<stabile ID>"
revision: "<Paketrevision>"
repo_commit: "<vollständige tatsächlich gelesene SHA>"
state: brief_ready
brief: "<Datei mit Auftrag, Invarianten, Grenzen und Herkunft>"
approved_parameters: []
reveal: {file: null, sha256: null, approval: null}
motif: {file: null, sha256: null, derived_from_reveal_sha256: null, approval: null}
candidate: {bundle: null, variant: null, proof: null, verification: null}
origin_verification: null
repair: {reference: null, plan: null, replay: null}
inventory: {file: null, sha256: null}
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
- Ergebnisse und Dateibelege für Produktmaße, Randregel, Herkunft, Hinweise, vollständigen Nachweis unter benanntem Profil, unabhängige Prüfung und Endmatrixgleichheit.
- Schwierigkeit L1–L5, plausiblen Bereich, Methode, Vertrauen und Technik-/Engstellenbegründung; getrennt Bearbeitungsumfang und belastbare Zeitdaten oder „nicht geschätzt“.
- Nutzungsgrundlage, tatsächlichen Zieladapter-/Exportstatus, KI-Durchläufe und aktive Menschenzeit oder „nicht erfasst“.
- Offene Blocker und nächsten erlaubten Schritt. Vorhandene menschliche Spieldaten optional ergänzen; ihr Fehlen ist kein Blocker.

Keine Ergebnis- oder Freigabefelder ohne Beleg als erfüllt ausgeben. Inhaltsfreigabe, Katalogfähigkeit und tatsächliche Integration getrennt halten. Ein unpassender oder fehlender Exportadapter darf nicht durch Umwidmung bestehender Pilotdefinitionen ersetzt werden.

## 8. Abgenommenes Paket ins Spiel integrieren

Voraussetzungen: tatsächlicher Integrationsauftrag, unverändertes `content_ready`-Paket mit vollständigen Inhaltsgates und gesonderte menschliche Endfreigabe nach [ZA-1](../ZA1_ADAPTER.md). Die Freigabe bindet Originalhandoff, Inventar, Endkandidat, Matrix-/Logikhash und Abschlussbild; ein `pass`-Flag genügt nicht. Die Archivablage selbst erteilt keine Endabnahme. Probespielen bleibt optional.

Codex MUSS den aktuellen Entwicklungsworkflow und ZA-1 vollständig lesen und dann:

1. Paket über `content/authoring/index.json` laden; ZIP-, Handoff-, Inventar- und Freigabebindung kontrollieren. Aktuellen `main` und vorhandene Arbeit prüfen, isolierten Arbeitsbranch verwenden. Keine fremden Änderungen aufnehmen.
2. Mit ZA-1 `inspect --input <paket> --approval <freigabe> --report <neue-datei>` frisch prüfen. Nur `technical=true` und `editorial_approved=true` erlauben den nächsten Schritt. Historische Adapterblocker im Original als historisch behandeln; aktuelle Ergebnisse im äußeren Record führen, Original nicht ändern.
3. Produktions-ID unverändert als Runtime-ID verwenden. Motivname, kollisionsfreien Dateistamm/Save-Slot und numerische Runtime-Revision explizit wählen; bei neuen IDs gewöhnlich Revision 1. F01…F09 nicht umwidmen. ZA-1 unterstützt 1…50 pro Achse, Rechtecke, Mono und höchstens vier Vordergrundfarben; Paketrevision und Runtime-Revision bleiben getrennt.
4. Kategorie-ID im äußeren Record und in der aktuellen Kategorienquelle abgleichen. `export` mit Paket, Endfreigabe, Name, Runtime-Revision, Stem, Slot sowie `--category-id <id> --categories content/categories.json` in ein neues temporäres Ziel ausführen; danach `verify-export` auf dem neuen v2-Manifest samt gehashtem Kategorien-Snapshot. Kategorienlose Altexporte sind nur technisch prüfbar; für eine neue Integration kategorisiert aus demselben unveränderten freigegebenen Paket neu exportieren. Das zuerst freigegebene Abschlussbild bleibt der bytegebundene Reveal. Kein manuelles Umschreiben von Matrix, Hinweisen oder Assets.
5. `plan --export <export> --checkout <arbeitscheckout>` ausführen, Kategorie-ID/aktuellen Anzeigenamen, konkrete Add-/Replace-Pfade und Registryänderungen auf Scope, Kollisionen und unveränderte Bestandsinhalte prüfen. Der Integrationsauftrag erlaubt anschließend `register` mit denselben Eingängen; keine zusätzliche routinemäßige Bestätigung verlangen. Ohne Auftrag beim Plan stoppen. Kein handgeschriebener Registryeintrag als Ersatz.
6. Tatsächliche Definition/Reveal/Nutzungshinweise, `content/registry.json`, deren Runtime-Projektion und die Prüfkopie unter `content/packages/…` kontrollieren, einschließlich Kategorienprojektion und eindeutiger Zuordnung im Katalog. Identischer Wiederholungsaufruf darf `no-op` sein; Konflikte nicht überschreiben. Bei offenem Registrierungsjournal nur den dokumentierten Recoverypfad verwenden.
7. Als Abschluss dieses Produktionsauftrags **dieses neue Rätsel einmalig außerhalb der CI** im isolierten regulären Spiel prüfen: Auswahl/Größe, proportionaler Raster- und Bildaufbau, eigener Teilstand und Neustart, Abschluss/Album sowie Motivverdeckung vor Abschluss. Keine echten Saves verwenden. Den für diese Produktion tatsächlich erzeugten Spielerexport/PCK-Inhalt einmalig außerhalb der CI kontrollieren: Runtimeassets/Nutzungshinweise enthalten, Produktionspakete/Proofs/Freigaben ausgeschlossen. Bereits passend an unveränderte Dateien gebundene Integrationsbelege wiederverwenden. Ergebnisse im äußeren Record verlinken; keinen rätselspezifischen Unit-/CI-Test einchecken. Native Sichtprüfung ist keine verpflichtende menschliche Komplettlösung.
8. Arbeitsrecord mit einmaligen Registrierungs-/Prüfbelegen aktualisieren, vollständigen Diff separat selbst prüfen, committen/pushen und Draft-PR mit Head/Basis/Checks/offenen Gates erstellen. Reine Rätseldateien müssen im Auswahlbericht `content_only=true` ergeben; dann sind nur `docs` (Pfad-/Dateimodusprüfung) und `ci-required` Pflicht. Keine vollständige Testsuite zusätzlich lokal oder per CI wiederholen. Bei unerwartet breiter Auswahl die tatsächlich geänderten Pfade prüfen; notwendige Codeänderungen getrennt behandeln, nichts am Gate vorbeischleusen. Nur mit passender ausdrücklicher Mergefreigabe nach bestandenen Pflichtprüfungen mergen; danach tatsächlichen Main-/Mergecommit prüfen. Erst dann „im Spiel auf main integriert“ melden; kein Release/Deployment ableiten.

Das Endergebnis nennt Paketfundort/-hash, Freigabebeleg, Runtime-ID/Revision/Slot, Registrierung, konkrete Produktprüfung, PR/Head und gegebenenfalls Main-Mergecommit. Bei Fehlern den letzten belegten Zustand und nächsten erlaubten Schritt nennen; keine unvollständige Integration als Erfolg melden.
