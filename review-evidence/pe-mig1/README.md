# PE-MIG1 · einmalige Runtimeprojektion

Produkt-Head: `424620a20761953a11e2daa40031e4181f04a340`.
Basis: `745877a681dfeb052c335b78386adf3a3b136c00`.
Auftrag: [#641](https://github.com/venomenon328/picross/issues/641), nur M1.
Dieser separate Reviewref wird nicht nach main oder in den Produktbranch integriert.

Empfänger: unabhängiger technischer Reviewer für PE-MIG1-A01 vor Merge.
Belege bis zur Sichtung benötigt; am **21.11.2026** Bedarf erneut prüfen,
anschließend im beauftragten Rückbau entfernen. Keine unabhängige Abnahme durch
den Implementierer und keine Mergefreigabe. #576 bleibt offen. M2 erfolgt erst
nach verbindlicher Implementierung des neuen Editorformats in #640 und neuem Auftrag.

## Tatsächliches Ergebnis

- Sauberer eigener Worktree von aktuellem main; Inhaltsregistry v4 mit 56 Entries,
  56 Metadatenzeilen und 3 Hintergrundbindungen; Runtime v7 mit 56 Entries und
  20 Kategorien. `source-summary.json` bindet sämtliche IDs/Keys/Slots/Revisionen.
- Unveränderte CLI aus dem Basiscommit, CPython 3.13.14 mit isoliertem Pillow
  12.3.0 unter Windows. Je Aufruf unverändertes 300-s-Standardbudget. Plan und
  Apply getrennt, absolute Ziel-/Ausgabepfade; Ausgaben/TEMP außerhalb des Worktrees.
- `migration.json`: genau `game/data/registry.json`; old=v7, new=v8, alle übrigen
  Felder einschließlich kompletter Kategorien und Einträge exakt gleich.
- `migration-result.json`: von allen 1.628 Dateien ändern sich ausschließlich die
  Runtimebytes und deren mtime. Tatsächliche neue Runtimebytes entsprechen exakt
  den alten Bytes mit einem einzigen Austausch der Formatkennung v7 nach v8.
  Alle anderen 1.627 Dateien byte- und mtimegleich; kein neuer/entfernter Pfad.
- `repeat-apply.stdout.json`: erneutes Apply desselben gebundenen Plans ist noop.
  `noop-migration.json` und `noop-apply.stdout.json`: auch frisches Plan/Apply auf
  v8 ist noop; `noop-audit.log` bestätigt sämtliche Bytes und mtimes unverändert.
- `reader.stdout.log`: echter unveränderter Godot-4.7.2-Runtime-/Definitionsreader
  akzeptiert alle 56 Einträge, 20 Kategorien und 56 Definitionen. IDs, Revisionen,
  Maße, Lösung, Palette und Hinweise im Speicher mit Originaldefinitionen verglichen;
  aktuelle Name-/Revealauflösung stimmt. `reader-inputs.json` bindet die kopierten
  Originalquellen. Eigener minimaler Projekt-/Profilordner, kein SaveStore, keine
  echten Saves, keine Spiel-/Textur-/GUIabnahme. Engine:
  `4.7.2.stable.official.ed1daf0bf`, Console-EXE SHA-256
  `c8f0a6bc45a19b33541501e57f6f7cd972ab18453743266339d495cbbe846643`.
- `final-audit.json`: erst nach diesen Prüfungen zusätzlich der vom Benutzer
  ausdrücklich erlaubte administrative `.ci/package.json` aktualisiert;
  alle übrigen 1.626 Dateien bleiben byte- und mtimegleich. Keine Journale,
  Stagingdateien oder unversionierten Dateien im Produktcheckout.
- `core-tests.log`: 21 CI-Vertragstests erfolgreich. `docs.log`: Dokumentkern
  erfolgreich. `local-ci-plan.json`: sourcegebundener Plan am Produktcommit,
  keine Zusatzmodule, kein Playerbau für reine Inhaltsprojektion. Keine neuen
  Dauerprüfungen. Aktuelle Remote-CI und Testmerge werden im Produkt-PR verlinkt.

Ein erster lesender CLI-Planlauf wurde wegen eines von mir mit `..` angegebenen
externen Ausgabepfads abgewiesen. Der Pfadschutz akzeptiert den aufgelösten
absoluten Pfad. Danach ausschließlich reguläre CLI, keine Werkzeug-/Guardänderung,
keine freie Runtime-JSON-Manipulation und keine Budgeterhöhung.

## Reproduktion und Originale

Im sauberen isolierten Checkout des Basiscommits mit absolutem CHECKOUT und
absolutem, neuem PLAN außerhalb des Checkouts:

```text
python -B -m tools.puzzle_production.images_cli plan-migration --target-root CHECKOUT --output PLAN
python -B -m tools.puzzle_production.images_cli apply --target-root CHECKOUT --plan PLAN
```

Die Helfer sind einmalige externe Prüfscripte, keine Produkt-/CI-Tests.
`audit.py` erwartet sich neben `repo/` und `evidence/`; Modi before/plan/after/noop
entsprechen den getrennten tatsächlich ausgeführten Prüfschritten. `prepare_reader.py`
kopiert ausschließlich den gebundenen Reader, Capability, Runtime und Definitionen
in einen neuen `temp/reader-project`; `reader_probe.gd` ist dessen Headless-Einstieg.
Ein Reviewer kann alle entscheidenden Bytevergleiche direkt aus den JSON-Originalen
und den Basis-/Produktcommits wiederholen. `manifest.json` bindet die ausgewählten
unverändert kopierten Originale und Helfer; diese README ist nur die Zuordnung.
