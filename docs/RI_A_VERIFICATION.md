# RI-A-T01: Registrierung, Betriebsgrenzen und Messung

Arbeitsnachweis zu [#478](https://github.com/venomenon328/picross/issues/478),
RI-A-V01/P01 vom 29.10.2026. Ausgangsbasis:
`f47a30b904a8d4eba79ca9d3f82576aebcceaa38`. Kein Merge, keine echten Rätseldaten,
keine RI-B-/RI-C-Umsetzung. Der unabhängige RI-A-R01 ist offen.

## Prüfaufbau und Quellen

Die neue feste Regression
[test_registration_budgets.py](../tests/puzzle_production/test_registration_budgets.py)
verwendet ausschließlich den vorhandenen synthetischen `direct-mono`-Eingang,
leere isolierte Kataloge und eine kontrollierte monotone Uhr. Keine Wartezeit
von 300/1800 Sekunden. Die vollständigen bisherigen Katalog-/Recoverytests
bleiben Pflicht; diese Ergänzung ersetzt sie nicht.

Der begrenzte manuelle
[Messtreiber](../tests/puzzle_production/ri_a_measurement.py) läuft unverändert
gegen beide Quellbäume. Er bindet Eingangsdateien und Quellmodule durch SHA-256,
misst drei Wiederholungen und protokolliert tatsächliche Aufrufe/Bytes.
Aufrufmuster: `python ri_a_measurement.py --repo <quellbaum> --inputs <feste-inputs>
--work <neuer-arbeitsordner> --output <bericht.json> --source <commit>`.
Einmaliges `--prepare` erzeugt ausschließlich synthetische Inputs. Es gibt
keinen neuen CI-Job und kein neues dauerhaftes Replaykorpus.

## Laufender Messabschluss

Die endgültige Tabelle folgt nach den identisch instrumentierten Messungen
auf Linux (natives Containerdateisystem), Windows/NTFS mit kurzem und mit
normal verschachteltem Pfad. Vorläufige Läufe werden nicht als endgültiger
Vorher/Nachher-Nachweis ausgegeben. Median und Spannweite, Setup, Export,
Plan, Writer/Guards/Staging, Recovery und Zähler werden getrennt gebunden.

Nicht gemessen werden reale Kataloge, langsame/blockierende Netzlaufwerke,
beliebige Fremdlast und komplexe Reparatur-/Paarproofkorpora. Der Betriebsbericht
zählt vollständige Kandidaten-/Proofaufrufe an der Adaptergrenze; innere Proofs
zusammengesetzter Prüfungen bleiben ausdrücklich eine Messlücke. Der T01-Treiber
zählt für seinen festen Direktimport außerdem die wirklichen Verifieraufrufe.
Read-/Hashbytes des Betriebsberichts decken `catalog_io` ab, nicht sämtliche
anderen Dateileser. Inklusive Phasendauern dürfen nicht addiert werden.

## Ergebnisgate

Der lokale RI-A-Zwischenstand bestand 14 neue Tests auf Windows (83,361 s)
und Linux (18,713 s). Diese Werte sind Zwischenstände, keine Bindung des noch
ausstehenden endgültigen PR-Heads. Die vollständige CI-Auswahl, `ci-required`,
finale Messwerte und der getrennte Selbstreview werden vor Arbeitsabschluss
ergänzt. Chromium ist nicht beauftragt und wird nicht gestartet.

Bis zum abgeschlossenen Mess-/CI-Nachweis und unabhängigem R01 bleibt die
Lieferung im Draft. Ein höheres Zeitlimit ist keine behauptete Beschleunigung.
