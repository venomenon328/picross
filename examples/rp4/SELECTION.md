# RP-4: festgelegter Korpus vor der Auswertung

Am 05.10.2026 aus `main@aa9cc23244c60d647d8468a8d76a819f977e85a6`
festgelegt. [plan.json](plan.json) bindet zwölf tatsächlich vorhandene Originale,
ihre SHA-256, Motive, Klassen, Größen, Farben, Ausschnitte und Budgets.
Dieser Stand wird vor dem ersten Solverlauf committet. Keine Quelle wurde nach
Kenntnis eines logischen Ergebnisses gewählt oder ersetzt.

- Drei eigene klare geometrische Illustrationen: Kanne mit Henkelinnenraum,
  zweifarbiges Segelboot mit Wellen und Tulpe. Die PNGs entstehen unmittelbar
  auf 800×800 beziehungsweise 900×600 aus den dokumentierten Zeichenoperationen
  in `create_illustrations.py`, nicht aus einem kleinen Lösungsraster.
- Drei echte KI-Vorlagen: Eule, Dampflok, Pagode; je ein nativer Imagegen-Aufruf
  innerhalb ChatGPT/Codex. Originalausgaben und genaue Briefings bleiben erhalten.
- Drei Fotos mit abgrenzbarem Hauptmotiv: Fotograf, Tasse und zugeschnittene Rakete.
  Klar abgrenzbar bedeutet hier nicht textur- oder störungsfrei.
- Drei schwierige Fotos: unscharfe Uhr mit schwachen Innenstrukturen, Astronautin
  mit überlagertem Helm und Katzenporträt mit Fellzeichnung. Die Uhr ist bewusst
  ein Informationsverlustfall: Stilisierung darf keine konkrete Uhrzeit erfinden.

Das kleine gezielt ausgewählte Korpus untersucht konkrete Arbeitsweisen, keine
repräsentative Erfolgsquote für beliebige Bilder. Eigene einfache Illustrationen
sind ein günstiger Vergleichsfall. Alle sechs Fotos kommen aus demselben
Testbildbestand; das begrenzt die Übertragbarkeit.

## Herkunft und Nutzungsgrundlage

Alle Fotografien wurden als unveränderte Originalbytes aus dem gepinnten
[scikit-image-Stand e8a42ba](https://github.com/scikit-image/scikit-image/tree/e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae/skimage/data)
geladen. Die dortige
[Quelldokumentation](https://github.com/scikit-image/scikit-image/blob/e8a42ba85aaf5fd9322ef9ca51bc21063b22fcae/skimage/data/_fetchers.py)
wurde tatsächlich gelesen; die [offizielle API-Dokumentation](https://scikit-image.org/docs/0.25.x/api/skimage.data.html)
bestätigt die Zuordnungen. Es wird keine scikit-image-Laufzeitabhängigkeit eingeführt.

| Datei | Herkunft / dokumentierte Freigabe |
| --- | --- |
| `camera.png` | Lav Varshney, CC0; aktuelle Ersatzaufnahme ab Version 0.18. |
| `coffee.png` | Rachel Michetti, CC0; Pikolo Espresso Bar. |
| `rocket.jpg` | SpaceX, als Public Domain veröffentlicht. |
| `clock_motion.png` | Stefan van der Walt, Public-Domain-Freigabe. |
| `astronaut.png` | NASA, Eileen Collins, Public Domain; Forschungsvergleich, keine Werbe-/Empfehlungsbehauptung. |
| `chelsea.png` | Stefan van der Walt, CC0. |

Eigene Geometrien wurden im Projektauftrag erstellt. Die drei KI-Vorlagen wurden
ohne externe Bildreferenz erzeugt. Die sechs Stilisierungen verwenden ausschließlich
die oben zugeordneten Fotografien. Eine Exklusivität generierter Bilder wird nicht
behauptet; weder Personen noch Logos werden als Produktwerbung verwendet.

## Vorab festgelegter Vergleich

Je Foto wird der gleiche ausgeschnittene Bildraum einmal direkt und einmal nach
genau einer KI-Stilisierungsrunde verarbeitet. Die Referenz-PNGs sind verlustfrei
aus dem Originalausschnitt abgeleitet; sie sind die tatsächlichen Eingaben der
Bildbearbeitung. Die Stilisierung darf Hintergrund und Textur vereinfachen, muss
aber Motiv, Pose, Proportionen und wesentliche Innenräume erhalten. Keine Masken-
oder Rasterreparatur. Die endgültigen KI-Ausgaben werden vor jedem Solverlauf
ebenfalls mit Hash gebunden. Kein Nachprompt nach Kenntnis eines Solverstatus.

Je Arm zwei Varianten: Mono `area-128` und `area-176`; Farbe `area-128` und
`contour-40`. Gleiche Palette, weißer Leerwert, Alpha-Schwelle 128 und explizites
`contain` innerhalb eines Paars. Bei einem abweichenden Bildseitenverhältnis der
KI-Ausgabe erhält `contain` dieses Verhältnis; Abweichungen werden im Bericht
bewertet, nicht nachträglich durch Strecken verborgen. Rastergrößen im Plan.
Kanne, Eule, Tasse und Katze zusätzlich direkt aus ihren hochauflösenden Quellen
nach 100×100; bei beiden Fotofällen auch der jeweilige KI-Arm mit gleichem Budget.
Damit 24 Imports, 48 Kandidaten und genau neun native KI-Aufrufe.

Je Kandidat maximal 30 s Solver und separat 30 s Prüfer, je 100000 Linien;
keine Änderung der RP-1/RP-2-Referenzbudgets. Reproduktionsprüfung insgesamt auf
600 s begrenzt. Originalresultate und spätere Prüfung werden getrennt gespeichert.
Nicht abgeschlossene Läufe bleiben offen/abgebrochen und zählen nicht als Zertifikat.
Keine Erfolgsquote oder Palette wird nach Kenntnis der Ergebnisse optimiert.

Agentenarbeit ersetzt keine gemessene menschliche Tätigkeit. Menschliche Minuten
bleiben in allen vier Kategorien explizit unbekannt (`null`), sofern nicht tatsächlich
beobachtet. Maschinenzeiten, native KI-Runden, Varianten und Solveraufrufe werden
separat erfasst. Aus unbekanntem menschlichem Aufwand wird keine Produktivitätszahl
berechnet. Schwierigkeit und RP-6-Spielabnahme bleiben separat.
