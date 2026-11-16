# Schritt 4: Kontextzeichnungen

**Version 0.8.0 · Dokumentrevision 8 · 16.11.2026 · RI-ONE**

Pflicht: [gemeinsamer Kern](PUZZLE_AUTHORING.md) vollständig und vollständiger
[Bildstil](../PUZZLE_IMAGE_STYLE.md), danach diese Phase. Zusätzlich: [Qualität](../PUZZLE_QUALITY.md) §2/§9.1; [Hintergrund](../PUZZLE_BACKGROUNDS.md) §3 für Manifest/Entscheidung, §4 erst bei tatsächlicher HP-W2-Ableitung/Prüfung.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

### 6.3 Hintergrundarbeit in Schritt 4

Erst nach tatsächlicher Wahl eines qualifizierten Rasters Kontextbriefing und
drei inhaltlich unterschiedliche echte ImageGen-Originale erzeugen. Ihre geprüften,
nötigenfalls nach §6.3.1 formatkorrigierten Kandidatenrevisionen speichern und
isoliert vorlegen. Gemeinsamer [Bildstil](../PUZZLE_IMAGE_STYLE.md) und
[Q-HG-Kriterien](../PUZZLE_QUALITY.md#91-isolierte-visuelle-beurteilung) sind Pflicht:
leichte Graphitsprache einschließlich sichtbar handschraffierter Objektfüllungen,
echte Transparenz in freien Außen-/Zwischenräumen und vollständige 4:1-Komposition
für die 2304×576-Ausgabe. Die Zeichnung nutzt mit ihrem bewusst gestalteten
Freiraum die volle vorgesehene Papierbreite; keine zusätzliche seitliche Leere
durch technisches Padding. Auch kleinere native 4:1-Originale sind zulässig;
gemeinsamer Fit/Anker, kein Alpha-Bounds-Crop oder sichtmotivbezogenes Zentrieren.
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
An der gewählten fertigen 2304×576-Ableitung tatsächliche Maße, erhaltene
Breitenverteilung und Strichqualität nochmals kontrollieren; HP-W2-Erfolg allein
belegt keine passende Komposition. Dafür genügt die isolierte Bildsichtung.
Eine offene Hintergrundwahl darf zusammen mit der tatsächlichen Endabnahme im
passend beauftragten Schlussauftrag erklärt werden; nicht dieselbe unveränderte
Entscheidung ein weiteres Mal verlangen. Die Schlussübersicht nach PW2-B bezeichnet die konkrete unveränderte Kombination.

#### 6.3.1 Formatkorrektur vor der Bildwahl

**HG-KOMPOSITION · 16.11.2026 · [Eigentümerentscheidung #673](https://github.com/venomenon328/picross/issues/673).**
Diese Regel ersetzt die frühere Empfehlung zur transparenten seitlichen
Leinwanderweiterung aus [HG-FORMAT/#663](https://github.com/venomenon328/picross/issues/663).
Die Korrekturbefugnis bleibt erhalten. Authoring bleibt in 0.8.0/Dokumentrevision 8;
aktueller Quellcommit und Dateihashes binden den Normstand, historische Snapshots
und Freigaben behalten ihren damaligen Umfang.

Jeder Bildauftrag fordert eine vollständige transparente **4:1-Komposition**.
2304×576 ist die spätere Ausgabe, keine Mindestauflösung der Generierung.
Eine kleinere echte 4:1-Quelle, etwa 2048×512, ist bei erhaltener Strichqualität
zulässig. 2896 Pixel Breite sind kein Zielgate und aus wiederholten 2172×724-
Resultaten folgt keine belegte KI-Maximalauflösung. Blindes Wiederholen nur zum
Erzwingen dieser Pixelbreite ist nicht erforderlich.

Nach der Generierung und vor jeder regulären Auswahlvorlage die **tatsächlichen
PNG-Maße jedes Kandidaten** lesen und im vorhandenen Bericht nennen:
`Breite == 4 * Höhe` muss gelten. Ein 3:1-Bild darf Rohmaterial sein, ist aber
noch keine formatkonforme Auswahlfassung. Proportionale Verkleinerung allein
ändert sein Seitenverhältnis nicht. Prompt, Vorschau oder späterer HP-W2-Erfolg
ersetzen weder Maßcheck noch Sichturteil.

Zusätzlich die **sichtbare Breitenverteilung der vollständigen Komposition**
prüfen: Die Zeichnung und ihr bewusst geplanter Freiraum müssen die gemeinsame
nutzbare Hintergrundfläche auf dem Buchpapier ausnutzen. Vorhandene Falz-/
Randabstände bleiben; beabsichtigte seitliche Positionen müssen erhalten bleiben.
Eine absichtlich rechte Zeichnung darf rechts stehen, eine luftige Mitte bleibt
zulässig. Keine Pflicht zu Objekten in beiden Ecken oder Tinte an jedem Randpixel.

**Keine Formatkorrektur durch bloßes transparentes Seitenpadding.**
2172×724 → 2896×724 mit je 362 transparenten Pixeln wäre zwar formal 4:1,
ließe die ursprüngliche Bildfläche aber nur 75 % der Breite belegen. In der
2304×576-Ausgabe entspräche dies 1728 Pixeln und je 288 zusätzlichen leeren
Pixeln seitlich. Diese Verengung/Verschiebung zur Mitte ist **Q-HG03 nicht erfüllt**,
kein akzeptabler Ersatz für die beabsichtigte vollständige Komposition.

Format- und dadurch nötige Kompositionskorrekturen innerhalb des laufenden
Hintergrundauftrags **ohne zusätzliche Rückfrage herstellen**, auch vor der
Bildwahl. Eine bereits richtige 4:1-Komposition darf per lokalem Skript/Pillow
proportional in der Auflösung angepasst werden, sofern feine Striche und Alpha
erhalten bleiben. Ist ein 3:1-Rohbild so nicht geeignet, innerhalb der bestehenden
Bildkorrekturbudgets gezielt zeichnerisch auf die volle Breite erweitern oder
eine passende vollständige 4:1-Komposition neu erzeugen. Kontext, geschützte
Merkmale und Stil erhalten. Diese kreative Arbeit zählt zum Korrekturbudget;
rein technische Größenableitung ist kein kreativer Versuch und setzt keine
verbrauchten Budgets zurück. Weder eine vorzeitige Bildwahl noch eine zusätzliche
Ausführungsfreigabe allein wegen des Formatproblems verlangen.

Kein Strecken, Abschneiden gezeichneter oder bewusst leerer Kompositionsbereiche,
Alpha-Bounds-Crop, gesondertes Verschieben sichtbarer Motive im Runtime-Fit oder
geometrisches Ersatzbild. Die korrigierte volle Leinwand erneut nach Q-HG01–Q-HG04
ansehen und ihre Dateimaße prüfen; schraffierte Objektflächen nicht pauschal als
Mangel behandeln. Bei nicht behebbarem Format-/Kompositionsmangel Ursache und
konkreten nächsten Schritt melden, kein bloß maßrichtiges Bild als erfüllt ausgeben.

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
