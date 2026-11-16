# PW-B · Fünfstufige Produktion 0.8.0

## #596/C · Reguläre motivtreue Rasterkorrektur

Der [geschlossene C-Vertrag](FIXED_RASTER.md) gilt für Authoring 0.8.0,
Dokumentrevision 4. Er ergänzt die Schritte 2–6 um freigegebene feste Mono-/
Farbzellenkorrekturen und leeren Außenbeschnitt, auch bei bereits gelösten Rastern.
Korridor, Schutzmaske, frische Endnachweise und echte Motivfreigabe sind Pflicht.
Die reguläre Übergabe endet bei raster_ready ohne Auswahl/Hintergrund/Endabnahme;
historische manuelle Sonderwege bleiben getrennt. Bildsichtung folgt der direkten
Originalprüfung nach Authoring §2.3/Q-B03, ohne verlagerte Montagen-/Fadepflicht.


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
Endfreigabe v2 bleibt kreativ unverändert. Integration, Registry und Recovery
folgen RI-ONE; Runtime v8 bleibt unverändert.
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

[#596/B](PRODUCTION_CURRENT_VIEW.md) ergänzt außerhalb der geschlossenen
Originalformen den gemeinsamen dateigebundenen aktuellen Ansichtsverweis.
Builder v3, Finalizer v2, Projektor und Completion veröffentlichen ihn nach
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
Der folgende Nachweisabschnitt beschreibt die historische PW-B-Einführung;
PW2-B erhält seinen eigenen Prüfplan und unabhängiges A01-Gate in #626.

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


## PW-PERF-C · aufrufgebundene Prüfung und Hintergrund v2

Die geschlossenen HP-W2-v1/v2-Formen und das unveränderte PNG2304-Profil stehen
in [Hintergrund §4](PUZZLE_BACKGROUNDS.md#4-hp-w2-eigenständige-datei--und-ableitungsschnittstelle).
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

Authoring 0.8.0 Dokumentrevision 9 führt die aktuellen Integrationsbefehle und Quellen nach RI-ONE ein. Neue geschlossene Generationen: Buildrequest v4, Handoff v5,
Record v4, Buildresult v4. Ihre Felder entsprechen v3/v4/v3/v3; allein rulebook
hat die folgende neue Form. Producer dispatcht nach Request, Reader nach Handoff/
Record. Gemischte Generationen sind Fehler. Phasen, zwölf Gates, Freigaben,
Inventar v1, Inhaltsinspektion v2, Projektion v2, Finalizerrequest/-result v2 und
Die kreativen Formen behalten ihre fachliche Semantik. Die Integration nimmt
ausschließlich den finalen aktuellen Input nach RI-ONE an. Kein unsupported WIP-Migrationsanspruch.

rulebook enthält exakt `format,version,document_revision,source_commit,sources`:
format `picross-authoring-rulebook-v2`, version `0.8.0`, document_revision 9,
source_commit volle Git-SHA identisch zum handoff.repo_commit. sources ist eine
lexikografisch nach path sortierte Liste; je Eintrag exakt `path,file,sha256,bytes`.
path ist der kanonische Repositorypfad, file exakt `rulebook/` + path; SHA-256 und
Bytezahl binden vollständige unveränderte Gitblobbytes (keine LF-Neukodierung).
Die geschlossene Menge enthält genau:

- `docs/ai-workflows/PUZZLE_AUTHORING.md` und `PUZZLE_AUTHORING_STEP_1.md` bis
  `PUZZLE_AUTHORING_STEP_5.md` im selben Verzeichnis;
- `docs/PUZZLE_IMAGE_STYLE.md` und `docs/PUZZLE_QUALITY.md`.

Alle acht Quellen liegen inventarisiert im Paket. Alle sechs Authoringheader
müssen Version/Dokumentrevision exakt ausweisen. Neue Builder vergleichen jeden
Eintrag zusätzlich mit den echten Gitbytes am source_commit im ausdrücklich
benannten history_repo; fehlende Quellen, fremde Commits, abweichende Hashes,
Bytezahlen, Pfade, Header, Formen oder Dokumentrevisionen scheitern. Der Commit
muss Vorfahr des aktuellen history_repo-HEAD sein. Kein Fetch oder Gitwriter.
Offline-/Export-/Ansichtsreader prüfen die vollständige geschlossene Menge und
alle tatsächlichen Bytes, Inventarbindung und Commitgleichheit; ohne Git behaupten
sie keine erneute Commitauthentisierung. Der Quellcommit ist Herkunft, keine
menschliche Freigabe. Alle Phasendateien im Snapshot zu sichern bedeutet nicht,
sie im normalen Phasenauftrag zu lesen.

Bedingte technische Verträge (PW-B/CLI, AT, HP-W2, RI/ZA-1, SD2, feste Korrektur,
Retirement) gehören nicht in diese Snapshotmenge. Der Router verlangt sie vor der
konkreten Operation am selben Regelquellstand; ihre vorhandenen eigenen Daten-/
Methoden-/Writerbindungen bleiben zusätzlich bestehen. Qualität wird vollständig
gebunden, aber für Farbe nur operativ §§8.4–8.5 gelesen. Historische Herleitung
wird durch die Bytebindung weder Routinelektüre noch neuer Produktionsauftrag.

Historische Handoff-v2/v3/v4-, Request-v1/v2/v3- und Record-v1/v2/v3-Pakete behalten
rulebook exakt `{version,file,sha256}` und ihre damaligen Header/Hashes. Keine
Ersatzdatei, Neubindung, Änderung oder Neuversiegelung alter Originale. BA-A bleibt
bei seinen lokalen 0.6/0.7-Eingängen; eine alte 0.6-Snapshotidentität wird gegen
ihren gebundenen Gitursprung statt gegen den heute anders organisierten Router
geprüft. BA-B bindet den finalen aktuellen Integrationsinput und einen eigenständigen
Auftrag; der Integrator verlangt keine Regelbuchherkunft. Die Package-/Batch-Werkzeugbindungen führen die
acht aktuellen Regelquellen mit. Keine Erweiterung von Writerrechten oder Budgets.

Die abgeleitete Palettenbindung übernimmt bei Handoff v5 das vollständige geprüfte
rulebook-v2-Objekt. Dafür erhält allein die äußere Palettenausnahme die explizite
Generation `picross-palette-editorial-exception-v2`: exakt v1-Felder, aber
binding.rulebook ist v2 statt Einzeldatei. Der Reader dispatcht nach Originalhandoff;
v1 gehört ausschließlich zu alten Originalen, v2 ausschließlich zu Handoff v5.
Negative Paarbefunde, echte Endfreigabe, sämtliche übrigen Bindungen und visuelle
Q-R04/Q-H01/Q-H02-Gates bleiben unverändert. Keine neue Farbmetrik oder Ausnahmebefugnis.

Rev9 ist ausschließlich über die neue Generation zulässig. Ein alter 0.8-Handoff/
Request/Record darf keinen Rev9-Einstieg als vermeintlich vollständigen einzelnen
Snapshot annehmen; für alte 0.8-Formen sind nur damalige Revisionen bis 6 zulässig.
Ein Wechsel des Versionslabels kann keine fehlenden neuen Quellen legitimieren.

Historische Ansichtsprojektionen behalten ihre frühere reine Datei-/Inventarbindung;
die neue Header-/Revisionsprüfung wird ihnen nicht nachträglich auferlegt. Der
Ansichtsreader weist jedoch eine ausdrücklich deklarierte Rev9 unter alter Form
zurück. Neue Ansichten prüfen alle neuen Quellen und Header vollständig.

HG31 erweitert ausschließlich die geschlossenen HP-W2-v2-Profilwerte nach
[Hintergrund](PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).
Die Snapshotmenge bleibt exakt acht Dateien, alle sechs Authoringheader Rev9,
Qualität 1.0/Rev13. Historische Originale werden nicht neu versiegelt.
