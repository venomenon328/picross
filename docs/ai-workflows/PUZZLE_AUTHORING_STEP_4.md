# Schritt 4: Kontextzeichnungen

**Version 0.8.0 · Dokumentrevision 9 · 16.11.2026 · RI-ONE**

Pflicht: [gemeinsamer Kern](PUZZLE_AUTHORING.md) vollständig und vollständiger
[Bildstil](../PUZZLE_IMAGE_STYLE.md), danach diese Phase. Zusätzlich: [Qualität](../PUZZLE_QUALITY.md) §2/§9.1; [Hintergrund](../PUZZLE_BACKGROUNDS.md) §3 für Manifest/Entscheidung, §4 erst bei tatsächlicher HP-W2-Ableitung/Prüfung.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

### 6.3 Hintergrundarbeit in Schritt 4

Erst nach tatsächlicher Wahl eines qualifizierten Rasters Kontextbriefing und
drei inhaltlich unterschiedliche echte ImageGen-Originale erzeugen. Ihre geprüften,
nötigenfalls nach §6.3.1 formatkorrigierten Kandidatenrevisionen speichern und
isoliert vorlegen. Gemeinsamer [Bildstil](../PUZZLE_IMAGE_STYLE.md) und
[Q-HG-Kriterien](../PUZZLE_QUALITY.md#91-isolierte-visuelle-beurteilung) sind Pflicht:
leichte Graphitsprache mit insgesamt geringfügig hellerer, zurückhaltender
Bleistiftwirkung einschließlich sichtbar handschraffierter Objektfüllungen,
echte Transparenz in freien Außen-/Zwischenräumen und vollständige 3:1-Einzelkomposition
für die 2304×768-Ausgabe. Die Zeichnung nutzt mit ihrem bewusst gestalteten
Freiraum die volle vorgesehene Papierbreite; keine zusätzliche seitliche Leere
durch technisches Padding. Auch kleinere native 3:1-Originale sind zulässig;
gemeinsamer Fit/Anker, kein Alpha-Bounds-Crop oder sichtmotivbezogenes Zentrieren.
Zusätzliche Höhe als Spielraum behandeln: als unverbindliche Gestaltungsrichtung
besonders die horizontale Bildmitte eher niedrig/luftig lassen; auch die Seiten
müssen die volle Höhe nicht ausnutzen. Motivgerechte höhere Partien bleiben
zulässig. Keine feste Höhenquote, U-Formpflicht oder Ablehnung allein wegen der
Höhenverteilung; maßgeblich ist die gestalterische Einordnung im Bildstil.
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
An der gewählten fertigen 2304×768-Ableitung tatsächliche Maße, erhaltene
Breitenverteilung und Strichqualität nochmals kontrollieren; HP-W2-Erfolg allein
belegt keine passende Komposition. Dafür genügt die isolierte Bildsichtung.
Eine offene Hintergrundwahl darf zusammen mit der tatsächlichen Endabnahme im
passend beauftragten Schlussauftrag erklärt werden; nicht dieselbe unveränderte
Entscheidung ein weiteres Mal verlangen. Die Schlussübersicht nach PW2-B bezeichnet die konkrete unveränderte Kombination.

#### 6.3.1 Formatkorrektur vor der Bildwahl

HG31 / [#675](https://github.com/venomenon328/picross/issues/675#umsetzungsvorbereitung-hg31)
ist mit [PR #676](https://github.com/venomenon328/picross/pull/676) in main integriert
und ersetzt die frühere 4:1-Anforderung für neue Arbeit einschließlich beauftragter
Bestandsrevisionen.
Neue Kandidaten als durchgehendes Einzelbild exakt 3:1 herstellen, etwa
2172×724; vor Vorlage tatsächliche PNG-Maße jedes Bildes lesen und binden:
Breite=3*Höhe. Prompt und Vorschau ersetzen diesen Check nicht.
Keine Mindestbreite aus einer beobachteten Generatorausgabe ableiten;
nicht exponierte Modell-/Seed-/Backendparameter bleiben ausdrücklich unbekannt.
Keine Serienversuche zum Erraten einer Generatorgrenze.

Sichtbare Breitenverteilung und bewusst gestalteten Freiraum der vollständigen
Leinwand prüfen. Geplante seitliche Positionen sowie Falz-/Randabstände bleiben;
rechtsbetonte und offene Kompositionen sind erlaubt. Keine Randpixelquote.
Format-/Kompositionskorrekturen im laufenden Auftrag ohne weitere Rückfrage
innerhalb des bestehenden Bildkorrekturbudgets herstellen. Nötigenfalls eine
passende vollständige 3:1-Komposition neu erzeugen. Kein Padding, Stitching aus
Halbbildern, Strecken, Crop oder individuelles Motivverschieben.

Rohoriginale unverändert sichern, kreative Korrektur als neue Revision mit
Ausgangsdatei, tatsächlichen Maßen und Operation dokumentieren. Geänderte Bytes
zur normalen tatsächlichen Bildwahl vorlegen; keine Übertragung früherer
Freigaben. Nur das gewählte Original mit ausdrücklich gewähltem
`picross-background-png2304x768-v1` nach HP-W2 ableiten und verify ausführen.
Tatsächliche 2304×768-Ausgabe, Breitenverteilung, Striche und Alpha prüfen.
Aktive 4:1-Assets bleiben bis zur tatsächlich gewählten und integrierten Ersetzung
unter ihrem alten Profil bytegleich. Ein ausdrücklicher Auftrag zur Neuproduktion
des Bestands wie [#671](https://github.com/venomenon328/picross/issues/671) schließt
sie ein; historische Originale und Freigaben bleiben unverändert erhalten.
Unveränderte Raster-, Proof- und Schwierigkeitsbindungen bleiben erhalten.

Übergabe: background_review zur Wahl/Korrektur oder ausdrücklichem none.
content_ready erst bei vollständiger Hintergrundbereitschaft; kein Spieleinbau.
