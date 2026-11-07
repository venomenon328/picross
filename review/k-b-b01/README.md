# K-B / B-01: aktuelle Windows-Originale

Produkt-Head `6b4bede4d76cce539daa488027e66711a5538db5`, Basis `c64cae2a464ccd8d27e986620592f6ef8667efea`.
Quelle: [B-01](https://github.com/venomenon328/picross/pull/538#issuecomment-6706794206).
Akteur: Implementierer; technische Nacharbeit vor Merge, keine unabhängige oder persönliche Abnahme.

Die acht `marker-*.png`/`save-*.png` sind native Originalausschnitte des rechten Buchkopfs:
1280×720/UI100/125 und 1920×1080/UI100/125, jeweils beide Fehler-/Retrywege.
Keine Skalierung, Montage oder nachträgliche Bildbearbeitung; der externe Beobachter
speichert die angegebenen Pixel direkt aus dem aktuellen Viewport. Je `*-crop.json`
nennt den Ursprung im vollständigen Clientframe; `manifest.json` bindet Bytes/SHA-256.
Alle acht Originale wurden vom Implementierer geöffnet.

`observations.json` enthält acht Fehler-/Trefferfälle und vier erfolgreiche Retrypaare.
Pro Fehlerfall: vollständiger Clipvergleich, fünf echte OS-Klicks (vier Ecken einen Pixel
innerhalb der Kante und Mitte), unabhängiger Signalzähler, danach erfolgreiche Wiederholung.
UI100 misst 44 px, UI125 55 px; Clip 48/60 px. Lange synthetische Meldungen scrollen
separat; Sortierung, Filter, Fortsetzen-Panel und Karten-Scrollrechtecke bleiben erhalten.
`os.jsonl` protokolliert die tatsächlichen Maus-/Navigationsinputs.

Echter Windowsprozess, NVIDIA RTX 3070/OpenGL, Monitor 2560×1440 und gemeldete DPI in
jeder Beobachtung. Vier Konfigurationen im selben echten EXE/PCK-Prozess, isoliertes
Testprofil, 54 feste synthetische IDs, keine echten Saves oder Produktionsrätsel.
Fenstergrößen und UI-Skala werden über die echten Einstellungen gewählt.

Merkerfehler: nach echter Bearbeitung von Blatt 02 wird die eigene Tempdatei als
Verzeichnis blockiert, Blatt 04 per Maus bearbeitet; alte Merkerbytes bleiben gleich.
Savefehler: der **externe Testtreiber** ruft im Katalog einmal die bestehende
`_save_current()`-Grenze auf, während die eigene Slot-Tempdatei ein Verzeichnis ist.
Die Fehler sind echte Dateisystemfehler, keine `fail_step`-Simulation im Produkt.
Der Beobachter setzt außerdem ausschließlich für die Überlängenprobe einen langen
synthetischen Diagnosetext. Alle Retry- und Scrollinputs erfolgen über die OS-Maus.
Diese zwei gezielten Testinjektionen sind in `driver/observer.gd` sichtbar; sie
gehören nicht zum Produkt-PCK. Der Source-/Registry-Testaufbau ist in `driver/build_gui.py`.
Die Treiber sind befristete Originale dieses Laufs, keine neue Dauersuite.

`build.json`: tatsächlich exportiert auf `36cf3a9a0947f188f34a44126cf12571094d979f`.
Danach änderte sich nur `.ci/package.json`; **alle 69 Produktquellen** wurden gegen
den finalen Head `6b4bede4d76cce539daa488027e66711a5538db5` erneut byteweise per SHA-256 abgeglichen. EXE/PCK-Hashes
sind gebunden; der externe Autoload-Beobachter erweitert nur die Testumgebung.
Die reguläre Windowslieferung des aktuellen Produktbestands liefert separat Package CI.

Empfänger: unabhängiger K-B-R01-Reviewer und Eigentümer bei passendem Prüfumfang.
Nur separater Reviewref `review/485-k-b-b01`, kein Merge-PR und keine Übernahme in main.
Nach abgeschlossener B-01-Sichtung/R01 rückbauen; Bedarf spätestens **21.11.2026** prüfen.
K-B-W01 bleibt offen; keine Browser- oder Mergefreigabe.
