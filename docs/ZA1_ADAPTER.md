# ZA-1: Authoring-Eingang, Zieladapter und Registrierung

**AT · Abschlussbildtransparenz, freigegebener Sollvertrag vom 19.10.2026; Umsetzung offen:**
[AT](REVEAL_TRANSPARENCY.md) ergänzt nach gesonderter Beauftragung mit AT-A einen
eng begrenzten Bildupdateweg; AT-B stellt anschließend den gebundenen Bestand um.
Der aktive Bildhash und die neue tatsächliche Bildfreigabe werden außerhalb
historischer Produktions-/Integrationsbelege gebunden. Die vorhandenen
Export-/Rasterupdatebefehle werden dadurch noch nicht geändert oder freigegeben.
Definitionen, Runtime-Revisionen, IDs, Ressourcenpfade, Slots, Kategorien, Ratings
und Hinzugefügt-Daten bleiben beim Bildupdate unverändert.

**KU-B / #244, freigegebener Sollstand vom 18.10.2026; Umsetzung offen:**
[Katalogsortierung](CATALOG_SORTING.md) ergänzt die erste Katalogaufnahme als
separate ID-gebundene Metadatenquelle außerhalb historisch versiegelter Pakete.
Erstregistrierung, Update, Sync, Bewertungsübernahme und Recovery müssen dieselbe
versionierte Quellenprüfung und minimale UTC-Zeitpunkt-/null-Projektion verwenden.
Bei der neuen Erstregistrierung wird UTC genau einmal im mutierenden
Transaktionsplan fixiert; lesende Pläne erzeugen keinen endgültigen Zeitpunkt.
Erfolgreiche Wiederholung, spätere Inhalts-/Metadatenänderung und Recovery
erhalten den bestehenden Wert oder ausdrücklich unbekannten Altwert. Kein
Vorwegnehmen des späteren main-Mergezeitpunkts und kein erneutes Datieren beim Export.

Der ausdrücklich ausgeführte historische Backfill erhält Plan, kontrollierte
Übernahme und dauerhaften Herkunftsbeleg je ID. Ein erster belegter gültiger
sichtbarer Registry-Snapshot darf gemäß dem Sortiervertrag als rekonstruierter
Referenzzeitpunkt dienen; Quellenlücken bleiben neutral dokumentiert.
Definitionen, Rätsellogik, Schwierigkeit, Slots, Freigaben und historische
Integrationsmanifeste bleiben unverändert. Neue Feld-/Datei-/Versionsverträge
werden vor der ersten betroffenen KU-B-Codeänderung konsistent festgeschrieben;
die folgenden exakten Altformate bleiben als solche lesbar. Der jetzige
Spezifikationsauftrag führt weder Registrierung noch Übernahme aus.

**SD-C1, technischer Vertrag vom 17.10.2026:**
[Bewertungsquelle und Transaktionen](SD_CATALOG.md) ergänzen den
Integrationsweg. Die unten dokumentierten Export-, Registrierungs- und
Recoverybefehle verwenden gemeinsam die neue Quelle. Neue Registrierungen und
logikrelevante Updates benötigen einen extern vollständig geprüften 0.3-Input.
Export-/Inhaltsfreigaben bleiben; reale Bestandsübernahme bleibt SD-C2.

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
versuchen kontrollierten Rollback; Fremdänderungen erhalten Dateien und Journal.
Ein Prozesskill hinterlässt
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

## SD · Zusätzliche Bewertungsbindung

Ab SD-C1 braucht jedes neu registrierte oder logisch geänderte Rätsel einen
vollständig geprüften 0.3-Input. Die vorhandenen technischen und redaktionellen
Inhaltsgates bleiben unabhängig davon bestehen. Ein fehlender, abgebrochener oder
unpassender Bewertungsnachweis wird nicht durch eine Schätzung oder 5 ersetzt.

[SD-C1](SD_CATALOG.md) und die [Werkzeuganleitung](../tools/puzzle_production/README.md)
binden Formate und Befehle. `catalog_analysis candidate` verwendet vor der
Endfreigabe dieselbe Farbabbildung wie der reguläre Export; `analyze`/`import`
prüfen das vollständige Bundle. Nach Export bindet `rebind` bei identischer
ID/Produktionsmodus/Logik/Matrix die echten Definitionsbytes, ohne `rating.source` umzuschreiben.
Analyse und Standalone-Rebind verlangen den expliziten Produktionsmodus; neue
checked-/aktive v2-Hüllen binden ihn getrennt vom eingefrorenen SD-B-Rating.
Mono↔Einfarb-Color erfordert auch bei identischen numerischen Hinweisen eine neue
Analyse. Alte v1-Hüllen bleiben lesbar und recoverbar, liefern aber keine erfundene
Modusherkunft für eine Neubindung. Einzelheiten stehen im SD-C1-Vertrag.
`plan`/`register` und `plan-update`/`update` erhalten den Input mit
`--difficulty <checked.json>`. `--rebind-difficulty` erlaubt die ausdrückliche
Neubindung im Integrationsschritt, bei Update auch aus dem bisherigen aktiven
Rating. Registrierung startet keine Schwierigkeitsanalyse oder SD-Spurprüfung;
die bestehenden obligatorischen ZA-1-Produktions-/Exportprüfungen bleiben vollständig.

Reine Neubewertung verwendet `preview` beziehungsweise `preview-checked`, dann
`plan-adoption` und `adopt` im Modul `catalog_analysis`. Sie ändert keine
Definitionen, Revisionen, Saves, historischen Produktionsbewertungen, Originalhandoffs,
Inventare oder Integrationsbelege. Fehlendes Sidecar erhält historische 0.1/0.2
beziehungsweise null; vorhandene ungültige Daten blockieren ohne Fallback.
Aktive Gültigkeit hängt nicht am gesamten Registry-, Git-HEAD- oder Pakethash.
Produktionscleanup entfernt die kompakte Bewertung und Berichte nicht.

Register, Update, Übernahme, Sync und Recovery verwenden dieselbe Quellenpriorität.
Neue Journale sind Registrierung v3, Update v2 und Bewertungsübernahme v1 unter
dem bestehenden gemeinsamen Lock. Exakte KE-Altjournale bleiben ausschließlich
ohne ungebundene aktive Sidecars wiederaufnehmbar; Journal-v1-Sperren bleiben.
Fremdänderungen stoppen mit erhaltenen Dateien und Journal. Erfolgreiche Recovery
hinterlässt unmittelbar einen gültigen aktuellen Checkout, ohne nachträgliches Sync.
Identische Legacy-Wiederholungen bleiben ohne neue Bewertung No-op.

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

Der freigegebene [AT-Bildupdatevertrag](REVEAL_TRANSPARENCY.md) erweitert diesen
Rasterupdateauftrag nicht. AT-A muss zusätzlich sicherstellen, dass spätere
Rasterupdates eine bereits aktive separat freigegebene Bildfassung erhalten und
deren Bindung über die gemeinsame Quellenprüfung kontrollieren. Die bisherigen
Raster-/Revisionsregeln und unveränderten historischen Freigaben bleiben bestehen.

```sh
python -m tools.puzzle_production.target_adapter plan-update --export <neuer-export> --checkout <checkout> --expected-definition-sha256 <Hash-der-bisherigen-Definition> --difficulty <checked.json>
python -m tools.puzzle_production.target_adapter update --export <neuer-export> --checkout <checkout> --expected-definition-sha256 <derselbe-Hash> --difficulty <checked.json>
```

API: `content_update.update(export_dir, checkout, expected_definition_sha256,
apply=False|True, difficulty=Path(...), rebind_difficulty=False)`. Der Plan ist
lesend, nennt alle geänderten Pfade, vorherige/neue Registry, Revisionen und das
erhaltene alte Paket. Der explizite
Erwartungshash verhindert ein Überschreiben eines inzwischen geänderten Rasters.
Die aktuelle Registry und der neue Export werden vollständig geprüft. Frischer
Staging-Replay, exakte Dateihashes und unveränderte Ausgangsbytes gehen der
Publikation voraus. Die Runtimeprojektion wird zuletzt geschrieben.

Das exklusive `content/.registration-pending.json` verwendet bei neuen Updates
`picross-content-update-journal-v2` nach [SD-C1](SD_CATALOG.md). Alte/neue
UTF-8-Bytes einschließlich Sidecars/Abwesenheit, beide Indizes, Definitionen,
Nutzungshinweise, Kategorien und alle gelesenen Bindungen sind gebunden.
Höchstens 24 MiB Journal; bestehende Paket-/Dateigrenzen bleiben. Normale Fehler
versuchen kontrollierten Rollback. `recover-registration` prüft nach Abbruch
vollständig alte/neue Zustände und erwartet eigene Bytes. Fremdänderungen
blockieren mit erhaltenen Dateien und Journal. Alte Pakete bleiben erhalten.

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

## AT · Getrennte Bildrevision und aktive Bindung

Dieser Abschnitt beschreibt ausschließlich den noch zu implementierenden
[AT-A-Sollstand](REVEAL_TRANSPARENCY.md). Neue reguläre Exporte verwenden weiterhin
die tatsächlich freigegebenen Abschlussbildbytes; transparente PNGs behalten
ihren Alphakanal. Für einen vorhandenen Eintrag ist weder `register` noch der
oben begrenzte Rasterupdateweg ein Ersatz für den neuen Bildupdateweg.

Eine Bildänderung erhält ihre eigene Revision und tatsächliche Freigabe mit
unveränderlichem Alt-/Neubildbezug. Originalhandoffs, Inventare, Exportmanifeste,
kompakte Integrationsbelege und deren ursprüngliche Bildhashes bleiben unverändert.
Die aktuelle zulässige Bildfassung wird separat und eindeutig an die Rätsel-ID
und ihre Herkunft gebunden. Der vollständige Eintragsvergleich alter kompakter
Integrationsbelege bleibt erhalten; eine aktive Bildquelle darf ihn nicht durch
gelockerte Vergleiche umgehen. Ein zulässiger Altstand ohne neue Bildquelle und
eine vorhandene ungültige, veraltete oder widersprüchliche Quelle bleiben
verschiedene Fälle.
Ohne neue Bildquelle gilt die bisherige Originalbindung, bei ungültiger vorhandener
Quelle wird vor Mutation gestoppt und nicht auf einen Altwert zurückgefallen.

P01 schließt den nachfolgenden Datenvertrag vor der AT-A-Codeänderung.
[Kategorien/Projektion](CATEGORIES.md) definiert die gemeinsame Auflösung,
[Transaktionen](SD_CATALOG.md) Journal und Recovery. Inhaltsregistry-v2,
Runtime-v4 mit ihren exakten v2/v3-Lesern und Save-Schema 1 bleiben erhalten;
keine Runtime-v5. Alle neuen Formate sind **Sollstand, noch nicht implementiert**.
Historische Freigaben werden nicht auf neue Bytes umgeschrieben; bereinigte
Produktionspakete werden nicht rekonstruiert.

Der lesende Plan bindet den vollständigen relevanten Ausgangsstand und zeigt
konkrete Bild-/Metadatenänderungen. Die ausdrückliche Übernahme ersetzt nur das
gebundene Bild samt seiner neuen aktiven Bindung. Definitionen einschließlich
Runtime-Revision, Raster, Hinweise, IDs/Keys, Pfade, Save-Slots, Kategorien,
Schwierigkeiten und Hinzugefügt-Daten bleiben bytegleich. Der gemeinsame Lock,
vorab vollständig geprüfte Alt-/Zielzustände, versionierter Binärersatz und
kontrollierter Rollback schützen unterbrochene Übernahmen. Bei fremden Bytes
bleiben Dateien und Journal erhalten; erfolgreiche Recovery endet unmittelbar
in einem gültigen Checkout. Identische Wiederholung ist nur beim vollständig passenden eigenen
Ergebnis ein echter No-op ohne Rewrite, neue Bildrevision oder Journal.

Register, Rasterupdate, Quellenprüfung, Sync, Bewertungs-/Hinzugefügt-Übernahme,
Produktionscleanup und Recovery müssen dieselbe aktive Bildbindung berücksichtigen
und erhalten. Tests verwenden feste synthetische Bilder, Definitionen und Saves.
Die tatsächliche Bestandsfreistellung, motivbezogene Behandlung szenischer Bilder,
Bildfreigaben und neue Bild-/Rasterkonsistenzprüfung gehören anschließend zu AT-B.
Dieser Spezifikationsstand liefert noch keinen ausführbaren zusätzlichen Befehl.

### AT-P01-D01 · Geschlossene aktive Bildquelle

Einzige optionale Autorität ist `content/reveals/<pz-ID>.json`, Format
`picross-catalog-reveal-v1`. Alle hier aufgezählten Schlüssel sind Pflicht und
exakt; zusätzliche/doppelte JSON-Schlüssel, NaN/Infinity, BOM, ungültiges UTF-8,
Surrogate, falsche Typen und boolesche Ganzzahlen sind Fehler auf jeder Ebene.
JSON-Tiefe höchstens 32, numerische Tokens höchstens 16 Zeichen, keine neuen
Fließkommafelder. Unverändert eingebettete historische Difficultywerte behalten
ihre bisher zulässigen endlichen Zahlentypen und werden nicht umgedeutet.
`C(x)` bezeichnet die vorhandenen kanonischen JSON-UTF-8-Bytes mit sortierten
Schlüsseln, kompakten Separatoren und `ensure_ascii=False`, ohne LF/BOM;
`H(x)=SHA256(C(x))`. Dateihash ist dagegen SHA-256 aller tatsächlichen Bytes.
Neue JSON-Dateien sind exakt `C(x)+LF`; JSON-Strings speichern Texte unverändert.
Hashfelder enthalten 64 kleine Hexzeichen, nie null außer ausdrücklich unten.

| Objekt | Exakte Felder und Typen |
| --- | --- |
| Bildquelle | `format,id,record_revision,identity,origin,bindings,revisions,current,record_hash` |
| `identity` | `key,save_slot,definition,reveal,notice`: Strings; Key gleich ID, Slot nach ZA-1; Pfade repositoryrelativ, exakt aus dem registrierten Eintrag hergeleitet: `game/` + Definition/Reveal, Notice mit `.txt` statt Bildsuffix. |
| `origin` | `entry,runtime_revision,notice,receipt`: unveränderliche kompakte Ausgangsbelege. `entry` ist der ursprüngliche vollständig validierte Inhalts-v2-Eintrag mit **Exportmanifesthash** in `production.package_sha256`; `runtime_revision` ist 1…1000000; `notice` folgt unten; `receipt` ist null vor Cleanup oder das vollständig geprüfte ursprüngliche `picross-integrated-content-v1`-Objekt. |
| `bindings[]` | Je exakt `binding_revision,runtime_revision,entry,notice,previous_binding_hash,binding_hash`; Revisionen positive Ganzzahlen, lückenlos ab 1; `previous_binding_hash` nur bei 1 null, sonst Hash des Vorgängers. `entry` wie bei `origin`, jeweils mit ursprünglichem Exportmanifesthash dieser Produktion; `notice` ist die vollständig gebundene historische Exportnotice dieser Bindung. `binding_hash=H(Objekt ohne binding_hash)`. |
| `revisions[]` | Je exakt `image_revision,binding_hash,previous_reveal_sha256,reveal_sha256,notice,approval,provenance,revision_hash`; Bildrevisionen lückenlos ab 1; `binding_hash` verweist auf eine vorhandene Bindung; `revision_hash=H(Objekt ohne revision_hash)`. |
| `current` | Exakt `binding_revision,image_revision`; beide gleich letzter Listenrevision. |
| `notice` | Exakt `text,sha256`; Text ist vollständiges UTF-8/LF-Notice ohne BOM/NUL, 1…65536 Dateibytes, endet LF; Hash bindet `text.encode('utf-8')`. |
| `provenance` | Exakt `author,usage_basis,source,changes`; je nichtleerer String, 1…4096 Unicodezeichen, kein Randwhitespace, keine C0/C1-Steuerzeichen. `source` ist eine gespeicherte Herkunftsbeschreibung, kein automatisch zu öffnender Pfad/URL. |

`entry` ist kein Erweiterungsobjekt: exakt
`id,key,save_slot,definition,reveal,visible,category_id,production`;
`production` exakt `package,package_sha256,revision,width,height,mode,difficulty,status,blockers,test_only,definition_sha256,reveal_sha256`.
Typen, sichere Pfade und Limits folgen dem unveränderten Inhalts-v2-Vertrag.
`difficulty` ist allein ein **unveränderter historischer Beleg** unter dessen
bisheriger validierter Semantik, kein neues freies AT-Metadatenobjekt und keine
aktive Bewertung. Es wird vollständig aus dem geprüften Original übernommen
und bei Wiederverwendung bytekanonisch verglichen, niemals vom Bildupdateinput
vorgegeben oder um neue Felder ergänzt. Ebenso folgt `receipt`, wenn vorhanden,
exakt seinem vierfeldrigen Altvertrag; sein `entry` muss `origin.entry` gleichen,
sein `notice_sha256` der ursprünglichen Notice. Seine kanonischen Bytes und der
physisch aktuelle Receipthash werden getrennt geprüft. Ein vor Cleanup angelegtes
`origin.receipt=null` bleibt auch danach null: `entry` und vollständige Notice
halten den notwendigen kompakten Beleginhalt bereits selbständig fest.

`origin.entry` ist bei erster Bildrevision die aktuelle Produktionsbindung,
normalisiert ausschließlich am Pakethash: Exportmanifesthash bei vorhandenem
Export, sonst `receipt.entry.production.package_sha256`. Die physische
Manifestdatei muss gleichzeitig gegen den aktuellen Registryhash passen.
`bindings[0].entry/runtime_revision/notice` gleichen `origin`. Identität und ID stimmen
über alle Bindungen überein. Keine Bindung an Git-HEAD oder Registrygesamthash.
Bei jeder Folgebindung ist die Runtime-Revision streng höher, die Paketrevision
neu. Bildrevisionen referenzieren vorhandene Bindungen in nicht abnehmender
Reihenfolge; die erste referenziert Bindung 1, jede neue die dann aktuelle.
Alle historischen Notices der Bindungen bleiben erhalten und gegen ihre
Produktionsbelege geprüft; die erste aktive Notice erhält bereits `origin.notice`
vollständig als Präfix. Nach einem Quellen-Rebind darf eine neue Exportnotice
keine bisherige aktive Attribution entfernen oder ihre Bedeutung ersetzen.

`record_revision` ist 1…1000000 und genau
`len(revisions)+len(bindings)-1`. `record_hash=H(Quelle ohne record_hash)`.
Listen enthalten jeweils 1…256 Einträge; jede neue Revision/Bindung überschreitet
weder Zähler noch Dateilimit. Quelle höchstens 1 MiB; bis 10000 registrierte
ID-Dateien. Kein Abschneiden alter Historie zur Umgehung eines Limits.

Erste Bildrevision: Vorgängerhash gleich `origin.entry.production.reveal_sha256`;
weitere: gleich dem unmittelbar vorigen `reveal_sha256`. Neuer Bildhash muss
verschieden sein; eine bloße Freigabe-/Noticeänderung ist kein Bildwechsel.
Jede Revision bindet die **damals** aktuelle Definition über `binding_hash` und
die Freigabe. Frühere Revisionen bleiben bei späterem Quellen-Rebind unverändert.
Die effektive Notice ist die letzte `notice`, der effektive Bildhash der letzte
`reveal_sha256`. Notice einer Folgerevision erhält alle bisherigen Noticebytes
als Präfix; neue Attribution wird nur angehängt. Ohne Ergänzung bleibt sie exakt.

### AT-P01 · Tatsächliche Freigabe

`approval` enthält exakt `format,id,image_revision,definition_sha256,previous_reveal_sha256,reveal_sha256,notice_sha256,actor,timestamp_utc,statement,checks,test_only`.
Format ist `picross-reveal-approval-v1`; ID/Bildrevision/Hashes stimmen mit Revision,
damaliger Bindung und vollständiger Zielnotice überein. `actor` hat 1…128,
`statement` 1…4096 Zeichen, beide nichtleer, ohne Randwhitespace/C0/C1.
`timestamp_utc` ist ein existierender Zeitpunkt `YYYY-MM-DDTHH:MM:SSZ`, Jahr
0001…9999, ohne Offset, Bruchteil oder Schaltsekunde. `checks` enthält exakt
`reveal_approved,motif_raster_consistent,final_editorial_approved`, jeweils `true`;
die tatsächliche Erklärung muss alle drei Entscheidungen für die gebundenen
Bytes dokumentieren. `test_only` ist Boolean und stimmt mit der Produktion
überein. Synthetische Freigaben dürfen nie im echten Checkout übernommen werden.
Keine Softwareauthentifizierung des Akteurs und keine Freigabe durch Hash oder
`true` allein. Materielle Motiv-/Rasteränderung ist außerhalb dieses reinen Wegs.

### AT-P01-D03 · Rebind und erhaltene Herkunft

Beim reinen Bildwechsel sind `origin,identity,bindings` exakt unverändert;
genau eine Bildrevision wird angehängt, `current.image_revision` und
`record_revision` steigen um 1, der Recordhash wird neu berechnet.
Bei der ersten Revision wird die Hülle aus dem vollständig geprüften Altstand
gebildet. Es gibt weder einen vorab leeren Record noch eine Bildrevision 0 darin.

Späterer Rasterupdate darf ausschließlich **genau das effektive aktive Bild**
exportieren. Sein Export, dessen echte Freigaben und SD-Eingang bleiben vollständig
ZA-1-geprüft. Der Vergleich erfolgt gegen den aktiven Hash, nicht gegen den
ursprünglichen `production.reveal_sha256`. Neue Paketrevision und höhere
Runtime-Revision bleiben Pflicht; alte Pakete bleiben erhalten. Die neue
Registryproduktion darf daher den schon aktiven Hash als ihren eigenen
historischen Exportbildhash führen. Das ist keine Änderung des alten Belegs.

In derselben Update-v4-Transaktion wird genau eine `bindings`-Zeile mit neuer
Definition/Produktion und Vorgängerhash angehängt; `current.binding_revision`
und `record_revision` steigen um 1. `origin`, alle Bildrevisionen und deren
Freigaben, aktive Bild-/Noticebytes sowie Added bleiben bytegleich. Das neue
Exportbild muss der letzten Bildrevision entsprechen. Die alte Bildfreigabe
beansprucht weiterhin nur ihre damalige Definition; die neue Rasterfreigabe
steht im neuen Export. Kein kombinierter Bild-/Rasterwechsel, kein Rebind aus
einer bloß ähnlichen Definition. Ohne AT-Quelle gilt der bisherige Updatevertrag.

Cleanup ändert ausschließlich seine bisher erlaubten Produktions-/Indexdaten.
Der kompakte Receipt erhält die **historische Produktionsnotice**, nicht eine
nach AT ergänzte Live-Notice. Manifest-/Receiptprüfung und aktiver Noticevergleich
werden nach [Auflösung](CATEGORIES.md) getrennt. Alle AT-Bytes bleiben erhalten;
ein anderer physischer Manifesthash ist kein Quellen-Rebind und keine Bildrevision.
Vor/nach Cleanup liefert der stabile Exportanker denselben Wert. Erste und
weitere Bildrevision funktionieren in beiden Zuständen ohne Produktionsrekonstruktion.
Die Main-/Arbeitsbaumprüfung des Cleanup bleibt vollständig; sie prüft zusätzlich
die aktive Quelle und Bild-/Noticebytes am ausdrücklich bestätigten integrierten
Stand. Unveröffentlichte AT-Änderungen werden nicht als integriert ausgegeben.

Historisch identisches `register` nach AT: den geprüften Eingang vollständig mit
dem normalisierten aktuellen Produktionseintrag vergleichen, anschließend
aktiven Checkout und vollständigen Snapshot erneut prüfen. Historisches Bild und
Notice werden nur im Eingang geprüft, nie über Live-Bytes geschrieben. Ergebnis
echter No-op vor Journalanlage, ohne neue SD-/Added-/AT-Revision. Eine frühere
Produktion nach einem tatsächlichen Rasterupdate ist dagegen kein No-op.

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

## KU-B · Erstregistrierung und kompatible Metadaten

Die [Added-Quelle](CATALOG_SORTING.md) liegt außerhalb versiegelter Pakete.
Ein nur lesender Registrierungsplan erzeugt keinen Zeitpunkt. Erst die mutierende
Erstregistrierung erzeugt genau einmal UTC in ihrem Journal; der Zeitpunkt wird
nur zusammen mit der erfolgreich spielbaren Registrierung dauerhaft. Rollback
entfernt die eigene neue Quelle. Wiederholung, Update, Reveal-/Kategorieänderung,
Sync und Recovery bewahren den vorhandenen Record bytegenau; ein alter fehlender
oder null-Wert wird niemals durch die aktuelle Zeit ersetzt.

Alle diese Wege verwenden den gemeinsamen [Transaktionsvertrag](SD_CATALOG.md).
Neue Runtimeprojektionen sind v4; alte v2/v3 und ihre exakt abgegrenzten Journale
bleiben nach den dortigen Kompatibilitätsregeln rückführbar. Keine Änderung an
ID, Save-Slot, Rätseldefinition, Bewertung oder historischer Produktionsbindung
allein zur Einführung von Hinzugefügt-Metadaten.
