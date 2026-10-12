# Picross: Regeln für die KI-gestützte Rätselproduktion

**Version 0.4.1 · 12.10.2026**
**Zielpfad:** `docs/ai-workflows/PUZZLE_AUTHORING.md` im Repository `venomenon328/picross`.

Diese Arbeitsanweisung regelt die Erstellung neuer Rätsel vom Motivauftrag über das zuerst freigegebene Abschlussbild bis zum katalogfähigen Paket. **MUSS** bezeichnet eine Pflicht, **SOLL** den begründet abweichbaren Standard, **DARF** eine Option.

## 1. Einstieg und Befugnisse

1. Aktuelle `AGENTS.md` tatsächlich abrufen und deren Pflichtquellen einschließlich Workflow und Projektprofil lesen. Außerdem vollständig lesen: `docs/PRODUCT_DEFINITION.md`, `docs/DESIGN_CONCEPT.md`, `docs/PUZZLE_PRODUCTION.md` und `tools/puzzle_production/README.md`.
2. Einschlägige aktuelle Eigentümerentscheidungen berücksichtigen. Repository-/Toolstand mit vollständiger Commit-SHA binden. Beschluss, implementierte Funktion und eigene Annahme unterscheiden; offene PRs nicht als verfügbare Implementierung behandeln.
3. Bestehende technische Formate, Farbregeln, Solverprofile, Nachweise und Reparaturverträge verwenden. Dieses Regelwerk ersetzt sie nicht. Fehlende Pflichtquellen oder widersprüchliche Vorgaben vor dem betroffenen Schritt klären.
4. Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine Funktionen, Prüfungen oder Ergebnisse behaupten, die nicht verfügbar beziehungsweise ausgeführt sind.
5. Keine direkte Modell-API in das Produktionswerkzeug einbauen. Werkzeugänderungen, Repository-Schreibaktionen und Veröffentlichung benötigen einen entsprechenden separaten Auftrag.
6. **Menschliches Probespielen ist optional und kein Freigabekriterium.** Ein großer Rätselbestand darf ohne Probespiele entstehen. Verpflichtend bleiben die Abschlussbildfreigabe, die Freigabe der daraus abgeleiteten Motivvorlage, die technische Prüfung und die abschließende redaktionelle Abnahme. Spätere Spielerfahrungen dienen der Verbesserung und Kalibrierung.

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
| `catalog_ready` | Codex/Werkzeug validiert einen tatsächlich passenden Export und Katalogdatensatz | Eindeutige ID, gültige Zielassets und Metadaten | Fehlenden Adapter als Blocker ausweisen |

`blocked`, `rejected` und `superseded` benötigen einen konkreten Grund und eine betroffene Revision. Katalogfähigkeit ist keine bereits erfolgte Integration oder Veröffentlichung. Fehlt ein passender Export, darf ein vollständig geprüftes Paket bei `editorially_approved` verbleiben; keine Pilot-ID für ein neues Rätsel wiederverwenden.

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
| Nur Schwierigkeit/Metadaten | Bewertungs-/Metadatenrevision; unveränderte Matrix-/Nachweisbindung erhalten |

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

### 6.1 Ablagepflichten

- Stabile motivneutrale ID vergeben, etwa `pz-000001`; im gemeinsamen Index auf Kollision prüfen. Runtime-IDs nach tatsächlichem Zielvertrag vergeben.
- Pro ID Briefing, Originalquellen, Abschlussbildvarianten samt freigegebener Referenz, abgeleitete Motivvorlagen, unveränderte Import-/Reparaturbündel und Reviews getrennt ablegen. Konkrete Revisionen verwenden, keine Freigabe nur auf „latest“ beziehen; vorgelegte Revisionen nicht überschreiben.
- Produktionsdateien dauerhaft verfügbar halten. Der gemeinsame Index enthält ID, Revision, Maße, Modus, Schwierigkeit, Status, Blocker und Paketort. Technische Spoilerarchive nicht ungewollt in Spieleransichten ausliefern; Produktvertrag zur Motivverdeckung beachten.
- UTF-8-Markdown/JSON für Begleitdaten, bestehende JSON-Verträge für Matrix/Hinweise/Proof, verlustfreies Raster-PNG und zielkompatibles Reveal verwenden. Keine konkurrierenden technischen Formate erfinden.
- Herkunft, Urheber soweit bekannt, Nutzungsgrundlage und Belege pro Quelle erfassen. Ungeklärte Rechte blockieren die Freigabe zur vorgesehenen Katalognutzung. Bei KI-Bildern Prompt, Referenzen, Datum, Oberfläche und tatsächlich bekannte Einstellungen speichern; verborgene Modellwerte als `not_exposed` führen.
- Tatsächliche Datei-SHA-256 im Inventar erfassen; kanonische Vertrags-Hashes separat erhalten. Kein selbstreferenzieller Hash: Inventar bindet Nutz-/Nachweisdateien, Freigabe bindet dieses Inventar.
- Jeden Versuch mit Hypothese, Parametern, Ergebnis und Annahme-/Ablehnungsgrund erfassen. Bildaufrufe, Überarbeitungsrunden, Import-/Reparaturversuche sowie aktive Menschenminuten getrennt zählen; unbekannt ist `null`, nicht `0`.

### 6.2 Übergabedatensatz

Die KI MUSS einen aktuellen Übergabedatensatz in diesem Begleitformat führen. Er ersetzt keine Werkzeugeingabe. Platzhalter/`null` sind keine Nachweise. Alle Pfade relativ zum Paket; benötigte Dateien müssen tatsächlich mitgeliefert oder dauerhaft auflösbar sein.

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

Nach Chatwechsel zuerst Regelwerk, Übergabe, Pflichtquellen, Freigaben und referenzierte Dateien lesen; Hashes prüfen. Nur den nächsten autorisierten Schritt fortsetzen. Fehlenden Gesprächskontext nicht erfinden, gültige Freigaben nicht unnötig erneut einholen und den Toolstand nicht heimlich wechseln.

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

## 8. Regulärer Zieladapter ZA-1

Der [ZA-1-Vertrag](../ZA1_ADAPTER.md) verarbeitet Authoring-v2 mit diesem Regelwerk
oder unverändertem 0.4.0-Eingang. Er unterstützt 1…50 Zellen pro Achse, Rechtecke,
Mono und höchstens vier Vordergrundfarben. Neue Runtime-IDs übernehmen die
motivneutrale Produktions-ID. Dateistamm, Save-Slot, Motivname und numerische
Runtime-Revision sind explizit; Paketrevision und Runtime-Revision bleiben getrennt.
Technische Bindungen und `gate_evidence` gemäß Adaptervertrag führen, nichts aus
Fließtext erraten.

Finale Freigabe kann getrennt vorliegen. Sie bindet Originalinventar und
Originalhandoff, Endkandidat, Matrix-/Logikhash und Abschlussbild, dazu Akteur,
UTC-Zeit und tatsächliche Erklärung. Das Original bleibt unverändert. Ein
`pass`-Flag ersetzt keine Erklärung. Fehlende Endabnahme erlaubt Diagnose,
verhindert Export/Registrierung. Eine Adapterlieferung ist keine Inhaltsabnahme.
