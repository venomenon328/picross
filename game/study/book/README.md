# Buchstudie B-A · #493

Isolierter ausführbarer Studienstand. Der normale Spielstart verwendet weiterhin
das bisherige A-Buch. Drei feste synthetische Muster, keine echten Rätsel oder
Spielstände; Bearbeitung und Sortierung gelten nur bis zum Schließen der Studie.

Mit der gebundenen Godot-4.7.2-Toolchain nach Import:

```sh
godot --path game res://study/book/main.tscn
```

Eine Karte öffnet ihr Blatt mit insgesamt drei Sekunden Bewegung. Der Buchreiter
kehrt zum Katalog zurück. Escape beendet einen laufenden Wechsel zum Katalog.
Die vorhandenen Werkzeuge lassen sich auf der ruhenden Seite ausprobieren.
Fenster-/UI-Wechsel und Fokusverlust stellen die gewählte Arbeitsseite stabil
her; während der Bewegung und bis zum Loslassen gehaltener Tasten bleibt die
Eingabe gesperrt. Nebenwege sind vorhandene unmittelbare UI, keine B-B-Integration.

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
drei bestehenden Konfigurationen, erzeugt einen 30-fps-Enginefilm sowie getrennte
Windows-/Webstudienexporte und kontrolliert beide regulären Pakete auf Ausschluss.
Er startet keinen Browser. `--native-only` ist eine ausdrücklich unvollständige
Entwicklungsprüfung ohne Exporte. Quellenbindung, Hashes, Zeiten und Grenzen
stehen in `report.json`; `native.json` und Originalframes ergänzen den Nachweis.

Die Materialshader und Meshkonstruktion sind eigene prozedurale Studienquellen:
kein Fremdmodell, kein Rasterasset und keine neue Bibliothek. Lederporen, Holz,
Papierkanten und ruhige Papierstruktur sind deterministische Shaderfunktionen;
Parameter stehen direkt in `main.gd` und den beiden Shadern. T01/T06 stammen aus
`tools/product_fixtures.py`, T08 daraus mit 30 statt 40 Zeilen und neu abgeleiteten
Spaltenhinweisen. Regeneration: `python tools/book_study.py --write-fixtures`.
Die drei kleinen SVGs sind eigene technische Spoilersentinels, keine Motive.
`report.json` bindet sämtliche Studienquellen per SHA-256.

Tidy Hand, Delight Coffee, Bakso, Fraunces, Plex, Zellatlanten, SL-Rahmen und
HZ-Icons bleiben unveränderte Projektressourcen mit ihren bestehenden Rechten
und Nutzungshinweisen. Die geerbten UI-Skripte halten auch das historische A-PNG
als Ressource; die Studie zeichnet es nicht als Buchmaterial. Die Exportpakete
liefern die bestehenden Nutzungshinweise mit. Alte Assets/Freigaben werden
weder ersetzt noch umetikettiert.

Bericht, Zustandsvertrag und offene Gates: [B-A-T01](../../../docs/BOOK_STUDY.md).
