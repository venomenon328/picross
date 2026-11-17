# PW-B: Authoringdaten und Ansichtsprojektion

- **Status:** aktiver technischer Vertrag; Phasenablauf in [Authoring](../production/authoring/PUZZLE_AUTHORING.md), UI und Dienst in [PW](PRODUCTION_WORKSPACE.md).
- **Neue Regelbindung:** Authoring 0.8.0, Dokumentrevision 10; Details im Abschnitt Regelquellen.
- **Feste Rasterkorrekturen:** ausschließlich [FIXED_RASTER](../production/FIXED_RASTER.md).
- **Historische Formen:** nur mit ihren eigenen Versions-/Commit-/Bytebindungen lesen; keine WIP-Migration oder Freigabeübertragung.

## Phasen und Autorität

Neue reguläre Produktion verwendet Authoring 0.8.0. Die fünf Schritte sind
Abschlussbilder → Motivvorlage → Rasterangebote → Kontextzeichnungen → Integration.
In `brief_ready`, `reveal_review`, `motif_review`, `motif_approved`,
`raster_review` und `raster_ready` sind `background` und `raster_selection` null.
Beide Hintergrundgates bleiben pending, ihre Belege null. Sie erscheinen vor
Schritt 4 nicht als Arbeitsblocker. Die bisherigen Rastergates bleiben vollständig.
`raster_ready` verlangt die frische vollständige Prüfung des geschriebenen ZIPs;
ein Sichtungsentwurf kann niemals als qualifiziertes Angebot ausgewählt werden.

`background_review` benötigt eine tatsächliche, bytegebundene menschliche
Rasterwahl aus einem veröffentlichten qualifizierten Angebot. Kandidatenzahl, Sichtung und kreative Entscheidung folgen
[Authoring Schritt 4](../production/authoring/PUZZLE_AUTHORING_STEP_4.md).
`content_ready` benötigt zusätzlich die vollständige Hintergrundbereitschaft;
`editorially_approved` entsteht erst durch die echte äußere Endfreigabe.
Registrierung und bestätigter Mainmerge bleiben getrennte tatsächliche Ereignisse.
Ein UI-Klick, kopierter Auftrag oder gespeicherte Absicht bestätigt keine Phase.

Materiell geänderte Bytes invalidieren ihre Freigaben und abhängigen Bindungen.
Eine neue Reveal-/Motivfassung macht eine daran gebundene Rasterwahl ungültig.
Eine reine Hintergrundkorrektur erhält unveränderte Raster-/Logikbelege.

## Geschlossene Produktionsgenerationen

Neue Produktion verwendet genau die folgende Generation. Die gemeinsamen
Datei-, Pfad-, Hash-, Mengen- und Ressourcenregeln des
[PB-A-Baukerns](../../tools/puzzle_production/README.md#pb-a-deterministischer-authoring-paketbau)
bleiben erhalten; die folgenden Versions-/Phasenbindungen ersetzen dessen
historische 0.6-/0.7-Auswahl. Inventar und Index bleiben v1. Bereits vorhandene
Originale werden nicht umetikettiert oder neu versiegelt.

| Gegenstand | Aktuelle Form und Bindung |
| --- | --- |
| Bauauftrag | `picross-authoring-build-request-v4`, Handoff v5, Authoring 0.8.0 und neue Regelaufnahme Revision 10. |
| Originalhandoff | `picross-authoring-handoff-v5`; Mehrdateiregelbuch v2 gemäß Abschnitt Regelquellen. Die zwölf Gates und ihre Belege bleiben erhalten. |
| Äußerer Arbeitsrecord | `picross-authoring-record-v4`; ursprüngliche Paket-/Inventar-/Handoffbytes, Regelbuch und tatsächliche Phase bleiben gebunden. |
| Bauergebnis | `picross-authoring-build-result-v4`; Erfolg exakt `format,status,directory,indexed,record,sheet,files`, Status `built|reused`, Record v4 und `sheet=null`. Fehler exakt `format,status,message,remaining,next_action`, Status `invalid_input|aborted`. |
| Kreative Inhaltsprüfung | `picross-authoring-content-inspection-v2`; vollständig geprüfte eigene Raster-/Hintergrundphase. Diese Form erklärt keine Integrationsbereitschaft nach RI-ONE. |
| Finalizerauftrag | `picross-authoring-finalize-request-v2`, exakt `format,record,sidecar_root,background,authorizations,files`; bestehender unintegrierter Record v4 mit wirklicher Rasterwahl und bereits deklarierter Hintergrundarbeit. |
| Finalizeroperation | `picross-authoring-finalization-v2`, exakt `format,request_sha256,record,before,after,files`; unveränderte Vorher-/Nachherbytes und getrennte Sidecars. |
| Finalizerergebnis | `picross-authoring-finalize-result-v2`; Erfolg exakt `format,status,record,sheet,operation`, Status `updated|reused`, `sheet=null`. Fehler exakt `format,status,message,remaining,next_action`, Status `invalid_input|conflict|aborted|technical_error`. |
| Projektion und Projektionsauftrag | `picross-production-presentation-v2` beziehungsweise `picross-production-presentation-request-v2`; exakt `format,puzzle_id,revision,record,title,assets,offers`. Die vollständigen Bild-/Angebotsunterformen stehen im [PW-Vertrag](PRODUCTION_WORKSPACE.md). |

### Bauauftrag und Originalhandoff

Der aktuelle Bauauftrag enthält exakt:

```text
format,handoff,document_revision,files,target,category_id,reveal_options,external,presentation
```

`presentation` ist exakt `{title,raster_offers}`. Titel und Angebotstexte haben
1–512 Zeichen ohne Steuerzeichen; höchstens 20 Angebote, je exakt
`{id,label,record:{commit,file}}`. Angebots-IDs sind eindeutig und erfüllen
`[A-Za-z0-9][A-Za-z0-9_-]{0,63}`. Es werden nur tatsächlich angebotene indexierte
Einzelrevisionen gebunden. Die Referenz prüft den kanonischen Produktionspfad
und den wirklichen vollständigen Quellencommit; `null` bezeichnet ausdrücklich
den aktuellen lokalen Quellstand, keine behauptete Git-Sicherung.

`target=repository` und ein ausdrücklich benannter Gitcheckout sind Pflicht,
auch bei synthetischen Durchstichen. Lokale ungesicherte Dateien dürfen Inputs
sein; sie sind kein veröffentlichtes 0.8-Handoff. `files` führt explizite
`{path,source,sha256,bytes}`-Objekte; `external` enthält nur die tatsächlich
gegebenen äußeren Autorisierungen gemäß PB-A. Der unversiegelte Draft hat
`inventory=null`; ausschließlich der Builder setzt anschließend die tatsächlich
erzeugte Inventarbindung.

Die zulässige Handoff-Feldmenge ist geschlossen:

```text
format,puzzle_id,revision,repo_commit,state,rulebook,inventory,brief,report,
decisions,effort,approved_parameters,proposed_parameters,reveal,motif,candidate,
repair,difficulty,gates,gate_evidence,origin_verification,palette_review,
palette_assessment,playtest,blockers,content_blockers,next_action,authorization,
test_only,final_editorial_approval,manual_edit_record,editorial_manual_derivation,
editorial,background,raster_selection
```

Nicht jedes optionale Fachfeld muss in jeder Phase vorhanden sein. Verlangte
Inputs und Entscheidungen folgen der tatsächlichen Phase; fehlende Werte
werden nicht erfunden. `background` und `raster_selection` sind immer vorhanden
und folgen den frühen/späten Nullregeln oben. `gates` und `gate_evidence`
enthalten jeweils exakt die zwölf Schlüssel:

```text
reveal_approval,motif,provenance,logic,frame,visual,difficulty,reveal_consistency,
final_editorial,target_export,background_choice,background_asset
```

Gatewerte sind `pending|pass|fail|blocked`. Der versiegelte Originalhandoff
behält `final_editorial_approval=null`; `final_editorial` und `target_export`
dürfen dort nicht `pass` sein. Spätere echte Endfreigaben werden außen gebunden.
Redaktionelle Zusatzangaben gehören ausschließlich in die dafür vorgesehenen
Felder, nicht in frei ergänzte technische Objektformen.

### Äußerer Record und Finalisierung

Record v4 enthält exakt:

```text
format,puzzle_id,revision,state,category_id,build_request_sha256,repo_commit,
document_revision,rulebook,package,handoff,inventory_sha256,
final_editorial_approval,width,height,mode,used_colors,difficulty,verification,
blockers,next_action,next_step,integration,source_commit,pr,reveal,motif,
reveal_options,parameters,background,raster_selection,presentation,candidate
```

`candidate`, `raster_selection`, `rulebook` und Bildreferenzen bleiben an ihre
geprüften Originale gebunden. `verification` gibt die tatsächlich ausgeführte
Phasen-/Inhaltsprüfung wieder, keine neue pauschale Zertifizierung. Frühe
phasenabhängig unbekannte Werte bleiben null. Die kreative Prüfung und äußere
Endfreigabe prüfen weiterhin Paletten-, Bild-, Proof- und Entscheidungsbelege.
Die unabhängige aktuelle Integration konsumiert anschließend ausschließlich den
vollständigen [RI-ONE-Eingang](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md).

Der Finalizer v2 liest die unveränderte Originalrevision zuerst vollständig.
Sein Record befindet sich in `background_review`, `content_ready` oder
`editorially_approved` und hat `integration=null`. Er veröffentlicht Sidecars
vor dem Record und ersetzt nur die gebundene Vorher-/Nachherprojektion.
Unterbrechung nach Recordwechsel lässt die alte Projektion sichtbar ungültig;
die identische Wiederholung vervollständigt sie. Fremde Bytes stoppen. Keine
Zwischenfassung committen oder als abgeschlossene Phasenübergabe ausgeben.
Die geschlossenen Hintergrund-/Sidecarunterformen stehen im
[Hintergrundvertrag](../production/PUZZLE_BACKGROUNDS.md); Finalisierung führt
keine neue Bildentscheidung, Integration oder Registrymutation aus.

### Tatsächliche Registrierung abschließen

Nach erfolgreicher Registrierung und Git-Sicherung verwendet Completion
`projector.complete(repository,record_path,commit,current_input=...)` bzw.
`--complete-record ... --integration-commit ... --input ...`. Der ausgewählte
aktuelle Integrationsinput muss bereits registriert sein; die volle Commit-SHA
muss in der aktuellen Historie liegen und genau die aktuelle Lieferung enthalten.
Zulässig sind tatsächlich endfreigegebene Record-v3/v4-Originale. Completion
behält die jeweilige ursprüngliche Recordgeneration.

`integration` ist bei der ersten Completion exakt:

```text
{operation:"register",commit:<volle-SHA>,result:<current-delivery-snapshot>}
```

`result` enthält exakt `entry,mode,metadata,runtime,files`.
`entry` enthält exakt `id,key,save_slot,definition,reveal,visible,category_id`;
`mode` bewahrt den expliziten aktuellen Wert beziehungsweise einen zulässigen
historischen Nullwert. Metadaten- und Runtimeunterformen folgen RI-ONE.
`files` bindet die ausgewählten aktuellen Definitions-/Bild-/Notice-/Rating-/
Added-Dateien als `{file,sha256,bytes}`; eine zulässigerweise abwesende ältere
Hintergrundnotice wird als `null` genauso streng verglichen wie vorhandene Bytes.
Maßgeblich ist die vollständige frisch gelesene
[`current_delivery.snapshot`](../../tools/puzzle_production/current_delivery.py),
kein Produktionsarchiv oder früheres Exportmanifest.

Der lesende Abschlussabgleich prüft diese Lieferung am gebundenen Commit; er
registriert nichts und meldet keinen Merge. Erst der geprüfte Zustand erlaubt
`registered` mit leeren Blockern. Record, Projektion und aktueller Ansichtsverweis
werden kontrolliert nachgeführt; identische Wiederholung ist No-op, ein fremder
Stand oder abweichender Registrierungscommit ist Konflikt. Historische
Completionobjekte ohne `result` bleiben nur alte Recorddaten: Der Reader prüft
Registeroperation, Commit und die dortige aktuelle Lieferung, rekonstruiert
aber keine abgelöste Export-/Originalpaketkette.

Der Integrationsbatch besitzt seinen eigenen aktuellen Eingang nach
[BA-B](PRODUCTION_BATCH.md#8-ba-b-autorisierte-serielle-einzelintegration).
Authoring-Record und Phase erweitern seine Writer-/Recoverybefugnisse nicht.

### Tatsächlich gelesene frühere Generationen

| Originalgeneration | Weiterhin gebundene Lesesemantik |
| --- | --- |
| Request v3 / Handoff v4 / Record v3 / Bauergebnis v3 | Authoring 0.8.0 mit ursprünglicher Einzeldateiregelbindung, identischer fünfstufiger Phasenfolge und eigener `raster_selection`/`presentation`/`candidate`-Bindung. Finalizer und Projektion verwenden bereits v2. |
| Request v2 / Handoff v3 / Record v2 / Bauergebnis v2 | Authoring 0.7.0 mit damaligem Hintergrund-/Phasenvertrag; Finalizerauftrag/-operation/-ergebnis v1 und Projektion v1 behalten ihre Bedeutung. |
| Request v1 / Handoff v2 / Record v1 / Bauergebnis v1 | Der ausdrücklich gewählte PB-A-/BA-A-0.6.0-Eingang mit seinen eigenen Feldern und Grenzen; keine aktuelle Workspaceprojektion. |
| Handoff v5 / Record v4 mit Regelrevision 9 | Historischer Mehrdateisnapshot mit genau seinen acht damaligen Quellpfaden; keine Umschreibung zu Revision 10. |

Die jeweiligen Reader entscheiden ausdrücklich nach Format und gebundener
Regelrevision. Die heutige normale Produktion erzeugt nur die aktuelle
Generation; vorhandene Lesefähigkeit erteilt keinen WIP-Migrationsauftrag.
Abgelöste Export-/Completion- und Einführungsaussagen sind am
[festen PW-B-Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PW_B_CONTRACT.md)
erhalten und begründen keine heutigen Writer- oder Recoverywege.

## Rasterwahl

`raster_selection` ist null oder eine inventarisierte `{file,sha256}`-Referenz
auf `picross-raster-selection-v1`. Dessen exakte Felder sind
`format,puzzle_id,source_commit,option_id,record,projection,inventory_sha256,
candidate,reveal,motif,human,test_only`.
`record` und `projection` sind `{file,sha256,bytes,copy}`: Originalpfad im
Produktionsrepository, tatsächlicher Dateihash und Bytezahl sowie Paketpfad einer
byteidentischen Originalkopie. `source_commit` ist eine vollständige Git-SHA.
`candidate` enthält exakt `variant,matrix_hash,logic_hash`; `reveal` und `motif`
je exakt `file,sha256`. `human` enthält exakt `actor,timestamp_utc,statement,evidence`;
Text-/UTC-Regeln entsprechen den bisherigen menschlichen Entscheidungen,
`evidence` ist eine inventarisierte `{file,sha256}`-Ref auf die tatsächliche Erklärung.
`test_only` muss dem Paket entsprechen. Maximal 1 MiB pro Entscheidungs-/Originaldatei.

Der Builder prüft am ausdrücklich übergebenen `history_repo` die vollständige
Quellprojektion und Originalrevision am genannten Commit. Er muss Vorfahr des
aktuellen HEAD sein; die gewählten Record-/Projektionsbytes müssen dort noch
unverändert vorliegen. Unbeteiligte neue Commits entwerten eine gültige Auswahl
nicht. Ein ersetzter Arbeitsstand benötigt eine neue Auswahl. Offer-ID, Record, Inventar, qualifizierter Rasterstatus,
Matrix/Logik sowie Reveal/Motiv müssen exakt passen. Die beiden Originalkopien
müssen den Gitbytes gleichen. Kein Fetch, keine Branchmutation und keine
Authentifizierung eines Menschen durch Software. Die spätere Offlineprüfung
prüft Kopien, deren Hashbindungen und dieselbe aktuelle Kandidaten-/Bildidentität;
sie behauptet keinen erneuten Git- oder Remotezugriff. Die vollständigen
aktuellen Rasterprüfungen bleiben zusätzlich Pflicht.

## Veröffentlichung und Bedienung

[#596/B](PRODUCTION_CURRENT_VIEW.md) ergänzt außerhalb der geschlossenen
Originalformen den gemeinsamen dateigebundenen aktuellen Ansichtsverweis.
Aktueller Builder, Finalizer v2, Projektor und Completion veröffentlichen ihn nach
vollständiger Quellenprüfung; der Akteur sichert ihn gemeinsam mit allen Originalen.
Motivgruppe, Versionsansicht und konkrete Quellwahl ersetzen die flache Hauptliste.
Ansichtsöffnung ist keine Raster-/Bildwahl oder Freigabe.

Ein Job behält `content/pw/<puzzle_id>`. Vor jedem Handoff baut der Akteur die
neue Revision, den Index und automatisch die geprüfte Projektion aus den echten
Angeboten. Er sichert alle benötigten Originale mit Commit und Push. Der Dienst
bleibt lesend; er erstellt weder Entscheidungen noch Arbeitsdateien im Projekt.
Fehlende/defekte Bilder, Quellenkonflikte und unbestätigter Remotestand sind sichtbar.
Eine lokale SHA oder localhost-Adresse wird nicht als Cloudquelle ausgegeben.

Neue Jobs brauchen nur das tatsächliche Briefing und optional eine eigene
Eingangsdatei; ID und erster Produktionsbranch werden erst vom Akteur vergeben.
Die primäre Aktion „Auftrag kopieren“ nennt den passenden Schritt, die feste
erreichbare Quelle, den kanonischen Record als Einstieg und die gewählte Option.
Folgeaufträge ergänzen nur neue Absichten/Befugnisse; vorhandene Daten und allgemeine
Regeln bleiben über diesen Einstieg und den kurzen AGENTS-/Authoringverweis gebunden.
Größe, Modus und
Farbzahl sind optionale Hinweise in Motiv-/Rasterarbeit, Kontext erst in Schritt 4.
Arbeitswurzel und Merge sind persönliche ausdrückliche Optionen; Records setzen
sie nicht. Zusätzliche lokale Bereinigung braucht einen gesonderten Auftrag. Job-/Quellwechsel löscht ungesendete Auswahlabsichten.
Nur neu geladene Gitdaten ändern den angezeigten Produktionsstand.

## PW2-B · Folgeumfang ohne neue Originalgeneration

[PW2-B / #626](https://github.com/venomenon328/picross/issues/626#issuecomment-6855815878)
verbindet im abgesendeten Schlussauftrag Hintergrundwahl/none, Endabnahme und
Integration einschließlich bedingtem Squash-Merge. Die vorhandenen Zwischen-
zustände, Finalizer-, Export-, Registrierungs- und Freigabeverträge bleiben
unverändert. Die lesende Schlussprojektion und die persönliche Mergeoption
stehen im [PW-Vertrag](PRODUCTION_WORKSPACE.md#pw2-b--schlussübersicht-und-gebundener-auftrag).
Die abgeschlossenen PW-B-/PW2-B-Einführungsprüfungen und damaligen
Windows-/Browser-/Review-/Eigentümergates stehen am
[festen Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PW_B_CONTRACT.md#nachweis-und-lebenszyklus)
und im jeweiligen Paket. Sie erzeugen keine neuen Dauerprüfungen oder
Freigabepflichten. Aktuelle Entwicklungsarbeit prüft ihren tatsächlichen Diff
nach [CI v2](../ci/CI_WORKFLOW_V2.md) und dem beauftragten Paketplan.


## PW-PERF-C · aufrufgebundene Prüfung und Hintergrund v2

Die geschlossenen HP-W2-v1/v2-Formen stehen in
[Hintergrund §4](../production/PUZZLE_BACKGROUNDS.md#4-hp-w2-eigenständige-datei--und-ableitungsschnittstelle),
ihre genau zwei Profilformen in [HG31](../production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).
Neue Ableitungen verwenden Request/Befund v2 und Tool `picross-background-2`;
Git-`producer` bleibt getrennt vom Bildkern aus `background_render.py` und
`image_normalization.py`. Alle Consumer prüfen v1 und v2 generationsgenau;
keine Neusiegelung alter Originale oder Erweiterung von #645.

Der aktuelle Export prüft den vollständigen finalen Input und die tatsächlich
kopierten Stagingbytes. Vor Publikation werden Quelle und Ziel frisch geprüft.
Separates `verify-export --input` beginnt eine vollständige aktuelle Prüfung;
keine Originalpakete oder historischen Producer werden zugelassen oder benötigt.

Der Finalizer darf zwei Projektionen aus einem vollständig geprüften gemeinsamen
Paket-/Record-/Quellkontext ableiten. Nur ein geschlossenes Delta der bereits
unabhängig geprüften Zustands-, Hintergrund- und Freigabefelder ist zulässig;
abweichende Darstellungs-/Bild-/Angebotsquellen verlangen vollständige Prüfung.
Alte und neue Inhalts-/Freigabeprüfung bleiben eigenständig. Sidecar vor Record,
Bytevergleich, Fremddatenschutz, Wiederaufnahme und No-op bleiben verbindlich.
Keine Befunde über Aufrufe, Ziele oder Locks hinweg weiterverwenden.

## PW-PERF-D · Regelquellen und Snapshotgeneration

### Aktuelle Form

| Feld | Geschlossener Wert oder Bedeutung |
| --- | --- |
| `format` | `picross-authoring-rulebook-v2` |
| `version` | `0.8.0` |
| `document_revision` | Neue Aufnahmen: `10`; historischer Mehrdateisnapshot: `9` |
| `source_commit` | Volle Git-SHA, identisch zu `handoff.repo_commit` |
| `sources` | Nach `path` lexikografisch sortierte, vollständige Liste der zur Revision gehörenden Quellmenge |

Je Quelle exakt `path,file,sha256,bytes`: `path` kanonischer Repositorypfad,
`file="rulebook/"+path`, SHA-256 und Bytezahl der unveränderten Gitblobbytes.
Keine LF-Normalisierung oder nachträgliche Umschreibung. Die fünf Feldnamen oben
sind die vollständige Objektform; unbekannte oder fehlende Schlüssel sind Fehler.

### Quellenmenge Revision 10

Genau zwölf Dateien, keine Globs bei der Validierung:

- `docs/production/authoring/PUZZLE_AUTHORING.md`
- `docs/production/authoring/PUZZLE_AUTHORING_STEP_1.md`
- `docs/production/authoring/PUZZLE_AUTHORING_STEP_2.md`
- `docs/production/authoring/PUZZLE_AUTHORING_STEP_3.md`
- `docs/production/authoring/PUZZLE_AUTHORING_STEP_4.md`
- `docs/production/authoring/PUZZLE_AUTHORING_STEP_5.md`
- `docs/production/images/README.md`
- `docs/production/images/REVEAL.md`
- `docs/production/images/MOTIF.md`
- `docs/production/images/RASTER.md`
- `docs/production/images/BACKGROUND.md`
- `docs/production/PUZZLE_QUALITY.md`

Alle sechs Authoringheader weisen Version `0.8.0` und Dokumentrevision `10` aus.
Die übrigen Quellen haben eigene Dokumentidentitäten. Die gesicherte Gesamtmenge
ist keine Anweisung, in jeder Produktionsphase alle zwölf Dateien zu lesen;
maßgeblich bleibt die phasenbezogene Authoringroute.

### Prüfung und Aufnahme

- Neue `capture`-Aufnahmen erzeugen ausschließlich Revision 10.
- Der Reader dispatcht ausdrücklich nach `document_revision`; Mischmengen sind Fehler.
- Buildrequest v4, Handoff v5, Record v4 und Buildresult v4 bleiben bestehen; das bereits vorhandene Revisionsfeld unterscheidet den Quellsatz. Phasen, Gates und fachliche Freigabebedeutungen ändern sich nicht.
- Der Builder prüft jede Quelle zusätzlich gegen den Gitblob am `source_commit` im ausdrücklich benannten `history_repo`; der Commit muss Vorfahr seines HEAD sein.
- Fehlende Quellen, fremde Commits, manipulierte Hashes/Bytes, unpassende Header und unzulässige Pfade scheitern. Kein Fetch und kein Gitwriter.
- Offline-/Export-/Ansichtsreader prüfen dieselbe geschlossene Menge, tatsächliche Bytes, Inventarbindung und Commitgleichheit. Ohne Git behaupten sie keine erneute Commitauthentisierung.
- Technische Zusatzverträge außerhalb dieser Menge werden nur vor der konkreten Operation am selben Quellcommit gelesen; ihre eigenen Daten-/Methoden-/Writerbindungen bleiben bestehen.

### Historische Bindungen

Revision 9 bleibt als Mehrdateiform mit ihren genau acht damaligen Pfaden lesbar:
`docs/ai-workflows/PUZZLE_AUTHORING.md`, die fünf
`docs/ai-workflows/PUZZLE_AUTHORING_STEP_1.md` bis `_5.md`,
`docs/PUZZLE_IMAGE_STYLE.md` und `docs/PUZZLE_QUALITY.md`.
Das sind Herkunftspfade am jeweiligen alten Commit, keine Dateien des heutigen
Arbeitsbaums. Alle sechs historischen Authoringheader müssen Revision 9 tragen.
Keine Altbindung wird als Revision 10 etikettiert oder neu versiegelt.

Historische Handoff-v2/v3/v4-, Request-v1/v2/v3- und Record-v1/v2/v3-Originale
behalten `rulebook={version,file,sha256}`. Bei Authoring 0.8.0 ist diese
Einzeldateiform nur bis Dokumentrevision 6 zulässig. Revision 7 und später
benötigen die passende Mehrdateiform; ein geändertes Versionslabel heilt keine
fehlenden Quellen. Unveränderte historische Ansichtsprojektionen behalten ihre
damaligen Datei-/Inventarbindungen.

BA-A behält seine ausdrücklich gewählten 0.6/0.7-Eingänge. Die 0.7-Referenz liegt
unter [legacy/authoring](../legacy/authoring/PUZZLE_AUTHORING_0_7_0_PREVIEW.md); ein alter
Quellcommit wird weiter gegen seinen damaligen Repositorypfad geprüft. BA-B
bindet den finalen aktuellen Integrationsinput und den eigenen Integrationsauftrag;
historischer Authoringtext ist keine zusätzliche neue Integrationsnorm.
Werkzeugbindungen führen die aktuellen zwölf Quellen mit, ohne Writerrechte oder
Budgets zu erweitern.

### Palettenausnahme

Dieser Abschnitt besitzt die geschlossenen Sicht-, Binding- und Ausnahmeformen.
Die redaktionelle Zulässigkeit steht in [Qualität §6/§8.5](../production/PUZZLE_QUALITY.md#6-gezielte-redaktionelle-einzelfallentscheidung);
Berechnung und vollständige Paarobjekte folgen dem
[P-B1-Diagnoseformat](../../tools/puzzle_production/README.md#diagnoseformat-picross-palette-assessment-v1).
Die historische Normidentität des Palettenalgorithmus bleibt unverändert.

**Generationen.** Der Reader wählt die Ausnahmeform anhand des unveränderten
Originalhandoffs, nicht anhand des Alters oder Dateipfads einer Quelle:

| Originalhandoff | Ausnahmeformat | `binding.rulebook` |
| --- | --- | --- |
| `picross-authoring-handoff-v5` | `picross-palette-editorial-exception-v2` | Das vollständige geprüfte `picross-authoring-rulebook-v2`-Objekt; aktuelle Revision 10 und historische Revision 9 behalten ihren jeweiligen geschlossenen Quellsatz. |
| `picross-authoring-handoff-v2`, `-v3`, `-v4` | `picross-palette-editorial-exception-v1` | Das unveränderte geprüfte Einzeldateiobjekt `{version,file,sha256}` des Originalhandoffs. |

**Gemeinsame Typen.** SHA-256 sind 64 kleingeschriebene Hexzeichen. Erklärungstexte
`actor`, `statement` und `reason` sind jeweils 1–4096 Zeichen lang und nicht nur
Whitespace. `timestamp_utc` ist ein ISO-Zeitstempel mit explizitem UTC-Offset und
höchstens 64 Zeichen. JSON-Objekte besitzen exakt die angegebenen Schlüssel;
fehlende und zusätzliche Schlüssel sind Fehler.

**Binding.** Exakt zwölf Felder, frisch aus den vollständig geprüften
Produktionsinputs rekonstruiert:

| Feld | Exakter Bezug |
| --- | --- |
| `puzzle_id`, `revision` | Identische Werte des Originalhandoffs. |
| `candidate` | Exakt `{bundle,variant,source_type}` mit den identischen drei Werten aus `handoff.candidate`. |
| `source` | Das vollständige unveränderte, frisch rekonstruierte und geprüfte Quellobjekt des Kandidaten. |
| `matrix_hash`, `logic_hash` | Kanonische Hashes der tatsächlich geprüften Matrix und normalisierten Logik. |
| `palette_sha256`, `source_fingerprint` | Identische Bindungen des frisch erzeugten und unabhängig geprüften P-B1-Assessments. |
| `rulebook` | Vollständiges unverändertes Originalobjekt gemäß Generationstabelle. |
| `handoff_sha256`, `inventory_sha256` | SHA-256 der wirklichen Handoff- beziehungsweise inventarisierten Originalinventarbytes. |
| `original_zip_sha256` | Hash der tatsächlich gebundenen Original-ZIP-Bytes; bei einer geprüften Ansichtsableitung dessen unveränderter Wert aus `derivation.original_zip_sha256`; `null` bleibt bei einem zulässigen Eingang ohne ZIP-Bindung `null`. |

**Visuelle Einzelurteile.** Farbpakete binden über
`handoff.palette_review={file,sha256}` einen inventarisierten
`picross-palette-visual-review-v1`-Record von höchstens 128 KiB. Dieser besitzt
exakt `format,puzzle_id,revision,matrix_hash,logic_hash,palette_sha256,criteria`.
Identität und Hashes stimmen mit dem Originalhandoff und den frisch geprüften
Produktionsinputs überein. `criteria` enthält exakt `Q-R04,Q-H01,Q-H02`; jedes
Urteil hat exakt `result,accepted,actor,timestamp_utc,statement,reason,evidence`.

- `result` ist `erfüllt|Warnung|nicht erfüllt|nicht geprüft`; `accepted` ist Boolean.
- `evidence` enthält 1–32 exakte `{file,sha256}`-Refs auf inventarisierte und
  tatsächlich geprüfte Dateien. Eine große isolierte Farbtafel ersetzt keine
  nach dem Qualitätsvertrag erforderliche Zell-/Hinweisansicht.
- `erfüllt` besteht ohne zusätzliche Ausnahme. `Warnung` oder `nicht erfüllt`
  erfordern `accepted=true` mit wirklichem Wortlaut und Begründung.
  `nicht geprüft` besteht nie, auch nicht mit `accepted=true`.
- Mono führt hier keinen Farbprüfrecord; sein eigenes visuelles Gate bleibt
  erforderlich. Ein positives S-Ergebnis ersetzt keine visuelle Prüfung.

**Äußerer Ausnahmerecord.** Höchstens 128 KiB, exakt neun Felder:

| Feld | Typ und Bindung |
| --- | --- |
| `format` | Exakter Wert aus der Generationstabelle. |
| `binding` | Das vollständige zwölfteilige Binding oben, kanonisch identisch zur frischen Rekonstruktion. |
| `negative_pairs` | Das vollständige unveränderte Array `assessment.negative_pairs`, einschließlich aller exakten S-/RGB-/ID-Werte; keine Teilmenge. |
| `actor`, `timestamp_utc`, `statement`, `reason` | Tatsächliche Erklärung und Begründung nach den gemeinsamen Typen. |
| `approval_sha256` | Hash der tatsächlichen Endfreigabebytes. |
| `test_only` | Boolean, identisch zum Scope des Originalhandoffs. |

Der Record ist nur bei einem vollständig geprüften negativen Paarbefund und
wirklicher Endfreigabe zulässig. Er liegt als reguläre nicht aliasierte Datei
außerhalb des versiegelten Originalpakets; keine Symlinks, Reparsepunkte oder
Hardlinks. Eine zulässige Paketdarstellung erhält die unveränderten Bytes als
`palette-exception.json`; ihr Gatefeld `exception` ist exakt `{record,sha256}`.
Der Reader prüft sämtliche Bindungen und alle negativen Paare frisch. Fremde,
unvollständige oder mutierte Bindungen scheitern; die Software authentifiziert
keinen Menschen und erzeugt keine Erklärung.

Der technische Negativbefund bleibt negativ. Nur der konkret angenommene
Palettenredaktionsblocker entfällt. Q-R04/Q-H01/Q-H02, wirkliche Endfreigabe,
zusätzlich erforderliche manuelle Autorisierungen und sämtliche übrigen harten
Gates bleiben erhalten. Originale werden weder umgeschrieben noch umetikettiert.
