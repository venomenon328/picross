# Schritt 3: Rasterangebote

**Version 0.8.0 · Dokumentrevision 12 · 23.11.2026 · KORRIDOR-NORM-A**

Pflicht: [Kern und Phasenroute](PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
danach diese Phase und die dort zugeordnete Bildnorm. Zusätzlich:
[Qualität](../PUZZLE_QUALITY.md) §2, §3.3–3.4 und §4; §5 bei diagnostischer
Sichtung, §6 bei konkreter Ausnahme. Farbe: operative §§8.4–8.5;
§§8.1–8.3.1 nur bei einer konkreten historischen Referenzfrage.

Vor dem Rasterangebot je endgültiger Revision Proof, Endmatrix, Difficulty, benutzte Farbpaare, Rand und gegebenenfalls Crop prüfen. Q-R01–04 und Q-H01–03 an den tatsächlichen Ansichten beurteilen. Die Mindestgröße des Revealbilds ergibt sich aus seinen gebundenen Maßen und dem neuen Raster.

## 4. Rasterproduktion und technische Pflichtprüfung

Wenn ChatGPT die gebundenen Motiv- oder Rasterbytes fehlen, öffnet der Akteur sie über den [Remote-Originalabruf](../../tools/PW_REMOTE.md#originale-in-chatgpt-sichten). Die Sichtung des publizierten Rasters und seiner Zell-/Hinweisansicht gehört vor die Angebotsqualifikation.

Rasterprüfung hat einen eigenen Gegenstand. Hintergründe liefern keine Zellwerte
und werden nicht durch Solvererfolg freigegeben. Für 0.8.0 ist vollständig
qualifiziertes raster_ready ohne Hintergrund zulässig; content_ready setzt später
die eigene Hintergrundbereitschaft voraus. Keine vorgezogenen Hintergrundblocker.

### 4.1 Import und Rastervarianten

1. Von der freigegebenen gespeicherten Motivvorlage ausgehen; Ableitung aus genau
   dem freigegebenen Reveal anhand aktueller Bilder und Inhaltsbindungen prüfen.
   Aktuelle Motivbytes, Inhaltsbindung, echte Nutzungsgrundlage und gültige Parameter prüfen.
   Während der Produktion beginnt deterministische Prüfung bei Bildbytes, nicht
   beim Prompt. Nach finaler Integration gilt der Abschluss nach §9.
2. Striktes bestehendes Designformat und aktuelle Format-/Ressourcengrenzen der
   aktuellen Bildhelfers nach PW-B verwenden. Redaktionelle Angaben stehen im aktuellen Record.
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
   Maße/Werte/Palette, feste Wünsche, offensichtliche Formmängel und exakten
   Vergleich von Maßen, Palette und Zellwerten. Parametergebundene Kandidatenhashes
   sind kein reiner Matrixvergleich. Bei einem sonst brauchbaren Kandidaten
   einen negativen Randbefund oder einen motivtreuen leeren Außenbeschnitt unter
   den ungefähren Korridor für die Sichtung nach §4.5 festhalten. Die
   Vorprüfung ersetzt keine vollständige Qualifikation. Nur aktuelle Angebote,
   Sichtungsentwürfe, Prüfergebnisse und offene Defizite erhalten.
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
  zählen. Mono hat genau eine, Color zwei bis acht. Der explizite Modus,
  die endgültige Palette und der freigegebene Korridor müssen dazu passen.
  Ungenutzte Paletteinträge zählen nicht. Widersprüche offen melden und vor
  erneuter Produktion klären.
- Hinweise deterministisch aus exakt dieser Matrix. Gleichfarbige Folgeblöcke
  haben mindestens eine Leerzelle Abstand; verschiedenfarbige dürfen sich berühren.
- Vollständige deduktive Lösung vom unbekannten Start, ohne vorgefüllte Zellen,
  notwendiges Raten, Suchannahmen oder Motivwissen; vollständiger Proof unter
  benanntem Profil, frischer unabhängiger Prüferprozess und exakter Endmatrixvergleich.
- Aktuelle Motiv-/Revealbindung, Parameter, Motivtreue und Nutzungsgrundlage
  dateibasiert prüfen. Matrix und Hinweise müssen zusammenpassen. Kein
  Normalisierungs-/Import-/Reparaturreplay oder Herstellungsarchiv als Zulassung.
  Rechte und echte Freigaben sind keine Solverergebnisse.
- Randregel: mindestens eine gefüllte Zelle an linker ODER rechter Außenkante
  UND mindestens eine an oberer ODER unterer Außenkante. Jede Vordergrundfarbe
  zählt, nicht alle vier Kanten sind nötig; gilt auch für Breite/Höhe 1.
  Ein vollständig leeres Raster scheitert. Keine motivfremden Randpixel/Rahmen
  allein zum Bestehen der Regel hinzufügen.

Einen negativen Randbefund am tatsächlichen Raster als H-01-Befund mit den
betroffenen Kanten sichtbar machen. Nur die ausdrücklich erteilte technische
`frame`-Ausnahme für genau diesen Kandidaten und seine aktuelle Endrevision
kann die Randverletzung decken. Akteur, Erklärung und aktuellen Beleg nach
[PW-B](../../tools/PW_B_CONTRACT.md#pw-find--freigegebene-erweiterung-der-entscheidungsdaten)
und [RI-ONE](../ZA1_ADAPTER.md) binden. Negativer Befund und Ausnahmebeleg bleiben
getrennt sichtbar. Alle übrigen Gates bleiben hart.

Vollständige gültige Deduktion belegt Eindeutigkeit. stalled beweist weder
Mehrdeutigkeit noch Unlösbarkeit; aborted ist Abbruch. Exitcode 0, Importbündel,
generiertes Zahlenbild und KI-Erfolgsaussage sind keine Zertifizierung.
Die separate Eindeutigkeitsdiagnose sucht und liefert eigene Lösungszeugen;
unique ersetzt keinen Deduktionsproof, unknown nach einer Lösung keine
Eindeutigkeit. check-diagnosis prüft Bindungen/Zeugen, nicht die vollständige Suche.
Keine neue Schwierigkeit oder Freigabe aus einem Suchurteil ableiten.

Die aktuelle Datei-, Parameter-, Matrix-/Hinweis- und Proofprüfung zusätzlich
zur Sichtung benutzen; kein Wiederabspielen des Imports. Nur verfügbare Befehle/API
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
3. Profil und zulässige Budgets vor dem konkreten Lauf festlegen. Der aktuelle
   Bild-/Rasterhelfer verwendet --profile line|paired und erhält ausschließlich
   aktuelle Definition, Proof, Schwierigkeit und Vorschau. Keine Importpaketkette.
4. Bei Paarbedarf die unveränderte Logik mit Linienbaseline und Paarprofil frisch
   unabhängig prüfen. Baseline und Assessment dürfen für diese konkrete Analyse
   temporär vorliegen; dauerhaft bleiben aktueller Paarproof und passende geprüfte
   Bewertung. Endmatrix- und Datei-/Motivprüfung bleiben erforderlich.
5. Nur verifizierte stalled-Baseline plus vollständiger verifizierter Paarproof
   belegen notwendigen R4. Aborted, unvollständiger Paarproof oder unique genügen
   nicht. Bei Nichtabschluss aktuelle Lücke und Endgrund nennen.
6. Aktuellen Proof und Bewertung im einzigen aktuellen Record referenzieren.
   Kein zusätzliches candidate.certification/Handoff oder historischer Replay
   als Zulassung. Motivschutz, echte Bildwahl und Endabnahme bleiben Pflicht.

Die separate Eindeutigkeitsdiagnose ist nur bei konkreter offener Frage sinnvoll,
keine Voraussetzung der bereits zugelassenen Paarprofilwahl. Kein neuer CI-Fall
oder Bestandsreplay entsteht aus einer konkreten Produktion.

### 4.3 Redaktionelle Kriterien

[Qualität §3.3–3.4 und §4](../PUZZLE_QUALITY.md) bindet die Einzelurteile,
Sichtmethoden und harten Voraussetzungen. Die gestalterischen Anforderungen
stehen ausschließlich in [RASTER](../images/RASTER.md). Tatsächliche
Raster-/Zell-/Hinweisansichten prüfen; technische Messwerte ersetzen diese
Sichtungen nicht.

Die eingeführte und für 0.8.0 fortgeltende Regel picross-palette-separation-1 aus
[Qualität §§8.4–8.5](../PUZZLE_QUALITY.md#84-verbindliche-berechnung-und-randwerte)
trennt Oklab-Ausschluss, Warnzone und Sichturteil. RP-3 prüft die Ist-Matrix vor
Solver, RP-5 jede Bewertung, feste Wege die rekonstruierte Matrix vor Endproof.
Negative Entwürfe bleiben sichtbar. check-palette ist nur zusätzliche Diagnose.
Nach Änderungen Matrix, IDs/RGB/Nutzung und Regelbindung frisch rekonstruieren;
Palettenentwürfe ohne tatsächliche Verwendung sind vorläufig.

Vor einem qualifizierten Angebot den aktuellen Record und seine Nutzdateien
frisch mit dem aktuellen Reader prüfen. raster_ready enthält alle Rastergarantien;
content_ready zusätzlich die Hintergrundbereitschaft. Fällige Sichturteile
Q-R04/Q-H01/Q-H02 und tatsächliche Ausnahmen stehen kompakt am gebundenen
aktuellen Raster nach [PW-B](../../tools/PW_B_CONTRACT.md). Ein negatives
Paar bleibt negativ; konkrete frame-/palette-Ausnahmen und echte Erklärungen
werden zusätzlich durch RI-ONE geprüft. Kein ZIP-/Handoff-/Inventar- oder
Regelbuchbinding. Fehlende oder ungeprüfte Sichtung bleibt ein Blocker.

Historische F05-Referenzannahmen sind keine Ausnahme oder Freigabe eines neuen
realen Kandidaten. Diagnostische Entwürfe mit echten Bildern, Defiziten und
Korrekturmöglichkeiten nach §4.5 vorlegen.

### 4.4 Reparaturen und Änderungen

Im Remoteweg den Kandidaten am aktuellen Arbeitsref über `diagnosis`,
`profile_check`, `fixed` oder `repair` adressieren. Für die erklärte
Wahl nach der Sichtung `select` mit den konkreten Befundentscheidungen
verwenden. Felder und Zählwirkung stehen im [Workervertrag](../../tools/PW_REMOTE.md#schritt-3-am-veröffentlichten-kandidaten).

Konkrete kleine Kontur-/Flächenmängel und störende leere Außenlinien innerhalb
des freigegebenen Korridors vor Rückgabe bearbeiten, auch bei solved. Gute
Kandidaten nicht unnötig ändern. Reguläre feste Korrektur folgt
[FIXED_RASTER](../FIXED_RASTER.md): vorab festgelegte erlaubte Änderungen am
aktuellen Raster, keine Suche/nachträglich erweiterte
Editliste, Schutzmaske und frische Endnachweise einschließlich aktiver 0.4-Analyse.
Offene/ungefähre Endmaße bleiben trotz konkretem Importstart offen/ungefähr.
Materielle Änderungen entscheiden lassen; eine Zelle ist nicht automatisch
harmlos. Runden/Kandidaten/Änderungen zählen kumulativ unter allen Namen/Ordnern.
Erst frisch geprüfter aktueller Record erlaubt raster_ready, ohne damit
Rasterwahl, Hintergrund oder Endfreigabe zu erklären.

Ergibt ausschließlich Beschnitt an erlaubten Außenseiten ein motivtreues Raster,
dessen ungefähre Achse unter die genehmigte Untergrenze fällt, den tatsächlichen
Zuschnitt nach §4.5 vorlegen. Nur ursprünglich leere, ungeschützte Außenlinien
kommen dafür infrage. Die Maßabweichung bleibt bis zur ausdrücklichen Freigabe
eines aktualisierten Korridors ein hartes Hindernis. Vor einer gültigen festen
Ableitung sind neue Parameter- und Motivfreigabebindung herzustellen. Nach
Zell- oder Maßänderung gelten die Neuprüfungen unten. Bei exakter Breite 20
verbietet der Korridor links und rechts jeden Beschnitt und eine Endbreite 17
bleibt unzulässig.

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

Laufende Suche hält nur die für die konkrete Operation erforderlichen Masken,
Parameter und Zähler temporär. Nach Vorliegen des aktuellen Ergebnisses keine
Rundenprotokolle, erfolglosen Raster/Proofs oder historischen Reparaturpläne
aufbewahren. Aktuelles Ergebnis motivisch und mathematisch prüfen; Nichtfund
bleibt Nichtfund. Grenzen setzen keine rückwirkende Dokumentationspflicht.

| Änderung | Erforderliche Wiederholung |
| --- | --- |
| Zellwert oder Rastermaß, auch eine Zelle oder nur leerer Außenbeschnitt | Neue Revision, Hinweise, vollständiger Logiknachweis, unabhängige Prüfung und Rasterbewertung. |
| Quelle, Crop, Palette oder Importparameter | Neuer gebundener Import und vollständige Prüfung. |
| Materielle Motivänderung | Zusätzlich erneute ausdrückliche Motivfreigabe. |
| Abschlussbild | Neue Bildrevision und menschliche Bildfreigabe; Ableitung, Motiv-/Rasterkonsistenz und Endabnahme erneut prüfen. Materielle Änderungen invalidieren abhängige Motivfreigaben. Kein neuer Logiklauf allein bei nachweislich identischem Raster/Logikeingang. |
| Hintergrundillustration, Komposition oder Transparenz | Neue Bildrevision/Wahl und abhängige Ableitung; Aktuellen Mangel benennen und ersetzte Datei nach Ende ihrer Nutzung entfernen; kein automatisches none. Unveränderte Raster-/Proof-/Schwierigkeitsbindungen erhalten. |
| Nur Schwierigkeit/Kategorie/Metadaten | Keine neue Bild-/Rasterproduktion oder Freigabe allein deswegen; aktuelle Daten/Bindungen korrigieren und nur tatsächlich abhängige Endentscheidungen erneuern. |
| Erstmals Paarprofil bei gleicher Matrix | Aktueller Paarproof und passende unabhängig geprüfte Bewertung; Baseline/Assessment nur für den laufenden Vorgang. Keine umetikettierten Altproofs, keine dauerhafte Handoff-/Inventarkette. |

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
Erzeugung weiterer Varianten allein für eine Angebotszahl. Jedes qualifizierte
Angebot erfüllt Korridor und §§4–5 vollständig. Es benötigt eigene technische
Prüfung, visuelle Bewertung, Bildkonsistenz und gebundene Schwierigkeit.
Zulässige Ausnahmen und redaktionelle Abweichungen folgen Qualität §6.
Gleiche Matrizen unter anderer ID oder anderem Solverprofil sind keine
zusätzlichen Angebote. Empfehlung ist keine Wahl.

Nach [Qualität §5](../PUZZLE_QUALITY.md#5-diagnostische-sichtung) sonst überzeugende
Kandidaten mit offenem Rand- oder ungefährem Maßproblem auch neben einem
qualifizierten Angebot zeigen. Das qualifizierte Raster bleibt unabhängig
wählbar. Bei null qualifizierten Kandidaten zwei bis drei möglichst
unterschiedliche beste brauchbare bereits vorliegende Entwürfe zeigen, sofern
vorhanden. Bei nur einem diesen zeigen. Ohne brauchbaren Entwurf den Nichtfund
und den konkreten nächsten Korrekturschritt nennen. Sichtung setzt weder eine
neue Erzeugungsquote noch höhere Budgets voraus.

Jeder `Sichtungsentwurf – nicht integrationsbereit` nennt stabile ID und Revision,
verlinkt tatsächliches Raster und Reveal und zeigt Prüfergebnisse, Lücken und
Handlungsoptionen. Bei einem Randbefund die verletzte Randbedingung samt
betroffenen Kanten und den zulässigen Korrektur- oder `frame`-Ausnahmeweg zeigen.
Bei einer Maßabweichung zusätzlich tatsächliche Ansichten und Maße vor und nach
dem Beschnitt, entfernte Außenseiten, verletzte Grenze und den konkreten Vorschlag
zur Parameteränderung zeigen. Beispiel für die Breite: Ziel ungefähr 20,
freigegebenes Minimum 18, Startbreite 20, Endbreite 17 nach drei erlaubten leeren
Außenspalten links. Minimum 17 bei unverändertem Ziel und unveränderter
Obergrenze ausdrücklich zur Entscheidung stellen. Folgeprüfungen nach §4.4
benennen.

Der Entwurf bleibt unqualifiziert und dient der Sichtung oder Korrektur.
Ohne qualifiziertes Angebot `raster_review` beziehungsweise `blocked` mit
Grund führen. Fehlender oder negativer Deduktionsproof und ungeklärte Rechte
bleiben Blocker. Wenn der aktuelle technische Weg einen Befund oder die
Maßabweichung nicht gültig in der Werkstatt abbildet, die tatsächlichen Ansichten
und den Befund im bestehenden Sichtungsbericht vorlegen und die technische
Grenze benennen. Keine unqualifizierte Auswahl im Record publizieren.

Jedes Angebot erhält stabile Kennung, Unterschiede, Maße/Modus/Istfarbzahl,
Schwierigkeit und echte Rasteransicht. Ein gemeinsamer aktueller Record bindet
alle tatsächlich angebotenen Raster samt aktuellen Definitionen, Proofs,
Bewertungen und Sichturteilen. Kein Einzelpaket/ZIP pro Angebot. Auswahl bindet
die konkreten Inhaltsbytes nach [PW-B](../../tools/PW_B_CONTRACT.md).
Für monochrome Angebote im aktuellen PW-B-Record ein Label mit Maßen, dem
Modus „Monochrom“ und sichtbaren Motivmerkmalen formulieren, beispielsweise
„19 × 13 · Monochrom · Aussparung und drei Bögen“. Konkrete Rasterfarbnamen und
RGB-Angaben bleiben aus dem Label. Die Vorschau nach [PW-B](../../tools/PW_B_CONTRACT.md#rastervorschau-und-bindung)
zeigt belegte Zellen schwarz und Leerzellen transparent. Ein gebundenes älteres
Label bei beauftragter Korrektur redaktionell im aktuellen Record fortschreiben.
Schritt 4 beginnt erst mit der tatsächlichen qualifizierten Rasterwahl.
Ungewählte Angebote danach entfernen, sobald sie keine aktuelle Nutzung mehr
haben. Keine automatische Auswahl nach Reihenfolge oder Dateinamen.

### 4.6 PW-FIND · Annahme und Rasterwahl

Für aktuelle Befundentscheidungen gilt der Weg nach
[Kern §6.3](PUZZLE_AUTHORING.md#63-pw-find--phasenübergreifende-befundentscheidungen):
Ein Raster wird anhand seiner eigenen aktuellen Befunde, zulässigen Annahmen
und Nachweise auswählbar. Offene Vergleichskandidaten sperren diese Wahl nicht.
Annahme und Behandlung, qualifizierte Wahl des vorhandenen Rasters und
Fortsetzung zu Schritt 4 dürfen in derselben tatsächlichen Erklärung erfolgen.
Eine zusätzliche menschliche Runde allein zur Änderung des globalen Status
entfällt. Vollständiger Logiknachweis, Schwierigkeit und übrige harte Bedingungen
bleiben fällig; Befundannahme ersetzt ihre Prüfung nicht.

Bei einer Randverletzung gilt ausschließlich die aktuelle `frame`-Ausnahme
nach §4.2. Bei einer Korridorunterschreitung ist eine ausdrückliche
Parameterentscheidung nötig. Eine redaktionelle Checkbox deckt keine
Maßabweichung. Der Eigentümer kann den neuen Korridor und die beabsichtigte
Kandidatenwahl für den nächsten Schritt in einem Auftrag erklären. Der Akteur
bindet zuerst die neue Freigabe, prüft den konkreten Endstand frisch und
vollzieht die Rasterwahl und Schritt 4 erst bei vollständig erfüllten
Voraussetzungen und gültiger Wahlbindung. Die gemeinsame Erklärung spart eine
zusätzliche Annahmerunde und gilt für den konkret bezeichneten Kandidaten,
dessen Revision und die ausdrücklich freigegebenen Parameter.

Ein blockierter Sichtungsentwurf bleibt als Korrekturgrundlage adressierbar.
Ein angenommener Befund oder alter globaler Blockertext verlangt keine weitere
Rasterproduktion. Materielle Änderungen erfordern die betroffenen neuen Prüfungen;
Korrektur- und Suchbudgets bleiben unverändert.

## 5. Schwierigkeit L1–L5

Logische Schwierigkeit, Rastergröße, Bearbeitungsumfang und Lösungszeit trennen;
Sterne-/Fehlerwertung im Spiel bleibt unabhängig. Hintergrundstatus/-wahl fließen
nicht ein. Bei reiner Bildrevision passende unveränderte Analyse-/Proofbindungen
erhalten; tatsächliche Logikänderungen verlangen neue Nachweise nach §4.

### 5.2 Aktueller zusätzlicher Integrationsstandard SD

Für neue Produktion gilt die aktive 0.4-Analyse-/Bewertungsbindung aus
[SD2](../../difficulty/PUZZLE_DIFFICULTY_V2.md) und [SD2-Integration](../../difficulty/SD2_INTEGRATION.md).
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
erzwingen keinen neuen Analyselauf. Tatsächliche Entscheidungen erhalten; ausschließlich die aktuelle Bewertung
an die aktuelle Definition binden.
Probespielen bleibt optional; technische Referenzen sind keine empirische
menschliche Kalibrierung. Ungemessene Lösungszeiten nicht behaupten.

Historische 0.1/0.2-Schätzungen/Snapshots/Freigaben bleiben gemäß
[Vorgänger §5.1](https://github.com/venomenon328/picross/blob/a4bb4f929f29cd6d6e188500b5a8dbb1dead60fe/docs/ai-workflows/PUZZLE_AUTHORING.md#51-historische-produktionsmethoden-01-und-02),
keine Routinelektüre/Neubewertung. Profilgebrauch beweist keinen Technikbedarf;
stalled/Abbruch ist keine Schwierigkeitsstufe.
