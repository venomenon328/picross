# BP-2 · Prüfbericht

Stand: 26.09.2026 · B2-01 bis B2-05 · Branch `chore/27-bp2-buchillustrationen`.
Basis und unveränderter BP-1R-Input: `4ef926fe033418090512d82b9aba151031534c5f`.
Finaler Head, Test-Merge, tatsächliche CI-Ergebnisse und getrennter Selbstreview
werden im eigenen Draft-PR gebunden. Keine alten BP-1R-Läufe als BP-2-Nachweis.

## Dateiprüfung

Der [enge Prüfer](../../../../tools/book_inventory/artwork.py) wird durch die
bestehende unittest-Entdeckung ausgeführt. Nur Python-Standardbibliothek, kein
Netzwerk oder Bildgenerierungsdienst. Geprüft werden tatsächliche Datei-/PNG-Bytes:

- Vollständige PNG-Decodierung einschließlich CRC, Dekompression und Filterumkehr;
  Maße, RGB/Opazität, Dateimenge und SHA-256 für alle Paketdateien.
- Alle versionierten BP-1R-Produktionsdateien bytegleich zum gebundenen Commit,
  einschließlich Vorlagen, Masken, Quellen, Dokumente und Review-ZIP.
- A-Retusche gegen die native Generatorquelle; außerhalb der unteren Zone exakt
  unverändert, darin dokumentierter Pixeltransfer mit höchstens einem Kanalwert
  Rundungsdifferenz zu Pillow. Beide finalen 2560er Bilder vollständig aus ihren
  nativen Quellen rekonstruiert; gleicher Maßstab beider Achsen, expliziter Beschnitt.
- Alle zehn Kontrollmontagen pixelweise rekonstruiert: nur Hintergrund skalieren,
  exakte BP-1R-PNGs in eigener Größe per Source-over. Zusätzliche native/Screen-
  Ausschnitte byteweise auf korrekte Ausschnittpixel geprüft.
- Lokale Normaltext-Minima erneut berechnet, ZIP-Dateimenge und jeder Eintrag
  bytegleich zum Paket. Separate kleine Rechenbeispiele prüfen Alpha 0/128/255,
  Pixelzentren sowie Ablehnung nichtproportionaler Skalierung und falscher UI-Größe.

## Tatsächliche Sichtprüfung

A vor B und beide finalen Ausgaben nach der endgültigen Aufbereitung betrachtet.
Alle zehn Gesamtmontagen einzeln geöffnet; 2560er Ansichten wurden vom Anzeigetool
teilweise auf 2048 Pixel Breite verkleinert. Deshalb zusätzlich alle 20 unskalierten
Zahlen-/Statusausschnitte als zwei beschriftete 1:1-Tafeln gesichtet, sowie die vier
nativen Materialausschnitte pro Kandidat. Beide Hintergründe allein bei 1080p und
ihre nativen Materialquellen angesehen. Kein behaupteter 1:1-Gesamtbildtest aus
einer verkleinerten Anzeige.

Ergebnis des Bearbeiters: beide als Hintergrundkandidaten nutzbar. Eine große
flache linke Seite, Falz am rechten Rand, schmaler angeschnittener Fortsetzungsbereich.
Keine vollständige Doppelseite, Texte, Pseudoschrift, Raster, Werkzeuge, Register-
attrappen oder Lösungsbilder in den Hintergründen erkannt. B zeigt gewebtes Taupe
statt des dunklen Leders, bei erhaltener Buchlage und ruhigerem Licht.

Materialdetails liegen an den schmalen Buchrändern. Die Papierfläche bleibt warm
und leicht strukturiert; kein opaker Kartenersatz über der Arbeitsfläche. Bindung,
kleine Metall-/Blauakzente und Seitenkante sind auch bei 1080p erkennbar. Wegen der
nativen Auflösung und schmalen Randreserve bleiben sehr feine Nähte/Seitenlagen
begrenzt. A hat eine weichere lokale Retuschezone unten; das ist dokumentiert,
nicht als unberührte Generatorausgabe dargestellt.

Bei allen fünf Fällen bleiben Raster/Hinweise, eigene Miniatur, Palette, Koordinaten,
Werkzeugzustand und Navigation auf ihren vorgesehenen Flächen. Keine Blattkante
oder Falzschatten durch Hinweiszahlen bzw. Status, insbesondere F-03 und 720p/UI 125 %.
Die natürliche gezeichnete Kante weicht geringfügig von einer mathematischen Geraden
ab; die UI wird dafür weder verschoben noch verkleinert. Am linken Rand überlagert
der unveränderte opake Albumknopf den Materialrand; seine Lesefläche ist die
BP-1R-Knopffläche. Die Binärmasken sind keine pixelgenaue Garantie für generierte
Materialgrenzen. Kein OCR-/Kunstqualitätsbeweis aus Prompts oder Dateihashes.

## Kontrast auf tatsächlichem Material

`checks/contrast.json` enthält jeden normalen Text mit seinem im BP-1R-Browser
gemessenen Rechteck. Für die gesamte Rechteckfläche wird der kleinste Kontrast zum
deklarierten Textfarbwert `#293e3d` berechnet, nicht ein Mittelwert des Papiers.
Unter „DEIN STAND“ liegt die unveränderte opake BP-1R-Miniaturkarte `#fffaf0`.
Antialias-Kanten werden nicht als eigene Textfarbe gewertet.

| Fall | Minimum A | Minimum B |
| --- | --- | --- |
| F-02 1080p | 8,0986:1 | 8,3355:1 |
| F-02 1440p | 8,0558:1 | 8,4757:1 |
| F-01 1440p | 8,0558:1 | 8,4757:1 |
| F-03 1080p | 8,0986:1 | 8,3355:1 |
| F-02 720p / UI 125 % | 8,3233:1 | 8,7076:1 |

Damit wird das 4,5:1-Entwurfsziel für normale UI-Texte in diesen Montagen erreicht.
Rätselfarben und vorhandene C1-Konturen bleiben unverändert; sie sind ausdrücklich
nicht durch dieses Normaltext-Ergebnis zertifiziert. Die historische technische
Studienfußzeile liegt auf dem dunkleren Außenrand und ist dort kontrastarm. Sie ist
keine Produkt-UI und wurde entsprechend der Pflicht zu unveränderten Overlays nicht
umgestaltet; sie gehört nicht zum Normaltext-Kontrasturteil.

## Reproduktion und Abnahmen

Im Repositoryroot, Python 3.11 oder neuer:

```powershell
python tools/book_inventory/artwork.py verify
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
git diff --check 4ef926fe033418090512d82b9aba151031534c5f HEAD
```

`artwork.py build` rekonstruiert Ausgaben/Kontrollen/Manifest/ZIP aus den erhaltenen
nativen Dateien, `pack` aktualisiert Metadaten/ZIP nach Dokumentänderungen. Kein
Aufruf des unveränderten Produktionsgenerators erforderlich. Das ZIP enthält keine
Tools; den Helfer am im PR gebundenen Repositorycommit verwenden.

Die lokalen Abschlussresultate und aktuellen `docs`-/`product`-/`preflight`-Läufe
stehen im PR. Produktworkflows prüfen den bestehenden P1, keine künstlerische
Qualität oder native Darstellung dieses noch nicht integrierten Hintergrunds.

Lokaler vollständiger Testlauf: 57 Tests in 71,330 Sekunden erfolgreich, ein
bestehender Windows-Symlinktest übersprungen. Die Dokumentprüfung im ursprünglichen
Arbeitsbaum erfasste vorhandene ignorierte Altartefakte/venvs unter `artifacts/` und
meldete 629 Probleme. Diese fremden Dateien wurden nicht verändert. Die Lieferung
wird deshalb zusätzlich als vollständiger Export des Git-Index in einem isolierten
temporären Verzeichnis mit demselben unveränderten Dokumentvalidator geprüft;
Resultat und aktueller CI-Nachweis stehen im PR.

Offen vor späterem Merge: unabhängiges technisches/visuelles Review und ausdrückliche
Eigentümerfreigabe. Getrennter Selbstreview ist keine unabhängige Prüfung. Finale
Kunst-/Typografie-/Icon-/Layoutwahl bleibt BP-3; reale DPI-/Bedienprobe nicht erfolgt.
Kein BP-3/#23/#24-Start, keine Spiellogikänderung, kein Merge/Release.
