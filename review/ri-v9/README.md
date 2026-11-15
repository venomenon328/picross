# RI-V9 · temporäre Revieworiginale

Zweck: RI-V9-A01/K01–K07, Draft-PR #654, Issue #652.
Produkt-Head: 4b7286461d3b074eaf6f044d45d69237d0b8b42b.
Mainbasis: 628f88101d5bdc01cd44299eaaa2065e26bbcc03.
Unveränderte Eingangsoriginale: PR #603, e3b177673011c5477dd605c24420fef589e8f878.
Keine ZIPs, PNGs oder Inhaltsintegration in diesem Reviewdelta.

Reviewref: review/652-ri-v9-until-20261122.
Am Ende von RI-V9-A01 entfernen, spätestens **2026-11-22T00:00:00Z**.
Keine dauerhafte Archivierung, kein Merge dieses Refs. Der kompakte Befund
bleibt im Produkt-PR. Der Implementierer verantwortet die Entfernung;
ein nachfolgender Review-/Abschlussauftrag muss diesen Restpfad mitführen.

Die *-result.json und *-operation.json sind unveränderte native Ausgaben.
.gitattributes verhindert Zeilenendekonvertierung; SHA-256/Größen stehen
in inventory.json. Beobachter im run-through.py zählen nur Weiterleitungen
an die unveränderten Funktionen. Keine Validierung wird ersetzt oder umgangen.
Der Runner ist der tatsächlich ausgeführte lokale Nachweis, kein allgemeines
Tool und keine dauerhafte CI-Fixture. Absolute lokale Pfade sind Laufkontext.

summary.json und registration-diff.json binden Ausgang, exaktes Journaldelta,
bestehende Bytes und Completion. Die isolierte Registrierung ba3b353070063f9c7f32d857e2a5cd037f290bad
ist ein lokaler Testcommit, kein Main-/Produktionscommit. Completionquellen und
gebundenes Exportmanifest sind als kleine Originalmetadaten beigefügt.

Lokale Windows-Regression: 14 bestehende Publikationsfälle erfolgreich.
Der erste Gesamtlauf enthält einen Fehler der neuen Testassertion auf wiederhergestellte
Dateizeiten. Nach Korrektur auf Byteerhalt sind sämtliche sechs aktuellen
v9-Fälle erfolgreich (current-generation-final.log). Der echte synthetische
Completion-/Resume-/§9-Test und 21 CI-Kerntests sind ebenfalls erfolgreich.
Maßgeblicher gesamter Linuxlauf: Package CI 43659533003, am Produkt-Head.

Realprobe: Export 10,691 s; Plan 48,200 s; Register 286,655 s;
Completion einschließlich anschließender Bindungsprüfung 8,043 s.
56 unveränderte Altzeilen, davon weiterhin drei unkompaktierte Obstpakete.
23 Neuanlagen; nur content/registry.json und game/data/registry.json als
bestehende Dateien ersetzt. Danach ausschließlich Record/Projektion/current-view
für r07 abgeschlossen. Original-ZIP und Endabnahme unverändert.
Kein Retirement realer Inhalte und keine Änderung an PR #603.

Die Phasenzeiten sind inklusiv, daher nicht beliebig addierbar.
Lese-/Hashzähler erfassen catalog_io, keine vollständige Betriebssystem-I/O.
Der ältere 584,065-s-Fehllauf enthält Rollback; keine direkte Geschwindigkeitsgarantie.
