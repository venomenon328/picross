# Buchstudie B-A-N01 · #493

Isolierter ausführbarer Studienstand. Der normale Spielstart verwendet weiterhin
das bisherige A-Buch. Drei feste synthetische Muster unter 27 Katalog-IDs, keine echten Rätsel oder
Spielstände; Bearbeitung und Sortierung gelten nur bis zum Schließen der Studie.

Mit der gebundenen Godot-4.7.2-Toolchain nach Import:

```sh
godot --path game res://study/book/main.tscn
```

Der Katalog zeigt eine Doppelseite mit mittiger Bindung, höchstens 24 Karten und
gemeinsamer Sortierung/Filterung. Beide Hälften scrollen gemeinsam. Weiter blättert
rechts nach links, Zurück links nach rechts, jeweils 0,85 Sekunden; Randbefehle
bewegen nichts. Filter und Sortierung wirken sofort.

Eine neue/begonnene Karte öffnet drei einzelne Blätter in insgesamt drei Sekunden
und endet auf der großen rechten Arbeitsseite mit Bindung links. Der Buchreiter
kehrt zum Katalog zurück. Escape beendet einen laufenden Wechsel zum Katalog.
Die vorhandenen Werkzeuge lassen sich auf der ruhenden Seite ausprobieren.
Fenster-/UI-Wechsel und Fokusverlust stellen die gewählte Arbeitsseite stabil
her beziehungsweise beenden einen Katalogwechsel auf dessen Zielseite;
während der Bewegung und bis zum Loslassen gehaltener Tasten bleibt die
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

Die Meshkonstruktion und Materialshader sind eigene Studienquellen. Sie verwenden
das unveränderte A-Buch `art/book/bp2-a-inventarband.png` als Materialquelle für
Papier und Einband, mit dessen bestehenden Herkunfts-/Nutzungshinweisen.
SHA-256: `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`.
Keine neuen Fremdmodelle, Bildrechte oder Bibliotheken. Parameter, Flächen und
UV-Ausschnitte stehen in `main.gd` und den Shadern. T01/T06 stammen aus
`tools/product_fixtures.py`, T08 daraus mit 30 statt 40 Zeilen und neu abgeleiteten
Spaltenhinweisen. Weitere feste IDs wiederholen nur diese Formen und erzeugen
die nötige volle/teilweise Katalogseite. Regeneration:
`python tools/book_study.py --write-fixtures`.
Die drei kleinen SVGs sind eigene technische Spoilersentinels, keine Motive.
`report.json` bindet sämtliche Studienquellen per SHA-256.

Tidy Hand, Delight Coffee, Bakso, Fraunces, Plex, Zellatlanten, SL-Rahmen und
HZ-Icons bleiben unveränderte Projektressourcen mit ihren bestehenden Rechten
und Nutzungshinweisen. Die A-Bildbytes bleiben unverändert; die neue Geometrie
verwendet nur UI-freies Material, keine gespiegelten Texte. Die Exportpakete
liefern die bestehenden Nutzungshinweise mit. Alte Assets/Freigaben werden
weder ersetzt noch umetikettiert.

`opening.avi` zeigt beide Blätterrichtungen und die volle Öffnung in normalem
Tempo. Alte/neue native Ansichten und Bindungsdetails dienen dem Materialvergleich;
Originalpixelpaare prüfen separat die Textur-/Direktübergabe.

Bericht, Zustandsvertrag und offene Gates: [B-A-N01-T01](../../../docs/BOOK_STUDY.md).
