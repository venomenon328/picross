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
Der Akteur führt vom eigenen Checkout aus folgende Befehle aus:

```text
python -m tools.work_publish publish <id> --expected new
python -m tools.work_publish resume <id> --expected <arbeitscommit>
python -m tools.work_publish publish <id> --expected <arbeitscommit>
python -m tools.work_publish retire <id> --expected <erwarteter-Arbeitscommit>
```

Resume arbeitet auf einem eigenen Worktree am erwarteten Commit. Der Publisher
benötigt angemeldetes gh mit Repository-Schreibrecht und vollständige Gitbasis.
Er prüft Rechte, Release-Mutierbarkeit und beide Generationen im Katalogbudget
der installierten Appclients. Die kurzlebige Ref work-prod-control/catalog
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
über den öffentlichen Leser geprüft. Der Arbeitsref enthält ausschließlich
Record und Indexdelta. Die erwartete Remote-SHA bindet die Veröffentlichung.
Erst danach entfallen ersetzte Originale. Aktive Auswahlen haben keine
technische Siebentagesfrist. Rollout und Produktionsfreigabe setzen einen
tatsächlich verfügbaren v2-Reader und bestätigten Originalzugriff voraus.

## Veröffentlichung und Ansichten

Der Windows-Assistent kann die öffentliche REST-Abfrage der Originalmetadaten
mit seiner [Windows-Benutzervariable](PRODUCTION_WORKSPACE.md#optionaler-rest-zugang-unter-windows)
authentifizieren. Die Downloadanfrage bleibt anonym. Release- und Asset-ID,
Name, Größe und SHA-256 bleiben verbindlich.

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
Ein qualifizierter Kandidat ist unabhängig von offenen Vergleichskandidaten
auswählbar. Für Rand- und Maßabweichungen gelten die Diagnose- und
Entscheidungspfade aus [Schritt 3 §§4.4–4.6](../production/authoring/PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen).
Das diagnostische Vorlegen eines Zuschnitts unter den freigegebenen Korridor
ändert die Parameterbindung des qualifizierten Angebots nicht. Die bereits
gebundene technische `frame`-Ausnahme bleibt der Weg für eine ausdrücklich
angenommene Randverletzung. Die Soll-Sichtung eines konkreten H-01-Randbefunds
samt getrenntem Ausnahmebeleg und die Sichtung eines Korridorentwurfs mit
Vorher-/Nachheransichten und Änderungsvorschlag sind durch die allgemeine
Unterstützung gemischter Kandidatenstände in Reader, Projektion und Bedienung
noch nicht vollständig abgedeckt. Bis dahin gilt die Sichtung im bestehenden
Bericht nach Schritt 3.

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
