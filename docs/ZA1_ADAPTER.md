# ZA-1: Authoring-Eingang, Zieladapter und Registrierung

KAT-1 ergänzt den verbindlichen [Kategorien-/Kompatibilitätsvertrag](CATEGORIES.md).
Neue Direkt-/Reparaturexporte verwenden v2, autorisierte manuelle Ableitungen v3,
jeweils mit expliziter Kategorie und gehashtem Snapshot;
Authoring-v2 und alte ZA-1-v1-Exporte bleiben technisch prüfbar.

Issue [#74](https://github.com/venomenon328/picross/issues/74), Stand 13.10.2026.
`authoring-p1-rect-color-1` ergänzt Schema-2-Exporte; die Pilotprofile v1/v2 bleiben
unverändert. Keine neue Zertifizierungsregel, kein Solver im Spiel.

Workflow, schlanke Repositoryablage und Integration: [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md), Abschnitte 3, 6 und 8. Die Dokumentrevision 6 ergänzt gebundene manuelle Ableitungen und Ausnahmen; die kompatible Vertragsversion 0.4.1 bleibt erhalten.

## Eingang und Grenzen

Python 3.11+, eigene Image-venv mit Pillow exakt 12.3.0 gemäß
[Werkzeuganleitung](../tools/puzzle_production/README.md). Ein Aufruf liest einen
Ordner oder ein ZIP mit optional genau einem Wurzelordner. Mitgeliefertes HTML,
Code und historische Archive werden niemals ausgeführt oder weiter entpackt.
Das Werkzeug ruft weder Netzwerk noch Git-Schreibaktionen auf.

Unterstützt: `picross-authoring-handoff-v2`, Regelwerk 0.4.0/0.4.1,
`picross-authoring-file-inventory-v1` sowie unveränderte RP-3/RP-5-Verträge.
Redaktionelle Zusatzfelder bleiben erhalten. Pflichtbindungen sind typisiert;
unbekannte technische Schemas, doppelte JSON-Schlüssel, nichtendliche Zahlen
und fehlende Dateien sind Fehler. Das Inventar schließt Inventar und Handoff aus;
alle anderen Originaldateien bindet es mit Größe und SHA-256.

| Grenze | Wert |
| --- | --- |
| ZIP / einzelne Datei / entpackte Gesamtbytes | 128 MiB / 64 MiB / 512 MiB |
| Dateien / Verzeichnisse plus Dateien | 2048 / 4096 |
| Eingangsprüfung inklusive Extraktion | 300 Sekunden |
| Importprüfung / vollständiger Reparatur-Replay | höchstens 120 / 60 Sekunden |
| Proof-Linienbudget | 1.000.000; weitere RP-Budgets bleiben bestehen |
| Raster | 1…50 pro Achse, Mono oder 1…4 Vordergrundfarben plus Leer |
| Reveal | PNG/SVG, 32 MiB, 8192 pro Achse, 8.000.000 Pixel |
| Detailauflösung | mindestens zwei Pixel pro Zelle auf jeder Achse |
| SVG | lokales begrenztes Formprofil, höchstens 10.000 Elemente |

Relative Pfade: `/`, höchstens 240 Zeichen, keine absoluten Pfade, Traversal,
Backslashes, Laufwerke, Windows-Gerätenamen/-Kollisionen, Symlinks oder Reparsepunkte.
Produktions-ID: `pz-[a-z0-9][a-z0-9-]{0,59}`. Explizite Dateistämme/Save-Slots:
`[a-z][a-z0-9_-]{0,63}` unter denselben Pfadgrenzen. Paketrevision:
`[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}`. Runtime-Revision: explizite Ganzzahl
1…1.000.000, keine Ableitung aus `r03`. Grenzen führen zum Fehler ohne Zertifikat.

## Technische Bindungen und Freigabe

Diagnose prüft Inventar, Regelwerk, Briefing/Bericht/Entscheidungen/Aufwand als
Dateien, beide Bildfreigaben samt Beleg, Provenienz/Nutzungsgrundlage,
Motivableitung, Parameterkorridor und alle acht Inhaltsgates.
`candidate.source_type` ist ausdrücklich `import`, `repair` oder das unten
beschriebene, gesondert autorisierte `manual`. Direktimporte
binden `bundle`, `variant`, `proof`, `matrix_hash`, `logic_hash`; Reparaturen
zusätzlich `repair_id`, `parent_variant`. `repair` bindet `reference`,
`reference_variant`, `plan`. Endkandidat und Referenzvariante sind getrennt.
Externes und im Bündel enthaltenes Plan-JSON müssen kanonisch identisch sein.

`inspect_candidate` rekonstruiert Quelle, Normalisierung, Matrix und Hinweise;
`inspect_repair` prüft sämtliche Kandidaten, Eltern, Masken und Proofs erneut.
Ursprüngliche Abbrüche oder passende Ergebnisflags genügen nicht. Exakte
Singleton-Enddomains müssen der Auswahl entsprechen. Zusätzlich gilt
`(left OR right) AND (top OR bottom)`; keine künstlichen Randpixel.

`approved_parameters` bindet Maße, Modus, Farbzahl, Methode, Fit und Crop.
`gate_evidence` referenziert Inventardateien. Bildprovenienz bindet `puzzle_id`,
`file`, `sha256`, `author`, `usage_basis`; Motivprovenienz zusätzlich `derived_from`.
Schwierigkeit bindet Methode `picross-difficulty-0.1`, Logikhash, L1…L5,
plausiblen Bereich, Vertrauen und Regelfamilienbegründung. Schätzung/low und
fehlendes Probespiel bleiben zulässig.

Finale Freigabe liegt getrennt vom versiegelten Original als `--approval` oder
ausdrücklich referenzierte `final_editorial_approval`-Datei vor:

```json
{
  "format": "picross-editorial-approval-v1",
  "actor": "<tatsächlicher Akteur>",
  "timestamp_utc": "<tatsächliche UTC-Zeit>",
  "statement": "<tatsächliche Erklärung>",
  "puzzle_id": "<Produktions-ID>",
  "revision": "<Paketrevision>",
  "handoff_sha256": "<Originalhandoff-Dateihash>",
  "inventory_sha256": "<Originalinventar-Dateihash>",
  "selection": {
    "variant": "<ausgewählter Endkandidat>",
    "matrix_hash": "<kanonischer Matrixhash>",
    "logic_hash": "<kanonischer Logikhash>",
    "reveal": {"file": "<Originalpfad>", "sha256": "<Originalbildhash>"}
  },
  "test_only": false
}
```

Die Software prüft Aufzeichnung und Dateibindungen, authentifiziert aber keinen
menschlichen Akteur. Seine tatsächliche Erklärung muss vorliegen. Keine erfundene
Freigabe, kein Force-Schalter. Fehlende Endabnahme erlaubt technische Diagnose
mit konkretem Blocker, verhindert Export. `technical`, `editorial_approved`,
`category_ready`, `catalog_ready` und `registered` bleiben getrennt.
Diagnose ohne Kategorie behauptet keine Katalogbereitschaft; ein kategorisierter
Export benötigt zusätzlich die ausdrücklich angegebene gültige Kategorienquelle.

## Aufruf und Ausgabe

Aus dem Repository-Root; Platzhalter bezeichnen echte bereitgestellte Eingänge.
Ausgabepfade müssen neu sein; `inspect` darf ohne Freigabe laufen.
Standardintegration: `export` → `plan` → `register`. `export` prüft den Eingang
und seinen geschriebenen Export intern; `plan` und `register` prüfen ihn erneut.
Die unten zusätzlich gezeigten `inspect`-/`verify-export`-Befehle dienen gezielter
Diagnose oder separater Prüfung, nicht einer verpflichtenden Doppelrunde.

```sh
python -m tools.puzzle_production.target_adapter inspect --input <paket-oder-zip> --report <neue-diagnose.json>
python -m tools.puzzle_production.target_adapter export --input <paket-oder-zip> --approval <echte-endfreigabe.json> --name "<Motivname>" --runtime-revision 1 --stem blatt_001 --save-slot blatt_001 --category-id <kategorie-id> --categories content/categories.json --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter verify-export --export <neuer-export>
python -m tools.puzzle_production.target_adapter plan --export <neuer-export> --checkout <checkout>
python -m tools.puzzle_production.target_adapter register --export <neuer-export> --checkout <checkout>
```

JSON-Ausgabe: Diagnose/Erfolg Exit 0, blockierter Eingang Exit 2, Budgetabbruch
Exit 4. API: `inspect`, `export`, `verify_export`, `registration(..., apply=False|True)`.
Manifest `picross-target-export-v2` bindet Kategorie/Snapshot, Eingänge, separate Freigabe, frische
Prüfung mit Toolcommit/Modulhashes, Matrix/Logik, Farbabbildung und Runtimebytes.
Farb-IDs werden stabil nach Logikfarben auf 1…N abgebildet, Leer bleibt 0.
PNG/SVG bleiben bytegleich, Darstellung proportional. Geschriebene Dateien
werden frisch geprüft und erst dann veröffentlicht. Bestehende Ziele sind Fehler.

## Registrierung und Fehlerverhalten

[content/registry.json](../content/registry.json) ist autoritativ;
[game/data/registry.json](../game/data/registry.json) ihre exakt kanonisch geprüfte
Runtime-Projektion ohne Produktionsmetadaten, beide jetzt versioniert als v2.
Kategorien/Zuordnung folgen [KAT-1](CATEGORIES.md). Alle Produktions-IDs folgen
lexikografisch, ohne reservierten Präfixbestand; auch null Einträge sind gültig.
Die früheren F01…F09-Reservierungen sind durch #114 aufgehoben. Unbekannte IDs
und Großschreibungsaliase haben keinen Loader-/Savepfad. Hauptszene, Loader,
SaveStore und Reset verwenden dieselbe Zuordnung. Neue ungelöste Titel:
`Blatt NN · W × H`. Appidentität, Save-Schema 1, registrierte Slots,
Revisionen und Recoveryregeln bleiben erhalten; keine Save-Migration. Verwaiste
Savedateien bleiben unberührt und erzeugen keine Katalogeinträge.

Der Produktionsindex führt Paketort/-hash, Revision, Maße, Modus, Schwierigkeit
samt Unsicherheit, Status und Blocker. Runtime lädt nur mitgelieferte Pfade.
`plan` prüft sämtliche ID-/Slot-/Pfadkollisionen und zeigt Add-/Replace-Pfade
samt Registry vorher/nachher. `register` ist die ausdrückliche Übernahme.
Exklusives Journal; Runtime-Projektion wird zuletzt geschrieben. Normale Fehler
rollen Dateien und Indizes zurück. Ein Prozesskill hinterlässt
`content/.registration-pending.json`; folgende Prüfungen/Registrierungen stoppen.

```sh
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

Recovery prüft vor jeder Änderung alte/neue Indizes, sichere Ziele und vorhandene
Zielbytes. Fremdänderungen stoppen zur manuellen Prüfung. Identische erneute
Übernahme ist `no-op`; abweichende Daten unter belegter ID/Revision sind Konflikte.
Allgemeine Inhaltsupdates sind außerhalb ZA-1.

Prüfketten: `content/packages/<id>/<revision>/`, außerhalb des Spiels.
`picross-authoring-derivation-v1` erhält Originalinventar und Handoff unverändert,
bindet deren Hashes und gegebenenfalls Original-ZIP-Hash und enthält alle erneut
benötigten Originaldateien. Es behauptet keine vollständige Paketkopie.
Der Spieler erhält Runtime-Ressourcen und einen `.txt`-Hinweis aus
Urheber/Nutzungsgrundlage. Proofs, Quellen, Freigabeprotokolle und Testpakete
bleiben ausgeschlossen. Für reine Inhaltsintegration gelten die Adapter-/Dateiprüfungen
aus [PUZZLE_AUTHORING §8](ai-workflows/PUZZLE_AUTHORING.md); kein obligatorischer
nativer Spiel-/Neustart-/PCK-Test oder Spielerbuild je Rätsel. Zusätzliche Proben
nur wegen konkreter Befunde; allgemeine Code-/Exportregressionen bleiben separat.

Künstliche Freigaben sind `test_only=true`; Registrierung im echten eigenen
Checkout wird verweigert. Die folgenden allgemeinen Entwicklungsprüfungen gehören
zu passenden Werkzeug-/Spieländerungen, nicht zur Produktion einzelner Rätsel.
Reproduzierbarer Durchstich ausschließlich temporär:

```sh
python -m tools.puzzle_production.za1_fixtures --output-dir artifacts/za1-replay
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python tools/p1_product.py --cache-dir <toolchain-cache> --output-dir <neuer-produktnachweis>
```

Referenzeingang und Beleggrenzen: [ZA1_VERIFICATION.md](ZA1_VERIFICATION.md).

## Autorisierte manuelle Ableitungen

Die ausdrückliche Eigentümerentscheidung vom 13.10.2026 stellt die geprüfte
manuelle Ableitung dem technischen Produktionsweg gleich. Dafür unterstützen
`inspect` und `export` zusätzlich `--manual-authorization <datei>`; die übrigen
Inhalts-, Nachweis-, Bild- und Endfreigabegates bleiben bestehen. Kein Force-Modus,
keine Änderung des versiegelten Pakets oder seiner ursprünglichen Freigabe.

Der begrenzte erste Vertrag unterstützt monochrome, feste `ink`→`empty`-Edits.
`picross-manual-edit-plan-v1` enthält Referenzbundle/-variante/-kandidat/-manifest-
und Matrixhash, exakte Editfolge, boolesche Schutzmaske für jede andere Position,
Änderungs-/Schritt-/Prüfbudgets, genau einen Kandidaten, Operator
`remove-ink-only` und `seed=null`. `picross-manual-candidate-v1` bindet Planhash,
Referenz, unveränderten Entwurf, jede Elternmatrix, vollständigen Zell-Diff und
Endmatrix. Quelle/Normalisierung werden mit RP-3 rekonstruiert; dann wird jede
Entfernung motivgeschützt replayt. Hinweise müssen exakt aus dem Ergebnis folgen.
Der abgeschlossene `picross-result-v1` und geschriebene Proof unter
`<bundle>/certificate/` werden mit dem bestehenden unabhängigen Prüfer bestätigt;
Enddomains müssen exakt der Matrix entsprechen. Kein Raten oder neues Solverprofil.

Die externe `picross-manual-authorization-v1`-Datei hat genau diese Felder:

```json
{
  "format": "picross-manual-authorization-v1",
  "puzzle_id": "<ID>",
  "revision": "<Revision>",
  "original_zip_sha256": "<Original-ZIP-Hash, bei unverpacktem Eingang null>",
  "handoff_sha256": "<unveränderter Originalhandoff>",
  "inventory_sha256": "<Originalinventar>",
  "selection": {"variant": "<Endkandidat>", "matrix_hash": "<Matrix>", "logic_hash": "<Logik>", "reveal": {"file": "<Reveal>", "sha256": "<Hash>"}},
  "plan_sha256": "<Plan-Dateihash>",
  "owner_override": {"file": "owner-override.json", "sha256": "<Dateihash>"},
  "superseded_content_blockers": ["<exakt autorisierte historische Metadatenblocker>"]
}
```

Daneben liegt die bytegebundene tatsächliche `picross-owner-override-v1`-Erklärung
mit Akteur, UTC-Zeit, Erklärung, ID/Revision, Paket-/Handoff-/Inventarhash,
exakter Auswahl und `approval_sha256`. Die Software prüft Bindungen, authentifiziert
keinen menschlichen Akteur. `superseded_content_blockers` muss exakt dem alten
Handoff entsprechen; keine anderen Inhaltsgates werden dadurch aufgehoben.
Ein historischer `raster_review`-Handoff wird nur bei explizitem manuellem Eingang
gelesen und danach vollständig geprüft. Alle anderen Zustände/Quelltypen behalten
ihren bisherigen Prüfweg. Freigabe und Autorisierung liegen außerhalb des Inventars.

Manuelle Exporte verwenden **`picross-target-export-v3`** mit Kategorie und
zusätzlicher `manual_authorization={file,sha256}`. Autorisierung und tatsächliche
Eigentümererklärung werden unverändert mitgeliefert; Originalhandoff/-inventar
bleiben in der deklarierten Prüfkopie bytegleich. `verify-export` und
`plan`/`register` prüfen diesen Weg offline erneut. Reveal bleibt bytegleich zum
zuerst freigegebenen Abschlussbild. Runtime-Schema 2, IDs, Slots, Saveformat und
Registrierungstransaktion bleiben gleich. v1/v2-Direkt-/RP-5-Exporte bleiben
unverändert lesbar; v1 wird weiterhin nicht neu registriert.

Die allgemeinen Regressionen liegen in `test_manual_adapter.py` und erzeugen nur
feste synthetische Eingänge. Reale Pakete/Overrides werden nicht in Tests oder CI
aufgenommen. Der konkrete Produktionsexport bleibt eine getrennte Einzelprüfung.

### Feste bearbeitete Rasterimporte und gebundene Randregel-Ausnahme (v2)

`picross-manual-authorization-v2` ergänzt v1 für bereits versiegelte monochrome
RP-3-Ableitungen mit festen Entfernungen **und Einfügungen**. Das Originalhandoff
bleibt unverändert: `candidate.source_type=import`, `repair=null` und
`manual_edit_record` bezeichnet die gespeicherte feste Änderungsliste. Auch
`state=blocked` darf mit ausdrücklich übergebener v2-Autorisierung eingelesen
werden; das allein erteilt keine technische Freigabe. Andere Quelltypen und die
bisherigen v1-Verträge bleiben unverändert.

Die externe Autorisierung hat genau folgende Felder:

```json
{
  "format": "picross-manual-authorization-v2",
  "puzzle_id": "<ID>",
  "revision": "<Originalrevision>",
  "original_zip_sha256": "<ZIP-Hash oder null bei unverpacktem Eingang>",
  "handoff_sha256": "<Originalhandoff>",
  "inventory_sha256": "<Originalinventar>",
  "selection": {"variant": "<Endvariante>", "matrix_hash": "<Matrix>", "logic_hash": "<Logik>", "reveal": {"file": "<Reveal>", "sha256": "<Hash>"}},
  "plan_sha256": "<Dateihash von manual_edit_record>",
  "reference": {"bundle": "<Originalimport>", "variant": "<Referenzvariante>", "candidate_id": "<Kandidat>", "manifest_sha256": "<Manifest>", "matrix_hash": "<Referenzmatrix>"},
  "owner_override": {"file": "owner-override.json", "sha256": "<Dateihash>"},
  "superseded_content_blockers": ["<exakt gebundene historische Metadatenblocker>"],
  "frame_exception": true
}
```

Daneben liegt die tatsächliche `picross-owner-override-v2`-Erklärung mit Akteur,
UTC-Zeit, Wortlaut, `package_sha256`, `approval_sha256`, sämtlichen gemeinsamen
Identitäts-/Auswahl-/Plan-/Referenz-/Blockerbindungen und exakt
`permissions={fixed_mono_edits:true, frame_exception:<bool>}`. Beide
Ausnahmeberechtigungen müssen typisiert übereinstimmen; ein allgemeiner
Force-Schalter existiert nicht. Die Erklärung muss tatsächlich vorliegen;
Software prüft Bindungen, authentifiziert aber weiterhin keinen menschlichen Akteur.

Die inventarisierte Änderungsliste führt `puzzle_id`, `revision`, `reference`
mit Bundle/Variante/Kandidaten-/Matrixbindung, `edits` als geordnete
`{column,row,before,after}`-Objekte (**1-basierte** Spalte/Zeile), die boolesche
Maske `protected`, `max_changes`, `seed=null`, `search=false` sowie
`solve_seconds`, `verify_seconds` (1…120) und `solve_lines`, `verify_lines`
(1…1.000.000). Redaktionelle Begleitfelder bleiben erhalten. Jede Position darf
nur einmal geändert werden; ausschließlich `ink`↔`empty`, tatsächlicher
Vorwert, genau diese ungeschützten Positionen, alle anderen Zellen geschützt.
Die feste Liste und ihre Grenzen sind vor der Bearbeitung zu speichern.

Der Adapter rekonstruiert zuerst den vollständigen Originalimport, replayt
sämtliche Edits und rekonstruiert anschließend das vollständige neue RP-3-Bündel.
Endmatrix, Maße, Palette, Hintergrund, Alpha und Fit müssen passen; Herkunft und
freigegebener Parameterkorridor werden am **Originalimport** geprüft. Hinweise
und geschriebener Endproof werden unabhängig neu geprüft; ursprünglicher
Produktionsstatus muss vollständig zertifiziert sein. Der neue Rasterquellimport
wird ausdrücklich als manuelle Ableitung exportiert, nicht als unveränderter
Motivimport. Die Endfreigabe ist bei diesem Weg auch zur Diagnose zwingend.

Alle Inhaltsgates bleiben Pflicht. Ausschließlich `frame=fail` kann mit
ausdrücklich freigegebener `frame_exception=true` akzeptiert werden. Die
Randformel wird weiterhin berechnet; Berichtsfelder `frame_valid=false` und
`frame_exception_accepted=true` zeigen die Abweichung sichtbar. Kein Überschreiben
des Originalgates, keine zusätzlichen Randpixel und keine Lockerung von
Logik-, Herkunfts-, Rechte-, Bild- oder sonstigen Gates. Dies setzt die ausdrückliche
Eigentümerentscheidung für die exakte Auswahl voraus, keine pauschale Randfreigabe.

CLI bleibt `--manual-authorization <v2-Datei>`; Exportformat bleibt v3.
Autorisierung, Eigentümererklärung und unveränderte Originalbindungen werden
offline mitgeliefert und bei `plan`/`register` erneut geprüft. Allgemeine
Positiv-/Negativtests stehen in `test_edited_import_adapter.py`; keine realen
Produktionspakete als Test- oder CI-Eingänge.
