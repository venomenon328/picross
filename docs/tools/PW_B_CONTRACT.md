# PW-B: aktueller Produktionsstand

Dokument-ID: `authoring-current`
Status: `active`
Stand: 17.11.2026 · [PROD-SLIM / #700](https://github.com/venomenon328/picross/issues/700)

## Phasen und Autorität

Authoring 0.8.0 verwendet genau einen aktuellen Record je Job. Die fünf Schritte
bleiben Abschlussbilder → Motivvorlage → Rasterangebote → Kontext → Integration.
Kreative Regeln und fällige Entscheidungen stehen in [Authoring](../production/authoring/PUZZLE_AUTHORING.md),
Einzelurteile in [Qualität](../production/PUZZLE_QUALITY.md). Technische Prüfung
erzeugt keine menschliche Erklärung. Es gibt keine neue persönliche Abnahmeschleife.

## Geschlossene aktuelle Form

`content/authoring/<puzzle_id>/current/record.json` ist die einzige aktuelle
Metadatenautorität. Veröffentlichungsformat `picross-authoring-current-v2`, exakt:

`format,work_release,puzzle_id,revision,source_commit,operation,target,title,category_id,state,brief,parameters,assets,rasters,selected,decisions,budgets,blockers,test_only,integration`.

- `work_release` bindet die numerische Release-ID (`id`) und den vollen bereinigten Tagzielcommit (`anchor`), auch bei leerem Angebot.
- `revision=current`; Git bindet den jeweiligen veröffentlichten Stand. Keine Paketkette.
- ID: `pz-[a-z0-9][a-z0-9-]{0,59}`; source_commit: volle 40-stellige kleine Git-SHA zur aktuellen Quellenzuordnung. Kein Snapshot oder historischer Erzeugerzugriff.
- operation: production/background. target ist bei production null, bei reiner Hintergrundpflege exakt definition/reveal als aktive Refs und mode=mono|color. Unveränderte aktive Raster brauchen dafür keinen neuen Proof oder Difficulty. Die Rasteransicht verwendet die gebundene Definition und den Modus des aktiven Ziels. Spätere Hintergrundpflege für registrierte IDs verwendet den gemeinsamen Editorweg.
- budgets: exakt limits/used, jeweils raster_candidates/repair_rounds/image_corrections als ganze Zähler 0–1.000.000. Used bleibt monoton; Erhöhung eines Limits braucht eine echte budget-Entscheidung. Nur aktueller Budgetverbrauch, keine Versuchsliste oder interne Historie.
- title: 1–128 Zeichen, brief: 1–16384, übrige Texte: 1–4096, ohne NUL; category_id nach Kategorienvertrag, bei ungeklärter Zuordnung null.
- parameters: exakt `proposed,approved`, jeweils Liste mit höchstens acht gültigen vorhandenen Rasterparameterobjekten. Frühe Vorschläge mit exakt einer Vordergrundfarbe dürfen den Modus offenlassen. Bei der Parameterfestlegung ergibt das mono. Explizites color plus 1 ist ein Widerspruch. Approved braucht den expliziten Modus und eine tatsächliche Motiv-/Parameterentscheidung. Mehrere Objekte sind vollständige Alternativen: Ein Raster muss mindestens eine ganze passende Option erfüllen. Sein expliziter Checked-Modus muss zu einer solchen Option gehören; ohne Checked ist ein eindeutiger Modus nötig. Einzelne Felder verschiedener Optionen dürfen nicht vermischt werden.
- assets: höchstens 100 Objekte `id,role,label,file,rights,review`. Eindeutige ID nach `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`; role: reveal/motif/background/input. label 1–512 Zeichen. file ist Ref. rights: null bei offener Klärung, sonst exakt `author,usage_basis,source,changes`, mit tatsächlichen Angaben. review: Kriterien-ID → Urteil.
- rasters: höchstens 20 Objekte `id,label,definition,proof,difficulty,preview,review,exceptions`. Definition/preview sind Refs; proof/difficulty bleiben bei ungeprüften Sichtungsentwürfen ausdrücklich null, qualifizierte Angebote brauchen alle vier Refs auf aktuelle Nutzdaten; kein Import-/Reparaturbaum. Definition und Proof müssen dieselbe endgültige Runtime-Farbsemantik verwenden. Vorschau und Beschriftung folgen dem nachstehenden Sichtvertrag. Difficulty ist der bestehende Checked-Befund. exceptions ist die aktuelle RI-ONE-Liste konkreter frame-/palette-Ausnahmen mit Erklärung und Beleg.
- Urteil: exakt `result,accepted,reason,method,actor,timestamp_utc`; result erfüllt/Warnung/nicht erfüllt/nicht geprüft, accepted bool. Negative und ungeprüfte Befunde bleiben unterscheidbar. Annahme braucht die konkrete echte Entscheidung; harte Kriterien sind nicht redaktionell heilbar.
- selected: exakt `reveal,motif,raster,background`, jeweils ID oder null; background zusätzlich none/standard. Null bedeutet offen. Jede gesetzte Auswahl verlangt bereits vor Verdichtung eine gültige Entscheidung desselben Scopes; die unveränderte aktive Revealreferenz eines Hintergrundjobs benötigt keine neue Bildwahl. Angebote bleiben bis zur Entscheidung erreichbar. Danach bleiben nur gewählte Dateien und noch benötigte Eingaben.
- decisions: höchstens acht Objekte `scope,binding,actor,timestamp_utc,statement`, je Scope genau eine noch gültige echte Erklärung. scope reveal/motif/raster/background/final/integration/budget; binding ist H des aktuellen semantischen Auswahlscope nach `current_authoring.binding`. UTC explizit Z/+00:00; ein nicht überlieferter Prüfzeitpunkt im Urteil bleibt null. Keine separate kopierte Erklärung, Prompt- oder Korrekturdatei. Tatsächliche Inhaltsänderung invalidiert abhängige Entscheidungen; reine Pfad-/Beschriftungsumstellung gleicher Bytes erhält kreative Wahlen. Endabnahme/Integration binden zusätzlich aktuelles Briefing, Titel/Kategorie, Rechte, Sichturteile und technische Ausnahmen.
- blockers: höchstens 64 konkrete aktuelle Texte. test_only: bool, unveränderlicher Scope. integration: null oder `commit,result` der tatsächlich erreichten aktuellen Lieferung nach RI-ONE; keine historische Receiptdatei.

Aktive Repositoryreferenz: exakt `file,sha256,bytes`; sicherer repositoryrelativer POSIX-Pfad,
64 kleine Hexzeichen, positive tatsächliche Bytezahl. Zulässig sind eigene
Produktressourcen im fixierten Gitbaum. Eine eigene Arbeitsdatei unter
`content/authoring/<id>/` hat dieselben drei Messfelder und genau ein
zusätzliches Objekt `asset` mit `repository,job,release_id,asset_id`.
Repository ist venomenon328/picross, job dieselbe Rätsel-ID, beide numerischen
IDs sind positiv. Der Reader prüft Zugehörigkeit zum eigenen Arbeitsrelease,
Bytezahl und SHA-256 vor der fachlichen Dekodierung. Keine Links, Hardlinks,
Reparsepunkte, Traversal, Windowsgeräte-, Case- oder Datei-/Ordneraliase.
Record höchstens 1 MiB, Definition 2 MiB, Proof 64 MiB, Bild 32 MiB,
sonstige JSON-Nutzdatei 8 MiB, insgesamt höchstens 512 MiB/2048 aktive Dateien.
Tiefe höchstens 32; eindeutige Schlüssel und endliche Zahlen. Kein ZIP,
Regelbuch, Generator-/Codec-/Toolhasharchiv oder Inventar als neue Pflichtdatei.

### Rastervorschau und Bindung

- Aktuelle Darstellung und neue Vorschau-PNGs bilden jede Zelle ohne Glättung in
  12×12 Pixeln ab. EMPTY ist transparent. Bei mono sind belegte Zellen opak
  schwarz (#000000), bei color behalten sie ihre tatsächlichen RGB-Werte.
  Kachel und Großansicht verwenden dieselbe aus der gebundenen Definition und
  dem geprüften Modus gerenderte Ansicht.
- Der explizite Checked-Modus muss zum ganzen genehmigten Parameterobjekt und
  zur tatsächlichen Zahl unterschiedlicher belegter Zellwerte passen. Die
  Modusgrenze für Produktion und Erstintegration steht in [ZA-1](../production/ZA1_ADAPTER.md#eingang-und-grenzen).
- Der Reader prüft Dateibindung, dekodierte PNG-Maße und sämtliche RGBA-Pixel.
  Ein bereits gebundenes mono-Original darf exakt die frühere farbgetreue
  12×12-Darstellung enthalten. In einer Fortschreibung darf diese Fassung nur
  aus dem Vorgänger für dieselbe Angebots-ID und dieselben Definitions- und
  Vorschauhashes übernommen werden. Die Ansicht rendert auch dann neutral.
  Neue Vorschauen müssen der aktuellen Darstellungsregel entsprechen.
- Der Autor beschriftet neue monochrome Angebote mit Maßen, Modus und
  Motivmerkmalen nach [Schritt 3](../production/authoring/PUZZLE_AUTHORING_STEP_3.md#45-geprüfte-raster-zur-menschlichen-auswahl).
  Die Oberfläche übernimmt das gebundene Label. Ein altes Label kann über die
  aktuelle Authoring-Fortschreibung redaktionell korrigiert werden. Beim Austausch
  des Vorschau-PNGs bindet der Record die neuen gemessenen Bytes. Definition,
  Proof, Difficulty und unveränderte semantische Entscheidungen können dabei
  weiterverwendet werden.

## Zustände und aktuelle Prüfung

brief_ready/reveal_review brauchen gültiges Briefing und vorhandene Angebote;
motif_review zusätzlich gewähltes freigegebenes Reveal und Motivangebot;
motif_approved/raster_review zusätzlich echte Motiv-/Parameterfreigabe.
Die oben beschriebene v2-Form verlangt für `raster_ready` bei jedem angebotenen
Raster Maße/Palette/Hinweise, vollständigen unabhängigen Proof mit
Endmatrixvergleich, gebundene Difficulty, fällige Sichturteile und passende
Parameter. Hintergrundarbeit ist vorher kein
Blocker. background_review braucht eine wirkliche qualifizierte Rasterwahl.
content_ready zusätzlich gültigen Hintergrund selected/none/standard, Rechte
und Bildurteile einschließlich H-07. editorially_approved braucht echte Endabnahme
und Integrationsauftrag am aktuellen Auswahlscope; registered zusätzlich einen
frisch bestätigten tatsächlichen Registrierungsstand. Blockierte Arbeit bleibt
in ihrer wirklichen Phase mit konkreten Blockern; kein erfundener Phasenerfolg.

Prüfung beginnt bei aktuellen Ergebnissen, nicht bei ihrer Erzeugung. Kein Replay
von Import, Normalisierung, Reparatur oder Bildableitung als Zulassung. Aktuellen
Proof tatsächlich unabhängig prüfen. Bildqualität, Transparenz/Randabschluss,
Motivtreue, Parameter und reale Nutzungs-/Integrationsbefugnis bleiben erforderlich.
Kein Ergebnisflag ersetzt die jeweilige Prüfung.

## Bau, Auswahl und sichere Fortschreibung

Builderrequest `picross-authoring-current-request-v1`: exakt
`format,record,expected,files`. record ist obige Form; expected ist null für
Neuanlage oder SHA-256 der erwarteten Recordbytes; files enthält ausschließlich
neue benötigte Nutzdateien als `path,source,sha256,bytes` relativ zu explizitem
source_root. Vorhandene aktive Dateien referenzieren, nicht kopieren.
API/CLI bleiben authoring_builder.build beziehungsweise build --request
--source-root --output-root --publish-to. Der aktuelle Weg benötigt publish-to;
kein Benutzer pflegt JSON in der Oberfläche. Der Produktionsakteur erstellt den
Request aus den aktuellen Ergebnissen und tatsächlichen Erklärungen.

Builder und Finalizer bearbeiten den lokalen Arbeitsstand. Die lokal messbare
Form v1 hat dieselben Inhaltsfelder und Dateibindungen ohne Transportidentität.
Vor Originalabruf, Finalizer oder großem Checkout kann der Akteur aus einem
fest gebundenen vertrauenswürdigen Werkzeugstand die geplante Operation prüfen.
Für den folgenden Befehl genügen Git, GitHub-Zugang und der Werkzeugstand.

```text
python -m tools.work_publish preflight <id> --for publish --repository venomenon328/picross --expected <new-oder-arbeitscommit> --auth env
```

Die Python-API `work_publish.preflight(root, operation, job, expected,
repository=..., auth=...)` akzeptiert als `root` ein vorhandenes Verzeichnis,
als Operation `publish`, `resume` oder `retire` und für eine Erstpublikation
`expected=None`. Der JSON-Bericht enthält Git-/REST-Basis, Arbeits-SHA,
Release-/Tagbindung und den Prüfstatus je Fähigkeit. Gitref-Zugriff und
Release-/Assetzugriff werden einzeln ausgewiesen. Schreibrechte und der Zugriff
auf Originalbytes bleiben bis zur jeweiligen Operation offen. Produkt-PR und
seine CI haben einen eigenen Zugang. Der Preflight führt nur Leseoperationen aus
und wird nicht im Record abgelegt.

Die eigentlichen Operationen laufen im eigenen Checkout.

```text
python -m tools.work_publish publish <id> --expected new
python -m tools.work_publish resume <id> --expected <arbeitscommit>
python -m tools.work_publish publish <id> --expected <arbeitscommit>
python -m tools.work_publish retire <id> --expected <erwarteter-Arbeitscommit>
```

Der [PW-LOCAL-Einstieg](PRODUCTION_GIT_WORKSPACE.md) bindet den Jobworktree an den erwarteten Commit. Resume lädt die gebundenen Originale in denselben Ordner. Für die
Publikation benötigt der Publisher eine vollständige Gitbasis. Preflight und
Ausführung verwenden dieselbe gewählte Authquelle. `--auth env` liest
`GH_TOKEN` oder `GITHUB_TOKEN` und stoppt bei widersprüchlichen Werten.
Die gleichnamigen expliziten `--auth`-Werte wählen bei Bedarf genau eine
Variable. `--auth gh` verwendet gezielt die aktive Anmeldung für
`github.com`. Ein fehlender gewählter Zugang stoppt. REST, Git-HTTPS und
der gebundene Originalabruf verwenden den ausgewählten Token. Der lesende
Windows-Assistent schützt den Token weiterhin vor Weitergabe an seine Kinder.

Für eine bestehende eigene Releasegeneration liest der Publisher die konkrete
Release-ID frisch zurück und bindet sie an Job, Tag und Anchor. `immutable:false`
erlaubt deren Fortschreibung auch bei fehlendem Administration-Leserecht oder
aktiviertem Setting für neue Releases. Unveränderliche, unklare oder fremde
Generationen und eine fehlende bereits gebundene Generation stoppen den Ablauf.
Ein neues Release erfordert eindeutig deaktivierte Unveränderlichkeit. Bei
einem Settings-404 bestätigt derselbe Token den Zugriff über den lesenden
[Actions-Settings-Endpunkt](https://docs.github.com/en/rest/actions/permissions#get-github-actions-permissions-for-a-repository)
mit Administration(read) für genau dieses Repository. 401, 403,
ein uneindeutiges 404 und ungültige Antworten lassen die Neuanlage offen.
[GitHub-Settings-Vertrag](https://docs.github.com/en/rest/repos/repos#check-if-immutable-releases-are-enabled-for-a-repository)

Release- und Refbindungen werden vor der tatsächlichen Publikation erneut geprüft.
Die Schreiboperation und ihr Readback entscheiden über den Erfolg. Der Publisher
prüft beide Generationen im Katalogbudget der installierten Appclients.
Die kurzlebige Ref work-prod-control/catalog
serialisiert Arbeitsänderungen und signierte PW-/PE-/PG-Veröffentlichungen. Jeder
Arbeitswriter reserviert zusätzlich drei Releases mit je sieben Assets für die
Appkanäle. Alle Writer prüfen Seitenzahl, Metadatenumfang
und Abrufdauer innerhalb der Lease. Ein Appwriter prüft den vollständigen Draft
erneut vor der Sichtbarschaltung. Nach Abbruch eines Arbeitswriters dieselbe
Operation im selben Checkout wiederholen. Ein Appwriter wartet bis zu fünf
Minuten auf die Lease. Bei hart beendetem Actions-Runner den beendeten Lauf und
seinen Maincommit vor einer manuellen bedingten Freigabe der Lease abgleichen.
Einen aktiven oder unklaren Besitzer niemals überschreiben.

Ein Job besitzt den Prerelease work-prod-<id> mit make_latest=false und einem
Tag am bereinigten Maincommit. Neue Originale werden einzeln hochgeladen und
über Release-/Asset-ID, Namensbindung, Größe und Hash zurückgelesen. Der Arbeitsref
enthält ausschließlich Record und Indexdelta. Die erwartete Remote-SHA bindet die Veröffentlichung.
Erst danach entfallen ersetzte Originale. Aktive Auswahlen haben keine
technische Siebentagesfrist. Rollout und Produktionsfreigabe setzen einen
tatsächlich verfügbaren v2-Reader und bestätigten Originalzugriff voraus.

Die im abgesendeten Auftrag erklärte und an den aktuellen Record gebundene
Kandidatenwahl deckt die anschließende automatische Bereinigung der nicht mehr
referenzierten, eindeutig eigenen Arbeitsrelease-Assets bereits ab. Nach
bestätigter Record-/Ref-Veröffentlichung führt `work_publish publish` diesen
begrenzten Assetabgleich ohne weitere menschliche Löschfreigabe durch. Eigene,
noch referenzierte, gewählte oder fremde Assets dürfen dadurch nicht entfallen;
Asset-/Releaseidentität, Eigentum, SHA-Bindung, Konfliktschutz und Readback
bleiben verbindlich. Bei API-, Rechte- oder Plattformblockade den gesicherten
Arbeitscommit und die noch zu entfernenden eigenen Asset-IDs als technischen
Rest melden und den identischen Publisher-/Wiederaufnahmepfad benutzen. Weder
erneute Kandidatenwahl noch zweite Zustimmung zur normalen Bereinigung
einfordern; technische Sicherheitsgrenzen nicht umgehen. Diese Auswahl ist
keine Freigabe zum Löschen eines ganzen Arbeitsreleases/Produktionsbranches,
zur abschließenden `retire`-Operation oder zum Merge.

## Veröffentlichung und Ansichten

Der Windows-Assistent kann die öffentliche REST-Abfrage der Originalmetadaten
mit seiner [Windows-Benutzervariable](PRODUCTION_WORKSPACE.md#optionaler-rest-zugang-unter-windows)
authentifizieren. Sein öffentlicher Originaldownload bleibt anonym. Im Publisher
verwendet der Originalabruf den ausgewählten REST-Kontext und eine gegebenenfalls
von GitHub gelieferte signierte Download-URL. Release- und Asset-ID, Name, Größe
und SHA-256 bleiben verbindlich. Der [Remote-Einstieg](PW_REMOTE.md) bindet den vollständigen Record und dieselben Reader an den Auftrag. Ein vollständiger Remote-Abschluss aus ChatGPT
mit Produkt-PR und CI ist ein gesonderter Betriebsnachweis.

Ein frischer Chat kann die ausgewählten Originale dieses Records, HG31-Ableitung und Rasteransichten über den [gebundenen Actions-Abruf](PW_REMOTE.md#originale-in-chatgpt-sichten) öffnen.

Der gemeinsame Index enthält nur `puzzle_id,revision,record`-Verweise nach
Index v1. Aktuelle Records verwenden revision=current. Keine workspace.json
oder current-view.json pro aktuellem Job: Liste, Bilder, Angebote und Folgeauftrag
werden direkt aus dem Record abgeleitet und gegen denselben fixierten Gitstand
geprüft. Der lesende Dienst bleibt ohne fachlichen Writer. Arbeitsref
`content/pw/<id>` sichert die aktuelle Auswahl; unerreichbare Quellen bleiben Fehler.
Öffnen/Kopieren ist keine Entscheidung. Bestehende UI und sichere Remoteauswahl
bleiben erhalten. Auswahlkennungen und Inhaltsbindungen verhindern Verwechslung.

## Übergabe und Abschluss

Die ausgewählten finalen Daten werden über denselben aktuellen RI-ONE-Eingang
nach [ZA-1](../production/ZA1_ADAPTER.md) exportiert. Integration erfolgt in einem
sauberen Branch vom aktuellen Main. Nur gewählte finale Produktdaten und wirklich
benötigte aktive Metadaten übernehmen; niemals den Arbeitsbranch mit Alternativen
und Protokollen nach Main mergen. Completion und jeder registered-Readback vergleichen die tatsächliche Lieferung einschließlich aktueller Reveal-/Hintergrundnotices und vollständiger ausgewählter Bewertung,
auch wenn der Integrationscommit keine Arbeitsdateien enthält. Retirement prüft
bestätigtes Mainergebnis und eigene ausgewählte aktuelle Arbeitsbytes am Arbeitsref;
die Arbeitsdateien müssen nie zuvor in Main gelegen haben. Nach bestätigtem
Mainergebnis führt der Akteur `retire` direkt mit dem erwarteten veröffentlichten
Arbeitscommit aus. Der Publisher liest das Fehlen des eigenen Arbeitsrefs,
des gebundenen Releases und des Tags zurück. Ein abgebrochener Abschluss
verwendet im selben Checkout denselben Arbeitscommit. Geänderte Generationen
und unklare Zuordnungen stoppen die Bereinigung.

Die aktive PW-Liste blendet jede im gültigen gebundenen Mainkatalog registrierte
ID vor der Prüfung ihrer Arbeitsdaten aus
([PW2-C](PRODUCTION_WORKSPACE.md#pw2-c--aktive-produktionen-und-fachlicher-abschluss)).
Auch höhere Revisionen, frühere Phasen und `operation=background` bleiben
ausgeblendet. Der Listenfilter erteilt keine Befugnis zu Schreiboperationen.

## Historische Formen

Die früheren geschlossenen Paket-/Snapshot-/Projektionsformen sind am
[Mainanker vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/docs/tools/PW_B_CONTRACT.md)
dokumentiert. Ihre Erkennung erlaubt keine neue normale Archivproduktion und
verlangt keine WIP-Migration. Die aktuelle Form ist keine Umbenennung alter Originale.

## Palettenausnahme

Aktuelle Urteile und konkrete technische Ausnahmen stehen direkt am aktuellen
Raster. Die geschlossene Ausnahmeform entspricht dem RI-ONE-Eingang nach ZA-1;
negative Befunde bleiben negativ. Redaktionell ausdrücklich angenommene
Abweichungen bleiben mit result und accepted getrennt. Ungeprüft ist nie zulässig;
Q-HG01 und H-07 bleiben unabdingbar; Hintergrundabweichungen sind ausschließlich für Q-HG02–04 redaktionell annehmbar. Keine Original-ZIP-/Inventar-/Handoffbindung.

## PW-PERF-C · aktuelle Prüfung

Aktuelle Datei-/Inhaltsprüfung und gemeinsame Publikationsguards ersetzen keine
Qualität oder tatsächliche Entscheidung. Historische Ableitungsbefunde sind keine
Zulassungsbedingung für aktuelle Ergebnisse.

## PW-PERF-D · Regelquellen und Snapshotgeneration

Für aktuelle Jobs genügt der aktuelle Quellencommit. Kein neuer Regelwerksnapshot
und kein Zugriff auf frühere Erzeugerbytes. Alte Snapshotformen bleiben nur als
explizit historische Daten erkennbar; sie sind kein normaler Writerweg.

## PW-FIND · freigegebene Erweiterung der Entscheidungsdaten

Neue Aufträge verwenden lokal `picross-authoring-draft-v3` und veröffentlicht
`picross-authoring-current-v3`. Der Builderrequest und die gemessenen Dateirefs
bleiben dieselben. Der lesende Dienst leitet die Ansicht
`picross-production-presentation-v3` aus diesem Record ab. Für vorhandene
v2-Bytes gilt weiterhin die oben beschriebene Feldmenge.

Zusätzliche Pflichtfelder sind `findings` (Liste) und `instructions` (aktuelle
Kandidaten-ID → weiterhin geltende Behandlungstexte). Ein Befund enthält
`target,content,id,criterion,rule,properties,context,effect,extent,result,description,method,actor,timestamp_utc,decision`.
`target` bezeichnet eine Kandidaten-ID oder `@selection` für die gewählte
Schlusskombination. `content` ist die aktuelle semantische Identität. Ein
Kriteriensammelurteil bildet das schlechteste Einzelurteil ab. Sein
`accepted` bleibt in v3 false. `decision` ist null oder enthält
`binding,action,treatment,actor,timestamp_utc,statement,source`. Die Bindung
umfasst alle Beobachtungsfelder. Die Aktionen heißen `accept` und `revoke`.
Eine Übernahme benennt in `source` den unmittelbaren Ursprung mit `target,binding`.

`blockers` enthält ausschließlich auftragsweite Objekte mit `scope`
(source, transport oder job) und `message`. Kandidatenbefunde stehen in
`findings`. Hintergrundassets binden zusätzlich `profile` sowie `prepared`
(null bis zur Ableitung, danach `original_sha256,profile,file` mit Ergebnisref).
Technische Rasterausnahmen binden zusätzlich `definition_sha256`.
Vor der Wahl genügt ein qualifizierter Rasterkandidat für `raster_ready`.

Der [Entscheidungshelfer](../../tools/puzzle_production/finding_decisions.py)
definiert Identitäten, zugelassene Teilregeln und die geprüfte Fortschreibung.
Die Tabelle ordnet die Angaben der fachlichen Entscheidung zu.

| Information | Bindung und Bedeutung |
| --- | --- |
| Konkreter Befund | Stabile eigene Kennung, Kandidat beziehungsweise gewählte Schlusskombination und relevante Inhaltsidentität, Kriterium/Teilregel, betroffene Eigenschaften, Kontext, Wirkung und tatsächliches Urteil samt Prüfbegründung/Methode. Mehrere Befunde je Kriterium sind möglich. |
| Annahme/Widerruf | Genau dieser Befund an diesem Bezugsobjekt, tatsächliche Erklärung, Akteur und überlieferter Zeitpunkt. Keine Ableitung aus einer fremden Erklärung oder einem Kürzel im Freitext. |
| Behandlung | Eigenständiger Nutzertext; sichtbar erklärte Standardbehandlung nur bei leerer erstmaliger Annahme. Befundbegründung und Behandlung überschreiben einander nicht. |
| Fortführung | Unmittelbare Korrekturgrundlage, gültige frühere Entscheidung und nachvollziehbare Deckung des neuen Befunds. Kompakte aktuelle Herkunft statt vollständigem Kandidaten-/Entscheidungsarchiv. |
| Bereitschaft | Aus aktuellen Voraussetzungen, Befunden und zulässigen wirksamen Annahmen je Kandidat abgeleitet; kein vom Erzeuger gesetzter pauschaler Bypass. |

Die fachliche Deckung, Gleichheitsgrenzen und Widerrufswirkung definiert allein
[Qualität §6.1](../production/PUZZLE_QUALITY.md#61-pw-find--befundentscheidungen-in-allen-phasen).
Die Kandidatenbindung darf nicht durch eine unabhängige Änderung der übrigen
Angebotsmenge entwertet werden. Materielle Änderungen invalidieren weiterhin die
betroffenen kreativen Wahlen und technischen Nachweise. Eine fortgeführte Annahme
ist keine automatische Auswahl des Nachfolgers.

Prüfer, Projektion und Promptgenerator unterstützen gemischte Kandidatenstände.
Die Detailprojektion prüft die Bereitschaft je Kandidat. Sie zeigt qualifizierte
Raster als Rasterangebote und harte Sperren als Sichtungsentwürfe. Zum negativen
H-01-Randbefund gehören die aus der Endmatrix gemessene Belegung aller Kanten,
die betroffene Achse, Kandidat, Endrevision und Definitionshash. Neue technische
`frame`-Ausnahmen enthalten zusätzlich `candidate_id,revision` am bisherigen
`definition_sha256` und dem eigenen Erklärungsbeleg. Bestandseinträge im
bisherigen Format bleiben in ihren ursprünglichen Bindungen lesbar. Der
Reader und der [Integrationseingang](../production/ZA1_ADAPTER.md)
prüfen die technische Ausnahme. Der negative Randbefund bleibt auch mit
gültigem Ausnahmebeleg sichtbar.

Ein v3-Raster kann optional `crop_diagnosis` mit dem Format
`picross-raster-crop-diagnosis-v1` enthalten. Die geschlossene Bindung enthält
`before,preview,protection,rectangle,parameters_sha256`. Die drei Refs messen
die ursprüngliche Definition, ihre echte PNG-Vorschau und die Schutzdatei.
Letztere enthält `before_sha256,motif_sha256,cells` mit einer vollständigen
booleschen Zellmatrix. Bei genehmigten geschützten Merkmalen bindet die
tatsächliche Motiventscheidung die Schutzdatei in `crop_protection` als
Zuordnung vom Hash der Vorher-Definition zum Hash der Schutzdatei. Eine
vorhandene Zuordnung muss passen. Das Rechteck enthält Zellkoordinaten
`[links,oben,rechts,unten]` mit exklusivem rechten und unteren Ende. Der
geprüfte Ausschnitt erhält alle Zellen, Farbbedeutungen und die Revealbindung
innerhalb des Rechtecks. Die erlaubten Seiten und die freigegebene vollständige
Parameteralternative gelten auch für die Diagnose.

Die Detailprojektion zeigt die gebundenen Originale vor und nach dem Beschnitt,
die tatsächlichen Maße, die entfernten Seiten und Zellzahlen und den konkreten
Vorschlag zur Änderung der ungefähren Untergrenze. Andere Parameterwerte bleiben
gültig. Fehlende oder abweichende Originale sperren diesen Entwurf. Nach
ausdrücklicher Neufreigabe müssen der Cropbezug und die Motiventscheidung auf
die genehmigte Alternative zeigen. Der finale Reader verlangt aktuelle
Hinweise, vollständige unabhängige Deduktion mit Endmatrixvergleich,
Difficulty und alle übrigen Pflichtprüfungen. Die Vorschlagsalternative
ändert keine Auswahl oder Phase. Die Originale liegen im einen aktuellen
Record und folgen dessen Verdichtung. Das optionale Feld wird bestehenden
v2-/v3-Records nicht automatisch hinzugefügt.

Der globale Phasenstatus beschreibt den tatsächlichen Fortschritt
und ersetzt keine Prüfung des ausgewählten Kandidaten. Auch ein blockierter
Entwurf kann als Korrekturgrundlage adressiert werden; das setzt selected nicht
auf eine unqualifizierte kreative Wahl. Nach tatsächlicher Wahl gelten die
bisherigen Regeln zur Verdichtung und Entfernung nicht mehr benötigter Varianten.

Ein abgesendeter Auftrag darf Annahme/Behandlung, Wahl und Folgeaktion zusammen
erklären. Builder und Finalizer prüfen und binden die gültige Kombination ohne
zusätzliche menschliche Annahmerunde. Bei fehlenden Voraussetzungen keine halb
gültige Auswahl oder Phasenfortschaltung publizieren. Bereits gültig erklärte
Annahmen können im tatsächlichen Reviewstand gesichert bleiben; ein anderer
Blocker verlangt keine erneute Erklärung derselben unveränderten Annahme.
Erwarteter Record, sichere Publikation, Wiederholung und Readback bleiben wirksam.

Alle noch relevanten Vorgaben müssen auch nach Verdichtung und am Übergang zum
[Integrationseingang](../production/ZA1_ADAPTER.md#pw-find--entscheidungen-bis-zur-integration)
verfügbar bleiben. Ein alter globaler Blockertext darf einen angenommenen Befund
nicht erneut sperren. Der lesende Dienst führt keinen Solver und keinen neuen
fachlichen Writer aus. Kein zweiter Browserbestand, Promptarchiv, Regelbuchsnapshot
oder historischer Vererbungsbaum; Retirement und benötigte Produktnachweise bleiben.

## Katalogprofile für Abschlussbilder

Integrationseingang v1 und Authoringrecord v2 führen das gewählte Original. Die automatische Ableitung gehört zur Erstintegration. Completion vergleicht die aktuelle Revealquelle und beide tatsächlichen Profilbytes gegen den Integrationscommit.
