# B-B-T01 · Reguläre Buchintegration

Paket: [#498 / B-B-V01](https://github.com/venomenon328/picross/issues/498),
übergeordnet [#493](https://github.com/venomenon328/picross/issues/493).
Basis: `2a0d9e4ae21802637dc26ff8fdf904bf27772972`, Branch
`feat/493-book-integration`. [Aktueller Vertrag](BOOK_INTEGRATION.md).

Dieser Bericht wird während der Implementierung fortgeschrieben. Die endgültige
Lieferbindung von Head, Basis, Test-Merge/Checkout, CI-Run/Attempt, Windows-/Web-
Exporthashes, zugänglichen Originalen und getrenntem Selbstreview steht im
zugehörigen Draft-PR. Ein lokaler Zwischenstand ist keine aktuelle Pflicht-CI.

## Entwicklungsprüfungen

- Gemeinsamer nativer Buchkern: 1125 Assertions erfolgreich; ursprüngliche
  Geometrie-, Eingabe-, Navigations- und Unterbrechungsfälle. Pixelvergleich und
  vollständige abschließende Lieferbindung stehen noch aus.
- Erster regulärer Lifecycle-Durchstich mit echtem SaveStore: erfolgreich,
  einschließlich fehlgeschlagenem Flush/Quit, sichtbarem Retry, ursprünglicher
  Sessionbindung, leeren/fehlerhaften Katalogen und Freigabe der Captures.
- Headless-Kernprüfung nach Anpassung der alten Navigationsannahmen:
  17299 Assertions, null Fehler. Weitere Änderungen werden gezielt nachgeprüft.
- Unabhängiger Berichtsguard: fünf Werkzeugtests erfolgreich, einschließlich
  fehlender/fehlgeschlagener Lifecycle-Assertions und falscher Quellenbindung.

## Noch zu bindende Lieferung

Aktueller Pflicht-CI-Lauf, ausdrücklich beauftragtes Chromium `short`, neuer
exportierter Windowslauf mit OS-Eingabe, Originalsichtung, Kosten/Hashbindungen
und abschließendes Selbstreview sind noch offen. Lokale Desktopprüfungen werden
nach der vom Eigentümer verlangten vorherigen Freigabe ausgeführt.

B-B-R01 ist eine getrennte unabhängige technische und visuelle Prüfung;
B-B-M01 eine getrennte persönliche Funktions-/Komfortabnahme. Beide werden
weder durch diese Implementierung noch durch Selbstreview ersetzt. Kein Merge,
Deployment, automatisches Schließen von #498/#493 oder behaupteter Browserpass.
