# Rätselproduktion: Werkzeuge und Befehle

Diese Anleitung beschreibt die Bedienung der vorhandenen Werkzeuge. Geschlossene
Datenformen, Grenzen und Befugnisse stehen in den verlinkten Fachverträgen.
Alle Aufrufe starten im Repositoryroot; Bildbefehle benötigen die unten erläuterte
[isolierte Image-Umgebung](#rp-3-isolierte-image-umgebung-und-reale-befehle).

| Aufgabe | Einstieg und maßgeblicher Vertrag |
| --- | --- |
| Neue Rätsel und Wiederaufnahme | [Authoring](../../docs/production/authoring/PUZZLE_AUTHORING.md), [PW-B](../../docs/tools/PW_B_CONTRACT.md) |
| Finalen aktuellen Eingang integrieren | RI-ONE-Aufrufe im nächsten Abschnitt; [ZA-1](../../docs/production/ZA1_ADAPTER.md) und [RI](../../docs/production/PUZZLE_INTEGRATION.md) |
| Registrierte Rätsel bearbeiten | Aktueller Editorweg unten; [PE §13](../../docs/tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung) |
| Bildtyp und Darstellung beurteilen | [Bildnormen](../../docs/production/images/README.md) und [Qualität](../../docs/production/PUZZLE_QUALITY.md) |
| Logik, Rasterableitung und Analyse | Die jeweiligen Werkzeugabschnitte dieser Anleitung; [Produktionsvertrag](../../docs/production/PUZZLE_PRODUCTION.md) |

## RI-ONE: aktuelle Integration

Der aktuelle Eingang ist ein Verzeichnis mit `manifest.json` im Format
`picross-integration-input-v1` und seinen finalen referenzierten Dateien.
[ZA-1](../../docs/production/ZA1_ADAPTER.md) definiert allein die Feldformen,
Qualitätsnachweise, Rechte und tatsächlichen Entscheidungen.
[RI-ONE](../../docs/production/PUZZLE_INTEGRATION_SINGLE_PATH.md) legt die
Bestandsautorität fest; [RI](../../docs/production/PUZZLE_INTEGRATION.md) den Writer.

```text
python -m tools.puzzle_production.target_adapter inspect --input FINAL_INPUT
python -m tools.puzzle_production.target_adapter export --input FINAL_INPUT --output-dir NEW_EXPORT
python -m tools.puzzle_production.target_adapter verify-export --input NEW_EXPORT
python -m tools.puzzle_production.target_adapter plan --input FINAL_INPUT --checkout CHECKOUT
python -m tools.puzzle_production.target_adapter register --input FINAL_INPUT --checkout CHECKOUT
python -m tools.puzzle_production.target_adapter recover-registration --checkout CHECKOUT
python -m tools.puzzle_production.target_adapter check-registry --checkout CHECKOUT
python -m tools.puzzle_production.target_adapter sync-runtime --checkout CHECKOUT
```

`inspect`, `verify-export` und `plan` lesen und prüfen. `export` schreibt eine
neue geprüfte Kopie außerhalb des Checkouts. `register` prüft selbst vollständig
und schreibt nur im ausdrücklich autorisierten Integrationsauftrag; die beiden
separaten Diagnoseaufrufe sind davor keine zusätzliche Routinepflicht.
`sync-runtime` schreibt die Projektion aus aktuellen gültigen Quellen.
`prepare-integration` im Authoringbuilder verwendet denselben Exportkern.

Eine identische Wiederholung bleibt ein No-op. Eine belegte ID mit anderen Daten
ist ein Konflikt und gehört in die gezielte Editorpflege. Alte Authoring-ZIPs,
Export-/Receiptgenerationen und frühere Journale sind keine alternativen aktuellen
Integrationseingänge. Getrennte neue Befehlsaufrufe prüfen ihre eigenen Eingänge;
ein früherer Diagnoseerfolg erteilt keine Schreibbefugnis. Budgets, Diagnostik und
Recovery folgen den Fachverträgen, ohne zusätzliches Kompatibilitätsversprechen
für abgelöste Writer.

Serielle Integration verwendet [BA-B Plan v2](../../docs/tools/PRODUCTION_BATCH.md#8-ba-b-autorisierte-serielle-einzelintegration).
Nach bestätigter autorisierter Mainintegration führt der Produktionsakteur den
[v2-Produktionsabschluss](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung)
mit `python -m tools.work_publish retire ID --expected ARBEITSCOMMIT` aus.
Der Publisher liest Branch-, Release- und Tagabwesenheit zurück. Bei Teilfehlern
im selben Checkout mit derselben Arbeits-SHA wiederholen.

## Aktuelle Bestandsbearbeitung

[`editor_cli`](editor_cli.py) ist der gemeinsame CLI-Einstieg für Name, Kategorie,
Bilder und Raster. Seine aktuelle Requestform und die gezielte Prüfgrenze gehören
[PE §13](../../docs/tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Der Editor setzt aktuelle RI-ONE-Quellen voraus und führt keine Bestandsmigration aus.

```text
python -m tools.puzzle_production.editor_cli list --target-root CHECKOUT
python -m tools.puzzle_production.editor_cli detail --target-root CHECKOUT --id PUZZLE_ID
python -m tools.puzzle_production.editor_cli plan --target-root CHECKOUT --request INPUT/request.json --output PLAN.json
python -m tools.puzzle_production.editor_cli apply --target-root CHECKOUT --plan PLAN.json
python -m tools.puzzle_production.editor_cli recover --target-root CHECKOUT
```

`INPUT` und die neue Plandatei liegen außerhalb des Inhaltscheckouts. Beispiel
für eine reine Namensänderung an einer zuvor aus `list` gelesenen ID:

```json
{
  "format": "picross-editor-request-v2",
  "id": "pz-beispiel",
  "metadata": {"name": "Neuer Motivname"},
  "text": null,
  "profile": null,
  "reveal": null,
  "background": null,
  "imports": {}
}
```

Für Bildimporte ordnet `imports` die verwendeten Uploadschlüssel relativen neuen
PNG-/SVG-Dateien unter `INPUT` zu. Reveal verwendet `{ "upload": "reveal" }`;
ein eigenes Hintergrundbild `{ "status": "selected", "upload": "background" }`.
Die vollständigen Zustände und Importgrenzen stehen in PE; es gibt keine
Akteur-, Herkunfts- oder Bestätigungsfelder im aktuellen Editorrequest.
Rastertext und Prüfprofil werden im selben Request übergeben. Nur tatsächliche
Logikänderung erzeugt einen neuen Proof, eine neue Bewertung und Rasterrevision.

Planen bereitet die gebundenen Schreibbytes vor und verändert keinen Inhalt.
Vor `apply` Vorschau und Dateiliste prüfen. Apply kontrolliert Planhash und
aktuelle Altbytes, verwendet die vorbereiteten Bild-/Rasterbytes und schreibt
unter gemeinsamem Lock mit Runtime zuletzt. Stale Eingänge verlangen einen
frischen Plan; fremde Bytes bleiben bei Konflikt und Recovery erhalten.
Spielstände behandelt ausschließlich der Spieler nach
[PE §9.3](../../docs/tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart), nicht der Editor.

`images_cli` und `raster_cli` bleiben schmale Bedienadapter dieses aktuellen
Editorwegs; ihre eigenen Argumentnamen zeigt jeweils `--help`. Sie nehmen
keine alten A2-/A3-Requests, Migrationen oder Altjournale wieder in Betrieb.
Die früheren A1/A2/A3-Anleitungen sind im
[historischen README](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
erhalten.

### Namen und Kategorien über die Metadaten-CLI

[`metadata_cli`](metadata_cli.py) bietet einen direkten Einstieg für die
Operationsliste aus [PE §13.2](../../docs/tools/PUZZLE_EDITOR.md#132-geschlossener-änderungsplan-und-kleines-journal):

```text
python -m tools.puzzle_production.metadata_cli view --target-root CHECKOUT
python -m tools.puzzle_production.metadata_cli plan --target-root CHECKOUT --operations OPERATIONS.json --output PLAN.json
python -m tools.puzzle_production.metadata_cli apply --target-root CHECKOUT --plan PLAN.json
python -m tools.puzzle_production.metadata_cli recover --target-root CHECKOUT
```

Beispiel für `OPERATIONS.json` mit einer vorhandenen ID und Kategorie:

```json
[
  {"op": "set_metadata", "id": "pz-beispiel", "name": "Neuer Motivname", "category_id": "voegel"}
]
```

`plan` erzeugt den aktuellen gezielten Editorplan. Die separate Fach-API
`catalog_metadata.view/plan/apply` bleibt nach
[PE §7.1](../../docs/tools/PUZZLE_EDITOR.md#71-getrennte-aktuelle-metadaten-fach-api)
verfügbar; `metadata_cli apply` akzeptiert auch deren Metadatenplan v2 mit dem
aktuellen gemeinsamen Katalogjournal. Das ist keine Unterstützung der früheren
v4/v7-Migration oder ihrer Journalformen. Namens-/Kategoriepflege verändert keine
Definitionen, Bilder, Rasterrevisionen, Bewertungen oder Hinzugefügt-Daten.

## #596/C · Feste Rasterableitung

Der vor Code festgelegte [Vertrag](../../docs/production/FIXED_RASTER.md) definiert die
geschlossenen Parameter-/Plan-/Record-/Manifestformen und deren Grenzen.
`python -m tools.puzzle_production.fixed_raster derive --root ROOT --plan PLAN --output OUT`
erzeugt das reguläre Bundle; `inspect --root ROOT --bundle BUNDLE` prüft es frisch.
`source_type=fixed`, kein manueller Override; die aktuelle Authoringgeneration
steht in [PW-B](../../docs/tools/PW_B_CONTRACT.md).
Aktive Schwierigkeit zusätzlich über catalog_analysis mit expliziter Methode 0.4.


<a id="pw-b-neue-produktion-080"></a>

## PW-B: aktuelle Produktion ohne Entstehungsarchive

Für neue Jobs die geschlossene [v3-Form](../../docs/tools/PW_B_CONTRACT.md#pw-find--freigegebene-erweiterung-der-entscheidungsdaten) verwenden.
Im bestehenden Builderrequest den aktuellen Record mit `findings=[]` und `instructions={}` beginnen.
Der Akteur bindet jede neue Beobachtung mit `finding_decisions.identity(job, target)` an ihren Inhalt.
`declare(row, expected=…, action=…, treatment=…, actor=…, timestamp_utc=…, statement=…)` wendet die
tatsächlich gesendete Erklärung an. Die im Auftrag sichtbare Standardbehandlung wird wörtlich gespeichert.
Bei widersprüchlicher Behandlung vor der Fortsetzung die konkrete Erklärung klären.

Für eine Korrektur zuerst am tatsächlichen unmittelbaren Ausgangsrecord neu beurteilen, dann
`carry(previous, job, source_id, successor_id, continuing=…)` verwenden. In `continuing`
die weiterhin relevanten früheren Texte für den Nachfolger angeben, auch wenn ein Befund verschwunden ist.
Bei weiteren Blockern den tatsächlichen Reviewstand mit den bereits wirksamen Erklärungen sichern.
Zum gezielten Wechsel eines aktuellen Altstands dient `current_authoring.upgrade(job, observations=…, backgrounds=…, job_blockers=…)`.
Negative Sammelurteile benötigen konkrete neu gebundene Einzelbefunde, Hintergrundoriginale ihr tatsächliches Profil.
Frühere Annahmen nur mit belegter Einzelzuordnung erklären. Auftragsweite Altblocker ausdrücklich prüfen.
Nach Resume, Builder und Finalizer mit dem regulären Publisher und erwarteten Arbeitscommit sichern.

Neue Jobs verwenden den [fünfstufigen Authoringweg](../../docs/production/authoring/PUZZLE_AUTHORING.md)
und den geschlossenen aktuellen [PW-B-Vertrag](../../docs/tools/PW_B_CONTRACT.md).
Ein Record plus benötigte Nutzdateien, ein gemeinsamer Verweisindex. Kein
Handoff, Inventar, ZIP, Regelwerksnapshot, Generator-/Prompt-/Reparaturarchiv,
workspace-Snapshot oder Pointer pro neuem Job. Die UI und Folgeaufträge werden
direkt aus dem Record und seinen konkreten Datei-/Inhaltsbindungen abgeleitet.

`authoring_builder build --request REQUEST --source-root QUELLEN --output-root
ARBEIT --publish-to CHECKOUT` verarbeitet `picross-authoring-current-request-v1`.
Der Akteur erstellt den Auftrag aus tatsächlichen Ergebnissen und Erklärungen;
keine manuelle JSON-Pflege im Benutzerablauf. Finalize-background verarbeitet
denselben aktuellen Fortschreibungsauftrag. Identische Wiederaufnahme vollendet
nur die eigene offene Operation; nach Abschluss verschwindet ihr Journal.
Vor Originalabruf, Finalizer oder großem Checkout prüft der Akteur den geplanten
Publisherzugang mit diesem Befehl aus dem vertrauenswürdigen Werkzeugstand.

```text
python -m tools.work_publish preflight ID --for publish --repository venomenon328/picross --expected new --auth env
```

Für einen laufenden Job ersetzt die erwartete Arbeits-SHA `new`. Mit
`--for resume` oder `--for retire` und derselben SHA lässt sich der jeweilige
Zugang vorprüfen. Der JSON-Bericht weist Gitrefs und Release-/Assetmetadaten
aus. Erst die echte Publikation oder der Abschluss mit Remote-Readback belegt
den jeweiligen Schreibzugriff. Eine frische eigene veränderbare Releasegeneration
kann auch ohne Zugriff auf die Repository-Settings weitergeführt werden. Neue
Releases erfordern eindeutig deaktivierte Unveränderlichkeit.

Der Akteur sichert das lokale Ergebnis mit
`python -m tools.work_publish publish ID --expected new --auth env`
bzw. der erwarteten Arbeits-SHA. Für beide Befehle dieselbe explizite Authquelle
verwenden. `env` verwendet `GH_TOKEN` oder `GITHUB_TOKEN`. Bei einem Konflikt
die passende Variable mit `--auth GH_TOKEN` oder `--auth GITHUB_TOKEN` wählen.
`--auth gh` wählt die aktive github.com-Anmeldung. Wiederaufnahme, Originalabruf
und Abschluss folgen [PW-B](../../docs/tools/PW_B_CONTRACT.md#bau-auswahl-und-sichere-fortschreibung).

`prepare-integration --repository ARBEITSCHECKOUT --record RECORD --output-dir NEU`
leitet den aktuellen RI-ONE-Eingang ab. Eine reine Hintergrundpflege erzeugt
statt Erstregistrierung den aktuellen gemeinsamen Editorrequest. Die Integration
bekommt einen sauberen Branch vom aktuellen Main und ausschließlich ausgewählte
finale Produktdaten. Completion und Retirement benötigen keine Arbeitsarchive im
Produktcommit. Aktuelle angebotene Alternativen bleiben bis zur tatsächlichen
Wahl erreichbar; danach entbehrliche Varianten ohne Archivierung entfernen.

### Aktuelle Bild- und Rasterhelfer

Die folgenden Befehle benutzen die vorhandenen Algorithmen in der isolierten
Pillow-Umgebung; sie erzeugen keine neue Spielmechanik oder Solverregel:

`python -m tools.puzzle_production.current_tools image --input BILD --design DESIGN
--puzzle-id ID --name NAME --output-dir NEU` schreibt je tatsächlichem Kandidaten
nur Definition, aktuellen Proof, Preview und bei vollständigem Ergebnis aktuelle
Difficulty. Original/Normalisierung/Generator-/Toolhash-/Vergleichsarchive entfallen.

`python -m tools.puzzle_production.current_tools raster --input DEFINITION --mode
mono|color --output-dir NEU` prüft einen aktuellen Rasterstand unabhängig von
seiner Herstellung. Vollständiger geschriebener Proof wird in einem frischen
Verifierprozess geprüft und mit der Endmatrix verglichen. Bei stalled bleibt
Difficulty null; kein qualifiziertes Angebot oder falscher Erfolg. Paarprofil nur
mit ausdrücklichem `--profile paired`. Methode standardmäßig aktuelle 0.4;
keine neuen Algorithmen, automatische Profil-/Budgeterhöhung oder Kataloganalyse.

`python -m tools.puzzle_production.current_tools background --input ORIGINAL.png
--output AKTUELL.png` bereitet allein aktuelle Bildbytes nach dem ausdrücklich
gewählten HG31-Profil vor. Keine Ableitungs-/Tool-/Codecdatei. none/standard
benötigen keinen Bildlauf und keinen Nullbefund. Angebote selbst prüfen/vorlegen.

Temporäre Analyse-, Such-, Masken- oder Reparaturdaten dürfen während einer
konkreten Operation existieren und enden nach dem aktuellen Ergebnis. Nur
aktuellen Budgetverbrauch im Record fortführen. Aktueller Proof, echte Rechte,
Motiv-/Parameterkonformität, Bildsichtung und tatsächliche Entscheidungen bleiben.
Vorhandene aktive Produktbilder werden referenziert und nicht pro Job kopiert.

Die folgenden alten BA-A-/PB-A-/PB-H-/HP-W2-Bundleformen sind ausdrücklich
historische beziehungsweise temporäre Operationswege, keine Aufbewahrungs- oder
Zulassungsbedingung neuer aktueller Jobs. Kein automatisches Wiederherstellen
entfernter Herstellungsunterlagen und keine allgemeine WIP-Migration.

## BA-A: lokale Batchverarbeitung und Wiederaufnahme

[`batch_cli`](batch_cli.py) verarbeitet ausdrücklich vorbereitete Jobs seriell.
[PRODUCTION_BATCH](../../docs/tools/PRODUCTION_BATCH.md) beschreibt die vollständigen
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

Der aktuelle Batchplan v2, seine Run-/Resume-/Statusbefehle und die geschlossenen
Ledgerformen stehen in [BA-B](../../docs/tools/PRODUCTION_BATCH.md#8-ba-b-autorisierte-serielle-einzelintegration).
Jeder Job verwendet denselben [RI-ONE-Kern](#ri-one-aktuelle-integration) mit
vollständigem aktuellen Input. Die frühere BA-B-Export-/Receiptgeneration ist
abgelöst; die eigenständigen BA-A-Leser für 0.6/0.7 bleiben davon getrennt.

## HP-W2: eigenständige Hintergrundableitung

[`background_assets`](background_assets.py) stellt die lokale API/CLI für die
Arbeits-, Entscheidungs-, Auftrags- und Befundformen aus
[PUZZLE_BACKGROUNDS §§3–4](../../docs/production/PUZZLE_BACKGROUNDS.md) bereit. Maßgeblich
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
samt Hash sowie getrennte tatsächliche Git-Herkunft `producer={commit,dirty}`.
V2-`dirty` beschreibt den Arbeitsbaum einschließlich unversionierter Dateien
zu Aufrufbeginn vor eigenen Schreibvorgängen. Spätere eigene Lock-/Stagingdateien
ändern keine Bildautorität; Quellen, Renderstand und Ziele werden frisch geprüft.
Die genaue Provenienzsemantik steht in [Hintergrund §4.7](../../docs/production/PUZZLE_BACKGROUNDS.md#47-pw-perf-c-neue-hp-w2-beleggeneration-v2).
`describe --generation 1` beschreibt ausdrücklich die alte Neun-Modul-Identität. Für einen neuen Auftrag diese Werte verwenden; ein abweichender
`expected_tool_sha256` wird vor dem Schreiben zurückgewiesen.

Der neue geschlossene `picross-background-derive-request-v2` bindet das
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
Referenzen frisch. Nur das gewählte Original wird dekodiert. Das ausdrücklich
gewählte Profil aus [HG31](../../docs/production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile)
bestimmt Ausgabegröße und Fit: neue 3:1-Arbeit verwendet
`picross-background-png2304x768-v1` mit exakter vollständiger Skalierung;
das alte Profil behält seinen proportionalen Contain-Fit. Gemeinsamer unterer
mittiger Anker, vormultipliziertes Lanczos und unveränderte Originale bleiben.
Keine individuellen Crop-/Masken-/Positionsparameter.
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
Beide Generationen prüfen vollständige Originalbefunde; bei v2 bleibt `producer`
außerhalb der Bildidentität. Für v1 gilt weiterhin: Lesendes `verify` prüft
originale Request-/Befund-/Toolhashes strikt, verlangt
aber nur für `id`, vollständige `versions` und die exakte Modulpfad-/Bytehashmenge
Gleichheit mit dem aktuellen Werkzeug. Originales `commit/dirty` bleibt
Erzeugerherkunft; ein späterer reiner Contentcommit macht gleiche ausführbare
Bytes nicht ungültig. Ausgabe und vollständigen Befund mit dem ursprünglichen
Toolobjekt reproduzieren; geladene/gespeicherte Module und Eingänge müssen dabei
unverändert bleiben. HP-W2-COMPAT-1 aus
[#645](https://github.com/venomenon328/picross/issues/645#issuecomment-6882921168)
ergänzt ausschließlich für `selected` die geschlossene Menge qualifizierter
historischer Erzeugeridentitäten in `background_assets._SELECTED_PRODUCERS`.
Ihr Hash bindet das vollständige Original-Toolobjekt einschließlich Commit,
dirty, sämtlicher Modulhashes und Versionen. Erster Eintrag ist
`23971ee3834218f28977a346e09f716de6eb18fd6fc3acb8cab25a5ad8cab691`
aus `94f0fb35ab4f6623a1ddde6d0ca3b03590be0e57` (dirty=false), nach Abgleich
der neun Originalmodule mit Git und tatsächlicher bytegenauer Reproduktion.
Weitere Identitäten benötigen eigene Qualifizierung. Keine Modulnamenausnahme
und keine Ausführung historischer Quellen. Aktuelle sichere Leser reproduzieren
PNG und vollständigen Originalbefund einschließlich Diagnostik; die vollständige
aktuelle Modul-/Codecbindung wird währenddessen vor/nach geprüft. ID und gesamte
Versionsmap müssen auch bei dieser Route exakt stimmen. `none`, unbekannte alte
Tools, geänderte Codecs/Profile oder abweichende Reproduktion bleiben Fehler.
Finalizer (zuerst alter Record), Export und Offline-`verify-export` erreichen
dieselbe zentrale Prüfung. Es entsteht kein zusätzlicher persistenter Beleg.
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

Die Standalone-Ableitung ist ein kreatives Werkzeug und registriert keinen
Hintergrund im Spiel. Neue Produktion folgt [PW-B](#pw-b-neue-produktion-080),
Integration [RI-ONE](#ri-one-aktuelle-integration), Bestandsänderung dem
[Editor](#aktuelle-bestandsbearbeitung). Die folgenden PB-H-Formen erhalten ihre
ausdrückliche 0.7-Lese-/Baukompatibilität; sie setzen keinen neuen Produktionsdefault.

## PB-H: Hintergrundpakete und lesende Inhaltsprüfung

Dieser Abschnitt beschreibt die weiterhin unterstützte 0.7-Werkzeuggeneration
nach [#489/PB-H](https://github.com/venomenon328/picross/issues/489#issuecomment-6751071312).
Ihre geschlossenen Hintergrundformen stehen im
[Hintergrundvertrag](../../docs/production/PUZZLE_BACKGROUNDS.md).
Der isolierte [0.7-Referenztext](../../docs/legacy/authoring/PUZZLE_AUTHORING_0_7_0_PREVIEW.md)
bleibt mit seinem tatsächlichen Dateihash verwendbar. Gespeicherte ältere
Snapshots behalten dagegen exakt ihre ursprünglichen Bytes und Quellencommits;
die Verschiebung und korrigierte Links behaupten keine alte Dateichecksumme.
Für neue reguläre Produktion gilt [PW-B](#pw-b-neue-produktion-080).

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
`authoring_inspection.inspect_authoring(package, ..., allow_background=True)`. Optionaler
`approval_path` bezeichnet eine schon vorhandene `picross-editorial-approval-v2`;
`external_root` ist nur bei tatsächlich äußeren Hintergrundbelegen ausdrücklich
anzugeben. Das Ergebnis `picross-authoring-content-inspection-v1` unterscheidet
`original_state` und frisch ermittelten `effective_state`, führt offene Gates
und setzt stets `integration_ready=false`. Keine frühere Phase oder gespeicherte
Erfolgsflagge ersetzt eine neue Inhaltsprüfung. PB-H ergänzt keinen eigenen CLI;
der Builder verwendet diese Arbeitsprüfung. Die aktuelle Integration nimmt
anschließend den vollständigen [RI-ONE-Eingang](#ri-one-aktuelle-integration),
keinen alten Paketexport.

Endfreigabe v2 muss das unveränderte Original-ZIP, Handoff, Inventar, Rasterwahl,
Manifest, tatsächliche Entscheidung, Original, Ableitung, Profil, Ausgabe und
`test_only` exakt binden. Sie wird weder erzeugt, neu datiert noch an neue Bytes
angepasst. Späte äußere Fortschreibung und frühere Export-v6-Strecke (aktuell durch RI-ONE ersetzt) folgen dem HP-I1a-Vertrag
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

Das frühere Offline-Sheet ist entfernt. Seine Bedienung ist ausschließlich im
[historischen README](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md#mj-a-reguläre-jobs-im-offline-sheet)
erhalten. Neue Produktion verwendet [PW-B](#pw-b-neue-produktion-080), die Pflege
registrierter Bilder den [aktuellen Editor](#aktuelle-bestandsbearbeitung).

## HP-I1a: äußere Endabnahme und frühere Export-v6-Strecke (aktuell durch RI-ONE ersetzt)

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## HP-I1b1: erste Hintergrundregistrierung und Produktionsabschluss

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

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

Die kreative Rasterprüfung berechnet die aktuelle Palette frisch: RP-3 vor dem
Solver, RP-5 vor einer Bewertung und feste manuelle Wege vor dem Endproof.
Negative Entwürfe bleiben als Diagnose sichtbar und werden dadurch nicht
freigabefähig. Ein Entwurf ohne Matrix hat nur eine vorläufige Palette.

Der [P-B1-Aufruf](#p-b1-lesende-palettendiagnose) liefert die eigenständige
technische Diagnose. Der [Authoringbuilder](#pb-a-deterministischer-authoring-paketbau)
führt die benötigte Arbeitsprüfung über `authoring_inspection` aus. Die exakten
Palettengate-, Review-, Ausnahme- und Bindungsformen sowie ihre generationsabhängigen
Unterschiede stehen ausschließlich in [PW-B · Palettenausnahme](../../docs/tools/PW_B_CONTRACT.md#palettenausnahme).
[Qualität](../../docs/production/PUZZLE_QUALITY.md) besitzt die Kriterien und ihre
redaktionelle Bedeutung. Ein positiver technischer Abstand ersetzt keine
Bildsichtung; eine dokumentierte Ausnahme ersetzt keinen unabhängigen Endproof.

Die frühere P-B2-Export-v5-/CLI-Zulassung ist im
[historischen README](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md#p-b2-automatische-frühdiagnose-und-finale-palettengates)
erhalten. Die aktuelle Integration verwendet [RI-ONE](#ri-one-aktuelle-integration)
und die dort referenzierten finalen Qualitätsdaten; alte `target_adapter inspect`
Optionen für Authoring-ZIPs werden nicht als aktuelle Bedienung angeboten.

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

**Geltung:** Die einzelne P-B1-CLI ist eine freiwillige Diagnose, kein Zertifikat.
Die kreative Arbeitsprüfung verwendet die generationsgebundenen Palettengates
nach [PW-B](../../docs/tools/PW_B_CONTRACT.md#palettenausnahme); die aktuelle
Integration prüft die finale Palette nach [ZA-1](../../docs/production/ZA1_ADAPTER.md).
F05 bleibt metrisch negativ bei historisch dokumentierter visueller
Referenzannahme, ohne Produktionsausnahme. Keine rückwirkende Bestandsprüfung
oder zusätzliche Standard-Erfolgsausgabe.

Die historische AT-Einführung und ihre tatsächliche Bestandsabnahme sind über
[Transparenz](../../docs/production/REVEAL_TRANSPARENCY.md) und die
[Eigentümerabnahme](../../docs/history/AT_B_OWNER_APPROVAL.md) erreichbar.
Aktuelle Bildänderungen verwenden den [Editorweg](#aktuelle-bestandsbearbeitung).

**Aktuelle Prüfzuordnung:** Konkrete Rätsel werden während ihrer Produktion und
Integration geprüft, nicht als wachsender CI-Korpus. Keine rätselspezifischen
Unit-Tests. Der aktuelle Paketplan wählt bei Werkzeugänderungen begründete Fachmodule
mit festen synthetischen Eingängen. Reine Inhalts-PRs erhalten den allgemeinen Quellen-/Plankern ohne Player-Build;
das ist keine erneute Logik-/Proof-/Rasterprüfung. Auch der Main-Nachlauf bleibt buildfrei.
Maßgeblich: [CI-Vertrag](../../docs/ci/CI_WORKFLOW_V2.md) und
[Authoringworkflow](../../docs/production/authoring/PUZZLE_AUTHORING.md).

## Historische Integrationswege

Die früheren KAT-1-/ZA-1-Exporte, RI-A/B/C, RI-REPLAY, RI-V9 und KE-Recoveryformen
stehen im [gebundenen Vorgänger-README](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md).
Die damaligen RI-C-Phasengrenzen sind im
[historischen Transaktionsvertrag](https://github.com/venomenon328/picross/blob/62401382f58adc2e3d303b19c1ecb1f1dc8a5040/docs/SD_CATALOG.md#ri-c--phasengrenzen-für-erstregistrierung-v6)
nachschlagbar. Diese Quellen dokumentieren frühere Implementierungen und
Nachweise; sie sind keine aktuelle Writer-, Recovery- oder Replaypflicht.
Der aktuelle Integrationsweg steht ausschließlich im [RI-ONE-Einstieg](#ri-one-aktuelle-integration).

## Deduktionskern

Python **3.11+**, ausschließlich Standardbibliothek, ohne Installation von Paketen,
Netzwerk-/Modellaufrufe oder P1-Abhängigkeit. Aus dem Repository-Root ausführen;
unter Windows einen tatsächlichen Python-Interpreter statt eines Store-Alias nutzen.
Fachvertrag: [Rätselproduktion](../../docs/production/PUZZLE_PRODUCTION.md).
Prüfzuordnung: [RP1_VERIFICATION.md](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/RP1_VERIFICATION.md).
Farberweiterung: [RP2_VERIFICATION.md](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/RP2_VERIFICATION.md).
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

Der [Paarlinienvertrag](../../docs/production/PAIRED_LINES.md) ergänzt ausdrücklich gewählte
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
Die aktuelle kreative Handoffbindung und alle Phasengates stehen in
[PW-B](../../docs/tools/PW_B_CONTRACT.md) und
[Authoring Schritt 3](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_3.md).
Alte Import-/Reparaturmanifeste und Authoring 0.4.x legitimieren keine Paarproofs.
Historische Handoff-v2- und Export-v4/v5-Hüllen behalten ihre Originalbedeutung
nach dem [Paarlinienvertrag](../../docs/production/PAIRED_LINES.md#konkrete-produktionsbindungen-und-historische-hüllen);
sie sind kein aktueller Integrationseingang.

`assess` prüft die übergebenen gespeicherten Proofs frisch. Optionales
`--diagnosis <A-Verzeichnis>` ergänzt den unveränderten A-Dateicheck, ohne eine
erschöpfende Suche als unabhängig nachgewiesen auszugeben. Der Bericht trennt
`multiple`, `reported_unique_without_complete_deduction`, `diagnosis_incomplete`,
`line_logic_solved`, `paired_lines_solved` und vollständige Deduktion ohne
Notwendigkeitsbeleg. Difficulty 0.2 meldet R4/L5 nur bei geprüfter Linienbaseline
`stalled` und vollständigem Paarproof derselben Logik. Umfang, Zeit und
redaktionelle Freigabe bleiben eigene Angaben; kein vollständiger R0–R3-Analysator.

Die kreative Annahme monochromer Pixelvorlagen behält ihre tatsächlichen
Motiv-/Parameterentscheidungen und unabhängigen RP-3-Nachweise.
Historische Autorisierungs-v6-/Export-v3/v4-Bindungen sind am
[ursprünglichen ZA-1-Vertrag](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/ZA1_ADAPTER.md)
nachschlagbar. Die aktuelle Katalogintegration verwendet ausschließlich den
[RI-ONE-Eingang](#ri-one-aktuelle-integration); dort gibt es keine Zulassung
über alte Exportnummern oder `--manual-authorization`.

## Instrumentierte Einzelanalyse (SD-A) und feste Bewertung (SD-B)

Der freigegebene [SD-Vertrag](../../docs/difficulty/PUZZLE_DIFFICULTY.md), Ursprung
[#235](https://github.com/venomenon328/picross/issues/235), bindet die getrennte
Bewertungsspur mit instrumentierten R0–R3-Regeln und synchronen Wellen.
Bestehende Proofverträge und der unabhängige R4-Notwendigkeitsbeleg bleiben
unverändert. SD-B bindet feste Skalen- und Größenregeln an unabhängige synthetische
Referenzen; der reale Katalog ist weder Kalibrierungskorpus noch Testbestand.
Auch Kopien realer Rätsel dürfen keine automatisierten Bewertungsfälle werden.

SD-C1 führt den gemeinsamen manuellen Weg für ausgewählte Bestandsrätsel und
neue Rätsel nach finaler Deduktionsprüfung ein: Bericht erzeugen, Bindungen prüfen,
ausdrücklich beauftragt übernehmen. Passende Berichte sind wiederverwendbar.
Die [Methode 0.3](../../docs/difficulty/SD_CALIBRATION.md) ist als opt-in Einzelbewertung
implementiert; [SD-C1](../../docs/difficulty/SD_CATALOG.md) liefert die technische Übernahme.
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

Der vollständige [SD-A-Vertrag](../../docs/difficulty/SD_ANALYZER.md) definiert die endlichen
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

Der [technische Vertrag 1.0](../../docs/difficulty/SD2_ANALYZER.md) wurde vor Code versioniert.
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
über PR #408 integriert. [Historische Prüfzuordnung](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_A_VERIFICATION.md).

## SD2-C: gemeinsamer Integrationsvertrag

[SD2-C-V01](../../docs/difficulty/SD2_INTEGRATION.md) bindet vor Code die neuen Checked-/
Rating-/Kontext-/Reportformate, Runtime-v5 und Journalgenerationen. Die bisherigen
0.3-Formate und eigenständigen A-/B-CLIs bleiben geschlossen. Der reale
Produktionsdefault ist nach [D-F01/T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_D_ADOPTION.md)
auf dem Arbeitsbranch 0.4. Neue `--method`-Auswahl und explizites
`catalog_method plan/adopt` folgen diesem Vertrag.
[SD2-C-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_C_VERIFICATION.md) ordnet die synthetischen Nachweise zu.
C ist nach separatem R01 über PR #410 integriert;
[D-V01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_D_VERIFICATION.md) liefert den gesondert beauftragten
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
Die geprüfte Bewertung wird als aktuelle Bewertung im finalen Input gebunden;
`target_adapter plan/register --input` liest ausschließlich diesen Input. Rasteränderungen
benutzen den separaten aktuellen Editor.
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

Der [B-Vertrag](../../docs/difficulty/SD2_CALIBRATION.md) bindet vorab festgelegte unabhängige
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
`--r4-baseline`; kein automatischer Paarlauf. [SD2-B-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD2_B_VERIFICATION.md)
bindet den historischen Lieferstand/Selbstreview; B ist nach separatem R01
über PR #409 integriert.

## SD-C1: Kandidat, geprüfter Input, Vorschau und Übernahme

[Daten-/Recoveryvertrag](../../docs/difficulty/SD_CATALOG.md). Keine dieser Operationen läuft
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
Der Wrapper prüft für neue Bewertungen den expliziten Modus anhand der
tatsächlich benutzten Vordergrundfarben nach [ZA-1](../../docs/production/ZA1_ADAPTER.md#eingang-und-grenzen)
und bindet ihn an die analysierten Definitionsbytes in
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

Eine geprüfte Bewertung bei Bedarf ausdrücklich an die finale Definition binden:

```sh
python -m tools.puzzle_production.catalog_analysis rebind --input <final-definition.json> --production-mode <mono-oder-color> --rating <work/checked.json> --output <work/final-checked.json>
```

Rebind verlangt identische ID, Produktionsmodus, kanonische Logik und Zielmatrix;
ursprüngliches `rating.source` bleibt erhalten. Die aktuelle fachliche Auswahl
und zulässige Integration bestimmen [SD-Catalog](../../docs/difficulty/SD_CATALOG.md)
und [SD2-Integration](../../docs/difficulty/SD2_INTEGRATION.md). Die passende fertige
Bewertung gehört in den [RI-ONE-Eingang](#ri-one-aktuelle-integration).
Alte `--rebind-difficulty`- und `plan-update`-/`update`-Routen sind abgelöst;
Rasteränderung registrierter Rätsel verwendet den [Editor](#aktuelle-bestandsbearbeitung).

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
konkret ohne Mutation. Der aktuelle gemeinsame Katalogjournalvertrag steht in
[SD-Catalog](../../docs/difficulty/SD_CATALOG.md#aktuelle-katalogjournale);
frühere Journalgenerationen sind keine aktuellen Recoveryeingänge.
Der gemeinsame Lock schützt Registrierung, Editor, Sync und Adoption. Nach Unterbrechung:

```sh
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

Recovery prüft vollständig vor Mutation und stellt eine gültige Altprojektion
her. Fremdänderungen erhalten Dateien und Journal; den Konflikt klären, nicht
den Lock löschen oder durch `sync-runtime` umgehen. Formen und Grenzen stehen im
[aktuellen Katalogvertrag](../../docs/difficulty/SD_CATALOG.md#aktuelle-katalogjournale).

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

[Package CI](../../docs/ci/CI_WORKFLOW_V2.md) wählt `production.solver/images/adapter/catalog`
über den aktuellen Paketplan. [Fachgruppen](../../docs/ci/CI_A_SELECTION.md) und
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
Installation. Jedes Ausgabeziel muss **neu/nicht vorhanden** sein. Die
[Beispielquelle](../../examples/rp3/README.md) liegt im Repository. Der
[Offlinevergleich des damaligen Produktionsbundles](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp3/production/index.html).
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
Die gebundene `manual_authorization` und unveränderten Originalbindungen werden
in der kreativen Arbeitsprüfung behandelt; fachliche Einordnung:
[ZA-1: kreative Vorbereitung](../../docs/production/ZA1_ADAPTER.md#kreative-werkzeuge-und-fachliche-qualität).
Dieser Weg ersetzt weder RP-5 noch dessen Such-/Nachweisvertrag.

Die additive v2-Autorisierung unterstützt auch feste manuelle Einfügungen in
gespeicherten Mono-Rasterimporten und eine ausdrücklich an die Endauswahl
gebundene Randregel-Ausnahme. Beide RP-3-Bündel, sämtliche feste Edits und der
Endproof werden frisch geprüft; Original-ZIP/Handoff/Inventar bleiben unverändert.
Schema, Grenzen und synthetische Tests: [ZA-1-v2-Vertrag](../../docs/production/ZA1_ADAPTER.md).

Die additive v3-Autorisierung bindet bereits versiegelte feste Farbkorrekturen
mit nachträglicher menschlicher Motiv-/Parameterannahme. Sie replayt eine begrenzte
Kette gespeicherter Edits mit exakten Schutzmasken und prüft sämtliche RP-3-/RP-5-
Herkunfts- und Proofbindungen frisch. Originale bleiben unverändert, alle übrigen
Inhaltsgates einschließlich Randregel Pflicht. Die Autorisierung gehört zur
Arbeitsprüfung, der finale Katalogeingang zu [ZA-1](../../docs/production/ZA1_ADAPTER.md).

Die additive v4-Autorisierung unterstützt feste manuelle Farbkorrekturen aus
einer bereits freigegebenen Motivvorlage. Original-ZIP, Handoff, Inventar und
Motivfreigabe bleiben unverändert; Parameter werden am Originalimport geprüft,
danach die exakte feste Zellkette und sämtliche unabhängigen Proofs. Alle
Inhaltsgates und echte Endabnahme bleiben Pflicht. Auch diese Arbeitsform ist
kein eigener Katalogexport; aktueller Eingang nach [ZA-1](../../docs/production/ZA1_ADAPTER.md).

V5 ergänzt ausdrücklich freigegebene feste Farbkorrekturen aus einem unabhängig
bestätigten ursprünglichen `stalled`-Direktimport. Die Originalquelle und der
vollständige Fixpunkt werden frisch geprüft; alle korrigierten Kindstufen
benötigen vollständige Zertifikate. Eigentümerbindung, Masken und Endabnahme
bleiben Pflicht; v1–v4 werden nicht gelockert. CLI/Exportformate bleiben gleich.
[ZA-1-v5-Vertrag](../../docs/production/ZA1_ADAPTER.md).

[Versionierter Vertrag, Status-/Exitcodes, Schema-/Hash-/Ressourcengrenzen](../../examples/rp5/README.md),
[Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP5_VERIFICATION.md), [Offlinevergleich](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp5/index.html).
Gleiche isolierte Image-Umgebung; keine neue Abhängigkeit. P1-Export und Spiel
bleiben unverändert; `export-p1` weist das eigene Reparaturmanifest zurück.

```sh
python -m tools.puzzle_production.repair search --reference <aktuelles-importbundle> --plan <reparaturplan.json> --output-dir <neues-reparaturbundle>
python -m tools.puzzle_production.repair verify --reference <aktuelles-importbundle> --bundle <reparaturbundle> --report <neuer-pruefbericht.json>
```

Alle Ausgabepfade neu. Der ausdrücklich benutzte alte Operationsreader rekonstruiert seine
Kandidaten temporär; aktuelle Authoringreader prüfen nur das aktuelle Ergebnis. Ein ursprünglicher
Abbruch wird nicht zur logischen Freigabe aufgewertet. Aktuelle Ergebnisse benötigen keine dauerhafte Vorher-/Nachher-, Plan- oder
Schutzmaskenkopie nach Abschluss der Operation.
Die CI prüft das allgemeine Verfahren mit synthetischen Eingängen; der alte
RP5-Korpus, seine Suchpläne und der separate Replayjob werden nicht benötigt.

## Historische Produktionen und Abschluss

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## KU-B: Hinzugefügt-Metadaten

`catalog_added` validiert ID-gebundene Sidecars und dauerhafte Quellenbelege;
Registryprojektion, Registrierung, Update, Sync, Bewertungsadoption und Recovery
verwenden den aktuellen Katalogtransaktionsweg. Runtimeprojektion und reine
Spieler-Lesekompatibilität stehen in [RI-ONE](../../docs/production/PUZZLE_INTEGRATION_SINGLE_PATH.md#21-geschlossene-aktuelle-runtimeprojektion).
Der separate historische Nachtrag läuft ausdrücklich und ohne Analyse:

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
Recovery vor Mutation. Details: [KU-B-Vertrag](../../docs/game/CATALOG_SORTING.md),
[Bestandsplan](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/KU_B_BACKFILL.md).

## Bildrevisionen: aktueller Weg und AT-Historie

Aktuelle registrierte Bilder werden über den
[gezielten Editor](#aktuelle-bestandsbearbeitung) bearbeitet. `catalog_reveal`
leitet ebenfalls auf die aktuelle Bild-CLI; der frühere eigene AT-Plan-/Adopt-
Vertrag und seine Binärjournale sind abgelöst. Seine früheren Feldformen,
Befugnisse und Nachweise bleiben im
[historischen AT-Abschnitt](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md#at-noch-zu-implementierender-bildupdateweg).
Die weiterhin geltenden visuellen Regeln besitzt der
[Transparenzstandard](../../docs/production/REVEAL_TRANSPARENCY.md).

## HP-I1b2: eigenständiger Hintergrundwechsel und revisionsgenauer Abschluss

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## HP-I1c: Rasterupdate und Revealadoption gültiger Hintergrundziele

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## HP-I2: Runtimeanschluss und isolierter Hintergrundimport

[Paketentscheidung](https://github.com/venomenon328/picross/issues/561#issuecomment-6770077470)
und [normativer Runtimevertrag §13](../../docs/production/PUZZLE_BACKGROUNDS.md#13-hp-i2--runtime-darstellung-und-besuch)
führen Reader v6, papiergebundene Darstellung A und begrenztes Bedarfsladen im
regulären Buch. Die bestehende `game/data/background-capability.json` darf erst
mit diesem funktionierenden und technisch abgenommenen Weg true sein. Die
einmalige unabhängige Renderer-/Gestaltungsabnahme steht am konkreten Produkt-
Head; sie ist keine zusätzliche persönliche Buchabnahme pro produzierter Datei.
Neue Produktion folgt der aktuellen [Authoringroute](../../docs/production/authoring/PUZZLE_AUTHORING.md).
0.6-/0.7-Paketformen behalten ausschließlich ihre bezeichnete Lesegeneration.
Der historische Aktivierungsabgleich aus #560 ist kein neuer Default- oder Betriebsauftrag.

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

Das gebundene HG31-Profil bestimmt Maße und Pixelmodus; der Import verwendet verlustfreie Kompression
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

Das frühere Offline-Sheet ist entfernt. Seine Bedienung ist ausschließlich im
[historischen README](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md#mj-b-eigener-hintergrundwechsel-im-offline-sheet)
erhalten. Neue Produktion verwendet [PW-B](#pw-b-neue-produktion-080), die Pflege
registrierter Bilder den [aktuellen Editor](#aktuelle-bestandsbearbeitung).

## PW-A: lesende Git-/Bildansicht

[Launcher, Projektor und geschlossene Datenformen](../production_workspace/README.md)
stehen separat bereit. PW-A liest neu veröffentlichte Handoff-v3-/Record-v2-
Arbeitsstände über Index und `workspace.json`; keine Alt-WIP-Konvertierung.
Der Projektor schreibt ausschließlich die neue Ansichtsdatei, der HTTP-Dienst
ist projektseitig Leser. Der fünfstufige Default und die verbindliche
Phasenveröffentlichung folgen erst PW-B; bestehende Produktionsbefehle bleiben.

## PW-PERF-B · Begrenzte Erstregistrierungsprüfung

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## PW-PERF-C · aufrufgebundene Prüfung und Hintergrund v2

Die geschlossenen HP-W2-v1/v2-Formen und das unveränderte PNG2304-Profil stehen
in [Hintergrund §4](../../docs/production/PUZZLE_BACKGROUNDS.md#4-hp-w2-eigenständige-datei--und-ableitungsschnittstelle).
Neue Ableitungen verwenden Request/Befund v2 und Tool `picross-background-2`;
Git-`producer` bleibt getrennt vom Bildkern aus `background_render.py` und
`image_normalization.py`. Alle Consumer prüfen v1 und v2 generationsgenau;
keine Neusiegelung alter Originale oder Erweiterung von #645.

frühere Export-v6-Strecke (aktuell durch RI-ONE ersetzt) prüft Original und tatsächliches Staging jeweils vollständig. Zwischen
beiden ersetzt ausschließlich der eigene unveränderte, byte-/pfadgebundene
Aufrufkontext die redundante volle Pending-Inspektion. Ein geschlossener Vergleich
der geschriebenen Pending-Dateimenge samt Bytes/Manifest und frischen Identitäten
bleibt Pflicht. Inspection, Hashliste, Methoden, Freigaben, Notices, Kategorien und
vollständige Readbacks bleiben gebunden. Vor Publikation werden Quellen und Ziel
frisch geprüft. Separates verify-export beginnt immer eine vollständige Prüfung.

Der Finalizer darf zwei Projektionen aus einem vollständig geprüften gemeinsamen
Paket-/Record-/Quellkontext ableiten. Nur ein geschlossenes Delta der bereits
unabhängig geprüften Zustands-, Hintergrund- und Freigabefelder ist zulässig;
abweichende Darstellungs-/Bild-/Angebotsquellen verlangen vollständige Prüfung.
Alte und neue Inhalts-/Freigabeprüfung bleiben eigenständig. Sidecar vor Record,
Bytevergleich, Fremddatenschutz, Wiederaufnahme und No-op bleiben verbindlich.
Keine Befunde über Aufrufe, Ziele oder Locks hinweg weiterverwenden.


## PW-PERF-E · Gezielter Abschluss aktueller Quellen

Dieser frühere Weg ist durch [RI-ONE](#ri-one-aktuelle-integration) ersetzt.
Frühere Formen und Befehle bleiben im
[gebundenen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/tools/puzzle_production/README.md)
nachschlagbar. Aktuelle Bild-/Rasterpflege verwendet den [Editor](#aktuelle-bestandsbearbeitung),
aktueller Abschluss [Authoring Schritt 5](../../docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## HG31: explizite Profilwahl

Neue Einzelkompositionen sind exakt 3:1. HP-W2: `describe --profile-id
picross-background-png2304x768-v1` (in einer Zeile aufrufen), dann dessen
vollständiges Profil/Hash in Request v2 und Entscheidung binden. Ausgabe
2304×768 RGBA8; verify prüft dieselbe Bindung. Altes Profil bleibt unverändert.
Fertigimport erkennt 2304×768 bzw. 2304×576 aus validierten PNG-Bytes und
übernimmt unverändert. V1-Capability erlaubt ausschließlich das alte Profil.
[Geschlossener Vertrag](../../docs/production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).
Keine Kandidatenintegration vor geprüftem Mainmerge oder neue WIP-Migration.

## Katalogprofile für Abschlussbilder

Nach der Originalwahl erzeugt die Integrationsplanung beide Profile nach [Revealtechnik](../../docs/production/REVEAL_TRANSPARENCY.md). Die private Umgebung benötigt Pillow 12.3.0 und resvg_py 0.5.0. Ein identischer registrierter Eingang bewahrt Bildbytes und Dateizeiten. Änderungen am gewählten Original gehören in den Bestandseditor.
