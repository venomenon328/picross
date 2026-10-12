# KAT-1-Prüfzuordnung

Vertrag: [Kategorien](CATEGORIES.md), [Issue #78](https://github.com/venomenon328/picross/issues/78).
Die aktuelle Ausführung und ihre Commit-/Basis-/Test-Merge-Bindung stehen im
zugehörigen Draft-PR; diese Datei beschreibt reproduzierbare Prüfwege und Inputs.
Getrenntes Selbstreview und unabhängiges Review bleiben unterschiedliche Nachweise.
Unabhängiges Review ist vor Merge erforderlich; kein zusätzliches persönliches
Komplett-Probespielen für die Kategorienmetadaten. #79 bleibt außerhalb des Pakets.

## Akzeptanzzuordnung

| Kriterium | Ausführbarer Nachweis |
| --- | --- |
| A01 | `tools/test_categories.py`: initiale 20 Kategorien, sechs Zuordnungen, drei unveränderte Reservierungen; vollständiger Diff gegen die Basis für Definitionen, Assets, Proofs, Slots und Freigaben. |
| A02 | `tests/puzzle_production/test_categories_adapter.py`: zusätzliche Kategorie, Mono-/Farbrätsel in verschiedenen Kategorien, Export/Plan/Übernahme/No-op und identische Projektion ohne Code-Falllisten. |
| A03 | Kategorien-Schema-/Grenztests; manipulierte Kategorie, Referenz und Snapshot, fehlende/mehrfache CLI-Eingaben, unbekannte/entfernte IDs, veraltete Projektion, belegte ID mit anderer Kategorie; vollständige Checkout-Bytes bleiben beim Ablehnen gleich. Umbenennen bei gleicher ID bleibt zulässig. |
| A04 | Plan ohne Mutation; Fehler vor und nach Indexschreiben; Abbruch nach Datei, Index und Runtime; Recovery, veränderte Kategorienquelle während Planung/Staging/Übernahme, fremde Änderungen und altes Journal. Direkte Registryänderung gegen gebundene Exportkategorie blockiert. |
| A05 | Eingefrorener ZA-1-v1-Export wird nach altem Vertrag frisch geprüft; neuer kategorisierter Export aus denselben Inputs/Freigaben erhält die Originalbytes. Bestehende ZA-1-Tests prüfen weiterhin fehlende Endfreigabe, Pakethashes und unerlaubte reale Testregistrierung. |
| A06 | `game/tests/kat1_cases.gd` im regulären Godot-Testlauf: neue Runtimevalidierung, Datenwachstum, Fehlbezüge und echte Schema-1-Saves vom Stand vor KAT-1; Teilstand mit Undo/Redo und abgeschlossener Stand mit Reveal. Bestehende Auswahl-/Save-/Reset-/Recoverytests bleiben aktiv. |
| A07 | `game/tests/content_pack_probe.gd` gegen das tatsächlich exportierte Windows-PCK: Kategorien und Zuordnungen vorhanden, alle sichtbaren Definitionen gültig, historische Reservierungen und technische Daten ausgeschlossen. Product-Harness kontrolliert zusätzlich Exportressourcen und startet die Windows-EXE unter Windows. |

## Gebundene Altinputs

[provenance.json](../game/tests/fixtures/kat1/provenance.json) bindet ausschließlich
synthetische Testdaten, keine Nutzerspielstände und keine Eigentümerfreigaben.

- `f01.json`: echter alter Save nach zwei Gesten und Undo; eine Aktion aktiv,
  eine per Redo wiederherstellbar, unvollständig.
- `f02.json`: echter alter, über die Session-Gesten vollständig gelöster Save.
- Beide wurden mit [kat1_save_seed.gd](../game/tests/kat1_save_seed.gd) in einer
  temporären Kopie von `game/` aus
  `0da2bb67f15c3fad90ed276518b3d31f225d9c41` erzeugt. Der Seed liegt nur als
  Testinstrument vor, verlangt `KAT1_SEED_OUTPUT` und verwendet keine echten Saves.
  Offizieller gepinnter Windows-Editor 4.7.2; Archiv- und Seedhash stehen im Manifest.
  Der Lauf meldete `KAT1_LEGACY_SAVES_OK`. Die neuen Tests prüfen Schema,
  semantische Gleichheit nach JSON-Roundtrip, Abschluss/Reveal, Redo und unveränderte
  Savebytes auch bei reiner Metadatenänderung. Der Roundtrip berücksichtigt, dass
  Godot JSON-Zahlen als Float lädt und die Session Zellen als Integer führt.
- [za1-v1-export.zip](../tests/puzzle_production/fixtures/za1-v1-export.zip) wurde
  vor der Adapteränderung vom gleichen Basiscommit mit dem alten Exporter aus
  der vorhandenen künstlichen `direct-mono`-Fixture erzeugt. Die separat erzeugte
  Freigabe ist ausdrücklich `TEST ONLY`. Der unveränderte alte Bericht enthält
  seine ursprüngliche Werkzeugidentität. SHA-256 und Save-/Seedhashes werden im
  schnellen Test geprüft; der Fachtest prüft den kompletten Altvertrag erneut.

## Prüfweg und Grenzen

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python -m tools.puzzle_production.target_adapter check-registry --checkout .
python tools/p1_product.py --cache-dir <isolierter-archivcache> --output-dir artifacts/kat1-product
```

Fach- und Product-Prüfungen verwenden die eigene Image-venv mit Pillow 12.3.0;
Godot-Archive und temporäre Profile folgen [P1_PREFLIGHT](P1_PREFLIGHT.md).
Der Product-Harness aktiviert lokal Integration, Piloten, Visual und PERF-B.
Er erzeugt keine historischen Vollgalerien. Die [CI-Policy](CI_POLICY.md)
bestimmt die Jobs anhand des vollständigen Diffs, einschließlich aller neuen
Daten-/Testpfade. Head, Basis, getesteter Integrationscommit, tatsächliche
Jobergebnisse und Artefaktbindung sind vor Übergabe im PR zu dokumentieren.
Technische Daten bleiben unter 30 MB, gemeinsam mit Spielerpaket unter 75 MB.

Startbasis und Parallelstand: sechs sichtbare Rätsel auf `0da2bb67…`; PR #77
war offen und nicht integriert. Die dortigen Freigaben, Registrierungsbytes und
Integrationsbelege werden weder kopiert noch ersetzt. Bei späterem Merge beider
Pakete den neueren Record erhalten, die siebte Bestandskategorie ergänzen und
die betroffenen Prüfungen erneut ausführen. Ein bereits registrierter v1-Export
bleibt historisch gebunden; neue Registrierung verlangt den kategorisierten Export.
