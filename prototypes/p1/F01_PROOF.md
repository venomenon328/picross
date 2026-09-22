# F-01: Herkunft und Deduktionsnachweis

**Prüferdokument mit Motivspoiler.** In der Spieloberfläche vor Abschluss nicht verlinkt.

F-01, Revision 1, ist ein eigens für #8 am 22.09.2026 aus Rasterkoordinaten
entworfenes Segelboot. Keine Bildvorlage, kein fremdes Pixelbild, keine externen
Schrift-/Bildassets und keine Übernahme aus den Gestaltungsmocks. Das Motiv ist
ein Testinhalt, keine Entscheidung zwischen Sammelalbum und Reisealbum.
Godots eingebaute Standardschrift wird für die Oberfläche verwendet.

Der Mast, zwei Segelflächen und der breite Rumpf bilden die Silhouette. Die
Abschlussrepräsentation koloriert exakt dieselben gefüllten Rasterzellen in
Ocker, Salbeigrün und Terrakotta; der Mast bleibt braun. Sie verschiebt weder
Bildaufbau noch Proportionen und fügt kein unabhängiges Belohnungsbild hinzu.
Der Validator prüft diese identische Silhouette in beiden Richtungen.

## Daten

[data/f01.json](data/f01.json) enthält Schema 1, stabile ID/Revision, Dimensionen,
Palette (stabile Farb-ID 1), Lösung, sämtliche Hinweise und die gated Motivdaten.
In der Lösung bedeutet 0 Hintergrund; positive IDs bezeichnen Farben. Der
Spielerzustand ist separat: −1 unbekannt, 0 leer, positive ID gefüllt. Der Zustand
startet vollständig unbekannt. Die Palette ist unabhängig vom Zustandswert.

## Endliche Begründung ohne Raten

[data/f01-proof.json](data/f01-proof.json) dokumentiert 48 aufeinanderfolgende
Linienschlüsse. Zeilen/Spalten und Zellpositionen im Zertifikat sind einsbasiert.
Jeder Schritt nennt Linie, Zahl der verbleibenden Platzierungen und alle neu
erzwungenen Paare `[Position, Wert]` (0 leer, 1 gefüllt).

Einzige Schlussregel: Alle zulässigen Anordnungen der vollständigen Hinweise
einer Linie werden mit den bereits sicher bekannten Kreuzungszellen abgeglichen.
Eine bisher unbekannte Zelle wird nur gesetzt, wenn **jede** verbleibende
Anordnung dort denselben Wert hat. Gleiche Blöcke haben mindestens eine Leerzelle
Abstand. Leere Hinweise erzwingen eine leere Linie. Es wird nie eine
Rasterannahme ausprobiert, zurückgenommen oder aus der Lösung vorgelesen.

Der Beginn folgt direkt aus den Hinweisen: leere Randlinien werden geleert;
die langen Segel-/Rumpfblöcke besitzen unvermeidliche Überlappungen. Diese sicheren
Felder reduzieren danach die möglichen Spaltenanordnungen, deren Schnitt wiederum
Zeilen erzwingt. Das Zertifikat führt diesen Vorgang bis zu allen 400 Zellen aus.
Da jeder eingetragene Wert erzwungen ist und das Raster vollständig bestimmt wird,
ist zugleich die Eindeutigkeit dieses Testfalls nachgewiesen.

Reproduktion im Repository-Root:

```sh
python tools/check_f01.py
python -m unittest discover -s tools -p 'test_f01.py' -v
```

Der Prüfer berechnet die Folge allein aus den Hinweisen und vergleicht erst am Ende
mit der hinterlegten Lösung. Er verlangt außerdem die exakte Übereinstimmung mit
dem eingecheckten Zertifikat. Manipulierte Schritte und abweichende Lösungen werden
abgelehnt. Die Routine ist auf F-01 Revision 1/20×20 monochrom begrenzt, bleibt
außerhalb der Spielausführung und ist kein allgemeiner Produkt-Solver oder Editor.
