# PW-B · Fünfstufige Produktion 0.8.0

Vertrag vor Code · 11.11.2026 · maßgeblich ist die
[Paketentscheidung PW-B](https://github.com/venomenon328/picross/issues/578#issuecomment-6799208194).
Die Voraussetzung PW-A2 ist mit PR #580 auf `f9764a91fc0e0c717d9d4ffeb0a769ec8ec0aab9`
integriert. Dieser Vertrag konkretisiert ausschließlich den freigegebenen Umfang.

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
Rasterwahl aus einem veröffentlichten qualifizierten Angebot. Erst jetzt entstehen
drei unterschiedliche echte isolierte Kontextbilder. Nur eine dokumentierte
Eigentümerentscheidung erlaubt eine andere Anzahl oder einen frühen Verzicht.
`content_ready` benötigt zusätzlich die vollständige Hintergrundbereitschaft;
`editorially_approved` entsteht erst durch die echte äußere Endfreigabe.
Registrierung und bestätigter Mainmerge bleiben getrennte tatsächliche Ereignisse.
Ein UI-Klick, kopierter Auftrag oder gespeicherte Absicht bestätigt keine Phase.

Materiell geänderte Bytes invalidieren ihre Freigaben und abhängigen Bindungen.
Eine neue Reveal-/Motivfassung macht eine daran gebundene Rasterwahl ungültig.
Eine reine Hintergrundkorrektur erhält unveränderte Raster-/Logikbelege.

## Geschlossene neue Generationen

Alle bestehenden Grenzen, strikten JSON-/Pfad-/Hashregeln, zwölf Gates und
Inhaltsprüfer bleiben erhalten. Alte Originale behalten ihre Versionsbedeutung.
Für bestehende WIP gibt es keinen Konvertierungs- oder UI-Kompatibilitätsauftrag.

| Format | Vollständige Änderung gegenüber dem jeweiligen Vorgänger |
| --- | --- |
| `picross-authoring-handoff-v4` | v3-Felder plus `raster_selection`; Regelwerk exakt 0.8.0, neue Phase `background_review`, frühes `background=null` wie oben. |
| `picross-authoring-build-request-v3` | v2-Felder plus `presentation`; Handoff v4, neue Phasen. `presentation` exakt `{title,raster_offers}`; Titel 1–512 Zeichen, maximal 20 Angebote je `{id,label,record:{commit,file}}`, IDs/Texte/Pfade nach PW. Nur tatsächlich angebotene indexierte Einzelrevisionen. |
| `picross-authoring-record-v3` | v2-Felder plus `raster_selection,presentation,candidate`; `candidate` ist die exakte Originalbindung aus dem Handoff. Unveränderte Originalbindungen und ausdrückliche neue Phasensemantik. |
| `picross-authoring-build-result-v3` | v2-Erfolgs-/Fehlerfelder; `sheet=null`, Record v3, tatsächliche `workspace.json` unter den gebundenen Dateien. Kein neuer Offline-Sheetzustand. |
| `picross-authoring-content-inspection-v2` | v1-Felder; v4/0.8.0 mit eigener Hintergrundphase. Auch hier keine Integrationsbereitschaft. |
| `picross-authoring-finalize-request-v2` | Exakt dieselben Felder wie v1; ausschließlich Record v3 mit bereits vorhandenem Hintergrundmanifest und Rasterwahl. |
| `picross-authoring-finalize-result-v2` / `picross-authoring-finalization-v2` | Dieselben Felder wie v1, Record v3 und `sheet=null`; Operation bindet weiterhin unveränderte Vorher-/Nachherbytes. |
| `picross-production-presentation-v2` / `picross-production-presentation-request-v2` | Dieselben Felder und Grenzen wie v1, ausschließlich aktuelle v4-/v3-Arbeitsstände; `background_review` zulässig. |

Inventar v1, Index v1, Hintergrundarbeit/-entscheidung/-ableitung v1,
Endfreigabe v2, Export v6, Registry/Runtime und Recovery bleiben unverändert.
Die Exportprüfung bindet die neue Originalgeneration ausdrücklich und prüft
weiterhin alle tatsächlichen Inhalts-, Paletten-, Bild- und Freigabebytes.

Nach erfolgreicher Registrierung und deren Git-Sicherung ergänzt der Akteur
den Record mittels `projector.complete(repository, record_path, commit)` und
erzeugt dabei die Projektion automatisch neu. `integration` ist dann exakt
`{operation,commit,manifest,registry,runtime}`, `operation="register"`, Commit eine
volle SHA; die drei Referenzen sind `{file,sha256,bytes}` auf den tatsächlich
gesicherten Exportmanifest-, Registry- und Runtimeindexstand. Der lesende
Abschlussabgleich prüft die kanonischen Pfade, Bytes, registrierte ID/Revision,
Export-/Originalpaketbindung und Runtimezuordnung. Er registriert nichts und
meldet keinen Merge. Nur dieser gebundene Zustand erlaubt `registered` mit
leeren Blockern; die technische Exportprüfung bleibt unverändert im Record.
Record und Projektion werden nacheinander atomar ersetzt; nach Unterbrechung
schließt derselbe Aufruf die fehlende Projektion. Fremde Bytes stoppen.
Die neuen internen lesenden Katalogpfade sind ausschließlich `content/registry.json`,
`game/data/registry.json` und das kanonische `content/packages/<id>/<revision>/manifest.json`.
Sie sind keine frei adressierbare HTTP-Datei-API.

Finalizer v2 veröffentlicht weiterhin Sidecars vor dem Record. Danach ersetzt
er ausschließlich die aus dem gebundenen Vorher-/Nachherrecord berechnete
Projektion. Eine Unterbrechung nach dem Recordwechsel lässt den alten Stand
sichtbar ungültig; die identische Wiederholung vervollständigt die Projektion.
Keine solche Zwischenfassung committen oder als Phasenhandoff melden.

Der bestehende BA-B-Eingangsvertrag nimmt zusätzlich 0.8.0/Record v3 an;
Form, Mengen, Budgets und Writer-/Recoveryautorität bleiben unverändert.

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

Build v3 veröffentlicht ausschließlich in einen ausdrücklich benannten
Repositorycheckout (`target=repository`). Auch synthetische Durchstiche nutzen
ein isoliertes echtes Gitrepository. Lokale ungesicherte Quellen bleiben
Eingänge; sie sind kein vollständig veröffentlichtes 0.8-Handoff.

## Veröffentlichung und Bedienung

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
Arbeitswurzel, Bereinigung und Merge sind persönliche ausdrückliche Optionen;
Records setzen sie nicht. Job-/Quellwechsel löscht ungesendete Auswahlabsichten.
Nur neu geladene Gitdaten ändern den angezeigten Produktionsstand.

## Nachweis und Lebenszyklus

Kern docs/ci-required einschließlich Windowsbau; genau `tools`,
`production.adapter`, `production.catalog`. T01: kleine echte synthetische
Gitproduktionen Farbe/selected und Mono/none bis Export/Plan/Registrierung,
Negative, No-op und Unterbrechung/Recovery. T02: tatsächliche Aufträge und reale
Browserbedienung am finalen Head sowie getrennte Windows-Starterprobe.
T03: Quellen-/Consumer-/Versionsabgleich und einmalige begrenzte Kostenmessung.
Keine Bild-/Solveralgorithmen, echte Produktion, automatische Chromium-CI oder
technischen Uploads. Höchstens die zwei ausdrücklich vereinbarten UI-PNGs
auf befristetem Reviewref, Originalabruf vor Übergabe prüfen; maximal sieben Tage.
PW-B-A01 (unabhängiges Review) und PW-B-M01 (Eigentümerdurchlauf oder ausdrücklicher
paketbezogener Erlass) bleiben vor Merge. Dieser Auftrag enthält keinen Merge.
