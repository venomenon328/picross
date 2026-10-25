# SD2-A-T01: Technische Lieferung und Prüfzuordnung

Stand: 25.10.2026 · [#403](https://github.com/venomenon328/picross/issues/403),
[Draft-PR #408](https://github.com/venomenon328/picross/pull/408).
Basis `7709a50d0f34482e5be54c17cc5f0a6167ee8821`, Branch `feat/403-sd2-analyzer`.
Die aktuellen finalen Head-/Basis-/Test-Merge-/Runbindungen stehen im PR.

## Vertragsauftakt und Umfang

[SD2_ANALYZER](SD2_ANALYZER.md) wurde in `ad5457e` vor Regel-/Formatcode
versioniert; `bfd27a0` ergänzt vor dem betroffenen Messcode die dynamische
Hinweisstruktur, `07cd445` den getrennten Deadlinebeginn. Neue E0–E3-Regeln, unabhängiger Prüfer, drei Rohprofile und
eigene `sd2_cli analyze/check` sind vollständig vom aktiven 0.3-Weg getrennt.
Keine Endnote, Bestandsanalyse, Aktivierung, Runtime-/Save- oder Inhaltsänderung.

## Akzeptanz und feste synthetische Nachweise

[test_sd2_analysis.py](../tests/puzzle_production/test_sd2_analysis.py) verwendet
kleine vollständige Mono-/Farborakel und feste technische Raster. Die wiederverwendeten
FLOW/GENERAL_LINE/MONO/COLOR-Muster stammen aus den ausdrücklich synthetischen
SD-A-/Paarlinientests, keine Katalogkopien oder Kalibrierungsreferenzen.

| Akzeptanz | Tatsächlich geprüfte Aussage |
| --- | --- |
| A01 | Leerfeldüberlappung und eindeutige Verlängerung in E1; zwei getrennte Anker erfordern gemeinsame E2-Zuordnung; allgemeine Lückenbedingung bleibt E3. |
| A02 | Jede Regel gegen vollständige kleine Belegungsorakel, auch unerfüllbare Domains; längere feste Mono-/Farbfälle. Prüfer funktioniert bei gesperrtem Erzeuger/Automaten. Verfälschte Stärke, unvollständiges Angebot, übersprungener schwacher Fortschritt, Enddomains und Widerspruch werden abgewiesen. |
| A03 | Drei rekonstruierte Profile, handgerechnete Rechteck-/Strich-/Nullfälle, dynamische kurze Hinweise/Farben, frühe/späte/wiederkehrende Phasen. Abbruchpräfixe und Prüfabbrüche ohne Note; CLI in separaten Prozessen, Runtimeziel erst nach Deduktion. |
| A04 | Gleicher Eingang reproduziert Trace und Resultat; beide Spiegelungen, Transposition und Farb-ID-Bijektion erhalten alle skalaren Profile. Partielle Farbänderungen, wiederholte Ereignisse, eindeutige Positionen und gelöste Linien getrennt. |
| A05 | Bestehende 17 SD-A- und 16 Rating-/Referenztests erfolgreich; alter CLI-Weg mit/ohne Methode bleibt enthalten. 13 Quelldateien, Methodenhash `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` unverändert. Alter Checker weist SD2-Bundle zurück. |

R4 wird nur aus ausdrücklich übergebenen unveränderten Proofs neu unabhängig
geprüft. Stalled-Linienbaseline plus vollständiger Paarproof belegt Notwendigkeit;
abgebrochene Baseline bleibt unbewiesen. Seine Schritte sind keine SD2-Wellen.

## Lokale Prüfung und Pflicht-CI

Python 3.13.14, Windows. 20 gezielte SD2-Fachtests sowie bestehende Analyse-/Ratingtests
erfolgreich. 217 Werkzeugtests erfolgreich mit drei ausgewiesenen Plattformskips:
Symlinkanlage auf dieser Windows-Umgebung und zwei Linux-Shell-Ausführungstests.
Der Linux-CI-Pfad bleibt dafür Pflicht. Keine Testabschwächung oder neue Abhängigkeit.

Der erste ungefilterte lokale Dokumentlauf las bestehende ignorierte Altartefakte
unter `artifacts/` mit und schlug dadurch fehl. Die anschließende Prüfung einer
sauberen `git archive HEAD`-Kopie des Vertragscommits bestand. Fremde/unversionierte
Dateien wurden nicht verändert. Abschließende Dokumentprüfung und alle durch den
vollständigen Diff ausgewählten Jobs werden im PR am konkreten Head belegt;
ältere Vertrags-CI ist kein Produktnachweis der Implementierung.

Erwartete Auswahl aus neuen Modul-/Testpfaden: docs, production, product, web,
delivery und ci-required; maßgeblich ist der tatsächliche vollständige Diff.
Keine Änderung an Selektor, Workflow oder bestehenden Prüfumfängen.

## Getrennter Selbstreview und offene Abnahme

Der getrennte vollständige Selbstreview wird am Lieferhead im PR dokumentiert:
Regelgrenzen, Prüferunabhängigkeit, Metrik-/Null-/Budgetsemantik, Dateibindungen,
0.3-Freeze, vollständiger Diff und ausgewählte CI. Er ist keine unabhängige
Zweitprüfung. Qualifiziertes separates **SD2-A-R01** am finalen Head und passende
ausdrückliche Mergefreigabe bleiben vor Merge erforderlich. Kein neues
verpflichtendes Eigentümer-Probespiel. B/C/D und #402 bleiben offen.
