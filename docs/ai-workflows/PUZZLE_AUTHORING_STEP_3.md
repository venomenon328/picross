# Schritt 3: Rasterangebote

**Version 0.8.0 · Dokumentrevision 8 · 16.11.2026 · RI-ONE**

Pflicht: vollständiger [Kern](PUZZLE_AUTHORING.md) und [Bildstil](../PUZZLE_IMAGE_STYLE.md).
Zusätzlich: [Qualität](../PUZZLE_QUALITY.md) §§2–4; §5 bei fehlendem qualifiziertem Kandidaten, §6 bei konkreter Ausnahme. Farbe: ausschließlich operative §§8.4–8.5; §§8.1–8.3.1 sind historische Referenz-/Herkunftslektüre nur bei konkreter Frage. Q-R04/Q-H01/Q-H02, Farb-/Ausnahme-/Proofgates und echte Endfreigaben bleiben.

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
[Qualität §§8.4–8.5](../PUZZLE_QUALITY.md#84-verbindliche-berechnung-und-randwerte)
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

Bei Warnung/negativem Sichturteil gilt Qualität §6: ursprüngliches Urteil,
Akteur, UTC, Wortlaut, Begründung und Beleg. Technischer Negativbefund bleibt negativ.
Für die Übernahme außerhalb versiegelter Originale via --palette-exception:
Handoff v5/Rev7 verlangt picross-palette-editorial-exception-v2 mit vollständigem
rulebook-v2 in binding.rulebook; historische Originale ausschließlich v1.
Alle negativen Paare, exakte Werte/IDs, Kandidat/Revision/Istmatrix/Quelle/Regel,
Handoff/Inventar/Paket und echte Endfreigabe binden. Erforderliche manuelle
Autorisierungen bleiben zusätzlich nötig. Die Ausnahme heilt weder Proof noch
Rechte, Freigaben, feste Parameter, Difficulty oder Randregel.

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
Einzelpaketrevision derselben ID nach Kern §6 sichern, mit genau einem handoff.candidate,
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

Historische 0.1/0.2-Schätzungen/Snapshots/Freigaben bleiben gemäß
[Vorgänger §5.1](https://github.com/venomenon328/picross/blob/a4bb4f929f29cd6d6e188500b5a8dbb1dead60fe/docs/ai-workflows/PUZZLE_AUTHORING.md#51-historische-produktionsmethoden-01-und-02),
keine Routinelektüre/Neubewertung. Profilgebrauch beweist keinen Technikbedarf;
stalled/Abbruch ist keine Schwierigkeitsstufe.
