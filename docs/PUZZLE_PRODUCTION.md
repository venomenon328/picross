# Rätselproduktion: Bildentwurf, Deduktionsnachweis und Pilot

**AT · Abschlussbildtransparenz, freigegebener Sollvertrag vom 19.10.2026; noch nicht implementiert:**
[Abschlussbildtransparenz](REVEAL_TRANSPARENCY.md) ergänzt echte Transparenz für
neue Abschlussbilder und den eng begrenzten Austausch vorhandener Bildfassungen.
AT-A liefert den Produktionsstandard, die getrennte aktive Bildbindung und den
gemeinsamen abgesicherten Bildupdateweg; danach bearbeitet AT-B den gebundenen
Bestand samt tatsächlichen Bildfreigaben. Historische Produktions- und
Integrationsbelege bleiben unverändert. Die Spezifikationsfreigabe startet weder
Bildbearbeitung noch Raster-/Logikproduktion oder Integration.

**Prüfzuordnung für neue Arbeit (12.10.2026):** Sämtliche konkreten Rätselprüfungen
finden einmalig je relevanter Revision während der Produktion/Integration statt,
nicht in CI. Keine rätselspezifischen Unit-Tests oder Bestands-Replays hinzufügen.
[Regelwerk](ai-workflows/PUZZLE_AUTHORING.md) und [CI-Policy](CI_POLICY.md) ersetzen
die unten historisch dokumentierten pauschalen RP-Paket-/CI-Prüfpflichten.
Allgemeine Werkzeugtests mit festem synthetischem Testbestand bleiben erforderlich.

**SD / [#235](https://github.com/venomenon328/picross/issues/235), SD-C1 integriert (18.10.2026):**
[Rätselschwierigkeit](PUZZLE_DIFFICULTY.md) ergänzt die instrumentierte
Skala 1–5 und den ausdrücklich manuellen Bewertungsweg. [SD-A](SD_ANALYZER.md)
liefert den separaten Analysator; [SD-B](SD_CALIBRATION.md) ergänzt die eingefrorene
Methode 0.3 für den ausdrücklichen Einzelaufruf. Aktuelle Profile und
Produktionsverträge gelten weiter. Die Integration neuer Bewertungen erfolgt
über [SD-C1](SD_CATALOG.md); ein SD-B-Rating allein ändert keine Produktionsfreigabe.
Neue Registrierung und logisch geänderte Definitionen verlangen den extern vollständig
geprüften 0.3-Input. SD-C2 hat nach bestandenem Vor-Übernahme-Review gemäß SD-C2-F01
26 Bewertungen kontrolliert übernommen, einschließlich echtem Wiederholungs-No-op.
Separates qualifiziertes finales Datenreview und Merge bleiben offen.

[KAT-1](CATEGORIES.md) ergänzt den Produktionsfundus und ZA-1 um thematische Kategorien. Die Zuordnung steht spätestens vor dem kategorisierten Export fest und bleibt außerhalb von Raster-, Logik-, Proof- und Freigabeidentität. Arbeitsindex und Runtime-Registrierung bleiben getrennt.

Der [ZA-1-Zieladapter](ZA1_ADAPTER.md) verbindet Authoring-v2 mit regulärem Spiel
und kontrollierter Datenregistrierung. Frische RP-3-/vollständige RP-5-Prüfung und
an Originalhandoff, Inventar und Auswahl gebundene Endfreigabe sind erforderlich.
[Nachweise](ZA1_VERIFICATION.md). Alte Pilotprofile bleiben unverändert; keine
automatische Freigabe oder Katalogaufnahme des Beispiels.

Eigentümerentscheidung vom 11.10.2026 in [PERF-B/#68](https://github.com/venomenon328/picross/issues/68#issuecomment-6109644419): Reguläre Rätsel sind auf höchstens **50×50** begrenzt. Der aktuelle Katalog enthält ausschließlich Workflow-Inhalte. F01–F09 sind gemäß #114 aus dem Spiel entfernt. 100×100 ist ausschließlich eine optionale theoretische Performance-Stressgröße, keine aktuelle Produktabnahme. Frühere Größenpflichten in historischen Paketbeschreibungen gelten für neue Produktprüfungen nicht mehr.

Stand: 06.10.2026 · Arbeitsfassung 0.8 · RP-1 bis RP-6 integriert; aktueller Katalog gemäß #68

## 1. Geltung und Ziel

Für neue Rätsel gilt ergänzend die verbindliche
[KI-Arbeitsanweisung zur Rätselproduktion](ai-workflows/PUZZLE_AUTHORING.md).
Sie beginnt mit der Auswahl und Freigabe farbiger detaillierter Abschlussbilder;
daraus wird die separat freizugebende Motivvorlage für das Nonogramm abgeleitet.
Sie regelt Gestaltung, beide Bildfreigaben, Randregel, Schwierigkeit L1–L5 und
dateigebundene Übergaben auf Grundlage der hier bestehenden technischen Verträge.
Menschliches Probespielen ist für neue Rätsel kein Abnahmekriterium; Abschlussbildfreigabe,
Abstraktionsfreigabe und abschließende redaktionelle Abnahme bleiben verpflichtend. Die unten
dokumentierten RP-Paket- und Pilotabnahmen bleiben an ihre damaligen Aufträge gebunden.

Diese Spezifikation konkretisiert die Eigentümerentscheidung vom 03.10.2026 auf
Basis der [Produktdefinition](PRODUCT_DEFINITION.md), insbesondere §§3.2–3.4 und 4,
und der Motivtreue aus dem [Gestaltungskonzept](DESIGN_CONCEPT.md) §4.3.
Ziel ist ein externes Produktionswerkzeug für vorab kuratierte monochrome und
farbige Nonogramme. Es unterstützt vorhandene Bilder und gezielt vorbereitete
Motiventwürfe, erzeugt exakte Raster, prüft die vollständige deduktive Lösbarkeit,
unterstützt begrenzte Überarbeitung und liefert freigabefähige Inhaltsdatensätze.

Die erste Phase untersucht mit einer kleinen Vergleichsproduktion, welche
Motivarten und Größen mit vertretbarem menschlichem Aufwand funktionieren.
Einige Hundert Veröffentlichungsrätsel bleiben das Produktziel; sie werden durch
diesen Auftrag weder bestellt noch als technisch oder wirtschaftlich gesichert
zugesagt. Das Qualitätsversprechen gilt für jeden freigegebenen Datensatz.

Übergeordnetes Ziel und aktueller Paketstatus: [Rätselproduktion / RP](https://github.com/venomenon328/picross/issues/34).
Diese Datei führt den dauerhaften Fachvertrag. Issue-Bodies führen Scope,
Abhängigkeiten und Akzeptanz der einzelnen Pakete; PRs führen Änderungen,
Prüfbelege und Abnahmen. Der Spezifikationsauftrag enthält keine
Produktimplementierung und keine Mergefreigabe.

## 2. Verbindliche Entscheidungen

| Kennung | Festlegung |
| --- | --- |
| RP-D01 | Die Produktion erfolgt außerhalb des regulären Spiels. Der freigegebene Inhalt und das Solo-Spiel benötigen keine KI oder Onlineverbindung zur Laufzeit. |
| RP-D02 | KI wird ausschließlich innerhalb von ChatGPT oder Codex verwendet. Das Werkzeug besitzt keine direkte Modell-API-Anbindung, benötigt keine Modell-API-Keys und startet keine automatischen Modellaufrufe. |
| RP-D03 | Der Übergang zwischen KI-Arbeit und Werkzeug erfolgt über tatsächlich vorhandene Dateien und nachvollziehbare Briefings. Codex darf die deterministischen lokalen Werkzeuge ausführen. |
| RP-D04 | Exakte Zellwerte und Randhinweise werden durch Programmlogik erzeugt. Ein generiertes Bild mit sichtbarem Raster ist noch kein validierter Rätseldatensatz. |
| RP-D05 | Erstes ausreichendes Zertifizierungsprofil ist vollständige Linienlogik aus einem vollständig unbekannten Raster. Zusätzliche Startfelder sowie notwendige hypothetische Spielfortsetzungen mit Rücksprung sind ausgeschlossen. |
| RP-D06 | #139/B-D01 ergänzt die unabhängig prüfbaren Profile `paired-lines-mono` / `paired-lines-color` v1 gemäß [Paarlinienvertrag](PAIRED_LINES.md). B-D02 bindet notwendige Paarlinienlogik als R4/L5 unter Schwierigkeit 0.2. Weitere Regeln brauchen einen eigenen Vertrag. |
| RP-D07 | Logische Zulässigkeit, Motivqualität, Schwierigkeit, Bearbeitungsumfang und redaktionelle Freigabe werden getrennt erfasst. Ein technischer Erfolg ersetzt keine Motiv- oder Spielabnahme. |
| RP-D08 | Der Generator darf Entwurfsvarianten suchen, verwerfen und verändern. Jeder zur Freigabe vorgesehene Endstand braucht einen neuen, an genau diesen Stand gebundenen Nachweis vom unbekannten Raster aus. |
| RP-D09 | Motivschutz, Änderungsbudget und Suchbudget begrenzen automatische Reparaturen. Kein brauchbarer Kandidat gefunden ist ein reguläres Ergebnis; die Grenzen werden nicht zur Erzwingung eines Erfolgs gelockert. |
| RP-D10 | Monochromer Kern zuerst, unmittelbar folgende Farberweiterung auf derselben Fachstruktur. Rechteckige Raster und echte 100×100-Fälle werden früh untersucht; Laufzeiten werden gemessen, nicht vorausgesetzt. |
| RP-D11 | Ein erster neu erzeugter Kandidat wird bereits mit dem Bildimportpaket im P1-Spielablauf erprobt. Die vollständige Pilotproduktion folgt nach Vergleich und Reparatur. |
| RP-D12 | Erstes Werkzeug ist ein headless nutzbarer lokaler Ablauf mit einer einfachen lokalen Vergleichsansicht. Ein umfangreicher öffentlicher Editor oder eine vollständige Produktionsoberfläche wird erst aus dem Pilotbefund spezifiziert. |

## 3. KI-Arbeit und Bildvorbereitung

### 3.1 Dateibasierter Ablauf

Die produktionsverantwortliche Person oder ein beauftragter Agent erstellt in
ChatGPT/Codex ein Motiv beziehungsweise überarbeitet eine vorhandene Vorlage.
Das Werkzeug importiert die gespeicherte Ausgabe über denselben Pfad wie eine
gewöhnliche Illustration. Es entstehen keine Provideradapter, Prompt-Queues,
automatischen ChatGPT-Browserabläufe oder eigene Modellhosting-Komponenten.
Die tatsächlichen Fähigkeiten der jeweiligen ChatGPT-/Codex-Umgebung sind bei
Ausführung zu prüfen; fehlende Bildausgaben dürfen nicht durch behauptete Assets
oder eine verdeckte API-Integration ersetzt werden.

Ein Briefing hält mindestens Hauptmotiv, wichtige Merkmale, Zielabmessungen,
Mono-/Farbmodus, gewünschte Detailreduktion und erlaubte Abweichung fest.
Diagnosebilder und Berichte können für eine weitere ChatGPT-/Codex-Runde exportiert
werden. Die Rückgabe ist erneut eine Datei; der Logikprüfer erhält kein Motivwissen.
Es ist keine eigene Modellschulung erforderlich oder beauftragt.

Gespeichert werden das tatsächliche Original und verwendete Zwischenbilder,
Herkunft/Nutzungsfreigabe, Briefing, Bearbeitungsschritte und Dateihashes.
KI-Durchläufe und menschliche Arbeitszeit werden erfasst; eine reproduzierbare
Neugenerierung aus einem Prompt wird nicht zugesagt. Die deterministische
Reproduzierbarkeit beginnt an der konkret gespeicherten Eingabedatei.

### 3.2 Motivtreue und Rastervarianten

Zwei klar bezeichnete Arbeitsweisen sind vorgesehen:

- **Vorlagentreu:** Hauptgegenstand, wesentliche Formen und Bildaufbau erhalten;
  Ausschnitt, Detailreduktion und ausdrücklich begrenzte Korrekturen zulassen.
- **Freie Motivübertragung:** stärkere Vereinfachung und veränderte Gewichtung
  charakteristischer Merkmale zulassen; die gewünschte Neuinterpretation im
  Briefing festhalten. Kein stiller Wechsel aus dem vorlagentreuen Modus.

Die erste Importstrecke verarbeitet PNG und JPEG. Dekodierung, Bildorientierung,
Transparenz/Hintergrund und Farbraum werden eindeutig normalisiert und versioniert.
Ein normalisiertes Zwischenbild verhindert Abhängigkeit von unsichtbaren
Darstellungsunterschieden. Beschädigte oder nicht unterstützte Dateien erhalten
einen verständlichen Fehler. Ressourcenlimits für Bildgröße und Variantenanzahl
werden im jeweiligen Werkzeug dokumentiert.

Zielbreite und -höhe sind explizit; Seitenverhältnis nicht unbemerkt verzerren.
Zuschnitt, Hintergrundbehandlung, Flächen-/Schwellwert- oder Konturvariante und
eine begrenzte Palettenreduktion liefern mehrere nachvollziehbare Kandidaten.
Einfache klassische Verfahren bilden die Vergleichsbasis. Ein Qualitätsgewinn
gegenüber diesen Verfahren wird für KI-Stilisierung untersucht, nicht angenommen.
Alle Kandidaten verwenden exakte diskrete Zellwerte ohne Antialiasing-Zwischenwerte.
Hintergrund/Leer ist ein eigener Wert, keine Verwechslung mit einer hellen Rätselfarbe.

Das Werkzeug darf ein anderes Format oder eine stärkere Vereinfachung empfehlen.
Die universelle erfolgreiche Umwandlung jedes Bilds bei jeder Rastergröße ist kein
Versprechen. Die tatsächlich verwendeten Einstellungen und jeder ausgewertete
Fehlschlag gehören zum Produktionsbericht.

## 4. Gemeinsamer Daten- und Prüfvertrag

Das interne Produktionsformat bleibt vom Godot-P1-Ressourcenformat getrennt.
Ein Exportadapter übersetzt freigegebene Stände in das jeweilige Spielformat.
Die Produktionswerkzeuge sind kein Beschluss der endgültigen Spielengine,
Produktsprache oder Betriebssystemmatrix.

| Objekt | Mindestinhalt und Invariante |
| --- | --- |
| Motivquelle | Stabile Quellen-ID, Original/Normalisierung/Zwischenbilder mit Hashes, Herkunft, Briefing, Arbeitsweise und Bearbeitungsparameter. |
| Rasterentwurf | Stabile ID/Revision, Breite/Höhe, Zellmatrix mit Leerwert und stabilen Farb-IDs, Palette, Quellenbezug und Schutzinformationen. |
| Rätseldefinition | Dimensionen, vollständige geordnete Randhinweise mit Länge/Farbe, Regelversion und Bezug zum exakten Rasterentwurf. Die Hinweise müssen aus diesem Raster reproduzierbar ableitbar sein. |
| Logikeingang | Ausschließlich Dimensionen, Hinweise, Farb-/Abstandsregeln und initiale volle Zell-Domains. Keine Lösungsmatrix, Bilder, Motivnamen oder vorgegebenen Zellen. |
| Nachweis | Regelprofil-/Formatversion, Hash der relevanten Logikdaten, geordnete Schlussfolge mit prüfbaren Voraussetzungen und Folgerungen sowie Endstatus. |
| Qualitätsbericht | Getrennte technische Ergebnisse, Motivvergleich, geschätztes Schwierigkeitsprofil, Arbeits-/Rechenaufwand, offene Fragen und tatsächliche redaktionelle Bewertungen. |
| Exportmanifest | Exakte Definition/Revision, Nachweis- und Abschlussbildbezug, Palette/Assets, Hashes, Zieladapterversion und Freigabestatus. |

RP-1 konkretisiert serialisierbare Schemas und Schnittstellen für Logikeingang,
Ergebnis und Nachweis sowie die dafür erforderlichen Raster-/Hinweisbezüge,
Fehlerzustände, kanonische Hashbildung und Profilkennungen. Ergänzungen für weitere
Produktionsstufen folgen im jeweils zuständigen Paket. Zufall bei späterer
Varianten- oder Reparatursuche erhält gespeicherte Seeds und deterministische
Reihenfolgen. Betriebssystemabhängige Laufzeitmessungen gehören nicht in den
Identitätshash. Die deterministische Rasterisierung liefert mit unveränderter
Werkzeugversion, identischem normalisiertem Eingang und denselben Parametern
denselben Rasterstand. Für spätere Suche gilt dies bei identischen tatsächlich
ausgeführten Suchschritten. Ein Zeitlimit kann auf unterschiedlicher Hardware
verschiedene Teilverläufe beenden; deshalb tatsächliche Schritte und Ergebnisse
speichern und keinen identischen Suchausgang allein aus Seed und Zeitlimit zusagen.

### 4.1 Technische Konkretisierung RP-1

RP-1 verwendet Python 3.11+ mit ausschließlich Standardbibliothek als getrenntes
lokales Werkzeug unter `tools/puzzle_production/`. Der vollständige versionierte
Wire-/Hash-/CLI-Vertrag steht in der [Werkzeuganleitung](../tools/puzzle_production/README.md).
`picross-logic-v1` führt Dimensionen, geordnete Länge-/Farbhinweise, Leerwert,
stabile Vordergrund-ID `ink`, `mono-gap-v1` mit Pflichtabstand 1 und eine volle
Broadcast-Startdomain für jede Zelle. Keine Lösung/Asset-/Motivfelder oder
Vorbelegungen. `picross-proof-v1` bindet Logikhash und exaktes Profil
`full-line-mono` Version 1, geordnete Linien-/Domainänderungen und Endstatus samt
Enddomains/Widerspruchsreferenz. Kanonische JSON-UTF-8-Bytes mit sortierten Schlüsseln,
ohne Whitespace/BOM/Abschlusszeile werden mit SHA-256 gebunden; Messdaten bleiben außen vor.

Der Solver nutzt Zellautomaten-Erreichbarkeit, der unabhängig implementierte Prüfer
einen Blockintervall-DAG mit eigener Intervallkompatibilität. Gemeinsam sind nur
Vertrag/Validierung, Datentypen, Domainkonvention, Budgets und Hashbildung.
Vollständige Endraster werden zusätzlich direkt gegen die Hinweise geprüft;
Fixpunkt/Widerspruch erhalten eigenständige Statusprüfung. Nur der erfolgreich
geprüfte vollständige Status wird als zertifiziert ausgegeben.

### 4.2 Technische Konkretisierung RP-2

RP-2 erweitert denselben Python-/Standardbibliothekskern. `picross-logic-v2`,
`picross-proof-v2`, `color-gap-v1` und `full-line-color` Version 1 binden gemeinsam
geordnete Länge-/Farbhinweise, volle Startdomains und partielle Farbausschlüsse.
Unterstützt werden 1..8 stabile Vordergrund-IDs plus Leer und 1..100 je Achse.
Die Palette wird lexikografisch normalisiert; semantische IDs bleiben erhalten.
Die alten Monoformate/-profile und ihre Hashbedeutung bleiben prüfbar; ein vor
der Erweiterung erzeugter unveränderter RP-1-Nachweis ist eine Testfixture.
ID-Grammatik, kanonische Domains, Dateilimits und vollständiger Wire-Vertrag stehen
in der [Anleitung](../tools/puzzle_production/README.md).

Zellautomat und unabhängig implementierter Blockintervall-DAG berücksichtigen
Farben gemeinsam. Jeder Domainverlust wird gespeichert und an Kreuzungen propagiert;
kein Singletonzwang für Fortschritt. Die maximale Schrittzahl ist Breite·Höhe·K
bei K Vordergrundfarben, abgeleitet aus monoton entfernbaren Werten. 2 MiB Eingang,
8 MiB Mono-/64 MiB Farbnachweis und kooperative Arbeits-/Zeitbudgets sind begründet
und an Grenzen geprüft. Vollständige Endraster werden zusätzlich durch direkte
Runextraktion einschließlich berührender Farbwechsel geprüft. Kein zweiter
Prüfkern, Spieladapter, Bildimport oder Suchprofil wird eingeführt.

### 4.3 Technische Konkretisierung RP-3

Bildbefehle verwenden die separate isolierte Abhängigkeit Pillow 12.3.0;
der Logikkern bleibt Standardbibliothek. `picross-image-design-v1` bindet Quelle,
Herkunft/Nutzungsgrundlage, Briefing, vorlagentreue oder freie Arbeitsweise,
Zieldimensionen, orientierten Ausschnitt, expliziten Fit, Hintergrund/Alpha,
Mono-/Farbpalette und höchstens acht Flächen-/Konturvarianten.
PNG/JPEG werden strikt dekodiert, EXIF inklusive Spiegelung angewendet und ICC
nach sRGB transformiert. Ungetaggte RGB-/Graubilder gelten ausdrücklich als sRGB.
Originalbytes und normalisiertes RGBA-PNG bleiben getrennt erhalten.

32 MiB Dateigröße, 8 Millionen dekodierte Pixel und 8192 je Quellachse begrenzen
den Import. Die endgültige Matrix enthält nur stabile Paletten-IDs/Leer;
vollständige Hinweise entstehen ausschließlich durch Runextraktion daraus.
`picross-image-candidate-v1` bindet Normalisierungshash, Entwurf, Variante,
Werkzeug-/Codecversionen, Matrix und Logikhash; Zeiten sind keine Identität.
`picross-image-manifest-v1` führt tatsächliche Dateihashes und getrennte technische,
Motiv- und redaktionelle Status. Eine statische Offline-HTML-Seite zeigt den
vollständigen Vergleich samt Raster bei echter Zellauflösung.

`picross-p1-export-v1` / Adapter `rp3-p1-square-mono-1` rekonstruiert die gebundene
Quelle und Matrix, leitet Hinweise neu ab, prüft den gespeicherten Nachweis
unabhängig und vergleicht die bewiesenen Enddomains mit der Matrix. Erst ein
vollständiges Zertifikat erlaubt den Export. P1 erhält Leer 0 und fortlaufende
Paletten-IDs 1..N, ausdrücklich im Manifest; erster registrierter Inhalt ist F-04.
Andere als quadratische monochrome Kandidaten und lokale SVG-Enthüllungen werden
in diesem ersten Adapter abgewiesen. Die Produktion unterstützt weiterhin Farben,
Rechtecke und 100×100. Details/Grenzen: [Anleitung](../tools/puzzle_production/README.md),
[reales Beispiel](../examples/rp3/README.md), [Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP3_VERIFICATION.md).

### 4.4 Technische Konkretisierung RP-5

`picross-repair-plan-v1`, `picross-repair-v1` und eigenes Reparaturmanifest
binden unveränderten geprüften Import, Farbsemantik, boolesche Schutzmaske,
festgelegte Suchkonfiguration/Seed, tatsächliche Vorschläge/Elternänderungen,
alle Kandidaten und Endmatrix. Keine Umetikettierung als unveränderter RP-3-Import.
Der [Paketvertrag](../examples/rp5/README.md) dokumentiert genaue Hash-/Zähler-/
Ressourcengrenzen und Abbruch-/Replayregeln; [Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP5_VERIFICATION.md).

Einzellokale Änderungen, Manhattan-Priorität um ursprünglich offene Zellen,
SHA-256-Tiereihenfolge und begrenzte Frontier genügen dem Paket. Partielle
Farb-Domainverluste, offene Zellen und Änderungsabstand bleiben getrennte
Merkmale. Schutz und Abstand werden vor jeder Bewertung kontrolliert;
Duplikate/Rücknahmen/verworfene Varianten verbrauchen kumulative Vorschläge.
Ein gemeinsames Suchbudget umfasst Importrekonstruktion und alle Solve-/
Prüfoperationen; die frische Abschlussprüfung besitzt ihr eigenes vorab
festgelegtes Zeit-/Linienbudget. Kooperative Grenzen sind keine harten OS-Limits.
Abgebrochene Abschlussprüfung verleiht keine Freigabe, auch wenn ein späterer
Replay den gespeicherten Proof bestätigen kann.

Jede Matrix und ihre Hinweise werden neu rekonstruiert, jeder geschriebene
Proof unabhängig vom unbekannten Raster geprüft. Nur ein vollständig geprüfter
Endproof mit identischen Singleton-Enddomains erlaubt logische Freigabe.
Der v1-P1-Adapter weist Reparaturmanifeste ausdrücklich zurück; RP-5 selbst
lieferte kein neues Zielprofil. Der additive RP-6-v2-Adapter ist unten festgelegt.
Manuelle Rasterkorrekturen werden als neue Eingabedatei/-revision importiert
und verlangen eine neue vollständige Prüfung.

## 5. Deduktionsnachweis

### 5.1 Erstes Profil: vollständige Linienlogik

Jede Zelle beginnt mit allen nach dem Farbmodus möglichen Werten. Für eine Linie
werden sämtliche Belegungen berücksichtigt, die ihren vollständigen Hinweisen
und den bereits sicher eingeschränkten Zell-Domains entsprechen. Ein Wert darf
genau dann ausgeschlossen werden, wenn keine solche Belegung ihn an dieser
Position unterstützt. Singleton-Domains bestimmen die entsprechende Zelle.
Veränderte Domains werden an kreuzende Linien weitergegeben. Vollständige
Iteration endet bei gelöstem Raster, bewiesenem Widerspruch oder Fixpunkt.

Die Linienauswertung muss auch partielle erzwungene Werte finden, wenn die ganze
Linie noch mehrere mögliche Belegungen hat. Bloße linke/rechte Extremplatzierung
ist ohne Vollständigkeitsnachweis kein Ersatz. Der Prüfkern darf vollständige
Belegungslisten nicht als skalierenden Standardweg verwenden; dynamische
Programmierung oder eine gleichwertige vollständige Zustandsanalyse ist vorgesehen.
Kleine unabhängige Belegungsaufzählungen sind als Testoracle sinnvoll.

Unzulässig in diesem Profil sind hypothetische Rasterfortsetzungen, Probing,
Backtracking oder Folgerungen aus dem bekannten Bild, einer vermuteten Symmetrie
beziehungsweise der bloßen Zusage einer eindeutigen Lösung. Deterministische
Ausführungsreihenfolge allein bedeutet nicht, dass ein Solver ohne solche
Versuchsschritte arbeitet.

### 5.2 Farben und Grenzen

Gleichfarbige benachbarte Hinweisblöcke benötigen mindestens ein Leerfeld;
unterschiedliche Farben dürfen sich berühren oder durch Leerfelder getrennt sein.
Farben werden gemeinsam gelöst, nicht als unabhängige monochrome Kanäle.
Auch ein sicherer Ausschluss wie nur noch Blau oder Leer ist ein Fortschritt,
obwohl noch keine endgültige Zelle feststeht. Der Vertrag ist deshalb bereits
in RP-1 domainfähig; RP-2 implementiert und prüft die Mehrfarbenfälle auf derselben Grundlage.

Der erste unterstützte Bereich umfasst positive rechteckige Dimensionen bis
einschließlich 100 je Achse. Kleine Randfälle und 1×N/N×1 gehören zur Fachprüfung.
Die erste Farberweiterung weist mindestens die vier bereits im P1 verwendeten
Vordergrundfarben plus Leer nach. Eine konkrete höhere Palettenobergrenze wird
im Werkzeug ausdrücklich angegeben; unbegrenzte Farben werden nicht versprochen.
Das spätere Produktziel jenseits von 100×100 bleibt hiervon unberührt.

### 5.3 Getrennte Ergebnisse

| Status | Bedeutung |
| --- | --- |
| Vollständig nachgewiesen | Alle Zellen wurden ausschließlich durch erlaubte Schritte bestimmt und erfüllen die Randhinweise; der unabhängige Prüfer hat den Nachweis einschließlich Endstatus bestätigt. |
| Fixpunkt unvollständig | Vollständige Linieniteration kann keine weitere Domain einschränken. Das ist kein Beweis für Mehrdeutigkeit oder notwendiges Raten mit anderen Profilen. |
| Widerspruch | Mindestens eine Linie besitzt nach den gesicherten Voraussetzungen keine zulässige Belegung beziehungsweise eine Domain ist leer. |
| Abgebrochen/nicht abgeschlossen | Zeit-/Ressourcenlimit oder Abbruch; weder Eindeutigkeit noch Ungültigkeit sind dadurch bewiesen. |
| Ungültiger Eingang/Fehler | Format, Parameter oder interner Ablauf sind fehlerhaft. Nicht als logische Eigenschaft des Rätsels ausgeben. |

Existenz, Eindeutigkeit und Profilnachweis sind getrennte Aussagen. Eine korrekt
aus dem Entwurf abgeleitete Hinweismenge besitzt bereits den Entwurf als Lösung.
Ein korrekter vollständiger Deduktionsnachweis bestimmt jede Zelle zwingend und
beweist damit zugleich Eindeutigkeit. Ein allgemeiner zusätzlicher SAT-/Suchsolver
ist für diese Phase optional, kein Pflichtbestandteil. Wird er zur Diagnose
eingesetzt, bleiben sein Modus und sein Ergebnis getrennt; er ersetzt niemals
den Profilnachweis. Mehrdeutigkeit ist nur mit entsprechendem Nachweis, etwa zwei
verschiedenen gültigen Lösungen, als festgestellt auszugeben.

### 5.4 Unabhängige Nachweisprüfung

Der Prüfer rekonstruiert die Domains vom unbekannten Start aus, bindet den Nachweis
an die tatsächlich geprüften Logikdaten und prüft jeden Schluss selbstständig.
Ein Aufruf derselben Herleitungsroutine und Vergleich ihres Logs ist keine
unabhängige Nachweisprüfung. Gemeinsame Format-/Eingabevalidierung darf verwendet
werden; die Rechtfertigung einer Folgerung muss unabhängig vom Ergebnis und den
internen Flags des erzeugenden Solvers erfolgen. Das konkrete unabhängige Verfahren
wird im RP-1-PR begründet und durch gezielt verfälschte Nachweise abgesichert.

Der Nachweis beschreibt Linienbezug, vorangehenden Zustand beziehungsweise
rekonstruierbare Voraussetzungen und neu ausgeschlossene Werte. Jeder Ausschluss
muss aus den Linienbedingungen folgen; keine unbegründeten Startannahmen.
Der Prüfer bestätigt auch den beanspruchten Endstatus. Bei vollständigem Abschluss
müssen alle Domains eindeutig sein und sämtliche Hinweise erfüllt werden. Bei
einem unvollständigen Fixpunkt bleiben unbestimmte Zellen; zugleich bestätigt eine
vollständige unabhängige Prüfung aller Linien, dass keine weitere Domain
eingeschränkt werden kann. Ein beanspruchter Widerspruch benötigt einen unabhängig
bestätigten Widerspruchsgrund aus den geprüften Voraussetzungen. Eine korrekt
geprüfte Teilspur allein bestätigt weder Fixpunkt noch Abschluss. Ein Abbruch
bleibt als solcher bezeichnet, auch wenn die bis dahin vorliegenden Schritte
korrekt sind.

Bei vollständigem Abschluss wird anschließend separat die Übereinstimmung mit
dem beabsichtigten Raster geprüft. Geänderte Logikdaten machen
einen alten Nachweis ungültig; reine Assetänderungen erhalten einen neuen
Manifeststand und eine erneute Zuordnungs-/Motivprüfung.

Für den freigegebenen [AT-Sollvertrag](REVEAL_TRANSPARENCY.md) werden ursprüngliche
Bild-/Paket-/Integrationsbindungen dabei nicht rückwirkend umgeschrieben. Die
neue Bildrevision, ihre tatsächliche Freigabe und der aktive Bildhash werden
außerhalb der historischen Belege nachvollziehbar gebunden. Definition samt
Runtime-Revision, Raster, Hinweise, Identität, Ressourcenpfade, Slots, Ratings und
Hinzugefügt-Daten bleiben bei einem reinen Bildupdate unverändert. Dafür entsteht
kein neuer Logik-, Proof- oder Schwierigkeitslauf. Der gegenwärtige Rasterupdateweg
ist kein Bildupdateweg; die zusätzliche Technik und ihre synthetischen
Regressionen gehören zu AT-A, die konkrete Motivbearbeitung und Bildabnahme zu AT-B.

### 5.5 Separate Eindeutigkeitsdiagnose (#139, Paket A)

Die additive Diagnose untersucht ausschließlich validierte Logikeingänge v1/v2,
ohne Zielmatrix, Motivwissen oder Vorbelegungen. Die intern verzweigende vollständige
Domain-Suche erzeugt keine Deduktionsschritte. Bestehende Profile, Proof-/Logikhashes,
Import-/Reparatur-/ZA-1-Zertifizierung und Produktionsfreigaben bleiben unverändert.

`unique` (eindeutig) verlangt genau einen unabhängig geprüften Lösungszeugen und
vollständige Erschöpfung aller Suchzweige. `no_solution` (keine Lösung) verlangt
vollständige Erschöpfung ohne Lösung. `multiple` (mehrdeutig) verlangt zwei verschiedene,
unabhängig gegen dieselben Hinweise geprüfte Endmatrizen; danach endet die Suche.
`unknown` erlaubt kein abschließendes Urteil, auch nach einer gefundenen Lösung.
Ungültiger Eingang und technische Fehler bleiben gesonderte Fehlerzustände.

Ein neues Diagnoseverzeichnis bindet exakte Eingabebytes und geprüfte Lösungsdateien
per SHA-256 und Bytezahl an `picross-uniqueness-v1` mit Werkzeugversion, Methode,
kumulativen Budgets, tatsächlichen Zählern und Endgrund. Die notwendige Prüfung der
geschriebenen Zeugen gehört zum Suchbudget. `check-diagnosis` prüft Dateibindungen und
Zeugen unabhängig durch direkte Runextraktion; es replayt keinen Suchbaum und
bestätigt allein aus einem Zeugen weder Eindeutigkeit noch Unlösbarkeit.
Vollständigkeitsargument, Reihenfolge, Formate, Grenzen und CLI stehen in der
[Werkzeuganleitung](../tools/puzzle_production/README.md).

Die Diagnose ersetzt weder Produktionsmanifest noch vollständigen Deduktionsnachweis;
`certified` bleibt stets falsch. `unique` bei bisherigem `stalled` erlaubt keine
Produktionsfreigabe oder neue Schwierigkeitsstufe. Die bestätigten B/C-Regeln
stehen im folgenden Abschnitt; Diagnose A bleibt davon getrennt.

### 5.6 Paarlinienprofil und nachgewiesener Technikbedarf (#139 B/C)

Der [vollständige Vertrag](PAIRED_LINES.md) definiert Regel, unabhängige Herleitung,
Proof-v3, Reihenfolge und kumulative Ressourcen. Zwei beliebige gleichgerichtete
Linien werden gemeinsam betrachtet. Jede Kreuzlinie liefert die exakte Relation
der Werte an beiden Kreuzungen. Entfernt werden ausschließlich Werte außerhalb
der vollständigen Projektion aller kompatiblen Linienpaare. Keine hypothetische
Rasterfortsetzung, keine Sollwerte und keine Eindeutigkeitsprämisse.

Neue Profile werden ausdrücklich gewählt. Alte Logik-/Proofbytes und Standardaufrufe
bleiben unverändert. Neue Import-/Reparaturversionen binden Profil, Budgets,
eigenen Linienbaseline-Proof und Assessmentdatei. Endmatrix, ursprüngliche Abbrüche,
Motivschutz und menschliche Freigaben behalten ihre Wirkung. Ein starker Fixpunkt
schöpft alle Einzel- und alle ungeordneten Paarlinien aus; Zeit-/Arbeitsende ist
Abbruch. Ein Widerspruch wird ohne Anwendung einer leeren Projektion belegt.

`picross-difficulty-0.2` ergänzt R4 innerhalb L1–L5. Ausschließlich ein separat
dateigebundener, unabhängig bestätigter `full-line-* / stalled` und vollständiger
geprüfter Paarproof derselben Logik begründen R4, L5 und „linienübergreifend /
besonders hoher logischer Anspruch“. Solververwendung allein genügt nicht.
R0–R3-Kriterien und alte 0.1-Bewertungen bleiben erhalten. Instrumentiert wird
R4-Notwendigkeit, kein vollständiger R0–R3-Analysator und keine menschliche
Kalibrierung. Unvollständige Nachweise erhalten keine Freigabe durch eine hohe Zahl.

`assess` berichtet Diagnose, Deduktion, Technikbedarf und Umfang getrennt.
Ein aus A übernommenes `unique` bleibt ausdrücklich ein berichtetes Suchurteil:
der Zeugenchecker replayt keine erschöpfende Suche. Zwei geprüfte verschiedene
Zeugen bestätigen Mehrdeutigkeit. Vollständige Deduktion beweist selbst Eindeutigkeit.
Authoring 0.5.0 und ZA-1-v4 binden die neuen Profile ausdrücklich; alte Snapshots
oder alte Exportformate können sie nicht durch gelockerte Flags legitimieren.

## 6. Überarbeitung und Motivschutz

Ein zur Reparatur ausgewählter Entwurf ist die unveränderte Vergleichsreferenz.
Geschützte Zellen/Bereiche gelten hart; dazu gehören bei Bedarf auch wichtige
Leerstellen wie ein Henkelinnenraum. Das Änderungsbudget begrenzt bei jedem
bewerteten Kandidaten die Anzahl gegenüber der Referenz veränderter Zellwerte.
Hinzu kommen separate kumulative Grenzen für Suchschritte, Kandidaten und
Rechenzeit; temporäres Zurücknehmen setzt diese Suchbudgets nicht zurück.
Parameter werden vor dem Lauf festgelegt und protokolliert.

Zunächst genügen einzelne Zelländerungen und wenige nachvollziehbare lokale
Formänderungen. Neue Abmessungen, ein anderer Ausschnitt oder eine neue Stilisierung
sind ein neuer Entwurfsauftrag mit neuer Referenz, kein versteckter Reparaturschritt.
Die vollständigen Hinweise werden für jeden bewerteten Kandidaten neu abgeleitet.
Der endgültige Nachweis gilt vom unbekannten Raster aus; alte Teilbeweise und
Caches dürfen nur bei nachweislich identischen Eingaben wiederverwendet werden.

Die Bewertung berücksichtigt logischen Fortschritt, Abweichung vom Entwurf und
gemessene Aufwandsmerkmale. Sie darf Schutzgrenzen nicht durch einen besseren Score
überstimmen. Weniger unbekannte Zellen sind ein Suchsignal, keine Erfolgszusage;
Verbesserung muss nicht mit jeder einzelnen Änderung monoton sein. Abbruch oder
kein akzeptabler Kandidat gefunden werden regulär berichtet. Vorher-/Nachher-
Ansicht zeigt alle Änderungen. Jede manuelle Rasteränderung verlangt ebenfalls
erneute Prüfung, bevor eine logische Freigabe möglich ist.

## 7. Qualitätsurteil, Vergleichsproduktion und Pilot

### 7.1 Getrennte Qualitätsachsen

Technisch geprüft werden Logikdaten, vollständiger Nachweis, Reproduzierbarkeit
und Exportidentität. Redaktionell beurteilt werden Hauptmotiv, wesentliche Formen,
Innenräume, störende Details, tatsächlicher Lösungsverlauf und Motivtreue des
Abschlussbilds. Ein monochromes Rätsel darf gemäß
Produktdefinition durch die kolorierte Enthüllung verständlicher werden; ein
Farbrätsel soll bereits selbst als Bild erkennbar sein.

Historische Produktionsbewertungen behalten 0.1/0.2 aus Authoring §5 einschließlich
ihrer Schätzgrenzen. Neue Integrationen verwenden zusätzlich 0.3 nach
[SD-C1](SD_CATALOG.md): geprüfte R0–R3-Regeln, synchrone Bewertungswellen,
gemeinsam erfasste Fortschrittsmöglichkeiten und belegte Engstellen. Die
eigene Bewertungsspur ersetzt keinen bestehenden Proof. R4-Notwendigkeit wird
weiterhin nach §5.6 unabhängig belegt; auch anspruchsvolle reine Linienfälle
können Stufe 5 erreichen. Alte Bewertungen behalten ihre Methodensemantik.

Logische Basis, begrenzter Größenbeitrag und Katalogstufe werden getrennt
berichtet; CPU-Zeit, Farbzahl oder Eingabemenge allein begründen keinen hohen
Grad. SD-B bindet feste Grenzen anhand unabhängiger synthetischer Referenzen.
Der reale Katalog ist weder Kalibrierungskorpus noch automatischer Testbestand;
er dient erst danach einer beauftragten manuellen Plausibilitätsprüfung.
Synthetische Kalibrierung ist kein Nachweis menschlicher Lösungszeit oder
empirisch validierter Schwierigkeit. Spielerwertung bleibt unabhängig;
Probespielen bleibt optional. Neue Rätsel erhalten nach finaler Deduktionsprüfung
denselben manuell gestarteten Analyseweg wie ausgewählte Bestandsrätsel.

## Historische Machbarkeitsphase

RP-1 bis RP-6 sind abgeschlossen. Vergleichskorpus, Sechserpilot, damalige Exporte,
Abnahmen und Paketfolge sind im [gebundenen Vorgänger](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/PUZZLE_PRODUCTION.md)
und den ursprünglichen Issues/PRs dokumentiert. Sie werden weder erneut produziert
noch dauerhaft im aktiven Tree aufbewahrt. Aktuelle Registrierung folgt
[ZA-1](ZA1_ADAPTER.md), neue Rätsel dem [Authoringworkflow](ai-workflows/PUZZLE_AUTHORING.md).
Nach bestätigter Main-Integration werden Produktionsunterlagen entfernt; benötigt
bleiben nur Runtime-Inhalte, Nutzungsgrundlage, Metadaten und kompakte Integrationsbindung.
Reproduzierbarkeit während der Produktion ist keine lebenslange Aufbewahrungspflicht.

Ab SD-C1 bleiben außerdem die kompakte aktive Bewertung, ihre
Eingangsbindungen und der gebundene Methoden-/Referenzstand erhalten. Diese liegen
außerhalb versiegelter Produktionsoriginale und ermöglichen die beauftragte
Neubewertung aus aktuellen Logikeingängen nach SD-D09/D10. Daraus entsteht keine
allgemeine Pflicht zum Produktions-Replay oder zur Wiederherstellung alter Pakete.

Über das Paarlinienprofil hinausgehende Regeln, menschlich kalibrierte Schwierigkeit, öffentliche
Editoren und Veröffentlichung bleiben gesonderte Folgeentscheidungen.
