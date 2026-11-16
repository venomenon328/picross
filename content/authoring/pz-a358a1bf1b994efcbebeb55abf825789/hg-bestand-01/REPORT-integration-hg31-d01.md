# HG-BESTAND-01 · gewählter Hintergrund K4/r01

Die Eigentümererklärung „K4, T5 und Q4 sind meine Favoriten. Bitte integriere diese.“ wählt für `pz-a358a1bf1b994efcbebeb55abf825789` den Kandidaten **K4/r01** aus Manifest bg05. Ursprünglicher Angebotscommit: `b356bbd4c1d1ac6f71358bbb7a46b3ac2bcda23b`.

## Ergebnis und Bindung

- K01/K02: feste Ziele und ursprünglicher neuer Dreiersatz bleiben unverändert gesichert.
- K03: tatsächliche Auswahl in `decisions/hg31-d01.json`, Wortlaut und Dateibindung in `evidence/owner-selection-hg31-d01.txt`. Keine Übertragung alter Freigaben.
- K04: ausschließlich das gewählte Original mit `picross-background-png2304x768-v1` auf 2304×768 RGBA8 abgeleitet. Erstverify und erneutes Verify der aus dem Sicherungsordner transportierten Bytes bestanden. Isolierte Sichtung auf Weiß/Graublau bestätigt Q-HG01–04 an der Ableitung.
- K05: `picross-editor-request-v2` und aktueller `editor_cli plan/apply`; alle ungewählten Bereiche null. Writer übernimmt exakt die geprüften Bytes; Bildsource, Inhaltsregistry und Runtime binden dieselbe Datei. Bild- und Sourcerevision jeweils 1 → 2.
- K06: Integration auf dem Inhaltsbranch vorbereitet; Mainmerge, unabhängiges Review und §9-Abschluss stehen aus. Die bisherige Vorgabe „kein Merge“ bleibt maßgeblich. Issue #671 wird nicht geschlossen und seine Serienkästchen bleiben offen.

Liveasset: `game/art/backgrounds/pz-a358a1bf1b994efcbebeb55abf825789.png`, SHA-256 `608958f5211620dcb5fec7b424057023b968774d0ca699f46680819b02921504`, 1283677 Bytes.

## Prüfung und Selbstreview

HP-W2-Befund, Originalrequest, Describe, Entscheidung und fertiges PNG liegen mit unveränderten relativen Bindungen unter `derivations/hg31-d01/`, `requests/`, `decisions/` und `evidence/`. Die tatsächlichen Editorpläne liegen außerhalb des Inhaltscheckouts; kompakte Before/After-, Planhash-, Schreibmengen- und Readbackbelege stehen in `evidence/editor-import-hg31-d01.json`.

Der tatsächliche Produktdiff enthält ausschließlich drei Hintergrundsources, drei PNGs und die beiden betroffenen gemeinsamen Indizes. Definitions-/Rasterbytes, Revealbytes/-sources, Hinweise/Palette, Modus, IDs/Keys/Slots, Runtime-/Rätselrevisionen, Namen/Kategorien, Bewertungen und Added-Daten bleiben unverändert. Alle unbeteiligten Runtimezeilen sind identisch. Keine Änderungen an Engine, Code, Loader, Profilkörpern oder Deckkraft. Frühere Angebote und Nachweise bleiben unverändert; 256 vorbestehende lokale HG-Dateien erneut hashgenau bestätigt.

Dokumentprüfung und die 21 Tests des kleinen CI-Kerns bestanden. `.ci/package.json`: Paket HG-BESTAND-01, modules=[], evidence.mode=none. Reine Inhalte ohne Playerbau; keine Solver-/Proof-/Ratingwiederholung. Quellengebundene PR-CI wird am veröffentlichten Integrationshead geprüft.

Selbstreview: Auswahl/Original/Sollprofil stimmen überein; vollständige Komposition, Strichqualität und Alpha erhalten; Writerplan auf exakt vier Pfade je ID geprüft; bytegleicher Import und unveränderte geschützte Werte bestätigt. Keine offenen Implementierungsbefunde. Dieses Selbstreview ersetzt kein unabhängiges Vor-Merge-Review. Arbeitsdaten bleiben für dieses Review erhalten; kein Retirement vor bestätigter Mainintegration.
