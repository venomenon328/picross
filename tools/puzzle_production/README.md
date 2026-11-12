# RP-1 bis RP-5: Deduktionskern, Bildproduktion und Reparatur

## PE-A1: aktuelle Namen und Kategorien

[`metadata_cli`](metadata_cli.py) pflegt vorhandene registrierte IDs gemäß
[PE-A1](../../docs/PUZZLE_EDITOR.md#7-pe-a1-geschlossener-metadatenvertrag).
Aktuelle Namen und Kategorien stehen in Inhaltsregistry v4; Runtime v7 ist die
geprüfte Projektion. Definitions-/Bildbytes, Rasterrevisionen, Ratings, Added und
historische Produktionsbelege werden bei dieser Pflege nicht neu geschrieben.
Die gemeinsame API liegt in [`catalog_metadata`](catalog_metadata.py).

Alle Aufrufe laufen vom Repositoryroot. `CHECKOUT` ist der explizite lokale
Zielcheckout. Plan-/Operationsdateien sind UTF-8-JSON. `--output` schreibt eine
neue Datei außerhalb des Zielcheckouts als UTF-8 ohne BOM und überschreibt
keine vorhandene Datei; ohne diese Option steht das JSON auf stdout.

```text
python -m tools.puzzle_production.metadata_cli view --target-root CHECKOUT
python -m tools.puzzle_production.metadata_cli plan-migration --target-root CHECKOUT --output MIGRATION.json
python -m tools.puzzle_production.metadata_cli apply --target-root CHECKOUT --plan MIGRATION.json
python -m tools.puzzle_production.metadata_cli plan --target-root CHECKOUT --operations OPERATIONS.json --output PLAN.json
python -m tools.puzzle_production.metadata_cli apply --target-root CHECKOUT --plan PLAN.json
python -m tools.puzzle_production.metadata_cli recover --target-root CHECKOUT
```

`view` ist lesend und zeigt alle aktuellen Autorenmetadaten. Eine v4-Ansicht
öffnet nur Registry und Kategorienquelle. Die API `MetadataView(root)` baut
einmal die ID-Zuordnung auf; `lookup(id)` und `document()` liefern anschließend
abgetrennte Speicheransichten ohne weitere Datei-, Bild- oder Proofzugriffe.

Die explizite Migration validiert v2/v3 und schreibt ausschließlich die beiden
Registrydateien. Ein bereits gültiger v4/v7-Bestand bleibt unverändert. Normale
mutierende Writer verlangen danach v4/v7 und migrieren nicht nebenbei. Alte
gebundene Journale zuerst über ihren gemeinsamen Recoveryweg auflösen.

Eine Operationsdatei enthält eine Liste. Beispiel mit einer zuvor aus `view`
gelesenen ID und aktuell vorhandener Kategorie:

```json
[
  {"op": "set_metadata", "id": "pz-beispiel", "name": "Neuer Motivname", "category_id": "voegel"}
]
```

`set_metadata` verlangt mindestens Name oder Kategorie. Weitere Operationen
sind `category_create` mit `name`, `category_rename` mit `id,name` sowie
`category_delete` mit `id` und optionalem `reassign_to`. Der Plan vergibt bei
Kategorieanlage eine stabile ID und hängt den internen Ordnungswert an.
Eine belegte Kategorie kann nur mit einer anderen vorhandenen Ersatzkategorie
gelöscht werden; sämtliche betroffenen Rätsel werden in derselben Transaktion
neu zugeordnet. Ihre historischen Kategorieangaben bleiben erhalten.

Planen schreibt keinen Inhalt. Vor Übernahme `changes` und `files` prüfen;
die Übernahme bindet auch die unveränderten Quellen und deren Abwesenheiten.
Eine zwischenzeitliche Bearbeitung verlangt einen frischen Plan. Identische
aktuelle Werte ergeben beim erneuten Planen einen No-op ohne neue Bytes oder
mtimes. Offene Journale/Locks verhindern auch einen konkurrierenden No-op.
Recovery stellt den vollständigen alten Zustand wieder her und schützt fremde
Änderungen. Es gibt keine zusätzliche Metadatenhistorie oder freie Registry-API.
Rückgabecodes: 0 erfolgreich, 2 ungültiger Eingang/Konflikt, 4 Ressourcenabbruch.
Raster-/Bildpflege und eine Weboberfläche gehören zu späteren PE-Paketen.

## #596/C · Feste Rasterableitung

Der vor Code festgelegte [Vertrag](../../docs/FIXED_RASTER.md) definiert die
geschlossenen Parameter-/Plan-/Record-/Manifestformen und deren Grenzen.
`python -m tools.puzzle_production.fixed_raster derive --root ROOT --plan PLAN --output OUT`
erzeugt das reguläre Bundle; `inspect --root ROOT --bundle BUNDLE` prüft es frisch.
Authoring 0.8.0 Dokumentrevision 4: source_type=fixed, kein manueller Override.
Aktive Schwierigkeit zusätzlich über catalog_analysis mit expliziter Methode 0.4.


**PW-B · 0.8.0, 11.11.2026:** Für neue Produktionen gilt der
[fünfstufige Authoringweg](../../docs/ai-workflows/PUZZLE_AUTHORING.md) mit dem geschlossenen
[PW-B-Datenvertrag](../../docs/PW_B_CONTRACT.md). Hintergrundbriefing, drei Kandidaten und
Auswahl beginnen erst nach der ausdrücklichen qualifizierten Rasterwahl in Schritt 4.
Frühe Hintergrundpflichten sowie 0.6-Default/0.7-Opt-in-/Offline-Sheetbeschreibungen
weiter unten bezeichnen ihre alten Generationen und gelten nicht für neue 0.8-Jobs.
Bestehende Inhalts-, Proof-, Paletten-, Bild-, Freigabe- und Integrationsgarantien
bleiben erhalten. Der Dienst bleibt lesend; Veröffentlichung und Gitabschluss
führt der beauftragte Akteur aus. Historische Originale werden nicht migriert.

## PW-B: neue Produktion 0.8.0

Build v3 veröffentlicht Handoff v4/Record v3 und die automatisch geprüfte
workspace.json gemeinsam mit der Revision im expliziten Repositoryziel.
[#596/B](../../docs/PRODUCTION_CURRENT_VIEW.md) ergänzt den gemeinsamen
`current-view.json`-Übergabeschritt für Builder, Finalizer, Projektor und Completion.
Den Pointer samt aktuellen Record-/Projektionsbytes im selben Handoffcommit
sichern/pushen und Remotezugriff prüfen; unterbrochene Aufrufe identisch vollständig
wiederholen. Für bestehende vollständige 0.8-Arbeit gezielt
`python -m tools.production_workspace.projector --repository <checkout> --current-view <pz-ID> <revision>`
aufrufen. Kein HTTP-Writer und keine Änderung versiegelter Originale.
Request v3 ergänzt `presentation={title,raster_offers}`. Frühe background- und
raster_selection-Felder sind null. Erst die gebundene menschliche Rasterwahl
öffnet background_review. Finalizer v2 aktualisiert den bestehenden Record v3
und die zugehörige Projektion; keine alten Originalbytes werden verändert.
Die vollständigen neuen Formen, Beispiele und Aufrufe stehen in
[PW-B](../../docs/PW_B_CONTRACT.md) und [Authoring §§6–8](../../docs/ai-workflows/PUZZLE_AUTHORING.md).
Alle folgenden älteren formatgebundenen CLIs bleiben unter ihren ursprünglichen
Grenzen verfügbar; der neue reguläre Bedienweg ist der lokale Assistent.


## BA-A: lokale Batchverarbeitung und Wiederaufnahme

[`batch_cli`](batch_cli.py) verarbeitet ausdrücklich vorbereitete Jobs seriell.
[PRODUCTION_BATCH](../../docs/PRODUCTION_BATCH.md) beschreibt die vollständigen
geschlossenen Formen, festen Operationen, Entscheidungen, Budgets und Zustände;
maßgeblich ist [BA-A / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6779908657).
Die Befehle laufen im Repositoryroot mit Python aus der isolierten
[Bildumgebung](#rp-3-isolierte-image-umgebung-und-reale-befehle), Pillow exakt 12.3.0:

```text
python -m tools.puzzle_production.batch_cli validate --plan <plan.json> --source-root <quellen> --repo-root <checkout>
python -m tools.puzzle_production.batch_cli run --plan <plan.json> --source-root <quellen> --work-root <neuer-leerer-root> --repo-root <checkout>
python -m tools.puzzle_production.batch_cli resume --plan <plan.json> --source-root <quellen> --work-root <eigener-bisheriger-root> --repo-root <checkout>
python -m tools.puzzle_production.batch_cli status --work-root <eigener-bisheriger-root>
```

Die API `validate/run/resume/status` liegt in `batch_runner`. Ein ausdrücklich
angegebener `--history-root` wird nur lesend vom vorhandenen lokalen Builder
verwendet. Plan-/Werkzeug-/Dateibindungen müssen aktuell sein; ein Nachfolgeplan
bindet die exakten Vorgängerbytes und erhält sämtliche verbrauchten Versuche.
`run` braucht einen neuen leeren Root außerhalb von Quellen und Checkout.
`resume` prüft frühere Ausgaben mit einem eigenen begrenzten Prüfversuch neu.
`status` bleibt lesend und kennzeichnet den Bericht mit `fresh=false`.

Ein fehlender menschlicher Entscheid wartet als `waiting_human`, ein noch nicht
gelieferter vollständiger Bauauftrag als `waiting_input`. Unabhängige Zweige
laufen weiter. Paketbau verwendet ausschließlich `target=local` und
`publish_to=None`; der technische Abschluss enthält keine Inhaltsfreigabe.
Ein Exit 0 kann einen korrekt geprüften stalled-/Widerspruchsbefund enthalten.
Vorhandene fachliche Status und Zertifizierungen bleiben im Bericht getrennt.

## BA-B: autorisierte serielle Einzelintegration

[`integration_batch_cli`](integration_batch_cli.py) verarbeitet ausschließlich
vollständig vorbereitete und tatsächlich autorisierte Integrationsjobs.
[PRODUCTION_BATCH](../../docs/PRODUCTION_BATCH.md) schließt Plan, Checkpoint,
Bericht, Phasen und Wiederaufnahmefälle; maßgeblich ist
[BA-B / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6782256272).
BA-A bleibt der getrennte lokale Produktionsrunner. Die folgenden Befehle laufen
im Werkzeugcheckout mit Python aus der isolierten Bildumgebung und Pillow
exakt 12.3.0:

```text
python -m tools.puzzle_production.integration_batch_cli validate --plan <batch-plan.json> --source-root <vorbereitete-quellen> --repo-root <werkzeugcheckout> --target-root <zielcheckout>
python -m tools.puzzle_production.integration_batch_cli run --plan <batch-plan.json> --source-root <vorbereitete-quellen> --repo-root <werkzeugcheckout> --target-root <zielcheckout> --work-root <noch-nicht-vorhandener-root>
python -m tools.puzzle_production.integration_batch_cli resume --plan <batch-plan.json> --source-root <vorbereitete-quellen> --repo-root <werkzeugcheckout> --target-root <zielcheckout> --work-root <eigener-bisheriger-root>
python -m tools.puzzle_production.integration_batch_cli status --work-root <eigener-bisheriger-root>
```

API: `integration_batch_runner.validate/run/resume/status`. `validate` darf
zusätzlich `--work-root` erhalten und bleibt lesend; es bestätigt Form, erreichbare
gebundene Eingänge und aufgezeichnete Autorisierung, keine Inhaltsfreigabe oder
ausgeführte Integration. Ein optionaler `--history-root` lokalisiert ausschließlich
den ausdrücklich vorhandenen lesenden Gitkontext des nativen Exports. Kein Fetch
oder Erraten von Quellen. Werkzeug- und Zielcheckout dürfen identisch sein;
Arbeits-/Ausgabebereiche bleiben von Eingängen und aktiven Zielbäumen getrennt.
`run` verlangt einen noch nicht vorhandenen eigenen Arbeitsroot, `resume` dessen bestehende
unveränderte Buchführung. `status` ist ausschließlich historisch mit `fresh=false`.

| Job | Vollständiger Eingang und native Folge |
| --- | --- |
| `register` | Originalpaket samt tatsächlicher Endfreigabe, benötigten äußeren Dateien, manuellen Autorisierungen/Palettenausnahme und geprüftem Difficultyinput. `target_adapter.export` prüft seinen Eingang und geschriebenen Export vollständig; anschließend unmittelbar `content_registry.registration(apply=False)` und autorisiert `apply=True`. Kategorie, Parameter und gegebenenfalls erlaubtes Difficulty-Rebind sind ausdrücklich gebunden. |
| `background_adopt` | Byteidentischer `picross-background-adoption-request-v1` samt vollständigem Inventar seiner Arbeitsdateien und tatsächlichem Bildänderungsauftrag. Native Folge `catalog_background_change.store → plan → adopt`; unveränderte Ziel-/Source-/Capability- und HP-W2-Prüfungen. |

`register.authorization` bindet einen bereits vorbereiteten
`picross-integration-order-v1` mit Ref auf die tatsächliche ursprüngliche
Auftragserklärung; Endfreigabe bleibt ein eigener nativer Eingang. Bei
`background_adopt` ist die Autorisierungsref exakt die Ref des unveränderten
Requests. Der Runner erzeugt oder ergänzt keine dieser Erklärungen.

Ein bereits vorbereitetes lokales Rasterpaket benötigt weder einen zusätzlich
erfundenen Authoring-Store noch einen vorherigen Finalizerlauf. Für den
Hintergrundwechsel bleibt die native reale Arbeits-/Indexablage dagegen Pflicht.
Keine routinemäßigen zusätzlichen `inspect`-/`verify-export`-Runden;
`registration(apply=True)` erzeugt selbst einen aktuellen nativen Plan und
übernimmt keinen Prüfbeweis aus dem vorangehenden lesenden Aufruf.
Ein vollständig bestätigter nativer Plan-No-op beendet den Job ohne
mutierende Wiederholung.

Der kooperative Batchlock bindet den kanonischen Zielcheckout, auch bei
verschiedenen Arbeitsroots. Native Locks und Journale bleiben zuständig.
Der erste ungeklärte Fehler, Teilstore, offene Journal-/Stagingrest oder unsichere
native Abschluss stoppt die ganze Auswahl. Bereits erfolgreiche Jobs bleiben;
kein Batchrollback, automatische Wiederholung, Locklöschen oder Recoverykommando.
Erforderliche native Recovery gesondert autorisiert ausführen, danach `resume`.

Resume unterscheidet nativ publizierten, noch ungebuchten Registererfolg
(frisches lesendes natives No-op), entsprechend ungebuchte Bildadoption
(ursprüngliches Planbundle mit Pythonoption `adopt(..., no_op_only=True)`) und
bereits gebuchte Erfolge nach späteren erfolgreichen Jobs. Für den letzten Fall
einmal den heutigen vollständigen Katalog prüfen und erreichte jobbezogene
Bindungen abgleichen; alte stale Bildpläne nicht erneut adoptieren. Die additive
Pythonoption darf ausschließlich den vollständig eigenen nativen No-op liefern
und weist erforderliche Mutation im selben Kontrollfluss zurück. Sie führt
keinen neuen nativen CLI-Befehl ein und lockert keinen Plan-/Retirementvertrag.

Vor jeder Phase wird der endliche Versuch dauerhaft reserviert; auch ein harter
Abbruch verbraucht ihn. Planfortschreibung, Umbenennen oder neuer Root setzen
die Versuchslinie nicht zurück. Export/Plan/Authoring behalten ihre nativen
300-s-Teilgrenzen; neue Registrierungspublikation und ihre Recovery getrennt
je 1800 s mit zulässigen vorab festgelegten Overrides und 300-s-Warnung.
Hintergrundplan/-adoption/-recovery bleiben jeweils bei 300 s. Der Runner läuft
synchron im CLI-Prozess; Recovery erhält ihren eigenen Rahmen.
Native Ergebnisse/Exits und das vom Runner beobachtete reale RI-Diagnoseobjekt
bleiben im Bericht getrennt. Das gilt auch für Aufrufe ohne eigene native
CLI-Diagnostik; inklusive Phasenzeiten nicht addieren, unbekannte Zeiten null.
Batch-Exit 0 bedeutet vollständig frisch bestätigt,
2 ungültigen Eingang, 3 unvollständigen Lauf, 4 Abbruch, 5 technischen Fehler.

Batchabschluss belegt den Zielcheckout; `status` ist keine neue Zielprüfung.
Gitabschluss und spätere Main-gebundene Bereinigung folgen weiterhin Authoring
§§8–9. Der Runner erzeugt keine Entscheidungen/Freigaben, führt keine Gitaktionen,
Retirement-, Rasterupdate- oder Revealadoptionsoperation aus. Aktiver Default
0.6.0 und ausdrückliches 0.7.0-Opt-in bleiben erhalten.

## HP-W2: eigenständige Hintergrundableitung

[`background_assets`](background_assets.py) stellt die lokale API/CLI für die
Arbeits-, Entscheidungs-, Auftrags- und Befundformen aus
[PUZZLE_BACKGROUNDS §§3–4](../../docs/PUZZLE_BACKGROUNDS.md) bereit. Maßgeblich
ist die [Paketentscheidung HP-W2](https://github.com/venomenon328/picross/issues/560#issuecomment-6748799473).
Sie verarbeitet gespeicherte ausgewählte PNG-Bytes oder eine tatsächliche
ausdrückliche Leerentscheidung. Die API erzeugt keine Kandidaten und trifft
keine Auswahl. Noch ungeklärte Rechte und ausstehende Sichturteile bleiben
auch nach erfolgreicher technischer Vorbereitung offen.

Die folgenden Aufrufe verwenden `python` aus der
[isolierten Bildumgebung](#rp-3-isolierte-image-umgebung-und-reale-befehle) mit
**Pillow exakt 12.3.0** und starten im Repositoryroot:

```text
python -m tools.puzzle_production.background_assets describe
python -m tools.puzzle_production.background_assets derive --request <request.json> --source-root <quellen> --output-root <ausgaben>
python -m tools.puzzle_production.background_assets verify --request <request.json> --source-root <quellen> --output-dir <befundordner>
```

API: `describe()`, `derive(request, source_root, output_root)` und
`verify(request, source_root, output_directory)` aus
`tools.puzzle_production.background_assets`. `describe` liefert das vollständige
feste Profil, dessen kanonischen Hash und den tatsächlichen Tool-/Codecstand
samt Hash. Dessen `dirty` bezieht sich auf Abweichungen der tatsächlich verwendeten
eigenen Module vom gebundenen Gitcommit. Für einen neuen Auftrag diese Werte verwenden; ein abweichender
`expected_tool_sha256` wird vor dem Schreiben zurückgewiesen.

Der geschlossene `picross-background-derive-request-v1` bindet das
`picross-background-work-v1`-Manifest, die `picross-background-decision-v1`-
Entscheidung und bei `selected` das genaue Original über Pfad, Bytezahl und
Dateihash. Sein `profile` ist das vollständige Profil aus `describe`, `output`
ein neuer relativer Verzeichnisname unter dem Ausgabe-Root. Die beiden Roots
müssen bereits existieren, explizit gewählt, sicher und voneinander getrennt
sein; aktive Spiel-/Katalogziele sind ausgeschlossen. Sämtliche benötigten
Quellen/Belege liegen unter genau einem `source_root` mit unveränderten
relativen Pfaden. ZIP-Entpacken, `StoredRef`-Paketauflösung oder Beschaffen
fehlender Dateien gehören nicht zu diesem Werkzeug.

`derive` prüft die vollständigen Formen und die tatsächlich benötigten
Referenzen frisch. Nur das gewählte Original wird dekodiert und nach
`picross-background-png2304-v1` proportional auf 2304×576 RGBA/sRGB eingepasst,
mit gemeinsamem unteren mittigen Anker, vormultipliziertem Lanczos und
transparentem Rest. Keine individuellen Crop-/Masken-/Positionsparameter.
Im neuen Ausgabeordner entstehen ausschließlich `derivation.json` und bei
`selected` `background.png`. Gültiges `none` erzeugt nur den Befund; ein früher
Verzicht auf die Kandidatenproduktion braucht zusätzlich den tatsächlichen
Eigentümerbeleg. Fehlende, offene, abgelehnte oder fehlerhafte Eingänge werden
nicht als Leerentscheidung ausgegeben.

`verify` erhält den tatsächlichen Befundordner, liest Eingänge und Ergebnis
erneut, reproduziert die Ausgabe und verändert keine Quellen oder Resultate.
Der vollständige ursprüngliche Request steht in `derivation.json.request`;
ohne ursprüngliche Requestdatei darf die CLI dieses exakte Objekt aus einer
eigenen temporären Datei verwenden. Transportierte Ergebnisordner bleiben
prüfbar, solange die erforderlichen unveränderten Quellen erreichbar sind.
Lesendes `verify` prüft originale Request-/Befund-/Toolhashes strikt, verlangt
aber nur für `id`, vollständige `versions` und die exakte Modulpfad-/Bytehashmenge
Gleichheit mit dem aktuellen Werkzeug. Originales `commit/dirty` bleibt
Erzeugerherkunft; ein späterer reiner Contentcommit macht gleiche ausführbare
Bytes nicht ungültig. Ausgabe und vollständigen Befund mit dem ursprünglichen
Toolobjekt reproduzieren; geladene/gespeicherte Module und Eingänge müssen dabei
unverändert bleiben. Echte Modul-/Codec-/Profiländerung bleibt `tool_mismatch`.
`derive` einschließlich `reused` verlangt weiterhin den **vollständigen aktuellen**
`expected_tool_sha256`. Keine Umschreibung alter Befunde oder Freigaben.

`derive` und `verify` liefern genau `{status,derivation,output,error,remaining}`;
Refs in erfolgreichen Antworten sind relativ zum Befundordner. Exit 0 mit
`derived|none|reused|verified` bezeichnet nur technischen Erfolg, Exit 2
ungültige Eingänge oder Konflikte, Exit 4 Abbruch und Exit 5 technischen Fehler.
Stdout enthält genau ein JSON-Objekt, Diagnose steht auf stderr. Exakte
Wiederholung wird nur nach frischer Prüfung als `reused` übernommen und erhält
Bytes/mtimes; fremde, leere oder unvollständige Zielordner bleiben Konflikte.
Bei Fehlern melden `error` die konkrete Ursache und `remaining` einen tatsächlich
verbliebenen eigenen Restpfad oder null. Ressourcen-, Fehlercode-, Lock- und
Veröffentlichungsvertrag stehen vollständig in Hintergrundvertrag §4.4.

**Der Produktionsdefault bleibt 0.6.0.** Authoring 0.6.0 und PB-A
behalten ihre Hüllen und Gates. PB-H ergänzt den ausdrücklich gewählten
Paketbau und die lesende Inhaltsprüfung unten; HP-I1a ergänzt äußere
Fortschreibung und Export v6. HP-I1b1 ergänzt zielgebundene Erstregistrierung
und ersten Abschluss. Die echte Capability folgt dem HP-I2-Runtime-/Abnahmevertrag.
Späterer reiner Hintergrundersatz folgt dem HP-I1b2-Weg, erlaubte Raster-/
Revealneubindung vorhandener Hintergrundziele HP-I1c. MJ-A führt den regulären
Sheetweg; MJ-B ergänzt den eigenen Hintergrundänderungsjob nach §7.6. Die Standalone-
Fähigkeit allein liefert keinen Hintergrundersatz im Spiel oder Produktionsabschluss.

## PB-H: Hintergrundpakete und lesende Inhaltsprüfung

[Paketentscheidung #489/PB-H](https://github.com/venomenon328/picross/issues/489#issuecomment-6751071312)
und [Hintergrundvertrag §§2–8](../../docs/PUZZLE_BACKGROUNDS.md) legen die
neue geschlossene Generation fest. Sie verwendet ausdrücklich den vollständigen
[Authoring-0.7.0-Vorschausnapshot](../../docs/ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md),
Dokumentrevision 9, mit tatsächlichem Dateihash und gelesenem Quellencommit.
Der aktive Authoringpfad und der Default neuer Offline-Sheetjobs bleiben
**0.6.0 / Dokumentrevision 48**. Beide eingebetteten Snapshots entsprechen ihren
Markdownquellen; 0.7.0 / Dokumentrevision 9 bleibt ausdrücklich opt-in. Die
verpflichtende Gesamtaktivierung wird am konkreten Einzelweg in #560 abgeglichen.
Versiegelte ältere Pakete behalten ihren gebundenen Snapshot unverändert.

```sh
python -m tools.puzzle_production.authoring_builder build --request <request-v2.json> --source-root <quellen> --output-root <arbeitsordner> [--publish-to <checkout>] [--history-repo <lokaler-checkout>]
```

API: `authoring_builder.build(request, source_root, output_root, publish_to=None,
history_repo=None)`, wobei `history_repo` nur als benannter Parameter übergeben
wird. `picross-authoring-build-request-v2` behält exakt die acht v1-Schlüssel
`format,handoff,document_revision,files,target,category_id,reveal_options,external`.
`handoff` ist unversiegeltes `picross-authoring-handoff-v3` mit Regelwerk 0.7.0,
`inventory=null`, vollständigen zwölf `gates`/`gate_evidence` und zusätzlichem
`background={manifest,decision,derivation,history}`. Die neuen Gates heißen
`background_choice` und `background_asset`. Die übrigen Felder und die
`files`-Einträge `{path,source,sha256,bytes}` behalten ihren Vertrag. Die äußere
Dateimenge bleibt `approval.json`, `manual-authorization.json`,
`owner-override.json`, `palette-exception.json`; vorhandene Endfreigabe ist v2.
Unbekannte Felder/Formate sind Fehler, keine erweiterbare Metadatenhülle.

| Neue Bauphase | Fällige Prüfung |
| --- | --- |
| `brief_ready`, `reveal_review` | Bisherige frühe Bild-/Dateibindungen plus tatsächliches Arbeitsmanifest; offenes Briefing bleibt offen. |
| `motif_review` | Freigegebenes Reveal, Motivvorlage und drei tatsächlich gesicherte Hintergrundangebote; abweichende Zahl oder frühes `none` braucht die gebundene Eigentümererklärung. |
| `motif_approved`, `raster_review` | Motiv-/Parameterfreigabe und vorhandene Kandidatenbindungen; offene, vorgelegte oder abgelehnte Hintergrundwahl stoppt unabhängige autorisierte Rasterarbeit nicht. |
| `raster_ready` | Vollständige bisherige 0.6.0-Inhaltsprüfung am geschriebenen ZIP, einschließlich frischer Palette/Norm/Sichtung, Proof/Paarbaseline, Herkunft, Parametern, Randregel und Difficulty. Nur Hintergrundbereitschaft und Endabnahme dürfen fehlen. |
| `content_ready` | Zusätzlich gültige Auswahl mit geklärten Rechten, konkreten Q-HG-Urteilen und frisch geprüfter HP-W2-Ableitung oder tatsächlich erklärtes `none` mit Nullbefund. Nur Endabnahme bleibt gegebenenfalls offen. |

Der Builder erhöht keine Phase und erzeugt keine menschliche Erklärung. Neue
Originale mit `editorially_approved`, `catalog_ready` oder `registered` sowie
bereits versiegelte Eingänge werden nicht gebaut. `final_editorial` und
`target_export` bleiben im Originalhandoff offen; tatsächlich schon vorhandene
separate Belege werden ausschließlich gelesen.

`background_package` löst typisierte Referenzen mit getrennten Paket-, Manifest-,
Entscheidungs-, Befund- und Historywurzeln auf. Innere Pfade, Bytes und Hashes
bleiben unverändert; nur äußere `StoredRef={storage,root,ref}` lokalisieren sie.
`norm.file` und Toolmodulpfade binden Quellcode/Normstand, keine Paketpayloads.
Es gibt keine automatische Dateisuche, Rootvermutung oder Netzbeschaffung.
Sichere Pfade, Windows-/Casefoldaliase, Datei-/Ordnerkonflikte und Links werden
an der vollständigen Referenzmenge geprüft. Ein verschachtelter, gebundener
HP-W2-Befund `derivation.json` ist erlaubt; Authoring-Teilkopie im Root,
ZIP-Verschachtelung und Neuversiegelung bleiben ausgeschlossen.

Vor Auswahl enthält das Paket alle angebotenen Originale und Belege. Nach
Auswahl darf es ausschließlich verworfene Kandidatendateien weglassen, wenn
`history` die frühere identische Manifestrevision und alle betroffenen Bytes
belegt. Dafür dient ausschließlich das ausdrücklich übergebene lokale Gitrepo
`--history-repo`/`history_repo`; der Reader liest die angegebene vorhandene
Commit-SHA, ohne Fetch, Checkout oder Git-Schreibzugriff. Ohne erreichbaren
Historykontext sämtliche Dateien behalten; eine verlangte Weglassung ist sonst
ein Fehler. Aktive Quelle, Entscheidung, Rechte-/Sichtbelege und Ableitung sind
nie durch History ersetzbar. Der Historykontext ist kein neues Requestfeld.

Ein deklarierter Ableitungsbefund wird mit HP-W2 `verify` frisch gegen die
tatsächlichen Quellen, Originalrequest, Profil, Ausgabe und Tool-/Codecbindung
geprüft. Die typisierten Quellen werden dafür unter einer eigenen sicheren
temporären Wurzel mit unveränderten inneren Ref-Pfaden bereitgestellt. Nur der
gewählte Kandidat wird abgeleitet beziehungsweise reproduziert. Fehlende oder
veraltete Ableitung bleibt offen oder wird bei falscher deklarierter Bindung
zurückgewiesen; kein stilles Re-Derive und kein Wechsel der gebundenen Werkzeuge.
Technischer Erfolg erfindet weder Nutzungsrechte noch visuelle Annahmen.

Die öffentliche **rein lesende API** verwendet die vorhandenen Prüfer:
`authoring_package.open_package(path, allow_background=True,
history_repo=..., external_root=...)` und anschließend
`target_adapter.inspect(package, ..., allow_background=True)`. Optionaler
`approval_path` bezeichnet eine schon vorhandene `picross-editorial-approval-v2`;
`external_root` ist nur bei tatsächlich äußeren Hintergrundbelegen ausdrücklich
anzugeben. Das Ergebnis `picross-authoring-content-inspection-v1` unterscheidet
`original_state` und frisch ermittelten `effective_state`, führt offene Gates
und setzt stets `integration_ready=false`. Keine frühere Phase oder gespeicherte
Erfolgsflagge ersetzt eine neue Inhaltsprüfung. PB-H selbst ergänzt keinen CLI;
HP-I1a öffnet inspect/export ausschließlich über den ausdrücklichen Opt-in unten.
Die bisherigen Defaultwege bleiben für 0.7.0 geschlossen; der neue
zielgebundene HP-I1b1-Katalogweg steht unten.

Endfreigabe v2 muss das unveränderte Original-ZIP, Handoff, Inventar, Rasterwahl,
Manifest, tatsächliche Entscheidung, Original, Ableitung, Profil, Ausgabe und
`test_only` exakt binden. Sie wird weder erzeugt, neu datiert noch an neue Bytes
angepasst. Späte äußere Fortschreibung und Export v6 folgen dem HP-I1a-Vertrag
unten. HP-I1b1 ergänzt Registry-/Source-/Receiptformen, Erstintegration und
deren Abschluss im kompatiblen Ziel; reiner Ersatz folgt HP-I1b2 unten, Runtime HP-I2.

Ergebnis ist `picross-authoring-build-result-v2` mit denselben Erfolgs-/Fehler-
Schlüsseln wie v1; darin Record v2 und eine aus diesem Record plus frisch
geprüftem Manifest abgeleitete Sheet-v3-Projektion. Inventar v1 und Index v1
bleiben unverändert. Offene Auswahl, tatsächliches `none`, technische Rasterreife
und fehlende Integration bleiben in Record, Blockern und Projektion getrennt.
Update v3 enthält zusätzlich `Hintergrunddaten`, `Hintergrundstatus`,
`Hintergrund-Optionen` und `Hintergrundauswahl` nach dem Hintergrundvertrag.
MJ-A übernimmt diese tatsächliche Projektion allein oder gemeinsam mit dem
passenden Record v2; Sitzung v5 und Auftrag v4 erhalten alle Hintergrundbindungen.
Ein nackter Record v2 reicht für Status und Kandidaten nicht aus und bleibt bis
zur ausdrücklich zugeordneten v3-Projektion ohne Zustandsänderung.

Determinismus, erneutes Lesen und Prüfen des geschriebenen ZIPs, bytegleiche
Handoffkopie, exakter Dateisatz, Lock, unveränderter No-op, Kollisionsprüfung,
Revisionspublikation vor atomarem Indexwechsel und ehrliche Restpfade bei
Abbruch folgen vollständig dem untenstehenden PB-A-Vertrag. Ein erfolgreicher
Bau schreibt keinen Gitcommit und behauptet keinen Sicherungsstand.

## MJ-A: reguläre Jobs im Offline-Sheet

[Paketentscheidung #490/MJ-A](https://github.com/venomenon328/picross/issues/490#issuecomment-6774440064)
und [Hintergrundvertrag §7.5](../../docs/PUZZLE_BACKGROUNDS.md#75-mj-a-mehrjob-arbeitsbereich-und-sichere-übernahme)
regeln Jobidentität, persönliche Globals/Joboptionen, atomare Importvorschau,
geschlossene Sammlung v1 und die Bindung asynchroner Vorgänge. Einzelne Sitzungen
bleiben nutzbar; die Sammlung sichert Reihenfolge, aktive lokale Jobkennung,
Sitzungen v4/v5, Joboptionen und passend importierte Records. Import und Export
erteilen keine Freigabe und prüfen keine tatsächliche Repositoryverfügbarkeit.

Für Record v2 das erfolgreiche Builder-/Finalizerresultat mit seinem wirklichen
Update v3 oder beide ausdrücklich zugeordneten lokalen Eingänge verwenden. Der
Record allein enthält keine vollständige Kandidaten-/Statusprojektion. Keine Daten
aus Refs nachladen oder erfinden, keine fremden Hashwerte durch JSON-Neuhashung
ersetzen. Vollständige Updates v3 bleiben eigenständig ladbar. Historische false-
Readiness, offene Auswahl und wirkliche `none`-Entscheidung bleiben unterscheidbar.

Neue Jobs starten mit 0.6.0/v4; der reguläre Hintergrundweg ist ausdrücklich
0.7.0/v5 mit Auftrag v4 und passendem Regelpfad. Beide eingebetteten Regeltexte sind
bytegleich mit ihren Markdownquellen. Nach Authoring §9 bleiben kompakte echte
Abschlussbezüge erhalten, bereinigte Produktionsdateien werden nicht rekonstruiert.
Der separate `picross-background-adoption-request-v1` folgt MJ-B mit eigener
Sitzung v1 und Sammlung v2 nach Hintergrundvertrag §7.6. Keine Batchausführung, automatische Bildproduktion oder neue Modell-API.

## HP-I1a: äußere Endabnahme und Export v6

[Paketentscheidung #561/HP-I1a](https://github.com/venomenon328/picross/issues/561#issuecomment-6752672149),
[Hintergrundvertrag §7.4](../../docs/PUZZLE_BACKGROUNDS.md#74-hp-i1a-sichere-äußere-fortschreibung)
und [ZA-1-v6](../../docs/ZA1_ADAPTER.md#hp-i1a--äußere-endabnahme-und-export-v6)
schließen die neuen Auftrags-, Ergebnis-, Wiederaufnahme- und Transportformen.
Die höchste effektive Phase ist `editorially_approved`. Auch ein frisch
verifizierter v6-Export behält seine historischen Felder
`integration_ready/catalog_ready/registered=false`; die frische zielbezogene
Registrierungsprüfung folgt HP-I1b1. Der aktive Default bleibt 0.6.0; es gibt
keine neue Phase „exportiert“. Der Runtimeanschluss folgt HP-I2 unten.

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <request.json> --source-root <neue-dateien> --output-root <authoring-root> [--history-repo <checkout>]
```

API: `authoring_builder.finalize_background(request, source_root, output_root,
history_repo=...)`; `history_repo` nur als benannter Parameter. Bei Repositoryarbeit
ist das Zielroot der Checkout, lokal die vorhandene Authoringwurzel.
`picross-authoring-finalize-request-v1` hat exakt
`format,record,sidecar_root,background,authorizations,files`. `record` bindet den
erwarteten vorhandenen Record v2 mit Pfad, SHA und Bytezahl. `sidecar_root` ist
ein neuer Ordner derselben Authoringrevision. `background` ist die vollständige
Bindung an dasselbe Originalmanifest; `authorizations` enthält genau die vier
Namen `approval.json`, `manual-authorization.json`, `owner-override.json`,
`palette-exception.json`, jeweils `Ref|null` relativ zum Zielroot. `files` führt
exakt die neuen Nutzdateien als `Ref` mit gleichen relativen Pfaden unter den
getrennten Quellen-/Zielroots. Keine Globs, Dateisuche oder stillen Umbenennungen.

Der Finalizer konsumiert vorhandene tatsächliche Entscheidungen und Befunde,
er erzeugt keine Freigabeerklärung. Gültige frühe Wahl wiederverwenden;
späte Wahl an `presented_package` binden. `none` braucht Erklärung und geprüften
Nullbefund, gegebenenfalls auch den frühen Kandidatenverzicht. HP-W2 kann zuvor
die autorisierte Ableitung erzeugen. Bereits gültig gebundene Autorisierungen
dürfen durch null nicht verloren gehen. Original-ZIP, Handoffkopie, Inventar,
ursprüngliche Gates und logische Nachweise bleiben bytegleich; Index v1 bleibt
unverändert. Record v2 und Sheet-Update v3 zeigen nur den frisch geprüften Stand.
`record.verification.authorizations` lokalisiert eng die tatsächlich geprüften
vier Ref/null-Eingänge für die nächste Fortschreibung; kein neues Recordfeld
auf oberster Ebene und keine zusätzliche Autorisierung.

Gemeinsamer Authoringlock, eigener markierter Stage, vollständige Sidecarprüfung
und Veröffentlichung des ganzen neuen Ordners ohne Ersetzen kommen vor dem
**atomaren Recordcommit**. `operation.json` bindet Requesthash, Recordpfad,
bytegenaue `record.before.json`/`record.after.json` und Nutzdateirefs. Diese
internen Namen sind reserviert. Ein HP-W2-Befund liegt in eigenem Unterordner
mit unverändertem exakten Dateisatz. Nach Abbruch denselben Request wiederholen:
vollständigen unverreferenzierten Sidecar frisch prüfen und fortsetzen oder
nach bereits erfolgtem Recordcommit echten Byte-/mtime-No-op melden. Fremde
Bytes, veränderter Record oder Zielkollision sind Konflikte; keine pauschale
Rest-/Locklöschung oder automatisch neue Zielwahl.

`picross-authoring-finalize-result-v1` enthält bei Erfolg exakt
`format,status,record,sheet,operation` mit `updated|reused`, sonst exakt
`format,status,message,remaining,next_action` mit
`invalid_input|conflict|aborted|technical_error`. `operation` ist ein Zielroot-Ref;
`remaining` der tatsächliche eigene Restpfad oder null. Exit 0/2/4/5 und genau
ein JSON auf stdout. Kein Gitcommit, Branchwechsel, Fetch oder Push; kein
erfundener Sicherungsstand, keine Integration.

Für finale Prüfung und Export die vorhandenen ZA-1-Befehle `inspect` und
`export` ausdrücklich mit **`--allow-background`**, bei äußeren Belegen
`--external-root <wurzel>` und bei benötigter lokaler History
`--history-repo <checkout>` verwenden. Die API verwendet entsprechend
`allow_background=True`, `external_root` und `history_repo`. Export verlangt
vollständige Inhalts-/Hintergrundbereitschaft und echte Endfreigabe v2;
`verify-export --export <exportordner>` erkennt die strikte Manifestgeneration.
Die alten Defaultaufrufe und Registry-/Cleanupwege nehmen keine neuen
Hintergrunddaten an.

V6 transportiert das bytegleiche Original als `input/package.zip`, alle nötigen
äußeren Dateien unter `external/<StoredRef.root>/<Ref.file>` und Endfreigabe/
Autorisierungen an den bisherigen Exportorten. Befund und PNG behalten ihre
inneren Pfade und denselben Elternordner. Nur ausgewähltes
`runtime/art/backgrounds/<puzzle_id>.png` und dessen `.txt`-Notice sind neue
Runtimebytes; `none` erzeugt keine Textur. Das geschlossene Manifest v6 bindet
diese Daten, `input.discarded_files` und die vollständige Approval-v2-
Hintergrundbindung; bestehende v5-Felder und Palettengates bleiben erhalten.

Bei schlanken PB-H-Paketen die deklarierte lokale History zuerst vollständig
prüfen. Nur tatsächlich fehlende **inaktive** Kandidatenrefs als ausdrücklich
gebundene Ergänzung unter `input/discarded/<ref.file>` mitnehmen. Original- und
aktuelle äußere Sicht getrennt prüfen: eine später aktiv gewählte Datei muss
regulär vorliegen und darf nie aus dem Supplement gelesen werden. Doppelte,
zusätzliche oder in keiner zulässigen Sicht benötigte Ergänzungen scheitern.
Die genaue Manifest-/Ref-/Pfadbindung steht im ZA-1-Vertrag; allgemeiner
PB-H-Historyvertrag und Originalinventar bleiben unverändert.

Den vollständigen Export vor Veröffentlichung frisch prüfen. Danach kann
`verify-export` alle Original-, Außen-, Supplement-, Freigabe-, Inhalts-, HP-W2-
und Runtimebytes ohne ursprünglichen Quellcheckout/Historyroot/Netz prüfen.
Er benötigt weiterhin die tatsächlich kompatible vollständige Modul-/Codec-/
Profilbindung nach der engen lesenden HP-W2-Regel oben. Ein inkompatibler
Altbefund im Original bleibt prüfpflichtig und blockiert; eine neue äußere
Ableitung ersetzt ihn nicht. `picross-target-inspection-v6` unterscheidet
originalen Erzeugerstand und aktuellen Prüfstand und setzt erst nach frischer
Prüfung `export_verified=true`. Nur das deklarierte `input/package.zip` darf
bis 128 MiB statt des gewöhnlichen 64-MiB-Dateilimits groß sein; übrige Limits,
Alias-/Link-/Kollisions- und Quellenänderungsprüfungen bleiben erhalten.

Der folgende HP-I1b1-Weg öffnet erste Registrierung und Abschluss; späterer
Hintergrundersatz folgt dem HP-I1b2-Weg unten, Runtime/Import/Mipmaps/Laden HP-I2. Alte volle/
Quick-/Metadaten-/direkte API-Verbraucher bleiben geschlossen. Kein Forcepfad;
Export v6 und Registrierungsjournal v6 sind getrennte Formate. Gültige v1–v5-
Exporte bleiben nach ihren eigenen Verträgen nutzbar. MJ-A führt den regulären
Sheetweg; Batchbetrieb gehört nicht zu diesem Paket.

## HP-I1b1: erste Hintergrundregistrierung und Produktionsabschluss

[Paketentscheidung #561/HP-I1b1](https://github.com/venomenon328/picross/issues/561#issuecomment-6754303684),
[Datenvertrag](../../docs/PUZZLE_BACKGROUNDS.md#10-hp-i1b1--erste-registrierung-und-kompakter-produktionsabschluss)
und [Transaktionsmatrix](../../docs/SD_CATALOG.md#hp-i1b1--hintergrundquellen-pläne-und-transaktionen)
führen die genaue Zulassung. Bestehende CLI/API verwenden; kein neuer Export
oder alternativer Zertifizierungseingang. Ein unveränderter frisch geprüfter
v6-Export darf genau eine neue ID im kompatiblen Ziel registrieren.

### Zielfähigkeit vor Planung und Mutation

Feste Datei `game/data/background-capability.json`, exakt
`format,runtime_format,profile_id,enabled` mit
`picross-runtime-background-capability-v1`, `picross-runtime-registry-v6`,
`picross-background-png2304-v1` und Boolean `enabled`. Höchstens 4096 Bytes.
Fehlend/false blockiert den Hintergrund-Plan/-Registeraufruf vor Journal und
Katalogänderung. Ungültige Form/Pfade sind Eingabefehler. **True verlangt den
funktionierenden HP-I2-Runtime-/Importweg samt technischer Abnahme.**
Keine Änderung dieser Datei als Bedienhilfe, kein API-/CLI-/Umgebungs-Override;
`--allow-background` lässt nur den inspect/export-Eingang zu. Isolierte
synthetische Ziele dürfen true/test_only verwenden, ohne Spielerverhalten oder
reale Produktionsabnahme zu belegen. Testinputs bleiben im echten Katalog verboten.

Exportfalse-Felder, Original-ZIP, Approval und Finalizerrecord bleiben unverändert.
Bereitschaft wird frisch am konkreten Ziel außerhalb des Manifests ermittelt.
Unter diesen Voraussetzungen folgt nach regulärer Difficultybindung:

```sh
python -m tools.puzzle_production.target_adapter plan --export <v6-export> --checkout <kompatibles-ziel> --difficulty <checked.json>
python -m tools.puzzle_production.target_adapter register --export <v6-export> --checkout <kompatibles-ziel> --difficulty <checked.json>
```

Die vorhandene ausdrücklich gewählte `--rebind-difficulty`-Alternative und
Kategorie-/Zielbindungen bleiben. `register` führt eigene volle Eingangsprüfung
und unabhängiges Stagingreplay aus; ein früherer Plan ist kein Vertrauenscache.
Ein erfolgreicher Lauf bedeutet registrierten Checkout. Main-Integration
verlangt weiterhin den tatsächlich bestätigten Merge und passende Befugnis.

### Dauerhafte Source, minimale Runtime und Folgeoperationen

Registry v3 hat exakt `format,entries,backgrounds`. Bestehende Entryformen
bleiben unverändert. Jeder neue v6-Entry erhält den indexierten Ref auf
`content/backgrounds/<id>.json`, auch none. `picross-catalog-background-v1`
bewahrt ursprünglichen Exportanker/Approval, tatsächliche Entscheidung/Ableitung,
gewählte Herkunft/Rechte/Q-HG-Urteile, feste Identität, aktive Integerrevision 1
und gewähltes PNG/Notice oder null. Keine Alternativen/Prompts. Nur selected
erzeugt `game/art/backgrounds/<id>.png` und `.txt`; none erzeugt keine Nulltextur.
Die genaue geschlossene Unterform steht im Datenvertrag, kein freies Metadatenobjekt.

Runtime v6 ergänzt je Entry genau `background={status,image_revision,asset}`.
Legacy ist nur ein gültiger alter Eintrag, none braucht ausdrücklichen Verzicht,
selected enthält Ref auf `art/backgrounds/<id>.png`. Keine Freigabetexte oder
Produktionsdateien in Runtime. Ungültige deklarierte Quelle wird nie als
Legacy/none behandelt. Legacy-only bleibt Runtime-v5; Hintergrundkatalog verlangt
gültige aktive Capability, ohne stillen Downgrade.

| Verbraucher | Neue geschlossene Generation / Umfang |
| --- | --- |
| Erste Registrierung / Recovery | `picross-registration-journal-v7`; vollständige neue Quellen, `replacements={}`, nur Neuanlagen/Textdelta. |
| Rating-/Added-Pflege und Sync | `picross-catalog-difficulty-report-v5`, `picross-added-plan-v4`, `picross-catalog-metadata-journal-v4`; Hintergründe bytegleich. |
| Methodenaktivierung | `picross-difficulty-activation-plan-v2`, `picross-difficulty-activation-journal-v2`; nur bisheriger Defaultrecord, Runtime/Hintergründe bytegleich. |
| Rasterupdate eines Legacyziels im gemischten Katalog | `picross-content-update-journal-v6`; Hintergründe erhalten. |
| Revealadoption eines Legacyziels im gemischten Katalog | `picross-reveal-plan-v3`, `picross-reveal-adoption-journal-v3`; gültige Runtime/Hintergründe bytegleich. |

Aktive Rating-/Added-/Defaultrecords und Revealrequest/-result v1 bleiben erhalten. Rasterupdate
und Revealadoption **eines Hintergrundziels** benötigen HP-I1c (unten);
die älteren Generationen blockieren sie weiterhin. Reiner Hintergrundersatz samt Binär-Add/Delete/
Replace-Recovery folgt HP-I1b2 unten; altes Raster-ZIP wird dafür keine Voraussetzung.
Zulässige Kategorienquell-/Anzeigenamenpflege ist erhalten, keine neue freie
Umklassifizierung historischer Entries/Receipts.

### Quellen, Recovery und No-op

Neue Quellenmengen binden Capability/null, Hintergrundsource/Notice pro ID,
ausgewählte PNGs und alle erwarteten Abwesenheiten; vollständige Namespaces
`backgrounds,background_assets` kommen zu den bisherigen vier. Fremde Dateien,
Aliase, Links und Quellenwechsel blockieren. Alte Pläne werden im neuen Katalog
stale/unsupported; kein stilles Auffüllen. Alte Journale behalten ihre Originalform.
Nur bei gültigem Legacy-Registry-v2-/Runtime-v2–v5-Stand ohne Hintergrundnamespace
darf fehlende/streng gültige false-Capability als inaktive Deklaration bestehen.
True oder neue Registry-/Runtime-/Hintergrunddaten blockieren alte Recovery.

Gemeinsamer Writerlock, vollständige Alt-/Zielansicht, sichere Neuanlagen und
Runtime zuletzt bleiben. RI-B erhält alle neuen Bytes privat im Prozess;
registration-v7 übernimmt ausdrücklich G0/G2/G5a/G5b/G6/GR0/GR2 samt lokalen
Prüfungen dazwischen. Keine Performancezusage oder globale Prüfung vor jedem
Dateischritt. Recovery bleibt Rollback; fremde Bytes/Locks erhalten, tatsächliche
Reste nennen. RI-A-Budgets unverändert, keine automatische Erhöhung.
Nur das deklarierte v6-Original-ZIP erhält über Inventar/Staging/Additions/
Guard/Readback die 128-MiB-Grenze; andere Limits bleiben.

Identische Registrierung vor/nach Retirement prüft Eingänge und Checkout frisch
und endet byte-/mtimegleich ohne neue Added-Daten. Der ursprüngliche Exporthash
ist Vergleichsanker; den späteren Receipthash nicht als anderes Original deuten.
Kein Wiederherstellen bereits abgeschlossener Produktionsdateien.

### Main-gebundener erster Produktionsabschluss

Nach tatsächlich bestätigter Main-Integration `origin/main` aktualisieren und
den bisherigen `retire-production --integrated-commit <volle-main-SHA>` verwenden.
Vor erster Entfernung alle ausgewählten IDs/Arbeitsbytes, Source/Index,
PNG/none/Notice gegen tatsächlichen Main-Stand samt Abstammung prüfen.
`picross-integrated-content-v2` hat die bisherigen vier Receiptfelder plus
`background={origin_sha256,source}`. Source/Ursprung bleiben unverändert;
der Mainbeleg steht im Receipt, aktueller `production.package_sha256` bindet
dessen echte Bytes. V1-Receipts bleiben für alte Inhalte unverändert gültig.

Nur belegte abgeschlossene Arbeit entfernen. Neuere/offene Geschwister und
fremde/unklare Dateien erhalten oder bei nicht trennbarem ID-Baum vor Mutation
blockieren. Aktive Definition/Reveal/Hintergrund, Rechte, kompakte echte
Freigabe-/Ableitungsbindungen, Rating, Added und Runtime bleiben. Danach prüft
der Reader Receipt/Source/Livebytes und interne historische Identitäten; er öffnet
keine gelöschten ZIPs/Kandidaten neu und behauptet keine Bild-/Proofreproduktion.
Gleicher vollständiger Abschluss mit gleichem Mainbeleg ist No-op. Teilfehler
mit tatsächlichen Resten melden. Der Befehl erzeugt einen lokalen Diff und führt
keinen Commit/Merge aus; Werkzeugpakete erben keine Authoring-Cleanup-Mergefreigabe.

## PB-A: deterministischer Authoring-Paketbau

Bestehender 0.6.0-Bauvertrag, [Paketentscheidung #489/PB-A](https://github.com/venomenon328/picross/issues/489#issuecomment-6745424504).
Der Builder sichert ausdrücklich benannte Produktionsdateien. Er erzeugt keine
Bild-, Solver-, Bewertungs- oder Freigabeentscheidungen und führt keine Git-
Schreibaktionen aus. Die additive PB-H-Generation steht oben; der folgende
v1-/0.6.0-Vertrag bleibt erhalten.

```sh
python -m tools.puzzle_production.authoring_builder build --request <request.json> --source-root <quellen> --output-root <arbeitsordner> [--publish-to <checkout>]
```

API: `authoring_builder.build(request, source_root, output_root, publish_to=None)`.
Request ist ein JSON-Objekt mit exakt `format,handoff,document_revision,files,
target,category_id,reveal_options,external`. Format:
`picross-authoring-build-request-v1`. `handoff` ist der noch **unversiegelte**
Authoring-v2-Datensatz mit `inventory=null`, ID, neuer Revision, tatsächlichem
gelesenem `repo_commit`, Regelwerk 0.6.0 samt Snapshot-Dateihash und Phase.
`document_revision` ist eine positive Ganzzahl und muss zum Snapshot passen.
Der Quellencommit ist eine Herkunftsangabe, kein behaupteter Sicherungscommit.
`target` ist `local` oder `repository` (nur mit `--publish-to`); Kategorie darf
null bleiben. `files` enthält ausschließlich explizite Objekte
`{path,source,sha256,bytes}`: normalisierter Paketpfad, sicherer relativer Pfad
unter `source-root`, erwarteter Datei-SHA-256 und Bytezahl. Keine Ordnersuche.
Unbekannte Requestfelder und deklarierte technische Formate sind Fehler;
redaktionelle Ergänzungen stehen im Handoff unter `editorial` und bleiben erhalten.

`reveal_options` enthält die tatsächlich noch angebotenen Bilder mit genau
`ID,Beschreibung,Datei,SHA-256` gemäß Authoring §7; jedes Bild benötigt Herkunft.
Nach Auswahl ist die Liste leer und `handoff.reveal` bindet die konkrete Datei
samt Entscheidung. Historische verworfene Varianten werden in `editorial` als
Commit/Pfad/Hash/Entscheidung referenziert, nicht als ZIP/Galerie kopiert.
`external` ist eine Map expliziter äußerer Dateien auf `{source,sha256,bytes}`:
zulässig sind `approval.json`, `manual-authorization.json`, `owner-override.json`
und `palette-exception.json`. Diese Bytes werden separat erhalten; vorhandene
Autorisierungen müssen zu den tatsächlich erzeugten Originalbindungen passen.

Phasen: `brief_ready` verlangt Briefing und Regelwerk; `reveal_review` zusätzlich
alle angebotenen Revealoriginale/Herkunft; `motif_review` ein tatsächlich
freigegebenes Reveal sowie Motivdatei/-herkunft; `raster_review` zusätzlich eine
Motivfreigabe und vorhandene Kandidaten-/Bündelbindungen. Entscheidungen/Aufwand
werden, soweit geführt, erhalten. Alle vorhandenen Datei-/Freigabe-/Gatebelege
werden geprüft, fehlende Entscheidungen bleiben offen. `content_ready` verlangt
den vollständigen bisherigen ZA-1-Eingang: Bildfreigaben, Parameter, RP-3/RP-5,
Proofs, Herkunft, Berichte, Difficulty und gegebenenfalls Palettensichtung.
Nur dort wird das **geschriebene ZIP** frisch mit ZA-1 inspiziert; ausschließlich
die fehlende separate finale Endabnahme darf als Inhaltsblocker übrig bleiben.
Der Builder setzt keine Gates auf `pass` und erhöht keine Phase automatisch.

Inventar v1 schließt sich und Handoff aus. Alle Quellen einschließlich sämtlicher
manifestgebundener Dateien werden vor und nach dem Lesen gegen Größe, SHA-256
und Dateidentität geprüft. Dateihashes bleiben von kanonischen Logik-/Vertrags-
Hashes getrennt. Sichere Pfade, Windowsaliase, Link-/Reparseverbot sowie die
ZA-1-Datei-/ZIP-/Mengenlimits und 300 Sekunden gelten auch hier. Bereits
versiegelte Eingänge werden zurückgewiesen; der vorhandene lesende ZA-1-Weg
für Altpakete und deklarierte Teilkopien bleibt unverändert.

Stabile JSON-Bytes, Memberreihenfolge und ZIP-Metadaten ergeben aus demselben
Request dieselben Bytes. Zunächst entsteht eine eigene temporäre Revision;
frische sichere Extraktion prüft CRC, exakten Dateisatz, Hashes und die bytegleiche
äußere Handoffkopie. Ergebnisdateien: `package.zip,handoff.json,record.json` plus
explizite äußere Belege. Der Record bindet Phase, Prüfung, offene Freigaben,
Paket/Inventar, Blocker und nächsten Schritt; Sheet-v2 wird ausschließlich daraus
abgeleitet und auf stdout geliefert. Lokale ungesicherte Arbeit führt einen
Sicherungsblocker und `Quellbranch / Commit=null`; kein erfundener Gitstand.

Lokales Ziel ist `<output-root>/<ID>/<Revision>`, Repositoryziel ausschließlich
`<checkout>/content/authoring/<ID>/<Revision>`. Output-root dient bei Publikation
nur als explizite Arbeitswurzel; veröffentlicht wird im Checkout auf demselben
Dateisystem. Ein kooperativer einzelner Writer sperrt den Zielindex/-baum über
einen OS-Dateilock; Prozessende gibt ihn frei. Vollständige Revisionen werden
ohne Ersatz publiziert. Identische Wiederholung prüft alle Bytes und bleibt
auch hinsichtlich mtimes unverändert; anderer Request oder andere Bytes unter
derselben Revision sind Konflikte. Spätere äußere Recordpflege wird nicht ersetzt.

Der bestehende Index v1 wird zuerst gelesen, dann unter Lock frisch verglichen
und erst nach vollständiger Revisionspublikation atomar ersetzt. Fremde Änderungen
bleiben erhalten und ergeben Konflikt, keinen stillen Retry. Revision und Index
sind keine gemeinsame Transaktion: Abbruch dazwischen hinterlässt höchstens eine
vollständige unindexierte Revision. Das Ergebnis meldet Fehler und konkreten
Restpfad; derselbe unveränderte Request kann sie erneut prüfen und indexieren.
Eigene unveröffentlichte Stages werden bei behandeltem Fehler/Abbruch entfernt;
nach hartem Kill dürfen markierte eigene Stages erst nach Lock-/Besitzprüfung
gemäß WORKSPACE entfernt werden. Der kooperative Lock verhindert keine beliebigen
fremden OS-Schreibzugriffe; Vergleichsprüfungen erkennen sie an den Grenzen.
Exit 0: `built`/`reused`; 2: Eingangs-/Kollisions-/Dateifehler; 4: Abbruch.
Keine Teilpublikation wird als Erfolg gemeldet, kein `editorially_approved`-
Übergang und keine Runtime-/Index-Gitaktion durch den Builder.

## P-B2: automatische Frühdiagnose und finale Palettengates

Vor Code festgelegter Vertrag, 08.11.2026: [ZA-1 P-B2](../../docs/ZA1_ADAPTER.md#p-b2--authoring-060-und-additive-palettengeneration-v5)
definiert die exakten geschlossenen Pflicht-/Optionalfelder, C(x)/H(x),
Dateihashes, Fehlerzustände und Kreuzbindungen. Neue Produktionen verwenden
Authoring 0.6.0 und ausschließlich `picross-target-inspection-v5` /
`picross-target-export-v5`; 0.4.x/0.5.0 und v1–v4 bleiben unverändert lesbar.
Der aktuelle Authoring-/Offline-Snapshot weist 0.6.0 selbst aus. Paarprofile und
manuelle Autorisierungen v1–v6 bleiben zulässig. Kein Legacy-Schalter für neue
Produktion, kein neuer Solver-/Runtime-/Recoveryvertrag.

RP-3 prüft konkrete Matrizen vor dem Solver, RP-5 vor jeder Bewertung, feste
manuelle Wege vor dem Endproof-Replay. Die bestehenden Vergleiche zeigen die
Diagnose; negative Entwürfe bleiben vorhanden. Ein Palettenentwurf ohne Matrix
ist nur vorläufig. Endprüfung in ZA-1 liest immer den tatsächlichen finalen
Stand neu. Der unveränderte P-B1-Bericht bindet Normrevision 4 und bleibt die
Rechenbasis; kein früherer positiver Report wird übernommen.

`palette_gate` enthält genau `assessment,binding,visual_review,exception,allowed`.
Die vollständige aktuelle Messung entsteht im Adapter selbst; ein optional
inventarisiertes `palette_assessment={file,sha256}` wird zusätzlich frisch
verifiziert. `binding` enthält genau `puzzle_id,revision,candidate,source,
matrix_hash,logic_hash,palette_sha256,source_fingerprint,rulebook,handoff_sha256,
inventory_sha256,original_zip_sha256` nach ZA-1. V5-Exporte führen dieselbe
Gatehülle, gegebenenfalls die bisherige `manual_authorization` und bei Paarprofil
`deduction`. Andere Felder oder Formatdowngrades sind Fehler.

Farbpakete führen im Handoff `palette_review={file,sha256}` auf einen
inventarisierten `picross-palette-visual-review-v1`-Record. Exakt `format,
puzzle_id,revision,matrix_hash,logic_hash,palette_sha256,criteria`; die drei
Kriterien Q-R04/Q-H01/Q-H02 führen je `result,accepted,actor,timestamp_utc,
statement,reason,evidence`. Ergebniswörter sind die vier deutschen Urteile des
Qualitätsvertrags. Belege sind nichtleere Listen exakter `{file,sha256}`-Refs.
Nicht geprüft blockiert; Warnung/negatives Sichturteil braucht ausdrücklich
`accepted=true` samt tatsächlichem Wortlaut/Begründung. Ein positives S allein
erteilt keine Sichtfreigabe. Ohne Review bleibt die Diagnose sichtbar und
gesperrt; Mono hat hier null, sein bisheriges visuelles Gate bleibt Pflicht.

```sh
python -m tools.puzzle_production.target_adapter inspect --input <paket> --report <neue-diagnose.json>
python -m tools.puzzle_production.target_adapter inspect --input <paket> --approval <endfreigabe.json> --palette-exception <externe-einzelfallannahme.json>
python -m tools.puzzle_production.target_adapter export --input <paket> --approval <endfreigabe.json> --palette-exception <externe-einzelfallannahme.json> --name "<Motiv>" --runtime-revision 1 --stem <stamm> --save-slot <slot> --category-id <kategorie> --categories <kategorien.json> --output-dir <neuer-export>
```

`--palette-exception` ausschließlich bei negativem vollständigem Paarset und
echter Endfreigabe; mit `--manual-authorization` kombinierbar. Der äußere Record
`picross-palette-editorial-exception-v1` hat exakt `format,binding,negative_pairs,
actor,timestamp_utc,statement,reason,approval_sha256,test_only` (maximal 128 KiB).
Er bindet das vollständige Gate-Binding und alle negativen P-B1-Paarobjekte,
einschließlich exaktem S/RGB/IDs, plus Endfreigabebytes und Paketscope. Keine
Links/Reparsepunkte, keine Ablage im Originalpaket. Export liefert ihn unverändert
als `palette-exception.json`, sein Gatefeld `exception` hat exakt `record,sha256`.
Die Software authentifiziert keine Menschen; eine tatsächliche Erklärung ist
weiterhin notwendig. Teilmenge, Freitext, fremde oder mutierte Bindung scheitert.
Der technische Status bleibt negativ; nur der Palettenredaktionsblocker entfällt.

Vor `content_ready` die geschriebene Paketfassung inspizieren. Die 0.6.0-Diagnose
liest schon `raster_review`, ohne daraus Bereitschaft abzuleiten. Export verlangt
`technical=true` und echte Endabnahme. Offline-Reader, Plan/Register und
Rasterersatz prüfen die Originale und Gatebindung erneut, nicht nur Flags/Hashes.
Ungültige oder stale Records sind Eingabefehler; Budget-/Prozessabbruch kein
Erfolg (bestehende Exitcodes 2/4). Rechte, Proof, Bild-/Motivabnahmen, feste
Parameter, Difficulty, Randregel und Registrierungsauftrag bleiben unabhängig.
Bei null freigabefähigen Angeboten echte Sichtungsentwürfe mit konkreten
Defiziten/Korrekturen zeigen; `Raster-Optionen=[]`. Keine neue Oberfläche,
Bestandsvalidierung, persönliche Referenzabnahme oder dauerhafte Bildgalerie.

**Q-A / #488:** [PUZZLE_QUALITY](../../docs/PUZZLE_QUALITY.md) ist die verbindliche
redaktionelle Produktionsreferenz, zusammen mit dem
[Authoringworkflow](../../docs/ai-workflows/PUZZLE_AUTHORING.md). Sie regelt auch
Sichtungsentwürfe ohne vollständige Qualifikation und gezielte redaktionelle
Einzelfallentscheidungen. Diese sind keine technischen Zertifikate; Proof,
Herkunft/Rechte, Datei-/Freigabebindungen und bestehende Adaptergates bleiben
Pflicht. Q-A führt den Qualitätsvertrag; P-A normiert die unveränderte
Farbregel und P-B1 liefert die lesende Diagnose. P-B2 aktiviert sie unter 0.6.0
gemäß dem obigen v5-Vertrag. Altformate und versiegelte Belege behalten ihre
Semantik, tatsächliche Sichtentscheidungen bleiben eigenständig.

## P-B1: lesende Palettendiagnose

Vertrag vor Implementierung, #488 / P-B1, 08.11.2026. Regel unverändert
`picross-palette-separation-1`, Normquelle `docs/PUZZLE_QUALITY.md`, Vertrag 1.0,
Dokumentrevision 4, Quellcommit `45b8fe697364bf73f4277c8b76f92d5c00400919`, §8.4.
Diese feste Normbindung bezeichnet die Berechnung, nicht den jeweiligen Tool-Head.

```sh
python -m tools.puzzle_production check-palette --candidate <bundle/area-candidate.json>
python -m tools.puzzle_production check-palette --candidate <bundle/area-candidate.json> --report <neue-externe-datei.json>
python -m tools.puzzle_production check-palette --candidate <bundle/area-candidate.json> --verify <gespeicherter-report.json>
```

Python 3.11+, für den Kandidatenleser bestehende Image-Umgebung. `--report` und
`--verify` schließen einander aus. `--seconds` ist das kumulative kooperative
Lese-/Rechen-/Prüfbudget (Default 120, endlich, nicht negativ; 0 bricht ab).
Der reine Kern `palette_quality.assess(matrix, palette, identity, budget=None)`
braucht nur die Standardbibliothek und kann später vor dem Solver aufgerufen
werden. `identity` enthält exakt `id` (stabile Zeichenkette, 1..128 ohne
Steuerzeichen), `revision` (Ganzzahl 1..1000000), `source_id` (bestehende
ASCII-ID-Grammatik), `normalized_sha256` (64 kleine Hexzeichen).
Matrix 1..100 je Achse, rechteckige Zeilenlisten, Zellen ausschließlich
`empty` oder deklarierte Vordergrund-ID. Palette 1..8 eindeutige IDs mit jeweils
`#rrggbb`; gleiche RGB unter verschiedenen IDs ergeben im reinen Kern S=0.
Null verwendete Farben ist ungültig. Unbenutzte Einträge werden nur gemeldet.
Der bestehende RP-3-Designleser lehnt doppelte RGB weiterhin gesondert ab.

Der CLI-Leser validiert das geschlossene bestehende Kandidatenformat, Design,
Variante, Produzentenversionen, Quellhash, Matrix und frisch abgeleiteten
Logikhash und rekonstruiert die Kandidaten-ID. Er vertraut keinem Erfolgsflag.
Er rekonstruiert weder Originalbild noch Proof: Quellen-ID, Herkunft/Rechte und
Normalisierungshash sind gebundene Herkunftsangaben, keine verifizierte
Bildableitung oder Rechtefreigabe. Dafür bleiben die bisherigen Replaygates nötig.

### Diagnoseformat picross-palette-assessment-v1

Alle folgenden Top-Level-Felder sind Pflicht, zusätzliche Felder unzulässig:

| Feld | Inhalt |
| --- | --- |
| `format`, `rule_id`, `norm` | Formatkennung, obige Regel-ID; `norm` exakt `file,contract,document_revision,commit` nach obiger Normbindung. |
| `candidate` | Exakte `identity` wie oben. |
| `matrix` | Exakt `width,height,order,sha256`; `order=row-major`, Hash über kanonisches Objekt `{width,height,order,cells}` mit vollständiger Matrix als `cells` (Zeilenlisten). |
| `palette_sha256` | Hash der nach ID sortierten vollständigen Liste `{id,rgb}`; RGB wird kleingeschrieben. Unbenutzte Einträge bleiben darin gebunden. |
| `source_fingerprint` | Hash über `{rule_id,norm,candidate,matrix,palette_sha256}` aus diesem Bericht. |
| `used` | Nach ID sortierte Liste, je exakt `id,rgb,cells,q`; q drei quantisierte Ganzzahlen nach §8.4. |
| `unused_ids`, `empty_cells`, `pair_count` | Sortierte unbenutzte IDs, getrennte Leerzahl, vollständige Anzahl ungeordneter Paare (maximal 28). |
| `pairs` | Alle Paare lexikografisch nach IDs; je exakt `ids,rgb,q,S,D,status,rule_id`. Zwei IDs/RGB/q in derselben Reihenfolge; S exakte Ganzzahl, D Dezimalzeichenkette mit sechs Nachkommastellen (Half-even), nur Anzeige. Status `negative` bei S<10000000000, sonst `borderline` bei S<22500000000, sonst `positive`. |
| `worst_pair` | Vollständiges Paarobjekt mit kleinstem S, Gleichstand nach IDs; bei einer Farbe null. |
| `negative_pairs`, `warning_pairs` | Vollständige Listen derselben Paarobjekte mit Status `negative` bzw. `borderline`, auch bei negativem Gesamtbefund. Korrektur: klarere Palette, weniger Farben oder motivtreue neue Variante; bestehende Freigaben beachten. |
| `status`, `complete` | `negative` falls irgendein negatives Paar, sonst `positive`; `complete=true` ausschließlich nach vollständiger Auswertung. Eine Farbe: positive, 0 Paare. |

Hashes verwenden die bestehenden kanonischen JSON-UTF-8-Bytes/SHA-256 (ohne LF),
Dateien kanonisches JSON plus LF. Kein Zertifikat, `content_ready`, Sichturteil
oder Ausnahmerecord. Technisches `positive` ersetzt Q-R04/Q-H01/Q-H02 nicht.
`verify_assessment(report, matrix, palette, identity, budget=None)` rekonstruiert
Bindungen, Nutzung, q, sämtliche Paare und den Gesamtstatus frisch, unabhängig
von gespeicherten Behauptungen; fehlende/zusätzliche/falsche Felder sind Fehler.
Andere Matrix, ID, RGB, Nutzung, Herkunft, Revision oder Normbindung ist stale.
Das ist Integritätsprüfung, keine Signatur gegen gemeinsam neu erzeugte Eingänge.

Stdout enthält genau ein kompaktes JSON: bei abgeschlossener Diagnose bzw.
erfolgreichem `--verify` den vollständigen Bericht, auch bei `negative` Exit 0.
Fehler liefern ausschließlich `picross-palette-error-v1` mit `status,message`:
`invalid_input`/2 (auch stale/manipulierter Bericht, unsicheres Ausgabeziel),
`aborted`/4 (Budget, Signal, Speicher), `error`/5 (Rechen-/Dateifehler).
Argparsefehler verwenden Exit 2; harter Kill garantiert keine Abschlussausgabe.
Fehler/Abbruch erzeugen keinen Assessmentbericht oder positiven Teilbefund.

Ein Reportziel muss einen vorhandenen regulären Elternordner und einen neuen
einfachen `.json`-Dateinamen besitzen. Kein Überschreiben (auch nicht bei Rennen),
keine Links/Reparsepunkte, kein Ziel innerhalb eines Git-Checkouts, des
Kandidatenordners oder eines anhand `handoff.json`, `inventory.json`,
`manifest.json` oder `package.zip` erkannten Paketordners. Die Eingabepfade
werden ebenfalls ohne Links/Reparsepunkte gelesen. Reportpfade aus fremden
JSONs werden nie geöffnet. Die CLI prüft den erzeugten Bericht vor Ausgabe
erneut; optionale Reportdatei wird exklusiv neu angelegt und frisch gelesen.

**Aktivierungsgrenze:** Die einzelne P-B1-CLI bleibt freiwillige Diagnose,
kein Zertifikat. Seit P-B2 laufen zusätzlich automatische Frühchecks und das
verbindliche v5-Endgate für neue 0.6.0-Pakete. F05 bleibt metrisch negativ bei
historisch dokumentierter visueller Referenzannahme, ohne Produktionsausnahme.
Keine rückwirkende Bestandsprüfung oder zusätzliche Standard-Erfolgsausgabe.

**AT · Umsetzungsvorbereitung V4 vom 19.10.2026; AT-A nach AT-A-R01 mit PR #263 integriert:**
[AT](../../docs/REVEAL_TRANSPARENCY.md) ergänzt mit AT-A den Produktionsstandard
für transparente Abschlussbilder und einen eigenen eng begrenzten Bildupdateweg.
AT-B stellt danach den gebundenen Bestand mit tatsächlichen Bildfreigaben um.
Reine Bildrevisionen verwenden den eigenen `catalog_reveal`-Weg; `plan-update`/
`update` bleibt auf den gesonderten Rasterersatz begrenzt und erhält aktive
Bildfassungen. Die technische AT-A-Lieferung übernimmt keine realen Bilder
oder Metadaten.
[AT-B-V01](../../docs/AT_B_VERIFICATION.md) liefert die vollständige
Bild-/Endfreigabevorlage im frühen Authoringstatus `reveal_review`.
Die anschließende [Eigentümerabnahme](../../docs/AT_B_OWNER_APPROVAL.md) erlaubt
AT-B-F01 mit kontrolliertem `catalog_reveal plan/adopt` und AT-B-T01.
Kein produktiver Request oder Plan mit ausstehenden Zustimmungen.

**Aktuelle Prüfzuordnung:** Konkrete Rätsel werden während ihrer Produktion und
Integration geprüft, nicht als wachsender CI-Korpus. Keine rätselspezifischen
Unit-Tests. Der aktuelle Paketplan wählt bei Werkzeugänderungen begründete Fachmodule
mit festen synthetischen Eingängen. Reine Inhalts-PRs erhalten den allgemeinen Quellen-/Plankern ohne Player-Build;
das ist keine erneute Logik-/Proof-/Rasterprüfung. Auch der Main-Nachlauf bleibt buildfrei.
Maßgeblich: [CI-Vertrag](../../docs/CI_WORKFLOW_V2.md) und
[Authoringworkflow](../../docs/ai-workflows/PUZZLE_AUTHORING.md).

KAT-1 ergänzt [Kategorien und Zuordnung](../../docs/CATEGORIES.md): neue ZA-1-Exporte verlangen `--category-id` und `--categories`; Snapshot, Manifest v2, Zielregistry und Runtimeprojektion werden gemeinsam geprüft. `sync-runtime --checkout .` übernimmt geprüfte Metadaten in die Projektion. `check-registry --checkout .` prüft laufende Produktionspakete per Replay, abgeschlossene Produktion über die kompakte Integrationsbindung. Alte Exporte bleiben prüfbar, benötigen zur neuen Registrierung aber einen kategorisierten Neu-Export.

ZA-1 ergänzt den allgemeinen Authoring-v2-Zieladapter und Datenregistrierung:
[CLI, Schemas und Fehlerverhalten](../../docs/ZA1_ADAPTER.md),
[Prüfzuordnung](../../docs/ZA1_VERIFICATION.md). Diese Befehle benötigen die
isolierte Image-Umgebung mit Pillow 12.3.0. Alte Pilotprofile bleiben erhalten.
Das reguläre Ziel unterstützt 1…8 Vordergrundfarben plus Leer. Ein ausdrücklich
beauftragter Rasterersatz verwendet `plan-update` → `update` mit
`--expected-definition-sha256`, höherer Runtime-Revision und neuer Paketrevision;
Identität, Slot, Kategorie und Reveal bleiben erhalten. Recovery nutzt weiterhin
`recover-registration`; Details und Grenzen im ZA-1-Vertrag. `register` allein
überschreibt weiterhin keine vorhandenen Inhalte.

**RI-A-V01 · Über PR #484 auf main integriert:**
[RI](../../docs/PUZZLE_INTEGRATION.md) und [RI-A-T01](../../docs/RI_A_VERIFICATION.md)
binden Umfang, Messungen und Gates. Nur `register` akzeptiert
`--publication-seconds S` und `--recovery-seconds S` (jeweils Default 1800).
`recover-registration --recovery-seconds S` gilt nur für sicher erkannte
Registrierungsjournale; andere Operationen lehnen diesen Override ab und
behalten sonst 300 s plus bestehende Außenbudgets. Die feste Warnung nach
300 s bricht keinen Lauf ab. API: `registration`/`integrate` erhalten
`publication_seconds=None, recovery_seconds=None`; `recover` erhält
`recovery_seconds=None`. Plan/Update lehnen mutierende Overrides ab.
`S` ist positiv und endlich, API exakt `int`/`float` ohne `bool`, inklusive
endlicher berechneter Deadline.
Noch unbekannte Recoveryoperationen bleiben während der lesenden Klassifikation
unter höchstens 300 s beziehungsweise einem kürzeren Override. Erst sichere
Zuordnung erlaubt den Registrierungsrahmen ab dem ursprünglichen Aufrufstart;
abgelaufene Erst-/Außenfristen werden nicht verlängert. Eine früh erkannte
zulässige Registrierungs-Format-/Operationspaarung erlaubt die vollständige
Validierung über die Warnschwelle von 300 s hinaus, sofern die ursprüngliche
Registrierungsfrist noch läuft. Die Vorzuordnung ist keine Autorisierung
für Mutation; Journal-/Quellenprüfung bleibt vollständig verbindlich.

`export`, `plan`, `register`, `recover-registration` ergänzen stdout ausschließlich
um `operation_diagnostics`; es bleibt genau ein JSON-Ergebnis. Fortschritt,
300-s-Warnung und Abschluss stehen auf stderr, regulär höchstens alle 30 s.
`--operation-report <neue-datei>` veröffentlicht dieselbe Hülle
`picross-ri-a-operation-v1` atomar außerhalb des Checkouts und aller Eingänge.
Der Elternordner muss existieren; keine Überschreibung. Ein Berichtsfehler nach
Commit bleibt ein Diagnosefehler auf stderr, kein fehlgeschlagener Commit.
Verschachtelte Phasen sind inklusive, nicht additiv; Zähler zählen tatsächliche
Aufrufe/Bytes, benannte Messlücken bleiben offen. Ressourcen/Signale: Exit 4
auch nach Rollback; fachliche Fehler: Exit 2. Dauerhaftes P6 einschließlich
Lockentfernung bleibt Erfolg bei erst danach bemerktem Fristablauf.
Ein harter Prozessabbruch kann den Abschlussbericht verhindern.
`*_attempts` zählt begonnene Kandidaten-/Input-/Exportprüfungen, die drei
`full_*`-Zähler nur deren erfolgreichen vollständigen Rücklauf. Fehler und
Fristabläufe bleiben als Versuche/Teilzeiten erhalten. Phasen P0–P6/R0–R2
bezeichnen die gerade ausgeführte Arbeit einschließlich wiederholter Dateien;
Checkpointfortschritt ist kein vorgezogener Phasenabschluss. Details und
Zählernamen stehen im [ZA-1-Vertrag](../../docs/ZA1_ADAPTER.md).

Andere Writer, `catalog_reveal --seconds` 1…300, Authoring-Eingangsprüfung,
Solver-/Import-/Proof- und Datei-/Bytegrenzen bleiben unverändert.

**RI-B-V01 · Branchlieferung zu #479:** Innerhalb einer mutierenden neuen
Registrierung bleiben Eingangsprüfung und unabhängiger Staging-Replay vollständig.
Ein privater prozess-/threadgebundener Kontext ersetzt danach ausschließlich die
beiden wiederholten Proofprüfungen des neuen Pakets in P3/P5 durch vollständige
frische Inventar-/Byte-Nachprüfungen. Er bindet tatsächliche Freigaben, Parameter,
Quellen, Methodenbytes, Stagingidentitäten und konkretes Journal. Änderungen,
Austausch und Scopeende bei Erfolg/Fehler/Abbruch entziehen die Wiederverwendung.
Diagnostik zählt `verified_package_reuses` getrennt von `full_*`; Nachprüfung ist
keine weitere vollständige Proofprüfung. Es gibt keinen neuen CLI-Schalter,
persistenten Cache oder externen Pass-Beleg. Getrennte Befehle prüfen unabhängig;
`verify-export` vollständig, `plan` lesend, `register` ausdrücklich autorisiert.
Updates/No-ops, alle globalen Guards, P0–P6/R0–R2 und Recovery bleiben durch B unverändert.
Recovery verwendet niemals den Kontext. [RI-B-T01](../../docs/RI_B_VERIFICATION.md)
bindet Plattformmessungen, tatsächliche CI und offene Gates.

**RI-C-F01 / RI-C-V01 · Branchlieferung zu #480:** Nur mutierende v6-
Erstregistrierungen und deren Recovery verwenden vollständige G0/G2/G5a/G5b/G6-
bzw. GR0/GR2-Prüfungen mit frischen lokalen Journal-/Ziel-/Eltern-/Tempprüfungen
zwischen diesen Grenzen. Runtime bleibt letztes Datenziel. Unbeteiligte fremde
Quellen seit G2 werden spätestens vor Runtime an G5a erkannt; danach an G5b/G6,
bei Recovery an GR2. Unsicherer Rollback erhält Fremdbytes und Journal.
Andere Writer/Generationenpfade, CLI, Limits und RI-A-Budgets bleiben erhalten.
Der [Transaktionsvertrag](../../docs/SD_CATALOG.md#ri-c--phasengrenzen-für-erstregistrierung-v6)
erklärt die geänderte Erkennungszeit, kooperativen Lock und verbleibende OS-Rennen.
[RI-C-T01](../../docs/RI_C_VERIFICATION.md) bindet die tatsächlichen Nachweise;
keine Sekundenbeschleunigung allein aus verringerten Guardzahlen ableiten.

KE-N1: `recover-registration` übernimmt gültige alte Runtime-v2-Snapshots in
Registrierungsjournal v2 bzw. Updatejournal v1 und stellt direkt einen vollständig
geprüften v3-Checkout her. Beide Snapshots müssen kanonisch und formatgleich sein.
Die gesamte Zielansicht wird vor Änderungen ohne Produktionsreplay geprüft;
Wiederaufnahme erlaubt nur exakt gebundene alte/neue Bytes oder die eigene
hergeleitete v3-Projektion. Fremde Änderungen erhalten alle Dateien samt Journal.
Kein nachgeschobenes Sync, keine realen Saveänderungen; Journal v1 bleibt gesperrt.
Feste Altformatregressionen: `tests/puzzle_production/test_ke_recovery.py`.

Python **3.11+**, ausschließlich Standardbibliothek, ohne Installation von Paketen,
Netzwerk-/Modellaufrufe oder P1-Abhängigkeit. Aus dem Repository-Root ausführen;
unter Windows einen tatsächlichen Python-Interpreter statt eines Store-Alias nutzen.
Fachvertrag: [Rätselproduktion](../../docs/PUZZLE_PRODUCTION.md).
Prüfzuordnung: [RP1_VERIFICATION.md](../../docs/RP1_VERIFICATION.md).
Farberweiterung: [RP2_VERIFICATION.md](../../docs/RP2_VERIFICATION.md).
RP-1/RP-2 sind nach unabhängigem Review über PR #42/#43 in `main` integriert.
RP-3-Bildbefehle benötigen die separate Image-Umgebung weiter unten; die bisherigen
Kernbefehle bleiben ohne Pillow nutzbar. [RP-3-Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP3_VERIFICATION.md).

## Aufruf an gespeicherten Beispielen

Die Ausgabe muss ein neuer Pfad ohne `proof.json`/`result.json` sein. Eine Wiederholung
verwendet einen neuen Pfad, damit ein altes Zertifikat nicht als neues Ergebnis erscheint.

```sh
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/deductive.json --output-dir artifacts/rp1-example
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/deductive.json --proof artifacts/rp1-example/proof.json
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/unique-stalled.json --output-dir artifacts/rp1-unique-stalled
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/color-four.json --output-dir artifacts/rp2-four
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/color-four.json --proof artifacts/rp2-four/proof.json
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/color-propagation.json --output-dir artifacts/rp2-propagation
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
```

`solve` serialisiert den zunächst ungeprüften Nachweis und prüft die gespeicherte Datei
mit dem unabhängigen Prüfer. `verify` kann diese Datei in einem frischen Prozess
prüfen; `--report <datei>` speichert zusätzlich das Prüfungsergebnis. Jede CLI gibt
ein JSON-Ergebnis auf stdout aus. `proof_verified` bezeichnet die geprüfte Spur und
den beanspruchten Status, `certified` ist ausschließlich bei `solved` wahr.
Eine korrekt geprüfte Abbruchspur bleibt `aborted`, ohne Zertifikat.

| Status / Exitcode | Bedeutung |
| --- | --- |
| `solved` / 0 | Vollständiges gültiges Raster und unabhängig geprüfter Nachweis; `certified=true`. |
| `stalled` / 0 | Unvollständiger, unabhängig bestätigter Fixpunkt; kein Eindeutigkeits-/Mehrdeutigkeitsurteil. |
| `contradiction` / 0 | Unabhängig bestätigte unmögliche Linie nach den bewiesenen Einschränkungen. |
| `invalid_input` / 2 | Ungültiges oder nicht unterstütztes Logikformat/Parameter. Auch argparse-Aufruffehler verwenden 2. |
| `invalid_proof` / 3 | Manipulierter, unpassender oder fehlerhaft formatierter Nachweis. |
| `aborted` / 4 | Zeit-/Arbeitslimit, Abbruchsignal oder `MemoryError`; kein Zertifikat. |
| `technical_error` / 5 | Datei-/interner Laufzeitfehler; kein logisches Rätselurteil. |

Ein wohlgeformter Eingang mit überfüllter Linie oder unvereinbaren Hinweisen ist
`contradiction`, kein Formatfehler. SIGKILL und ein harter OS-Prozessabbruch können
keinen JSON-Abschluss garantieren; der übergeordnete Benchmark wertet sie als
nicht erfolgreich. Ergebnisse sind nur aus erfolgreich beendeten Aufrufen zu übernehmen.

## Versionierter Datenvertrag

Alle Objekte sind UTF-8-JSON. Unbekannte Schlüssel, doppelte JSON-Schlüssel,
NaN/Infinity, numerische Überläufe zu nicht-endlichen Werten, boolesche Dimensionen und versteckte Startannahmen werden abgewiesen.
Dimensionen liegen in 1..100, Rechtecke und 1D eingeschlossen. Hinweislisten sind
geordnet; Leerlinien verwenden `[]`, jeder Block positive Länge 1..100 und
`color="ink"` im alten Monoformat. Maximal 100 Hinweise pro Linie. Auch formal übervolle Listen bleiben
wohlgeformte, logisch widersprüchliche Eingänge.

Ein minimales vollständiges Beispiel für 1×1:

```json
{
  "format": "picross-logic-v1",
  "width": 1,
  "height": 1,
  "colors": ["ink"],
  "empty": "empty",
  "rules": {"id": "mono-gap-v1", "same_color_gap": 1},
  "initial_domain": ["empty", "ink"],
  "row_clues": [[{"length": 1, "color": "ink"}]],
  "column_clues": [[{"length": 1, "color": "ink"}]]
}
```

`initial_domain` ist eine Broadcast-Domain für **jede** Zelle, keine Matrix mit
Vorbelegungen. Der Leerwert und die stabile Vordergrund-ID bleiben getrennt;
Domainmengen werden als geordnete Arrays `["empty","ink"]`, `["empty"]` oder
`["ink"]` serialisiert. Intern nutzt RP-1 Bitmengen 1/2/3. RP-2 erweitert die
Bitmengen um Farben, ohne Kanalzerlegung. Keine Motive, Bilder, Lösungsmatrix,
Vorbelegungen oder Assetmetadaten gehören in den Logikeingang.

Kanonische Hashbytes: `json.dumps(obj, sort_keys=True, separators=(',', ':'),
ensure_ascii=False, allow_nan=False).encode('utf-8')`; **ohne** BOM/Abschlusszeile.
SHA-256 als 64 kleine Hexzeichen. Der Logikhash umfasst das vollständig validierte,
über `Puzzle.to_wire()` normalisierte Logikobjekt, einschließlich aller Regeln und
der Startdomain. Gespeicherte Dateien besitzen zusätzlich eine LF-Abschlusszeile.
Dateihashes wie `proof_sha256` umfassen die tatsächlich gespeicherten Bytes.
Zeitmessungen, Auswertungsreihenfolge und Betriebssystemdaten sind keine Logikidentität.

Das Regelprofil ist exakt:

```json
{"id":"full-line-mono","version":1,"start":"unknown","deduction":"all-line-supported-values","search":false}
```

Sein kanonischer SHA-256 ist
`e49e4cd74c4c4c02e08170ce670a40f48b82490a6bea52c3c764143d7a0af4b0`.
Es gibt kein auswählbares schwächeres/anderes Zertifizierungsprofil.

### Farbvertrag und Kompatibilität

Die ursprünglichen Monoformate, `mono-gap-v1` und `full-line-mono` Version 1 behalten
ihre Bedeutung und kanonischen Hashbytes. Ein vor RP-2 mit `main@b18a234` erzeugter
unveränderter [Referenzbeleg](../../tests/puzzle_production/fixtures/rp1-proof.json)
wird tatsächlich erneut eingelesen. Seine Herkunft und Dateihashes stehen im RP-2-Prüfbericht.

`picross-logic-v2` hat dieselben neun Top-Level-Felder wie v1, unterstützt jedoch
**1..8 Vordergrundfarben plus Leer**. Farb-IDs sind eindeutig, 1..32 ASCII-Zeichen
nach `[a-z][a-z0-9_-]{0,31}`; `empty` ist reserviert. Es gibt keine RGB-/Bildfelder.
Die Eingabepalette kann beliebig geordnet sein; `initial_domain` muss exakt
`["empty", *colors]` in dieser Eingabereihenfolge enthalten. Nach Validierung wird
die Palette lexikografisch sortiert; Hinweise behalten ihre Reihenfolge und binden
ihre semantische ID. Das normalisierte Objekt bestimmt den Logikhash. Eine andere
Reihenfolge derselben Palette ändert diesen Hash nicht; andere IDs/Regeln/Hinweise schon.

Die Regeln sind exakt
`{"id":"color-gap-v1","same_color_gap":1,"different_color_gap":0}`.
Gleiche Nachbarfarben brauchen Leer; verschiedene Farben können direkt berühren
oder durch Leer getrennt sein. Der gemeinsame Zellautomat berücksichtigt alle Farben.
Intern ist Leer Bit 0, Farbe i der normalisierten Palette Bit i+1. Domains sind
nichtleere Bitmengen; Wire-Domains folgen immer `empty`, danach der sortierten Palette.
Partielle Startdomains sind weiterhin unzulässig; Einschränkungen entstehen nur
durch Deduktion oder in isolierten Linientests.

Das zugehörige Profil ist exakt
`{"id":"full-line-color","version":1,"start":"unknown","deduction":"all-line-supported-values","search":false}`
mit SHA-256 `f63ee6c88e6baa9f6a22f386ae532482d7ffb7b9a2237867f0d7cd9960ab608f`.
`picross-proof-v2` nutzt dieselben Proof-Felder/Schrittregeln wie v1, jetzt mit
farbigen Domains. Logik v2 verlangt Proof v2 und das Farbprofil; v1 verlangt weiterhin
Proof v1 und das Monoprofil. Kein stiller Profilwechsel und keine frei auswählbaren Regeln.
Eine einzelne ausgeschlossene Farbe zählt auch bei noch mehrwertiger Restdomain
als Fortschritt und führt die kreuzende Linie erneut aus.

`picross-proof-v1` besitzt genau die Felder `format`, `logic_hash`, `profile`,
`profile_hash`, `steps`, `status`, `final_domains`, `contradiction`, `reason`.
Jeder Schritt beider Versionen hat `axis` (`row`/`column`), nullbasierten `index` und `changes`.
Jede Änderung hat nullbasierten `offset` sowie `before`/`after`-Domains. Sie umfasst
alle unabhängig erzwungenen Einschränkungen dieser Linie im rekonstruierten Zustand.
Die Reihenfolge der Änderungen ist aufsteigend; Linien ohne Fortschritt erzeugen
keinen Schritt. Der Prüfer erlaubt verschiedene zulässige Linienreihenfolgen.
`final_domains` ist die vollständige Domainmatrix nach Replay; kein Zielbild.
`contradiction` ist bei Widerspruch eine Linienreferenz, sonst `null`.
`reason` ist nur bei Abbruch `time_limit`, `work_limit` oder `cancelled`, sonst `null`.
Ein CLI-`MemoryError` liefert einen Abbruchbericht und keinen beanspruchten Nachweis.

`picross-result-v1` führt Status, `certified`, `proof_verified`, erfolgreiche
Logik-/Profilbindung (einschließlich des tatsächlichen Profils), Schritt-/Linienzahlen und getrennte Zeiten; Fehlermeldungen
führen `error`/`message`. Zusätzliche technische Berichtsfelder sind keine Beweisvoraussetzungen.
Eine erfolgreiche Prozessausführung ist von vollständiger Zertifizierung zu unterscheiden.
Python-API: zuerst `validate_logic`, dann `solve` und separat `verify`;
`solve(Puzzle, Budget, order)` allein liefert einen **ungeprüften** Nachweis.

## Separate Eindeutigkeitsdiagnose (#139/A)

```sh
python -m tools.puzzle_production diagnose --input tests/puzzle_production/fixtures/unique-stalled.json --output-dir artifacts/uniqueness-1
python -m tools.puzzle_production check-diagnosis --input tests/puzzle_production/fixtures/unique-stalled.json --bundle artifacts/uniqueness-1
```

Python-API: `diagnosis.diagnose(Puzzle, DiagnosisBudget)` liefert unabhängig
geprüfte Zeugenobjekte im Speicher; `diagnosis.diagnose_file(input_path, output_dir,
DiagnosisBudget)` schreibt das dateigebundene Bundle.
`diagnosis_verifier.verify_witness` prüft vollständige Matrizen durch eigene
Runextraktion ohne Solverimport. Kein Sollraster wird akzeptiert; Eingang bleibt
das strikte Logikformat v1/v2 mit Rechtecken/1D, 1..100 je Achse und 1..8
Vordergrundfarben im Farbformat. Keine zusätzliche Produktionszertifizierung.

| Diagnose / Exitcode | Voraussetzung |
| --- | --- |
| `unique` / 0 | Genau eine unabhängig geprüfte Lösung; Suchraum vollständig erschöpft. |
| `multiple` / 0 | Zwei verschiedene unabhängig geprüfte Lösungen; weitere Suche endet. |
| `no_solution` / 0 | Suchraum vollständig erschöpft, keine Lösung. |
| `unknown` / 4 | Untersuchung unvollständig, auch nach genau einer gefundenen Lösung. |
| `invalid_input` / 2 | Ungültiges Logikformat, Budget oder bereits vorhandenes Ausgabeziel. |
| `invalid_diagnosis` / 3 | Checker: beschädigte, unpassende oder ungültige Belege. |
| `technical_error` / 5 | Datei-/interner Fehler; kein logisches Negativurteil. |

Aufruffehler verwenden argparse-Exitcode 2. Alle JSON-Ausgaben setzen
`certified=false`. Fehler verwenden `picross-uniqueness-error-v1` mit `status`,
`error` und `message`. Harte OS-Abbrüche garantieren keinen Abschluss. Nur
geschriebene Berichte nach beendetem Aufruf übernehmen; Exitcode 4 kennzeichnet
ausschließlich eine Teiluntersuchung.

**Vollständigkeit und Reihenfolge:** `domain-dfs-line-support` Version 1 startet
mit voller Domain jeder Zelle. Der vorhandene Zellautomat entfernt ausschließlich
Werte ohne Unterstützung in einer zulässigen Linienbelegung. Jede tatsächliche
Lösung des aktuellen Zweigs bleibt erhalten. Nach vollständiger Linienpropagation
wird die erste Zelle mit kleinster mehrwertiger Domain gewählt (Gleichstand:
Zeile, Spalte). Ihre Werte werden aufsteigend untersucht: Leer, danach sortierte
Palette. Diese Zweige sind disjunkt und decken den Elternsuchraum vollständig ab.
Jeder Abstieg bestimmt mindestens eine weitere Zelle; Tiefe höchstens Breite·Höhe.
Unmögliche Linien verwerfen nur ihren aktuellen Zweig. Ein reversibler Änderungspfad
stellt beim Rücksprung den Elternzustand wieder her; iterative Tiefensuche vermeidet
Rekursionslimits und vollständige Rasterkopien je Knoten. Endmatrizen werden
separat direkt gegen alle Hinweise geprüft. Erschöpfung beweist daher Eindeutigkeit
beziehungsweise Unlösbarkeit; zwei verschiedene geprüfte Matrizen beweisen
Mehrdeutigkeit. Worst-Case-Aufwand bleibt exponentiell; Erfolg im Budget ist keine Zusage.

**Kumulative Budgets:** `--seconds` 120, `--max-lines` 100000 und `--max-nodes`
100000 standardmäßig; Zählergrenzen jeweils 0..1000000. Ein Knoten ist die Wurzel
oder ein betretenes Kind vor Propagation. Jede Linienauswertung und jede Zeilen-/
Spaltenprüfung eines Zeugen verbraucht denselben Linienvorrat. Kein Zweig erhält
neue Budgets. Die monotone CLI-Deadline beginnt vor Eingabelesen und umfasst
Schreiben/Neueinlesen sowie notwendige Prüfung der Zeugen; abschließende kleine
Berichtsserialisierung erfolgt danach. Kooperative Grenzen gelten zwischen den
durch 100 Zellen begrenzten Linienoperationen; kein hartes RSS-/OS-Limit.
`node_limit`, `work_limit`, `time_limit`, `cancelled` und `memory_limit` ergeben
`unknown`. Ein während der Prüfung abgebrochener Zeuge zählt nicht als Lösung.
Nullbudgets erlauben deterministische Abbruchproben. Zeitlimits garantieren
keine identischen Teilverläufe auf anderer Hardware.

**Dateivertrag:** Das Ausgabeziel muss neu/nicht vorhanden sein, auch ein leerer
vorhandener Ordner wird zurückgewiesen. Es enthält `input.json` als exakte
Eingabekopie, null bis zwei `solution-1.json`/`solution-2.json` und `diagnosis.json`.
Unvollständig geprüfte Kandidaten können unreferenziert zurückbleiben; nur
referenzierte Zeugen zählen. Fehler können eine Eingabekopie hinterlassen,
niemals einen erfolgreichen Bericht. Limits: Logik 2 MiB, einzelne Zeugen 512 KiB,
Berichte 64 KiB. 100×100 Werte mit maximal langen IDs passen ins Zeugenlimit.
Dateihashes umfassen tatsächliche Bytes einschließlich Abschlusszeile.

`picross-solution-witness-v1` hat exakt `format`, normalisierten `logic_hash`
und `matrix`: vollständige Zellmatrix aus Leer-/Paletten-IDs, keine Domains.
`picross-uniqueness-v1` hat exakt `format`, `tool` (`picross-uniqueness`, Version 1),
`method` (ID/Version, obige `branch_order`/`value_order`, `search=true`), `logic_hash`,
`status`, `search_complete`, `reason`, `certified`, `budgets` (`seconds`, `max_lines`,
`max_nodes`), `statistics` (`nodes`, `line_evaluations`, `witness_line_evaluations`,
`elapsed_seconds`), `input` und `witnesses`. Die letzten beiden binden `file`,
`sha256` und `bytes`. In der Speicher-API stehen unter `witnesses` stattdessen
Zeugenobjekte; `input` fehlt. `search_complete=true` gilt ausschließlich bei
`unique`/`no_solution` mit `exhausted`; `multiple` endet mit `two_solutions`.

`check-diagnosis` prüft Berichtskonsistenz, exakte Eingabebytes, referenzierte
Dateibindungen, vollständige gültige Zeugen und deren Verschiedenheit. Feste lokale
Dateinamen verhindern frei gewählte Pfade; Symlinks werden zurückgewiesen.
Sein `picross-uniqueness-check-v1` meldet `file_bindings_verified`, die Zahl
`witnesses_verified`, `reported_status`, `logic_hash`, `search_replayed=false`
und `certified=false`. `confirmed_status` ist nur mit zwei Zeugen `multiple`, sonst
`null`: keine unabhängige Bestätigung der erschöpfenden Suche oder Zertifizierung
für `unique`/`no_solution`. Dafür ist der Diagnosealgorithmus mit vollständiger
Suchraumabdeckung zu reviewen. Hashbindungen sind keine Signaturen. Der Checker
hat ein eigenes kumulatives Zeit-/Linienbudget; Abbruch liefert keinen Prüferfolg.

Ein Eindeutigkeitsurteil ersetzt kein Produktionsmanifest, keinen vollständigen
Deduktionsnachweis und keine redaktionelle Abnahme. Der verifizierte Linienfixpunkt
bleibt `stalled`, auch wenn die Suche `unique` ergibt. Import, Reparatur, ZA-1
und Schwierigkeit L1–L5 werden durch diese Diagnose nicht verändert.

## Paarlinienprofil und Schwierigkeit 0.2 (#139 B/C)

Der [Paarlinienvertrag](../../docs/PAIRED_LINES.md) ergänzt ausdrücklich gewählte
`paired-lines-mono`/`paired-lines-color` v1 und `picross-proof-v3`. Exakte Beziehungen
zweier beliebiger paralleler Linien werden nach dem vollständigen Linienfixpunkt
ausgewertet. Der getrennte Prüfer leitet sie selbst her. Standardaufrufe,
`full-line-*`, alte Proofbytes und Diagnose A behalten ihren Vertrag.

```sh
python -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/unique-stalled.json --profile paired-lines-mono --output-dir artifacts/paired-example
python -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/unique-stalled.json --proof artifacts/paired-example/proof.json
python -m tools.puzzle_production assess --input tests/puzzle_production/fixtures/unique-stalled.json --proof artifacts/paired-example/proof.json --baseline artifacts/paired-example/baseline-proof.json --report artifacts/paired-assessment.json
```

`solve` schreibt zusätzlich `baseline-proof.json` und `assessment.json`, prüft
beide Proofdateien unabhängig und berichtet die gemeinsame Arbeit unter
`certification_line_evaluations`/`certification_seconds`. `--max-pair-work`
(20.000.000) und `--max-pair-records` (250.000) begrenzen innere Arbeit und
gleichzeitig gespeicherte Struktureinträge, auch im unabhängigen Prüfer.
Verbrauchte Arbeit wird niemals zurückgesetzt; unvollständige Projektionen
werden nicht angewendet. Ressourcenende ist `aborted`, kein starker Fixpunkt.

`import-image` erhält dieselbe ausdrückliche `--profile`-Auswahl und Paarbudgets.
Es schreibt Manifest v2 mit `certification` und je Variante Baseline/Assessment.
Reparaturen binden diese Konfiguration im [Plan v2](../../examples/rp5/README.md).
Handoff-v2 bindet sie in `candidate.certification`; mindestens Regelwerk 0.5.0,
bei neuer Produktion 0.6.0 mit seinem zusätzlichen v5-Palettengate ist Pflicht.
Alte Import-/Reparaturmanifeste und Authoring 0.4.x legitimieren keine Paarproofs.
Die 0.5.0-ZA-1-Exporte verwenden v4, damalige Linienfälle v2/v3;
0.6.0 verwendet für alle diese Wege ausschließlich v5.

`assess` prüft die übergebenen gespeicherten Proofs frisch. Optionales
`--diagnosis <A-Verzeichnis>` ergänzt den unveränderten A-Dateicheck, ohne eine
erschöpfende Suche als unabhängig nachgewiesen auszugeben. Der Bericht trennt
`multiple`, `reported_unique_without_complete_deduction`, `diagnosis_incomplete`,
`line_logic_solved`, `paired_lines_solved` und vollständige Deduktion ohne
Notwendigkeitsbeleg. Difficulty 0.2 meldet R4/L5 nur bei geprüfter Linienbaseline
`stalled` und vollständigem Paarproof derselben Logik. Umfang, Zeit und
redaktionelle Freigabe bleiben eigene Angaben; kein vollständiger R0–R3-Analysator.

ZA-1 ergänzt mit `picross-manual-authorization-v6` die ausdrücklich angenommene
monochrome Pixelvorlage aus einem versiegelten manuellen Neuentwurf. Die separate
Eigentümererklärung bindet Originalpaket, Motivannahme, Parameter und Endabnahme;
eine eng geprüfte Präfixbindung erhält historische Revealfreigabe und Provenienz.
Der vollständige RP-3-Pixelimport wird frisch unabhängig zertifiziert, ohne alte
Gates oder Dateien umzuschreiben. V1–v5, Randregel und Inhaltsgates bleiben erhalten.
Schema und Grenzen stehen in [ZA-1](../../docs/ZA1_ADAPTER.md); CLI weiterhin
`--manual-authorization`, Export v3/v4. Synthetische Regressionen prüfen diesen
Weg; reale Rätsel bleiben reine Produktionsinputs.

## Instrumentierte Einzelanalyse (SD-A) und feste Bewertung (SD-B)

Der freigegebene [SD-Vertrag](../../docs/PUZZLE_DIFFICULTY.md), Ursprung
[#235](https://github.com/venomenon328/picross/issues/235), bindet die getrennte
Bewertungsspur mit instrumentierten R0–R3-Regeln und synchronen Wellen.
Bestehende Proofverträge und der unabhängige R4-Notwendigkeitsbeleg bleiben
unverändert. SD-B bindet feste Skalen- und Größenregeln an unabhängige synthetische
Referenzen; der reale Katalog ist weder Kalibrierungskorpus noch Testbestand.
Auch Kopien realer Rätsel dürfen keine automatisierten Bewertungsfälle werden.

SD-C1 führt den gemeinsamen manuellen Weg für ausgewählte Bestandsrätsel und
neue Rätsel nach finaler Deduktionsprüfung ein: Bericht erzeugen, Bindungen prüfen,
ausdrücklich beauftragt übernehmen. Passende Berichte sind wiederverwendbar.
Die [Methode 0.3](../../docs/SD_CALIBRATION.md) ist als opt-in Einzelbewertung
implementiert; [SD-C1](../../docs/SD_CATALOG.md) liefert die technische Übernahme.
Reale Bestandsbewertung/Übernahme bleibt der separate Auftrag SD-C2. Neue Registrierung
und logikrelevante Updates verlangen zusätzlich den vollständig geprüften 0.3-Input.
Authoring 0.5.0 und Produktionsfreigaben bleiben erhalten. Keine reale Analyse in CI,
gewöhnlichem Build, Registryprüfung oder Katalogstart.

```sh
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd-a-example
python -m tools.puzzle_production check-analysis --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd-a-example
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/deductive.json --output-dir artifacts/sd-a-logic
python -m unittest discover -s tests/puzzle_production -p 'test_analysis.py' -v
```

Für den eingefrorenen Methodenstand **zusätzlich bei Erzeugung und Prüfung**:

```sh
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --method picross-difficulty-0.3 --output-dir artifacts/sd-b-example
python -m tools.puzzle_production check-analysis --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd-b-example --method picross-difficulty-0.3
python -m unittest discover -s tests/puzzle_production -p 'test_difficulty_rating.py' -v
```

SD-B schreibt zusätzlich `rating.json` (`picross-difficulty-rating-v1`, maximal
64 KiB). Es bindet den vollständigen festen Methodensatz, exakte Konfiguration,
Referenzen, Kalibrierungsbelege und Quellmodule sowie geprüften v1-Ergebnishash und
Quellidentität. Der Checker prüft zuerst das gesamte v1-Bundle unabhängig neu,
danach sämtliche Ratingfelder gegen die eingefrorene Berechnung. Fehlende oder
veränderte Bindungen sind Fehler, auch bei neu berechnetem Hash. Keine Ratingpfade
aus Berichten werden geöffnet. API: `analyze_file(..., method="picross-difficulty-0.3")`
und `check_bundle(..., method="picross-difficulty-0.3")`; die reinen mathematischen
Reducer sind selbst keine Proofprüfer und erwarten bereits geprüfte Metriken.

Logische Basis, Größenbeitrag und Endstufe werden getrennt berichtet. Ein gültiger
Wert ist `instrumented`/`medium`, ohne menschliche Kalibrierung oder Lösungszeit.
Abbruch, Widerspruch und unvollständige Deduktion liefern `unrated` mit null als
Stufe. Vollständiger Paarproof ohne unabhängig bewiesene R4-Notwendigkeit genügt
nicht. Nur geprüftes notwendiges R4 erhält 5 bei unvollständigem Linienverlauf.
Die vorhandenen Exitcodes und getrennten R4-Dateien gelten weiter.

Ohne `--method` bleiben Erzeugung und Prüfung exakt SD-A/v1. Sie behaupten keine
Ratingprüfung, auch wenn daneben ein Rating liegt. Die historische v1-Erklärung
„SD-B ausstehend“ bleibt zur exakten alten Ergebnisrekonstruktion erhalten;
die neue CLI zeigt bei gewählter Methode die aktuelle Ratingerklärung.

Der erste Eingang ist ein fester künstlicher 3×2-Balken, ohne Produktionspaket
oder Revealdatei. Nur das **neue** Analyseverzeichnis wird geschrieben. Es enthält
`input.json` (exakte Quellbytes), `logic.json` (eigener kanonischer Analyseinput),
`trace.json` und `report.json`. Bestehende Ausgabeordner werden abgewiesen.
Der lesende Checker vergleicht die aktuelle explizite Quelle mit der Kopie und
prüft Dateihashes, Regelstärken, vollständige gleichzeitige Möglichkeiten,
schwächere Fixpunkte, Endstatus und rekonstruierte Berichtsfelder.

`--input-kind logic` (Standard) liest unveränderte Logik v1/v2. `runtime` liest
ausschließlich die benannte Schema-2-Definition und normalisiert numerische
Farben auf `c1`…`c8` unter Farbregeln; auch bei einer Farbe wird kein historischer
Produktionsmodus behauptet. Die Sollmatrix wird erst nach der Ableitung geprüft.
Analysehash, Engine-Logikhash und tatsächlicher Definitions-Dateihash bleiben
getrennt. Kein Bestandscheck und keine Rekonstruktion alter Produktionspakete.

Der vollständige [SD-A-Vertrag](../../docs/SD_ANALYZER.md) definiert die endlichen
Regeln, Wellen, Zähler/Nenner, Symmetrie und die Formate
`picross-analysis-input-v1`, `picross-analysis-trace-v1` sowie
`picross-analysis-report-v1`. `result` mit `result_hash` ist deterministisch;
Dateibindungen, `operation` mit Budgets/Verbrauch/Laufzeit und Prüfstatus sind
getrennt. Kein Score: `method`, `level`, `confidence` und `estimated_minutes`
bleiben im v1-Bericht null. Bei `stalled` ist der Linienfixpunkt geprüft, aber der Lösungsverlauf
unvollständig. Ein geprüfter Abbruchpräfix bleibt `aborted`.

Budgets: `--seconds 120`, `--max-lines 100000`, `--max-rule-work 20000000`,
`--max-waves 80000`; eigene Prüfgrenzen `--verify-seconds 120`,
`--verify-max-lines 100000`, `--verify-max-rule-work 20000000`.
Der Checker verwendet seine eigenen `--seconds`/`--max-*`-Grenzen.
Abbruch in einer Welle übernimmt keinen Teilfortschritt. Kann der gespeicherte
Trace nicht fertig geprüft werden, entsteht kein erfolgreicher `report.json`.
Teilartefakte können zur Diagnose bleiben; ein harter Prozessabbruch garantiert
keine JSON-Abschlussausgabe. Fehler liefern auf stdout ein eigenes Fehlerobjekt.

| Status / Exit | Bedeutung |
| --- | --- |
| `solved`, `stalled`, `contradiction` / 0 | Unabhängig geprüfter jeweiliger Linienstatus; nur solved ist vollständiger Linienverlauf. |
| `invalid_input` / 2 | Ungültiger Eingang/Parameter oder vorhandenes Ausgabeziel. |
| `invalid_analysis` / 3 | Falsche Spur, veraltete Bindung oder widersprüchlicher Bericht. |
| `aborted` / 4 | Zeit-/Arbeits-/Wellen-/Speicherende oder Abbruch; keine Einstufung. |
| `technical_error` / 5 | Datei-/interner Fehler, kein logisches Rätselurteil. |

Optional bindet `--parameters <json>` genau `{"aggregation":null}` oder das
im Vertrag definierte `sd-aggregation-1`-Objekt. Die angegebenen Engstellen- und
Restaufräumkriterien erscheinen explizit im Trace; es gibt keine kalibrierten
Defaults. SD-B verwendet die Rohmetriken mit exakt `{"aggregation":null}` und
seine eigene gebundene Bewertungsaggregation. Andere Parameter zusammen mit
`--method picross-difficulty-0.3` werden vor dem Analyselauf abgewiesen.

Optional und ausschließlich zusammen: `--r4-proof <proof-v3.json>` und
`--r4-baseline <linienproof.json>`. Beide werden unverändert kopiert und mit dem
vorhandenen unabhängigen Verifier geprüft. Die Nachweise müssen exakt zur
Engine-Logik passen; nach Runtime-Farbnormalisierung passen alte semantische IDs
nicht automatisch. Nur eine bestätigte stalled-Linienbaseline und ein vollständiger
Paarproof bei ebenso abgeschlossenem SD-Linienfixpunkt begründen R4. Seine Schritte
bleiben außerhalb der Wellenzählung. `--max-pair-work` und `--max-pair-records`
behalten die bestehenden Paarbudgets. Kein automatischer Paar-/Suchlauf.

Python-API: `analysis.analyze(Puzzle, config, AnalysisBudget)` erzeugt eine noch
ungeprüfte Spur; `analysis_verifier.verify_trace` beziehungsweise `verify_result`
prüfen sie. `analysis_io.analyze_file` und `check_bundle` binden die gespeicherten
Bytes. Vorhandene Proof-v1/v2/v3-Verifikation und `quality.assess()` bleiben erhalten.

## SD2-A: Separater Analyseweg

Der [technische Vertrag 1.0](../../docs/SD2_ANALYZER.md) wurde vor Code versioniert.
Der eigene Analysator und unabhängige Prüfer verwenden E0–E3 und liefern getrennte
Rohprofile für Denkanspruch, Suchaufwand und Bearbeitungsumfang. Die eigene CLI
ist ohne Pillow oder Engine ausführbar:

```sh
python -m tools.puzzle_production.sd2_cli analyze --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd2-example
python -m tools.puzzle_production.sd2_cli check --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-example
python -m unittest discover -s tests/puzzle_production -p 'test_sd2_analysis.py' -v
```

Das Beispiel ist ein fester synthetischer Balken. Ohne `--input-kind runtime`
werden Logikdateien v1/v2 gelesen. Ausgabeordner müssen neu sein. Das Bundle
enthält `input.json`, `logic.json`, `trace.json`, `report.json`; optional die
beiden expliziten `--r4-proof`/`--r4-baseline`-Dateien. Der Checker ist lesend,
prüft die ganze Spur und rekonstruiert sämtliche Profile. Keine Registry wird
gelesen. Alle Dateiformate besitzen eigene `picross-sd2-*-v1`-Kennungen.

`--seconds 120 --max-lines 100000 --max-rule-work 20000000 --max-waves 80000`
sowie `--max-pair-work 20000000 --max-pair-records 250000` begrenzen den Lauf.
Analyze hat eigene `--verify-seconds`, `--verify-max-lines`,
`--verify-max-rule-work` mit denselben Defaults. Unterbrochene Wellen werden
verworfen; Prüfabbruch schreibt keinen Erfolgsbericht. Exit 0 bestätigt den
jeweiligen Status solved/stalled/contradiction, 2 ungültigen Input, 3 ungültige
Analyse, 4 Abbruch und 5 technischen Fehler. Ein Fixpunkt ist kein vollständiger
Lösungsverlauf. Proxys sind keine gemessenen menschlichen Zeiten oder Klickzahlen.

Auch vollständige SD2-A-Berichte enthalten keine Endnote oder aktive Bewertung;
`method`, `level`, `confidence`, `estimated_minutes` bleiben null. Alte Aufrufe
und der vollständige 0.3-Freeze bleiben erhalten. A ist nach separatem Review
über PR #408 integriert. [Historische Prüfzuordnung](../../docs/SD2_A_VERIFICATION.md).

## SD2-C: gemeinsamer Integrationsvertrag

[SD2-C-V01](../../docs/SD2_INTEGRATION.md) bindet vor Code die neuen Checked-/
Rating-/Kontext-/Reportformate, Runtime-v5 und Journalgenerationen. Die bisherigen
0.3-Formate und eigenständigen A-/B-CLIs bleiben geschlossen. Der reale
Produktionsdefault ist nach [D-F01/T01](../../docs/SD2_D_ADOPTION.md)
auf dem Arbeitsbranch 0.4. Neue `--method`-Auswahl und explizites
`catalog_method plan/adopt` folgen diesem Vertrag.
[SD2-C-T01](../../docs/SD2_C_VERIFICATION.md) ordnet die synthetischen Nachweise zu.
C ist nach separatem R01 über PR #410 integriert;
[D-V01](../../docs/SD2_D_VERIFICATION.md) liefert den gesondert beauftragten
Bestandsvergleich und Planungsstand vor der anschließenden F01-Übernahme/Aktivierung.

Einzelanalyse und frischer Import verwenden eine ausdrücklich übergebene
Definition. Das neue äußere Arbeitsverzeichnis enthält `catalog-context.json`
und das unveränderte geschlossene B-Bundle in `rating/`. Aktive Ratingquellen
enthalten keine vollständigen Spuren; das Arbeitsbundle bleibt der vollständige
externe Analysebeleg. Beispiel mit dem festen technischen Input:

```sh
python -m tools.puzzle_production.catalog_analysis analyze --method picross-difficulty-0.4 --production-mode mono --input tests/puzzle_production/fixtures/sd-runtime.json --work-dir artifacts/sd2-c-single --output artifacts/sd2-c-checked.json
python -m tools.puzzle_production.catalog_analysis import --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-c-single --output artifacts/sd2-c-imported.json
```

Für eine freigegebene neue Produktion bleibt der vorbereitende Weg
`candidate --design ... --matrix ... --logic ... --puzzle-id ... --runtime-revision ... --output ...`,
danach `analyze` oder `import`, abschließend
`rebind --input <fertige-Definition> --rating <checked.json> --production-mode mono|color --output <neue-checked.json>`.
Die geprüfte Datei geht als `--difficulty` an `target_adapter plan/register/update`.
Register/Update verlangen für neue oder tatsächlich geänderte Logik genau die
aktive Produktionsmethode; ohne Defaultdatei ist dies **0.3**. Ein 0.4-Checked-
Ergebnis aktiviert die Methode nicht. Einfarb-Color bleibt explizit Color.
Metadaten-Rebind erhält den ursprünglichen Analysebeleg einschließlich seiner
Methode, sofern Logik, Matrix und Produktionsmodus gleich bleiben. Ursprüngliche
Authoringbewertungen und Freigaben werden nicht ersetzt.

Auswahl und Übernahme sind getrennt. Die folgenden Aufrufe setzen einen
**isolierten synthetischen Checkout** und passende gebundene Dateien voraus;
sie sind kein Auftrag zur Ausführung am echten Bestand:

```sh
python -m tools.puzzle_production.catalog_analysis preview-checked --method picross-difficulty-0.4 --checkout /tmp/sd2-c-checkout --id pz-sd-synthetic --checked pz-sd-synthetic /tmp/checked.json --work-dir /tmp/sd2-c-preview --run-id synthetic-c --source-commit 0000000000000000000000000000000000000000
python -m tools.puzzle_production.catalog_analysis plan-adoption --checkout /tmp/sd2-c-checkout --work-dir /tmp/sd2-c-preview
python -m tools.puzzle_production.catalog_analysis adopt --checkout /tmp/sd2-c-checkout --work-dir /tmp/sd2-c-preview
```

`preview` analysiert nur die explizite Auswahl; `preview-checked` konsumiert
vorhandene geprüfte Ergebnisse. `--all` ersetzt die ID-Auswahl für einen ausdrücklich
beauftragten Gesamtlauf. Ohne `--method` bleibt auch hier 0.3. JSON/Markdown nennen
Alt-/Neumethode, Stufe, vollständiges 0.4-Assessment und offene Fälle. Unvollständige
Versuche erhalten keine Ersatzstufe und verdrängen keinen aktiven Altwert.
Plan/Adopt prüfen vollständige Quellen einschließlich Standarddatei; gleiche
Übernahme ist nur bei exakt passendem Zielzustand ein byte-/mtimegleicher No-op.

Explizite Aktivierung ist ein eigener Plan ohne Rating-/Runtimeänderung:

```sh
python -m tools.puzzle_production.catalog_method plan --checkout /tmp/sd2-c-checkout --expected-method picross-difficulty-0.3 --target-method picross-difficulty-0.4 --target-method-hash 5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf --output /tmp/sd2-c-activation.json
python -m tools.puzzle_production.catalog_method adopt --checkout /tmp/sd2-c-checkout --plan /tmp/sd2-c-activation.json
```

Der Plan bindet vollständige Quellen, erwartete Vorgängerrevision und beide
Methodenfreezes. `adopt` ändert ausschließlich `content/difficulty-method.json`
über das gemeinsame Journal. Nach Unterbrechung zuerst `content_registry recover`;
fremde Bytes bleiben mit offenem Journal erhalten. Exitcodes 0/2/4 bedeuten
Erfolg/Vertragsfehler/Abbruch. C aktiviert ausschließlich synthetische Checkouts.
Die echte Aktivierung, Analyse und Umstellung bleiben #406.

## SD2-B: Eigenständige Bewertung 0.4

Der [B-Vertrag](../../docs/SD2_CALIBRATION.md) bindet vorab festgelegte unabhängige
synthetische Referenzen, getrennte Validierung, genaue rationale Arithmetik und
den eingefrorenen Methodensatz. Der folgende Weg bewertet nur den ausdrücklich
übergebenen Input. 0.3 bleibt aktiv; gemeinsame Integration und reale Umstellung
gehören ausschließlich zu SD2-C/D.

```sh
python -m tools.puzzle_production.sd2_rating_cli analyze --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd2-rating-example
python -m tools.puzzle_production.sd2_rating_cli check --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-rating-example
python -m tools.puzzle_production.sd2_rating_cli rate --input tests/puzzle_production/fixtures/sd-runtime.json --analysis-bundle artifacts/sd2-example --output-dir artifacts/sd2-rated-raw
python -m unittest discover -s tests/puzzle_production -p 'test_sd2_rating.py' -v
```

Das Balkenbeispiel demonstriert nur die CLI, nicht den neuen B-Referenzsatz.
Die Hülle enthält exakt `analysis/` (unverändertes A-v1-Rohbundle),
`rating.json` und den deterministischen `report.md`. `rate` kopiert ein vorhandenes
A-Bundle bytegetreu und prüft es frisch; `check` rekonstruiert Rohprofile,
R4-Notwendigkeit und Bewertung unabhängig von gespeicherten Ergebnissen.
Jeder Einstieg prüft den vollständigen Methoden-/Quellenfreeze.

Alle drei Beiträge, Score, Stufe, Wert ohne Umfang und exakte Grenzabstände
bleiben sichtbar. Zahlen sind gekürzte `[Zähler,Nenner]`; Gleichheit gehört zur
höheren Stufe. Ohne vollständigen Liniennachweis oder separat nachgewiesenes
notwendiges R4 bleibt die Bewertung leer. R4 verwendet einen festen L5-Anker und
kennzeichnet Linienprofile als Präfixe. Keine menschlichen Minuten; bewertete
Fälle sind Modellschätzungen höchstens mittlerer Aussagekraft.

Analyse- und Prüfgrenzen entsprechen den oben aufgeführten A-Budgets;
`analyze` hat ein getrenntes Verifikationsbudget. Exit 0 heißt vollständig
geprüft, auch wenn stalled/contradiction keine Note erlauben. Exit 2/3/4/5
bezeichnen Eingabe-/Beleg-/Abbruch-/Technikfehler. Ein verifizierter abgebrochener
Präfix bleibt unrated und liefert Exit 4; Prüfabbrüche schreiben kein Rating.
Ausgabeordner müssen neu sein. Explizites R4 erfordert beide `--r4-proof` und
`--r4-baseline`; kein automatischer Paarlauf. [SD2-B-T01](../../docs/SD2_B_VERIFICATION.md)
bindet den historischen Lieferstand/Selbstreview; B ist nach separatem R01
über PR #409 integriert.

## SD-C1: Kandidat, geprüfter Input, Vorschau und Übernahme

[Daten-/Recoveryvertrag](../../docs/SD_CATALOG.md). Keine dieser Operationen läuft
automatisch bei Export, Registryprüfung, Build oder Spielstart. In C1 werden nur
synthetische Fälle geprüft; der echte Erstlauf und seine Übernahme bleiben SD-C2.
Alle Arbeits-/Ausgabepfade ausdrücklich wählen, außerhalb von `game/` und
`content/difficulty/`; neue Ausgaben dürfen nicht bereits existieren.

Nach endgültiger Deduktionsprüfung, vor redaktioneller Endfreigabe:

```sh
python -m tools.puzzle_production.catalog_analysis candidate --design <design.json> --matrix <matrix-array.json> --logic <logic.json> --puzzle-id <pz-ID> --runtime-revision 1 --output <work/provisional.json>
python -m tools.puzzle_production.catalog_analysis analyze --input <work/provisional.json> --production-mode <mono-oder-color> --work-dir <work/full-bundle> --output <work/checked.json>
```

`candidate` nutzt die validierte ZA-1-Farbabbildung; sein vorläufiger Reveal ist
keine Freigabe. `analyze` ruft die eingefrorenen SD-A/SD-B-APIs auf und prüft das
fertige Bundle vollständig. Den Produktionsmodus ausdrücklich aus dem geprüften
Design übernehmen: Schema 2 allein unterscheidet Mono und Einfarb-Color nicht.
Der Wrapper bindet den Modus an die analysierten Definitionsbytes in
`catalog-context.json`; das eingefrorene SD-B-Bundleformat bleibt unverändert.
Schon vorhandene Bundles werden ausdrücklich importiert:

```sh
python -m tools.puzzle_production.catalog_analysis import --input <runtime-or-provisional.json> --bundle <full-bundle> --output <checked.json>
```

Nur passende ausdrücklich übergebene `--r4-baseline <file> --r4-proof <file>`
ergänzen R4. Nach Farbremapping passen alte Produktionsproofs nicht automatisch.
Ohne Notwendigkeitsbeleg bleibt ein Linienfixpunkt `unrated`; kein versteckter
Paarlauf. `analyze`, `preview` und `import` bieten `--seconds` (120), `--max-lines`
(100000), `--max-rule-work` (20000000), `--max-waves` (80000), `--max-pair-work`
(20000000), `--max-pair-records` (250000). Analyse/Vorschau bieten dieselben
`--verify-*`-Grenzen separat. Vorab festlegen; Budgets ändern keine Methodengrenze.
Ein gültiger Bericht, auch `unrated`, beendet den Befehl mit 0; ungültige Daten
mit 2, ein nicht als Bericht abgeschlossener Budgetabbruch mit 4. Status/Grund
im Bericht sind maßgeblich, nicht allein der Prozessstatus.

Nach tatsächlicher Endfreigabe und unverändertem regulärem `target_adapter export`:

```sh
python -m tools.puzzle_production.catalog_analysis rebind --input <export/runtime/data/content/stem.json> --production-mode <mono-oder-color> --rating <work/checked.json> --output <work/final-checked.json>
python -m tools.puzzle_production.target_adapter plan --export <export> --checkout <checkout> --difficulty <work/final-checked.json>
python -m tools.puzzle_production.target_adapter register --export <export> --checkout <checkout> --difficulty <work/final-checked.json>
```

Rebind verlangt identische ID, Produktionsmodus, kanonische Logik und Zielmatrix; ursprüngliches
`rating.source` bleibt erhalten. Alternativ führt `--rebind-difficulty` im Plan/
Register/Update die ausdrücklich gewählte Neubindung durch. Neue Registrierung
und logisch geänderte Definitionen brauchen vollständiges 0.3. Für einen
Metadatenupdate mit vorhandener aktiver Bewertung genügt bei gleichem Modus/Logik/Matrix
`--rebind-difficulty`. Identische Legacy-Wiederholungen brauchen keine neue Analyse.
`plan-update`/`update` behalten zusätzlich ihren Erwartungshash, neue Paket-/Runtime-
Revision und vollständige ZA-1-Prüfung. Reine Bewertungsänderung benutzt sie nicht.

Neue checked-/aktive Hüllen verwenden v2 mit separatem `production_mode`.
Alte v1-Hüllen bleiben lesbar, aber ohne erfundene Modusherkunft: Rebind und neue
Integration benötigen eine frische modegebundene Analyse. `import` kann ohne
Kontextdatei nur checked-v1 liefern; es gibt keine nachträgliche Modusoption.
Ein Moduswechsel verlangt auch bei gleichen numerischen Hinweisen eine neue Analyse.

Ausdrücklich ausgewählte bestehende IDs werden in ein neues Arbeitsverzeichnis
analysiert; `--id` darf wiederholt werden, `--all` wählt ausdrücklich alle:

```sh
python -m tools.puzzle_production.catalog_analysis preview --checkout <checkout> --id <pz-ID> --id <weitere-ID> --source-commit <volle-SHA> --run-id <run-id> --work-dir <work/preview>
python -m tools.puzzle_production.catalog_analysis preview --checkout <checkout> --all --source-commit <volle-SHA> --run-id <anderer-run> --work-dir <work/all-preview>
```

Optional pro ID: `--r4 <pz-ID> <baseline.json> <proof.json>`. Vorab importierte
Inputs verwenden stattdessen `preview-checked` mit denselben Auswahlargumenten
und wiederholtem `--checked <pz-ID> <checked.json>`. Fehlende oder unvollständige
Fälle bleiben mit Altwert, Status/Grund und Bindung sichtbar; keine ID entfällt.
JSON und Markdown enthalten beobachtende Alt-/Neuverteilungen. `source-commit`
ist ausdrücklich benannte Provenienz; die tatsächlichen Datei-/Ausgangshashes
sichern die Übernahme, ohne Git oder Paketreplay im Analyzer vorauszusetzen.

```sh
python -m tools.puzzle_production.catalog_analysis plan-adoption --checkout <checkout> --work-dir <work/preview>
python -m tools.puzzle_production.catalog_analysis adopt --checkout <checkout> --work-dir <work/preview>
```

Erst `adopt` schreibt aktive Ratings und beide Dauerberichte. Unvollständige
Versuche ersetzen keine gültigen aktiven Werte. Identische Übernahme ist No-op;
alte Produktionsbelege, Definitionen, Revisionen, Kategorien und Saves bleiben.
Report-v2 bindet zusätzlich alle gelesenen Quellen. `plan-adoption` und `adopt`
prüfen vor einem No-op den erwarteten Übernahmezustand einschließlich dieser
Quellen; nach zwischenzeitlicher Kategorie-/Registry-/Ratingänderung stoppen beide
konkret ohne Mutation. Alte Report-v1-Journale und identische Wiederholungen bleiben
unter ihren ursprünglichen Bindungen unterstützt; die zusätzliche vollständige
Quellenbindung gilt für neue v2-Berichte.
Der gemeinsame Lock schützt Register/Update/Sync/Adoption. Nach Unterbrechung:

```sh
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

Recovery prüft vollständig vor Mutation und stellt eine gültige Altprojektion
her. Fremdänderungen erhalten Dateien und Journal; den Konflikt klären, nicht
den Lock löschen oder durch `sync-runtime` umgehen. Exakte KE-Altjournale bleiben
nur ohne ungebundene aktive Sidecars wiederaufnehmbar. Neue Formate und Grenzen
stehen im SD-C1-Vertrag.

Alle Quellen-/Recoverywege prüfen auch verwaiste oder falsch platzierte aktive
Ratingdateien. Nur `content/difficulty/<registrierte-ID>/rating.json` ist aktiv;
die erlaubten `reports/<run-id>/report.json|report.md` sind getrennt. Fremde und
aliasartige Dateien bleiben bei Blockade erhalten, statt einen Legacyfallback auszulösen.

## Linienverfahren und Ressourcen

Solver: Vorwärts-/Rückwärtserreichbarkeit eines Zellautomaten aus Gap- und
Blockfortschrittszuständen, Aufwand O(n·(Summe der Blocklängen + Blockzahl + 1)).
Übervolle Linien werden vorher erkannt. Die Warteschlange führt betroffene
kreuzende Linien nach; nur Domainausschlüsse, kein Probing/Backtracking.
`--order rows-first|columns-first|reverse` bestimmt die deterministische Reihenfolge.

Prüfer: separat implementierter DAG mit Knoten (vollständige Blockzahl, verbrauchte
Zellen) und Kanten für ganze Blockintervalle samt Pflichtseparator bei gleicher
Nachbarfarbe oder ein Leerfeld. Unterschiedliche Farben benötigen keinen Separator.
Intervallkompatibilität verwendet eigene Präfixsummen je vorkommender Farbe. Vorwärts-/Rückwärtserreichbarkeit
liefert die unterstützten Intervalle. Aufwand höchstens O(n²·(Blockzahl + 1)),
Speicher O(n·(Blockzahl + 1)); keine vollständigen Belegungslisten. Der Prüfer importiert
keine Solverroutine. Gemeinsam sind Datentypen, Schema, Domains, Budget und Hashes.
Vollständige Endraster werden zusätzlich durch direkte Länge-/Farbrunextraktion geprüft;
Fixpunkte durch jede Zeile/Spalte, Widersprüche durch die angegebene unmögliche Linie.

CLI-Limits: **2 MiB Logikdatei**, **8 MiB Mono-/64 MiB Farbnachweisdatei**.
Auch 200 Linien mit je 100 Hinweisen und maximal langen Farb-IDs passen unter 2 MiB
in kanonischer Speicherung. Maximal **Breite·Höhe·Vordergrundfarbzahl** Proof-Schritte:
jeder Schritt entfernt mindestens einen Wert; jede Zelle behält mindestens einen
von anfangs K+1 Werten. Für Mono bleibt die Grenze Breite·Höhe; für acht Farben
auf 100×100 sind es 80000. Eine konservative obere kanonische Proof-Größe mit
einzelnem Wertverlust je Zelle/Schritt, längsten IDs und vollen Enddomains liegt unter
64 MiB; der Grenztest rechnet dies aus und prüft den Loader auch oberhalb der alten
8-MiB-Grenze. Zusätzlicher beliebiger JSON-Whitespace bleibt durch das Dateilimit begrenzt.
`--seconds` (Standard 120) und `--max-lines` (Standard 100000, höchstens 1000000)
gelten kooperativ für die ganze Solver-/Prüferarbeit; `--max-lines 0` demonstriert
einen kontrollierten Abbruch. Eine einzelne Linienauswertung ist durch die
Dimensionen polynomial begrenzt. Die CLI erzwingt kein OS-RSS-Limit.

**Vorab festgelegte RP1-/RP2-A05-Budgets:** je Referenzfall 120 Sekunden einschließlich
Solve, Serialisierung, frischer Prüfung und Prozessstart; je isoliertem Prozess
512 MiB gemessener Peak-RSS auf Linux. Der Benchmark misst selbstständige Solve-
und Verify-Prozesse via `getrusage(RUSAGE_SELF).ru_maxrss` (Linux-KiB → Bytes).
Zusätzlich setzt jeder Worker `RLIMIT_AS=1024 MiB` als hartes virtuelles Speicherlimit;
dies ist ausdrücklich **kein** RSS-Limit/-Messwert. Der Parent erzwingt das gemeinsame
120-Sekunden-Prozesslimit. Fehlende RSS-Messung führt zu `accepted=false` (Windows),
auch wenn der logische Lauf erfolgreich ist. Neue Ausgabepfade für Wiederholungen verwenden.

Referenzen: 40×40/100×100 verschachtelte Balken mit variierenden Hinweisen,
Leer-/Füllzellen und echter Propagation; zusätzlich 100×100 mit je zwanzig
Einserblöcken pro Linie und `C(81,20)=4694436188839116720` Belegungsmöglichkeiten
je unbekannter Linie. Der letzte Fall bleibt ein geprüfter unvollständiger Fixpunkt.
Farbreferenzen: `color-woven-40`/`color-woven-100` mit wechselnden zusammenhängenden
Farbblöcken in beiden Achsen, Leerfeldern und tausenden partiellen Domainänderungen.
`color-sparse-100` stammt aus einem dünn besetzten diagonalen Vierfarbenraster;
20 Einserblöcke je Linie mit unterschiedlichen Nachbarfarben erlauben
`C(100,20)=535983370403809682970` Belegungen pro unbekannter Linie. Der unabhängig
geprüfte Fixpunkt bleibt unvollständig. Die drei Mono-Referenzen bleiben unverändert.
Diese technischen Referenzen behaupten keine Motiv-/Pilotqualität.

## CI und Artefakte

[Package CI](../../docs/CI_WORKFLOW_V2.md) wählt `production.solver/images/adapter/catalog`
über den aktuellen Paketplan. [Fachgruppen](../../docs/CI_A_SELECTION.md) und
`tools/production_contract.py` binden Tests und Integrationen. Kein pauschaler
Fachlauf bei jedem PR/Main-Push. Der eigene Fachtestort liegt außerhalb des
`tools`-Discoverys. Allgemeiner Windowsbau und Produktionsnachweis sind getrennt.

Der Solver-Benchmark (`picross-benchmark-v2`) bindet Head, Basis, tatsächlichen
Checkout, Profil/Profilhash und Eingänge je Fall. Mono- und Farbreferenzen werden
nicht gleichgesetzt. `RP1_SOURCE_HEAD`/`RP1_BASE_COMMIT` bleiben technische
Umgebungsnamen des gemeinsamen Läufers. Originale umfassen Logik, Proof, Ergebnis,
frische Prüfung, Prozessmessdaten und Logs; der unabhängige Reader prüft sie im
selben Job, bevor temporäre Daten entfernt werden. Upload nur mit aktuellem Zweck
und Ablauf. Die Referenz-Prozessbudgets oben sind funktionale Benchmarkgrenzen,
keine maximale CI-Gesamtlaufzeit.

[puzzle-production.yml](../../.github/workflows/puzzle-production.yml) bleibt ein
manueller/wiederverwendbarer Diagnoseworkflow ohne eigenen PR-/Push-Trigger.
Sein ausdrücklich beauftragter Belegtransport wird im Diagnosevertrag beschrieben;
er begründet keinen Standardupload der Haupt-CI. Die Machbarkeitsphase RP1–RP6 ist
historisch abgeschlossen; neue Produktionspakete benötigen eigene Aufträge.

## RP-3: isolierte Image-Umgebung und reale Befehle

Pillow **exakt 12.3.0**, ausschließlich für Bildbefehle/-tests. Die CI installiert
[requirements-image.txt](requirements-image.txt) in einer temporären venv. Lokal:

```sh
python3 -m venv .venv/rp3
.venv/rp3/bin/python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/rp3/bin/python -m tools.puzzle_production import-image --input examples/rp3/source.png --design examples/rp3/design.json --output-dir artifacts/rp3-import
.venv/rp3/bin/python -m tools.puzzle_production export-p1 --bundle artifacts/rp3-import --variant area-128 --reveal examples/rp3/reveal.svg --name Fliegenpilz --output-dir artifacts/rp3-export
.venv/rp3/bin/python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
```

Unter Windows entsprechend `.venv/rp3/Scripts/python.exe`; keine globale
Installation. Jedes Ausgabeziel muss **neu/nicht vorhanden** sein. Die mitgelieferte
[reale Quelle samt Produktionsbundle](../../examples/rp3/README.md) enthält bereits
einen offline öffnenden Vergleich: `examples/rp3/production/index.html`.
PNG/JSON/Briefing können ohne Dienst an ChatGPT/Codex übergeben werden.

### Entwurf, Normalisierung und Rasterverfahren

`picross-image-design-v1` hat exakt die Schlüssel des
[Beispielentwurfs](../../examples/rp3/design.json). `source_id` und Varianten-/Farb-IDs
folgen `[a-z][a-z0-9_-]{0,31}`, `empty` ist reserviert. Herkunft, Nutzungsgrundlage
und Briefing haben jeweils 1..4096 Zeichen. `working_mode` ist ausdrücklich
`faithful` oder `free`; Eingriffe sind im Briefing festzuhalten. Zielbreite/-höhe
1..100, Rechtecke/1D eingeschlossen. Palette 1..8 eindeutige Vordergrund-IDs und
`#rrggbb`-Werte; Mono verlangt genau `ink`. Hintergrund/Leer-RGB ist von jeder
Vordergrundfarbe verschieden, auch von Weiß. Palette wird nach ID sortiert.

PNG/JPEG: 32 MiB kodierte Bytes, 8 Millionen dekodierte Pixel, höchstens 8192 je
Quellachse, ein Frame. Beschädigte/trunkierte Dateien, Animation, andere Formate,
High-depth-Modi und unprofiliertes CMYK werden ausdrücklich abgewiesen. Unterstützt
werden 1/L/LA/P/RGB/RGBA sowie profiliertes CMYK. EXIF 1..8 einschließlich Spiegelung
wird angewendet. ICC wird mit LittleCMS nach sRGB, perceptual intent 0, konvertiert;
ungültiges/unpassendes ICC wird abgewiesen. Ungetaggtes RGB/Grau gilt als sRGB;
abweichendes PNG-gamma ohne sRGB-Tag/ICC wird abgewiesen. Alpha bleibt separat
erhalten. Normalisiertes PNG: RGBA, ohne EXIF/ICC/Text; Metadaten dokumentieren
Quellmodus/-maße, Orientierung, Behandlung und ursprünglichen ICC-Hash.

`crop=[left,top,right,bottom]` verwendet orientierte Quellpixel und muss vollständig
innerhalb des Bilds liegen. `fit=exact` fordert gleiche Seitenverhältnisse.
`contain` wählt ausdrücklich zentrierten Leerraum statt Strecken: Zielrechteck
mittels ganzzahligem Verhältnis, mindestens eine Zelle je Achse; Restpixel rechts/
unten. Sehr schmale Verhältnisse können dadurch um eine Zielzelle quantisiert sein.
RGBA wird auf den gewählten Hintergrund komponiert, dann mit Pillow BOX auf
Zellauflösung reduziert; Alpha wird separat mit BOX gemittelt. Unter
`alpha_below` (1..255) bleibt die Zelle leer. Rechnen erfolgt im kodierten sRGB,
keine behauptete lineare/perzeptuell optimale Bildabstraktion.

Höchstens acht Varianten: `area` nutzt im Mono-Modus Luminanz `< threshold`
(0..255), im Farbmodus nächstes RGB per quadriertem euklidischem Abstand zur
Palette einschließlich Leer. Gleiche Entfernung: Leer, dann lexikografische ID.
Bei Farbe ist der Area-Schwellwert wirkungslos und dennoch explizit gespeichert.
`contour` nutzt FIND_EDGES auf der Zellluminanz, innere Werte `> threshold`,
äußerste Zeile/Spalte stets leer (Pillow erhält dort sonst Quellwerte). Ausgewählte
Konturzellen werden Mono-ink oder der nächsten Farbe zugeordnet. 1D-Konturen sind
damit leer; Area bleibt nutzbar. Finale Werte sind ausschließlich IDs, keine
Zwischenfarben. Hinweise werden durch vollständige Länge-/Farbruns abgeleitet.

### Identität, Nachweis und P1-Grenze

`picross-image-candidate-v1` führt Revision 1, Quellen-ID, normalisierten Datei-
SHA-256, kompletten Entwurf/Variante, Werkzeug `rp3-image-1`, Pillow und tatsächlich
verwendete JPEG-/LittleCMS-/zlib-Versionen, Matrix und normalisierten Logikhash.
Sein SHA-256 verwendet die kanonischen JSON-Bytes des Kerns, ohne das `id`-Feld.
Messzeiten sind ausgeschlossen. Gleiche Normalisierung/Parameter/Versionen liefern
denselben Kandidaten. Unterschiedliche Codecbuilds können identische Pixel anders
komprimieren und erhalten deshalb unterschiedliche neue Kandidatenkennungen.
Bestehende Bundles behalten ihre tatsächlichen Produzentenbytes/-versionen.
Replay verlangt dieselbe Werkzeug-/Pillowversion und zusätzlich **exakte** RGBA-
Pixel-/Normalisierungsmetadaten-Gleichheit zur neu dekodierten Originaldatei,
neu berechnete Matrix/Hinweise und exakte Vergleichsrasterpixel. Schon ein
abweichendes Normalisierungspixel wird abgewiesen. JPEG/ICC-Rundungsunterschiede
werden damit nicht toleriert. Keine plattformübergreifende Byteidentität versprochen.

`picross-image-manifest-v1` bindet Originalbytes, normalisiertes PNG, Entwurf,
Kandidat, Logik, tatsächlichen Proof, Ergebnis, Zell-PNG, HTML und Briefing per
Dateihash. Alle Kandidaten bleiben vergleichbar, auch bei Fixpunkt/Abbruch.
Solver und unabhängiger Prüfer erhalten ausschließlich den bestehenden v1-/v2-
Logikeingang ohne Matrix/Bild/Motiv. `--seconds` 120 und `--max-lines` 100000
gelten getrennt pro Solver/Prüfer je Variante, keine gemeinsame Bildlaufzeitgrenze.
OS-Prozess-/RSS-Limits werden vom Import selbst nicht behauptet. CLI-Fehlercodes
entsprechen dem Kern; `import-image` meldet bei erfolgreicher Bundle-Erstellung
`produced`/0, auch wenn einzelne Kandidaten **nicht** zertifiziert sind.

`export-p1` rekonstruiert Original→Normalisierung→Matrix→Hinweise, prüft sämtliche
gebundenen Dateien und replayt den **geschriebenen** Proof unabhängig neu.
Ergebnisflags/Exitcode reichen nicht. Nur `solved`/zertifiziert und Singleton-
Enddomains gleich der beabsichtigten Matrix erlauben Export. Geänderte Raster,
Hinweise oder Farbsemantik binden andere Logik; ein alter unpassender Proof scheitert.
Reine RGB-/Assetänderungen können Logik erhalten, erfordern aber aktuelle
Herkunft/Identität/Assetbindung und separate Motivkontrolle.

Erster Adapter `rp3-p1-square-mono-1`: ausschließlich quadratisches Mono mit
mindestens einer Füllzelle, feste neutrale ID **F-04**, Revision 1..1000000,
Name 1..128 Zeichen erst nach Abschluss. Farb-IDs werden deterministisch auf
1..N, Leer auf 0 abgebildet; keine Domain-Bitmasken im P1-Raster. Schema 2 mit
exakt abgeleiteten Hinweisen, `res://art/f04.svg` als gebundener Reveal.
SVG: lokale begrenzte Shape-/Gradientressource, quadratische numerische Maße,
mindestens zwei Bildpixel je Zelle, höchstens 8192; keine externen Referenzen/
Ausführung/Entities. PNG-Enthüllungen und Rechteck-/Farbexporte werden in diesem
Adapter ausdrücklich abgewiesen. Kein automatisches Überschreiben/Registrieren
beliebiger Inhalte, keine öffentliche Importoberfläche oder zweite Spiellogik.

`picross-p1-export-v1` bindet Produktionsmanifest, Kandidat, Logik/Proof,
Definition/Revision, Farbzuordnung und Reveal-Dateihash. Der historische
RP3-Demo-Replay gehört nicht mehr zum aktiven Checkout. Für neue Inhalte gilt
ZA-1 mit expliziter Freigabe, Kategorie und Registrierung.

## RP-5: motivgeschützte Reparatur

Für ausdrücklich autorisierte feste manuelle Mono-Entfernungen ohne Suchlauf
unterstützt ZA-1 zusätzlich einen versionierten Replay-/Autorisierungsweg.
Vertrag, `--manual-authorization`, unveränderte Originalbindungen und v3-Export:
[ZA-1: manuelle Ableitungen](../../docs/ZA1_ADAPTER.md#autorisierte-manuelle-ableitungen).
Dieser Weg ersetzt weder RP-5 noch dessen Such-/Nachweisvertrag.

Die additive v2-Autorisierung unterstützt auch feste manuelle Einfügungen in
gespeicherten Mono-Rasterimporten und eine ausdrücklich an die Endauswahl
gebundene Randregel-Ausnahme. Beide RP-3-Bündel, sämtliche feste Edits und der
Endproof werden frisch geprüft; Original-ZIP/Handoff/Inventar bleiben unverändert.
Schema, Grenzen und synthetische Tests: [ZA-1-v2-Vertrag](../../docs/ZA1_ADAPTER.md).

Die additive v3-Autorisierung bindet bereits versiegelte feste Farbkorrekturen
mit nachträglicher menschlicher Motiv-/Parameterannahme. Sie replayt eine begrenzte
Kette gespeicherter Edits mit exakten Schutzmasken und prüft sämtliche RP-3-/RP-5-
Herkunfts- und Proofbindungen frisch. Originale bleiben unverändert, alle übrigen
Inhaltsgates einschließlich Randregel Pflicht. CLI bleibt `--manual-authorization`,
Exportformat v3. [ZA-1-v3-Vertrag](../../docs/ZA1_ADAPTER.md).

Die additive v4-Autorisierung unterstützt feste manuelle Farbkorrekturen aus
einer bereits freigegebenen Motivvorlage. Original-ZIP, Handoff, Inventar und
Motivfreigabe bleiben unverändert; Parameter werden am Originalimport geprüft,
danach die exakte feste Zellkette und sämtliche unabhängigen Proofs. Alle
Inhaltsgates und echte Endabnahme bleiben Pflicht. CLI und v3-Exportformat
bleiben gleich. [ZA-1-v4-Vertrag](../../docs/ZA1_ADAPTER.md).

V5 ergänzt ausdrücklich freigegebene feste Farbkorrekturen aus einem unabhängig
bestätigten ursprünglichen `stalled`-Direktimport. Die Originalquelle und der
vollständige Fixpunkt werden frisch geprüft; alle korrigierten Kindstufen
benötigen vollständige Zertifikate. Eigentümerbindung, Masken und Endabnahme
bleiben Pflicht; v1–v4 werden nicht gelockert. CLI/Exportformate bleiben gleich.
[ZA-1-v5-Vertrag](../../docs/ZA1_ADAPTER.md).

[Versionierter Vertrag, Status-/Exitcodes, Schema-/Hash-/Ressourcengrenzen](../../examples/rp5/README.md),
[Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP5_VERIFICATION.md), [Offlinevergleich](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp5/index.html).
Gleiche isolierte Image-Umgebung; keine neue Abhängigkeit. P1-Export und Spiel
bleiben unverändert; `export-p1` weist das eigene Reparaturmanifest zurück.

```sh
python -m tools.puzzle_production.repair search --reference <aktuelles-importbundle> --plan <reparaturplan.json> --output-dir <neues-reparaturbundle>
python -m tools.puzzle_production.repair verify --reference <aktuelles-importbundle> --bundle <reparaturbundle> --report <neuer-pruefbericht.json>
```

Alle Ausgabepfade neu. Während der Produktion rekonstruiert der Verifier jeden
Kandidaten und Proof unabhängig, auch bei Nichtfund/Abbruch. Ein ursprünglicher
Abbruch wird nicht zur logischen Freigabe aufgewertet. Vorher/Nachher, feste
Änderungen und Schutzmaske gehören bis zur Endabnahme zum aktuellen Paket.
Die CI prüft das allgemeine Verfahren mit synthetischen Eingängen; der alte
RP5-Korpus, seine Suchpläne und der separate Replayjob werden nicht benötigt.

## Historische Produktionen und Abschluss

RP3-Demo, RP4-Vergleichskorpus, RP5-Korpusreplay, RP6-Sechserpilot und VS1-Produktion
werden im aktuellen Checkout nicht neu aufgebaut. Für historische Untersuchungen
steht der [damalige vollständige Stand](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/tools/puzzle_production/README.md)
zur Verfügung. CI2-B entfernt nach aktuellem Leserabgleich die ausschließlich historisch
verwendeten `rp4.inspect_trial`-/`rp5.unpack_archive`-Hilfen samt sechs Tests.
RP6/`export_p1`, aktuelle Größen-/Codecgrenzen und die aktive Archiveingangsprüfung
in `authoring_package.open_package()` bleiben erhalten.

Nach endgültiger Integration auf main:

```sh
python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <main-SHA> --puzzle-id <pz-ID>
```

[Authoring §9](../../docs/ai-workflows/PUZZLE_AUTHORING.md) und
[Integrationsformat](../../docs/ZA1_ADAPTER.md) regeln die Bereinigung.
Bestandsprüfungen lesen danach Runtimehashes und kompakte Integrationsdaten,
keine Quellen, Proofs, ZIPs oder Produktionsreplays. Die Entwicklung neuer Rätsel
verwendet weiterhin vollständige neue Eingänge/Freigaben und technische Prüfung.

Nachträgliche integrierte Bildarbeit besitzt einen eigenen revisionsgenauen Abschluss:

```sh
python -m tools.puzzle_production.target_adapter retire-reveal-production --checkout . --integrated-commit <main-SHA> --authoring-revision <pz-ID> <Authoringrevision>
```

Vorher `origin/main` aktualisieren. `--authoring-revision ID REVISION` ist wiederholbar;
alle ausgewählten Revisionen werden vor der ersten Löschung geprüft. Der enthaltene
Main-Stand muss den registrierten Authoringrecord, die finale Freigabe und exakt die
aktuelle Bildquelle binden. Ungültige Quellen, offene Journale, fremde Dateien,
Index-/Stagingkonflikte und unvollständige Entfernung blockieren. Nur der ausgewählte
Revisionsordner und dessen Indexzeile entfallen; andere, auch offene Revisionen bleiben.
Originalpaket beziehungsweise `picross-integrated-content-v1`, aktuelle Bildrecords,
Freigaben, Herkunft, Notices, Runtime und Ratings werden nicht geschrieben.
Erneuter Aufruf nach vollständiger Entfernung mit demselben Main-Beleg ist ein No-op
einschließlich mtimes. Kleine historische Index-/Record-/Freigabedaten und Git-Objekt-IDs
genügen; historische ZIP-Blobs werden nicht aus Git geladen oder rekonstruiert.
Vorhandene lokale Arbeitsdateien werden zum Bytevergleich gehasht. Der Befehl erstellt nur
einen prüfbaren Arbeitsbaumdiff. Fehler während einer tatsächlichen Dateisystemoperation
sind kein erfolgreicher Abschluss; eine Teilentfernung blockiert den nächsten Aufruf
und muss anhand des Git-Diffs geklärt werden. Kein automatisches Wiederherstellen.

Ab SD-C1 bleiben zusätzlich die kompakte aktive Bewertung,
ihre Eingangsbindungen und der gebundene Methoden-/Referenzstand außerhalb
versiegelter Produktion erhalten. Neue Bewertung nutzt dann Runtime-Logikeingänge
nach SD-D09/D10; sie verlangt keinen allgemeinen Produktions-Replay und keine
Wiederherstellung bereinigter Produktionspakete.

## KU-B: Hinzugefügt-Metadaten

`catalog_added` validiert ID-gebundene Sidecars und dauerhafte Quellenbelege;
Registryprojektion, Registrierung, Update, Sync, Bewertungsadoption und Recovery
verwenden denselben Transaktionsweg. Neue Runtime ist v4; alte exakte v2/v3 bleiben
lesbar. Der separate historische Nachtrag läuft ausdrücklich und ohne Analyse:

```powershell
python -m tools.puzzle_production.catalog_added_history plan --root . --run <run> --base <vollstaendiger-main-SHA> --repository venomenon328/picross --output <plan.json>
python -m tools.puzzle_production.catalog_added_history adopt --root . --plan <plan.json>
python -m tools.puzzle_production.catalog_added_history adopt --root . --plan <plan.json> --apply
```

Nur `plan` liest Git und optional eindeutig gebundene gemergte PR-Vorgeschichten.
Direkte bereits geprüfte Erstregistrierungsbelege können mit `--direct-evidence`
als JSON-Liste übergeben werden. `adopt` ohne `--apply` bleibt lesend; beide Wege
prüfen vollständige Quellbindungen. Eine identische Übernahme ist ein echter
Byte-/mtime-No-op. Bestehende Metadaten bleiben bei Folgeplänen erhalten, neue IDs
oder geänderte Quellen verlangen einen neuen Plan. Fremde Bytes blockieren
Recovery vor Mutation. Details: [KU-B-Vertrag](../../docs/CATALOG_SORTING.md),
[Bestandsplan](../../docs/KU_B_BACKFILL.md).

## AT: Noch zu implementierender Bildupdateweg

Der freigegebene [AT-A-Vertrag](../../docs/REVEAL_TRANSPARENCY.md) verlangt eine
eigene Bildrevision mit neuer tatsächlicher Freigabe und nachvollziehbarer
Alt-/Neuhashbindung außerhalb historischer Produktions-/Integrationsbelege.
PNG-Alpha wird durch den bestehenden Revealexport bereits bytegleich erhalten;
der Austausch eines registrierten Bilds benötigt dennoch den zusätzlichen
abgesicherten Weg. Ein bloßes Überschreiben des PNGs oder nachträgliches
Umschreiben seiner alten Freigabe-/Manifestbindung ist keine gültige Übernahme.

P01 legt vor der ersten betroffenen Codeänderung die exakten Eingänge, Pfade,
Felder, Versionen, Grenzen und die nachfolgende Soll-Syntax gemeinsam in
[ZA-1](../../docs/ZA1_ADAPTER.md), [Projektion](../../docs/CATEGORIES.md) und dem
[Transaktionsvertrag](../../docs/SD_CATALOG.md) fest. Die AT-A-Implementierung
und ihr Prüfstand sind in [AT-A-T01](../../docs/AT_A_VERIFICATION.md) gebunden.
Lesender Plan, aktuelle
Erwartungshashes, gemeinsame Quellenprüfung, versionierter Binärersatz,
kontrollierter Rollback und echte Wiederholungs-No-ops gehören zusammen.
Ein zulässiger Altstand ohne neue Bildquelle und eine vorhandene ungültige
Bildquelle bleiben unterscheidbar; fremde Bytes werden einschließlich Journal
erhalten.

Reine Bildupdates erhalten Definitionen, Runtime-Revisionen, Raster/Hinweise,
IDs/Keys, Ressourcenpfade, Slots, Kategorien, Ratings und Hinzugefügt-Daten
bytegleich. Keine neue Analyse, Zertifizierung oder Wiederherstellung gelöschter
Produktionspakete. Bestehende Register-/Rasterupdate-/Sync-/Adopt-/Cleanup-/
Recoverywege müssen die aktive Bildbindung gemeinsam erhalten; alte exakte
Formate werden nicht gelockert. Synthetische technische Regressionen gehören
zu AT-A, konkrete Bestandsfreistellung, Bildabnahme und Motivprüfung zu AT-B.

### AT-P01-D04 · CLI für Bildrevisionen

Eigener Moduleinstieg `tools.puzzle_production.catalog_reveal`. Genau zwei
Unterbefehle, keine automatische Bestandsauswahl, kein Force/Resume/Skip-Schalter:

```sh
# Nur explizit freigegebene Bildrevisionen; keine automatische Bestandsauswahl.
python -m tools.puzzle_production.catalog_reveal plan --checkout <checkout> --id <pz-ID> [--id <weitere-ID>] --input <externe-anfrage.json> --output-dir <neuer-externer-planordner> [--seconds 300]
python -m tools.puzzle_production.catalog_reveal adopt --checkout <checkout> --plan <planordner/plan.json> [--seconds 300]
# Gemeinsamer Recovery-Einstieg, einschließlich AT-Binärjournalen:
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

`--checkout`, `--input`, `--output-dir`, `--plan` sind einzelne Pfadargumente,
`--id` wiederholbar, mindestens einmal, eindeutig und kanonisch. Keine `--all`-
Option oder implizite Auswahl. Anfrageliste und ID-Auswahl stimmen exakt überein;
beide werden lexikografisch normalisiert, doppelte IDs bleiben Fehler.
`--seconds` Ganzzahl 1…300, Default 300, kumulative monotone Deadline vom ersten
Eingabelesen bis zur Abschlussprüfung; keine Identitätswirkung. Recoverybudget
und Unterbrechungsregeln stehen im Transaktionsvertrag. Argparsefehler Exit 2.

Alle Eingangsbilder liegen neben/unter der externen Anfragedatei; relative
Pfade nach ZA-1, keine Links/Hardlinks/Reparsepunkte/Traversal oder Kollisionen.
Die geprüften absoluten Ein-/Ausgabewurzeln müssen außerhalb des gesamten
Checkouts liegen und dürfen einander nicht überdecken. Kein automatisches Laden
von URLs/Git/Chats. `plan` erzeugt nur einen **neuen nicht vorhandenen** externen
Ordner; ein vorhandener leerer Ordner ist ebenfalls Fehler. Darin exakt
`plan.json`, `images/<pz-ID>.png|svg` (neu) und `previous/<pz-ID>.png|svg` (alt),
je mit zur vorhandenen Revealendung passendem Suffix. Alte Live-Bildbytes werden
für die unabhängige Altprüfung beim Wiederholungs-No-op ebenfalls extern gesichert.
Bildbytes werden unverändert kopiert; keine Formatkonvertierung oder
Bildbearbeitung. Keine zusätzlichen/aliasierenden Dateien. Fehler dürfen ein
als unvollständig bezeichnetes externes Arbeitsverzeichnis hinterlassen; ohne
vollständig geschriebenen und frisch geprüften Plan ist es kein `adopt`-Input.

Inputformat `picross-reveal-request-v1`, exakt `format,entries`.
1…10000 Zeilen, je exakt `id,image,approval,provenance,notice_append`.
`image` ist der sichere relative Eingangsbildpfad; `approval` und `provenance`
sind die vollständigen geschlossenen Objekte nach ZA-1, keine Dateiverweise.
`notice_append` ist null für identische Notice oder nichtleerer UTF-8/LF-Text
ohne BOM/NUL, endet LF; Zielnotice ist exakt alte Notice + LF + dieser Text.
Das alte Präfix bleibt erhalten, Gesamtlimit 64 KiB. Freigabe bindet den Hash
dieser vollständigen Zielnotice. Nur Bildrevisionen mit tatsächlich anderen
Bildbytes sind planbar; bereits erreichter Stand wird durch denselben Plan
wiederholt, nicht durch künstliche neue Revision einer identischen Datei.

PNG/SVG-Grenzen bleiben: 32 MiB je Datei, 8192 je Achse, höchstens 8000000 Pixel,
Detailauflösung mindestens zwei Pixel je aktueller Rasterzelle; lokales begrenztes
SVG-Profil bis 10000 Elemente ohne externe Referenzen/Ausführung/Entities.
Kein JPEG oder Endungswechsel am bestehenden Pfad. PNG wird vollständig geprüft,
keine Animation/trunkierten Daten; vorhandene gültige Altformate bleiben erhalten.
Transparenzqualität ist eine tatsächliche Bildentscheidung nach AT, kein
automatisches Akzeptieren allein wegen eines Alphakanals.
Anfrage maximal 8 MiB, Plan-JSON maximal 128 MiB, bis 10000 Zeilen;
kopierte alte und neue Bilder zusammen maximal 96 MiB. JSON-/String-/Tiefen-/Hashregeln wie
ZA-1, sämtliche Objektfelder exakt. Engeres Journal-/Zielrecordlimit gilt schon
bei Planung: ein nicht journalisierbarer Mehrfachplan darf nicht erfolgreich
ausgegeben werden. Zu große Anfragen ausdrücklich aufteilen, keine Teilübernahme.

### Gespeicherter Plan und Ergebnis

`picross-reveal-plan-v1` hat exakt
`format,ids,snapshot,entries,writes,plan_hash`. Keine Zeit/Git-HEAD/absoluten
Maschinenpfade im Identitätskern; `plan_hash=H(Plan ohne plan_hash)` nach ZA-1.
Datei exakt kanonisches JSON plus LF. `ids` ist die eindeutige sortierte Auswahl.

| Feld | Geschlossener Untervertrag |
| --- | --- |
| `snapshot` | Exakt `sources,namespaces`. `sources` ist die vollständige Pfad→Dateihash/null-Map aus T/K des Transaktionsvertrags, einschließlich erwarteter AT-/Rating-/Added-Abwesenheiten und erlaubter fehlender neuer Textziele; maximal 100000 Pfade. `namespaces` exakt `reveals,difficulty,added,packages`, jeweils lexikografisch sortierte Liste aller bei der Quellenprüfung relevanten regulären Dateipfade, ohne doppelte Pfade. Leere erlaubte Verzeichnisse haben keine Identitätswirkung. |
| `entries[]` | Sortiert nach Auswahl, je exakt `id,old_image_revision,new_image_revision,binding_hash,old_reveal,new_reveal,old_record,new_record,old_notice,new_notice`. Altbildrevision 0 nur bei noch fehlendem Record, sonst letzte; neue genau +1. Bindung ist aktuelle geprüfte Bindung beziehungsweise neue erste Bindung aus Altproduktion. |
| `old_reveal` | Exakt `file,sha256,bytes`, `file` genau `previous/<id>.<vorhandene-Endung>`, externe unveränderte Kopie der geprüften alten Live-Bildbytes, nicht null. |
| `new_reveal` | Exakt `file,sha256,bytes`, `file` genau `images/<id>.<vorhandene-Endung>` im Planordner, Hash/Bytezahl der kopierten neuen Bytes. |
| `old_record` | Null bei bisher fehlender Quelle, sonst exakt `text,sha256`, ursprünglicher vollständiger kanonischer UTF-8-Record samt LF und Dateihash. |
| `new_record` | Exakt `text,sha256`, vollständige nach Appendregel hergeleitete neue Quelle, inklusive Freigabe/Herkunft/Historie; nicht null. |
| `old_notice,new_notice` | Exakt `text,sha256` nach ZA-1; unveränderte Notice ist in beiden gleich. |
| `writes[]` | Nur tatsächlich geänderte Ziele, lexikografisch nach Pfad; je exakt `path,kind,old_sha256,new_sha256,bytes`. `kind` ist `binary-replace`, `text-add` oder `text-replace`; `bytes` neue Dateibytes, positiver Integer. Althash nur bei Textneuanlage null. |

`old/new_record.sha256` sind Dateihashes, `record_hash` innen ist der eigene
kanonische Objekthash. Alle Inhalte/Hashes/Bytezahlen werden selbst berechnet und
bei `adopt` neu geprüft. Schreibpfade werden **ausschließlich** aus geprüfter
Registry/ID hergeleitet und gegen `writes` exakt verglichen. Keine Eingabepfade
in den Checkout kopieren. Alt-/Neubildgrößen und Notice-/Recordgrößen folgen
ihren strengeren Einzelgrenzen. Ganze Plandatei und Bildinventar werden beim
Planabschluss frisch gelesen und unmittelbar vor sowie unter Lock erneut geprüft.

`adopt` konsumiert genau diesen unveränderten gespeicherten Plan; keine neue
Freigabe, ID-Auswahl oder Bilddateioption. Vollständige Quellen-/Namespacebindung
erneut prüfen, Alt-/Zielzustand isoliert validieren, Journal nach SD_CATALOG
erzeugen, gemeinsame Transaktion ausführen, abschließend den Zielcheckout prüfen.
Geänderter Registry-/Kategorie-/Runtime-/Definitions-/Rating-/Added-/AT-/Bild-/
Notice-/Produktionsstand einer beliebigen gebundenen ID ist stale. Keine neue
Analyse, kein Produktionsreplay allein wegen des Bildwechsels.

**Eigener No-op:** Alle `writes` müssen exakt ihre vollständigen eigenen Zielbytes
besitzen, sämtliche übrigen Quellen und Inventare weiterhin passen. Hinzugekommene
eigene AT-Recordpfade werden nur im rekonstruierten Namespaceinventar entfernt. Die
gebundenen Alttexte/Bildhashes werden nur im Speicher eingesetzt und ergeben
exakt den ursprünglichen Snapshot; der ursprüngliche Altcheckout wird ebenfalls
isoliert geprüft. Planbilder, Freigaben, Historie, Zielrevisionen und Recordbytes
müssen vollständig passen. Das Erreichen nur einer Teilmenge ist kein No-op.
Bei offener Transaktion zuerst Recovery, niemals No-op am Lock vorbei.
Erfolg vor Journalanlage, ohne Byte-/Revisions-/mtimeänderung oder Rewrite.
Fehlendes Ziel, andere Freigabe, ähnliche Pixel oder inzwischen dritte Bildrevision
blockieren als stale/conflict. Ein alter Plan nach Cleanup ist ebenfalls stale.

Stdout ist genau ein JSON-Objekt `picross-reveal-result-v1`, exakt
`format,status,plan_hash,ids,changes,error,recovery_required`.
`status`: `planned,adopted,no-op,invalid_input,aborted`; `plan_hash` Hash oder
null falls noch kein gültiger Plan ermittelt; `ids` geprüfte sortierte Auswahl
oder leere Liste vor gültiger Auswahl; `changes` bei `planned/adopted` exakt
`writes`, sonst `[]`. `error` null bei Erfolg, sonst exakt `code,message`:
Code `invalid_input,stale,conflict,io_error,resource_limit,interrupted`, Nachricht
1…2048 Zeichen, keine Secrets. `recovery_required` Boolean, true ausschließlich
bei erhaltenem offenen Lock oder konkret blockierendem Journalstagingrest.
Kein zusätzliches dauerhaftes Ergebnisformat: stdout darf extern protokolliert
werden; die dauerhafte Freigabe-/Revisionshistorie steht im aktiven Record.

| Exit | Ergebnis und Grenze |
| --- | --- |
| 0 | Nur `planned`, `adopted`, `no-op`; vollständige Prüfung erfolgreich. `planned` verändert keine Repositoryquelle. |
| 2 | Ungültiger/blockierter Eingang, stale Plan, Fremdkonflikt oder gewöhnlicher Datei-/Schreibfehler. Nach Mutation nur mit erfolgreichem Rollback oder ausdrücklich erhaltenem Journal samt `recovery_required=true`. |
| 4 | Zeit-/Speicher-/Signalabbruch; keine Erfolgsaussage. Journal-/Rollbackzustand nach Transaktionsvertrag. |

Unbekannte Optionen sind Fehler; kein Exit 0 für Teiladoption. Harter Kill kann
kein stdout garantieren. Der bestehende Recoveryeinstieg behält seine Ausgabe
`rolled-back/registered=false` bei Erfolg und seine 0/2/4-Konvention.

## HP-I1b2: eigenständiger Hintergrundwechsel und revisionsgenauer Abschluss

[Paketentscheidung](https://github.com/venomenon328/picross/issues/561#issuecomment-6763700809) und
[vollständiger Normvertrag §11](../../docs/PUZZLE_BACKGROUNDS.md#11-hp-i1b2--eigenständiger-hintergrundwechsel).
Pillow exakt 12.3.0 in der oben beschriebenen isolierten Imageumgebung; nur ein
bereits gültig hintergrundgebundenes Ziel je Adoption. Die echte Capability
folgt HP-I2; Legacy-Nachrüstung bleibt geschlossen, Raster-/Revealneubindung
vorhandener Hintergrundziele verwendet HP-I1c.

```sh
python -m tools.puzzle_production.catalog_background_change store --root <checkout> --record <record.json> --source-root <vollstaendige-arbeitsdateien>
python -m tools.puzzle_production.catalog_background_change plan --root <checkout> --record <content/authoring/pz-ID/bg-r01/record.json> --output <neuer-planordner-ausserhalb-checkout>
python -m tools.puzzle_production.catalog_background_change adopt --root <checkout> --plan <planordner>
python -m tools.puzzle_production.target_adapter retire-background-production --checkout <checkout> --integrated-commit <vollstaendige-main-SHA> --authoring-revision <pz-ID> <revision>
```

API: `store(root, record_path, source_root)`, `plan(root, record_path, output,
seconds=300)`, `adopt(root, plan_path, seconds=300, integrated_commit=None)`;
Retirement-API `background_retirement.retire(root, revisions, integrated_commit)`.
store liest den bereits tatsächlich erklärten unveränderlichen Request und seinen
vollständigen Dateisatz, prüft ihn und publiziert die neue Arbeitsrevision ohne
Ersetzen unter `content/authoring/<id>/<revision>`; der vorhandene Authoringindex
v1 erhält nur die exakte neue Zeile. Gemeinsamer Authoringlock, frische Vor-/Nach-
Prüfung, Index zuletzt; vorhandene identische vollständige Revision/Zeile ist
No-op, fremde/teilweise Belegung Konflikt. Keine Freigabe erzeugen oder ändern.
Der Speicher-No-op gilt auch nach Adoption; er prüft identische Arbeitsbytes und
den gültigen aktuellen Katalog, erteilt aber keine neue Übernahmebefugnis für ein
inzwischen veraltetes Ziel. plan/adopt prüfen dessen vollständige Zielbindung.
Der Request selbst ist der Record, kein Rasterpaket und kein registrierter Status.
Die neue Familie wird im Index ausdrücklich dispatcht. MJ-B führt ihre eigene
Sheetbedienung nach Hintergrundvertrag §7.6; keine Umdeutung zum Rasterrecord.

plan ist gegenüber Checkout/Arbeit lesend und veröffentlicht das vollständig
geprüfte Bundle am neuen externen Pfad ohne Ersetzen. input/ ist dessen explizite
simulierte Checkoutwurzel; alle inneren Ref-/StoredRefwerte bleiben unverändert.
adopt liest/reproduziert HP-W2 frisch, leitet Alt-/Neuansicht unabhängig her und
prüft Arbeit/Index bei Eingang und unter Kataloglock vor erster aktiver Mutation.
Nur der vollständig eigene Zielstand ist Byte-/mtime-No-op. Nach revisionsgenauem
Mainabschluss erfordert dieser reine No-op `--integrated-commit <40-stellige-SHA>`;
fehlende/teilweise Arbeit darf niemals eine neue Mutation erlauben. Ein alter Plan
bleibt nach ursprünglichem Paket-/Receiptwechsel stale, auch als No-op.

Die CLI liefert genau ein JSON-Objekt `picross-background-adoption-result-v1`
mit `format,status,puzzle_id,revision,plan_hash,error,recovery_required,remaining`.
Status ist `stored,planned,adopted,no-op,invalid_input,aborted`; unbekannte
Identitäts-/Planwerte und nicht vorhandene Fehler/Restpfade sind null.
`error` enthält andernfalls `code,message`, `recovery_required` ist Boolean.
Exitcodes: 0 bei Erfolg, 2 bei ungültiger Eingabe/Konflikt/I/O-Fehler,
4 bei Abbruch. Ein nach Veröffentlichung fehlgeschlagener Sync oder Readback
meldet den tatsächlich verbleibenden eigenen Plan-/Arbeitsordner; eine nur
teilweise gespeicherte Revision wird nicht stillschweigend vervollständigt.

retire-background-production benötigt aktualisiertes origin/main und dessen
vollständigen bestätigten Commit, ausdrücklich wiederholbare `--authoring-revision
ID REVISION`-Paare. Alle ausgewählten tatsächlichen Mainadoptionen vor erster
Entfernung prüfen; supersedierte Arbeit darf mit ihrem eigenen Mainbeleg enden,
ohne aktuelle Source/PNG/none/Notice/Receipt oder jüngere Arbeit anzufassen.
Wiederholung vollständig entfernter Arbeit ist nach frischer Prüfung No-op;
Teilentfernung/Fremdbytes/Stagingfehler melden tatsächliche Reste. Kein Git-Commit,
Fetch, Push oder Merge im Writer. Die alten Reveal-/Rasterbefehle behalten ihren
Scope. Keine Rekonstruktion alter ZIPs oder dauerhafte Plankopie erforderlich.

Die technischen Nachweise sind kleine synthetische Fälle in tools, production.images,
production.adapter und production.catalog. Der Kern liefert bei Werkzeugentwicklung
Windows; das belegt keinen Windowsstart oder Hintergrundrenderer. Fachoriginale
werden im Lauf geprüft und danach entfernt, evidence.mode=none; vor Merge bleibt
ein unabhängiges technisches Review des konkreten Heads erforderlich.

## HP-I1c: Rasterupdate und Revealadoption gültiger Hintergrundziele

[Paketentscheidung](https://github.com/venomenon328/picross/issues/561#issuecomment-6766500497),
[exakte Formen, Grenzen und Versionsmatrix](../../docs/PUZZLE_BACKGROUNDS.md#12-hp-i1c--aktuelle-raster-revealbindung).
Die bestehenden `target_adapter plan-update/update`- und
`catalog_reveal plan/adopt`-Aufrufe bleiben unverändert. Ein Hintergrundziel
erhält Source v3 mit vollständigem unverändertem v1/v2-Ausgangsstand und begrenzten
chronologischen Events. Ein Rasterupdate erhält selected/none, technische
Bildrevision, Rechte und PNG/Notice; v5 bedeutet keine Bildentscheidung.
V6 muss exakt dieselben aktuellen Bild-/Entscheidungsdaten enthalten. Unpassende
Exporte und Legacy-Nachrüstung scheitern vor Mutation. Revealadoption benötigt
weiterhin die tatsächliche AT-Freigabe mit aktuellem Vorgängerhash.

Die Writer wählen nur bei Hintergrundzielen Updatejournal v7 beziehungsweise
Revealplan v4/Revealjournal v4 und AT-Source v2. Ein folgender separater
Hintergrundwechsel verwendet Hintergrundplan/-journal v2 und erhält die aktuelle
Raster-/Revealbindung. Alle übrigen zulässigen Formen bleiben erhalten.
Die gemeinsam gebundenen Quellen und aktuelle Planbytes werden vor und unter
Lock frisch geprüft. Alte Pläne nach Raster-, Reveal-, Hintergrund- oder
Receiptwechsel sind stale; nur exakte eigene Wiederholung ist Byte-/mtime-No-op.
Bei Unterbrechung bleibt `target_adapter recover-registration` der einzige
Recoveryeinstieg, mit unverändertem 300-s-Rahmen für diese Operationen.

Die beiden Produktionsabschlüsse prüfen Main und aktuelle Autorität ohne alte
ZIPs wiederherzustellen. Originale v6-register-Wiederholung darf nach vollständiger
Prüfung ein No-op sein und stellt keine frühere Definition/Bildwahl wieder her.
Für Rückbau eines begonnenen Writers das Journal verwenden; eine abgeschlossene
Source v3 darf nicht durch Entfernen von Events oder Umbenennen auf v1/v2
zurückgebaut werden. Ein Software-Rollback braucht einen dazu kompatiblen
Quellenstand. HP-I1c ändert keine aktive Authoring-/Sheetversion und aktiviert
allein keine reale Capability; der Runtimeanschluss steht im folgenden Abschnitt.

Die kleinen synthetischen Regressionsfälle stehen in
`tests/puzzle_production/test_background_rebind.py`; bestehende Legacy-,
Bild-, Quellen- und Transaktionssuiten bleiben den ausgewählten Fachmodulen
zugeordnet. Originale werden im Lauf geprüft und temporär entfernt.

## HP-I2: Runtimeanschluss und isolierter Hintergrundimport

[Paketentscheidung](https://github.com/venomenon328/picross/issues/561#issuecomment-6770077470)
und [normativer Runtimevertrag §13](../../docs/PUZZLE_BACKGROUNDS.md#13-hp-i2--runtime-darstellung-und-besuch)
führen Reader v6, papiergebundene Darstellung A und begrenztes Bedarfsladen im
regulären Buch. Die bestehende `game/data/background-capability.json` darf erst
mit diesem funktionierenden und technisch abgenommenen Weg true sein. Die
einmalige unabhängige Renderer-/Gestaltungsabnahme steht am konkreten Produkt-
Head; sie ist keine zusätzliche persönliche Buchabnahme pro produzierter Datei.
Authoring-/Sheetdefault bleibt 0.6.0, der gesonderte 0.7.0-Weg opt-in. Kein
Capabilityflag ersetzt den vollständigen Einzelwegabgleich in #560.

### Regulärer Import- und Exportweg

Die vorhandenen Builder verwenden den gemeinsamen Importvorbereiter automatisch
in ihren eigenen temporären Godotkopien:

```sh
python tools/build_main_player.py --cache-dir <engine-cache> --output-dir <windows-ausgabe>
python tools/build_web_player.py --cache-dir <engine-cache> --output-dir <web-ausgabe>
```

Die normalen nativen Prüf-/Exportwege verwenden denselben Helfer in ihrer
isolierten Spielkopie. Es gibt keine neue öffentliche Import-CLI und keinen
Editorimport im schreibenden Inhaltscheckout. Insbesondere erlaubt HP-I2 keine
`.png.import`-Dateien im aktiven `game/art/backgrounds/`-Quellnamensraum und
öffnet dessen Quellen-/Writer-/Journalguards nicht für technische Nebenprodukte.
Aktive Dateien bleiben die gebundenen PNGs und Notices; bei none gibt es keine
Nulltextur. Ausgewählte Quelldateien bleiben bytegleich und am kompakten
Source-/Runtime-Ref gebunden.

Der interne Helfer `tools/background_import.py` trennt vier Aufgaben:

| Aufruf | Wirkung und Grenze |
| --- | --- |
| `source_inventory(root)` | Prüft die tatsächliche kompakte Inhaltsautorität, Runtimeprojektion, gewählte PNG2304-/Noticebytes und den geschlossenen aktiven Namensraum. Kein Solver- oder Produktionsreplay. |
| `prepare_import(project, inventory=None)` | Prüft die isolierte Kopie und ihre exakte Bindung, schreibt nur deren eigene Importsidecars vor Godot. Ohne Inventar sind ausschließlich technische Kopien ohne selected zulässig. |
| `verify_import(project, inventory)` | Prüft nach Godot tatsächliche Sidecars, Profilwerte, Importremap und `.ctex`-Header sowie getrennte Importbytes/-hashes. Dekodierte Pixel und vollständige Mipmaps benötigen die gesonderte tatsächliche PCK-Probe. |
| `restore_sources(root, project, inventory=None)` | Stellt vor regulärem Export die wirklichen aktiven Hintergrundressourcen passend zum tatsächlichen Katalog wieder her und entfernt synthetische Dateien samt eigenen Importresten aus der isolierten Kopie. |

Das feste Profil erhält 2304×576 RGBA und verwendet verlustfreie Kompression
(`compress/mode=0`), generierte Mipmaps (`mipmaps/generate=true`), keine Alpha-
Randkorrektur/Premultiplikation, keine Größenbegrenzung und keine 3D-Erkennung.
Der Renderer verwendet passende Mipmapfilterung. Native und Web verwenden
dieselbe Quelle und dasselbe Profil; die nichtthreaded Webkonfiguration bleibt.
Der Webexport enthält `web/background_loader.js` für den gebundenen Workerweg
nach §13.3, ohne eine neue Hosting-/COOP-/COEP-Pflicht.

### Was die Nachweise aussagen

Quell-PNG-Hash und Engineimporthash sind verschiedene Bindungen. Das PCK muss
die tatsächlich importierte ausgewählte Textur samt Mipmaps und benötigter
Notice enthalten; eine zusätzliche rohe PNG-Kopie wird nicht vorausgesetzt.
Kein Kandidatensatz, Originalproduktions-ZIP, Freigabedokument oder Prüfprogramm
gehört in den Spielerexport. Kleine feste synthetische Regressionen erweitern
keinen echten Produktionskorpus. Ein tatsächlicher Windows-/Webexport und
PCK-Audit belegen Lieferung, keinen ausgeführten Windowsstart oder Browserlauf.

HP-I2-T01/T02 binden die einmalige echte native Interaktion, sechs unveränderte
Originalbilder und getrennte Quellen-/Import-/PCK-/Dekodiermessungen an den
konkreten Head. Das Paket führt keinen neuen Gameplaydauerlauf und kein hartes
Laufzeit- oder Größenbudget ein. Revieworiginale werden nach dem befristeten
Paketplan zugänglich gehalten; eigene technische Kopien enden nach ihrer Prüfung.
Die unabhängige HP-I2-A01-Abnahme bleibt bis zur tatsächlichen Erklärung offen.

Vor Capabilityänderung Zielstand und offene Journale prüfen. Geänderte
Capabilitybytes machen vorhandene daran gebundene Pläne stale; sie erlauben
keine alte Recovery auf inzwischen inkompatiblen Daten. Kein Flagwechsel als
Umgehung und keine Änderung historischer Exportfalse-Felder. Echte Bestands-
rätsel werden durch HP-I2 nicht migriert; Legacy-only bleibt Runtime v5.

## MJ-B: eigener Hintergrundwechsel im Offline-Sheet

[Vertrag §7.6](../../docs/PUZZLE_BACKGROUNDS.md#76-mj-b-eigenständige-hintergrundrevision-im-sheet)
führt die geschlossenen äußeren Formen. „Neuer Hintergrundwechsel“ legt einen
separaten 0.7-Job an; neue reguläre Jobs bleiben 0.6. Originalrequestdatei mit
kanonischen Bytes einschließlich End-LF nach Vorschau übernehmen, unverändert
als Sitzung sichern oder in Sammlung v2 gemeinsam mit regulären Jobs exportieren.
Alte v1-Sammlungen bleiben ausschließlich für reguläre Jobs lesbar. Familienwechsel
ist ausdrücklich vollständiger Ersatz mit erhaltener lokaler Job-ID.

`prepare/rework` sind Bild-/Auswahlaufträge; `resume/adopt/complete` verwenden
Codex mit eingestellter Arbeitswurzel. Ein neuer materieller Wunsch sperrt die
Adoption des alten Requests. `adopt` braucht vollständigen Originalrequest,
benannten Quellstand und den konkreten Fundort der vollständigen Arbeitsrevision.
ZIP enthält nur Bedienauftrag/Metadaten, Originalrequest und bei gewähltem Anhang
den 0.7-Snapshot, niemals die automatisch eingesammelten `request.files`.
Originale separat bereitstellen; `store/plan` prüft sie und das frische Ziel.

„Abschluss melden“ benötigt tatsächlich gemeldeten vollständigen Maincommit und
konkreten HTTPS-Bericht. Danach bleiben kompakte historische Refs und `test_only`;
Arbeitsinventar/Originaltext werden aus der Sitzung entfernt. Das ersetzt keine
Retirementprüfung oder Mainverifikation. Keine neuen Writer oder CLI-Ergebnisimporte.

## PW-A: lesende Git-/Bildansicht

[Launcher, Projektor und geschlossene Datenformen](../production_workspace/README.md)
stehen separat bereit. PW-A liest neu veröffentlichte Handoff-v3-/Record-v2-
Arbeitsstände über Index und `workspace.json`; keine Alt-WIP-Konvertierung.
Der Projektor schreibt ausschließlich die neue Ansichtsdatei, der HTTP-Dienst
ist projektseitig Leser. Der fünfstufige Default und die verbindliche
Phasenveröffentlichung folgen erst PW-B; bestehende Produktionsbefehle bleiben.
