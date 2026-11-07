# K-A-T02 · befristete Revieworiginale

Implementiererprobe durch Codex am 07.11.2026, kein unabhängiges R01 und keine
persönliche Eigentümerabnahme M01. PR #537, Issue #485, ausschließlich K-A.

Produkt-Head: `df072ba1bf8f15e0eaf4b88d575b52c39ad4ecf6`; Basis: `ec2188b5da7b3f24a070592b6fbe7b8003c73cc1`.
GitHub-Test-Merge: `58aa37cf4fa03a94b27da8c91c81f936b79872f5` (nicht gemergt).
Maßgeblich sind die ursprüngliche Paketentscheidung und die aktuellen ergänzenden
Entscheidungen 6704732025 / 6704802593 im Issue #485.

## Tatsächliche Probe

Windows 11 Pro 10.0.26200, NVIDIA GeForce RTX 3070, OpenGL Compatibility,
Godot 4.7.2.stable.official.ed1daf0bf; Monitor 2560×1440, gemeldete DPI 96.
Exportierte Windows-EXE/PCK mit unverändertem Produktcode des genannten Heads,
keine beschleunigte BookFixture, kein Test-Szenenroot und kein Browser.
Der Export wird gegen sämtliche versionierten Produkt-GDScript-/Szenen-/Projekt-/
Shaderbytes geprüft; Hashes in `source/build-manifest.json`. EXE/PCK sind nicht
Teil dieser begrenzten Galerie. Der reguläre aktuelle Windows-Spieler wird im
CI-Artefakt des PR bereitgestellt; er enthält den regulären Katalog.

Hier ausschließlich 54 synthetische, als test_only markierte Rätsel aus den
bestehenden Runtime-/KAT2-Fixtures. 48 in der absichtlich langen Testkategorie,
sechs Vögel, wechselnde vorhandene Stufen/fehlende Einstufung und Mono/Farbe,
27 gültig gelöste Ausgangsslots. Slot 005 ungültig, Slot 000 gültiges Backup bei
kaputter Primärdatei. Eigenes APPDATA/Saveprofil; keine Nutzerspielstände.
Registry und Fixturehashes stehen unter `source/`.

Der externe Observer liest Zustände und speichert unveränderte Root-Viewport-PNGs.
Er verändert weder Spielzustände noch Szenen noch Saves. OS-Maus bewegt/klickt
über Win32; echte Mausräder bedienen beide Hälften. Dropdowns werden mit der
Maus geöffnet und mit echten Pfeiltasten/Enter gewählt. Keine behauptete reine
Mausauswahl aller Menüeinträge. Programme/Controls außerhalb des eigenen PID
werden nicht angeklickt. Trace: `os.jsonl`; auslesbare Zustände zu jedem Original.

Alle 30 Kontrollen in `checks.json` bestanden. Der finale komplette Lauf
beendet sich regulär ohne Skript-/Renderfehler. Geprüft: native Clients
1920×1080/UI100, 1280×720/UI125, 2560×1440/UI100; UI100→125→100;
beide Scrollflächen, Info-/Arbeitsrückkehr und genaue rechte Karten-ID;
langes Kategorienpopup, 48 Treffer über zwei Doppelseiten; Fokus/Innenabstände;
Von/Bis nebeneinander ohne L-Präfix, wechselseitig gesperrte Optionen;
schmale Maßfelder rechtsbündig unter den Dropdowns, dritte Ziffer blockiert, 99 übernommen;
Übernehmen / Zurücksetzen / Schließen identisch groß in genau einer Zeile;
am Inhalt bemessene kompakte Panelhöhe bei UI100 und UI125; sichtbarer Fehler
bei 0 mit letzter gültiger Auswahl; UND-Leerbestand und getrennte Savewarnung;
Reset ausschließlich im Filterfenster; spezifische Reset-/Recoverydialoge
erreichbar und ohne Bestätigung abgebrochen. Kopf-/Fußcontrols bleiben im Client,
KL zeigt am großen Client drei Spalten je Hälfte. Meldungen stehen über der
Sortier-/Filterzeile im festen, begrenzt scrollbar lesbaren Kopfbereich.

`pages.json`/`pages.log`: 2071 native Assertions, keine Fehler; unabhängiger
Ergebnisreader akzeptiert exakt die fünf gebundenen Checkpoints. Die zusätzliche
Positionsprüfung blendet lange Save- und Sortierfehler in allen drei Zielgrößen
ein und aus: sämtliche Karten-, Scrollflächen- und Controlpositionen bleiben
identisch. Reader-Gegenproben: drei vorhandene Python-Tests bestanden. Der
Remote-Pflichtlauf ist separat im PR an den Test-Merge gebunden.

## Originalzugriff und Ablauf

Die neun PNGs sind unverkleinerte, unbeschnittene Originalbytes. Größen und
SHA-256 aller Dateien stehen in `manifest.json`. GitHub-Vorschauen können kleiner
sein. Für R01 die Datei über **Raw/Download** oder `git show COMMIT:PFAD`
binär lesen und gegen das Manifest prüfen. Die Lieferung kontrolliert nach dem
Push alle neun heruntergeladenen Originale erneut nach Länge und SHA-256.

Zweck ausschließlich K-A-R01/M01 zu diesem Head. Befristeter Branch
`review/485-k-a-layout`; nach Abschluss der Sichtung entfernen, Bedarf spätestens
**14.11.2026** prüfen. Keine automatische dauerhafte Bildarchivierung oder
Standard-CI-Bildpflicht. Kein Produkt-Merge aus dieser Evidenzlieferung.
