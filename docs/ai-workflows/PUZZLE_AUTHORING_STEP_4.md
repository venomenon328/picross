# Schritt 4: Kontextzeichnungen

**Version 0.8.0 · Dokumentrevision 7 · 15.11.2026 · PW-PERF-D**

Pflicht: [gemeinsamer Kern](PUZZLE_AUTHORING.md) vollständig und vollständiger
[Bildstil](../PUZZLE_IMAGE_STYLE.md), danach diese Phase. Zusätzlich: [Qualität](../PUZZLE_QUALITY.md) §2/§9.1; [Hintergrund](../PUZZLE_BACKGROUNDS.md) §3 für Manifest/Entscheidung, §4 erst bei tatsächlicher HP-W2-Ableitung/Prüfung.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

### 6.3 Hintergrundarbeit in Schritt 4

Erst nach tatsächlicher Wahl eines qualifizierten Rasters Kontextbriefing und
drei inhaltlich unterschiedliche echte ImageGen-Originale erzeugen. Ihre geprüften,
nötigenfalls nach §6.3.1 formatkorrigierten Kandidatenrevisionen speichern und
isoliert vorlegen. Gemeinsamer [Bildstil](../PUZZLE_IMAGE_STYLE.md) und
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

#### 6.3.1 Formatkorrektur vor der Bildwahl

**HG-FORMAT · 15.11.2026 · [Eigentümerentscheidung #663](https://github.com/venomenon328/picross/issues/663).**
Die folgende Präzisierung bleibt in Authoring 0.8.0/Dokumentrevision 7; aktueller
Quellcommit und Dateihashes binden ihren Stand, historische Snapshots bleiben erhalten.

Jeder Bildauftrag fordert die vollständige transparente 4:1-Leinwand, vorzugsweise
2304×576. Nach der Generierung und vor jeder regulären Auswahlvorlage die
**tatsächlichen PNG-Maße jedes Kandidaten** lesen und im vorhandenen Bericht nennen:
`Breite == 4 * Höhe` muss gelten. Andere native Auflösung bedeutet kein anderes
Seitenverhältnis. Prompt, Vorschau oder späterer HP-W2-Erfolg ersetzen den Maßcheck
nicht. Ein 3:1-Rohbild ist noch kein formatkonformes Hintergrundangebot.

Ein solches Formatproblem innerhalb des laufenden Hintergrundauftrags
**ohne zusätzliche Rückfrage korrigieren**, auch wenn noch kein Kandidat gewählt
ist. Das umfasst ausdrücklich lokale Skripte/Pillow für reine Leinwand- und
proportionale Größenkorrekturen. Weder eine vorzeitige Bildwahl noch eine separate
Erlaubnis zur Skriptnutzung verlangen. Keine weitere ImageGen-Runde allein für
einen bereits rein technisch behebbaren Formatfehler erzwingen.

Bevorzugt die vollständige ursprüngliche Leinwand pixelgleich und unten mittig
auf eine größere transparente 4:1-Leinwand setzen. Beispiel: 2172×724 wird
2896×724 mit je 362 transparenten Pixeln links/rechts, ohne Resampling.
Falls eine Größenanpassung nötig ist, ausschließlich proportional, mit erhaltener
feiner Zeichnung/Alpha und transparentem Freiraum. Bei dieser mechanischen
Korrektur kein Strecken, Beschnitt gezeichneter oder bewusst leerer Bereiche,
Alpha-Bounds-Crop, gesondertes
Verschieben sichtbarer Motive, Umzeichnen oder geometrisches Ersatzbild.

Die korrigierte vollständige Leinwand erneut nach Q-HG01–Q-HG04 ansehen und
ihre Dateimaße prüfen. Padding allein belegt weder passende Bildgewichtung noch
echte Transparenz. Erfüllt die mechanische Korrektur das Briefing nicht, innerhalb
des bestehenden Auftrags und seiner Bildkorrekturbudgets gezielt korrigieren.
Die technische Leinwandkorrektur ist kein weiterer kreativer ImageGen-Versuch
und setzt verbrauchte Budgets nicht zurück. Bei nicht behebbarem Mangel Ursache
und konkreten nächsten Schritt melden; kein formatwidriges Bild als erfüllt ausgeben.

Rohoriginal unverändert sichern; korrigierte Kandidatenbytes unter neuer Revision
führen. Ausgangsdatei/Revision, tatsächliche Maße, Operation und neue Datei im
vorhandenen Bericht binden. Die geltende Produktionsablage und ihr Abschluss
bleiben maßgeblich; kein zusätzliches Dauerarchiv. Anschließend die korrigierten
Kandidaten zur **normalen tatsächlichen Bildwahl** vorlegen. Diese Arbeitsbefugnis
erteilt keine Auswahl, Endabnahme oder Übertragung alter Freigaben auf neue Bytes.
Ein ausdrücklich bytegleicher Übernahmeauftrag wird dadurch nicht umgedeutet.

Diese Kandidatenkorrektur ist Authoring-Bildarbeit vor der Wahl, keine vorgezogene
HP-W2-Ableitung. HP-W2 weiterhin nur für das tatsächlich gewählte Original
ausführen; keine vorläufigen oder erfundenen Auswahlentscheidungen erzeugen.
Unveränderte Raster-, Proof- und Schwierigkeitsbindungen bleiben erhalten.

Übergabe: background_review zur Wahl/Korrektur oder ausdrücklichem none.
content_ready erst bei vollständiger Hintergrundbereitschaft; kein Spieleinbau.
