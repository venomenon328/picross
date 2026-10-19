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

Der getrennte vollständige Diff-/Vertragsreview erfolgt nach Abschluss der
Implementierung und wird hier mit seinem konkreten Stand und Befunden ergänzt.
Dieser Prüfschritt ist keine unabhängige AT-A-R01-Abnahme.

## Offene Gates

Technischer Abschluss AT-A-T01 und abschließendes Selbstreview laufen noch.
Danach bleiben unabhängiges qualifiziertes AT-A-R01, Merge, Deployment und
Issue-Abschluss ausdrücklich offen. AT-B und Freigaben realer neuer Bildbytes
bleiben ein eigener Auftrag.
