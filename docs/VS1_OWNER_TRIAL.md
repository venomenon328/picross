# VS-1 · native Vergleichsprobe

Die Größenstrategie [VS-D01 ist bestätigt](VS1_DECISION.md); die reguläre
Produktintegration bleibt separat. Diese Anleitung gilt für die gezielte GF-M01-Probe
vor GF1-Merge. Der frühere persönliche VS-M01-Bericht bleibt unvollständig.
Ein negatives Komforturteil ist ein gültiges Ergebnis.

Windows-ZIP vollständig entpacken. `picross-vs1.exe` starten; die benachbarte
`picross-vs1.console.exe` ist der Konsolenstart. Keine Godot-Installation nötig.
Bei einem Hinweis auf unbekannten Herausgeber handelt es sich um den unsignierten
Studienexport. Beide Programme verwenden denselben getrennten Studienstand.

Die zehn neutral benannten Blätter stehen über das Buchsymbol links zur Auswahl.
Format bedeutet Spalten × Zeilen. Eigene Einträge werden lokal fortgesetzt.
Die aktive Lieferung VS-GF1 bietet ausschließlich G/V für denselben Arbeitsstand:

- G: ganzes Raster; freie Breite zeigt zusätzliche Zeilenhinweise ohne kleinere
  Zellen. Nur noch verborgene lange Hinweise einzeln mit MMB verschieben. Mindestens fünf
  zusammenhängende vollständige Zahlen bleiben sichtbar, bei kürzeren Folgen alle.
- V: Raster und alle Hinweise. Beide Modi begrenzen den Zoom auf Rastervollsicht
  einschließlich des vollständigen äußeren Rahmens.

R ist entfernt; alte R-Ergebnisse bleiben historische Vergleichsbelege mit eigener
Head-/Dateibindung. Alte R-Auswahl wird beim Start auf G normalisiert. Hand und
Rasterpanning entfallen; die Miniatur zeigt eigene Einträge und bewegt keinen Ausschnitt.

Links füllen, rechts X setzen oder den begonnenen Eintrag umwandeln/neutralisieren.
Gerade ziehen, zum Verkürzen zurückziehen; Escape verwirft die Vorschau.
MMB verschiebt in G ausschließlich die angefasste lange Zeile oder Spalte.
Farbe und Radierer befinden sich neben beziehungsweise unter dem Blatt. Undo/Redo,
Minus/Plus, „alles einpassen“ und Arbeitsgröße bleiben verfügbar. Einpassen erreicht
die aktuelle Vollsichtgrenze; bewusst kleinerer Zoom ist möglich. Kein Handwerkzeug,
Zähllineal oder zusätzliche Modifierbelegung.

Über das Menü lassen sich UI 100/125 %, Zellanimation und Hinweisabstreichung
ändern. Dort können ein leeres Blatt oder feste künstliche Vergleichseingaben
bewusst gewählt werden. Diese Eingaben sind keine Lösungsvorgabe. Zurücksetzen
betrifft nur das ausgewählte Studienblatt. P1-Spielstände bleiben separat.
Bei Speicher-/Backupfehlern zuerst den sichtbaren Recoveryweg verwenden.

Bitte dieselben kurzen Abschnitte vergleichbar erproben; vollständige Lösungen
aller zehn Rätsel sind dafür nicht nötig:

1. Umgebung festhalten: Windows-Version, Bildschirmauflösung, Windows-Skalierung,
   normale und maximierte Clientfläche, UI-Skalierung, ZIP-/Headbindung aus
   `vs1-report.json`. Eine 1080p-Bildschirmauflösung ist nicht automatisch ein
   1920 × 1080 großer Fensterinhalt. Fehlende Konfigurationen als ungeprüft belassen.
2. Mindestfall VS01/VS02 (30 × 30): G/V durchgehen. Einzelzellen an vier Ecken,
   eine gerade Linie, Umwandeln, Neutralisieren, Zurückziehen, Escape, Undo/Redo.
3. GF1-Hauptprobe VS08 (40 × 40) bei 1920×1080-Client/UI100 und UI125: in G
   müssen alle 13 Zeilenhinweise ohne Auslassungsmarker oder unnötigen MMB-Drag
   sichtbar sein. Gegenüber der PR-58-Lieferung bleiben Zellen und Schrift gleich.
   VS07 und VS08 leer und mit Vergleichsstand jeweils etwa
   drei Minuten denselben kleinen Abschnitt bearbeiten. Lange Hinweise sowie
   normale, abgeschwächte und durchgestrichene Ziffern beurteilen.
4. VS04 und VS10 mit langen Zeilen: schmal→breit→schmal, G→V→G und Neustart
   erproben. Zuvor angefasste Zeilen sollen ihre Leseposition nach erneutem
   Verengen behalten; nicht verschiebbare vollständige Zeilen brauchen keinen Drag.
   Breite Alternative VS09/VS10 (50 × 30): denselben Abschnitt in G/V probieren.
   VS03/VS04 (40 × 30) und VS05/VS06 (30 × 40) ergänzend vergleichen. Die beiden
   Hochkantfälle sind kontrollierte Transponate mit unnatürlicher Motivorientierung.
5. UI 125 %, Fenstergröße und angebotene Zoomstufen prüfen. Kleine und gescheiterte
   Fälle ausdrücklich ansehen. „Unter 16 px“, Kollision oder „PASST NICHT“ ist
   kein positiver Komfortnachweis. Das negative Ergebnis notieren; es gibt keinen R-Ausweg.
6. Einige eigene Einträge speichern, schließen, erneut starten. Ausgewähltes Blatt,
   Modus und Einträge müssen fortgesetzt werden. Normale P1-Blätter prüfen, falls
   zuvor welche vorhanden waren.

Für jede tatsächlich erprobte Kombination getrennt notieren: Lesbarkeit,
Fehleingaben, nötige Vergrößerung/Verschiebung und subjektiven Komfort.
`owner-protocol.json` ist absichtlich leer. Nur tatsächliche Beobachtungen
eintragen; technische Automatikdaten sind keine Eigentümerprobe.

VS-D01 wird nicht erneut entschieden. GF-M01 bewertet die konkrete neue
Hinweisaufteilung; technische Automatikdaten füllen das persönliche Protokoll
nicht aus. Keine reguläre Produktumstellung durch diese Probe.
