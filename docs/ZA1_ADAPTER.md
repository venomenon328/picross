# ZA-1: Authoring-Eingang, Zieladapter und Registrierung

Issue [#74](https://github.com/venomenon328/picross/issues/74), Stand 12.10.2026.
`authoring-p1-rect-color-1` ergänzt Schema-2-Exporte; die Pilotprofile v1/v2 bleiben
unverändert. Keine neue Zertifizierungsregel, kein Solver im Spiel.

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
`candidate.source_type` ist ausdrücklich `import` oder `repair`. Direktimporte
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
`catalog_ready` und `registered` bleiben getrennt.

## Aufruf und Ausgabe

Aus dem Repository-Root; Platzhalter bezeichnen echte bereitgestellte Eingänge.
Ausgabepfade müssen neu sein; `inspect` darf ohne Freigabe laufen.

```sh
python -m tools.puzzle_production.target_adapter inspect --input <paket-oder-zip> --report <neue-diagnose.json>
python -m tools.puzzle_production.target_adapter export --input <paket-oder-zip> --approval <echte-endfreigabe.json> --name "<Motivname>" --runtime-revision 1 --stem blatt_001 --save-slot blatt_001 --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter verify-export --export <neuer-export>
python -m tools.puzzle_production.target_adapter plan --export <neuer-export> --checkout <checkout>
python -m tools.puzzle_production.target_adapter register --export <neuer-export> --checkout <checkout>
```

JSON-Ausgabe: Diagnose/Erfolg Exit 0, blockierter Eingang Exit 2, Budgetabbruch
Exit 4. API: `inspect`, `export`, `verify_export`, `registration(..., apply=False|True)`.
Manifest `picross-target-export-v1` bindet Eingänge, separate Freigabe, frische
Prüfung mit Toolcommit/Modulhashes, Matrix/Logik, Farbabbildung und Runtimebytes.
Farb-IDs werden stabil nach Logikfarben auf 1…N abgebildet, Leer bleibt 0.
PNG/SVG bleiben bytegleich, Darstellung proportional. Geschriebene Dateien
werden frisch geprüft und erst dann veröffentlicht. Bestehende Ziele sind Fehler.

## Registrierung und Fehlerverhalten

[content/registry.json](../content/registry.json) ist autoritativ;
[game/data/registry.json](../game/data/registry.json) ihre exakt kanonisch geprüfte
Runtime-Projektion ohne Produktionsmetadaten. F01…F09 bleiben reserviert, nur
F01/F02/F04/F06/F08/F09 sichtbar. Neue IDs folgen lexikografisch. Unbekannte IDs
und Großschreibungsaliase haben keinen Loader-/Savepfad. Hauptszene, Loader,
SaveStore und Reset verwenden dieselbe Zuordnung. Neue ungelöste Titel:
`Blatt NN · W × H`. Appidentität, Save-Schema 1, historische Dateinamen,
Revisionen und Recoveryregeln bleiben erhalten; keine Save-Migration.

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
bleiben ausgeschlossen. Der echte Windows-PCK wird nativ geprüft.

Künstliche Freigaben sind `test_only=true`; Registrierung im echten eigenen
Checkout wird verweigert. Reproduzierbarer Durchstich ausschließlich temporär:

```sh
python -m tools.puzzle_production.za1_fixtures --output-dir artifacts/za1-replay
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python tools/p1_product.py --cache-dir <toolchain-cache> --output-dir <neuer-produktnachweis>
```

Referenzeingang und Beleggrenzen: [ZA1_VERIFICATION.md](ZA1_VERIFICATION.md).
