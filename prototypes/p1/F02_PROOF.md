# F-02 / F-03 · Herkunft und Nachweis

Prüferdokument mit Motivspoiler, vor Abschluss nicht in der Spieloberfläche verlinkt.

F-02 Revision 1 ist ein für #9 aus eigenen Rasterkoordinaten entworfenes 40×40-Bild:
Leuchtturm am Meer, Sonne oben links, Turm rechts, Wellen am unteren Rand.
Vier stabile Farben A–D: dunkle Konturen, Ocker, Terrakotta, Blau. Keine fremde Vorlage,
kein importiertes Bild und kein Asset aus einem Mock. Das 600×600-SVG zeichnet dieselben
Farbflächen. Nur F-01 benötigt in diesem Paket eine detailliertere Neuzeichnung.

[Definition](data/f02.json) und [Zertifikat](data/f02-proof.json) sind getrennt.
Schema 2 speichert die unabhängige Abschlussressource mit Versions- und Definitions-ID;
die Ressource wird erst nach tatsächlichem Abschluss angezeigt. Alle Zellen starten unbekannt.

## Endliche farbige Deduktion

[Prüfer](../../tools/check_f02.py) ist ausschließlich auf F-02 Revision 1 begrenzt,
kein Runtime-Solver oder allgemeines Produktionswerkzeug. Die zulässigen Platzierungen
jeder Linie werden aus Länge **und Farbe** der Hinweise gebildet: gleicher Nachbarfarbe
folgt mindestens eine Leerzelle; verschiedene Farben dürfen ohne Abstand folgen oder
auch getrennt sein. Nur der Schnitt aller noch möglichen, mit vorher erzwungenen
Kreuzungszellen verträglichen Platzierungen liefert neue Zellwerte.

80 überprüfbare Schritte bestimmen alle 1600 Zellen. Jeder Schritt enthält Achse,
einsbasierte Linie, Anzahl verbleibender Möglichkeiten und sämtliche neu erzwungenen
Positions-/Wertpaare. Der breite farbige Hintergrund und leere Randlinien machen diesen
UI-Testinhalt bewusst einfach. Eine Lösung wird erst nach Ende der Deduktion verglichen;
keine Rasterannahmen, keine zusätzlichen Startfelder. Vollständige erzwungene Bestimmung
belegt auch Eindeutigkeit. Manipulierte Zertifikate, Lösungen und Revisionen werden abgelehnt.

```sh
python tools/check_f02.py
python -m unittest discover -s tools -p 'test_f02.py' -v
```

F-03 Revision 1 ist ein selbst erzeugtes 100×100-Stressmuster mit leerer erster Zeile,
wechselnden Farben und regelmäßigen Lücken. Sehr lange Hinweise werden vollständig
aus der Matrix abgeleitet. Kein Deduktions-/Motivqualitätsversprechen; sichtbare Kennzeichnung
„UI-Testdatensatz – Rätselqualität nicht abgenommen“, auch nach Solltreffer.
Die technische SVG-Abschlussressource zeigt den Teststand, kein reguläres Sammelmotiv.

F-02-/F-03-Daten und SVGs sind eigene Testinhalte dieses Repositorys ohne Fremdassets.
Zertifikate, Tests und diese Prüferdokumente gehören nicht zum Windows-Spielinhalt.
