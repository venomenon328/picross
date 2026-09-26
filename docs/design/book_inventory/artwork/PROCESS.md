# BP-2 · Herkunft und tatsächlicher Bildweg

Stand: 26.09.2026 · Basis `4ef926fe033418090512d82b9aba151031534c5f`.

## B2-01 und Inputs

Der gelesene lokale `imagegen`-Skill wurde im bevorzugten eingebauten Modus genutzt.
`image_gen.imagegen`, aufgerufen über `functions.exec`, nahm lokale PNG-Referenzen
entgegen und lieferte echte lokale PNG-Dateien unter dem Codex-Bildverzeichnis.
Die ausgewählten Dateien wurden in dieses Paket kopiert. Kein API-Schlüssel,
CLI-Fallback, Assetkauf oder zusätzlicher Dienst. Die Antwort lieferte Bild und
Dateipfad, aber keine Modell-ID, Seed- oder Qualitätsparameter; diese bleiben unbekannt.

AGENTS.md, Workflow, Projektprofil einschließlich aktueller BP-1R-Ergänzung,
Produktdefinition, Gestaltungskonzept, Modellauswahl/-katalog sowie vollständige
#27- und #21-Bodies mit Kommentaren gelesen. Aktueller main ist der gebundene
PR-#30-Squash. Spätere Issue-Bodies ersetzen die historischen Doppelseitenkommentare.
Die Produktionsanleitung, das Briefing, der Prüfbericht, Layout/Manifest und die
Bildinputs stammen unverändert von diesem Commit. Die vorhandene BP-1R-Lieferprüfung
war vor Bildproduktion erfolgreich. Beide Mastermasken und F-02-Layouts tatsächlich
geöffnet, alle fünf UI-/Einzelmaskensätze als benannte Übersichten betrachtet.

Die optionale alte Albumstudie war nicht angehängt und wurde nicht verwendet.
Der textliche Materialvertrag genügt ausdrücklich gemäß #27. Kein Zugriff auf oder
Nachzeichnen des verworfenen alten Chat-A. Die technische Geometriehilfe
[geometry-only.png](inputs/geometry-only.png) übernimmt ausschließlich `book`,
`sheet`, `fold` und `right_page_slice` aus dem 2560er BP-1R-Fall. Sie ist kein Artwork.
Masken wurden als Referenzen übergeben, niemals als angebliche Inpainting-Alpha.

## A: Herstellung, gezielte Korrekturen, Qualifikation

Vollständige tatsächlich übergebene Texte:
[A-01](prompts/a-01.txt), [A-02](prompts/a-02.txt), [A-03](prompts/a-03.txt),
[A-04](prompts/a-04.txt), [A-05](prompts/a-05.txt).
Die [Laufzuordnung](generation.json) enthält Eingaberollen, native Maße und
SHA-256 jeder Ausgabe. Nicht gewählte Zwischenbilder bleiben außerhalb der Lieferung;
ihre Hashes sind Verlauf, keine lokal ausgelieferten Dateinachweise.

A-01 erzeugte ausgearbeitetes Material, aber zu viel linken Rand, Requisiten und
Patina. A-02 entfernte die Gegenstände. A-03 korrigierte den linken Rand noch
unzureichend. A-04 nutzte zusätzlich die genaue UI-freie Geometriehilfe und erreichte
die breite Arbeitsseite. A-05 beruhigte die Papiertextur. Alle Korrekturen blieben
auf denselben Kandidaten bezogen; keine unabhängige Variantenserie.

Der untere Papierrand blieb trotz Bildbearbeitung ungefähr 24 native Pixel zu hoch.
Die in B2-02 erlaubte lokale Materialretusche verschiebt vorhandene untere Bildpixel
um 24 Zeilen nach unten. Zeilen 820–879 blenden linear zwischen Originalzeile und
Zeile `y-24`, ab 880 wird `y-24` übernommen. Das unterste Material wird dadurch
beschnitten. Kein opaker Füllblock, keine neu gezeichnete Ersatzbuchgrafik, keine
nichtproportionale Skalierung. Pillow 12.3.0 führte diese begrenzte Pixelretusche
aus; sie ist vollständig anhand Generatorquelle und qualifizierter Quelle prüfbar.
Die schmale Übergangszone ist weicher als die übrigen Ränder.

A wurde vor B am Hintergrund, vier nativen Detailausschnitten, 1080p und allen
fünf BP-1R-Montagen angesehen. Erst danach wurde die qualifizierte native A-Datei
als Editierziel an B übergeben. Die erste Vorschau verwendete Lanczos für die
Ausgabeaufbereitung; die endgültige Lieferung verwendet den unten reproduzierbaren
bilinearen Pfad und wird erneut geprüft. Die Materialquelle bleibt dieselbe.

## B und Ausgabeaufbereitung

[B-01](prompts/b-01.txt) bearbeitet ausschließlich das qualifizierte A: taupebraunes
Gewebe mit Lederkante, warmes Elfenbeinpapier, diffuseres Licht und geringerer
Schattenkontrast. Kein globaler Farbfilter. Keine neue Komposition oder Gegenstände.
Die native B-Ausgabe wird ohne weitere Materialretusche verwendet.

Beide Generatorquellen sind 1672×941 RGB. Für exakt 16:9 wird das kontinuierliche
Quellrechteck `[0,0.25,1672,940.75]` verwendet; oben und unten je 0,25 Pixel Beschnitt.
Beide Achsen skalieren identisch mit `2560/1672`. Bilineare Abtastung an Pixelzentren,
danach BP-1R-Faktoren 1 / 0,75 / 0,5 für die Kontrollansichten, Offset null.
Die unveränderten UI-PNGs werden ohne Skalierung per Source-over aufgesetzt.
Kein Schärfe-/Detailgewinn durch die Ausgabe in 2560×1440 behauptet.

Der enge [Dateihelfer](../../../../tools/book_inventory/artwork.py) erzeugt nur
Ausgaben, Ausschnitte, Kontrollmontagen, Hashmanifest und ZIP. Er generiert keine
Illustration und verändert keine Produktionsvorlage. Alle Prüfungen funktionieren
mit Python-Standardbibliothek; Bildgenerierung findet niemals in CI statt.

Keine fremde Stockgrafik oder ungeklärte externe Bildvorlage verwendet. Generierung
ist keine pauschale Rechtegarantie. Die Repo-eigenen technischen Eingaben, Prompts,
Bearbeitungen und Ausgaben sind nachvollziehbar dokumentiert.
