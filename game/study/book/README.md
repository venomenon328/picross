# Buchstudie B-A-N06 · #496

Isolierter ausführbarer Studienadapter um den gemeinsamen Kern unter `game/book/`.
Der normale Spielstart verwendet die [reguläre B-B-Integration](../../../docs/BOOK_INTEGRATION.md).
Die Studie enthält drei feste synthetische Muster unter 27 Katalog-IDs, keine echten Rätsel oder
Spielstände; Bearbeitung und Sortierung gelten nur bis zum Schließen der Studie.

Mit der gebundenen Godot-4.7.2-Toolchain nach Import:

```sh
godot --path game res://study/book/main.tscn
```

Der Katalog zeigt eine Doppelseite mit mittiger Bindung, höchstens 24 Karten und
gemeinsamer Sortierung/Filterung. Bis zu zwölf Karten stehen zuerst links,
die übrigen rechts. Beide Hälften scrollen unabhängig; ihre Positionen bleiben
beim Öffnen und Zurückkehren erhalten. Eine neue Filter-/Sortierwahl setzt beide
zurück, eine unveränderte Auswahl erhält sie. Weiter blättert
rechts nach links, Zurück links nach rechts, jeweils 0,85 Sekunden; Randbefehle
bewegen nichts. Filter und Sortierung wirken sofort.

Eine neue/begonnene Karte öffnet drei einzelne Blätter in insgesamt drei Sekunden
und endet auf der großen rechten Arbeitsseite mit Bindung links. Der linke Pfeil
im rechten Arbeitskopf
kehrt in 1,8 Sekunden mit Herauszoomen und drei nach rechts blätternden Seiten zum
erhaltenen Katalogkontext zurück. Der aktuelle Arbeitsstand bleibt sichtbar.
Escape bricht nur einen laufenden Wechsel ab: Blättern/Öffnen endet im Quellkatalog,
Rückkehr im gebundenen Zielkatalog. Im ruhenden Spiel ist Escape keine Katalognavigation.
Die vorhandenen Werkzeuge lassen sich auf der ruhenden Seite ausprobieren.
Fenster-/UI-Wechsel und Fokusverlust stellen die gewählte Arbeitsseite stabil
her beziehungsweise beenden einen Katalogwechsel auf dessen Zielseite;
während der Bewegung und bis zum Loslassen gehaltener Tasten bleibt die
Eingabe gesperrt.

Rechts stehen genau Katalogpfeil, Menü und Hilfe. Der alte linke Reiter entfällt.
Menü öffnet die Einstellungen links, `?` die Hilfe rechts, jeweils im Arbeitsnahmaßstab.
Beide Zugänge gibt es auch im Katalogfuß; bei knapper Breite steht „Weiter“ darunter.
Eintritt und Rückkehr blättern ein Blatt in 0,85 Sekunden. Beim Katalogbesuch fährt
die Kamera zugleich nah beziehungsweise wieder weit; bei Arbeit bleibt der Maßstab.
Einstellungen↔Hilfe pannt ohne Blatt/Zoom in 0,65 Sekunden. Navigation steht über
den beiden getrennten Scrollbereichen; der vollständige Hilfetext bleibt erreichbar.
„Zurück zum Katalog/Rätsel“ führt zum Ursprung dieses Besuchs. Arbeitsstand,
Katalogfilter/-sortierung und beide Scrollstände bleiben erhalten; bewusst geänderte
Optionen werden übernommen. Derselbe Informationszugang setzt Scrollen nicht zurück.
Escape während Eintritt/Pan stabilisiert die Quelle, während Rückkehr den Ursprung.
Resize, UI-Wechsel und Fokusverlust stabilisieren jeweils das gewählte Ziel.
Diese H?lle pr?ft dieselbe Pr?sentation mit isolierten Inputs.

Der getrennte Windows-Studienexport startet mit `book-study.exe`; EXE und PCK
bleiben zusammen. Der Webexport benötigt einen lokalen HTTP-Server. Er wurde
exportiert und statisch geprüft; eine Browserdarstellung wird damit nicht belegt.
Kein Deployment und kein Zugriff auf echte Spielprofile.

Für eine spätere ausdrücklich gewünschte Webprobe lokal bereitstellen:

```sh
python -m http.server 8000 --directory <ausgabe>/web
```

Danach `http://127.0.0.1:8000/` öffnen. Dies startet der Prüfharness nicht selbst.

Reproduzierbare technische Lieferung im Repository-Root, Python 3.11+ und
Pillow exakt 12.3.0 in einer eigenen venv:

```sh
python tools/book_study.py --cache-dir <gebundener-archivcache> --output-dir <leeres-ziel>
```

Der Harness isoliert Projekt und Benutzerpfade, prüft native Bewegung und die
drei bestehenden Konfigurationen und gezielt 1920×1200/UI100, erzeugt einen 30-fps-Enginefilm sowie getrennte
den regulären Lifecycle an synthetischen Daten. Er startet keinen Browser.
`--native-only` ist der Standard; reguläre Exporte werden von den Produkt-/Web-
Buildern geprüft. `--study-exports` erzeugt nur bei gesondertem Bedarf die frühere
Studienmatrix. Quellenbindung, Hashes, Zeiten und Grenzen
stehen in `report.json`; `native.json` und Originalframes ergänzen den Nachweis.
Im optionalen Studienexport führt der Windowsplayer zusätzlich Standardfenster,
Maximieren, Öffnen/Bearbeiten/Rückkehr und Wiederherstellen aus. Der Bericht
`windows-native.json` trennt Desktop-, Client-/Framebuffermaße und Skalierungen.

Die Meshkonstruktion und Materialshader sind eigene Studienquellen. Das
unveränderte A-Buch `art/book/bp2-a-inventarband.png` bleibt Qualitätsreferenz und
reguläre Produktressource mit seinen bestehenden Herkunfts-/Nutzungshinweisen.
SHA-256: `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`.
Der Einband verwendet die eigene homogene Ledertextur `leather.png`, ohne alte
Buch-/Untergrundkanten. `leather.json` bindet Prompt, Herkunft, Rechte, SHA-256 und
Import; die Exporte enthalten `licenses/Study-leather.json`. Der gerundete Einband,
Seitenblock und Rücken haben gemeinsam konstruierte Anschlüsse, gefilterte Lagen
und geometriebezogene Schatten. Die durchstoßenden kleinen Zierbänder an den
inneren Enden entfallen; der ganze Buchkörper bleibt erhalten. Das eigenständige
zusammenhängende Tischbild `table.png` liegt auf einer festen Weltfläche hinter
dem Buch. `table.json` beziehungsweise `licenses/Study-table.json` bindet Prompt,
Werkzeug, Rechte, Quellbytes, Hash und verlustlosen Mipmapimport ohne Repeat.
Die Innenflächen verwenden `paper.png`, eine originale imagegen-Ausgabe ohne
Fremdvorlage. `paper.json` bindet vollständigen Prompt, Herkunft, SHA-256, Rechte,
Import und logische Seitenzuordnung; die Exporte liefern diese Angaben auch unter
`licenses/Study-paper.json`. Die Textur wird unverändert importiert, mit Mipmaps
gefiltert und im Shader zurückhaltend aufgehellt. Die ruhende Falzwölbung ist echte
Geometrie außerhalb des ebenen UI-Bereichs. Controls nutzen transparente Füllung.
Hover/Druck verstärken ihre vorhandene Kontur. Leere/Whitespace-Hilfe erzeugt
kein Panel; sinnvolle Hilfen bleiben nach normaler Verzögerung erhalten.
Keine neuen Fremdmodelle oder Bibliotheken. Parameter, Flächen und
Materialzuordnung stehen in `binding.gd`, `main.gd` und den Shadern. T01/T06 stammen aus
`tools/product_fixtures.py`, T08 daraus mit 30 statt 40 Zeilen und neu abgeleiteten
Spaltenhinweisen. Weitere feste IDs wiederholen nur diese Formen und erzeugen
die nötige volle/teilweise Katalogseite. Regeneration:
`python tools/book_study.py --write-fixtures`.
27 eigene kleine SVGs sind technische Spoilersentinels, keine Motive. Jede ID
besitzt eine eigene Definition und Revealzuordnung. `inputs.gd` prüft alle mit
den normalen Registry-/Definitionsvalidatoren und einem festen Studienpfadpräfix;
auch kopierte Formen behalten keine fremde `reveal.definition_id`.
`report.json` bindet sämtliche Studienquellen per SHA-256.

Tidy Hand, Delight Coffee, Bakso, Fraunces, Plex, Zellatlanten, SL-Rahmen und
HZ-Icons bleiben unveränderte Projektressourcen mit ihren bestehenden Rechten
und Nutzungshinweisen. Die A-Bildbytes bleiben unverändert; der Studien-
Einbandshader verwendet ausschließlich das eigene Leder. Die Exportpakete
liefern die bestehenden Nutzungshinweise mit. Alte Assets/Freigaben werden
weder ersetzt noch umetikettiert.

`opening.avi` zeigt beide Blätterrichtungen und die volle Öffnung in normalem
Tempo sowie die Rückkehr nach echter Bearbeitung. Alte/neue native Ansichten und Bindungsdetails dienen dem Materialvergleich;
Fünf bisherige und vier neue Originalpixelpaare prüfen separat die Textur-/Direktübergabe.
Der Film enthält zusätzlich alle zehn Informationswege. Originale Informationsbilder
und Alphahüllen prüfen beide Seiten in vier Flächen; sechs echte Unterbrechungen
ergänzen eine günstige vollständige Entscheidungstabelle. Sechs unskalierte
Randdetails je gebundener Fläche einschließlich oberem und unterem Falz sowie tatsächliche verzögerte Tooltipbilder ergänzen
die Sichtprüfung; Quelle, Rechteck und Kosten stehen im Bericht.

Für B-A-N05-F01 ergänzt `tools/book_windows_probe.py` die native Prüfung durch
echte Windows-Mausereignisse. Auf einem freien Windows-Desktop, mit Python und
Pillow aus der vorhandenen isolierten Prüfumgebung:

```powershell
python tools/book_windows_probe.py --source artifacts/book-n05-f01-work/final --output artifacts/book-n05-f01-work/windows-final --head <vollständiger-Head>
```

`--source` enthält den vollständigen sauberen Studienexport mit `report.json`.
Der Treiber prüft dessen Head und EXE-/PCK-Hashes, verwendet isolierte Profile,
ergänzt in einer bytegleichen privaten EXE-/PCK-Kopie über `override.cfg` einen
externen rein lesenden Autoload-Beobachter am regulären Studien-Einstieg
und sendet ausschließlich echte OS-Mausereignisse. 32 Raster-/Kopfbutton-Rundwege,
Zell-Commits, Undo/Redo, Werkzeug/Farbe, Fokusverlust, Resize und Außenloslassen
werden protokolliert. Bei unerwartetem Fokusverlust bricht er die Eingabe ab.
Die Spur ist auf 4096 Engine-Einträge, der Lauf auf 180 Sekunden begrenzt.
Ein gewöhnlicher Exportstart ohne Beobachter und Originalbilder ergänzen den
Nachweis; kein physischer Eigentümer-Spieltest wird dadurch behauptet.

Für N06 ergänzt `--fold` beim gleichen Windows-Treiber echte Katalog-/Arbeits-/
Informationswege bei UI100 und UI125, Maximieren/Wiederherstellen und originale
Clientbilder. Anschließend läuft die vorhandene F01-Regressionsroute unverändert.
Vier kleine Shader-Tiefenbilder prüfen den echten Falz mit verbreitertem Spalt
und flacher Geometrie als Gegenbeispielen; der Einband bleibt im bisherigen Budget.

Historischer Bericht und Zustandsvertrag: [B-A-N06-T01](../../../docs/BOOK_STUDY.md).
Unabhängiges R08 und persönliche B-A-M01 sind auf PR #497 abgeschlossen.
Für B-B gelten die getrennten Gates im [aktuellen T01](../../../docs/B_B_VERIFICATION.md).
Frühere F01-Reviews und Eigentümerausnahmen bleiben an PR #495 gebunden.
