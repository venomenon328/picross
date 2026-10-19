# AT-A-T01 · Bildrevisionen und technische Nachweise

Stand: 19.10.2026 · Umsetzungsvorbereitung V3 · technische Abschlussprüfung läuft.
[Auftrag #256](https://github.com/venomenon328/picross/issues/256),
[Fachvertrag](REVEAL_TRANSPARENCY.md).

## Bindung und Umfang

Arbeitsbranch `feat/256-bildrevisionen`, geprüfte integrierte P01-Basis
`9cc58651518e3a28e97f46932d69554210b0abcb` / PR #257. Der separate Worktree
erhält den ursprünglichen Spezifikationscheckout samt dessen ungetrackter Arbeit.
Die Lieferung betrifft ausschließlich AT-A. Kein reales Katalogbild und keine
realen Bewertungs-, Hinzugefügt- oder Bildmetadaten werden übernommen.
Inhalts-v2, Runtime-v4 und Save-Schema 1 bleiben erhalten.

## Implementierung

`catalog_reveal` erzeugt externe, vollständig gebundene Pläne und übernimmt nur
explizit ausgewählte freigegebene Bildrevisionen. `reveal_source` trennt die
historische Exportbindung, den physischen Receipt-/Manifesthash und die wirksamen
Bild-/Noticebytes. Register, Update, Sync, SD-/Added-Adoption, Cleanup und Recovery
nutzen dieselbe Auflösung. Bildrevisionen verändern keine Definitionen oder Saves.

`catalog_transaction` und `catalog_publication` führen die neuen Journalgenerationen
mit vollständigen Quellenmengen, binären Alt-/Neuseiten, dauerhafter Lockpublikation,
Phasenguards und wiederholbarem Rollback. Die bisherigen Journalgenerationen
behalten ihre geschlossenen Schemas; ungebundene AT-Quellen sperren Alt-Recovery.
Paketneuanlagen behalten nur vollständig geschriebene Tempdateien: Windows nutzt
Delete-on-close bis zum geprüften vollständigen Inhalt, Linux `O_TMPFILE` mit
anschließender exklusiver Namensbindung. Bild- und Texttemps prüfen exakte eigene
Präfixe gegen das Journal. Unterstützte Veröffentlichung und Verzeichnis-Flush
werden am tatsächlichen Dateisystem vor aktiven Änderungen geprüft.

Die synthetischen Darstellungsfälle erzeugen zwei feste RGBA-Bildstände mit
weißem Motivteil, Innenaussparung und Alpha 80/255 am Rand. Die importierten
Bildpunkte und unveränderten Original-Framebufferausschnitte werden unabhängig
gegen die tatsächlichen Papierpixel geprüft. Windows und Chromium verwenden
je zwei echte Exporte mit gleichen Definitionen und geänderten Bildbytes.

## Nachweisweg und aktueller Prüfstand

Windows 11 `10.0.26200`, Python 3.13, isoliertes Pillow 12.3.0 und Playwright
1.58.0; echter Chromium-Start 145.0.7632.6. Git/GitHub-Zugriff und Pushbefugnis
wurden am tatsächlichen Repository geprüft. Verbindliche Engine ist
`4.7.2.stable.official.ed1daf0bf`, mit den unveränderten offiziellen Editor- und
Templatehashes aus [Preflight](P1_PREFLIGHT.md).

Der echte Windows-Preflight vor Implementierung bestand Import, positive und
bewusst negative Prüfungen, kontrollierten Start, Export und Start der exportierten
EXE. Originalarchiv: `artifacts/at-a-start/preflight/p1-preflight-windows-x86_64.zip`,
SHA-256 `922868cfae5fd230dfd0143f3d8ae65a31ccbbee50aa989f741eb63fd05a0351`.
Der grüne Docs-Lauf der P01-Basis ist kein AT-A-Produktnachweis.

### Dauerhaft gesicherte Originale

[Originalverzeichnis und Inventare](evidence/at-a/README.md) enthalten unveränderte
Windows- und Linuxausgaben. Die dortigen Nachweise binden Commit
`742f1837cf3a5600e4160c54744b87dfa88dcba1` an Basis
`9cc58651518e3a28e97f46932d69554210b0abcb`. Der Linuxlauf
[39261657542, Attempt 1](https://github.com/venomenon328/picross/actions/runs/39261657542)
prüfte den Integrationscommit `b28f5440f31c2ad79aef4c6e2104cf296b7b3d67`.
Spätere Korrekturen erhalten eine eigene finale CI-Bindung im Draft-PR; diese
Originale werden nicht als Ausgaben eines späteren Heads bezeichnet.

| Nachweis | Tatsächliche Ausführung und Ergebnis |
| --- | --- |
| AT-S01–S06 | Vollständige Linux-Produktionssuite: 294 Tests, 1220.602 s, `OK`. Danach Referenzläufe mit frischer Verifikation und ZA-1-Replay bestanden. Originale unter `evidence/at-a/production/`. Enthalten sind Windows-/Linux-kompatible Transaktionen, alte Journalgenerationen, Mehrfachadoption, harte Prozessabbrüche und erneuter Kill während Recovery, 32-MiB-Bildseiten sowie 24-/128-MiB-Dispatch. |
| AT-N01 | Alle sieben nativen Gruppen bestanden. Die festen AT-Fälle erzeugten zwölf Katalog-/Papier- und 18 Abschluss-/Papieroriginale in der vorgeschriebenen Dreiermatrix. Nach Download unabhängig erneut geprüft: 30 Katalog- und 45 Abschluss-/Überblend-/Wiederöffnungsmessungen bestanden. Kleine Karte, Hover und Überblendung wurden zusätzlich visuell geprüft. |
| AT-N02 | Sauberer Windowscheckout, zwei tatsächliche EXE/PCK-Exporte, drei tatsächliche Prozessstarts im gleichen isolierten Profil; eigener begonnener und gelöster Save wurden über echte Zeigerereignisse erzeugt. Zell-/History-/Statuswerte, Definitionen, Registry und gespeicherte Slotdateien bleiben über Bildwechsel und Neustart gleich. Sechs unveränderte Original-PNGs, Export-/Asset-/Savehashes und Prozessinstanzen stehen in `windows/windows-binding.json`. |
| AT-C01 | Vollständige Werkzeug-/Dokumentprüfung in CI bestanden, einschließlich positiver und negativer Scopefälle und Ablehnung manipulierter Originalpixel-/Exportbelege. Der Gesamtdiff wählt sieben native und fünf Chromium-Gruppen sowie Produktion, Preflight und isolierte Lieferung. Kein Kurzpfad für Werkzeugcode. |

Die Windowsprobe lief mit dem tatsächlichen OpenGL-3.3-Treiber der NVIDIA
GeForce RTX 3070; der Startzeitpunkt ergänzt den PID zur eindeutigen Bindung
aufeinanderfolgender Prozesse. Die Linux-Produktprüfung verwendet ihre eigene
gebundene Umgebung. Diese zwei Wege werden nicht als identische Plattformmessung
ausgegeben. Das Windows-Bild-/Saveexperiment wird mit
`python tools/at_windows_probe.py --cache-dir <offizieller-cache> --output-dir <neuer-pfad>`
in einem sauberen Checkout reproduziert.

Die Entwicklungsläufe sind ausdrücklich keine Abschlussbindung an den späteren
PR-Head. Bereits geprüft: Quellenlebenszyklus vor/nach Cleanup, Raster-Rebind,
echtes unverändertes No-op samt Nanosekunden-mtimes, SD-/Added-/Sync-Erhalt,
Mehrfachadoption mit einzelnen Schreib-/Recoverygrenzen, echte Prozessabbrüche,
32-MiB-Bildseiten und 24-/128-MiB-Dispatch, Windows-Hardlinks/Junctions sowie
native Alpha-Darstellung und Windows-Export-/Savewechsel. Ein gestarteter
Gesamtlauf wurde nach konkreten Registrierungsregressionen für die Nacharbeit
abgebrochen; die gezielten Regressionen bestehen nach Korrektur.

Der abschließende Nachweis bindet den finalen Head, die aktuelle Basis und den
getesteten Integrationscommit an den vollständigen CI-Diffplan, alle ausgewählten
Jobs und deren Originalartefakte. Ausschließlich die aktive Chromium-Workflowkette
wird verwendet. Die Linux-Lieferprüfung bleibt eine isolierte SSH-Referenz;
kein Produktivserver und kein Deployment werden angesprochen.

## Getrenntes Selbstreview

Der [getrennte Selbstreview](evidence/at-a/self-review.md) benennt Prüfumfang,
konkrete Befunde B-AT-SR01–03 und deren erfolgreiche Gegenproben. Er ergänzt
frühe Registry-/Manifestvalidierung, kontrollierten Speicher-/Typabbruch und
bytegenaue Git-Aufbewahrung der Originale. Die zusätzliche positive Versionsprobe
bestätigt Bildadoption, Recovery und No-op ohne Upgrade gültiger Runtime-v2/v3.
Dieser Prüfschritt ist keine unabhängige AT-A-R01-Abnahme.

## Offene Gates

Technischer Abschluss AT-A-T01 und abschließendes Selbstreview laufen noch.
Danach bleiben unabhängiges qualifiziertes AT-A-R01, Merge, Deployment und
Issue-Abschluss ausdrücklich offen. AT-B und Freigaben realer neuer Bildbytes
bleiben ein eigener Auftrag.
