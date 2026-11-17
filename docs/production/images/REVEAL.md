# Abschlussbilder

Dokument-ID: `image-reveal`
Status: `active`
Stand: 17.11.2026 · Kriterien: `Q-B01`, `Q-B02`, `Q-B03`

Normwörter und Geltung: [Bildverträge](README.md). Prüfzeitpunkt, Methode und
Einzelurteile: [Qualität §3.1](../PUZZLE_QUALITY.md#31-abschlussbildphase).
Auswahl und Revision: [Schritt 1](../authoring/PUZZLE_AUTHORING_STEP_1.md).

## RV-01 Motividentität

- MUSS: Hauptgegenstand, charakteristische Silhouette, motivgerechte Anatomie, stimmige Perspektive, Proportionen und notwendige Negativräume erhalten.
- MUSS: ausdrückliches Briefing, bindende Referenz und geschützte Merkmale erfüllen. Eine freie Interpretation muss als solche beauftragt sein.
- DARF NICHT: ungewollte anatomische Artefakte oder eine vom freigegebenen Motiv abweichende Ansicht als bloße Verfeinerung ausgeben.

## RV-02 Illustration

- MUSS: warme, klare, handgezeichnete 2D-Illustration mit zusammenhängenden erkennbaren Formen.
- MUSS: auch bei Mono-Rastern farbig und ausgearbeitet; tragende Farbflächen, Binnenformen, charakteristische Oberflächendetails und zurückhaltende Schattierung.
- MUSS: motivbezogene Details statt dekorativem Kleinstflächenrauschen; eine gemeinsame Form-, Kontur- und Flächenbehandlung verbindet die Serie.
- DARF: lebendige leicht sichtbare Kontur, dezente Farblagen wie Filzstift oder farbige Tusche sowie eine zum Motiv passende andere Zeichentechnik. Eine identische Palette oder ein gemeinsamer Effektfilter ist nicht erforderlich.
- DARF: mehr Farben und Details als im Lösungsraster. [Motivvorlage](MOTIF.md) und [Raster](RASTER.md) bleiben eigene Abstraktionen; Pixelmaske und Auflösung müssen nicht identisch sein.
- DARF NICHT: Fotorealismus, 3D-Look, vergrößerte Zellgrafik, bloß kolorierte Silhouette, unkontrolliert ausgefranste Doppelränder, schwache Ton-in-Ton-Trennung, überladener Hintergrund, ungewollte Schrift oder Wasserzeichen.
- DARF NICHT: ein Abschlussbild nachträglich an eine abweichende Motivvorlage oder ein abweichendes Raster anpassen oder zur Rechtfertigung technischer Fehlschläge mechanisch vereinfachen.

## RV-03 Transparenz und Kanten

- MUSS: echte Transparenz außerhalb des Motivs und in wirklichen Aussparungen. Ein Alphakanal bei weiterhin deckender Außenfläche genügt nicht.
- MUSS: weiße und helle Motivteile, Glanzlichter, Farben, feine Details und Konturen erhalten. Helligkeit allein ist kein Freistellkriterium.
- MUSS: saubere Alphakanten in großer und kleiner Darstellung; keine hellen Matten, störenden hellen/dunklen Säume, ausgeschnittenen Motivdetails oder ausgefransten Konturen.
- DARF: teiltransparente Randpixel.
- DARF NICHT: weiß oder cremefarben übermalte Außenflächen als Transparenz ausgeben.

## RV-04 Szenen

- MUSS: notwendige Szenenumgebung, prägende räumliche Beziehungen, Perspektive, Proportionen, Ausschnitt und Komposition erhalten.
- MUSS: eine motivgerechte transparente Außengestaltung oder Vignette konkret ausarbeiten und an der tatsächlichen Bildfassung beurteilen.
- DARF NICHT: Himmel, Meer, Boden oder anderes inhaltlich relevantes Umfeld pauschal entfernen.
- DARF NICHT: einen beliebigen opaken Bildkasten allein mit der Begründung „Szene“ zulassen.
- Weitergehende Motiv-/Kompositionsänderungen vor Bearbeitung entscheiden lassen; die Freigabefolgen regelt [Authoring](../authoring/PUZZLE_AUTHORING.md#gemeinsame-bildkorrektur).

## RV-05 Fertige Auswahlfassung

- MUSS: neue Bilder bereits transparent zur Auswahl vorlegen und in diesem Stand freigeben lassen.
- Nachträgliche Freistellung einer bereits freigegebenen Datei ist eine neue Bildrevision; sie darf nicht stillschweigend die freigegebenen Bytes ersetzen.
- Die technische Alphakette und der Austausch integrierter Dateien folgen [Revealtechnik](../REVEAL_TRANSPARENCY.md); diese Bildnorm definiert keine zusätzlichen Importformate oder Runtimeoperationen.
