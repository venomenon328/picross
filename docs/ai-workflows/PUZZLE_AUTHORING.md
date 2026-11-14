# Picross: Regeln für die KI-gestützte Rätselproduktion

**Version 0.8.0 · Dokumentrevision 6 · 13.11.2026 · PW2-A / PW2-B**

Neue Produktionen verwenden fünf Schritte: Abschlussbilder → Motivvorlage →
Rasterangebote → Kontextzeichnungen → Integration. Hintergrundarbeit beginnt
erst nach der tatsächlichen Wahl eines vollständig qualifizierten Rasters.
In Schritten 1–3 keine Hintergrundangebote, Briefings oder vorgezogenen
Hintergrundblocker erzeugen. Der [0.7-Vorschausnapshot](PUZZLE_AUTHORING_0_7_0_PREVIEW.md)
ist historisch. Bereits integrierte Inhalte, Saves, versiegelte Originale und
ihre Freigaben bleiben unverändert. Keine Alt-WIP-Migration und keine
Werkzeugentwicklung durch einen normalen Produktionsauftrag.

## 1. Einstieg und Befugnisse

### 1.1 Pflichtquellen nach Phase

Zuerst den Produktionseinstieg der aktuellen [AGENTS.md](../../AGENTS.md), diesen
Abschnitt 1 und den vollständigen [gemeinsamen Bildstil](../PUZZLE_IMAGE_STYLE.md)
lesen. Danach nur die folgende Zeile für die tatsächlich beauftragte Phase.
Abschnittsangaben verlangen den genannten Abschnitt, nicht die ganze Datei.
Herkunfts-/Querverweise darin sind keine rekursive Volllektüreplicht. Vor einer
konkreten technischen Operation zusätzlich ihren unten benannten Vertrag lesen;
benötigte Felder, Grenzen und Prüfungen niemals aus einem Kurztext erraten.

| Auftrag | Operative Pflichtlektüre zusätzlich zum gemeinsamen Kern |
| --- | --- |
| 1 · Abschlussbilder | §§2.1–2.4; Qualität §2 und §3.1; Transparenz §2. Vor Veröffentlichung §§6.1–6.2 und §7. |
| 2 · Motivvorlage | §§2.1–2.4; Qualität §2 und §3.2 sowie H-03/H-04 aus §4. Vor Veröffentlichung §§6.1–6.2 und §7. |
| 3 · Rasterangebote | §§4.1–4.5 und §5.2; Qualität §§2–4, §5 bei fehlendem qualifiziertem Kandidaten, §6 nur bei konkreter redaktioneller Ausnahme; bei Farbe zusätzlich §8. Vor Veröffentlichung §§6.1–6.2 und §7. |
| 4 · Hintergrund | §6.3; Qualität §2 und §9.1; Hintergrundvertrag §3 für Arbeitsmanifest/Entscheidung. Vor Veröffentlichung §§6.1–6.2 und §7. HP-W2 §4 erst bei tatsächlich anstehender Ableitung/Prüfung des ausgewählten Bilds. |
| 5 · Abschluss/Integration | §§6–9; die in §8 für die tatsächliche Operation gerouteten Integrations-/Zielverträge. Bereits passende Bild-/Rasterbelege prüfen, nicht deren Produktion wiederholen. |
| Bild-/Rasterkorrektur | §4.4 und die betroffene Phase oben. Nur abhängige Entscheidungen erneuern; für integrierte Bildrevisionen zusätzlich deren eigenen Ziel-/Abschlussweg in §§8–9. |
| Wiederaufnahme | §§6.1–6.2 und §7, aktuelle tatsächliche Phase oben; bei geänderten Bytes zusätzlich §4.4. Verbrauchte Budgets und gültige Entscheidungen aus dem gebundenen Stand fortführen. |

Die Tabellenbegriffe meinen [Qualität](../PUZZLE_QUALITY.md),
[Transparenz](../REVEAL_TRANSPARENCY.md) und
[Hintergrundvertrag](../PUZZLE_BACKGROUNDS.md). Ihre Kriterien und technischen
Invarianten gelten weiter; nur die Lesereihenfolge ist phasengerecht.
[Produktdefinition](../PRODUCT_DEFINITION.md), [Gestaltung](../DESIGN_CONCEPT.md),
[Produktion](../PUZZLE_PRODUCTION.md), [PW](../PRODUCTION_WORKSPACE.md) und die
[Tool-README](../../tools/puzzle_production/README.md) sind für normale Produktion
keine zusätzlichen pauschalen Gesamthandbücher. Technische Detaillektüre entsteht
nur durch eine tatsächlich verwendete Operation:

| Operation | Vor Ausführung benötigte Referenz |
| --- | --- |
| Paket bauen/veröffentlichen | [PW-B-Vertrag](../PW_B_CONTRACT.md): Phasen, geschlossene Generationen und Veröffentlichung; Tool-README Abschnitte PW-B und PB-A; §6 dieses Dokuments |
| Direkter Rasterimport und Endprüfung | Tool-README RP-3, Datenvertrag und Ressourcen; Produktion §§4–5 für verwendete Mono-/Farbsemantik und unabhängigen Proof |
| Paarprofil | [PAIRED_LINES](../PAIRED_LINES.md) vollständig und Tool-README Paarlinienprofil; kein Routinepaarlauf bei bereits vollständig gelöster Linienlogik |
| Feste Korrektur oder RP-5-Suche | [FIXED_RASTER](../FIXED_RASTER.md) beziehungsweise Tool-README RP-5; §4.4 und der wirklich verwendete Ableitungsvertrag |
| Aktuelle Schwierigkeit/Rebind | [SD2-Integration](../SD2_INTEGRATION.md) und Tool-README SD2-C/SD2-B; Analyse-/Bewertungsvertrag nur für die tatsächlich verwendeten Befehle |
| Gewählten Hintergrund ableiten | Hintergrundvertrag §4 und Tool-README HP-W2; keine Ableitung ungeklärter Kandidaten |
| Export/Plan/Register/Recovery | [RI](../PUZZLE_INTEGRATION.md) mit seinen aktuellen Budget-/Guardentscheidungen, [ZA-1](../ZA1_ADAPTER.md) für die verwendete Generation und die entsprechende CLI-Anleitung; §8 |
| Nachintegration/Bildrevision abschließen | §9 und der dort bezeichnete revisionsgenaue Retirementvertrag; keine allgemeine historische Lieferberichtslektüre |

Ein Link auf eine Einführung oder historische Lieferung ist kein neuer Auftrag.
Der aktuelle Quellenstand muss erreichbar und mit vollständiger Commit-SHA
gebunden sein. Die Regeldatei und die zugehörigen Stil-/Fachquellen aus demselben
festgehaltenen Regelstand lesen; alte versiegelte Snapshots nicht umschreiben.
Der bestehende Regelwerks-Snapshot und seine tatsächlichen Datei-/Hashbindungen
bleiben erhalten. Diese Dokumentrevision ändert keine Request-/Handoff-/Writer-
Schemas. Fehlende benötigte Quellen oder Widersprüche blockieren die betroffene
Operation, nicht automatisch unabhängige Arbeit.

Separat beauftragte Regel-/Werkzeug-/Spiel-/CI-Entwicklung verwendet weiterhin die
vollständige Entwicklungsroute aus AGENTS einschließlich WORKFLOW, Projektprofil
und auftragsbezogenen Fachquellen. Diese Ausnahme ist kein Entwickler-Kurzweg.

### 1.2 Gemeinsame Arbeitsregeln

Zu Beginn Kategorienquelle, Arbeitsindex und Runtime-Registry lesen, aber keine
Bestandsrätsel einzeln laden oder nachprüfen. Kategorie nach Auftrag oder prägendem
Hauptgegenstand gemäß [Kategorienvertrag](../CATEGORIES.md) zuordnen und in
Briefing/Record führen. Repository-/Toolstand mit vollständiger SHA binden.
Tatsächlichen Datei-, Bild-, Repository- und Ausführungszugriff prüfen. Keine
Funktionen, Originale, Prüfungen oder Erfolge behaupten, die nicht verfügbar oder
nicht ausgeführt sind. Bestehende Formate, Farbregeln, Solverprofile, Nachweise und
Reparaturverträge verwenden. Normale Produktion entwickelt keine neuen Werkzeuge.

Keine direkte Modell-API einbauen. Ein Produktionsauftrag mit Repositoryablage
erlaubt ausschließlich die beauftragte Paketsicherung samt Index; ein
Integrationsauftrag zusätzlich §8 und den fachlichen Abschluss nach §9.
Ablage-/Integrationsmerge braucht eine passende ausdrückliche oder bedingte
Freigabe. Bereits erteilte passende Aufträge nicht erneut erfragen. Kein direkter
Schreibzugriff auf main, keine fremden Änderungen, ungeklärten Fremdassets,
Secrets oder privaten Daten übernehmen. Vor lokaler Arbeit die beauftragte
Arbeitswurzel und [WORKSPACE](../dev-rules/WORKSPACE.md) beachten; diese Lektüre
betrifft die konkrete Ablage/Bereinigung, nicht den gesamten Entwicklungsworkflow.

Menschliches Probespielen ist optional und kein Produktionsgate. Verpflichtend
bleiben die tatsächliche Abschlussbildfreigabe, Motiv-/Parameterfreigabe,
technische Qualifikation, Raster-/Hintergrundwahl und finale redaktionelle
Abnahme am konkreten Gegenstand. Empfehlung, Dateiexistenz, Klick, Kopieren,
Aktualisierung oder Schweigen erzeugen keine Freigabe. Materiell geänderte
kreative Bytes benötigen die passende neue Entscheidung.

Normale Produktionsaufträge 1–5 einschließlich Korrektur und Wiederaufnahme
liefern keine Modell-, Reasoning- oder Eigenumsetzungsempfehlung. MODEL_SELECTION
und MODEL_CATALOG nicht dafür laden oder recherchieren. Der Nutzer wählt seine
Oberfläche selbst; fehlende erforderliche Bild-/Datei-/Werkzeugfähigkeiten bleiben
konkrete Blocker. Das Produktionsabschlussformat aus §7 gilt, nicht das
Entwicklungs-HANDOFF-JSON.

### Prüfungen gehören zur Produktion, nicht zur CI

Sämtliche rätselbezogenen Prüfungen – Lösbarkeit, Eindeutigkeit, unabhängiger
Proof, Herkunft, Reparatur, Gestaltung und Zielintegration – für die jeweilige
neue/geänderte Revision tatsächlich durchführen und dateigebunden belegen.
Unveränderte passend gebundene Ergebnisse wiederverwenden; §4.4 bestimmt die
nötigen Neuprüfungen. Keine rätselspezifischen Unit-Tests, Test-Snapshots,
CI-Falllisten oder dauerhaften Replayjobs. Auftragsprüfskripte bleiben temporär
außerhalb der Test-Discovery; Ergebnisse gehören zum Paket, nicht in einen
wachsenden CI-Korpus.

Vor jedem Inhalts-/Ablage-/Cleanup-PR den Abschnitt Paketplan sowie die buildfreien
Änderungsklassen aus [CI v2](../CI_WORKFLOW_V2.md) lesen und einen aktuellen
`.ci/package.json` führen. Reine Inhalte wählen begründet `modules=[]` und
`evidence.mode=none`; Quellen-/Planintegrität bleibt Pflicht, ohne Player-Build,
auch im Main-Nachlauf. Keine Solver-/Proof-Replays, vollständigen Fachtests oder
nativen Rendermatrizen allein wegen eines neuen Rätsels ergänzen. Code, gemeinsame
Spielassets und CI-Änderungen sind getrennte Entwicklungsarbeit mit geeignetem
Prüfplan; nicht die Inhaltsausnahme ausweiten oder manuell `all` wählen.

## 2. Abschlussbild zuerst, danach Abstraktion

### 2.1 Eingaben und Konfiguration

Zulässiger Input: Motivtext beliebiger Ausführlichkeit und/oder Ausgangsbild;
optional Breite/Höhe (ungefähr/fest), Mono/Farbe, Vordergrundfarbzahl
(ungefähr/genau) und weitere Einschränkungen. Eine Vorschau ersetzt keine
Originaldatei. Hauptmotiv, unverzichtbare Merkmale, erlaubte Umgestaltung und
Einschränkungen erfassen. Reversible Details sinnvoll ergänzen; nur wesentliche
offene Entscheidungen mit Empfehlung und Konsequenzen klären.

Frühe Breiten-/Höhenwünsche sind unabhängig: keine, eine oder beide Achsen.
Exakt/ungefähr gilt für ausgefüllte Achsen. Offene Achsen zum Motiv bestimmen;
keine 0, angenommene Quadratseite oder Wiederherstellung aufgehobener Altwerte.
Eine ausdrücklich aufgehobene Breite erhält die weiter gültige Höhe und umgekehrt.
Bloßes Leeren hebt keine veröffentlichte Vorgabe auf. Wünsche im Motivbriefing
sichern; die konkrete spätere Matrix besitzt zwei Maße. Ein freigegebener
Parameterkorridor wird nicht stillschweigend durch spätere Formularwerte geändert.

Zuerst farbige detaillierte Abschlussbilder, noch keine Abstraktion, Zellmatrix
oder Hinweise. Fehlende Rastermaße/offener Modus blockieren diese Bildwahl nicht.
Die spätere Abstrahierbarkeit berücksichtigen, ohne die Illustration vorzeitig
auf Zellniveau zu vereinfachen. Eine eigene Eingangsdatei ist zunächst Referenz,
keine automatisch freigegebene Abschlussbilddatei.

Nach Bildfreigabe bei offener Konfiguration zwei bis drei sinnvolle Möglichkeiten
knapp vergleichen und eine empfehlen. Motivtreue, Darstellbarkeit, Logikrisiko
und Spielgefühl getrennt begründen; Rechtecke gleichberechtigt berücksichtigen.
Dies verlangt nicht mehrere tatsächliche Abstraktionsbilder.

- Regulär höchstens 50 Zellen je Achse; größere technische Werkzeuggrenzen sind
  keine Produktfreigabe. Klein (längste Achse bis 20), mittel (21–35) und groß
  (36–50) unterscheiden Detailspielraum, nicht logische Schwierigkeit.
- Acht Vordergrundfarben plus Leer sind die technische Obergrenze, kein Ziel.
  Die kleinste motivgerechte Palette empfehlen; Ausgangspunkt Mono oder 2–4 Farben.
  5–8 nur mit benanntem motivischem Nutzen und erklärtem Verlust bei Zusammenlegung.
  Keine Farbe nur für Verfügbarkeit, Solvererfolg oder künstliche Schwierigkeit.
- Farbzahl zählt tatsächlich verwendete Vordergrund-IDs; EMPTY zählt nicht,
  Weiß kann Vordergrundfarbe sein. Unbenutzte Einträge, ähnliche Schattierungen
  und dekorative Einzelzellen erfüllen keinen Farbwunsch. Vor Versiegelung auf
  nötige Einträge reduzieren und die erforderlichen Neuprüfungen ausführen.
- Genaue Farbzahl ist fest; Konflikte vor Abweichung klären. Ungefähr ist ein
  begründbar abweichendes Ziel innerhalb des vorgeschlagenen und danach
  freigegebenen Korridors. Mono hat eine Vordergrundfarbe. Bei offener Farbzahl
  die empfohlene Palette und eine sinnvoll reduzierte Alternative erläutern,
  jede Farbe einer Motivfunktion zuordnen. Keine zusätzliche Vollmatrix verlangen.
- Maße, Seitenverhältnis und Palette zum Motiv wählen; vor Nachweis keine
  Lösbarkeit versprechen. Das Abschlussbild bleibt unabhängig davon ausgearbeitet
  und farbig. Materielle Abweichungen vor weiterer Produktion entscheiden lassen.

### 2.2 Darstellungen auseinanderhalten

| Darstellung | Zweck und Bindung |
| --- | --- |
| Ursprungsidee / Bildquelle | Auftrag/Referenz; Original, Herkunft und Nutzungsgrundlage erhalten. |
| Abschlussbild | Zuerst erzeugte farbige detaillierte Illustration; nach tatsächlicher Auswahl/Freigabe gestalterische Referenz und spätere Belohnungsansicht. |
| Motivvorlage | Aus genau diesem gespeicherten Bild abgeleitete vereinfachte Illustration; eigene Motiv-/Parameterfreigabe vor Rasterproduktion. |
| Lösungsraster | Exakte diskrete Zellmatrix; alleinige Grundlage von Hinweisen und Logiknachweis. |
| Hintergrundzeichnung | Eigenständiger Kontext, separate Bildrevision und Wahl; keine Quelle von Lösungszellen. |

Input → Abschlussbild → freigegebene Abstraktion → Lösungsraster bleibt die
verbindliche Richtung. Motivische Konsistenz, nicht Pixelidentität. Dateien und
Revisionen getrennt führen; das detaillierte Original nicht mit der Abstraktion
überschreiben. Der Hintergrund gehört nicht in diese Ableitungskette.

### 2.3 Styleguide

Die gemeinsame gestalterische Norm steht vollständig in
[PUZZLE_IMAGE_STYLE](../PUZZLE_IMAGE_STYLE.md): warme klare Illustration mit
Filzstift-/Tuscheanmutung, kontrollierte Abstraktion und leichte Graphitkontexte.
Sie ist in jeder Phase Pflicht. [Q-B02/Q-B03](../PUZZLE_QUALITY.md#31-abschlussbildphase)
und [AT §2](../REVEAL_TRANSPARENCY.md#2-verbindlicher-bildstandard) behalten
Einzelurteile, echte Transparenz, helle Motivteile und saubere Alphakanten.
Szenen bewahren notwendige Umgebung und erhalten eine bewusste transparente
Außenkomposition. Originale groß/klein direkt ansehen, bei Bedarf auf neutralem
Grund/Schachbrett. Keine routinemäßige Buch-/Katalogmontage, Fadeprobe oder
Testintegration, auch nicht in spätere Produktionsphasen verlagert.

Je fälligem Qualitätskriterium erfüllt/Warnung/nicht erfüllt/nicht geprüft mit
kurzer Begründung und konkreter Datei-/Revisionsbindung festhalten. Kein guter
Gesamteindruck verdeckt negative Einzelkriterien. Q-H01/Q-H02 behalten die echte
Zell-/Hinweissicht, ohne obligatorischen Spielstart je Rätsel. Im Raster nur
diskrete Werte, keine Textur/Zwischenfarben als Zellzustand. Transparenz des
Reveals ändert weder EMPTY noch weiße Vordergrundfarben der Matrix.

### 2.4 Abschlussbildauswahl und Abstraktionsfreigabe

1. Standardmäßig drei sinnvoll unterschiedliche echte Abschlussbilder erzeugen;
   Komposition/Pose/Farbgebung variieren, Stil, Detailanspruch und Auftrag bewahren.
   Bindende Referenz (`faithful`) und freie Interpretation (`free`) unterscheiden.
   Nur eine ausdrückliche Vorgabe reduziert die Variantenanzahl.
2. Native Bildgenerierung verwenden; jede Variante tatsächlich als Einzeldatei
   speichern und zeigen. Eine Kontaktübersicht ist nur Auswahlhilfe. Fehlende
   Bildfunktion blockiert den Bildschritt; Konzepte ersetzen keine Originale.
3. Vor jeder Abstraktion muss das konkrete Abschlussbild ausdrücklich freigegeben
   sein: Datei, Revision/Hash und geschützte Merkmale. Eine Auswahl mit Korrekturwunsch
   ist keine Freigabe noch nicht vorhandener korrigierter Bytes.
4. Danach standardmäßig eine begründete Abstraktion aus den gespeicherten Bytes
   für die empfohlene Konfiguration erstellen. Weitere Varianten nur für konkrete
   offene Darstellungs-/Detailfragen, nicht zur Erfüllung einer Quote. Reveal und
   Motivvorlage nebeneinander vorlegen; Verluste und Parameterkorridor benennen.
5. Vor Rasterproduktion echte Freigabe der Motivdatei samt Revision/Hash,
   Revealbezug, Invarianten und zulässigen Maß-/Modus-/Cropvarianten abwarten.
   Bildfreigabe ersetzt keine Motivfreigabe; Schweigen ist keine Entscheidung.

Nur die gewählte Darstellung korrigieren, geschützte Merkmale nennen und neue
Revision sichern. Nach zwei erfolglosen Bildkorrekturrunden Ursache und geänderten
Plan vorlegen. Bei ungeeigneter Abstraktion Vereinfachung, Größe oder Palette
überdenken; anderes Abschlussbild erneut freigeben lassen, nicht heimlich an
technische Fehlschläge anpassen.

## 3. Standardablauf: fünf Aufträge

| Schritt | Eingang und Arbeit | Übergabe und echte Entscheidung |
| --- | --- | --- |
| 1 · Abschlussbilder | Motivbriefing/optionale Referenz; drei echte detaillierte farbige transparente Bilder. Keine erfundene ID oder Gitquelle beim neuen Briefing. | reveal_review, erreichbare Originale; tatsächliche Bildwahl/-freigabe. |
| 2 · Motivvorlage | Freigegebene gespeicherte Revealbytes abstrahieren; geeigneten Parameterkorridor empfehlen. | motif_review, Vergleich/Verluste/Parameter; echte Motivfreigabe. |
| 3 · Rasterangebote | Erst nach Motivfreigabe bedarfsweise Kandidaten und erforderliche Korrekturen; vollständige technische/redaktionelle Qualifikation. | Qualifizierte Einzelrevisionen raster_ready; Sichtungsentwürfe getrennt raster_review. Keine automatische Rasterwahl. |
| 4 · Kontextzeichnungen | Ausdrückliche Wahl einer qualifizierten Rasteroption am festen Quellencommit; erst danach drei unterschiedliche isolierte Kontextbilder. | background_review; Auswahl, Korrektur oder ausdrückliches none. content_ready erst bei vollständiger Bereitschaft. |
| 5 · Integration | Tatsächliche Endabnahme, gültiger Rasterstand und ausgewählter abgeleiteter Hintergrund bzw. none. | Finalizer → Export → frischer Plan → autorisiertes Register; Git/Draft-PR, tatsächlicher Mainmerge und §9 nur mit passenden Befugnissen. |

Klick/Kopieren ist lokale Absicht, erst ein abgesendeter Auftrag erklärt eine
Entscheidung. Erst zurückgelesene Gitdaten belegen einen erreichten Stand.
Der Assistent ist kein Modellaufrufer oder Projektwriter. Quelle für Cloudakteure
muss über Git erreichbar sein, nicht bloß über localhost oder einen lokalen Pfad.

PW2-B in [#626](https://github.com/venomenon328/picross/issues/626) verbindet in der
Schlussübersicht konkrete Hintergrundwahl/none, Endabnahme und Integration in
einem regulären Auftrag. Der Standard beauftragt anschließend Commit/PR,
unabhängiges Review und Squash-Merge erst nach aktuellen Vor-Merge-Gates sowie
§9. Ein bewusst gewählter Draft-Umfang bleibt ausdrücklich erhalten. Korrektur
und Wiederaufnahme erklären keine neue Endabnahme oder Mergefreigabe. Die
technischen Zwischenzustände und Byteprüfungen bleiben, lediglich der gesonderte
Benutzerauftrag „Zur Endabnahme vorbereiten“ entfällt. Erst das tatsächliche
Absenden erteilt die genannten Befugnisse, nicht dieser Normtext oder ein Klick.

## 4. Rasterproduktion und technische Pflichtprüfung

Rasterprüfung hat einen eigenen Gegenstand. Hintergründe liefern keine Zellwerte
und werden nicht durch Solvererfolg freigegeben. Für 0.8.0 ist vollständig
qualifiziertes raster_ready ohne Hintergrund zulässig; content_ready setzt später
die eigene Hintergrundbereitschaft voraus. Keine vorgezogenen Hintergrundblocker.

### 4.1 Import und Rastervarianten

1. Von der freigegebenen gespeicherten Motivvorlage ausgehen; Ableitung aus genau
   dem freigegebenen Reveal anhand Originalen, Hashes und Bearbeitung prüfen.
   Originalbytes, SHA-256, Normalisierung, Rechte, Parameter und Toolversion erhalten.
   Während der Produktion beginnt deterministische Prüfung bei Bildbytes, nicht
   beim Prompt. Nach finaler Integration gilt der Abschluss nach §9.
2. Striktes bestehendes Designformat und aktuelle Format-/Ressourcengrenzen der
   RP-3-Anleitung verwenden. Redaktionelle Zusatzangaben in Begleitdateien.
   Crop und Seitenverhältnis beachten, nicht stillschweigend strecken.
3. Mit dem aussichtsreichsten begründeten Rasterkandidaten beginnen. Einen zweiten
   und weitere jeweils nacheinander nur für ein konkret benanntes unerfülltes
   Kriterium und eine neue motivisch zulässige Hypothese erzeugen. Keine anfängliche
   Viererquote, keine neue Zweierquote und keine blinde Kreuzprodukt-Suche.
   Ein vollständig geeigneter qualifizierter Kandidat genügt. Die bestehende
   Obergrenze bleibt höchstens sechs Rasterkandidaten pro Runde; alle bisherigen
   Versuche zählen kumulativ. Neue Namen, Ordner oder Wiederaufnahme setzen weder
   Gesamt-/Such-/Reparaturbudgets noch den freigegebenen Korridor zurück.
4. Vor teurer Qualifikation preisgünstige Ausschlüsse und Duplikate erkennen:
   Maße/Werte/Palette, feste Wünsche, offensichtliche Form-/Randmängel und exakten
   Vergleich von Maßen, Palette und Zellwerten. Parametergebundene Kandidatenhashes
   sind kein reiner Matrixvergleich. Entstehungswege und Ablehnungsgründe erhalten.
   Diese Vorprüfung ersetzt keine vollständige Prüfung eines angebotenen Rasters.
5. Unterschiedliche globale Maße, Crops oder Paletten benötigen getrennte Designs.
   Beim farbigen area-Pfad ist der Schwellenwert wirkungslos; reine Schwellenvarianten
   sind dort kein neuer Ansatz. Mono-Schwellen anhand des Bilds wählen. Verfahren
   mit zwangsläufig leeren Außenkanten, insbesondere der entsprechende contour-Pfad,
   nicht unverändert als reguläres Ergebnis übernehmen; derzeit area bevorzugen.
6. Passend gebundene unveränderte Nachweise wiederverwenden. Geänderte Logikeingänge
   erhalten die Neuprüfungen aus §4.4. Echte Raster klein, ohne Glättung vergrößert
   und mit Gitter beurteilen. Logischer Erfolg allein ist keine Auswahl.

### 4.2 Harte Kriterien

Jeder angebotene freigabefähige Kandidat erfüllt vollständig:

- Gültige Maße, Werte, Palette und Formate; regulär höchstens 50 je Achse.
  Tatsächliche Vordergrundzahl als len({v für v in allen Zellen, wenn v != EMPTY})
  zählen; endgültige Palette, genaue Vorgabe und freigegebener Korridor passen.
  Wunsch, Istzahl und Farbrollen nennen, nicht bloß Paletteinträge zählen.
- Hinweise deterministisch aus exakt dieser Matrix. Gleichfarbige Folgeblöcke
  haben mindestens eine Leerzelle Abstand; verschiedenfarbige dürfen sich berühren.
- Vollständige deduktive Lösung vom unbekannten Start, ohne vorgefüllte Zellen,
  notwendiges Raten, Suchannahmen oder Motivwissen; vollständiger Proof unter
  benanntem Profil, frischer unabhängiger Prüferprozess und exakter Endmatrixvergleich.
- Datei-/redaktionelle Herkunft Input → freigegebenes Reveal → freigegebene
  Motivvorlage; deterministische Rekonstruktion Motivvorlage → Normalisierung →
  Matrix → Hinweise. Alle Dateien/Parameter prüfen, bei Reparatur zusätzlich
  Referenz, Plan und Replay. Rechte und echte Freigaben sind keine Solverergebnisse.
- Randregel: mindestens eine gefüllte Zelle an linker ODER rechter Außenkante
  UND mindestens eine an oberer ODER unterer Außenkante. Jede Vordergrundfarbe
  zählt, nicht alle vier Kanten sind nötig; gilt auch für Breite/Höhe 1.
  Ein vollständig leeres Raster scheitert. Keine motivfremden Randpixel/Rahmen
  allein zum Bestehen der Regel hinzufügen.

Eine tatsächliche menschliche Randregel-Ausnahme für eine konkrete Endrevision
nur über den unterstützten äußeren ZA-1-v2-Autorisierungsvertrag an Originalpaket,
Handoff, Inventar, Wahl und Endfreigabe binden. Negativen Originalbefund sichtbar
erhalten; kein pass-Flag oder allgemeiner Bypass. Alle übrigen Gates bleiben hart.

Vollständige gültige Deduktion belegt Eindeutigkeit. stalled beweist weder
Mehrdeutigkeit noch Unlösbarkeit; aborted ist Abbruch. Exitcode 0, Importbündel,
generiertes Zahlenbild und KI-Erfolgsaussage sind keine Zertifizierung.
Die separate Eindeutigkeitsdiagnose sucht und liefert eigene Lösungszeugen;
unique ersetzt keinen Deduktionsproof, unknown nach einer Lösung keine
Eindeutigkeit. check-diagnosis prüft Bindungen/Zeugen, nicht die vollständige Suche.
Keine neue Schwierigkeit oder Freigabe aus einem Suchurteil ableiten.

Die vorhandene Rekonstruktionsprüfung (inspect_candidate bzw. passender Reparatur-/
Exportreader) zusätzlich zur Logik benutzen. Nur wirklich verfügbare Befehle/API
verwenden; aktuelle Zeit-/Linien-/Ressourcengrenzen der entsprechenden README-
Abschnitte vor Ausführung lesen. Abgebrochene Versuche nicht umetikettieren.

#### 4.2.1 Profilwahl und Produktionsnachweise

1. full-line-mono beziehungsweise full-line-color ist der Ausgangspunkt.
   Vollständig unabhängig bestätigte Linienlogik genügt; kein zusätzlicher
   Paarprofil- oder Eindeutigkeitssuchlauf als Routinepflicht.
2. Bei visuell tragfähigem, unabhängig bestätigtem Linienfixpunkt stalled vor
   rein logikbedingter Rasteränderung zunächst das passende zugelassene Paarprofil
   am unveränderten Raster prüfen. Eine begründete Abweichung (etwa ausdrücklich
   einfache Techniken oder Ressourcenblocker) festhalten. Vorgaben bleiben wirksam;
   Profilprüfung derselben Matrix ist keine zusätzliche Rastervariante. Durch
   zwei geprüfte Lösungen belegtes multiple dagegen direkt nach §4.4 bearbeiten.
3. Profil-ID und Zeit-/Linien-/Paarbudgets vor Lauf binden. import-image explizit
   mit --profile paired-lines-mono bzw. paired-lines-color und Paarbudgets aufrufen;
   Standard bleibt Linienlogik. Bestehende direkte Quelle mit identischem Design
   in neues Ziel importieren, Matrix-/Logikgleichheit prüfen. Isoliertes solve ist
   kein exportfähiges Produktionsbündel; keinen Proof im alten Manifest austauschen.
4. Der Paarlauf erzeugt eigenen full-line-Baselineproof und Assessment. Baseline
   und Paarproof derselben Logik frisch unabhängig prüfen, etwa mittels assess
   --input ... --proof ... --baseline ... gemäß CLI. Das ersetzt weder Herkunft
   noch Endmatrix-/Dateiprüfung. picross-quality-report-v1 ersetzt weder
   picross-deduction-assessment-v1 noch difficulty.json oder menschliche Freigaben.
5. Nur verifizierte stalled-Baseline plus vollständiger verifizierter Paarproof
   belegen notwendigen R4. Aborted, unvollständiger Paarproof oder unique genügen
   nicht. Bei Nichtabschluss Profil, offene Zellen, verbrauchte Budgets und Endgrund
   nennen, keine absolute Aussage über alle denkbaren Lösungsregeln treffen.
6. Passende versionierte Import-/Reparatur-/manuelle Ableitungsformen nach
   PAIRED_LINES und die exakte certification durch alle Stufen einschließlich
   candidate.certification im Handoff führen. Nicht in alten Ableitungsvertrag
   zurückfallen. Quelle, Motivschutz, Bildfreigaben und Endabnahme bleiben Pflicht.

Die separate Eindeutigkeitsdiagnose ist nur bei konkreter offener Frage sinnvoll,
keine Voraussetzung der bereits zugelassenen Paarprofilwahl. Kein neuer CI-Fall
oder Bestandsreplay entsteht aus einer konkreten Produktion.

### 4.3 Redaktionelle Kriterien

[Qualität §§2–4](../PUZZLE_QUALITY.md) bindet Einzelurteile zu Flächennutzung,
Hauptformen, Perspektive/Proportionen, Details/Negativräumen, Farbrollen,
tatsächlicher Raster-/Hinweissicht und Reveal-Konsistenz. Mono und Farbe behalten
unterschiedliche Erkennbarkeitsziele. Ein Auge darf eine Zelle sein; ein Henkel
braucht Innenraum. Leere Innenstreifen nicht mechanisch entfernen.

Belegung unter 15 %/über 85 %, isolierte Zellen und leere Innenlinien sind
Prüfanlässe, keine automatischen Ablehnungen. Motivischen Nutzen/Mangel begründen;
keine Verschlechterung der Form für eine Kennzahl. Alle tatsächlich verwendeten
Farbpaare betrachten, auch seltene/unbenachbarte. Kleine Zell-/Hinweisgrößen auf
aktuellem Papier mit Kontur/Schraffur, normale, abgeschwächte und ausgekreuzte
Hinweise wirklich ansehen. Verfügbare Farbsinnsimulation nur ergänzend.

Die eingeführte und für 0.8.0 fortgeltende Regel picross-palette-separation-1 aus
[Qualität §8](../PUZZLE_QUALITY.md#8-p-a-v01-freigegebene-regel-für-paarweise-farbunterscheidbarkeit)
trennt Oklab-Ausschluss, Warnzone und Sichturteil. RP-3 prüft die Ist-Matrix vor
Solver, RP-5 jede Bewertung, feste Wege die rekonstruierte Matrix vor Endproof.
Negative Entwürfe bleiben sichtbar. check-palette ist nur zusätzliche Diagnose.
Nach Änderungen Matrix, IDs/RGB/Nutzung und Regelbindung frisch rekonstruieren;
Palettenentwürfe ohne tatsächliche Verwendung sind vorläufig.

Vor einem qualifizierten Angebot das geschriebene Paket frisch mit ZA-1 prüfen;
raster_ready enthält alle Rastergarantien, content_ready später zusätzlich den
Hintergrund. Der Adapter erhebt den Pflichtbefund an allen Paaren frisch.
Optionales palette_assessment wird zusätzlich neu verifiziert; Farbpakete binden
palette_review an den inventarisierten picross-palette-visual-review-v1-Record
mit tatsächlichen Q-R04/Q-H01/Q-H02-Ansichten und Einzelurteilen. Die geschlossenen
Felder bleiben in [ZA-1 P-B2](../ZA1_ADAPTER.md#p-b2--authoring-060-und-additive-palettengeneration-v5)
und der entsprechenden Tool-Anleitung. Fehlende/stale Sichtung, nicht geprüft
und positive S-Werte allein erlauben keine Freigabe.

Bei Warnung/negativem Sichturteil verlangt eine zulässige Annahme Qualität §6:
ursprüngliches Urteil, tatsächlicher Akteur, UTC, Wortlaut, Begründung und Beleg.
Ein negativer technischer Befund bleibt negativ. Für tatsächliche Übernahme den
äußeren picross-palette-editorial-exception-v1 mit sämtlichen negativen Paaren,
exakten Werten/IDs und Kandidaten-/Revisions-/Istmatrix-/Quell-/Regel-/Handoff-/
Inventar-/Paketbindung und echter Endfreigabe benutzen, außerhalb versiegelter
Originale und ausdrücklich via --palette-exception. Bereits erforderliche
manuelle Autorisierungen bleiben zusätzlich nötig. Die Ausnahme heilt weder
Proof noch Rechte, Freigaben, feste Parameter, Difficulty oder Randregel.

Historische F05-Referenzannahmen sind keine Ausnahme oder Freigabe eines neuen
realen Kandidaten. Bei null qualifizierten Kandidaten §4.5 verwenden, mit echten
Bildern, Defiziten und Korrekturmöglichkeiten; keine qualifizierten Angebote vortäuschen.

### 4.4 Reparaturen und Änderungen

Konkrete kleine Kontur-/Flächenmängel und störende leere Außenlinien innerhalb
des freigegebenen Korridors vor Rückgabe bearbeiten, auch bei solved. Gute
Kandidaten nicht unnötig ändern. Reguläre feste Korrektur folgt
[FIXED_RASTER](../FIXED_RASTER.md): vollständiger vorab gebundener Plan gegen
den direkten unveränderten RP-3-Import, keine Suche/nachträglich erweiterte
Editliste, Schutzmaske und frische Endnachweise einschließlich aktiver 0.4-Analyse.
Offene/ungefähre Endmaße bleiben trotz konkretem Importstart offen/ungefähr.
Materielle Änderungen entscheiden lassen; eine Zelle ist nicht automatisch
harmlos. Runden/Kandidaten/Änderungen zählen kumulativ unter allen Namen/Ordnern.
Erst frisch geprüfter geschriebener Builder-ZIP erlaubt raster_ready, ohne damit
Rasterwahl, Hintergrund oder Endfreigabe zu erklären.

Wenn kein visuell tragfähiger Kandidat vollständig zertifiziert ist, gezielte
Verbesserungen versuchen, bevor allein wegen stalled oder belegtem multiple
zurückgegeben wird. Unique genügt nicht. Nur tragfähige Formen reparieren;
sonst zuerst Abstraktion/Größe/Palette und notwendige Motivfreigaben klären.

1. Ursache trennen. Stalled betrifft das benannte Profil; §4.2.1 ausschöpfen.
   Bei multiple beide Zeugen/Differenzbereiche prüfen. No_solution/contradiction
   bei Hinweisen aus derselben Matrix ist zunächst ein Eingangs-/Werkzeugwiderspruch,
   kein erfundener Bildfehler. Unknown/aborted erfordert Ressourcenanalyse.
2. Standardmäßig bis zu zwei gezielte Reparaturrunden, bei Erfolg sofort stoppen.
   Runde 1 am besten geeigneten Kandidaten: offene Domains/Kreuzlinien/Zeugen
   bestimmen zulässige Regionen. Motivisch plausible Kontur-/Flächen-/Negativraum-
   änderungen begründen; kein Rauschpixel, Zusatzrahmen oder neue Farbe als Logikanker.
3. Vor jedem RP-5-Lauf unveränderte Referenz, Schutzmaske für wichtige gefüllte
   und leere Zellen, Operatoren, Seed und Änderungs-/Such-/Abschlussbudgets speichern.
   Runde 1 standardmäßig höchstens zwei geänderte Positionen, 64 bewertete
   Kandidaten und 512 Vorschläge. Zeit-/Linien-/Paarbudgets passend zur gemessenen
   Referenz innerhalb Werkzeuggrenzen wählen; frische Abschlussprüfung reservieren.
   Kleinere Budgets nur begründet, nicht als Alibiversuch.
4. Ohne Fund eine andere begründete Hypothese, zulässige Region oder geeignete
   Referenz prüfen. Runde 2 bis 128 Kandidaten/1024 Vorschläge. Höheres Zellbudget
   nur vorab motivbezogen begründen; Schutzmerkmale und Korridor bleiben hart.
   Keine identische Wiederholung oder Umwertung alter Abbrüche. Ressourcen-/Replay-
   grenzen können kleinere Runden erfordern; Reichweite/Endgrund berichten.
   Früher Stopp nur bei Erfolg, fehlendem erlaubtem Änderungsraum, materieller
   Motivänderung oder konkretem technischem Blocker; nächsten Schritt benennen.
5. RP-5 optimiert begrenzt lokale Zelländerungen, nicht selbst nach Diagnosezeugen.
   Akteur legt Hypothese/Maske fest. Reicht das nicht, konkrete Formkorrektur oder
   Abstraktions-/Maß-/Palettenänderung vorschlagen und nur mit passender Befugnis
   ausführen. Historische manuelle Ableitungen brauchen ihren unterstützten
   ZA-1-Vertrag und gesonderte Autorisierung; nicht als regulären Import ausgeben.

Je Runde genügen Hypothese, Referenz-/Plankennung, tatsächliche Kandidaten-/
Änderungszahl, Endgrund und Auswahlentscheidung im bestehenden Protokoll.
Begrenzter Nichtfund ist kein Beweis unmöglicher Reparatur. Referenz, Resultat
und markierten Zell-Diff vergleichen; found allein genügt nicht ohne Endproof,
unabhängige Prüfung, Replay und Redaktion. Neue Hinweise verlangen eigene
Baseline/Endnachweise; Paarpläne binden certification bereits vor Lauf.

| Änderung | Erforderliche Wiederholung |
| --- | --- |
| Zellwert oder Rastermaß, auch eine Zelle oder nur leerer Außenbeschnitt | Neue Revision, Hinweise, vollständiger Logiknachweis, unabhängige Prüfung und Rasterbewertung. |
| Quelle, Crop, Palette oder Importparameter | Neuer gebundener Import und vollständige Prüfung. |
| Materielle Motivänderung | Zusätzlich erneute ausdrückliche Motivfreigabe. |
| Abschlussbild | Neue Bildrevision und menschliche Bildfreigabe; Ableitung, Motiv-/Rasterkonsistenz und Endabnahme erneut prüfen. Materielle Änderungen invalidieren abhängige Motivfreigaben. Kein neuer Logiklauf allein bei nachweislich identischem Raster/Logikeingang. |
| Hintergrundillustration, Komposition oder Transparenz | Neue Bildrevision/Wahl und abhängige Ableitung; Ablehnung mit Grund sichern, kein automatisches none. Unveränderte Raster-/Proof-/Schwierigkeitsbindungen erhalten. |
| Nur Schwierigkeit/Kategorie/Metadaten | Keine neue Bild-/Rasterproduktion oder Freigabe allein deswegen; bei versiegelten Paketen äußere Ergänzung/Exportbindung, passende Nachweise erhalten. |
| Erstmals Paarprofil bei gleicher Matrix | Neue profilierte Produktionsbindung samt Baseline, Paarproof und Assessment; keine umetikettierten Altproofs oder veränderten Rasterwerte. Neue Produktion bindet aktuellen 0.8-Regelstand; alte versiegelte Originale bleiben. Endfreigabe bindet tatsächliches Handoff/Inventar. |

Materiell sind Identität, Pose, prägende Proportionen, wichtige Innenräume,
Gesichtszüge oder geschützte Merkmale; schon eine Zelle kann materiell sein.
Eine reine Freistellung ist eine neue Bildrevision nach AT, keine Freigabe durch
Spezifikation. Bei unveränderten Definitionen/Runtime-Revision/Raster/Logik
entstehen keine neuen Solver-/Proof-/Difficulty-Läufe allein wegen Bildarbeit.
Identität, Ressourcenpfade, Slots, Rating und Hinzugefügt-Daten bleiben erhalten.

Deterministische vereinbarte Hintergrundableitung und bytegleicher Transport
brauchen keine erneute kreative Wahl. Reine Rastergeometrie-/Palettenänderung
verlangt keine Buchabnahme oder neue Dreierauswahl; geänderten Motivkontext gezielt
gegen Briefing/Bild prüfen. Hintergrundersatz folgt seinem eigenen Ziel-/Abschluss-
vertrag, nicht dem AT- oder Rasterersatzbefehl. Unabhängige unveränderte Freigaben
bleiben gültig; Korrektur/Wiederaufnahme erteilen keine neue End- oder Mergefreigabe.

### 4.5 Geprüfte Raster zur menschlichen Auswahl

Ein vollständig geeigneter, technisch und redaktionell qualifizierter Kandidat
genügt. Bereits vorhandene sinnvoll unterschiedliche qualifizierte Alternativen
dürfen mit kurzer Empfehlung angeboten werden. Keine Zwei-/Dreierquote und keine
Erzeugung weiterer Varianten allein für eine Angebotszahl. Jedes Angebot erfüllt
Korridor und §§4–5 vollständig: eigene technische Prüfung, visuelle Bewertung,
Bildkonsistenz, gebundene Schwierigkeit oder zulässige ausdrücklich angenommene
redaktionelle Abweichung nach Qualität §6. Gleiche Matrizen unter anderer ID oder
anderem Solverprofil sind keine zusätzlichen Angebote. Empfehlung ist keine Wahl.

Budgets werden nicht für eine Quote erweitert. Bei null qualifizierten Kandidaten
nach Qualität §5 zwei bis drei möglichst unterschiedliche beste brauchbare
bereits vorliegende Entwürfe zeigen, sofern vorhanden; bei nur einem diesen.
Das ist Sichtung, keine neue Kandidatenerzeugungspflicht. Jede Ansicht nennt
stabile ID/Revision, tatsächliches Raster/Reveal mit echten Links, Prüfungen/Lücken,
Qualitätsdefizite und Korrekturmöglichkeiten sowie ausdrücklich
`Sichtungsentwurf – nicht integrationsbereit`. Ohne brauchbaren Entwurf konkreten
Nichtfund und nächsten Korrekturschritt nennen; keine Dateien erfinden.

Sichtungsentwürfe sind keine Integrationsoptionen oder raster_ready. Raster_review
bzw. blocked mit Grund führen. Erst zulässige Korrektur/Einzelfallentscheidung und
alle technischen Nachweise erlauben den gültigen Auswahlweg. Fehlende Proofs oder
unklare Rechte bleiben Blocker. Empfehlungen erteilen keine automatische Freigabe.

Jedes Angebot bekommt stabile Kennung, Unterschiede, Maße/Modus/Istfarbzahl,
Schwierigkeit und echte Rasteransichten. Vor Ausgabe pro Raster eine kollisionsfreie
Einzelpaketrevision derselben ID nach §6 sichern, mit genau einem handoff.candidate,
allen nötigen Inputs und Inventar. Geschriebene ZIPs frisch prüfen; keine neue
Mehrfachhülle und keine verschachtelten Alternativen-ZIPs. Vergleich ersetzt kein Paket.
Workspace bindet Angebote an Einzelrecord, Originalinventar, Bilder und Quellencommit.
Schritt 4 beginnt erst mit tatsächlicher qualifizierter Rasterwahl; die neue Revision
führt picross-raster-selection-v1 nach PW-B. Originale bleiben bytegleich, nicht
gewählte Angebote bis bestätigter Mainintegration erreichbar. Weder erste Option
noch höchste Revisionsnummer gilt automatisch als Wahl.

## 5. Schwierigkeit L1–L5

Logische Schwierigkeit, Rastergröße, Bearbeitungsumfang und Lösungszeit trennen;
Sterne-/Fehlerwertung im Spiel bleibt unabhängig. Hintergrundstatus/-wahl fließen
nicht ein. Bei reiner Bildrevision passende unveränderte Analyse-/Proofbindungen
erhalten; tatsächliche Logikänderungen verlangen neue Nachweise nach §4.

### 5.1 Historische Produktionsmethoden 0.1 und 0.2

Diese Methoden beschreiben ihre damaligen Pakete, nicht die Wahl für neue 0.8-
Produktionen. Alte Schätzungen, Snapshots und Freigaben bleiben unverändert.
Die damaligen Technik-/Engstellen-/Schätzregeln sind im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/a4bb4f929f29cd6d6e188500b5a8dbb1dead60fe/docs/ai-workflows/PUZZLE_AUTHORING.md#51-historische-produktionsmethoden-01-und-02)
lesbar; keine Routinelektüre oder rückwirkende Neubewertung. Profilverwendung
allein beweist auch heute keine Notwendigkeit der stärksten Technik. Stalled oder
Abbruch ist keine zusätzliche Schwierigkeitsstufe.

### 5.2 Aktueller zusätzlicher Integrationsstandard SD

Für neue Produktion gilt die aktive 0.4-Analyse-/Bewertungsbindung aus
[SD2](../PUZZLE_DIFFICULTY_V2.md) und [SD2-Integration](../SD2_INTEGRATION.md).
Vor Endfreigabe aus endgültiger Matrix/Design/normalisierter Logik den passenden
vorläufigen Input erzeugen und den vollständigen aktuellen Bericht prüfen.
R4-Baseline/Paarproof nur bei tatsächlich beanspruchtem Bedarf binden. Nach
Endfreigabe/Export das unterstützte Rebind bei gleicher ID/Logik/Matrix auf die
wirklichen Definitionsbytes anwenden; ursprüngliches rating.source erhalten.
Befehle/Budgets vor Ausführung in den entsprechenden SD2-Abschnitten der
Tool-README lesen. Keine freie Ersatzschätzung, pauschale Stufe 5 oder neue
Bildproduktion bei fehlender/abgebrochener Analyse.

Passend gebundene vollständige Ergebnisse wiederverwenden. Gleiche Methodenversion
und Eingabe bestimmen dieselbe Bewertung. Keine Skalenenden aus dem realen Katalog,
kein realer Rätselbestand als Testkorpus. Titel/Kategorie/Reveal bei gleicher Logik
erzwingen keinen neuen Analyselauf. Alte Originalpakete/Handoffs/Freigaben nicht
überschreiben; aktive Bewertungen außerhalb versiegelter Produktion führen.
Probespielen bleibt optional; technische Referenzen sind keine empirische
menschliche Kalibrierung. Ungemessene Lösungszeiten nicht behaupten.

## 6. Dateien, Übergabe und Wiederaufnahme

### 6.1 Repositoryablage während der laufenden Produktion

Neuer Job: neue pz-ID und genau ein stabiler Branch content/pw/<puzzle_id> von main.
Alle Phasen/Varianten/Korrekturen/Wiederaufnahmen bleiben dort. Index und Kollisionen
prüfen, keine fremde Arbeit überschreiben. Jede Übergabe erhält eine vollständige
Revision unter content/authoring/<puzzle_id>/<revision>/ und Eintrag im Arbeitsindex.
Echten unversiegelten Request v3, Handoff v4, tatsächlichen aktuellen 0.8-Snapshot
und explizite Dateiliste nach PW-B und der PB-A-Anleitung benutzen:

```text
python -m tools.puzzle_production.authoring_builder build --request <request-v3.json> --source-root <vorbereitete-dateien> --output-root <eigene-arbeitswurzel> --publish-to <produktionscheckout> --history-repo <produktionscheckout>
```

Der vorhandene Builder validiert Dateien, erzeugt Inventar v1, geschriebenen
Original-ZIP, bytegleiche Handoffkopie, Record v3 und geprüfte workspace.json.
Der [Ansichtsübergabeschritt](../PRODUCTION_CURRENT_VIEW.md) bindet current-view.json
an genau diese Übergabe; das ist keine Bild-/Rasterwahl. Finalizer/Completion
ziehen tatsächliche Bindungen auch bei In-place-Fortschreibung nach. Frühphasen
sind keine Zertifikate; raster_ready/spätere Inhaltsphasen werden frisch geprüft.
Presentation enthält nur tatsächliche Angebote; weitere Raster referenzieren
bereits gesicherte qualifizierte Einzelrecords. Keine erfundene Galerie, kein
Projektwriter im lesenden Dienst.

Vollständige benötigte Originale einschließlich sichtbarer Alternativen, Index,
Projektion und Ansichtsverweis committen/pushen; feste Remote-Commit-/Dateipfade
wirklich prüfen. Sicherungscommit erst nach Erfolg melden; repo_commit ist nur
gelesene Herkunft. Lokale Pfade/localhost und ungesicherte SHAs sind keine
Cloudübergabe. Neuere Quellen ausdrücklich im Assistenten laden; bloße Suche
bewahrt gebundene Ansicht/Eingaben. Job-/Quellwechsel verwirft alte Auswahlabsichten.
Bei Wiederaufnahme aktuelle Quellen, gültige Freigaben, Budgets und offene Arbeit
prüfen; keine abgeschlossenen historischen Voraussetzungen erneut erfinden.

### 6.2 Übergabedatensatz

[PW-B_CONTRACT](../PW_B_CONTRACT.md) definiert unverändert Request v3, Handoff v4,
Record v3, Resultat v3, Rasterwahl, Inspektion v2 und Projektion v2. Für neue
Produktion genau die 0.8-Generation verwenden. Frühes background=null ist keine
Leerentscheidung; beide Hintergrundgates pending, ihre Belege null. Erst
background_review/content_ready besitzen Hintergrundarbeit und qualifizierte
Rasterwahl. Registered erst nach wirklicher Registrierung, Main erst nach
bestätigtem Merge berichten. Inventar v1, Index v1 und technische Bild-/Proof-/
Freigabeformen behalten; keine historischen Originale umetikettieren oder neu
versiegeln. Unsichere Restpfade, Konflikte und unvollständige Publikation offen
melden. Nur vollständig geprüfte identische Wiederholung ist No-op; keine
pauschale Locklöschung oder verdeckte Recovery.

### 6.3 Hintergrundarbeit in Schritt 4

Erst nach tatsächlicher Wahl eines qualifizierten Rasters Kontextbriefing und
drei inhaltlich unterschiedliche echte ImageGen-Originale erstellen, speichern
und isoliert vorlegen. Gemeinsamer [Bildstil](../PUZZLE_IMAGE_STYLE.md) und
[Q-HG-Kriterien](../PUZZLE_QUALITY.md#91-isolierte-visuelle-beurteilung) sind Pflicht:
leichte Graphitsprache, echte Transparenz und vollständige 2304×576-Komposition
mit ihrem Freiraum. Andere native Maße bilden dieselbe vollständige 4:1-Leinwand
ab; gemeinsamer Fit/Anker, kein Alpha-Bounds-Crop oder sichtmotivbezogenes Zentrieren.
Kontext statt Rätselsubjekt/Lösung/UI; indirekte Hinweise sind keine zugesicherte
Spoilerfreiheit. Nur tatsächliche dokumentierte Eigentümervorgabe erlaubt eine
andere anfängliche Bildzahl oder frühen Kandidatenverzicht. Fehlende Bilder sind
kein none. Die bedarfsweise Rasterregel verändert nicht diese Dreier-Bildauswahl.

Arbeitsmanifest/Entscheidung aus Hintergrundvertrag §3 verwenden. Wahl/none bindet
die tatsächlich vorgelegten Bytes. Rechte und isolierte Sichturteile bleiben
getrennt von Dateidiagnosen. Nur ausgewähltes Original gemäß HP-W2 §4 ableiten;
bei none echten Nullbefund prüfen. Keine Kandidaten-Testintegration, Buchvorschau
oder zusätzliche persönliche Buchabnahme. Geänderte kreative Bytes brauchen neue
Wahl; bytegleicher Transport und festgelegte Ableitung keine erneute kreative Wahl.
Eine offene Hintergrundwahl darf zusammen mit der tatsächlichen Endabnahme im
passend beauftragten Schlussauftrag erklärt werden; nicht dieselbe unveränderte
Entscheidung ein weiteres Mal verlangen. Die Schlussübersicht nach PW2-B bezeichnet die konkrete unveränderte Kombination.

## 7. Freigaben und Abschlussausgabe

Bild-, Motiv-/Parameter-, Raster-, Hintergrund- und finale redaktionelle
Entscheidungen stammen aus tatsächlichen menschlichen Erklärungen. Software
prüft Aufzeichnungen/Bytes, authentifiziert keine Menschen und ergänzt kein
Schweigen. Korrekturwünsche geben noch nicht vorhandene neue Fassungen nicht frei.

Jede Chatübergabe nennt kurz erreichte Phase, feste Quelle, tatsächlich ausgeführte
Prüfungen, offene Entscheidung und nächsten Schritt; echte Bild-/Dateilinks und
stabile Angebotskennungen. Keine Routine-JSON-Sammlung für ein zweites Sheet:
der Assistent liest veröffentlichte Originaldaten. Normale Produktion verwendet
ihr eigenes Abschlussformat, nicht Entwicklungs-HANDOFF.

Persönliche Arbeitswurzel und Merge bleiben ausdrücklich gewählte Auftragsoptionen,
keine Rechte aus einem Record oder einer Projektion. Normale Produktionsprompts
beauftragen keine zusätzliche lokale Ablagebereinigung; gesonderter Auftrag nach
WORKSPACE. Der fachliche Produktionsabschluss nach §9 bleibt davon unberührt.
Neue lokale Briefingentwürfe behaupten keine ID/Quelle/Freigabe. Eigene spätere
Hintergrundrevisionen benutzen HP-I1b2, keinen Alt-Sheet-Sitzungsimport.

## 8. Abgenommenes Paket ins Spiel integrieren

Schritt 5 setzt vollständige gültige Raster-/Hintergrundbereitschaft und echte
Endfreigabe v2 am unveränderten Original-ZIP voraus. Vorhandene äußere Entscheidung,
Ableitung und Endfreigabe über Finalizer v2 nachtragen; Originale bleiben bytegleich.
Atomare Recordfortschreibung und geprüfte Projektion verwenden denselben Stand.
Fehlende Freigaben sind keine technische Kleinigkeit.

Vor Erstintegration, Wiederaufnahme und jeder registrierenden Mutation tatsächlich
origin/main aktualisieren, vollständige SHA und beauftragten Zielcheckout feststellen.
Aktuelles main sicher in den Produktionsbranch einbeziehen, schmutzige WIP/Fremddaten
nicht überschreiben. Gültige Inhaltsregistry v4, die vom aktuellen gemeinsamen
Writer unterstützte Runtimegeneration und je ID genau eine aktuelle Metadatenzeile
mit gültiger Kategorie prüfen. Die [PE-A2-Zielregeln](../PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag)
gehören zum bestehenden Zielvertrag, nicht zu einer Migration durch dieses Regelpaket.
Veraltete/inkonsistente Ziele, Konflikte, Locks/Journale oder ungeklärte Recovery
stoppen vor Mutation; keine implizite Zielmigration oder Rückstufung.

Registered auf Draftbranch ist kein Mainabschluss. Bei verändertem Zielkatalog
mit unveränderten gebundenen Originalen und gültigen Freigaben frisch export → plan →
register gegen aktuellen Zielcheckout ausführen. Zielabhängige Index-/Runtime-/
Source-/Receipt-/Abschlussdaten fachlich neu erzeugen. Alte generierte Registries
nicht als Ersatz für aktuellen Bestand oder durch bloße Textkonfliktauflösung
übernehmen; alle bestehenden Inhalte/Metadaten erhalten. Original-ZIP, Raster-/
Revealbytes, historische Herkunft/Freigaben bleiben unverändert. Gültiges
Difficulty-Rebind benutzen, bei neuer ID --runtime-revision 1 beibehalten.
Technisch unmögliche Neubindung oder ungeklärte Herkunft konkret melden, nicht
erfinden/umschreiben. Keine direkte Mainmutation oder Umgehung von Guards.

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <finalize-v2.json> --source-root <neue-belege> --output-root <produktionscheckout> --history-repo <produktionscheckout>
python -m tools.puzzle_production.target_adapter export --allow-background --input <original-package.zip> --external-root <produktionscheckout> --approval <echte-endfreigabe.json> --name <motivname> --runtime-revision 1 --stem <stamm> --save-slot <slot> --category-id <kategorie> --categories content/categories.json --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter plan --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
python -m tools.puzzle_production.target_adapter register --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
```

Nur gewählte Lieferung übernehmen. Export v6 prüft vollständig vor Veröffentlichung;
frischer lesender Plan vor autorisierter Registrierung. Register plant selbst neu,
kein fremder Plan als Vertrauenscache. Historisch gespeicherte false-Readinessfelder
bleiben; Zielbereitschaft und registrierter Checkout werden frisch ermittelt.
RI, ZA-1 und aktuelle Katalogguards behalten sichere Pfade/Namespaces/Dateitypen,
Quelle/Capability/Provenienz, Bilder/Palette/Proof, Kategorie/Difficulty, IDs/Slots
und test_only. Keine Save-/Registry-/Runtimeänderung als Abkürzung.

Registrierung und Recovery behalten getrennte 1800-s-Schutzrahmen und 300-s-Warnung;
ein äußerer Ablauf darf Recovery nicht auf verbrauchte Restzeit beschränken.
Export/Plan/Eingangsprüfung behalten ihre eigenen Grenzen. Unterbrechung, Rollback,
offene Recovery und Abschluss getrennt berichten. Unklare/fremde Bytes und Journal
erhalten. Der bestehende BA-B-Runner bleibt nur bei ausdrücklich vorbereiteten
passenden Einzelintegrationen nutzbar, mit eigenen Mengen-/Budget-/Publikationsgrenzen.
Kein neuer Batchauftrag, versteckter Solverlauf oder zweites Hintergrundregister.

Nach wirklicher Registrierung Diff/Lieferbytes prüfen und Registrierungsstand
committen. Den Abschluss binden mit:

```text
python -m tools.production_workspace.projector --repository <checkout> --complete-record <recordpfad> --integration-commit <volle-SHA>
```

Record, Projektion und Ansichtsverweis danach committen/pushen und Draft-PR im
beauftragten Umfang erstellen. Reine Produktion erhält CI-Kern ohne Windowsbau
und ohne neue rätselspezifische Tests. Vor Merge aktuellen Head/Basis, unabhängiges
Review am tatsächlichen Stand, ausgewählte Pflichtchecks, Konfliktfreiheit,
erforderliche Abnahmen und ausdrückliche/bedingte Befugnis prüfen; Squash verwenden,
keine Release-/Deploymentfreigabe ableiten. Main erst am zurückgelesenen Mergecommit
melden; danach der revisionsgenaue Abschluss nach §9. Ein lokaler Erfolg reicht nicht.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: Ein fertiggestelltes und final auf main
integriertes Rätsel muss nicht erneut produzierbar sein. Produktionsunterlagen
sind Arbeitsmaterial, kein dauerhaft wachsender Spiel-/CI-Bestand.

1. Tatsächliche Endabnahme und Merge nachweisen, origin/main aktualisieren und
   vollständigen enthaltenen Commit nennen. Registered auf Draft genügt nicht.
   Neuere/offene Arbeit derselben ID zuerst klären, fremde/offene Produktion erhalten.
2. Nach Merge in eigenem kleinen Cleanup-Diff zuerst den
   [abgeschlossenen Ansichtsverweis](../PRODUCTION_CURRENT_VIEW.md) frisch gegen
   Revision/Mainbeleg prüfen und entfernen. Verweis auf neuere/offene Arbeit erhalten;
   bei ungeklärter ID vor Abschluss stoppen. Dann:

   ```sh
   python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <vollstaendige-main-SHA> --puzzle-id <pz-ID>
   ```

   Mehrere bestätigte IDs durch wiederholtes --puzzle-id. Der Befehl prüft Main-
   Abstammung und unveränderte Integrations-/Arbeitsbytes, entfernt abgeschlossene
   Authoringrevisionen/Indexeinträge und ersetzt das Produktionspaket durch einen
   kompakten Integrationsdatensatz. Kein Solver-, Proof- oder Bildreplay.
3. Dauerhaft bleiben Runtime-Definition mit Matrix/Hinweisen, Reveal, Rechte/Notices,
   ID/Runtime-Revision/Save-Slot, Kategorie und relevante Schwierigkeit. Kompakter
   Datensatz bindet diese Daten, ursprünglichen Exporthash und bestätigten Maincommit.
   Aktive Bildbindung samt Herkunft/Freigaben erhalten, nicht auf Vorgänger zurücksetzen
   oder historische Belege für nachträgliche Freigaben umschreiben. Aktive Bewertung,
   kompakte Berichte und Eingangs-/Methoden-/Referenzbindungen bleiben außerhalb
   versiegelter Produktion. Manuelle Neubewertung verlangt keinen Produktionsreplay.
4. Entfernt werden Quellen-/Abstraktionsbilder, verworfene Varianten, Prompts, ZIPs,
   duplizierte Exporte, Proofs, Reparaturspuren, Galerien und Zwischenberichte. Keine
   Kopien in neuen Archiven, Builds oder CI-Artefakten. Git-Historie und kompakte
   Commit-/PR-Entscheidungsbezüge genügen; Nutzungsrechte/Attribution nicht verlieren.
5. Diff und unveränderte Runtime kontrollieren, Cleanup committen/pushen, getrennt
   selbst prüfen und nach erfolgreichen Pflichtchecks unmittelbar mergen.
   Eigentümerfreigabe vom 15.10.2026: Genau dieser eng begrenzte Nachintegrations-
   Cleanup einschließlich Merge ist beauftragt, auch nach zuvor als Draft geliefertem
   Integrations-PR. Kein weiterer Routineprompt oder dauerhaft offener Cleanup-Draft.
   Vor tatsächlichem Integrationsmerge nichts bereinigen; konkrete Blocker melden.
   Eigener aktueller Paketplan mit begründet modules=[], Quellen-/Plankern ohne
   Player-Build und ohne rätselspezifische Tests. Maincommit/erhaltene Runtime nachweisen.

Spätere echte Rätseländerungen sind neue Aufträge. Fehlende alte Arbeitsdateien
sind kein Defekt und keine Wiederherstellungspflicht. Neue Exporte bleiben vollständig
geprüft; Bestandsregistrierung/Kategorienpflege benutzen die kompakte Integrationsbindung.
Diese fachliche Cleanupfreigabe erweitert keine lokale Checkoutbereinigung und
keine Befugnis für Werkzeug-/CI-Pakete.

### Abschluss nachträglicher Bildrevisionen · CI2 vom 26.10.2026

Spätere Revealrevisionen bereits integrierter Rätsel haben einen eigenen
revisionsgenauen Abschluss; eine bereinigte Rasterproduktion wird dafür nicht
wiederhergestellt. Vor Abschluss tatsächliche Bildfreigabe, aktive Bildbindung
und enthaltenen Maincommit prüfen; neuere/offene Arbeit erhalten. Zugehörige
erledigte Quellen, Prompts, Varianten, ZIP-/Rohkopien und Indexeinträge entfernen,
aber aktuelle Bilddatei, Rechte, Herkunft/Freigaben und aktive Revision behalten.
Definitionsbytes, Runtime-Revision, Save-Slot, Registrierung und Bewertungen bleiben.
Ursprüngliche versiegelte Integrationsbelege nicht neu erzeugen/umschreiben.

```sh
python -m tools.puzzle_production.target_adapter retire-reveal-production --checkout . --integrated-commit <vollstaendige-main-SHA> --authoring-revision <pz-ID> <Authoringrevision>
```

Jede Revision ausdrücklich wiederholen, kein impliziter ID-Gesamtabbau.
Origin/main vorher aktualisieren. Main muss Record, finale Freigabe und exakt
aktuelle Bildquelle binden. Offene Journale, fremde Bytes, Teilentfernung und
betroffene Indexänderungen blockieren vor Löschung. Neuere/offene Geschwister
bleiben. Identische Wiederholung nach vollständiger Entfernung ist nach frischer
Prüfung No-op, auch ohne alte Pakete. Unterstützte kompakte v1-Datensätze und
vollständige ursprüngliche Pakete unverändert belassen; retire-production bleibt
der Rasterabschlussweg. Begrenzter Datei-/Referenzvergleich, kein Solver-/Bild-/
Katalog-/Spielerreplay allein zur Bereinigung. Die enge Nachintegrationsfreigabe
aus §9 bleibt, nicht eine neue Befugnis aus historischen CI2-Lieferberichten.

### Abschluss der Hintergrundarbeit

[Hintergrundvertrag §10](../PUZZLE_BACKGROUNDS.md#10-hp-i1b1--erste-registrierung-und-kompakter-produktionsabschluss)
ergänzt Erstintegration: retire-production erhält aktive kompakte Hintergrundsource,
echte Freigabe-/Rechte-/Ableitungsbindungen, PNG/none/Notice und ursprünglichen
Exportanker; Mainbeleg separat im Receipt v2. Vor Löschung gewählte IDs/Bytes
gegen tatsächliches main prüfen. Offene/neuere/fremde Arbeit erhalten, bei nicht
trennbarem ID-Baum stoppen. Alte innere Refs sind danach historische Identitäten,
keine wieder zu öffnenden Pflichtdateien. Retire-reveal-production ist kein
Hintergrundabschlusswriter.

Bis Auswahl drei Einzelbilder erreichbar halten; bis tatsächlicher Integration
alle noch nötigen Arbeits-/Rechte-/Wahlbindungen. Nach bestätigter Endabnahme und
Mainintegration nur abgeschlossene Hintergrundarbeit entfernen: verworfene
Kandidaten, Prompts, Quellen-/Ableitungskopien, ZIPs und temporäre Review-/Diagnosedaten.
Kein Kandidatenarchiv, keine Wiederherstellung alter Rasterproduktion oder Solver-/
Bild-/Buchreplay. Aktives Asset bzw. echte Leerentscheidung, Rechte/Attribution,
aktive Bildrevision und kompakte Wahl-/Ableitungs-/Integrationsbindungen bleiben.
Historische Originale nicht umschreiben, aktive Bilder nicht zurücksetzen.

### HP-I1b2: eigene Hintergrundrevision und ihr Abschluss

[Hintergrundvertrag §11](../PUZZLE_BACKGROUNDS.md#11-hp-i1b2--eigenständiger-hintergrundwechsel)
definiert den unveränderlichen picross-background-adoption-request-v1. Tatsächliche
Auswahl/Entfernung und Zielautorisierung aufzeichnen, keine Dummy-ZIPs oder neue
Rasterfreigabe. Bytegleiche aktuelle Source/freigegebenes Reveal binden, ursprüngliche
Revealautorität in initial erhalten. Eigener Folgeauftrag nach §7.6 bleibt
unveränderlich; historische Sheetbedienung ist kein paralleler Assistent.
Aktuelle integrierte Herkunft lesen, Arbeitsrevision via catalog_background_change
store samt Index sichern, dann plan und autorisiertes adopt nach CLI. Fehlende/
false-Capability blockiert, kein Override. Gültige Freigaben nicht erneut verlangen;
Raster-/Revealneubindung folgt gegebenenfalls HP-I1c, nicht einem erfundenen Ersatzweg.

Nach bestätigter Mainintegration origin/main aktualisieren und gezielt ausführen:

```text
python -m tools.puzzle_production.target_adapter retire-background-production --checkout <checkout> --integrated-commit <vollständige-main-SHA> --authoring-revision <pz-ID> <revision>
```

Nur ausdrücklich gewählte vollständig belegte Revisionen/Indexzeilen entfernen;
neuere Arbeit, aktives PNG/none/Notice/Receipt bleiben. Eine inzwischen abgelöste,
tatsächlich integrierte Revision darf mit historischem Mainbeleg abgeschlossen
werden. Vollständig entfernte Revision plus Index ergibt nach frischer Prüfung
No-op, Teilreste nicht. Kein altes Raster-ZIP rekonstruieren oder Solver-/Buchreplay.
Der Befehl liefert lokalen Diff, keinen automatischen Commit/Merge.
