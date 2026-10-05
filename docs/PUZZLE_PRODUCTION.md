# Rätselproduktion: Bildentwurf, Deduktionsnachweis und Pilot

Stand: 05.10.2026 · Arbeitsfassung 0.6 · RP-1 bis RP-3 integriert; RP-4-Baseline und R1-Nacharbeit

## 1. Geltung und Ziel

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
| RP-D06 | Die bereits erlaubten linienübergreifenden Deduktionen bleiben als späterer Ausbau möglich. Das erste Profil ist keine endgültige Beschränkung des Produkts; zusätzliche Regeln brauchen einen eigenen nachvollziehbaren Vertrag. |
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
[reales Beispiel](../examples/rp3/README.md), [Prüfzuordnung](RP3_VERIFICATION.md).

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

Schwierigkeit ist zunächst eine versionierte Schätzung anhand tatsächlicher
Ableitungen, Regelbedarf, Engstellen, angebotener Fortschritte und ihrer Verteilung.
Rastergröße, Eintragungsumfang, Hinweislängen und Rechenlaufzeit werden separat
berichtet. CPU-Zeit oder Schrittzahl allein ergeben keine menschliche Schwierigkeit.
Reihenfolge/Strategie der Auswertung und Aggregation sind zu dokumentieren; keine
verbindlichen Stern- oder Schwierigkeitsstufen und keine Spielerwertung entstehen.

### 7.2 Vergleichsproduktion RP-4

Vor der Auswertung wird ein Korpus von zwölf Quellen festgelegt: je drei klare
Illustrationen, gezielt in ChatGPT/Codex erzeugte Vorlagen, Fotos mit gut
abgrenzbarem Hauptobjekt und schwierigere Fotos mit relevanten Innenstrukturen,
Texturen oder Überlagerungen. Herkunft und tatsächlich verfügbare Dateien müssen
geklärt sein. Ein späterer Austausch wird begründet; Fehlschläge verschwinden
nicht durch stilles Aussortieren.

Für die sechs Fotofälle werden direkte Verarbeitung und eine in ChatGPT/Codex
erstellte Stilisierung paarweise verglichen, mit gleicher Zielgröße, gleichem
Motivauftrag und vergleichbarem Variantenbudget. Weitere Paare sind möglich,
aber keine vollständige Kombination aller Größen/Filter/Quellen erforderlich.
Jede Quelle hat eine passende Hauptgröße; mindestens vier unterschiedliche
Quellen erhalten einen echten 100×100-Versuch. Mono- und Mehrfarbenfälle sowie
mindestens ein rechteckiges Format werden untersucht. Hochskalierte kleine Raster
zählen nicht als echte Großmotivproduktion.

Zu jedem Versuch gehören Dateien/Hashes, Einstellungen, alle ausgewerteten
Kandidaten, logischer Status, Motivurteil und verbleibender Änderungsbedarf.
Menschliche Arbeitszeit wird getrennt nach Vorbereitung, ChatGPT-/Codex-Runden,
Rasterkorrektur und Sichtprüfung erfasst; Schätzungen werden gekennzeichnet.
KI-Runden, Rechenzeit, Solveraufrufe und Variantenanzahl werden separat gezählt.
Zielmaß ist brauchbarer Inhalt pro menschlichem Arbeitsaufwand, keine API-Kostenrechnung.

### 7.3 Pilot RP-6 und Aussagegrenzen

Angestrebt werden sechs redaktionell freigegebene Rätsel mit mindestens zwei
monochromen und zwei farbigen, mindestens zwei Motiven mit beiden Dimensionen
größer als 40, darunter ein echtes 100×100-Motiv. Dieses Größenkriterium dient
der Pilotabdeckung, nicht einer allgemeinen Definition großer Rätsel.
Diese Produktionsziele sind Untersuchungsziele, keine
Erlaubnis, Qualitätsgrenzen zu senken oder zusätzliche unbegrenzte Arbeit anzuhängen.
Nicht erreichte Ziele werden mit Ursache, Daten und konkretem Folgevorschlag
ausgewiesen. Ein negativer Machbarkeitsbefund kann ein korrekt abgeschlossener
Versuch sein; er ist kein Nachweis erreichter Katalog-/Großrasterqualität.

Jeder tatsächlich als freigegeben bezeichnete Pilotdatensatz erfüllt alle
Qualitätsbedingungen und besitzt ein zum finalen Raster passendes Abschlussbild.
Die gezielte Sichtprüfung vergleicht zunächst Raster und Enthüllung sinnvoll,
danach bei Bedarf die Quelle. Die bestehende erlaubte Verfeinerung von Konturen,
Details und Schattierung bleibt erhalten; keine Pflicht pixelidentischer Silhouetten.
Abschlussbilder können in ChatGPT/Codex entstehen und werden als Dateien übernommen.

Reale Eigentümerproben prüfen mindestens ein neues monochromes und ein neues
farbiges Rätsel mit dem benannten Windows-Artefakt, Lösungsverlauf und Abschluss.
Eine repräsentative große Probe wird vollständig gelöst oder über dokumentierte
Sitzungen fortgesetzt; ihr konkreter Umfang wird vor dem Versuch festgelegt.
Fehlende Proben bleiben offen. Technische Tests oder eine Screenshotfreigabe
werden nicht nachträglich als vollständige reale Lösung ausgegeben.

## 8. Früher P1-Export und bestehende Grundlagen

Der erste Export in RP-3 enthält einen neuen, logisch akzeptierten Kandidaten,
ein geeignetes zugehöriges Abschlussbild und einen technischen Prüfnachweis.
Der vorhandene P1-Definitionsvertrag wird über einen begrenzten Adapter bedient.
Erforderliche additive Registrierung neuer Testinhalte und Pfadvalidierung sind
auf diesen Durchstich begrenzt; keine zweite Spiellogik oder neue öffentliche
Importoberfläche. Der neue Inhalt wird in einer isolierten Produktprobe tatsächlich
geladen, bearbeitet und abgeschlossen. Kein Zugriff auf normale Benutzerspielstände.

Vor Abschluss bleiben Motivname und fertiges Bild verborgen; die Miniatur zeigt
den eigenen Bearbeitungsstand einschließlich Fehlern. Bestehende F-01/F-02-Daten,
Proofs und Bilder werden nicht zur Erleichterung des neuen Nachweises verändert.
F-03 bleibt ein UI-Stressdatensatz ohne Rätselqualitätsabnahme.

RP-3 liefert F-04 als neu aus einer realen eigenen Bilddatei importiertes
20×20-Beispiel mit detaillierterer eigener SVG-Enthüllung. Definition, Hauptszene
und SaveStore registrieren ausschließlich feste Pfade/IDs. Appidentität,
Saveformat 1 und bestehende Slots bleiben erhalten; F-04 ergänzt `f04.json` samt
Backup/Temp. Produktionsbilder und Motivname sind vor Abschluss unzugänglich.
Der technische Durchstich ist keine reale Eigentümer-Lösung oder Pilotfreigabe.

Fachliche Vorarbeiten sind [F-01](../prototypes/p1/F01_PROOF.md),
[F-02](../prototypes/p1/F02_PROOF.md), die begrenzten
[Python-Prüfer](../tools/check_f01.py) und die
[H1-Linienanalyse](../prototypes/p1/model/clue_completion.gd).
Sie liefern Konzepte und Vergleichsfälle, aber keinen allgemeinen Produktionssolver
oder bereits unabhängigen Prüfer beliebiger Zertifikate. P1-spezifische Formatlimits,
Vollaufzählung von Linien und die bisherige H1-Ausgabe werden nicht unverändert zur
allgemeinen Produktionsarchitektur erklärt.

## 9. Pakete und Abhängigkeiten

| Paket | Ergebnis | Voraussetzung |
| --- | --- | --- |
| [RP-1](https://github.com/venomenon328/picross/issues/35) | Allgemeiner monochromer Deduktionskern, unabhängige Nachweisprüfung, Datenvertrag und frühe Großrasterbelege. | Diese Spezifikation; aktuelle Startprüfung. |
| [RP-2](https://github.com/venomenon328/picross/issues/36) | Mehrfarben-Domains, vollständige Farb-Linienlogik und gemeinsame Großrasterprüfung. | RP-1. |
| [RP-3](https://github.com/venomenon328/picross/issues/37) | Dateibasierter Bildimport, reproduzierbare Rastervarianten, einfache Vergleichsansicht und erster echter P1-Export. | RP-2 für den Paketabschluss; monochrome Vorarbeit ab RP-1 möglich. |
| [RP-4](https://github.com/venomenon328/picross/issues/38) | Zwölf Quellen, kontrollierter Direkt-/ChatGPT-Codex-Vergleich, Baseline und Aufwandserhebung. | RP-2 und RP-3; Quellenplanung kann vorher erfolgen. |
| [RP-5](https://github.com/venomenon328/picross/issues/39) | Begrenzte Reparatursuche mit hartem Motivschutz und Vorher-/Nachher-Auswertung. | RP-2, RP-3 und die Baseline aus RP-4. |
| [RP-6](https://github.com/venomenon328/picross/issues/40) | Zusammenhängender Pilot einschließlich Abschlussbildern, realer Spielerprobung und Produktionsentscheidung. | RP-4 und RP-5. |

Ein Paket entspricht standardmäßig einem eigenen Draft-PR. Parallel vorbereitete
Quellen oder Oberflächen umgehen keine fachlichen Abhängigkeiten. Implementierung
beginnt erst mit gesondertem Auftrag; Modellwahl und Ausführungsprüfung erfolgen
dann gemäß der lokalen Workflowfassung. Die Issues sind keine rückwirkende
Freigabe einer bestimmten Sprache, Modellkonfiguration oder fertigen Oberfläche.

## 10. Prüfwege und Abnahme

Alle Implementierungspakete halten aktuelle AGENTS-/Workflow-/Profilquellen ein.
Der verwendete lokale Werkzeug-Stack und erforderliche Abhängigkeiten werden vor
der betroffenen Implementierung konkret begründet; die vorhandenen Python-Werkzeuge
legen keine Produktsprache fest. Das erste Paket bindet ausführbare Testbefehle,
Umgebung, Ressourcenlimits und CI-Ausführung in Anleitung und Projektprofil.
Ohne diesen konkreten Prüfpfad keine Behauptung umsetzungsbereiter Folgepakete.

RP-1/RP-2 binden diesen Pfad im [Projektprofil](PROJECT_PROFILE.md), in der
[Anleitung](../tools/puzzle_production/README.md) und im
[RP-1-Prüfvertrag](RP1_VERIFICATION.md) und in der [RP-2-Prüfzuordnung](RP2_VERIFICATION.md).
Eigener `puzzle-production`-Job auf Ubuntu 24.04
mit Python 3.11+, lesenden Rechten und 15 Minuten führt Fachoracles, Negativtests
und tatsächliche Referenzläufe aus. Je 40×40-/100×100-Fall gelten vorab 120 Sekunden
für Solve/Serialisierung/frische Prüfung und 512 MiB gemessener Linux-Peak-RSS je
Prozess; getrennt davon erzwingt der Benchmark 1024 MiB virtuelles Speicherlimit.
Informationsarme Langlinien und echte Propagation sind eingeschlossen. Der PR
führt aktuelle Messwerte, Commit-/Basis-/CI-Artefaktbindung und offene Abnahme;
RP-1/RP-2 einschließlich des unabhängigen technischen Reviews sind über #42/#43
integriert; historische Nachweise behalten ihren ursprünglichen Commitbezug.
RP-3 ergänzt gezielte Bildtests und den realen Dateiimport/Export im gemeinsamen
Fachjob. `product` ergänzt denselben Import samt Bindungsprüfung sowie reguläre
Lade-/Bearbeitungs-/Abschluss-/Neustartprozesse und native Renderbilder.
RP3-A01 bis A06 und unabhängiges technisches/visuelles Review R2 sind über PR #44
abgeschlossen. RP-4 liefert die [unveränderte Vergleichsbaseline](RP4_VERIFICATION.md)
mit eigener Sichtprüfung und unabhängigem Daten-/Methodik-/Bildreview R1.
R1-N1 ergänzt den exakten Pixel-/Modus-/Dimensionsvergleich neuer Illustrationen,
einen begrenzten Windows-Regressionslauf und die Originalbytes des Produzentencommits.
Gespeicherte Eingänge und Baseline behalten sämtliche Dateihashes. Aktuelle technische
Nachweise und die gezielte unabhängige Nachprüfung von R1/B-01 und A-01 bleiben
Mergegates; ihr commitgebundener Abschluss steht in PR #45. Die reale Eigentümer-
Lösung bleibt ausdrücklich RP-6-Gate.

Für jedes Paket gelten der bestehende Dokumentprüfweg und ein vollständiger
Diffcheck. `docs` muss am aktuellen Head/zugehörigen Test-Merge erfolgreich sein.
Neue ausführbare Werkzeuge brauchen passende positive und negative Funktionstests
in einem dokumentierten automatisierten Prüfweg. Diese Tests und nötige
Dokumentation gehören zum jeweiligen Paket, nicht in eine spätere Restphase.

Bei P1-Export-/Produktänderungen gelten zusätzlich die vollständigen relevanten
P1-Pflichtquellen, isolierte Tests, aktuelle `product`-/`preflight`-Nachweise und
die jeweils benannten Artefakt-/Render-/Spielproben. Unveränderte Workflows werden
nicht deaktiviert. Ihre Ergebnisse sind getrennt von neuen Generatornachweisen
zu berichten. Keine neue Pflicht zu redundanten lokalen Vollprüfungen bei bereits
belastbarer passender CI.

Technischer Review auf konkrete Commits, erforderliche Sichtproben und tatsächliche
Eigentümerabnahmen bleiben getrennt. Die Issues legen die Mergegates je Paket
fest. Für den reinen Spezifikations-PR sind aktuelle Dokumentprüfung und fachlicher
Diffcheck relevant; er liefert keine Generator-, Bild- oder Spielabnahme.

## 11. Bewusst spätere Entscheidungen

Noch zu spezifizieren sind weitergehende linienübergreifende Regelprofile,
belastbar mit Menschen kalibrierte Schwierigkeitsstufen, der Ausbau einer vollständigen
Produktionsoberfläche, höhere Größen-/Palettengrenzen und die endgültige Stückzahl
des Veröffentlichungskatalogs. Der Pilot liefert hierzu Entscheidungsdaten.
Spielerhilfe, öffentlicher Bildimport/Editor, Community-Inhalte, Verbundraster,
Regionenbedingungen, Wertung, Plattformwechsel und Veröffentlichung gehören
nicht in diese Phase.

## 12. Technische Hintergrundquellen

Die folgenden Primärquellen begründen Untersuchungsansätze, ersetzen aber nicht
die oben definierten Produktregeln. Insbesondere bedeutet ein fremder Solverstatus
gelöst oder human-like nicht automatisch die Erfüllung von RP-D05.

- [Batenburg et al.: Constructing Simple Nonograms of Varying Difficulty](https://liacs.leidenuniv.nl/~kosterswa/constru.pdf): Bild-/Rasteranpassung mit wiederholter Linienprüfung; Motivschutz und 100×100-Leistung sind für unser Werkzeug eigenständig nachzuweisen.
- [Batenburg/Kosters: Solving Nonograms by combining relaxations](https://homepages.cwi.nl/~kbatenbu/papers/bako_pr_2009.pdf): vollständige Linieninformation und weitergehende logische Beziehungen; stärkere Versuchssolver des Papers gehören nicht automatisch zu unserem Profil.
- [Gerstner et al.: Pixelated Image Abstraction](https://pixl.cs.princeton.edu/gfx/pubs/Gerstner_2012_PIA/index.php): klassische gemeinsame Abstraktion von Bildmerkmalen und Farbpalette, ohne Nonogramm-Garantie.
- [Wolter: pbnsolve](https://webpbn.com/pbnsolve.html): Unterscheidung von Linien-/Farblogik und nachgelagerter Suche; Referenz, keine beschlossene Abhängigkeit.
