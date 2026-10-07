# ZS-1 · Prüfzuordnung und Liefergrenze

Stand: 07.10.2026 · Implementierung auf `feat/52-native-drawing-study`, Draft-Lieferung

Basis `ec99954268f1ad959d9ea779dbbd9e28edf7d8fa`; gebundene Spezifikation und
sechs Dokumentänderungen aus PR #54 bei `c82ae74f794936bca93d45f5f505ba283e971227`.
Sie wurden auf den aktuellen Main-basierten Studienbranch übernommen. #54 wird
dadurch weder gemergt noch geschlossen. Lieferhead, Test-Merge, sechs aktuelle
CI-Jobs, Downloadkennungen und ZIP-Hashes werden im Draft-PR zu #52 gebunden.

| Kriterium | Ausführbarer Nachweis |
| --- | --- |
| ZS1-A01 | Native Hauptszene `study/main.tscn`, Variantenknopf am identischen Sessionstand, F-01/F-02/F-03; lösungsunabhängig erzeugte eigene Muster mit vielen X. `zs1_capture.gd` vergleicht gegen ein echtes Git-Archiv der aktuellen Produktbasis. |
| ZS1-A02 | Normale/gesetzte/abgegrenzte Originalhinweise auf beiden Achsen, C1/alle Farben, echte lange Zeilen-/Spaltendrags und Tooltips; eigene beschriftete Ziffernprobe bis 100. Originalindizes, Slots und semantische Lesepositionen unverändert. |
| ZS1-A03 | Gezielte 1920×1080-, 1280×720/UI125-, 1600×900- und 2560×1440-Fälle; 12/24/36/72er-Zellen; F-01 bei 150 %. Geometrie-/Zellhashvergleich für alle Varianten, pixelidentische Studienbaseline gegen Main im Boardbereich. |
| ZS1-A04 | Native Zeitsequenz für ruhige Vorschau, 20 parallele Änderungen, zweite Geste vor Effektende, direkte Umwandlung und identischer Endzustand bei Aus. Separate echte GUI-Ereignistests für Rückzug/Abbruch, Schutz/No-op, jüngsten Zielzustand, Undo/Redo, Ausschalten, Fokus/Zoom/Resize/Seitenwechsel/Reset und sofortigen Abschluss. |
| ZS1-A05 | Unveränderter Session-/Gesten-/Savekern; vergifteter Normal-Sentinel bleibt bytegleich. Isolation vor Main._ready, eigene Speicherwurzel auch beim Direktstart; Originaldaten/Proofs unverändert. Bestehender kompletter Produktweg einschließlich 500 Aktionen, Neustart/Recovery und sämtliche sechs CI-Jobs bleiben aktiv. |
| ZS1-A06 | Eigener Windows-Export mit separater Hauptszene/Appidentität; eigenes schlankes ZIP und getrenntes Review-ZIP. Bericht bindet Source-Head, Dirty-Status, Checkout/Test-Merge, Basis, Run, Fonts/Engine und Datei-Hashes. |

Die reguläre `main.tscn` und ihr Appname bleiben erhalten. Ihre einzigen
Codeanschlüsse sind eine Board-Fabrik und überschreibbare Zeichenfunktionen mit
unveränderten Standardkörpern. Der normale Export schließt `study/*` aus.
Nur der temporäre Studienexport öffnet diesen Filter und setzt die andere
Hauptszene/Appidentität. Weder Modell-/Saveformat noch Originalinhalte ändern sich.

## Reproduktion

Der bestehende freigegebene Produktweg erzeugt zusätzlich die Studie:

```powershell
$zs1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $zs1Cache --output-dir artifacts/zs1-product
```

Voraussetzungen bleiben die isolierte Image-Umgebung, gepinnte Godot-Toolchain,
vollständige Git-Historie und unter Linux Xvfb/Mesa aus dem Projektprofil.
`tools/zs1_delivery.py` wird vom Produktharness ausgeführt; kein zweiter allgemeiner
Buildpfad. `zs1-tests` prüft die Ereignis- und Lebenszyklusverträge, die Renderphase
echte OpenGL-Bilder und Messwerte. Standard-Uploads ergänzen ausschließlich
`zs1-windows-study-<Head>` und `zs1-review-<Head>`; der große Vollnachweis bleibt opt-in.

Im Review-ZIP zeigt `index.html` statische native Vergleichsbilder und zeitgebundene
1:1-Bewegungsausschnitte. Der Index ist keine Browserimplementierung des Spiels.
Die eigentliche bedienbare Probe ist die EXE. PNGs bei 100 % prüfen; die verkleinerte
Übersicht ist keine Lesbarkeitsabnahme. Die synthetische Schriftprobe ist als solche
beschriftet und ersetzt keine unveränderten Rätseldaten.

## Bisherige lokale Befunde und Grenzen

Der erste lokale Windows/OpenGL-Durchlauf mit Godot 4.7.2 und RTX 3070 bestand
117 Studienprüfungen und die nativen Bewegungsassertionen. Nach Trennung der
Zellschicht lag deren gemessene F-03-Zeichenzeit im Entwicklungslauf ungefähr
bei 2,8–5,9 ms; die vollständige synthetische 100-Zellen-Eingabe einschließlich
des bestehenden synchronen Speicherwegs bei 81–120 ms. Diese Werte stammen aus
einem veränderten Entwicklungsbaum, sind keine finalen Head-/CI-Nachweise und
kein allgemeines Performanceversprechen. Ein vollständiges Neuzeichnen inklusive
Hinweisarbeit kann deutlich teurer sein; schnelle reale Eingaben sind ZS1-M01.

Vorschau-Ruhe wird über gleiche native Pixel vor/nach einer Wartezeit geprüft.
Die zweite Geste beginnt vor Ablauf der ersten 140 ms; jüngste Zielwerte haben
Vorrang. Ausgeschaltete Effekte ergeben denselben logischen und nativen Endzustand.
Die Messung des Animationstakts prüft ausdrücklich, dass keine zusätzlichen
Hinweissuchen ausgelöst werden. Technische synthetische Events sind keine
Eigentümermausprobe oder Bestätigung physischer Windows-DPI-Verhältnisse.

Vor Übergabe: vollständigen Diff, Originalhashes, separate Selbstprüfung,
aktuellen CI-Checkout und die heruntergeladenen Artefakte prüfen. Tatsächliche
Ergebnisse und eventuelle Nacharbeit stehen commitgebunden im PR. Ein Selbstreview
ist keine unabhängige technische/visuelle Zweitprüfung.

**Vor Merge offen:** unabhängiges technisches/visuelles Review, reale
[ZS1-M01-Eigentümerprobe und Auswahl](ZS1_OWNER_TRIAL.md), passende ausdrückliche
Mergefreigabe. Die [Entscheidungsvorlage](ZS1_DECISION.md) enthält Kandidaten,
keine gewählte Produktfassung. #52 bleibt offen; #53 und Release sind nicht geliefert.
