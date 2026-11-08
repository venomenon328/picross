# P-B2: befristete Textoriginale für P-B2-R01

Produkt-Head: `7d3b60dca307bad3d07c594f9676a3995268d2f8`.
Basis: `866ee990f2a04c197ada3a128311e5ed6323f259`.
Empfänger: unabhängiger Code-/Vertragsreviewer von PR #552.
Zweck: einmalige synthetische Abnahme P-B2-01–06/T01 nachvollziehen.
Endpunkt: Abschluss P-B2-R01; Bedarf spätestens **15.11.2026** erneut prüfen,
danach eigenen temporären Ref nach passendem Rückbauauftrag entfernen.
Dieser Belegbranch hat keinen Merge-PR und gehört nicht nach main.

- `acceptance.py`: exakt das einmalig ausgeführte Skript; kein Dauer-CI-Test.
- `acceptance-result.json`: vollständiger erfolgreicher Lauf am obigen sauberen
  Head; Python 3.13.12/Windows, isoliertes Pillow 12.3.0, 111,734 s.
- `baseline-windows-core.log`: separat auf unverändertem Main-Checkout
  reproduzierter bestehender Windows-Kernfehler. Produktcode/CI-Kern wurde dafür
  nicht geändert. Der Linux-Package-CI-Pass wird im Produkt-PR separat gebunden.

Der Lauf prüft F01–F08 aus dem ursprünglichen synthetischen P-A-Belegcommit
`1d5b7e90db4c8843d7737f83411f896ceeee6231`: 27 q-Koordinaten, 47 Paarwerte,
56 Stale-Mutationen; alle sechs manuellen Autorisierungswege unter 0.6.0/v5,
einschließlich negativer Palettenausnahme neben v4; vier Mono-/Farb-Import-/
Reparatur-Paarprofile; gefälschte Plan-/Registerinputs, lesender Plan,
Crash-Recovery, tatsächliche Registrierung, No-op und Rasterersatz.
Nur feste künstliche Testinputs; keine Katalog-/Savekopie. Alle Erklärungen sind
`TEST ONLY`, keine menschliche Produktionsabnahme oder neue Bildsichtung.
Die schmale visuelle Referenzzuordnung bleibt die bestehende P-A-Zuordnung:
F05 historisch angenommen/weiter metrisch negativ, F06 unzureichend,
F08 konkrete positive/Warnpaare. Keine behauptete vollständige Originalbildsicht.

Für eine gezielte Wiederholung einen sauberen separaten Produktcheckout am
obigen Produkt-Head und eine isolierte Python-/Pillow-12.3.0-Umgebung verwenden.
Das Skript zuerst in einen **neuen externen temporären Ordner kopieren**, damit
sein Ergebnis neben dieser Arbeitskopie und nicht über den Originalbeleg
geschrieben wird. `PICROSS_SOURCE_ROOT` auf den Produktcheckout setzen;
`TEMP`/`TMP` (unter POSIX `TMPDIR`) auf eigene Arbeitsdaten setzen. Dann mit dem
isolierten Python die Arbeitskopie ausführen. Optional nur `references`,
`manual`, `paired` oder `registration` als Argumente angeben. Das Skript liest
historische Referenzen per `git show`; fehlt ihr Git-Objekt, zuvor ausdrücklich
`git fetch origin 1d5b7e90db4c8843d7737f83411f896ceeee6231` ausführen.
Es verändert keine Produktquellen oder echten Inhalte; temporäre synthetische
Pakete/Checkouts verwalten Kontextmanager. Die Wiederholung ist keine neue
allgemeine Vor-Merge-Pflicht und ersetzt keinen unabhängigen Code-/Vertragsreview.
