# Kontextzeichnungen

Dokument-ID: `image-background`
Status: `active`
Stand: 17.11.2026 · Kriterien: `Q-HG01`–`Q-HG04`, `H-07`

Normwörter und Geltung: [Bildverträge](README.md). Prüfzeitpunkt, Methode und
Einzelurteile: [Qualität §9.1](../PUZZLE_QUALITY.md#91-isolierte-visuelle-beurteilung).
Kandidaten, Korrekturbudget und Auswahl: [Schritt 4](../authoring/PUZZLE_AUTHORING_STEP_4.md).
Profile und Runtimegeometrie: [Hintergrundtechnik](../PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).

## HG-01 Kontext

- MUSS: das Umfeld des Motivs zeigen.
- DARF NICHT: den konkret zu erratenden Gegenstand, seine Lösungssilhouette, eine Rasterkopie, den Motivnamen oder vom Spielerfortschritt abgeleitete Inhalte zeigen.
- DARF: indirekte Kontexthinweise. Universelle Spoilerfreiheit ist keine zugesicherte Eigenschaft.
- DARF NICHT: eingebrannte Buchoberfläche/UI, Schrift oder Wasserzeichen enthalten.

## HG-02 Beiläufige Handskizze

- MUSS: wie eine beiläufig entstandene Bleistiftskizze einer zeichnerisch begabten Person wirken; spontane Kritzelei auf einer Seite, erkennbare Kompetenz, lockere Ausführung.
- MUSS: helles neutralgraues Graphit, sichtbare einzelne Bleistiftstriche, natürlich variierende Strichführung/-stärke und lebendige teilweise offene oder nachgezogene Konturen zeigen. Formen bleiben lesbar, dürfen stellenweise nur angedeutet sein.
- PRIORITÄT: glaubwürdige Handskizze vor Detailperfektion. Komplexität und Ausarbeitungsgrad getrennt beurteilen.
- DARF: einzelne Objekte, Objektgruppen oder komplexe zusammenhängende Szenen. Keine maximale Objektanzahl und keine Pflicht zur Simplizität.
- DARF: kleinere zeichnerische Ungenauigkeiten, Suchlinien, korrigierte/überzeichnete Konturen, leichte Asymmetrien, Radierungen und natürliche Arbeitsspuren.
- DARF NICHT: Fehler, Radierungen oder Suchlinien als Pflichtmerkmal oder wiederkehrendes künstliches Deko-Element einsetzen. Eine saubere Skizze kann den Stil erfüllen.
- DARF NICHT: eine hochprofessionelle fertig ausgerenderte Atelier-/Ausstellungszeichnung liefern; ausgeschlossen sind makellos durchmodellierte Tonwerte, hyperrealistische Oberflächendetails, steril präzise Kanten, homogen perfekte Schattierungen und durchgehend finalisierte Konturen. Ein Graphitfilter auf einer polierten Illustration genügt nicht.
- DARF NICHT: absichtlich chaotische, unlesbare oder karikaturhaft schlechte Zeichnung als Ersatz für Skizzenhaftigkeit verwenden.

## HG-03 Schraffur und Helligkeit

- MUSS: motivgerecht dosierte, sichtbar von Hand geführte Schraffur/Kreuzschraffur verwenden; Richtung und Dichte folgen grob der Form. Unregelmäßigkeiten und lockere Strichenden sind zulässig.
- DARF: gefüllte Objektflächen, auch große oder zusammenhängende Partien, sofern deren Tonwerte sichtbar aus glaubwürdiger Hand-/Kreuzschraffur entstehen. Flächengröße allein ist kein Überarbeitungsgrund.
- DARF NICHT: glatte digitale Deckflächen, gleichmäßige Farbaufträge ohne erkennbare Graphitstriche oder perfekt weichgerenderte Schattierungen verwenden.
- MUSS: gegenüber der älteren Hintergrundserie insgesamt geringfügig heller und zurückhaltender wirken; Raster, Hinweise und UI nicht unnötig überlagern.
- DARF NICHT: so blass, ausgewaschen oder detailarm werden, dass Konturen und feine Striche verschwinden. Kein numerischer Helligkeits-/Alphagrenzwert; die Runtime-Deckkraft wird dadurch nicht verändert.
- MUSS: Luftigkeit durch Gewichtung erzeugen: tragende Hauptformen, zurückgenommene Nebeninformationen und bewusst offene Bereiche. Dichtere schraffierte Objektpartien bleiben erlaubt.

## HG-04 Transparenz

- MUSS: echte PNG-Transparenz in freien Außen-/Zwischenräumen und zwischen offenen Strichen/Schraffuren besitzen; das Spielpapier scheint dort durch. Ein Alphakanal allein genügt nicht.
- DARF: dichte gezeichnete Objektpartien; diese müssen nicht punktweise transparent sein.
- DARF NICHT: störende Säume, verlorene feine Striche, unerwünscht deckende freie Flächen, weiße Bildkästen, gemaltes Schachbrett, Papierimitation oder geometrische Ersatzzeichnung enthalten.

## HG-05 Ganze Leinwand

- MUSS: neue Kandidaten und beauftragte neue Bildrevisionen als vollständige zusammenhängende transparente Einzelbilder exakt 3:1 herstellen; tatsächliche PNG-Breite = 3 × Höhe. Native Maße sind variabel, beispielsweise 2172×724.
- MUSS: die gesamte Leinwand einschließlich bewusstem Freiraum komponieren; geplante seitliche Positionen und sichere Falz-/Randabstände erhalten. Gemeinsamer Fit und Anker folgen dem technischen Profil.
- DARF: rechtsbetonte, offene, durchgehende, U-/Halb-U-Kompositionen, wechselnde seitliche Positionen und unterschiedlich hohe Formen.
- DARF NICHT: Alpha-Bounds-Crop, Nachzentrieren nur des sichtbaren Motivs, Seitenpadding, Zusammensetzen generierter Hälften, Stretch, Beschnitt oder Motivverschiebung zur Formatheilung einsetzen.
- Keine Randpixel-, Prozentbelegungs-, Objektzahl- oder Zwei-Eckenpflicht. Die Beispielbreite ist keine technische Mindestbreite.

## HG-06 Randabschluss

- MUSS: jedes Objekt und jeden zusammenhängenden Szenenteil vollständig innerhalb der Leinwand zeigen oder an jeder erreichten Bildkante zeichnerisch weich in echte Transparenz auslaufen lassen.
- MUSS: an allen vier Rändern Konturen, Schraffur und sichtbare Tonwerte berücksichtigen. Baumkronen, Stämme, Dächer, Gebäude und weiterführende Szenenformen dürfen nicht plötzlich abgeschnitten erscheinen.
- DARF NICHT: harte Schnittlinien, unvermittelt endende Stämme oder scharf abgeschnittene Silhouetten als offenen Bildaufbau zulassen.
- DARF NICHT: Crop, Padding, technische Randkaschierung oder deckende Fade-Balken als Ersatz für eine stimmige Zeichnung verwenden.
- DARF: weich auslaufende Motive bis zum Rand sowie asymmetrische, hohe oder zusammenhängende Kompositionen. Keine Pflicht zu leeren Rändern oder festen Alpha-/Pixelwerten.
- Klassifikation: unabdingbare Voraussetzung H-07; keine redaktionelle Abweichungsannahme für harte Anschnitte.

## HG-07 Höhenverteilung

- EMPFEHLUNG: zusätzliche Höhe als Spielraum behandeln. Besonders die horizontale Bildmitte nicht routinemäßig über die volle Höhe füllen; die Mitte darf niedrig/luftig sein. Auch links/rechts muss die volle Höhe nicht genutzt werden.
- DARF: eine motivgerechte hohe Mitte, volle Seitenhöhe oder andere Verteilung.
- Keine feste Höhenquote, Pflicht zur niedrigen Mitte, hohen Seiten oder U-Form. Höhe allein begründet keine Ablehnung, Überarbeitung oder Ausnahmefreigabe.

## HG-08 Stilbezogene Korrektur

- Bei erkennbar professioneller Ausarbeitung nach HG-02 den Ausarbeitungsgrad, die Konturperfektion und Renderglätte reduzieren; natürliche Handzeichnung bewahren.
- DARF NICHT: zur Stilkorrektur pauschal Objekte entfernen oder künstliche Fehler/Radierstellen ergänzen.
- Diese Beurteilung gehört zu Q-HG02; keine zusätzliche Kriterien-ID, numerische Quote, Pflichtspur oder persönliche Bild-/Buchabnahme.
