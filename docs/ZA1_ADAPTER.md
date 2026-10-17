# ZA-1: Authoring-Eingang, Zieladapter und Registrierung

**KE / #233, Implementierungsvertrag vom 17.10.2026:**
Die Runtimeprojektion ist `picross-runtime-registry-v3` gemäß
[CATEGORIES](CATEGORIES.md): bisherige sieben Felder plus `difficulty` als null
oder sechs typisierte Angaben. Der Loader behält den exakten v2-Vertrag.
Registrierung, Update, explizite Projektion und Recovery verwenden dieselbe
minimale kanonische Projektion. Keine Produktionsfreitexte gelangen in die Runtime.
Exportmanifest-Versionen, Paket-/Integrationsbindungen und abgeschlossene
Freigaben bleiben unverändert. Entfernte Produktionspakete werden nicht
rekonstruiert. [KE-Nachweise](KE_VERIFICATION.md), separate KE-R01/KE-M01.

KAT-1 ergänzt den verbindlichen [Kategorien-/Kompatibilitätsvertrag](CATEGORIES.md).
Direkt-/Reparaturexporte mit Linienprofil verwenden v2, autorisierte manuelle Ableitungen v3,
jeweils mit expliziter Kategorie und gehashtem Snapshot;
Authoring-v2 und alte ZA-1-v1-Exporte bleiben technisch prüfbar.

Issue [#74](https://github.com/venomenon328/picross/issues/74), Fortschreibung [#144](https://github.com/venomenon328/picross/issues/144), Stand 15.10.2026.
`authoring-p1-rect-color-1` ergänzt Schema-2-Exporte; die Pilotprofile v1/v2 bleiben
unverändert. #139 B/C ergänzt ausdrücklich gebundene Paarprofile und Export v4;
kein Solver im Spiel.

Workflow, schlanke Repositoryablage und Integration: [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md), Abschnitte 3, 6 und 8. Version 0.5.0 ergänzt die Paarprofile; alte versiegelte 0.4.x-Pakete behalten ihren bisherigen Vertrag.

## Eingang und Grenzen

Python 3.11+, eigene Image-venv mit Pillow exakt 12.3.0 gemäß
[Werkzeuganleitung](../tools/puzzle_production/README.md). Ein Aufruf liest einen
Ordner oder ein ZIP mit optional genau einem Wurzelordner. Mitgeliefertes HTML,
Code und historische Archive werden niemals ausgeführt oder weiter entpackt.
Das Werkzeug ruft weder Netzwerk noch Git-Schreibaktionen auf.

Unterstützt: `picross-authoring-handoff-v2`, Regelwerk 0.4.0/0.4.1/0.5.0,
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
| Raster | 1…50 pro Achse, Mono oder 1…8 Vordergrundfarben plus Leer |
| Reveal | PNG/SVG, 32 MiB, 8192 pro Achse, 8.000.000 Pixel |
| Detailauflösung | mindestens zwei Pixel pro Zelle auf jeder Achse |
| SVG | lokales begrenztes Formprofil, höchstens 10.000 Elemente |

Relative Pfade: `/`, höchstens 240 Zeichen, keine absoluten Pfade, Traversal,
Backslashes, Laufwerke, Windows-Gerätenamen/-Kollisionen, Symlinks oder Reparsepunkte.
Produktions-ID: `pz-[a-z0-9][a-z0-9-]{0,59}`. Explizite Dateistämme/Save-Slots:
`[a-z][a-z0-9_-]{0,63}` unter denselben Pfadgrenzen. Paketrevision:
`[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}`. Runtime-Revision: explizite Ganzzahl
1…1.000.000, keine Ableitung aus `r03`. Grenzen führen zum Fehler ohne Zertifikat.

## Paarprofile, Schwierigkeit 0.2 und Export v4

Der [Paarlinienvertrag](PAIRED_LINES.md) gilt zusätzlich für ausdrücklich gewählte
Paarprofile. Authoring 0.5.0 samt tatsächlich als 0.5.0 bezeichnetem gebundenem
Regelwerksnapshot ist Pflicht. Handoff `candidate.certification` muss exakt der
aus Import/Reparatur/Manuellplan geprüften Konfiguration entsprechen. Alte
Produktionsformate und 0.4.x-Snapshots weisen diese Nachweise zurück.

`difficulty.method=picross-difficulty-0.2` bindet `profile_hash` und unter
`evidence` die tatsächliche Assessmentdatei neben dem ausgewählten Proof.
Baseline und Paarproof werden unabhängig frisch geprüft. R4 setzt einen
vollständigen Paarproof plus `full-line-* / stalled` derselben Logik voraus.
Dann sind `level=L5`, `plausible_range=[L5,L5]`, `assessment_type=instrumented`,
`confidence=medium`, Technikfamilie R4 und
`logical_demand="linienübergreifend / besonders hoher logischer Anspruch"` Pflicht.
Ein bereits mit Linien lösbarer Paarprofilfall darf R4 nicht beanspruchen und
behält die R0–R3-Kriterien. Fehlende/abgebrochene Baseline genügt nicht. Methode
0.1 bleibt für Linienfälle unter ihrem alten Vertrag lesbar; keine Umwertung.

Inspektionsbericht und Export verwenden v4 mit zusätzlichem `deduction`-Objekt
aus Profil, Profilhash und unabhängig rekonstruiertem Assessment. `tool_identity`
bindet auch `certification.py` und `paired_verifier.py`. Offline-Exportprüfung
vergleicht diese Bindung mit dem frischen vollständigen Replay; Registrierung
unterstützt v4 mit unverändertem Kategorie-/Slot-/Runtimevertrag.
Manuelle Exporte führen weiterhin ihre externe Autorisierung mit. Die folgenden
v1–v4-Autorisierungsverträge bleiben bestehen; lediglich ein ausdrücklich neu
profilierter Ableitungsplan/-datensatz verwendet seine in PAIRED_LINES benannte
v2-Variante. Keine neue Freigabe wird aus dem stärkeren Profil abgeleitet.

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
Runtime-Projektion v3 mit ausschließlich den typisierten KE-Katalogmetadaten;
die Inhaltsregistry bleibt v2.
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
`register` überschreibt belegte IDs weiterhin nicht. Für ausdrücklich beauftragte
Rasterersetzungen gilt der unten beschriebene gesonderte Updatepfad.

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

## Expliziter Ersatz eines registrierten Rasters (#144)

Die Eigentümeraufträge vom 15.10.2026 erlauben mehr als vier Vordergrundfarben
und den Ersatz der bisherigen Warnemünde-Fassung. Die gemeinsame technische
Obergrenze ist acht, passend zum bestehenden Produktionskern. Das reguläre
Zielprofil und feste Farbableitungen unterstützen 1…8 Farben plus Leer; der
eingefrorene v1-Exportweg behält seine Vierfarbgrenze. Neue Farben bleiben normale
stabile IDs; keine Zusammenlegung oder geänderte Leer-Semantik. Die Spielpalette
nutzt bei 5…8 Farben vier Spalten und zwei Reihen mit unveränderten Treffermaßen;
1…4 Farben behalten ihre bisherige Geometrie.

Ein neuer vollständig geprüfter und redaktionell freigegebener Export kann ein
vorhandenes Raster mit **höherer Runtime-Revision** ersetzen. Produktions-ID,
Key, Save-Slot, Runtimepfade, Sichtbarkeit, Kategorie und Revealbytes bleiben
gleich. Das neue Paket benötigt eine neue Paketrevision; das alte Produktions-
oder kompakte Integrationspaket wird unverändert behalten. Änderungen des
Abschlussbilds oder der Identität sind außerhalb dieses begrenzten Updatepfads.

```sh
python -m tools.puzzle_production.target_adapter plan-update --export <neuer-export> --checkout <checkout> --expected-definition-sha256 <Hash-der-bisherigen-Definition>
python -m tools.puzzle_production.target_adapter update --export <neuer-export> --checkout <checkout> --expected-definition-sha256 <derselbe-Hash>
```

API: `content_update.update(export_dir, checkout, expected_definition_sha256,
apply=False|True)`. Der Plan ist lesend, nennt alle Add-/Replace-/Unchanged-Pfade,
vorherige/neue Registry, Revisionen und den Hash des Updatemoduls. Der explizite
Erwartungshash verhindert ein Überschreiben eines inzwischen geänderten Rasters.
Die aktuelle Registry und der neue Export werden vollständig geprüft. Frischer
Staging-Replay, exakte Dateihashes und unveränderte Ausgangsbytes gehen der
Publikation voraus. Die Runtimeprojektion wird zuletzt geschrieben.

Das exklusive `content/.registration-pending.json` verwendet bei Updates
`picross-content-update-journal-v1`: alte/neue UTF-8-Bytes der beiden Indizes,
Definition und Nutzungshinweise, unveränderte Kategorienbytes, sicherer neuer
Paketpfad und dessen vollständige Dateihashes. Höchstens24 MiB Journal, bestehende
Paket-/Dateigrenzen unverändert. Normale Fehler rollen zurück. Nach Prozessabbruch
nutzt `recover-registration` denselben expliziten Recoverybefehl; alle aktuellen
Bytes müssen entweder dem alten oder neuen Stand entsprechen, und vorhandene
neue Paketdateien müssen ihren Hashes entsprechen. Fremdänderungen blockieren
vor jeder Mutation. Nur das neue Paket wird beim Rollback entfernt.

KE-N1 erweitert ausschließlich die Journal-Kompatibilität: Registrierungsjournal
v2 und Updatejournal v1 akzeptieren kanonisches Runtime-v2 (sieben Felder) sowie
aktuelles v3, jeweils einheitlich in beiden Snapshots. Der alte autoritative Stand
wird strikt einschließlich Schwierigkeit validiert; ein temporärer Prüfcheckout
mit gebundenen Runtime-Dateien, aufbewahrten Manifesten und Notices prüft den
gesamten v3-Zielstand vor der ersten Mutation. Kein Solver-/Exportreplay und keine
Rekonstruktion gelöschter Produktion. Definition/Notice werden bei Updates exakt
restauriert; Reveal, alte Pakete und fremde Dateien bleiben erhalten. Die Recovery
schreibt direkt die kanonische v3-Zielprojektion. Nach eigenem Prozessabbruch ist
nur genau diese zusätzliche Zwischenprojektion wiederaufnehmbar. Ein separates
späteres `sync-runtime` gehört nicht zum erfolgreichen Rollback. Unbekannte,
gemischte, nichtkanonische oder fremd veränderte Bytes blockieren mit erhaltenem
Journal. Die ältere Registrierungsjournal-v1-Sperre bleibt ausdrücklich bestehen.

Keine echten Saves werden gelesen, migriert oder gelöscht. Schema1 bleibt;
ein Save der alten Runtime-Revision wird nach bestehendem Vertrag als inkompatibel
abgewiesen und nicht auf neue Maße/Farben angewendet. Ein explizit vom Nutzer
ausgelöster Neustart unterliegt weiterhin dem bestehenden Save-/Recoverydialog.
Gleicher Export mit aktuellem Erwartungshash darf `no-op` sein; der frühere Hash
bleibt nach erfolgreichem Update absichtlich veraltet. Allgemeine Regressionen
verwenden ausschließlich synthetische Inputs in `test_content_update.py` und
`game/tests/multicolor_cases.gd`; keine reale Rätselprüfung in CI.

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

### Feste Farbkorrekturen mit nachträglicher Motivannahme (v3)

Eigentümerauftrag vom 14.10.2026 zur Nacharbeit B-PZ-03: Die additive
`picross-manual-authorization-v3` unterstützt versiegelte `raster_review`-
Farbimporte mit `editorial_manual_derivation`, `repair=null`, offenem Motivgate,
`motif.approval=null` und leerem `approved_parameters`. Keine Änderung des alten
Handoffs, kein rückdatiertes Gate. Die ausdrücklich nachträgliche menschliche
Annahme wird separat sichtbar. Alle übrigen Inhaltsgates müssen bestehen;
auch die Randregel bleibt ohne Ausnahme Pflicht. Die echten Endfreigabebytes
werden weiterhin über `--approval` gebunden. Bestehende v1/v2-Wege bleiben gleich.

Die Autorisierung hat genau die Felder `format`, `puzzle_id`, `revision`,
`original_zip_sha256`, `handoff_sha256`, `inventory_sha256`, `selection`,
`owner_override`, `superseded_content_blockers`, `accepted_motif`, `base`, `steps`.
Identität, Auswahl, Original-ZIP/Teilkopie und Owner-Dateireferenz folgen den
oben beschriebenen Bindungen. `superseded_content_blockers` stimmt exakt mit
den historischen `blockers` überein; zusätzlich vorhandene `content_blockers`
sind unzulässig. Keine anderen Gates werden dadurch aufgehoben.

- `accepted_motif` enthält genau `file`, `sha256`, `derived_from_reveal_sha256`,
  `revision`, `parameters`. Datei, Revealbezug und Revision entsprechen dem
  Originalhandoff. `parameters` ist ein tatsächlich vorgeschlagener Korridor
  mit Breite, Höhe, Modus, Vordergrundfarbzahl, Methode, Fit und tatsächlichem
  Crop; er muss zum geprüften finalen Design passen. Motivprovenienz und
  Abschlussbildfreigabe werden weiterhin aus dem Original geprüft.
- `base` enthält genau `source_type` (`import|repair`), `bundle`, `variant`,
  `reference_bundle`, `reference_variant`, `matrix_hash`. Bei Import sind beide
  Referenzfelder `null`; bei RP-5 werden der vollständige ursprüngliche RP-3-
  Import, die Reparatur, alle Eltern und Proofs rekonstruiert. Der ausgewählte
  Reparaturkandidat muss zertifiziert sein. Maße höchstens 50 je Achse, Modus
  `color`, höchstens acht Vordergrundfarben.
- `steps` enthält 1–8 Objekte mit genau `record`, `plan`, `output`, `protected`. Record/Plan
  sind `{file,sha256}`-Bindungen inventarisierter Dateien; Output enthält genau
  `bundle`, `variant`. Die letzte Stufe entspricht Handoff und
  `editorial_manual_derivation`. Jede Stufe replayt unveränderliche
  `picross-editorial-raster-redraw-v1`- oder
  `picross-editorial-fixed-cell-derivation-v1`-Records. Ihr zugehöriger
  `picross-editorial-raster-redraw-plan-v1` bzw.
  `picross-editorial-fixed-cell-plan-v1` bindet den Auftrag über `puzzle_id`.
  Redraw bindet den Plan-Dateihash; die feste Ableitung bindet dessen Pfad und
  identische Editliste. Eltern-/Ergebnismatrixhash und tatsächliche Editzahl
  müssen übereinstimmen. `search=false`, `seed=null` beziehungsweise nicht
  vorhanden; keine Suche oder neue Rasterwahl.

Edits sind eindeutige 1-basierte `{column,row,before,after}`-Objekte mit echten
Vorwerten und unterschiedlichen gültigen Leer-/Palettenwerten. Die historische
boolesche Schutzmaske steht beim Redraw im Record, bei der festen Ableitung im Plan.
Zusätzlich bindet jede externe Stufe `protected` als exakte wirksame Maske:
ausschließlich die gelisteten Edits sind ungeschützt. Eine historische
Redraw-Regionsmaske darf mehr Positionen freilassen; Edits dürfen keine ihrer
geschützten Positionen berühren, und jede übrige Zelle bleibt durch die externe
Maske und vollständige Ergebnismatrixprüfung unverändert. Bei festen Edits sind
historische und wirksame Maske identisch. Redraw-Limits stehen unter
`limits` (`max_changed_positions`, `solve_seconds`, `verify_seconds`, `max_lines`),
sonst im Plan (`max_changes`, `solve_seconds`, `verify_seconds`, `max_lines`).
Zellbudget höchstens Rastergröße, Sekunden 1–120, Linien 1–1.000.000. Der globale
Adapterbudgetrahmen bleibt bestehen. Jede geschriebene Zwischen-/Endstufe wird
mit RP-3 frisch rekonstruiert und unabhängig vollständig zertifiziert; Matrix,
Maße, Palette, Hintergrund, Alpha und Fit müssen zur festen Ableitung passen.
Crop und Methode werden am final akzeptierten Pixelquellimport gebunden.

`picross-owner-override-v3` enthält genau alle gemeinsamen Felder der
Autorisierung außer `format`, `original_zip_sha256`, `owner_override`, dazu
`format`, `actor`, `statement`, `timestamp_utc`, `package_sha256`,
`approval_sha256`, `permissions`. Die letzten Berechtigungen sind genau
`{fixed_color_edits:true, late_motif_acceptance:true}`. Originalpaket und echte
Endfreigabe sind hashgebunden. Software prüft Dateibindungen, authentifiziert
keinen menschlichen Akteur. Ein technischer Auftrag allein erfindet keine
Inhaltsabnahme; diese muss für die exakte Auswahl tatsächlich vorliegen.

CLI bleibt `--manual-authorization`; Exportformat bleibt
`picross-target-export-v3`. Autorisierung/Owner und alle benötigten Originale
werden offline mitgeliefert; Exportprüfung, Plan und Register prüfen sie erneut.
Der Prüfbericht führt historische Phase/Motivgate, externe Motivannahme,
überholte Metadatenblocker und frische feste Ableitungskette ausdrücklich.
Runtime-/Save-/Registryverträge bleiben gleich. Allgemeine Regressionen in
`test_color_derivation_adapter.py` verwenden ausschließlich synthetische Raster.

### Feste Farbkorrekturen bei bereits freigegebener Motivvorlage (v4)

Eigentümerauftrag vom 14.10.2026: Der additive Weg
`picross-manual-authorization-v4` ergänzt die ausdrücklich beauftragte
Integration fester Farbkorrekturen aus einer bereits freigegebenen Motivdatei.
Das versiegelte Original bleibt unverändert, einschließlich seiner tatsächlichen
Motivfreigabe. Keine nachträgliche Motivannahme und keine Gate-Ausnahme.

Der Eingang hat `state=raster_review`, `candidate.source_type=manual` und
`repair.type=fixed_color_editorial_redraw`. `repair` bindet `reference`,
`reference_variant`, `plan` und `record`; `editorial_manual_derivation` und
`manual_edit_record` sind nicht gesetzt. Alle acht Inhaltsgates einschließlich
`motif=pass` und Randregel bleiben Pflicht. Die separate tatsächliche Endabnahme
ist auch zur Diagnose zwingend.

Die Autorisierung hat dieselben Identitäts-, Auswahl-, Original-, Owner-,
Blocker-, `base`- und `steps`-Felder wie v3, ersetzt aber `accepted_motif` durch
`approved_motif`. Dieses enthält `file`, `sha256`,
`derived_from_reveal_sha256`, `revision`, `parameters` und zusätzlich
`approval={file,sha256}` für die ursprüngliche inventarisierte Motivfreigabe.
Die Parameter müssen im ursprünglichen `approved_parameters` liegen. Der
Originalimport (`base.source_type=import`) und seine Variante entsprechen
`repair.reference`/`reference_variant`. Die letzte Stufe entspricht
`repair.plan`/`record` und der Handoff-Auswahl.

`picross-owner-override-v4` folgt den gemeinsamen v3-Feldern mit
`approved_motif` und exakt `permissions={fixed_color_edits:true}`. Die echte
Erklärung bindet Paket, Handoff, Inventar, Auswahl und Endfreigabebytes. Es gibt
keine Berechtigung zur späten Motivannahme oder Randregel-Ausnahme. Historische
Blocker werden exakt extern gebunden; kein ursprüngliches Handoff wird geändert.

Der Adapter rekonstruiert den vollständig zertifizierten Originalimport aus der
unveränderten freigegebenen Motivdatei und prüft dort Crop, Methode und
Parameterkorridor. Danach werden alle festen Stufen wie bei v3 mit echten
Vorwerten, exakten Schutzmasken, Budgets, Eltern-/Ergebnishashes und vollständigem
unabhängigem Proof geprüft. Enthält ein fester Plan eine `reference`, bindet
sie exakt Bundle, Variante, Kandidaten-ID und Manifesthash des jeweiligen
Elternimports. Kindimporte dürfen Maße, Modus, Palette, Hintergrund, Alpha und
Fit nicht ändern. Ihre Pixelquellen sind Replayausgaben, keine Ersatzmotive.

CLI bleibt `--manual-authorization`, Exportformat bleibt v3. Offlineprüfung,
Plan und Register prüfen die vollständige Kette erneut. Der Bericht führt
`original_motif_gate=pass`, `late_motif_acceptance=false` und die tatsächliche
ursprüngliche Motivfreigabe. Allgemeine Positiv-/Negativregressionen in
`test_approved_color_adapter.py` verwenden ausschließlich synthetische Inputs.
Die bestehenden Autorisierungswege v1/v2/v3 bleiben getrennt und unverändert.

### Feste Farbkorrekturen aus einem bestätigten Linienfixpunkt (v5)

Der Integrationsauftrag vom 15.10.2026 zur vorgelegten korrigierten Nelke erlaubt
den notwendigen additiven Weg `picross-manual-authorization-v5`. Sein Schema
entspricht v4; die Eigentümerdatei verwendet `picross-owner-override-v5` und
exakt `permissions={fixed_color_edits:true, stalled_color_base:true}`. Beide
Wahrheitswerte und alle konkreten Paket-/Auswahl-/Freigabe-/Editbindungen sind
Pflicht. V1–v4 behalten ihre bisherigen Anforderungen.

Nur ein ursprünglicher Direktimport aus einer bereits freigegebenen Motivdatei
ist zulässig. Quelle, Normalisierung, Matrix und Hinweise werden rekonstruiert;
sein gespeicherter und frisch unabhängig bestätigter Status muss `stalled`,
`proof_verified=true`, `certified=false` sein. Bei Paarprofilen muss zusätzlich
die getrennte Linienbaseline unabhängig als `stalled` bestätigt sein.
Abbruch, Widerspruch, ungültiger Proof oder bloße Ergebnisflags genügen nicht.
Der Originalfixpunkt wird nicht in einen vollständigen Lösungsnachweis umgedeutet.

Alle festen Kindstufen benötigen weiterhin vollständige unabhängige Zertifikate
und exakte Endmatrixgleichheit; Schutzmasken, Originalparameter, Randregel,
Bild-/Motivfreigaben und tatsächliche Endabnahme bleiben Pflicht. Eine getrennte
Eindeutigkeitssuche an der Originalbasis ist nicht erforderlich: Die geprüfte
Originalmatrix belegt ihre Existenz, das vollständige Endzertifikat die
Eindeutigkeit des korrigierten Rasters. Kein Solver im Spiel.

Der Bericht führt unter `source.base_deduction` ausdrücklich den bestätigten
Originalstatus und dessen fehlende Vollzertifizierung. CLI, Runtime-/Saveformat
und die Exportversionen v3 beziehungsweise v4 bei Paarprofilen bleiben erhalten;
die Autorisierungsversion v5 ist keine neue Exportversion. Allgemeine Prüfungen
in `test_stalled_color_adapter.py` verwenden ausschließlich synthetische Raster.

## Abgeschlossene Produktion (14.10.2026, #116)

Nach nachgewiesener Endabnahme und Main-Integration ersetzt `retire-production`
die Prüfkopie durch `content/packages/<id>/<revision>/manifest.json` im Format
`picross-integrated-content-v1`. Es enthält exakt `format`, `entry` (ursprünglicher
Registryeintrag einschließlich ursprünglichem Exporthash), `integrated_commit`
und `notice_sha256`. Die Registry bindet jetzt den Hash dieses kleinen Manifests.
Definition, Reveal und Hinweisdatei unter `game/` bleiben bytegleich; deren Hashes,
Identität, Kategorie und Metadaten werden weiterhin geprüft. Die Runtimeprojektion
ändert sich nicht. Das ist kein neuer Export und keine neue Inhaltsfreigabe.

`check-registry`, `sync-runtime`, neue Registrierungen und identische Wiederholung
akzeptieren solche abgeschlossenen Einträge ohne Produktionsreplay. Ein fehlender
beliebiger Export wird nicht als abgeschlossen ausgegeben: dafür ist das explizite,
hashgebundene Format erforderlich. Neue Eingänge durchlaufen weiterhin den vollen
Export-/Freigabepfad. Kompakte Manifeste sind keine `verify-export`-Eingänge.

`retire-production --checkout <pfad> --integrated-commit <SHA> --puzzle-id <ID>`
prüft die SHA gegen das zuvor aktualisierte `origin/main`, die exakten damaligen
Registry-/Runtime-/Paket-/Arbeitsbytes und den Arbeitsindex vor jeder Löschung.
Neuere/unversionierte Arbeit und offene Registrierungsjournale blockieren. Der Befehl
bereitet ausschließlich einen Git-Diff vor; Commit, PR und Merge folgen dem Workflow.
Kein automatischer Nach-Merge-Job und kein wachsender CI-Testbestand.
