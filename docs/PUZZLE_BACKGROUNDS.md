# Rätselbezogene Hintergrundzeichnungen

**Vertrag 1.0 · Dokumentrevision 12 · 11.11.2026 · HP-W1/HP-W2 / #560; PB-H / #489; HP-I1a/HP-I1b1/HP-I1b2/HP-I1c/HP-I2 / #561; MJ-A/MJ-B / #490; BA-A/BA-B / #491**

## 1. Geltung und tatsächlicher Unterstützungsstand

Dieser Vertrag schließt den noch **nicht als Default aktivierten** Produktionsweg aus
[#560](https://github.com/venomenon328/picross/issues/560) und dem
[Paket HP-W1](https://github.com/venomenon328/picross/issues/560#issuecomment-6747196307).
Maßgeblich sind die [Eigentümerkorrektur zur isolierten Auswahl](https://github.com/venomenon328/picross/issues/560#issuecomment-6744957790)
und [#558 / D01](https://github.com/venomenon328/picross/issues/558#issuecomment-6744063800).
Die Evaluierung wird nicht übernommen; PR #559 bleibt geschlossen und ungemergt.
Der integrierte RAND-P1 ist ein Konzeptpilot. Die Werkzeugpakete ersetzen weder
dessen Kategoriezeichnungen noch die Runtimepfade. HP-I2 ergänzt den regulären
Runtimevertrag nach §13; der Kategoriepilot bleibt für Legacy erhalten.

Geprüfte Vertragsbasis für HP-I1a: `main@b994ce432fa0c436223f3eee8bb50b0f867a94ec`.
**Aktiv bleibt Authoring 0.6.0**, mit der jeweils tatsächlich gebundenen
Dokumentrevision und dem dazugehörigen Snapshot. Auf den Dokumentvertrag HP-W1
folgt die eigenständig nutzbare Teilfähigkeit
[HP-W2](https://github.com/venomenon328/picross/issues/560#issuecomment-6748799473):
Arbeitsmanifest, Entscheidung, Ableitungsauftrag und Befund nach §§3–4 sowie
`describe`, `derive` und lesendes `verify` sind unterstützt.
[PB-H](https://github.com/venomenon328/picross/issues/489#issuecomment-6751071312),
auf Basis `main@c0264ca84b99647bbe79460b16c57962c3130d33`, ergänzt den
deterministischen Paketbau und die lesende Inhaltsprüfung mit dem vollständigen
[0.7.0-Vorschausnapshot](ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md):
Bauauftrag v2, Handoff v3, Record v2, Bauresultat v2 und Sheet-Update v3.
[HP-I1a](https://github.com/venomenon328/picross/issues/561#issuecomment-6752672149)
ergänzt die sichere äußere Fortschreibung bereits vorhandener Entscheidungen,
Ableitungen und Endfreigaben (§7.4) sowie den vollständig prüfbaren Export v6
nach [ZA-1](ZA1_ADAPTER.md#hp-i1a--äußere-endabnahme-und-export-v6).
HP-I1b1 ergänzt auf Basis `main@045189cc5ef34eaf4d06823f22f7ec811d209de5`
die erste Registrierung, kompakte aktive Quelle, gemeinsame Transaktionen und
den ersten Produktionsabschluss nach §10. HP-I1b2 ergänzt den eigenständigen
Hintergrundwechsel und revisionsgenauen Abschluss nach §11; HP-I1c ergänzt
die aktuelle Raster-/Revealneubindung nach §12. Diese Werkzeugpakete sind auf
der HP-I2-Basis `main@964cfe2422a45871961760e65dcd863fe68ee5e0` integriert.
Der vollständige verpflichtende Produktionsweg bleibt **inaktiv**. Die echte
Zielfähigkeit darf erst HP-I2 mit tatsächlicher Runtime und technischer Abnahme
nach §13 liefern; deren Stand gehört in den konkreten PR. Eine aktivierte
Runtime-Capability stellt den Authoringdefault nicht automatisch auf 0.7.0 um.
MJ-A aus #490 führt den regulären Mehrjob-Arbeitsbereich nach §7.5; die eigene
spätere Hintergrundrevision folgt MJ-B nach Hintergrundvertrag §7.6. Synthetische kompatible Zielcheckouts prüfen
den Werkzeugweg, keine Bildproduktion oder persönliche Bildabnahme.

[BA-A](PRODUCTION_BATCH.md) verarbeitet ausdrücklich vorbereitete lokale Jobs
seriell und verwendet dabei die unveränderten HP-W2-Aufträge, Entscheidungen und
Prüfungen. Offene Bildwahl blockiert nur ihre abhängigen Stufen; eine reine
Hintergrundänderung erhält unveränderte Logik-/Difficultyartefakte. Technischer
Laufabschluss erteilt keine Bild-/Inhaltsfreigabe. Der Runner endet spätestens
am lokalen PB-A-/PB-H-Paketbau; Finalizer, Spielerexport, gemeinsame Writer und
Retirement sind nicht enthalten. Der eigene [BA-B-Integrationsrunner](PRODUCTION_BATCH.md)
führt dagegen ausdrücklich autorisierte, vollständig vorbereitete Einzeljobs
seriell aus. Neue Rätsel verwenden den bestehenden Export-/Plan-/Registerweg;
reine spätere Bildrevisionen den unveränderten Request nach §11.1 und
`store → plan → adopt`. Keine neue Finalisierung, Bildwahl oder Pflichtabnahme.
Default, Sheetbedienung und §§2–7 bleiben erhalten.

[Authoring](ai-workflows/PUZZLE_AUTHORING.md) bleibt für vier Aufträge,
vorhandene Bild-/Motiv-/Rasterfreigaben und Abschluss zuständig,
[Qualität §9](PUZZLE_QUALITY.md)
für die einzelnen Hintergrundurteile. Die genaue Einführung steht in §8.
Die eigenständigen Arbeitsformen dürfen mit HP-W2 vorbereitet, abgeleitet und
geprüft werden; die Verpflichtung zum vollständigen neuen
Produktionsweg beginnt erst mit einem funktionierenden kompatiblen Einzelweg.

### Bild- und Produktgrenze

Der Hintergrund ist eine eigene Kontextzeichnung. Er zeigt weder das konkrete
Rätselsubjekt noch dessen Lösungssilhouette, Rasterkopie oder Motivnamen und
verwendet keine Informationen aus dem Spielerfortschritt. Ein indirekter
Kontexthinweis ist möglich; universelle Spoilerfreiheit wird nicht behauptet.
Abschlussbild, Motivvorlage, Lösungsraster und Hintergrund bleiben getrennte
Dateien, Revisionen und Freigabegegenstände.

Standard sind echte ImageGen-Zeichnungen mit hellen neutralgrauen Graphitstrichen,
offenen beziehungsweise nachgezogenen Konturen und sparsamer Schraffur. Papier
muss auch zwischen den Strichen durchscheinen. Eingebrannte Buchflächen, UI,
weiße Bildkästen, Schrift und Wasserzeichen sind ausgeschlossen. Gemeinsame
transparente 4:1-Leinwand; durchgehende luftige Kompositionen sind ebenso möglich
wie niedrigere Mitte, U- oder Halb-U-Form. Keine Pflicht zu zwei Ecken und keine
individuellen Positions-, Crop- oder Maskenparameter.

Die HP-I2-Runtime nach [#561](https://github.com/venomenon328/picross/issues/561)
verwendet zunächst Variante A, dieselbe Grunddarstellung hinter Raster und
Hinweisen, gemeinsamen Fit/Anker und den unteren sichtbaren Seitenbereich.
Funktionslayout und Trefferflächen werden nicht verkleinert. Kein lokales
Abblassen, keine Unschärfe, kein deckender Rasteruntergrund und keine globale
Zoom-Ausblendung. B1/C sind verworfen; B2 ist keine jetzt einzuführende Option.
Verlustfreier Engineimport, Mipmaps und Bedarfsladen gehören zu HP-I2; ein lokales
PNG-Ergebnis belegt nichts davon und keinen bedarfsgesteuerten Netzwerkdownload.

## 2. Vier Aufträge und versionierte Bereitschaft

| Bestehender Auftrag | Hintergrundarbeit und nächster erlaubter Schritt |
| --- | --- |
| 1 · Abschlussbildauswahl | Bei feststehender Motivrichtung Kontext, geschützte Merkmale und Ausschlüsse aufnehmen. Die Abschlussbildauswahl bleibt erhalten; keine Reveal×Hintergrund-Kreuzmatrix. |
| 2 · Abschlussbildfreigabe und Abstraktion | Erst nach tatsächlicher Abschlussbildfreigabe drei inhaltlich unterschiedliche Kontextzeichnungen erzeugen, speichern und gemeinsam mit der Motivvorlage als drei isolierte Einzelbilder vorlegen. Ein endgültiges Raster ist nicht nötig. |
| 3 · Motivfreigabe und Produktion | Hintergrundwahl möglichst mit der Motivfreigabe im selben Eigentümerauftrag erklären. Die konkrete Bildrevision über Rastervarianten hinweg erhalten. Ohne Hintergrundwahl bereits autorisierte unabhängige Rasterarbeit fortsetzen und sichern; keine Auswahl oder Leerentscheidung erfinden. |
| 4 · Endabnahme und Integration | Noch offene Wahl darf mit der gewöhnlichen Endabnahme gebündelt werden. Nur das gewählte, gültig abgeleitete Bild oder ausdrücklich `none` zusammen mit dem endabgenommenen Rätsel übernehmen. Eine eindeutige frühere Wahl derselben unveränderten Datei nicht erneut bestätigen lassen. |

Nur eine ausdrückliche Eigentümervorgabe ändert die anfängliche Dreierzahl.
Eine bewusst frühe Entscheidung „für dieses Rätsel keinen Hintergrund erzeugen“
ist eine solche Vorgabe und wird tatsächlich belegt. Fehlende Bildfunktion,
Dateien, Zeit oder Entscheidung sind keine solche Ausnahme. Nach Korrektur wird
die tatsächlich geänderte Fassung erneut isoliert vorgelegt, nicht routinemäßig
ein neuer Dreiersatz. Keine Kandidaten-Testintegration, Buchvorschau, persönliche
Buchabnahme oder zusätzliche Standarddialogphase.

### Phasen für Authoring 0.7.0 / Handoff v3

Die folgende Semantik gilt für den ausdrücklich gewählten 0.7.0-Vorschaustand.
PB-H baut die Phasen bis einschließlich `content_ready`; ein neues Original
mit finalem Abnahme-/Exportzustand wird nicht gebaut. HP-I1a darf den äußeren
Record nach frischer Prüfung bis `editorially_approved` fortschreiben und v6
exportieren. `catalog_ready`, `registered` und `integration_ready` bleiben false;
eine Phase „exportiert“ wird nicht eingeführt. Die heutige 0.6.0-Bedeutung von
`content_ready`, ihre Inhaltsgates und die ZA-1-Prüfung auf dem geschriebenen ZIP
bleiben unverändert.

| Phase | Erforderlicher Befund / zulässige offene Entscheidung |
| --- | --- |
| `brief_ready`, `reveal_review` | Hintergrund-Arbeitsmanifest vorhanden; Kontext darf noch offen sein. Keine behauptete Bildwahl. |
| `motif_review` | Tatsächlich freigegebenes Reveal, Motivvorlage und drei gesicherte isolierte Hintergrundangebote; abweichende Zahl oder frühes `none` nur mit Eigentümerbeleg. |
| `motif_approved`, `raster_review` | Bestehende Motiv-/Parameterfreigabe erlaubt Rasterarbeit. Hintergrund darf noch `offered`, `rejected` oder in Korrektur `pending` sein. |
| **`raster_ready`** | Sämtliche bisherigen 0.6.0-Inhaltsvoraussetzungen einschließlich Palette, Herkunft, Proof und Difficulty erfüllt; nur Hintergrundbereitschaft und Endabnahme dürfen fehlen. Das ist eine technisch vollständige Rasterauswahlvorlage, keine Integrationsbereitschaft. |
| `content_ready` | Zusätzlich gültige Hintergrundwahl, Rechte/Sichturteile und HP-W2-Ableitung oder gültiges ausdrückliches `none`. Nur tatsächliche finale Endabnahme/Integrationsauftrag dürfen offen sein. |
| `editorially_approved` | Alle Inhaltsvoraussetzungen plus tatsächlich gebundene Endabnahme nach §5. Noch keine ausgeführte Integration. |
| `catalog_ready`, `registered` | Bisherige Kategorie-/Export-/Registrierungsvoraussetzungen plus unterstützte Hintergrundverbraucher. `registered` bezeichnet den geprüften Checkout; erst bestätigter Merge bedeutet Integration auf main. |

`blocked`, `rejected`, `superseded` behalten Grund und betroffene Revision. Ein
zurückgewiesener Hintergrund macht einen unveränderten gültigen Rasterproof
nicht falsch. Die Hintergrundzustände werden separat geführt (§3.4).

Handoff v3 ergänzt die bisherigen zehn Gates ausschließlich um
`background_choice` und `background_asset`, jeweils `pending|pass|fail|blocked`.
`background_choice=pass` benötigt eine tatsächliche gültige Auswahl oder `none`;
`background_asset=pass` benötigt die passende Ableitung, geklärte Nutzungsgrundlage
und die fälligen isolierten Qualitätsurteile. Bei `none` belegen Entscheidung
und HP-W2-Nullbefund den Entfall des Assets. Ein einzelnes `pass` ersetzt keine
Datei, Rechteangabe oder Erklärung. Noch nicht fällige Arbeit bleibt `pending`;
ein konkreter Zugriffs-/Formatfehler ist `blocked`, ein bestätigter Mangel `fail`.

## 3. Geschlossene Arbeits- und Entscheidungsdaten

### 3.1 Gemeinsame Typen, Pfade und Hashes

Alle neuen Formen sind UTF-8-JSON ohne BOM, doppelte Schlüssel, NaN/Infinity oder
stille Typumwandlung. **Alle aufgeführten Schlüssel sind Pflicht, zusätzliche
Schlüssel sind Fehler**, auch in Unterobjekten; `null` ist nur an ausdrücklich
genannten Stellen zulässig. Boolean ist kein Integer. Listen sind geordnet,
sofern keine Sortierung genannt wird. Leere Listen ersetzen keine Entscheidung.

| Typ | Exakte Bedeutung |
| --- | --- |
| `Text` | Nichtleere Zeichenkette, höchstens 4096 Unicode-Zeichen; keine NUL-Zeichen. Reine Leerzeichen sind ungültig. |
| `ID` | `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`; innerhalb des betreffenden Jobs eindeutig. |
| `PuzzleID` | Bestehendes `pz-[a-z0-9][a-z0-9-]{0,59}`. |
| `Revision` | Bestehendes `[A-Za-z0-9][A-Za-z0-9._-]{0,31}`; Hintergrund-, Entscheidungs- und Paketrevision sind verschiedene Kennungen. |
| `SHA` / `Commit` | Genau 64 beziehungsweise 40 kleine Hexzeichen. `SHA` bindet tatsächliche Dateibytes, außer ausdrücklich `H(x)` genannt. |
| `UTC` | Tatsächlicher ISO-8601-Zeitpunkt in UTC, `Z` oder Offset `+00:00`, höchstens 64 Zeichen. Keine erfundene Entscheidungszeit. |
| `Path` | Relativer POSIX-Dateipfad, 1–240 Zeichen, nach `authoring_package.relative`: keine absoluten Pfade, Backslashes, Doppelpunkte, leeren/Punkt-/Elternsegmente, Steuerzeichen, Windows-Gerätenamen oder abschließenden Punkte/Leerzeichen je Segment. |
| `Ref` | Exakt `{file: Path, sha256: SHA, bytes: Integer >= 0}`. Datei muss innerhalb ihres ausdrücklich benannten Wurzelverzeichnisses liegen. |
| `Root` | `.` für die ausdrücklich gewählte Wurzel selbst oder ein sicherer relativer `Path` auf ein Verzeichnis. Diese einzige Punkt-Ausnahme gilt nicht für Dateipfade. |
| `StoredRef` | Exakt `{storage:"package"\|"external",root:Root,ref:Ref}`. `package` bezieht `root` auf das sicher geöffnete Original-ZIP, `external` auf den ausdrücklich übergebenen äußeren Transportroot. Erst `root`, dann `ref.file` auflösen. |
| `Human` | Exakt `{actor: Text, timestamp_utc: UTC, statement: Text, evidence: Ref}`. Beleg enthält die tatsächlich erfolgte Erklärung, keine durch das Werkzeug erteilte Freigabe. |
| `PackageBinding` | Exakt `{puzzle_id: PuzzleID, revision: Revision, original_zip_sha256: SHA, handoff_sha256: SHA, inventory_sha256: SHA}`. Alle Werte stammen aus demselben unveränderten Originalpaket. |
| `History` | `null` oder exakt `{commit:Commit,storage:"directory"\|"package",path:Path,root:Root}`: genauer früherer Repositoryordner beziehungsweise ZIP-Pfad, danach dessen innere Arbeitswurzel. Kein Branchname und kein implizites „neuester Stand“. |

`C(x)` sind bestehende kanonische JSON-UTF-8-Bytes mit sortierten Schlüsseln,
`ensure_ascii=False`, `separators=(',', ':')`, `allow_nan=False`, ohne LF.
`H(x)=SHA256(C(x))`; geschriebene neue JSON-Dateien enthalten `C(x)` plus LF.
Zeitmessungen/absolute Maschinenpfade gehören nicht in Inhaltsidentitäten.

Manifestinterne Pfade sind ausschließlich relativ zur Arbeitswurzel, **ohne**
deren Präfix zu wiederholen. Im Standalone-Aufruf ist dies `source_root`; im
Transport die durch `BackgroundBinding.manifest` ausdrücklich bestimmte Wurzel.
Beispiel: `root="background"`, `ref.file="work/bg01.json"` und ein Original
`file="original/B-b01.png"` ergeben die ZIP-Member
`background/work/bg01.json` und `background/original/B-b01.png`.
Im äußeren Record ist der äußere Transportroot der Repositoryroot, beim lokalen
Dateitransport ein ausdrücklich übergebener Root. Für `storage=package` bindet
`record.package` das ZIP; bei finaler Freigabe wird das Original-ZIP ausdrücklich
mitgeliefert und gegen `original_zip_sha256` geprüft. Der Handoff erlaubt nur
`storage=package`; seine inneren Referenzen zeigen niemals auf spätere Sidecars.

Innerhalb eines Jobs erhalten neue Datei-/Bildrevisionen kollisionsfreie
unveränderliche Pfade, etwa `work/bg01.json`, `original/B-b01.png` und
`decisions/d01.json`. Keine neuen Bytes am alten relativen Pfad. Entscheidung
und Befund führen ihre `manifest`-/`source`-/`original`-Refs als unveränderte
Identitätsbezüge zur Arbeitswurzel, nicht relativ zu ihrem JSON-Elternordner.
Ihre Identität wird mit der separat ausdrücklich lokalisierten Manifestdatei
und Kandidatenzeile verglichen. Eigene Entscheidungsbelege und
`previous_decision`/`carried_from` liegen unter der für diese Entscheidung
gebundenen Wurzel; benötigte Vorgängermanifeste liegen unter der Arbeitswurzel.
Der Befund bindet seine Entscheidungsdatei über deren unveränderten `Ref`;
seine Ausgabe liegt allein relativ zum Elternordner der Befunddatei.

Für eine erneute HP-W2-Prüfung dürfen Verbraucher aus diesen expliziten Orten
einen eigenen temporären `source_root` mit denselben relativen Pfaden und
identischen Bytes bilden. Kein Eintrag wird umbenannt oder innerer Hash
umgeschrieben. Überlappende Referenzen müssen byteidentisch sein; widersprüchliche
Belegung ist Fehler. Nur äußere `StoredRef.root`/`storage` dürfen beim Transport
neu auf den tatsächlichen Ort weisen. Kein Reader probiert mehrere Wurzeln
oder lädt automatisch URLs, Git oder Chatinhalte.
Keine Links, Hardlinks, Junctions/Reparsepunkte, nichtregulären Dateien,
Casefold-Aliase, Datei-/Verzeichniskollisionen oder eingebetteten ZIPs.

Konkreter später Auswahlfall: Das unveränderte `original.zip` enthält
`background/work/bg01.json` und `background/original/B-b01.png`; der äußere
Transportroot enthält `sidecars/job01/decisions/d01.json` und
`sidecars/job01/evidence/choice01.txt`. Die äußere Bindung lokalisiert das
Manifest mit `storage="package", root="background"`, die Entscheidung mit
`storage="external", root="sidecars/job01"`; ihre `ref.file` bleiben
`work/bg01.json` und `decisions/d01.json`. Vor `derive`/`verify` stellt der
Aufrufer ausdrücklich einen eigenen sicheren temporären `source_root` her:
Manifest und benötigte Manifestquellen aus `background/`, Entscheidung und
deren Belege aus `sidecars/job01/`, jeweils unter unveränderten relativen
Pfaden. Er prüft jeden Ref gegen Größe/Hash, weist jede nicht byteidentische
Pfadkollision ab und verwendet keine globale Zusammenführung ganzer Verzeichnisse.
Der Request enthält dieselben beiden inneren Refs; das eingebettete Manifest
bleibt unverändert. Der neue Ausgabeordner mit `derivation.json` und gegebenenfalls
`background.png` wird als zusammengehöriges Paar transportiert. Sein äußerer
`StoredRef` nennt dessen tatsächlichen Root und Befundpfad. Diese explizite
Zuordnung liefert genau den einen Quellenroot der HP-W2-API, ohne Nebenroot,
impliziten Fallback oder Umschreiben innerer Bytes/Hashes. Finale Auswahlprüfung
und Ableitungsprüfung müssen dieselbe geprüfte Zuordnung verwenden.

### 3.2 Arbeitsmanifest `picross-background-work-v1`

Das Manifest beschreibt eine unveränderliche Vorlagenrevision, keine Wahl.
Ein neuer Inhalt erhält eine neue Revision/Datei. Es enthält keinen eigenen
Hash und keine Rückreferenz auf Inventar, Handoff, Entscheidung oder Ableitung.

| Schlüssel | Typ und Semantik |
| --- | --- |
| `format` | Exakt `picross-background-work-v1`. |
| `puzzle_id`, `job_id`, `revision` | `PuzzleID`, `ID`, Hintergrund-`Revision`. Derselbe Hintergrundjob kann mehrere Rasterpaketrevisionen versorgen. |
| `created_utc` | `UTC` der tatsächlichen Aufzeichnung. |
| `context` | Exakt `{summary: Text, protected_features: Text[], excluded_subjects: Text[], reveal: Ref\|null, reveal_approval: Ref\|null}`. Beide Revealrefs gemeinsam null oder beide vorhanden; bei vorhandenen Kandidaten muss das konkrete freigegebene Reveal gebunden sein. Arrays höchstens 64 Einträge. |
| `briefing` | `Text` für gewünschte Kontextmotive, Graphitsprache, Transparenz und gemeinsame Komposition. Keine versteckten Positionsparameter. |
| `candidate_policy` | Exakt `{count: Integer 0..20, exception: Human\|null}`. Standard `3/null`; jede andere Zahl braucht eine tatsächliche Eigentümervorgabe. `0` nur für ausdrücklichen Verzicht auf Kandidatenproduktion. |
| `presentation` | Exakt `{status: "pending"\|"offered", evidence: Ref\|null}`. `offered` verlangt den Beleg der tatsächlich erreichbaren isolierten Einzelbilder; `pending` hat null. |
| `candidates` | Liste von 0–20 Kandidaten nach untenstehender Tabelle. Bei `offered` genau `candidate_policy.count > 0`, eindeutige IDs/Originalpfade; drei reine Größenvarianten desselben Motivs erfüllen den Standard nicht. |
| `test_only` | Boolean; synthetische Beispiele/Fixtures true, reale Produktion false. |

Jeder Kandidat enthält exakt folgende Felder:

| Schlüssel | Typ und Semantik |
| --- | --- |
| `id`, `revision`, `description` | `ID`, Bild-`Revision`, `Text` zum inhaltlichen Unterschied. Die Auswahlkennung `none` ist reserviert und keine Kandidaten-ID. |
| `original` | `Ref` auf gespeicherte Originalbytes. Eine Anzeige, URL oder ein Prompt ersetzt sie nicht. |
| `provenance` | Exakt `{author: Text\|null, source: Text, usage_basis: Text\|null, rights_status: "resolved"\|"unresolved", attribution: Text\|null, evidence: Ref[]}`. `resolved` braucht tatsächliche bekannte Autor-/Nutzungsangaben und mindestens einen Beleg; Attribution null heißt ausdrücklich keine zusätzliche Attribution erforderlich. Bei ungeklärtem Attributionsbedarf bleibt `rights_status=unresolved`. |
| `generation` | Exakt `{tool: Text\|null, model: Text\|null, prompt: Ref\|null, parameters: Parameter[]\|null, seed: Text\|null, unknown: Unknown[]}`. Tatsächlich bekannte Angaben erfassen; keine erfundene Modell-/Seedangabe. |
| `review` | `null` oder exakt die vier Schlüssel `Q-HG01`, `Q-HG02`, `Q-HG03`, `Q-HG04`, jeweils ein `Judgment` nach unten. |

`Parameter` ist exakt `{name: Text, value: string|number|boolean|null}`;
Zahlen sind endlich, Parameternamen eindeutig, höchstens 64 Einträge. `Unknown`
ist exakt `{field,reason}` mit `field` aus `tool|model|prompt|parameters|seed`
und `reason` aus `not_exposed|not_recorded`. Genau die null-Felder stehen einmal
in `unknown`; bekannte leere Parameterliste ist `[]`, keine Unkenntnis.
Generierung bleibt kreative Arbeit in ChatGPT/Codex; diese Angaben versprechen
keine Wiedererzeugung des Originals und keine automatische Modell-API.

`Judgment` enthält exakt
`{result, reason, method, norm, actor, timestamp_utc, evidence}`:
`result` ist `erfüllt|Warnung|nicht erfüllt|nicht geprüft`, `reason/actor` sind
`Text`, `method: Text` nennt die tatsächlich ausgeführte isolierte Sichtmethode,
Zeitpunkt `UTC`, `evidence` eine Liste von `Ref`. `norm` ist exakt
`{file:"docs/PUZZLE_QUALITY.md",contract:"1.0",document_revision:Integer>0,
commit:Commit,sha256:SHA}` des tatsächlich gelesenen Qualitätsregelstands.
`norm.file` ist ein Repositorypfad am gebundenen `norm.commit`, kein Pfad unter
der Hintergrundarbeitswurzel. Ein tatsächlich ausgeführtes Urteil bindet
mindestens das betrachtete Original; `nicht geprüft` darf `[]` führen und nennt
die Lücke. Dessen `method` lautet ausdrücklich etwa „nicht durchgeführt“ und
behauptet keine ausgeführte Sichtung. Technische Alpha-/Dateidiagnose und diese
isolierten visuellen Urteile bleiben getrennt. Q-HG04 verlangt tatsächliche
Durchsicht zwischen Strichen; eine Alpha-Kanalzählung beweist das nicht.

### 3.3 Tatsächliche Entscheidung `picross-background-decision-v1`

Die Entscheidung wird getrennt gespeichert. Dropdownzustand, Empfehlung,
Dateiexistenz, Speichern und Import sind keine menschliche Erklärung.

| Schlüssel | Typ und Semantik |
| --- | --- |
| `format` | Exakt `picross-background-decision-v1`. |
| `puzzle_id`, `job_id`, `revision`, `background_revision` | `PuzzleID`, `ID`, Entscheidungs-`Revision`, exakt die Manifestrevision. |
| `manifest` | `Ref` auf genau das vorgelegte unveränderliche Arbeitsmanifest. |
| `outcome` | `selected\|none\|rejected`. `rejected` verwirft diese Auswahlvorlage; konkrete Korrekturwünsche stehen im Wortlaut. |
| `candidate_id`, `original` | Bei `selected` genau eine vorhandene Kandidaten-ID und deren identischer `Ref`; sonst beide null. |
| `profile` | Bei `selected` exakt `{id: "picross-background-png2304-v1", sha256: H(Profil aus §4)}`; sonst null. Die vereinbarte deterministische Ableitung ist Teil des Auswahlscope. |
| `actor`, `timestamp_utc`, `statement`, `evidence` | Dieselben vier Typen/Bedeutungen wie `Human`; tatsächliche eindeutige Erklärung zur Verwendung, zum Verzicht oder zur Ablehnung. |
| `presented_package` | `PackageBinding\|null`. Pflicht, wenn die Auswahl auf einem bereits versiegelten Paket vorgelegt wurde; null nur bei zuvor unabhängig vorgelegten Arbeitsdateien. |
| `previous_decision` | `Ref\|null` der ausdrücklich abgelösten vorherigen Entscheidung. Keine automatische Wahl nach Dateiname/Zeitstempel. |
| `carried_from` | `Ref\|null`. Nur zur nachvollziehbaren Übernahme derselben tatsächlichen Erklärung bei rein administrativ erneuertem Manifest (§6); keine neue Zustimmung. |
| `accepted_deviations` | Liste von exakt `{criterion,reason}`; Kriterium aus Q-HG02–04, `reason: Text`, eindeutig. Nur die in §3.4 bezeichneten Abweichungen der gewählten Kandidatenzeile; bei none/rejected zwingend `[]`. Die Annahme muss im tatsächlichen Wortlaut/Beleg enthalten sein; negative Urteile bleiben negativ. |
| `test_only` | Boolean, identisch zum Manifest. |

`selected` verlangt `presentation=offered`, ein tatsächlich vorgelegtes Original
und dessen gültige Revisionsbindung. Es benötigt keine zweite Bildbestätigung.
`none` verlangt ausdrücklich bewussten Verzicht für diesen Job. Ohne vorgelegten
vollständigen Kandidatensatz muss zusätzlich `candidate_policy.exception` genau
diesen Verzicht auf die anfänglichen Kandidaten belegen; die Erklärung darf
dieselbe sein. Ungeklärte Rechte, defekte Dateien oder noch offene Entscheidungen
werden niemals zu `none`. `rejected` erteilt weder Wahl noch Integrationsauftrag.
Die Software prüft Bindungen, authentifiziert jedoch keinen menschlichen Akteur.

Jeder nichtnull `previous_decision` und `carried_from` bindet eine bereits zuvor
aufgezeichnete vollständige Entscheidung desselben `puzzle_id`, `job_id` und
`test_only`. Die referenzierte Entscheidung muss im Referenzgraphen strikt
früher liegen; keine Selbstreferenz, kein Nachfolger, kein Kreis, auch nicht
über mehrere Vorgänger. Revisionsnamen werden dabei nicht lexikalisch sortiert.
`carried_from` bewahrt den ursprünglichen menschlichen Zeitpunkt, weshalb
gleiche tatsächliche UTC-Werte erlaubt sind; die beweisbare Vorgängerbindung,
nicht ein erfundener späterer Zeitstempel, bestimmt die Reihenfolge.

### 3.4 Effektiver Zustand und Referenzgraph

| Abgeleiteter Hintergrundzustand | Voraussetzung |
| --- | --- |
| `pending` | Gültiges Arbeitsmanifest, noch keine vollständige Auswahlvorlage und keine geltende Entscheidung. |
| `offered` | Gültig vorgelegte Dateien, tatsächliche Wahl offen. |
| `rejected` | Aktive explizite Ablehnung der vorgelegten Revision. |
| `selected` | Aktive gültige Auswahl genau eines Originals; Ableitung/Rechte können noch ausstehen. |
| `none` | Aktive ausdrücklich bewusste Leerentscheidung, gegebenenfalls mit belegter Kandidatenausnahme. |
| Legacy | Nur aus einem gültigen alten Vertrag ohne deklarierte Hintergrunddaten abgeleitet. Kein schreibbarer Status neuer Arbeit und keine Eigentümerwahl. |
| Fehler | Deklarierte Datei fehlt/ist defekt, Bindung widerspricht, Version unbekannt oder Daten unvollständig. Kein Legacy-/Leerfallback; betroffenen Schritt mit konkreter Ursache sperren. |

`selected` allein bedeutet noch keine Hintergrundbereitschaft. Diese entsteht
aus gültiger Wahl, zulässigen aktuellen Sichturteilen, geklärten Rechten und
erfolgreich geprüftem Ableitungsbefund; bei `none` aus Entscheidung und Nullbefund.

Für ein Bild müssen alle vier Urteile tatsächlich vorliegen. `nicht geprüft`
blockiert die Hintergrundbereitschaft. `erfüllt` ist das reguläre positive
Urteil. `Warnung` oder `nicht erfüllt` bleiben sichtbar; ausschließlich bei
redaktionellen Feinheiten wie Strichgewicht/Schraffurdichte, Luftigkeit oder
begrenzter Kantenqualität darf dieselbe Eigentümerwahl den konkret benannten
Befund ausdrücklich annehmen. Dafür ist der passende Eintrag in
`accepted_deviations` erforderlich, keine weitere Dialogphase. Q-HG01 und die
festen Grenzen bleiben unabdingbar: tatsächlicher Kontext statt Rätselsubjekt,
keine UI/Buchfläche/Schrift/Wasserzeichen, echte Transparenz zwischen Strichen,
keine deckenden Bildkästen, kein individuelles Positionieren/Croppen/Maskieren,
gültige Datei-/Profil-/Freigabebindung und geklärte Rechte. Eine redaktionelle
Annahme ersetzt diese Voraussetzungen nicht und macht einen technischen Fehler
nicht erfolgreich. Bildwahl darf schon vor ihrer technischen Auflösung
aufgezeichnet werden; `selected` allein ist gerade keine Bereitschaft.

Hashrichtung: Originale/Belegdateien → Arbeitsmanifest → Entscheidung →
Ableitungsbefund; Auslieferungs-PNG → Ableitungsbefund. Inventar bindet enthaltene
Dateien, Handoff bindet Inventar, ZIP enthält beide. Die äußere Endabnahme bindet
Original-ZIP/Handoff/Inventar und die konkrete Entscheidung/Ableitung. Pfeile
bezeichnen hier „wird vom rechten Objekt gebunden“, nicht Schreibreihenfolge.
Kein Objekt hasht sich selbst. Entscheidungs-/Ableitungsdateien, die das bereits
versiegelte Paket referenzieren, dürfen nicht nachträglich in dieses Paket
eingefügt werden. Früher gebundene Entscheidungen dürfen in einem neuen Paket
liegen, sofern ihre `presented_package` ausschließlich ein früheres Paket bindet.

## 4. HP-W2: eigenständige Datei- und Ableitungsschnittstelle

**Mit HP-W2 eigenständig ausführbar.** Die Schnittstelle benötigt weder Handoff
v3, Builder, Sheet noch Engine. Sie verarbeitet gespeicherte ausgewählte Bytes oder `none`,
erzeugt keine Kandidaten, wählt kein Bild und erteilt keine ZA-1-Zulassung.
Die ausdrückliche Zusammenstellung des einen Quellenroots aus Paket-/Sidecardaten
bleibt Aufgabe späterer Aufrufer; HP-W2 entpackt keine ZIPs und löst keine
`StoredRef`-Paketbindungen auf.

### 4.1 Festes Profil und Berechnung

Das folgende vollständige Objekt ist das einzige Profil v1; zusätzliche oder
abweichende Parameter sind ungültig. `profile_sha256=H(dieses Objekt)`.

```json
{
  "id": "picross-background-png2304-v1",
  "width": 2304,
  "height": 576,
  "format": "PNG",
  "mode": "RGBA",
  "fit": "contain",
  "anchor": "bottom-center",
  "upscale": true,
  "resample": "pillow-rgba-premultiplied-lanczos",
  "color_space": "sRGB",
  "transparent_rgb": "zero",
  "png_compress_level": 9,
  "png_optimize": false,
  "metadata": "sRGB-only"
}
```

Originale dürfen andere native Maße haben. Quelle vollständig als ein PNG-Frame
dekodieren; unterstützte Modi mit höchstens 8 Bit je Kanal
`1|L|LA|P|RGB|RGBA`, inklusive PNG-Transparenz.
Beschädigte/trunkierte Daten, Animation, High-depth und andere Formate werden
abgewiesen. EXIF-Orientierung 1–8 anwenden; ICC wie im bestehenden RP-3-Vertrag
mit LittleCMS, perceptual intent 0 nach sRGB konvertieren, Alpha separat erhalten.
Ungültiges/unpassendes ICC und abweichendes ungetaggtes PNG-Gamma sind Fehler;
ungetaggtes RGB/Grau gilt ausdrücklich als sRGB. Originalbytes niemals ändern.

Für orientierte Maße `W,H`: falls `W*576 >= H*2304`, Zielgröße
`w=2304, h=max(1,floor(H*2304/W))`; sonst
`h=576, w=max(1,floor(W*576/H))`. Das ist proportionaler Fit mit unvermeidbarer
Ganzzahlquantisierung, kein Crop. Auf einer transparenten RGBA-Leinwand bei
`x=floor((2304-w)/2), y=576-h` einsetzen: gemeinsamer unterer mittiger Anker,
Restpixel rechts. Diese aus dem Profil berechneten Werte sind keine individuellen
Eingabefelder. Logische Referenz bleibt 3072×768, kein zweites Ausgabeasset.

Pillow exakt 12.3.0: vor Größenänderung nach `RGBa` vormultiplizieren, mit
`Resampling.LANCZOS` auf `w,h` skalieren und nach `RGBA` zurückwandeln; bei gleichen
Maßen keine unnötige Filterung. Für Alpha 0 RGB auf 0 setzen. Ergebnis ohne erneute
Alpha-Multiplikation in die Nullleinwand kopieren. Keine Freistellung, Retusche,
Farb-/Helligkeitsschlüsselung oder Maskenerzeugung. PNG mit obigen Encoderwerten,
sRGB-Tag mit Intent 0, ohne EXIF/ICC/Text/Zeitdaten schreiben. Hochskalierung
erzeugt kein zusätzliches Originaldetail und wird diagnostisch genannt.

Identische Eingangsbytes und identische Profil-/Werkzeug-/Codecstände ergeben
identische Ausgabebytes. Keine pauschale Byteidentität zwischen unterschiedlichen
Codecbuilds; deren tatsächlicher Stand gehört in die Bindung. Eine andere
Implementierung muss den erklärten Toolstand ändern und frisch geprüft werden.

### 4.2 API, CLI und Auftrag

Moduleinstieg [`tools.puzzle_production.background_assets`](../tools/puzzle_production/background_assets.py):

```text
python -m tools.puzzle_production.background_assets describe
python -m tools.puzzle_production.background_assets derive --request <request.json> --source-root <quellen> --output-root <ausgaben>
python -m tools.puzzle_production.background_assets verify --request <request.json> --source-root <quellen> --output-dir <befundordner>
```

Die [Werkzeuganleitung](../tools/puzzle_production/README.md#hp-w2-eigenständige-hintergrundableitung)
beschreibt die lokale Verwendung mit dem gebundenen Pillowstand. `describe()` liefert exakt
`{profile,profile_sha256,tool,tool_sha256}`. `profile` ist das Objekt aus §4.1,
`tool_sha256=H(tool)`. `tool` ist exakt
`{id,commit,dirty,versions,modules}`: `id="picross-background-1"`, tatsächlicher
`Commit`, Boolean `dirty`, `versions` exakt `{python,pillow,zlib,littlecms}` mit
tatsächlich ermittelten nichtleeren Versionszeichenketten; `modules` eine nach
Pfad sortierte eindeutige Liste `{file: Path,sha256: SHA}` aller tatsächlich
verwendeten eigenen Dekodier-/Profil-/Prüf-/Schreibmodule. Keine behauptete
Übereinstimmung mit dem Commit bei abweichenden Arbeitsbytes.

`derive(request, source_root, output_root)` erhält dasselbe JSON-Objekt wie die
CLI. Wurzeln müssen explizite vorhandene sichere Verzeichnisse sein, dürfen
einander nicht überdecken und nicht auf einen aktiven Spiel-/Katalogbaum zeigen.
Der neue Auftrag `picross-background-derive-request-v1` enthält genau:

| Schlüssel | Typ / Bedeutung |
| --- | --- |
| `format` | Exakt `picross-background-derive-request-v1`. |
| `manifest`, `decision` | `Ref`, unter `source_root` vollständig erreichbar. |
| `source` | Bei `selected` der exakte Original-`Ref` aus Entscheidung/Manifest; bei `none` null. `rejected` ist kein Ableitungseingang. |
| `profile` | Vollständiges unverändertes Objekt aus §4.1, auch bei `none`. |
| `expected_tool_sha256` | `SHA` aus dem tatsächlich gewählten `describe`-Stand; Abweichung vor Schreiben zurückweisen. |
| `output` | Sicherer relativer neuer Verzeichnispfad unter `output_root`. Keine vorhandene fremde oder versiegelte Revision ersetzen. |

API-Objekte durch dieselbe strikte Serialisierung/Validierung isolieren. Der
Request wird mit `H(request)` gebunden; seine Pfade bestimmen keine Runtimeziele.
Alle Manifest-/Entscheidungs-/Originalhashes und Identitäten frisch prüfen;
die gewählte Kandidatenzeile und deren Rechte-/Sichtangaben müssen passen.
HP-W2 prüft Datei-/Entscheidungsbindungen, keine eigene kreative Qualität oder
juristische Rechtegültigkeit. Noch ungeklärte Rechte verhindern die spätere
Bereitschaft, nicht eine als technische Vorbereitung bezeichnete Ableitung.

### 4.3 Stabiler Ableitungsbefund

Bei Erfolg entstehen ausschließlich `derivation.json` und bei `selected`
`background.png` im neuen Ausgabeordner. `none` schreibt keine Nulltextur.
`derivation.json` hat Format `picross-background-derivation-v1` und exakt:

| Schlüssel | Typ / Bedeutung |
| --- | --- |
| `format`, `request_sha256` | Formatkennung und `H(request)`. |
| `request` | Vollständiger unveränderter Auftrag aus §4.2, mit allen sieben Schlüsseln und deren Null-/Typregeln. Sein `H(request)` muss dem obigen Wert entsprechen. Kein ungebundener dritter Pflichtbeleg. |
| `puzzle_id`, `job_id`, `background_revision` | Identische ID-/Revisionsbindung aus dem Manifest. |
| `manifest`, `decision` | Exakte `Ref` der geprüften Eingänge. |
| `outcome`, `candidate_id`, `source` | `selected\|none`; bei selected Kandidaten-ID und Original-`Ref`, bei none beide null. |
| `profile`, `profile_sha256` | Vollständiges Profil und dessen `H(profile)`. |
| `tool`, `tool_sha256` | Tatsächliches vollständiges Toolobjekt aus §4.2 und dessen `H(tool)`. |
| `output` | Bei selected exakt `{file:"background.png",sha256:SHA,bytes:Integer>0}` relativ zum Befundordner; bei none null. |
| `diagnostics` | Exakt `{source: ImageDiagnostic\|null,output: ImageDiagnostic\|null,upscaled: boolean\|null}`. Bei none alle drei null; bei selected vollständig gemessen. |
| `test_only` | Identisch zu Manifest und Entscheidung. |

Die wiederholten `manifest`, `decision`, `source` und `profile` müssen exakt
den entsprechenden Requestwerten entsprechen; `tool_sha256` muss dessen
`expected_tool_sha256` entsprechen. `request.output` bleibt als ursprüngliche
Ausgabeabsicht gebunden. Beim späteren Transport bestimmt der ausdrücklich
übergebene Befundordner den tatsächlichen Ausgabeort; er schreibt diese
ursprüngliche Absicht nicht um.

`ImageDiagnostic` ist exakt `{format,mode,width,height,alpha}`. Maße sind positive
Integer der orientierten sRGB-RGBA-Pixel; `format="PNG", mode="RGBA"` bezeichnen
diese geprüfte Dekodierung beziehungsweise tatsächliche Ausgabe. `alpha` enthält
exakt `{min,max,transparent_pixels,partial_pixels,opaque_pixels}`: min/max 0–255,
Anzahlen nichtnegative Integer mit Summe `width*height`; transparent bedeutet
Alpha 0, partiell 1–254, opak 255. Ausgabe exakt 2304×576. Quelle und Ausgabe
brauchen mindestens ein transparentes und ein sichtbares Pixel. Vollständig
deckend oder vollständig unsichtbar sind technische Fehler, kein `none`.
Eine vorhandene transparente Ecke beweist noch keine korrekte Transparenz
zwischen Strichen; dafür bleibt Q-HG04 erforderlich. Kein globales Qualitäts-,
Rechte- oder Freigabe-`pass` im Befund.

Ein Verbraucher liest Original, Ausgabe und Metadaten frisch, rekonstruiert die
Datei-/Profil-/Toolbindungen und diagnostischen Werte und prüft beim benötigten
Ableitungsnachweis die reproduzierte Ausgabe. Ein übernommener Hash oder
Erfolgsstatus allein ist kein solcher Nachweis. HP-W2 bietet dafür
`verify(request, source_root, output_directory)` als lesende API mit demselben
Ergebnisvertrag; CLI zusätzlich `verify --request … --source-root … --output-dir …`.
Der vollständige Request ist aus dem Befund erreichbar und muss dem übergebenen
Objekt exakt entsprechen; der Verbraucher benötigt keine verlorene Requestdatei
und rekonstruiert keine Felder durch Raten. Die CLI darf dafür eine eigene
temporäre Requestdatei mit genau diesem Objekt verwenden. Sie schreibt nichts
in Eingänge oder Ausgabeordner und gibt bei Erfolg `verified` zurück. Kein Solver oder
Engineimport gehört zu diesem Nachweis.

Für **lesendes `verify`** bleiben Request, Befund, originales `tool` und ihre
Hashes vollständig unverändert und werden strikt geprüft. Aktuelle `id`, die
vollständige `versions`-Map und die exakte sortierte Modulpfad-/Bytehashmenge
müssen dem Erzeugerstand entsprechen. Ausschließlich `commit` und `dirty`
bezeichnen die unveränderte Herkunft des Erzeugerlaufs; sie verlangen keinen
identischen HEAD oder Dirtyzustand im späteren Prüfcheckout. Geladene Modulbytes
müssen den aktuellen Dateien entsprechen; dieser vollständige aktuelle
Werkzeugstand und alle Eingangs-/Befundbytes dürfen sich während der Prüfung
nicht ändern. Ausgabe und vollständigen Befund mit dem **originalen Toolobjekt**
frisch reproduzieren und bytegenau vergleichen. Eine passende Hashliste allein
ist kein Reproduktionsnachweis.

`derive`, einschließlich seines schreibenden `reused`-Pfads, behält die strikte
vollständige aktuelle `expected_tool_sha256`-Bindung. Tatsächlich geänderte
Module, Codecs oder Profile bleiben `tool_mismatch` und erfordern eine getrennte
neue Ableitung; alte Request-/Befund-/Freigabebytes werden nicht umgeschrieben.
Der v6-Prüfbericht führt den aktuellen Prüfstand in `tool`; die unveränderte
Erzeugerbindung bleibt im über `background.binding.derivation` gebundenen
Originalbefund. Offline prüfbar bedeutet ohne ursprünglichen
Quellcheckout, Netzwerk oder ungenannte Dateiwurzel, jedoch mit dieser kompatiblen
vollständigen Modul-/Codec-/Profilbindung; keine beliebige zukünftige Portabilität.

Eine neue äußere Ableitung ersetzt keinen im unveränderten Originalhandoff
deklarierten, weiterhin prüfpflichtigen Altbefund. Ein inkompatibler Altbefund
sperrt den Eingang vor Mutation. Seine spätere Nutzung benötigt einen ausdrücklich
passenden Prüfstand oder eine reguläre neue Paketrevision mit ihren nötigen
Bindungen; keine automatische Neuversiegelung oder Umbindung alter Endfreigaben.
Damit wird keine allgemeine Übernahmefähigkeit älterer 0.7.0-Vorabableitungen
behauptet; gültige 0.6.0-Altwege bleiben erhalten.

### 4.4 Ressourcen, Ergebnis, Wiederholung und Fehler

Je Request/Manifest/Entscheidung/Befund höchstens 2 MiB; Quellen-PNG höchstens
32 MiB, 8192 Pixel je Achse und 8.000.000 dekodierte Pixel. Maximal 20 Kandidaten,
64 Parameter und 64 Einträge je übriger Liste; Referenzgraph höchstens 256
Dateien/96 MiB für die von HP-W2 tatsächlich benötigte gewählte Teilmenge.
JSON-Tiefe höchstens 32. Die Grenzen gelten vor vollständiger Dekodierung,
anschließend auch an den tatsächlich gelesenen Bytes. Kumulativer kooperativer
Zeit-/Prüfrahmen 300 Sekunden ab erstem Lesen; keine garantierte Laufzeit und
kein behauptetes hartes RSS-Limit. Speicher-/Signal-/Zeitabbruch liefert keinen
positiven Teilbefund. Die unveränderten ZIP-/Paketgrenzen gelten zusätzlich
beim späteren PB-H-Paketbau, nicht als Enginebudget.

API/CLI liefern dieselbe geschlossene **transiente** Antwort, deren Semantik an
Request v1 gebunden ist; keine weitere persistente Ergebnisdatei:
`{status,derivation,output,error,remaining}`. `status` ist
`derived|none|reused|verified|invalid_input|conflict|aborted|technical_error`.
Bei Erfolg ist `derivation` der `Ref` auf den frisch geprüften Befund und `output`
der `Ref` auf das PNG oder null; beide beziehen sich auf den ausdrücklich
benannten Ausgabeordner. `error=null, remaining=null`. Bei Fehlern sind beide
Refs null; `error` ist exakt `{code,message,path}` mit `message: Text`,
`path: Path|null`, und `remaining` ein tatsächlicher absoluter Restpfad oder null.
Fehlercodes und Status sind fest zugeordnet:

| Status | Ausschließlich zulässige Codes und Bedeutung |
| --- | --- |
| `invalid_input` | `invalid_json` für Syntax/Encoding/doppelte Schlüssel; `invalid_request` für Schlüssel-/Typ-/Null-/Parameter- oder CLI-Syntaxfehler; `unsupported_format` für unbekannte deklarierte Formatgenerationen; `invalid_binding` für bereits beim ersten Lesen widersprüchliche Hashes/Identitäten/Entscheidungen; `missing_file` für fehlende deklarierte Eingänge; `unsafe_path` für unzulässige Pfade/Dateiarten; `invalid_image` für nicht unterstützte oder beschädigte Bild-/Farbprofile; `opaque_image`, `empty_image` für die beiden Alpha-Grenzverletzungen; `resource_limit` für überschrittene deklarierte Größen-/Mengen-/Tiefegrenzen; `tool_mismatch` für abweichenden angeforderten Werkzeugstand. |
| `conflict` | `source_changed` für während desselben Laufs veränderte zuvor geprüfte Eingänge; `target_conflict` für vorhandene fremde/abweichende/unvollständige Ausgabe, widersprüchliche Quellenbelegung oder belegten Ziel-Lock. Keine automatische Wahl eines anderen Ziels. |
| `aborted` | `interrupted` für behandeltes Signal/Abbruch, `deadline_exceeded` für den kooperativen Zeitrahmen, `resource_exhausted` für tatsächlich erschöpften Arbeitsspeicher. |
| `technical_error` | `io_error` für sonstige tatsächliche I/O-/Berechtigungs-/Speicherplatzfehler, `internal_error` für unerwarteten Werkzeug-/Codecfehler. |

`derived` bezeichnet neue selected-Ausgabe, `none` einen neuen Nullbefund;
`reused` gilt für den unveränderten bereits vollständigen Dateisatz beider
Ausgänge, `verified` ausschließlich für erfolgreiche lesende Prüfung.
Erfolgsstatus mit Fehlercode und Fehlerstatus mit Erfolgsrefs sind ungültig.

| Exit / Status | Aussage |
| --- | --- |
| 0 / `derived`, `none`, `reused`, `verified` | Vollständiges erfolgreiches Datei-/Ableitungsergebnis; keine Inhalts-/Integrationsfreigabe. |
| 2 / `invalid_input`, `conflict` | Ungültige/fehlende/nicht unterstützte Eingänge, stale Bindung oder Zielkonflikt. Keine automatische Reparatur oder Wiederholung. |
| 4 / `aborted` | Zeit, Speicher oder Signal; kein Erfolg. |
| 5 / `technical_error` | Unerwarteter Datei-/Werkzeugfehler; keine Bewertung des Motivs. |

Stdout genau ein JSON-Objekt, Fortschritt/Diagnose auf stderr. Syntaxfehler
verwenden Exit 2; harter Kill garantiert keine Schlussausgabe. `describe`
verwendet bei Fehler dieselbe Fehlerantwort, bei Erfolg sein §4.2-Objekt.

Quellen vor/nach Lesen und vor Publikation gegen Pfad, Dateiidentität, Größe und
Hash prüfen. Nur in einem eigenen markierten Stagingordner schreiben, alle
geschriebenen PNG-/JSON-Bytes frisch prüfen, dann den vollständigen Ordner ohne
Ersetzen veröffentlichen. Kooperativer OS-Lock schützt denselben Zielroot.
Gleicher Request und gleicher Toolstand dürfen bei vollständig identischem
Dateisatz nach frischer Prüfung `reused` ergeben: keine Byte-/mtimeänderung.
Vorhandener leerer, unvollständiger, abweichender oder fremder Ordner ist Konflikt,
kein No-op. Keine stille Toolaktualisierung und kein Überschreiben mit ähnlichen
Pixeln. Bei behandeltem Fehler eigene unpublizierte Stages entfernen; fremde
Bytes und bereits vollständige Veröffentlichungen erhalten und Restpfad melden.
Nach hartem Kill eigene Reste erst nach Besitz-/Lockprüfung gemäß WORKSPACE
bereinigen. Ein möglicherweise vollständiger Rest wird erst nach vollständiger
frischer Prüfung desselben Requests wiederverwendet.

## 5. Paketbindung und gewöhnliche finale Endabnahme

Handoff/Inventar eines vorgelegten Pakets bleiben unverändert. Die spätere
Entscheidung und Ableitung liegen außen; der äußere Record führt die aktuellen
Refs und den daraus geprüften effektiven Status. Das funktioniert auch, wenn
das Originalhandoff noch `raster_ready` mit offener Bildwahl enthält. Die neue
Readergeneration muss Originalstatus und äußeren aktuellen Befund getrennt
ausgeben, statt das Original als nachträglich fertig versiegelt auszugeben.

Für 0.7.0 ist die finale Form **`picross-editorial-approval-v2`** vorgesehen.
Sie enthält exakt sämtliche Felder der bisherigen v1-Freigabe aus
[ZA-1](ZA1_ADAPTER.md), unverändert in Typ und Semantik:
`format,actor,timestamp_utc,statement,puzzle_id,revision,handoff_sha256,
inventory_sha256,selection,test_only`. Nur `format` wird v2. `selection` bleibt
exakt `{variant,matrix_hash,logic_hash,reveal}` mit bisheriger Kandidaten- und
kanonischer Matrix-/Logikbindung; `reveal` exakt `{file,sha256}`.
Zusätzlich sind genau diese zwei Felder Pflicht:

| Feld | Geschlossene Bindung |
| --- | --- |
| `original_zip_sha256` | `SHA` des unveränderten tatsächlich ausgewählten Original-ZIPs, zusätzlich zu Handoff/Inventar. |
| `background` | Exakt `{manifest:StoredRef,decision:StoredRef,derivation:StoredRef,outcome:"selected"\|"none",candidate_id:ID\|null,original:Ref\|null,output:Ref\|null,profile_sha256:SHA}`. Die drei StoredRefs lokalisieren unveränderte Dateien nach §3.1. Bei selected sind Original/Kandidat/Ausgabe exakt die inneren Werte aus Entscheidung/Befund, mit deren ausdrücklich bestimmten Wurzeln; bei none alle drei null. Keine zweite abweichende Pfadauflösung. |

Eine frühe Auswahl bleibt nutzbar. Bei später gebündelter Auswahl nennt der
gewöhnliche Auftrag 4 das tatsächlich vorgelegte Rasterpaket, die isolierte
Hintergrunddatei/Revision beziehungsweise `none` und das vereinbarte Profil.
Die KI berechnet Hashes, zeichnet die tatsächliche Erklärung in Entscheidung
und Endabnahme auf und darf die vereinbarte deterministische Ableitung fertigstellen.
Die finale v2-Freigabe wird erst nach ihrer erfolgreichen Prüfung mit den tatsächlichen
Ausgabe-/Befundhashes geschrieben; der Akteur/Zeitpunkt bleibt der echte frühere
Eigentümerakt. Das bindet dessen ausdrücklich vereinbarte mechanische Ableitung,
keine nachträglich kreativ geänderten unbekannten Bytes. **Keine Neuversiegelung
des Originalpakets, kein zweiter Bestätigungsprompt, keine Buchabnahme.**

Fehlt eine eindeutige finale Erklärung für das tatsächlich gewählte Raster oder
die Bildwahl, bleibt genau diese Entscheidung offen. Eine Auswahl mit
Korrekturwunsch genehmigt keine noch unbekannte Korrektur. Noch fehlende
Ableitung/Rechte/Adapterfähigkeit darf als technische Arbeit oder Blocker
fortgeführt werden; eine vorhandene Erklärung wird nicht als erfolgreiche
Integration ausgegeben. Die v2-Freigabe ersetzt keine manuellen Autorisierungen,
Palettenausnahme, Kategorie-/Difficultybindung oder Integrationsbefugnis.

Handoff, äußerer Record und finale Freigabe gehören zu derselben `puzzle_id`
wie Manifest, Entscheidung und Befund; alle tatsächlich vorhandenen
`test_only`-Felder sind identisch. Der äußere Record erbt diese Eigenschaft
unveränderlich aus seinem Handoff, ohne ein neues Feld zu erfinden. Reale und
synthetische Produktion dürfen weder gemischt noch ineinander umdeklariert
werden. Für bisher optionale `test_only`-Felder gilt der bestehende Default
false; auch dieser effektive Wert muss übereinstimmen. Paket-`revision` ist
absichtlich unabhängig von Hintergrund-, Bild- und
Entscheidungsrevision; Gleichheit von Revisionszeichenketten wird nicht gefordert.
Die konkrete ausgewählte Paketrevision und Originalbytes bleiben gleichwohl
über `PackageBinding`/Endabnahme vollständig gebunden.

## 6. Korrektur, Wiederaufnahme und reine Hintergrundrevision

| Änderung / Situation | Verbindliche Folge |
| --- | --- |
| Illustration, Komposition oder Transparenz materiell geändert | Neue Bild-/Manifestrevision, betroffene Wahl und sämtliche davon abhängigen Ableitungen veraltet. Geänderte Einzeldatei isoliert vorlegen und tatsächlich auswählen; alte Belege behalten ihre Aussage. |
| Unveränderte Originalbytes, vereinbarte Größenableitung oder identischer Pakettransport | Keine neue kreative Auswahl. Datei-/Profil-/Toolbindung prüfen; neue Ableitung bei geändertem Toolstand getrennt binden. |
| Nur administrative Manifestangaben berichtigt | Alte Originale/Entscheidung erhalten. Übernahme über `carried_from` nur bei identischen gewählten Originalbytes, Kandidaten-ID/Bildrevision, `context` und Profil; tatsächlicher Akteur/UTC/Wortlaut/Beleg bytegleich. Neue Manifestbindung und Berichtigungsgrund im Entscheidungsprotokoll; keine erfundene neue Zustimmung. Geänderte Rechte werden eigenständig geprüft. |
| Rastermaß, Zellwerte oder Palette geändert, Motivkontext unverändert | Vorhandene gültige Hintergrundwahl bleibt bestehen; nur die nach Authoring fälligen Raster-/Paletten-/Proofnachweise erneuern. Keine zusätzliche Buchsicht. |
| Motivkontext oder geschützte Merkmale geändert | Gezielten Hintergrundvergleich dokumentieren. Bei betroffener Kontext-/Bildidentität neue Bildentscheidung; nicht automatisch drei neue Motive. |
| Auswahl abgelehnt oder konkrete Korrektur offen | Zustand `rejected`/`pending`, Korrektur nur im Auftrag; unveränderte bereits autorisierte Rasterarbeit darf fortgesetzt werden. Keine automatische erste/empfohlene Option. |
| Wiederaufnahme | Index/Record, tatsächlichen Paketstand, Hintergrundmanifest, Entscheidung, Originale, Rechte, Befund und Freigaben selbst laden/prüfen. Keine erneuten Uploads/Bestätigungen für bereits erreichbare gültige Bytes; keine stillen Versionswechsel. |
| Reiner späterer Hintergrundersatz | Gesonderter Bildauftrag mit neuen Originalen/Wahl/Ableitung und dem sicheren HP-I1b-Weg. Lösungs-, Hinweis-, Paletten-, Schwierigkeits-, Runtime-/Saveidentität, Slot, Added-Daten und gültige unveränderte Freigaben erhalten. Keine Rekonstruktion alter bereinigter Rasterproduktion oder neuen Solverläufe allein wegen des Bilds. |

Neue Auswahl auf derselben gültigen Vorlage erzeugt eine neue separate
Entscheidung mit explizitem `previous_decision`; abhängige Ableitung/Endbindung
muss genau diese Wahl verwenden. Keine alten Freigaben überschreiben. Für
`carried_from` gilt dieselbe azyklische Vorgängerregel; der neue Record kann
nicht auf sich oder einen Nachfolger zeigen. Eine Materialänderung ist darüber
nicht übertragbar. Der ursprüngliche ImageGen-Prompt legitimiert keine Änderung.

## 7. Transportformen ohne Datenverlust

Unveränderte Felder werden nicht neu erfunden: „Basis“ bezeichnet nachfolgend
den exakten dokumentierten und ausführbaren Vertrag an der in §1 genannten
Commitbasis. Die angegebenen Deltas sind vollständig; alte Generationen
behalten ihre eigenen geschlossenen Feldmengen. Unbekannte deklarierte Formate
und neue Felder in alten Hüllen werden abgewiesen, nicht entfernt oder als
Freitext versteckt. PB-H unterstützt §§7.1–7.2 und die **Ausgabe** von
Sheet-Update v3 nach §7.3. HP-I1a ergänzt äußere Fortschreibung nach §7.4;
MJ-A führt Sheetimport, Sitzung v5 und Auftrag v4 im regulären Arbeitsbereich
nach §7.5. Der gesonderte spätere Änderungsjob folgt MJ-B nach Hintergrundvertrag §7.6.

### 7.1 Hintergrundbindung und Handoff v3

`BackgroundBinding` ist exakt
`{manifest:StoredRef,decision:StoredRef|null,derivation:StoredRef|null,history:History}`.
Diese Hülle ist kein weiteres Dateiformat. Sie enthält keine frei wählbaren
Erfolgsflags; Zustand und Bereitschaft werden nach §3.4 berechnet. Aktuelle
Entscheidung/Ableitung passen zum Manifest; ein `carried_from` wird vollständig
nach §6 geprüft. Frühe Phasen dürfen beide auf null lassen. Ableitung ohne
Entscheidung ist ungültig. Eine spätere äußere Bindung darf nur offene Daten
ergänzen oder eine ausdrücklich abgelöste Entscheidung fortschreiben.
Die `ref`-Werte innerhalb der StoredRefs müssen mit den entsprechenden inneren
Refs in Entscheidung, Befund und eingebettetem Request übereinstimmen.
Verschiedene `storage`-/`root`-Werte lokalisieren dieselben gebundenen Bytes;
sie ändern deren Identität nicht. Vor Auswahl und bei rejected ist `derivation`
null. Bei selected/none darf sie bis zum erfolgreichen HP-W2-Lauf null sein;
Bereitschaft benötigt den gültigen passenden Befund.

Handoff v3 erhält genau die bisherigen Handoff-v2-Felder gemäß Authoring §6.2
und dem geschlossenen `HANDOFF_KEYS`-/Phasenvertrag in
[authoring_build_contract.py](../tools/puzzle_production/authoring_build_contract.py),
mit `format="picross-authoring-handoff-v3"`, `rulebook.version="0.7.0"`,
dem tatsächlich dazu passenden Snapshot und dem zusätzlichen Pflichtfeld
`background: BackgroundBinding`. Die bestehenden Optionalfelder und ihre
Null-/Typregeln bleiben bestehen; keine Hintergrunderweiterung unter `editorial`.
`state` und die beiden neuen Gates folgen §2. `gate_evidence` erhält dieselben
zwei Schlüssel, jeweils `Path|null` relativ zum Original-ZIP-Root wie die
bisherigen Gatebelege. Bei `pass` zeigt `background_choice` genau auf die
gebundene Entscheidungsdatei und `background_asset` auf den Ableitungsbefund:
jeweils `StoredRef.root` plus `StoredRef.ref.file`, wobei Root `.` keinen
zusätzlichen Pfadteil erzeugt. Sonst ist der Wert null. Spätere äußere Befunde
stehen in `BackgroundBinding`; sie schreiben diese ursprünglichen Gates und
Belegpfade nicht um. Bestehende
Bild-/Motiv-/Kandidaten-/Paar-/Paletten-/Difficultyfelder behalten ihren Vertrag.
In neuen versiegelten Kandidatenhandoffs bleiben finale Endabnahme und Export
offen; diese späteren Erklärungen liegen außen.

Vor der Auswahl müssen alle angebotenen Originale wirklich gespeichert und
erreichbar sein. Nach Auswahl dürfen aktuelle Rasterpakete nur die gewählte
Quelle, benötigte Belege und Ableitung enthalten. Dann ist `history` Pflicht
für im Manifest noch deklarierte, ausschließlich verworfene Kandidaten-Dateien:
Sie bezeichnet die frühere gesicherte identische Vorlagenrevision. Fehlende
aktive Quelle, Entscheidung, Rechte-/Prüfbelege oder Ableitung dürfen darüber
nicht ersetzt werden. Der Reader unterscheidet die aktive erforderliche
Referenzmenge von historischen verworfenen Alternativen; keine leere/defekte
deklarierte aktive Datei wird als historisch erklärt. Ein lokaler Transport ohne
erreichbaren gesicherten früheren Stand behält sämtliche angebotenen Dateien.
PB-H erhält diesen Kontext ausschließlich als optionalen API-Parameter
`history_repo` beziehungsweise `--history-repo <checkout>`. Der Reader liest
die exakte bereits lokal vorhandene Gitrevision aus `history`; kein Fetch,
Checkout, Schreibzugriff oder Raten einer Arbeitswurzel. Dies ist kein weiteres
Bauauftragsfeld. Eine verlangte Weglassung ohne belegbaren lokalen Kontext
ist ein Fehler; aktive Quellen oder Belege sind dadurch nie ersetzbar.

### 7.2 Äußerer Record v2, Inventar und Builder

Record v2 ist der vollständige bisherige PB-A-Record aus
[authoring_builder.record_for](../tools/puzzle_production/authoring_builder.py),
mit `format="picross-authoring-record-v2"` und zusätzlich
`background: BackgroundBinding`. Vorhandene Felder bleiben erhalten:
`puzzle_id,revision,state,category_id,build_request_sha256,repo_commit,
document_revision,rulebook,package,handoff,inventory_sha256,
final_editorial_approval,width,height,mode,used_colors,difficulty,verification,
blockers,next_action,next_step,integration,source_commit,pr,reveal,motif,
reveal_options,parameters`. Ihre Typen/Nullbedingungen folgen unverändert PB-A;
`final_editorial_approval` bindet bei 0.7.0 die v2-Freigabe. `state` ist der
geprüfte effektive Stand nach §2; das Originalhandoff wird dadurch nicht geändert.
`verification` darf nur tatsächlich ausgeführte Prüfungen mit ihrem Umfang
ausweisen. Git-Sicherungscommit bleibt von gelesenem Tool-/Quellencommit getrennt.

Inventar **`picross-authoring-file-inventory-v1`** und Arbeitsindex
**`picross-authoring-index-v1`** bleiben unverändert. Datei-/SHA-/Byteeinträge
reichen für neue Hintergrunddateien; der Index verweist weiterhin nur auf
Recordpfad je ID/Revision. Selbstreferenzen bleiben ausgeschlossen. Auch der
Teilkopievertrag `picross-authoring-derivation-v1` bleibt unverändert; er ist
keine Hintergrundableitung und erlaubt keine Neuversiegelung.

PB-H verwendet **`picross-authoring-build-request-v2`**: dieselben acht
Top-Level-Schlüssel und Typen wie v1, jedoch Handoff v3/0.7.0 und neue
Phasen-/Referenzprüfung. Die geschlossene `external`-Menge bleibt unverändert;
`approval.json` enthält bei 0.7.0 die finale v2-Freigabe. Neue Hintergrunddateien
werden über die bestehende `files`-Liste eingebracht. Deren Paketpfade erhalten
die ausdrücklich gewählten Arbeitswurzeln und alle inneren Ref-Pfade; Befund und
PNG behalten ihren gemeinsamen Elternordner. Kein eigener Normalisierer und
keine Umbenennung auf feste Sidecar-Aliasnamen. Frühe Hintergrundentscheidungen
dürfen in frühen Handoffs unabhängig vom finalen ZA-1-Gate gesichert werden.
`approval.json` als finale Freigabe bleibt an vollständig geprüfte
Inhaltsbereitschaft gebunden. Nachträgliche äußere Recordpflege bindet Sidecars
nach §3.1/5/7.1, verändert keine Originalpaketbytes und ist keine erneute
`build`-Versiegelung. Ihr sicherer Writer ist HP-I1a nach §7.4. PB-H erzeugt oder datiert
keine Endfreigabe und bindet vorhandene Erklärungen nicht auf neue Bytes um;
er liest ausschließlich eine bereits passende `approval.json` v2.

Bei `raster_ready` und `content_ready` wird das **geschriebene ZIP** frisch
über die bestehenden Package-/Zieladapterprüfungen rein lesend kontrolliert.
`raster_ready` verlangt sämtliche bisherigen 0.6.0-Inhaltsgarantien; nur
Hintergrundbereitschaft und finale Endabnahme dürfen offen sein. `content_ready`
verlangt zusätzlich gültige Hintergrundwahl, geklärte Rechte, konkrete
Q-HG-Urteile und frisch mit HP-W2 geprüftes Asset beziehungsweise Nullbefund.
Die Prüfung setzt keinen Produktstatus selbständig hoch und gibt keinen neuen
Hintergrundeingang für alte v5-Exporte oder Registrierungswriter frei.
Verschachtelte, gebundene Hintergrund-`derivation.json` ist erlaubt; die
Authoring-Teilkopie im Root, ZIP-Verschachtelung und Neuversiegelung bleiben
ausgeschlossen. Pfad-/Dateihashes und innere Ref-Pfade bleiben unverändert;
nur äußere `StoredRef`-Wurzeln lokalisieren transportierte Bytes.

**`picross-authoring-build-result-v2`** behält exakt die bisherige erfolgreiche
Hülle `format,status,directory,indexed,record,sheet,files` beziehungsweise die
bisherige Fehlerhülle `format,status,message,remaining,next_action`; `record`
ist v2 und `sheet` v3. Diese geänderte verschachtelte Semantik begründet die
Versionserhöhung. Alte Bauaufträge/-ergebnisse v1 bleiben 0.6.0/PB-A; keine
pauschale Erhöhung der unveränderten RP-/Proof-/Inventar-/Indexformate.

### 7.3 Sheet-Update v3, Sitzung v5 und Auftrag v4

`picross-cheatsheet-update-v3` enthält sämtliche bisherigen v2-Schlüssel und
Typen aus Authoring §7, zusätzlich genau:

| Schlüssel | Typ / Bedeutung |
| --- | --- |
| `Hintergrunddaten` | `BackgroundBinding\|null`; null nur vor Anlage einer neuen Hintergrundarbeit oder bei tatsächlich altem Eingang, niemals als `none`. |
| `Hintergrundstatus` | `pending\|offered\|rejected\|selected\|none\|legacy` oder null vor Zuordnung. Legacy ausschließlich nach altem Eingangsvertrag. Muss zur tatsächlich geprüften Bindung passen; das Sheet selbst behauptet keine Byteprüfung. |
| `Hintergrund-Optionen` | 0–20 Einträge, je exakt `{ID,Beschreibung,Datei,SHA-256,Bildrevision}`; Typen `ID,Text,Path,SHA,Revision`, entsprechend dem gebundenen Manifest. |
| `Hintergrundauswahl` | Kandidaten-ID, `none` oder null. `none` ist reserviert und keine zulässige Kandidaten-ID. Dies ist Formularabsicht, keine erfundene tatsächliche Entscheidung. |

Für ein **erzeugtes Update v3** sind genau diese Kombinationen zulässig:

| Status | Bindung und Optionen | Auswahl im Update |
| --- | --- | --- |
| null | `Hintergrunddaten=null`, Optionen `[]`; neue Arbeit noch nicht zugeordnet. | null |
| `legacy` | `Hintergrunddaten=null`, Optionen `[]`; aus einem tatsächlich gültigen alten Eingang abgeleitet. | null |
| `pending` | Bindung vorhanden, Entscheidung/Ableitung null, Manifest presentation pending; Optionen `[]`. | null |
| `offered` | Bindung vorhanden, Entscheidung/Ableitung null, Manifest presentation offered; vollständige Optionen. | null |
| `rejected` | Bindung mit aktueller rejected-Entscheidung, Ableitung null; Optionen nach Manifestpräsentation. | null |
| `selected` | Bindung mit aktueller selected-Entscheidung, Ableitung passend oder noch null; vollständige Optionen. | Genau deren Kandidaten-ID |
| `none` | Bindung mit aktueller none-Entscheidung, Ableitung passend oder noch null; Optionen nach Manifestpräsentation. | `none` |

„Vollständige Optionen“ ist exakt die geordnete Projektion aller Kandidaten des
gebundenen offered-Manifests: `ID=id`, `Beschreibung=description`,
`Datei=original.file`, `SHA-256=original.sha256`, `Bildrevision=revision`.
`Datei` ist relativ zur gebundenen Manifestarbeitswurzel; keine andere
Dateiwurzel. Bei pending-Präsentation immer `[]`, auch bei bereits teilweise
gespeicherten Kandidaten. Gesicherte verworfene Optionen können nach §7.1 über
`history` erreichbar sein; ihre Anzeige behauptet keine lokal vorhandenen Bytes.
Eine geänderte Wahl benötigt die tatsächlichen Originale erneut erreichbar,
ohne sie automatisch herunterzuladen oder neu zu erzeugen.

In **Sitzung v5 und Auftrag v4** bleiben binding/status/options genau an diese
historische Kombination gebunden. Nur `selection` darf als neue Formularabsicht
abweichen: null, `none` oder eine ID der vorhandenen Optionen; bei null/legacy
Status zwingend null. Ohne angebotene Optionen ist allein null oder bewusst
`none` möglich. Der daraus erzeugte Eigentümertext nennt bei frühem `none`
ausdrücklich auch den Verzicht auf die üblichen drei Kandidaten. Umschalten
ändert weder Status noch Entscheidung; auch ein neuer Auswahlwert macht
rejected/ungelöste technische Arbeit nicht bereit. Der Sheetparser prüft diese
Formkombinationen, die nachgelagerte Produktion zusätzlich Dateien und Hashes.

Neue Übergaben setzen die Auswahl nur bei bereits tatsächlich erklärter Wahl;
ansonsten null, auch bei einer Empfehlung. Späteres Umschalten im Sheet ändert
nur die Absicht im nächsten Auftrag, nicht den historischen Entscheidungsrecord.
Der nächste abgesendete Eigentümerauftrag muss den gewählten Kandidaten mit
Originalhash/Revision und Manifestbindung beziehungsweise bewusst `none` nennen.
Im Auftrag 3 darf Hintergrundauswahl offen bleiben; Auftrag 4 darf sie mit der
Endabnahme bündeln. Vor einem Integrationsauftrag muss eine vorhandene gültige
Entscheidung oder eine ausdrückliche neue Auswahlabsicht vorliegen.

Hintergrundoptionen dürfen mit Rasteroptionen zusammen auftreten, ohne ein
Kreuzprodukt zu erzeugen. Abschlussbild- und Rasteroptionen bleiben wie bisher
gegenseitig ausgeschlossen. Jede Rasteroption erhält zusätzlich genau
`Hintergrunddaten` und `Produktionsstatus`; Hintergrundbindung muss zur jeweiligen
Paketrevision passen, Status ist `raster_ready|content_ready`. Der v3-Auswahlweg
darf `raster_ready` als solche beschriftete Vorlage für die gebündelte Entscheidung
führen; v2 bleibt bei seiner bisherigen `content_ready`-Pflicht. Rasterwechsel
übernimmt Paket-/Hintergrundbindungen gemeinsam, erhält eine schon tatsächlich
erklärte Hintergrundwahl nur bei identischer Manifest-/Originalbindung und
erfindet keine Auswahl für ein anderes Manifest.

**`picross-cheatsheet-session-v5`** hat exakt die v4-Top-Level-Schlüssel
`format,choices,fields,filter,image` plus `background`. Bestehende `fields`,
`filter`, `image` und persönliche Einstellungsgrenzen bleiben unverändert.
`background` ist exakt `{binding,status,options,selection}` und transportiert
verlustfrei die vier zusätzlichen Updatefelder. `choices` bleibt exakt
`reveals,rasters,reveal,raster`, mit den oben erweiterten Rasteroptionen.

**`picross-authoring-request-v4`** hat exakt die bisherigen v3-Schlüssel aus
`brief()`/`exportPackage()` des
[Offline-Sheets](ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html):
`format,execution,created_at,rulebook,fields,choices,input_image,note,
requested_step,prompt_file`, zusätzlich dasselbe `background`-Objekt.
`execution` einschließlich Arbeitswurzel/Bereinigung bleibt unverändert;
Regelquelle und tatsächlich verwendeter Stand bleiben ausdrücklich gebunden.
`requested_step`/`prompt_file` sind für den gespeicherten Auftrag Pflicht,
wie bisher erst beim Export ergänzt. Die Promptdatei enthält die konkrete
Auswahlabsicht und bestehenden Freigabe-/Integrationsauftrag. Export/Sitzung
allein erteilen keine Freigabe. `picross-request-files-v1` und persönliche
`picross-cheatsheet-settings-v1` benötigen keine Strukturänderung.

Importvalidierung ist atomar: unbekannte Version/Felder, unvollständige Optionen,
fremde IDs, widersprüchliche Nullwerte oder Bindungen verwerfen den gesamten
Import. Alte Updates/Records/Sitzungen bleiben nach ihrem Vertrag lesbar und
leeren ausschließlich im ausdrücklich gewählten Zieljob vorherige neue
Options-/Hintergrunddaten; dessen Joboptionen bleiben erhalten. Keine Vermischung
mit einer anderen Produktion. Import, Sitzungsbackup und Auftragsexport erhalten alle
neuen Bindungen, wirklichen Entscheidungen und offenen Werte. Alte Leser müssen
neue Generationen zurückweisen. Der Record-v1-Import projiziert nur
bekannte Felder und könnte hineingeschriebene Hintergrunddaten verlieren;
deshalb niemals neue Arbeit als scheinbar kompatiblen v1-Record ausgeben.

### 7.4 HP-I1a: sichere äußere Fortschreibung

Der Finalizer konsumiert bereits tatsächlich aufgezeichnete Entscheidungen,
HP-W2-Befunde und gegebenenfalls Endfreigabe v2. Er erzeugt keine menschlichen
Akteure, Zeitpunkte oder Erklärungen. Eine gültige frühe Auswahl bleibt nutzbar;
eine erst am versiegelten Paket erklärte Wahl bindet `presented_package`.
`none` benötigt die tatsächliche Erklärung, den HP-W2-Nullbefund und bei frühem
Verzicht den Beleg für die abweichende Kandidatenzahl. Das äußere Manifest
bleibt exakt dieselbe versiegelte Manifestidentität; neue materielle Bildarbeit
gehört in eine reguläre neue Revision.

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <request.json> --source-root <neue-dateien> --output-root <authoring-root> [--history-repo <checkout>]
```

API: `finalize_background(request, source_root, output_root, *, history_repo=None)`.
Bei Repositoryarbeit ist `output_root` die Checkoutwurzel, bei lokaler Arbeit
die vorhandene Authoringwurzel. `history_repo` wird ausschließlich lesend
verwendet; kein Fetch oder Checkout. Der geschlossene Auftrag
**`picross-authoring-finalize-request-v1`** enthält exakt:

| Schlüssel | Typ / Bedeutung |
| --- | --- |
| `format` | Exakt `picross-authoring-finalize-request-v1`. |
| `record` | `Ref` relativ zum Zielroot auf den erwarteten vorhandenen Record v2. Hash und Bytezahl schützen vor einem inzwischen geänderten Record. Die Originalidentität stammt aus dessen vollständig geprüftem Record/ZIP. |
| `sidecar_root` | Neuer sicherer relativer Ordner innerhalb derselben Authoringrevision, außerhalb von Paket-, Runtime- und Gitpfaden. Sämtliche neuen äußeren Dateien liegen darunter; vorhandene unveränderte äußere Refs werden ausdrücklich am Ziel gelesen. |
| `background` | Vollständiges `BackgroundBinding={manifest,decision,derivation,history}`. Nur hinzugefügte Daten oder eine ausdrücklich belegte Nachfolgeentscheidung sind zulässig; keine andere Manifest-/Rätselidentität. |
| `authorizations` | Exakt `approval.json`, `manual-authorization.json`, `owner-override.json`, `palette-exception.json`, je `Ref\|null` relativ zum Zielroot. Null erteilt nichts und darf keine bereits gültige gebundene Autorisierung still entfernen. |
| `files` | Geordnete eindeutige Liste von `Ref` für exakt die neuen äußeren Nutzdateien; gleiche relative Pfade unter `source_root` und `output_root`. Getrennte Wurzeln, keine Globs oder Umbenennungen. |

Original-ZIP, bytegleiche Handoffkopie, Inventar, ursprüngliche Gates, Regelwerk
und logische Nachweise bleiben unverändert. Index v1 verweist weiterhin auf
denselben Record und wird nicht geschrieben. Record v2 und Sheet-Update v3
behalten ihre geschlossenen Hüllen; `verification` beschreibt die tatsächlich
frische Prüfung, `state` deren effektiven Stand, höchstens
`raster_ready|content_ready|editorially_approved`. Der Integrationsblocker bleibt.
Neue ungesicherte Fortschreibung erfindet weder `source_commit` noch `pr`.

Innerhalb des tatsächlichen Prüfberichts speichert
`verification.authorizations` genau die vier geprüften Request-Refs oder null
als physische Zielroot-Lokalisierung für spätere Fortschreibung. Das ergänzt
keine Freigabesemantik und kein Record-Top-Level-Feld. Vorhandene Angaben werden
mit ihren tatsächlichen Bytes erneut geprüft. Bei bisherigen PB-H-Records ohne
diese Prüfdetails gelten ausschließlich deren ausdrücklich definierten bisherigen
Autorisierungsorte; keine Suche nach passenden Dateien und keine Übernahme bloßer
Erfolgsflags. Der unveränderte lesende Inhaltsbericht bleibt ein Prüfbericht;
die zusätzlichen Writer-Lokalisierungen gehören zum gespeicherten Record.

Der Writer verwendet denselben Authoring-OS-Lock wie `build`:
`.git/authoring-builder.lock` beziehungsweise lokal `.authoring-builder.lock`.
Im eigenen markierten Stage einen vollständig neuen Sidecarordner aufbauen,
Quellen, Recorderwartung, Referenzen und geschriebene Bytes frisch prüfen,
danach den ganzen Ordner ohne Ersetzen publizieren. **Den Record atomar zuletzt**
auf den geprüften Nachherstand umschalten. Kein Indexwechsel oder Katalogjournal.

Zur Wiederaufnahme liegt darin `operation.json` mit Format
**`picross-authoring-finalization-v1`** und exakt
`format,request_sha256,record,before,after,files`:
`request_sha256=H(request)`, `record` sicherer Zielrootpfad, `before` und `after`
je `Ref` relativ zum Sidecarordner auf die bytegenauen
`record.before.json`/`record.after.json`. `files` enthält exakt die Nutzdateirefs
relativ zum Sidecarordner, ohne Selbstreferenz oder die separat gebundenen
Records. Diese drei internen Namen sind für Auftragspayload reserviert.
Ein mitgelieferter HP-W2-Befund liegt in einem **eigenen Unterordner** mit seinem
exakten bisherigen Dateisatz; `sidecar_root` darf nicht selbst Befundordner sein.
Diese operativen Authoringdaten bleiben bis zum späteren regulären Abschluss
erhalten und bilden kein dauerhaftes Technikarchiv.

Vor Sidecarpublikation entstehen keine neuen aktiven Referenzen. Zwischen
vollständigem Sidecarordner und Recordumschaltung darf ein klar benannter,
vollständiger unreferenzierter Rest verbleiben; derselbe Request prüft ihn frisch
und setzt fort. Nach Recordcommit erkennt derselbe Request über Request-/Vorher-/
Nachherbindung den echten Byte-/mtime-No-op, obwohl der Record nicht mehr den
alten erwarteten Hash hat. Prüfzeitpunkte dabei nicht neu schreiben. Fremde oder
veränderte Record-/Sidecarbytes sind Konflikte; keine Locklöschung, pauschale
Verzeichnislöschung oder automatische Wahl eines anderen Ziels.

**`picross-authoring-finalize-result-v1`** enthält bei Erfolg exakt
`format,status,record,sheet,operation`: Status `updated|reused`, tatsächlicher
Record und Sheet-Update, `operation:Ref` relativ zum Zielroot. Bei Fehler exakt
`format,status,message,remaining,next_action`, Status
`invalid_input|conflict|aborted|technical_error`, tatsächlicher Restpfad oder null
und keine Erfolgsteilresultate. Exit 0/2/4/5 bedeutet Erfolg, Eingabe/Konflikt,
Abbruch beziehungsweise technischen Fehler; stdout enthält genau ein JSON-Objekt.
Keine Git-Schreiboperation, kein Commit, Branchwechsel, Fetch oder Push;
die vorgesehenen lesenden Gitprüfungen bleiben zulässig.

### 7.5 MJ-A: Mehrjob-Arbeitsbereich und sichere Übernahme

Maßgeblich ist die [Paketentscheidung MJ-A / #490](https://github.com/venomenon328/picross/issues/490#issuecomment-6774440064).
Der reguläre Offline-Arbeitsbereich führt unabhängige Produktionsjobs einschließlich
früher Jobs ohne Rätsel-ID. Zehn kleine gültige Jobs in mindestens drei Phasen müssen
gleichzeitig bearbeitbar und vollständig sicherbar sein. Kein Batchbetrieb, keine
Modell-API und keine automatischen Bild-, Repository- oder historischen Abrufe.

**Geschlossene Sammlung.** `picross-cheatsheet-workspace-v1` enthält exakt
`format,active_job_id,jobs`. `jobs` ist eine geordnete Liste; jeder Eintrag enthält
exakt `job_id,session,options,record`:

| Feld | Vertrag |
| --- | --- |
| `job_id` | Stabile lokale Kennung nach `[A-Za-z0-9][A-Za-z0-9_-]{0,63}`, unabhängig von Rätsel-ID und Manifest-`job_id`, nicht aus einer Rätsel-ID abgeleitet. Bleibt bei ID-Vergabe, Revision und Export/Import erhalten. |
| `session` | Vollständige Sitzung v4 oder v5 nach ihrem jeweiligen Vertrag. Alte v1–v3-Sitzungen werden ohne fachlichen Versionswechsel nach v4 normalisiert. |
| `options` | Exakt `repoSave,mergeMode,ruleSource,rulePath,ruleRef`, mit vorhandenen Enum-/Pfad-/Refregeln; neu aus persönlichen Voreinstellungen. |
| `record` | `null` oder der gültige unverändert importierte Record v1/v2, passend zu Rätsel-ID, Revision, Paket, Inventar und gegebenenfalls Hintergrund. Materielle Bindungsänderungen setzen ihn auf `null`; keine Originaldatei ändern oder neuen Record erfinden. |

`active_job_id` bezeichnet genau einen vorhandenen Job; bei leerer Sammlung ist es
`null`. Lokale Kennungen sind eindeutig; jede nichtleere Rätsel-ID gehört höchstens
einem Job. Reihenfolge bleibt erhalten. Die Übersicht leitet Motiv, ID, Status und
nächsten Schritt aus der Sitzung ab und zeigt den Hintergrundstatus getrennt.
Blocker kommen aus dem passenden Record, andernfalls „nicht mitgeliefert“.
Gespeicherte false-Readiness wird nicht zu Erfolg, `raster_ready` nicht zu
`content_ready`. Keine frische Prüfung oder Repositoryverfügbarkeit behaupten.

**Persönliche Daten und Joboptionen.** Nur `workspaceRoot`, `cleanupMode` und
`theme` gelten jobübergreifend und gehören nicht in die Sammlung. Die bestehende
Sicherung `picross-cheatsheet-settings-v1` bleibt das persönliche Setup-/
Voreinstellungsbackup. Bearbeitung, Import und Wechsel eines Jobs dürfen seine
Optionen nicht durch gemeinsam verwendete Listener als globale Voreinstellung
zurückschreiben. Alte Einzelimporte erhalten vorhandene Zieljoboptionen; neue Jobs
beginnen mit persönlichen Voreinstellungen. Ein neuer Hintergrundimport darf den
passenden Vorschaupfad ausdrücklich in derselben Übernahmevorschau anbieten.
Bei Sammlungsimport zeigt die Vorschau
auch mitgelieferte Ablage-/Mergeoption und Regelquelle/-pfad/-stand. Konfiguration,
Import, Auswahl, Wechsel oder Export erteilen keine Befugnis: maßgeblich bleibt der
tatsächlich abgesendete Eigentümerauftrag. Keine fremde Arbeitswurzel oder lokale
Bereinigungsfreigabe aus Produktionsdaten übernehmen.

Vor Jobwechsel den aktuellen Formularstand im Arbeitsspeicher sichern; keine neue
Pflicht zur dauerhaften Browserablage. Reset und Entfernen betreffen nur den
gewählten Job. Reset erhält seine lokale Kennung, beginnt aber eine neue Generation.
Nach Authoring §9 bleiben tatsächlicher Integrationscommit und kompakte
Abschlussbezüge erhalten. Gelöschte ZIPs, Arbeitsbilder oder Proofs weder als verfügbar
anbieten noch für die Übersicht wiederherstellen.

**Atomare Übernahme.** Vor Einzelimport einen bestehenden Zieljob oder einen neuen
Job ausdrücklich wählen. Die Vorschau zeigt Ziel, Rätsel-ID, Revision, Änderungen,
Joboptionen und Paket-/Hintergrundbindungen. Eine bisher ID-lose Produktion darf
eine noch freie ID erhalten; verschiedene nichtleere IDs dürfen nicht vermischt
werden. Ersetzen derselben Revision ist nach ausdrücklicher Vorschau erlaubt.
Sammlungsimport ersetzt ausdrücklich die ganze Sammlung; kein implizites Mischen.
Abbrechen erhält sämtliche bisherigen Jobs.

Erst vollständig parsen, Schemas und Querverbindungen prüfen, Bilder dekodieren
und dann einmalig übernehmen. Unbekannte Versionen/Felder, doppelte JSON-Schlüssel,
nichtendliche Zahlen, falsche Typen, doppelte IDs und widersprüchliche Bindungen
verwerfen die gesamte neue Hülle vor Mutation. `JSON.parse` allein erkennt keine
doppelten Schlüssel. Bestehende Datei-/Bildgrenzen bleiben; Sammlungsgrenzen vor
teurem Dekodieren prüfen und zehn kleine gültige Jobs zulassen. Bestehende fremde
Byte- oder semantische Hashes unverändert erhalten: kein Neuhashen umserialisierter
Objekte, kein erfundener Hash. Alteingänge wirken nur auf den gewählten Zieljob und
leeren neue Options-/Hintergrunddaten nach ihrem Altvertrag. Eine offene Vorschau
ist an Zielkennung und Generation gebunden und wird beim Anwenden erneut geprüft.

**Record v2 benötigt die tatsächliche Projektion.** Der Record besitzt Referenzen,
aber nicht die vollständigen Kandidaten-/Statusdaten eines Update v3. Zulässig sind
nur ein erfolgreiches `picross-authoring-build-result-v2` (`built|reused`) mit Record
und Sheet, ein erfolgreiches `picross-authoring-finalize-result-v1` (`updated|reused`)
mit Record und Sheet oder zwei ausdrücklich lokal zugeordnete Eingänge. Rätsel-ID,
Revision, Paket, Inventar, Phase, Source/PR und Hintergrundbindungen müssen
zusammenpassen. Einen nackten Record v2 mit Hinweis auf die benötigte Projektion
ablehnen, ohne Zustandsänderung oder Abruf/Rekonstruktion. Ein vollständiges Update
v3 allein bleibt gültig. Tatsächliche nächste Schritte aus
`authoring_builder.sheet_from_record` und `authoring_finalization` auf die
vorhandenen Auftragskarten abbilden, einschließlich „3 · Rätsel produzieren“,
Hintergrundbereitschaft/Endabnahme und finaler Integration mit HP-I1/HP-I2 oder
HP-I1b/HP-I2. Originaltext und Blocker erhalten; niemals beliebigen Importtext als
ausführbaren Code interpretieren oder ein historisches Zielgate für aufgehoben erklären.

**Version und Hintergrund.** Neue Jobs starten mit 0.6.0/Sitzung v4. Bewusstes
Aktivieren des Hintergrundwegs oder sichtbarer v3/v5-Import verwendet 0.7.0/v5.
Beide eingebetteten Snapshots müssen ihren Markdownquellen bytegleich entsprechen:
0.6.0/docrev48 und 0.7.0/docrev9. Jeder v5-Job bindet den Vorschaupfad beziehungsweise
den passenden 0.7.0-Anhang. Bleiben nach Alteingang inkompatible Joboptionen erhalten,
Prompt und ZIP bis zur ausdrücklichen kompatiblen Regelwahl sperren; kein stiller
Pfadwechsel, keine Umschreibung alter Pakete, keine andere Produktionsformaterhöhung.

Sitzung v5 und Auftrag v4 erhalten exakt `background={binding,status,options,selection}`.
Historische Bindung, Status und Optionen bleiben konsistent; allein `selection`
ist eine neue Absicht für den nächsten Auftrag. Unbekannt, Legacy, offen, angeboten,
abgelehnt, ausgewählt und tatsächlich `none` bleiben verschieden. Keine automatische
Erstwahl; fehlende Daten bedeuten nicht `none`. Frühe bewusste Leerabsicht erklärt
im abgesendeten Auftrag den Verzicht auf die drei Kandidaten. Hintergrundoptionen
führen kompakte Datei-/Hashrefs; der eigene Abschlussbild-/Motiv-/Rasteranhang bleibt
getrennt, ohne eingebettete Hintergrundgalerie. Rasterwechsel übernimmt Paket und
Hintergrund gemeinsam. Materielle Kontext-/Datei-/Hashänderungen übertragen keine
alte Entscheidung; gültiges importiertes `carried_from` folgt unverändert §6.
Unveränderte gültige Auswahl erhalten, nur tatsächlich abhängige Nachweise entwerten.

Prompts trennen drei isolierte Kandidaten, Auswahl, Korrektur und Verwendung der
konkreten Endfassung. Keine Kandidaten zur Auswahl ins Buch integrieren und keine
zweite Routinebestätigung einer gültigen unveränderten Entscheidung verlangen.
Auftrag 4 braucht eine gültige Entscheidung oder ausdrücklich neue konkrete Absicht;
technische Prüfung, Endabnahme und Integrationsbefugnis bleiben erforderlich.

**Asynchrone Bindung.** Jeder Datei-, Bild- oder Importvorgang bindet lokale
Jobkennung, monoton fortgeschriebene Generation und eigenes Operationsticket.
Jobwechsel A→B→A, Reset, Entfernen, Import oder Revisionswechsel entwerten ältere
Ergebnisse einschließlich Fehler-, Abschluss- und Zwischenablagepfaden. Prompt-/
ZIP-Exporte erfassen vor dem ersten `await` den vollständigen unveränderlichen
Jobstand mit Optionen, Regeltext, Bildbytes und Dateiname. Bei inzwischen veralteter
Ursprungsbindung abbrechen; niemals A-Inhalt mit B-Hash, Dateiname oder Befugnis
kombinieren. Lokale Bilder weiterhin frisch prüfen, `picross-request-files-v1`
unverändert verwenden.

`picross-background-adoption-request-v1` bleibt in MJ-A ausdrücklich abgewiesen;
der Hinweis nennt den vorhandenen HP-I1b2-Werkzeugweg. Der eigene spätere Änderungsjob
mit aktueller Ziel-/Sourcebindung gehört ausschließlich MJ-B. MJ-A schließt deshalb
Issue #490 nicht vollständig ab und aktiviert keinen neuen Produktionsdefault.


### 7.6 MJ-B: eigenständige Hintergrundrevision im Sheet

Maßgeblich ist die [Paketentscheidung MJ-B / #490](https://github.com/venomenon328/picross/issues/490#issuecomment-6778334390).
Dieser Bedienweg verwendet den unveränderten technischen Request aus §11.1.
0.6.0 bleibt Default; keine neue Produktions-, Writer- oder Freigabefunktion.

#### D01 · Versionierte Sammlung, bestehende Jobidentität

Neue äußere **`picross-cheatsheet-workspace-v2`**, exakt `format,active_job_id,jobs`; jeder Job weiterhin exakt `job_id,session,options,record`.

- Reguläre Jobs enthalten unverändert Sitzung v4/v5, vorhandene Optionen und null bzw. passenden Record v1/v2.
- Adoptionjobs enthalten die neue eigene Sitzung aus D02; `record` ist **zwingend null**, damit es nur einen unveränderlichen Requestträger gibt.
- Der neue Sammlungswriter schreibt v2. Der v1-Reader bleibt nach seinem alten geschlossenen Vertrag lesbar und akzeptiert weiterhin ausschließlich reguläre Jobs. Import einer alten Sammlung darf die neue Arbeitsfamilie nicht unter v1 verstecken; alte Originaldateien bleiben unverändert.
- Lokale `job_id`, Reihenfolge und aktiver Job behalten die MJ-A-Regeln. **Jede nichtleere Rätsel-ID gehört weiterhin höchstens einem Job in der ganzen Sammlung**, unabhängig von der Familie. Revisionen werden innerhalb dieses Jobs geführt; kein stiller Wechsel auf Eindeutigkeit nur je Jobart.
- Regulär ↔ Adoption ist ausschließlich als **sichtbarer vollständiger Ersatz** des ausdrücklich gewählten Zieljobs zulässig, bei gleicher oder noch leerer Rätsel-ID und mit erhaltener lokaler Job-ID. Die Vorschau nennt ersetzte Sitzung, Varianten/Anhänge/Quellrecord und Regelweg; vorherige Sicherung bleibt erreichbar. Kein Zusammenmischen. Andere nichtleere Rätsel-ID verlangt einen neuen Job.
- Reset erhält lokale ID und Jobart, leert deren Arbeitsdaten/Request/Abschluss; Entfernen wirkt nur auf diesen Job. Persönliche Defaults und bestehende Joboptionen behalten ihre Bedeutung. Sammlung bleibt auf die vorhandenen Grenzen beschränkt: höchstens 200 Jobs und 50 MiB Eingabe; kleine gemischte Arbeitsbereiche müssen passen.

Die neue Hülle ist eine **MJ-B-Entscheidung**, kein bereits bestehendes Format. Alte Updates, Sitzungen, Requests, Records und der Authoringindex behalten ihre Feldmengen.

#### D02 · Eigene geschlossene Adoption-Sitzung

**`picross-background-adoption-session-v1`** hat exakt `format,fields,request_text,completion`.

| Bestandteil | Verbindlicher Inhalt |
| --- | --- |
| `fields` | Exakt `title,puzzle_id,revision,briefing,change_request,source_ref,pr,integrated_commit`. `title` ist Text bis 200 Zeichen; `briefing`/`change_request` Text bis 20.000 Zeichen. Gültige Unicode-Skalare, kein NUL. `puzzle_id`/`revision` sind vor Zuordnung null, sonst nach den vorhandenen HP-I1b2-ID-/Revisionsregeln; `source_ref` null oder sichere vorhandene Repo-Ref-Grammatik, `pr` null oder positive sicher darstellbare PR-Nummer. `integrated_commit` ist null oder ausdrücklich angegebene vollständige Main-SHA für den Abschlussauftrag, keine im Sheet verifizierte Mainintegration. `source_ref` bezeichnet den beauftragten Repository-Lesestand auch bei Dateiübergabe; eine separat bereitgestellte vollständige Arbeitsrevision kann im Briefing konkret benannt werden. Metadaten sind ein überlieferter Fundort, keine bestätigte Dateiverfügbarkeit und kein geprüfter Zielzustand. |
| `request_text` | null oder vollständiger ursprünglicher UTF-8-Text eines Requests v1 einschließlich genau seiner End-LF, höchstens 2 MiB als UTF-8-Bytes. Strikt lesen gemäß D03; niemals trimmen, hübsch formatieren, neu autorisieren oder beim Export rekonstruieren. |
| `completion` | null oder die geschlossene kompakte **gemeldete** Abschlussbindung aus D06. `request_text` und `completion` schließen einander aus. |

Beide letzten Felder null bedeuten einen frühen Entwurf, keinen gültigen technischen Request. Bei nichtnull Request müssen dessen ID und Revision zu den Feldern passen; dieselbe Pflicht gilt für die aus einem Abschlussref ableitbare Identität. Kein zusätzlicher frei erfundener Produktionsstatus, keine Kandidatenliste aus Manifestrefs rekonstruieren, kein `registered`- oder Integrations-Erfolgsflag.

Die Oberfläche zeigt den eigenen Typ, Ziel-ID/Arbeitsrevision, Request-/Sourcebindung und überlieferte Autorisierung lesbar sowie den tatsächlichen Umfang ihrer lokalen Prüfung. Request, target, background und authorization sind schreibgeschützt. Auswahl-/Erfolgsaussagen nicht aus dem freien Autorisierungstext parsen: Der Request selbst enthält keinen `selected|none`-Outcome und keine Kandidatenprojektion.

Eine neue materielle `change_request` ist **neue Absicht** und sperrt die Übernahme des noch geladenen alten Requests. Den unveränderten alten Record zum Korrigieren/Abgleichen weiterreichen ist zulässig, ihn als Freigabe der neuen Bytes auszugeben nicht. Ein ausdrücklich angenommener neuer passender Request kann den Wunsch in derselben Importvorschau ablösen; identische alte Requestbytes heben ihn nicht still auf. Eine bewusste Rücknahme des Änderungswunsches ist getrennt erkennbar. Änderung gebundener Ziel-ID/Revision erfolgt nur über ausdrücklich neuen bzw. ersetzten Arbeitsstand. Ein anderer Request oder eine neue ID-/Revisionsbindung übernimmt keinen früheren Mainbeleg: `fields.integrated_commit` und eine alte Abschlussbindung werden in der sichtbaren Übernahme auf null gesetzt; auch die zugehörige PR wird bei geänderter Arbeitsrevision nicht still als neue PR übernommen.

#### D03 · Strikter, atomarer Import mit ehrlicher Prüftiefe

Direktimport des Original-Requests aus Datei oder exakt erhaltenem JSON-Text, neue Adoption-Sitzung, Sammlung v1/v2 und alle bisherigen regulären Einzelinputs unterstützen. Vollständige Vorschau und bewusste Übernahme wie in MJ-A; vor Fehler/Abbruch keine Teilmutation. Eine request-v1-Datei darf in keinen regulären Record-/Rasterpfad fallen. Bestehendes `pendingTransfer` muss Familie, Ziel, Generation und alle benötigten Daten binden.

Die reine Requestform aus [`background_request.py`](https://github.com/venomenon328/picross/blob/a87cd91cbd82c5bd69f9206a5466b20e2aeff83c/tools/puzzle_production/background_request.py) unverändert lesen:

- Exakt `format,puzzle_id,revision,target,background,authorization,files,test_only`; alle geschlossenen Unterformen, Typen und vorhandenen Grenzen berücksichtigen.
- `target.source` am festen Pfad `content/backgrounds/<id>.json`, gültiger Ref, Ursprungshash und positive gebundene Bildrevision; drei nichtnull externe Background-Refs unter genau der eigenen Arbeitsrevision, `history=null`; echte Human-Form und deren passender Inventarref.
- Sortiertes eindeutiges Dateiinventar gemäß bestehendem Vertrag, höchstens 256 Einträge, 32 MiB je Datei, 96 MiB deklarierte Gesamtbytes; kein Selbstref/Rootausbruch/erkennbarer Alias- oder Pfadpräfixkonflikt. Pfad-/Unicodevertrag nicht still auf ASCII einschränken.
- Doppelte JSON-Schlüssel, unbekannte Felder/Versionen, falsche Scalars/Nullen, nichtendliche oder nicht sicher darstellbare Zahlen und ungültige Unicode-Skalare abweisen. Binärdatei mit fataler UTF-8-Dekodierung lesen; BOM oder unzulässige Bytes nicht still normalisieren.
- Für diesen geschlossenen, ASCII-schlüsseligen Request nur **lesend** prüfen, dass der Originaltext `canonical_bytes(request) + LF` entspricht. Keine neue Produktionskanonisierung: eine abweichende Darstellung zurückweisen, nicht reparieren. Der Export verwendet ausschließlich den Originaltext/dessen identische UTF-8-Bytes. Dateihashes entstehen aus diesen tatsächlichen Bytes; vorhandene semantische Produktionshashes bleiben unverändert.
- Lesekompatibilität mit den echten reinen Python-`validate`/`encoded`-Regeln nachweisen, einschließlich erlaubter Unicode-Pfade/Erklärungen, Alias-/Präfixkonflikten und kanonischen Negativfällen. Keine bloße Prüfsimulation oder erfundene Gleichheit aller JS-/Python-Namensvergleiche.

**Grenze:** Das ist Form-/Byte-/innere Referenzprüfung. Die Oberfläche hat weder die in `files` genannten Originale gelesen noch aktuellen Source-/Capability-/Rechte-/Ableitungs-/Zielzustand geprüft. Keine vollständige `read`-/`plan`-Prüfung behaupten. `test_only` wird unverändert und sichtbar geführt; synthetische Autorisierung wird nicht als reale Inhaltsfreigabe ausgegeben. Fremde Plan-, Journal- und CLI-Ergebnishüllen bleiben kontrolliert abgewiesen.

#### D04 · Eigene Aufträge, unveränderte Befugnisse

Eigene Karten bzw. Schritte **`prepare,rework,resume,adopt,complete`**, getrennt von den vier regulären Rasteraufträgen:

| Schritt | Mindestkontext und Verhalten |
| --- | --- |
| `prepare` | Zugeordnete Rätsel-ID, expliziter Quellstand und Briefing. Bestehende aktuelle Zielsource/Revealautorität im beauftragten Produktionsweg prüfen, drei isolierte Hintergrundkandidaten vorbereiten/vorlegen. Ein gespeicherter Request ist noch nicht erforderlich; keine erfundene Zielbindung. |
| `rework` | Konkreter Auswahl-/Korrekturwunsch mit tatsächlich verfügbaren Datei-/Revisionsreferenzen; vorhandenen Request nur als unveränderten Bezug mitgeben. Eigentümertext unverändert und sichtbar in den Prompt übernehmen; materielle Änderungen haben neue passende Entscheidung, keine automatische Wiederverwendung alter Freigabe. |
| `resume` | Konkreter Arbeitsstand bzw. gültig importierter Request und Fundort. Nur nächsten bereits autorisierten Schritt fortsetzen; keine neue Freigabe und kein erfundener bereits gespeicherter/adoptierter Zustand. |
| `adopt` | Nichtnull strukturell gültiger Originalrequest, konkret benannter Repository- oder separat bereitgestellter Dateifundort der vollständigen Arbeitsrevision und keine offene materielle Änderungsabsicht. Vorhandene Auswahl/Zielautorisierung erhalten. Ausführender prüft vollständige Dateien und frisches Ziel, nutzt ausschließlich `store/plan/adopt` und beauftragten Gitablauf. Kein `request_text=null`- oder Abschlussfall als neue Adoption. |
| `complete` | Request/zugeordnete Arbeitsrevision oder kompakte historische Abschlussbindung plus ausdrücklich benannter vollständiger integrierter Maincommit. `retire-background-production` prüft aktualisiertes origin/main und genau diese Revision; keine ganze-ID-Bereinigung, kein Wiederaufbau alter Rasterpakete. |

Notwendige fehlende Angaben zeigen; technische `adopt`-/`complete`-Ausgabe bis dahin sperren, keine scheinbar ausführbare Integration mit Platzhaltern. Für reine Entwurfsaufträge erkennbare fehlende Angaben nach vorhandener Vorlagensemantik behandeln. `prepare/rework` sind Bild-/Auswahlaufträge für ChatGPT Work; `resume/adopt/complete` technische Aufträge für Codex mit gültiger eingestellter Arbeitswurzel.

Auftragstexte verlangen aktuelle AGENTS.md, Pflichtquellen, Hintergrundvertrag und den tatsächlichen HP-I1b2-/§9-Weg. Kein reguläres OUTPUT_POLICY erzwingen, das den Adoptionrecord als Raster-Sheet-Update ausgibt: Ergebnis nennt tatsächliche Dateien/PR, Stand und nächsten Schritt; ein erzeugter echter Request wird unverändert als record.json geliefert, ohne konkurrierende Übergabeform. Normale Inhaltsaufträge bleiben von Modell-/Reasoningempfehlungen ausgenommen.

Ablage-/Mergeoptionen stammen ausschließlich aus diesem Job und wirken erst im tatsächlich abgesendeten Auftrag. Der bloße Import, Jobwechsel, Kopieren oder Export erteilt keine Befugnis. Vorhandene eindeutige Auswahl nicht routinemäßig nochmals bestätigen; kein Testeinbau/Buchrender oder zusätzliche Rätsel-Endabnahme für einen reinen Hintergrundwechsel. Übernahme ist keine automatische Aktivierung von 0.7 als Default.

#### D05 · Eigener Auftragsexport, sichere Originalbytes und Regelbindung

Neue **`picross-background-adoption-sheet-request-v1`** mit exakt
`format,execution,created_at,rulebook,fields,request,completion,requested_step,prompt_file,note`.

- `execution` und `rulebook` verwenden exakt die bisherigen **äußeren** Sheettypen aus Auftrag v4; `fields` entspricht D02; `completion` entspricht D06. `requested_step` ist einer der fünf D04-Schritte, `prompt_file="auftrag.md"`.
- `request` ist null oder Ref `{file:"original-request.json",sha256,bytes}` der wirklich ausgegebenen unveränderten Requestbytes. Der feste technische Repositorypfad bleibt aus ID/Revision ableitbar und wird im Prompt genannt; äußeres Transportfile und technischer Recordpfad sind verschiedene Dinge.
- `created_at` ist nur die Exportzeit, niemals eine neue menschliche Autorisierungszeit. Fester `note`: „Bedienauftrag, keine Produktionsdateisammlung und kein frischer Freigabe-, Ziel- oder Prüfbeleg.“
- ZIP enthält `auftrag.md`, `brief.json`, bei nichtnull Request `original-request.json`, bei Offline-Regelquelle den passenden `PICROSS_PUZZLE_AUTHORING.md`-Snapshot und `dateien.json` nach unverändertem `picross-request-files-v1`. Keine automatische Aufnahme der referenzierten `request.files`-Dateien. Die vollständige Arbeitsrevision muss dem Ausführenden im benannten Repositorystand oder ausdrücklich separat bereitgestellt erreichbar sein; der Fundort kann im vorhandenen Briefing genannt werden. Das Sheet bestätigt weder diese Verfügbarkeit noch Payloadvollständigkeit; fehlende Originale bleiben im externen `store/plan`-Weg ein echter Blocker. Kein Dummy-`package.zip` und kein Auftrags-v4-Etikett für die neue Familie.
- Einzel-Sitzung und Sammlung sichern den Originaltext unverändert. Der Auftrag/ZIP bindet vor dem ersten await vollständigen unveränderlichen Job-, Options-, Regel-, Prompt-, Dateinamen- und Bytestand. Alle Hash-/Clipboard-/Downloadfortsetzungen verwenden die bestehende Job-/Besuchs-/Operationsticket-Disziplin; A→B→A, Reset, Typwechsel, Revision oder Entfernen machen veraltete Fortsetzungen ungültig.
- Adoption verwendet ausdrücklich den 0.7-Preview-Regelweg; neue reguläre Jobs starten weiterhin im aktiven **0.6.0**-Default. Auswahl/Übernahme eines Adoptionjobs macht die 0.7-Wahl sichtbar und lokal. Keine Änderung persönlicher Defaults oder anderer Jobs. Bei unpassender erhaltener Regelquelle bleibt Prompt/ZIP bis zur bewussten passenden Wahl gesperrt.
- Ausgangsstände sind **0.6.0/docrev46** und **0.7.0/docrev7**. Bei der Implementierung beide Dokumentrevisionen und vollständige eingebettete Snapshots konsistent nachführen; echte Snapshotbytes/Inventarhashes prüfen, ursprüngliche Request-/Produktionsbindungen nicht umetikettieren.

Ein Import dieses äußeren Auftragsexports als Live-Sitzung oder einer CLI-Ergebnishülle ist nicht Bestandteil von MJ-B. Sitzung und Sammlung sind die expliziten Wiederaufnahmeformate.

#### D06 · Gemeldeten Abschluss kompakt führen

`completion` hat exakt `request,target,background,authorization,test_only,integrated_commit,report_url`.

Über eine ausdrücklich bezeichnete Aktion **„Abschluss melden“** aus dem vorhandenen Originalrequest ableiten: `request` ist der Ref seiner tatsächlichen Bytes am festen `content/authoring/<id>/<revision>/record.json`-Pfad; `target,background,authorization` sind exakte unveränderte Kopien; `test_only` ist die unveränderte Boolean-Kopie und bleibt auch im historischen Abschluss sichtbar. Vollständiger tatsächlich gemeldeter Maincommit aus `fields.integrated_commit` und HTTPS-Link auf den konkreten Integrations-/Retirementabschluss werden ausdrücklich eingetragen; in einer abgeschlossenen Sitzung müssen beide Maincommitfelder übereinstimmen. Eine offene `change_request` sperrt diese Abschlusskonvertierung; sie muss zuvor durch den passenden neuen Arbeitsstand oder die getrennt erkennbare bewusste Rücknahme behandelt sein. Der Abschluss des alten Requests darf keinen neuen Änderungswunsch still entsorgen. Diese Angabe ist kein neues Inhaltsfreigaberitual und keine vom Sheet selbst geprüfte Mainintegration.

Danach `request_text=null`; vollständige `files`-/Kandidaten-/Arbeitsdaten nicht als weiter verfügbare Inhalte behalten oder anbieten. Alle verbleibenden Refs sind klar **historische Identitäten**, Status **„Abschluss gemeldet“**, niemals „frisch geprüft“. `briefing`/`change_request` werden für den abgeschlossenen Stand geleert; Identität/Fundort/PR und kompakte Bindung bleiben. Ein späterer neuer Bildjob darf diese alte `target.source` nicht automatisch als heutige Quelle verwenden.

Der Import einer solchen Sitzung prüft geschlossene Form und innere Querverbindungen einschließlich festem Recordpfad und ID/Revision; reale Belege verbleiben beim Ausführenden. `complete` kann den gebundenen erneuten Abschluss/No-op prüfen lassen. Neue materielle Arbeit benötigt einen ausdrücklich neuen Entwurf/Arbeitsstand. Keine Ergebnisflag-Rekonstruktion, keine Löschung im Browser und keine Wiederherstellung bereinigter Originale.



## 8. Konkrete Einführung und Reader-/Writermatrix

| Paket / vorhandene Dateien | Fähigkeit und erlaubter Zwischenstand |
| --- | --- |
| **HP-W1 / #560:** dieser Fachvertrag, Authoring/Snapshot, Qualität, Profil, Produkt/Design, Produktions-/Werkzeugrouting | Geliefert: Sollvertrag und Dokumentrevision. Aktive Version 0.6.0, durch HP-W1 keine geänderten ausführbaren Reader/Writer. |
| **HP-W2 / #560:** `tools/puzzle_production/background_assets.py` und zugehörige Hintergrundhilfen | Geliefert: eigenständige Arbeits-/Entscheidungs-/Ableitungsformen und API/CLI `describe/derive/verify` nach §3–4. Kleine synthetische Tests sichern die Datei-/Bildfähigkeit. Frühe Bildarbeit bleibt vorbereitet; kein Handoffbau oder ZA-1-/Runtimeversprechen. |
| **PB-H / #489:** `tools/puzzle_production/authoring_build_contract.py`, `authoring_builder.py`, `background_package.py`, `authoring_package.py` und der lesende Teil von `target_adapter.py` | Geliefert: vollständiger opt-in 0.7.0-Vorschausnapshot, geschlossene Format-/Phasenzulassung, typisierte Referenzmenge samt explizitem lokalen Historykontext, Builder v2, Record v2 und Sheet-v3-Projektion. Frische HP-W2-Verifikation, vollständige lesende Inhaltsprüfung des geschriebenen ZIPs bei `raster_ready`/`content_ready` und Lesen bereits gebundener Endfreigabe v2. Kein späterer Sidecarwriter oder finaler Export. |
| **HP-I1a / #561:** `tools/puzzle_production/authoring_builder.py`, `target_adapter.py` und Finalizer-/Hintergrund-/Exporthelfer | Sichere spätere äußere Entscheidung/Ableitung/Endfreigabe und Recordfortschreibung nach §7.4; v6-Export mit unverändertem Original-ZIP, expliziten Außen-/Transportbindungen und frischer Offlineprüfung. Höchstens `editorially_approved`, keine Registrierung; alte Verbraucher sperren v6 vor Mutation. |
| **HP-I1b1 / #561:** `tools/puzzle_production/catalog_background.py`, `content_registry.py`, `catalog_integration.py`, `integrated_content.py` und Zieladapter | Geliefert: erste v6-Registrierung im kompatiblen Ziel, Registry v3, kompakte aktive Quelle und Receipt v2 nach §10. Runtimefähigkeit und deren Abnahme gehören zu HP-I2; synthetische Werkzeugdurchstiche ersetzen sie nicht. |
| **HP-I1b1 gemeinsame Veröffentlichung:** `catalog_transaction.py`, `catalog_publication.py`, `catalog_io.py`, `registration_publication.py`, `registration_verification.py`, betroffene Folgeoperationen `content_update.py`, `content_registry.py`, `catalog_reveal.py`, `reveal_source.py`, `reveal_retirement.py`, `integrated_content.py` unter `tools/puzzle_production/` | Geliefert: vollständige Quellen-/Plan-/Journalbindung nach §10 und SD-Catalog; No-op, Recovery und Main-gebundener erster Abschluss. Metadaten-/Legacyzieloperationen erhalten Hintergründe; neue Hintergrundziel-Neubindungen verwenden gezielt §12. |
| **HP-I1b2 / #561** | Geliefert: eigener unveränderlicher Request, Source v2, Plan, nullable Binärrollback und revisionsgenauer Abschluss nach §11 für bereits hintergrundgebundene Ziele. Keine Legacy-Nachrüstung. |
| **HP-I1c / #561** | Geliefert: Source v3 mit unverändertem Erstursprung und aktuellen Raster-/Revealbindungen, genau begrenzte neue Plan-/Journalgenerationen und gemeinsame Reader-/Recoveryregeln nach §12. |
| **HP-I2 / #561:** `game/model/content_registry.gd`, erzeugte `game/data/registry.json` und Buch-/Importanschluss | Regulärer Runtime-v6-Eingang, Variante A, gemeinsames Assetlayout, verlustfreier Import/Mipmaps und Bedarfsladen nach §13. Der Kategoriepilot bleibt ausschließlich Legacy; kein Produktionsvorschau-Renderer. Technische Abnahme und Lieferstand am konkreten PR prüfen. |
| **MJ-A / #490:** `docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html` und `tools/test_authoring_sheet.py` | Regulärer Mehrjob-Arbeitsbereich nach §7.5, gepaarter Record-v2-/Update-v3-Import, Sitzung v5 und Auftrag v4; vorhandene v1–v4-Alteingänge bleiben getrennt lesbar. Beide eingebetteten Regelwerksnapshots entsprechen bytegleich ihren Markdownquellen. 0.6.0 bleibt Default, 0.7.0 ausdrücklich gewählt. Technische Nachweise und unabhängiges Review gehören an den konkreten MJ-A-PR. |
| **MJ-B / #490** | Eigener Sheetjob nach §7.6: früher Entwurf, unveränderlicher Originalrequest, fünf passende Bedienaufträge und kompakter gemeldeter historischer Abschluss. Sammlung v2 erhält reguläre und Adoptionjobs. Form-/Byteprüfung ist keine physische Datei-/Zielprüfung; HP-I1b2 bleibt der technische Werkzeugweg. |
| **BA-A / #491:** [PRODUCTION_BATCH](PRODUCTION_BATCH.md) | Lokale serielle Verarbeitung vorbereiteter Jobs mit frischer Fachprüfung, erhaltener Versuchsbuchführung und gezielter Wiederaufnahme. HP-W2-Originale und Entscheidungen unverändert, PB-H ausschließlich lokal mit vollständigem Request. Keine zusätzliche Sheetfunktion oder Integrationsfreigabe. |
| **BA-B / #491:** [PRODUCTION_BATCH](PRODUCTION_BATCH.md) | Getrennter serieller Integrationsrunner für vollständig vorbereitete und tatsächlich autorisierte `register`-/`background_adopt`-Jobs; frische native Einzelprüfung, ein Batchwriter je Zielcheckout, dauerhafte Versuche und sichere lesende Wiederaufnahme. Kein Finalizer, Gitabschluss, Retirement oder Defaultwechsel. |
| **#492** | Gesondert beauftragte Serienproduktion bleibt ein eigener Folgeumfang. Ein Werkzeugbatch ersetzt weder echte Motive noch Bild-/Inhaltsabnahmen oder deren tatsächlichen Produktionsnachweis. |

PB-H führt die zuvor explizit an **0.6.0** gebundenen Palettengates und
Paar-/Difficultyzulassungen für die **lesende Inhaltsprüfung** der neuen
Generation ausdrücklich mit. HP-I1a übernimmt diese für Export v6 und dessen
`verify_export`; HP-I1b1 öffnet ausschließlich den nach §10 frisch geprüften
Registrierungsweg mit kompatiblem Ziel. Alte Verbraucher bleiben geschlossen.
Handoff v3/0.7.0 erbt sämtliche bisherigen 0.6.0-Garantien:
frische Istpalette und Normbindung, echte Sichturteile/konkrete Ausnahme,
vollständige unabhängige Proofs, Paarbaseline und `certification`, Herkunft,
Bild-/Motiv-/Endfreigaben, feste Parameter, Randregel und Difficulty.
Ein neuer Versionsstring darf keines dieser Gates versehentlich abschalten.
Alte Exporte/Autorisierungen bleiben nach ihren eigenen Verträgen lesbar;
neue Hintergrunddaten werden nicht in v5-Altexporte eingeschmuggelt.

Aktivierung wird später in #560 mit tatsächlich funktionierendem Einzelweg,
Versionen, PRs und Commits nachgeführt. Erforderlich sind dessen benutzte
Writer/Reader, finale Integration und kompatible Runtime. Builder, Mehrjob-Sheet
und Batch sind keine pauschalen Aktivierungsgates, wenn ein anderer vollständig
unterstützter Einzelweg besteht. Das ist eine technische Lieferfeststellung,
kein zusätzliches Freigaberitual. Bis dahin bleiben gültige Altwege nutzbar;
vorbereitete neue Bildarbeit wird nicht als vollständige Integration ausgegeben.

## 9. Aufbewahrung, Abschluss und Vertragsfälle

Während Auswahl/Produktion alle noch angebotenen Einzeldateien samt Herkunft,
bekannten Generierungsdaten und tatsächlichen Belegen sichern. Nach Auswahl
nur benötigte aktive Inputs/Auslieferungsfassung weiterführen; verworfene
Alternativen dürfen über den genauen früheren gesicherten Stand referenziert
bleiben (§7.1). Keine ZIP-Verschachtelung oder dauerhaft wachsende Galerie.
Aufwand für Generierung, Fehlversuche, Alphakorrektur, Werkzeuglauf, aktive
Menschenzeit und Auswahlwartezeit getrennt im vorhandenen Authoringprotokoll;
unbekannte Zeiten `null`.

Nach bestätigter Endabnahme und tatsächlicher Main-Integration gilt
[Authoring §9](ai-workflows/PUZZLE_AUTHORING.md#9-produktionsabschluss-und-bereinigung).
Aktives PNG beziehungsweise explizite Leerbindung, Nutzungsrechte/Attribution,
kompakte echte Auswahl-/Ableitungs-/Integrationsbindungen und aktive Bildrevision
bleiben. Originale, Kandidaten, Prompts, Arbeits-ZIPs und Zwischenbelege enden
mit ihrer abgeschlossenen Produktion; keine dauerhafte Reproduzierbarkeit oder
neues Kandidatenarchiv. Historische Freigaben werden nicht umgeschrieben.
Noch offene/neuere Arbeit erhalten. Ein reiner späterer Hintergrundersatz hat
seinen eigenen revisionsgenauen Abschluss; keine Wiederherstellung gelöschter
Rasterproduktion. HP-I1b1 erweitert `retire-production` ausschließlich für die
belegte erste Integration nach §10. HP-I1b2 ergänzt Hintergrundersatz und seinen eigenen
Abschluss nach §11; `retire-reveal-production` wird kein Hintergrundwriter.

Die folgenden **synthetischen Vertragsfälle** sind keine erzeugten Bilder,
Freigaben, ausgeführten Programme oder Produktionsnachweise:

| Fall | Erwarteter Ausgang |
| --- | --- |
| Drei Dateien A/B/C offen | Manifest offered, Entscheidung null, keine Vorauswahl. Nach Motivfreigabe unabhängige Rasterarbeit zulässig; technisch fertiges Raster 0.7.0 nur `raster_ready`. |
| „B verwenden“ gemeinsam mit Motivfreigabe | Separate Entscheidung bindet B/Manifest/Profil; nur B ableiten, dieselbe Wahl über Rastervarianten erhalten. Keine zweite Bildbestätigung. |
| Späte Auswahl B plus Endabnahme am versiegelten Rasterpaket | `presented_package` bindet Originalbytes. HP-I1a ergänzt vorhandene Entscheidung/Ableitung/Endfreigabe v2 außen; Originalhandoff/-inventar/-ZIP unverändert. Exportfalse-Felder bleiben; HP-I1b1 prüft das Registrierungsziel gesondert. Fehlende/false-Capability blockiert; true folgt §13. |
| „Bewusst ohne Hintergrund“ | none mit tatsächlicher Erklärung; vor Kandidatenproduktion zusätzlich belegte Ausnahme von drei Bildern. HP-W2-Nullbefund, keine Nulltextur. |
| Gültiges 0.6.0-Altpaket ohne Hintergrund | Nach altem Vertrag lesbar, Hintergrund als Legacy eingeordnet. Keine rückwirkende Wahl, neue Pflicht oder Migration. |
| Deklarierte Quelle fehlt, Hash falsch oder Format unbekannt | Konkreter Eingangsfehler/Blocker, kein none/Legacy und keine Integration. |
| Materielle Alpha-/Kompositionskorrektur von B | Neue Bildrevision, alte Wahl/Ableitung nicht gültig für neue Bytes; nur korrigiertes Bild erneut vorlegen. Unveränderte Rasterproofs erhalten. |
| Unveränderte Ableitung oder Paketkopie | Frische passende Byte-/Profilbindung, keine zusätzliche kreative Freigabe. Wiederholung am exakten Ziel echter No-op. |
| Reine spätere Hintergrundrevision | Bild-/Paketbindungen dürfen wechseln; Matrix, Hinweise, Palette, Difficulty, Runtime-/Saveidentität und bestehende Integrationsoriginale bleiben unverändert. |

HP-W1 prüfte diese Verträge am tatsächlichen Dokumentdiff. HP-W2 ergänzt die
ausführbare Datei-/Bildfähigkeit mit kleinen synthetischen Tests für Deterministik,
Ressourcen-/Pfad-/Alpha-/Konfliktfälle; konkrete Laufnachweise gehören in seinen PR.
PB-H ergänzt kleine synthetische Paket-/Referenz-/Phasen-/Inhaltsfälle;
HP-I1a ergänzt Finalizer-/No-op-/Unterbrechungs-/Transportfälle und die enge
Verify-Regel. HP-I1b1 prüft Registrierung, Quellen-/Recoverybindung und Abschluss
an kleinen synthetischen Fällen. Konkrete Laufnachweise gehören in die jeweiligen
PRs; Runtime folgt HP-I2, Bildersetzung folgt §11 und drei reale erreichbare
Bilddateien einem gesonderten Produktionsauftrag. Diese Teilpakete schließen
weder #560, #561 noch den Gesamtplan #563.

### 9.1 Vollständiges synthetisches Formbeispiel: früher bewusster Verzicht

Die folgenden zwei JSON-Objekte zeigen alle Pflichtschlüssel einschließlich
Nullfelder für diesen Fall. **Akteur, Erklärung, Zeitpunkt, Bytezahlen und
Hashes sind ausdrücklich erfundene Beispieldaten.** Die wiederholten `e`-/`b`-
Hashes sind Platzhalter, keine geprüften Dateihashes. Es existiert kein damit
behaupteter Eigentümerbeleg; die Objekte sind ohne echte Dateien/Hashes kein
gültiger HP-W2-Eingang. `test_only=true` verhindert ihre Verwendung als reale
Produktion. Ein ausführbares synthetisches Fixture muss ebenfalls seine eigenen
tatsächlichen Testdateien hashen.

Arbeitsmanifest unter `work/bg01.json`, relativ zu einer ausdrücklich gewählten
Arbeitswurzel. Die gleiche synthetische Erklärung belegt hier die Ausnahme von
der anfänglichen Kandidatenproduktion und anschließend die Leerentscheidung:

```json
{
  "format": "picross-background-work-v1",
  "puzzle_id": "pz-hp-example",
  "job_id": "job-hp-example",
  "revision": "bg01",
  "created_utc": "2026-01-01T12:00:00Z",
  "context": {
    "summary": "Synthetischer Kontext für eine Formdemonstration.",
    "protected_features": [],
    "excluded_subjects": [],
    "reveal": null,
    "reveal_approval": null
  },
  "briefing": "Synthetisches Beispiel ohne Hintergrundproduktion.",
  "candidate_policy": {
    "count": 0,
    "exception": {
      "actor": "Synthetischer Beispielakteur",
      "timestamp_utc": "2026-01-01T12:00:00Z",
      "statement": "Für dieses synthetische Beispiel bewusst keinen Hintergrund und keine drei Kandidaten erstellen.",
      "evidence": {
        "file": "evidence/none01.txt",
        "sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "bytes": 123
      }
    }
  },
  "presentation": {"status": "pending", "evidence": null},
  "candidates": [],
  "test_only": true
}
```

Getrennte Entscheidung unter `decisions/d01.json`; ihr Manifestref benutzt
denselben relativen Arbeitswurzelpfad und bindet in echter Verarbeitung dessen
tatsächliche vollständige Bytes einschließlich der Ausnahme:

```json
{
  "format": "picross-background-decision-v1",
  "puzzle_id": "pz-hp-example",
  "job_id": "job-hp-example",
  "revision": "d01",
  "background_revision": "bg01",
  "manifest": {
    "file": "work/bg01.json",
    "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "bytes": 1234
  },
  "outcome": "none",
  "candidate_id": null,
  "original": null,
  "profile": null,
  "actor": "Synthetischer Beispielakteur",
  "timestamp_utc": "2026-01-01T12:00:00Z",
  "statement": "Für dieses synthetische Beispiel bewusst keinen Hintergrund und keine drei Kandidaten erstellen.",
  "evidence": {
    "file": "evidence/none01.txt",
    "sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "bytes": 123
  },
  "presented_package": null,
  "previous_decision": null,
  "carried_from": null,
  "accepted_deviations": [],
  "test_only": true
}
```

## 10. HP-I1b1 · Erste Registrierung und kompakter Produktionsabschluss

Vertrag vor konsumierendem Code, 09.11.2026, Paketentscheidung
[HP-I1b1 / #561](https://github.com/venomenon328/picross/issues/561#issuecomment-6754303684). Die Basis ist
`045189cc5ef34eaf4d06823f22f7ec811d209de5`; HP-I1a ist über PR #567 integriert.
Dieser Abschnitt öffnet nur die erste Registrierung und ihren Abschluss.
Die Typen, kanonischen Bytes und Hashfunktionen aus §3.1 gelten unverändert;
alle folgenden Feldmengen sind geschlossen, Boolean ist kein Integer.
Transaktionen und gespeicherte Pläne stehen ergänzend in
[SD-Catalog](SD_CATALOG.md#hp-i1b1--hintergrundquellen-pläne-und-transaktionen),
Aufrufe in [ZA-1](ZA1_ADAPTER.md#hp-i1b1--zielgebundene-erste-registrierung).

Für den vollständigen dateibasierten v6-Transport darf ausschließlich ein
unbenötigtes leeres `external/` fehlen: keine externe Ref und keine externe
Inventardatei. `input.external_root` bleibt `external`; Git und Journal müssen
keinen leeren Ordner oder Dummyfile transportieren. Benötigte externe Roots/
Dateien bleiben Pflicht, sonstige ungebundene Leerordner bleiben unzulässig.

### 10.1 Feste Zielkompatibilität

`game/data/background-capability.json` hat exakt
`format,runtime_format,profile_id,enabled`: Format
`picross-runtime-background-capability-v1`, Runtimeformat
`picross-runtime-registry-v6`, Profil `picross-background-png2304-v1` und
Boolean `enabled`. Datei höchstens 4096 Bytes, sichere reguläre UTF-8-JSON-Datei
nach §3.1. Fehlend oder false bedeutet fehlende kompatible Hintergrund-Runtime;
Hintergrundplanung und Registrierung stoppen vor Journal und Katalogmutation.
Ungültige Formen, Kennungen, Typen oder Pfade sind Eingabefehler.

**HP-I1b1 allein belässt `enabled=false`.** HP-I2 darf true erst gemeinsam
mit tatsächlichem Runtime-Reader, Darstellung/Laden, Import-/Lieferweg und
technischer Abnahme nach §13 liefern. Kein CLI-/API-/Umgebungs-Override, kein `force` und kein Aktivieren
durch `--allow-background`; letzteres lässt lediglich das Eingangsformat zu.
Isolierte synthetische Ziele dürfen true mit test_only-Eingängen verwenden,
ohne damit Spielerverhalten oder eine Bildabnahme zu belegen. Synthetische
Inhalte bleiben im echten Katalog verboten.

Neue Pläne/Journale binden die exakten Capabilitybytes oder ihre ausdrückliche
Abwesenheit; Änderung macht den Snapshot stale. Ein vorhandener Hintergrundkatalog
ohne aktive gültige Capability blockiert neue Mutationen, ohne Downgrade nach v5.
Gültige Legacy-only-Kataloge behalten Runtime-v5. Die HP-I1a-Exportfelder bleiben
unverändert false; erst frische zielbezogene Prüfung außerhalb des Manifests
ermittelt Bereitschaft. `registered` bedeutet abgeschlossenen Checkoutlauf,
Integration auf main weiterhin bestätigten Merge. Keine Neuversiegelung von
Original, Finalizerrecord oder Approval.

### 10.2 Registry und aktive kompakte Quelle

`picross-content-registry-v3` hat exakt `format,entries,backgrounds`.
`entries` behält den vollständigen bestehenden Registry-v2-Eintragsvertrag
einschließlich `production`. `backgrounds` ist eine nach ID sortierte eindeutige
Liste aus exakt `{id,source}`. Die ID bezeichnet einen vorhandenen Entry;
`source:Ref` bindet ausschließlich `content/backgrounds/<id>.json` mit echtem
Dateihash und Bytezahl. Jeder neue v6-Export erhält eine Zeile, auch bei none.
Fehlen ist ausschließlich für nach altem Export-/Receiptvertrag gültige
Legacyeinträge zulässig. Die erste Hintergrundregistrierung hebt nur die
Wurzelgeneration an; vorhandene Entryobjekte und ihre Entscheidungen bleiben.
Keine automatische Bestandsmigration oder erfundene Legacy-Leerentscheidung.

`picross-catalog-background-v1` hat exakt
`format,puzzle_id,identity,origin,image_revision,candidate_revision,decision,
derivation,provenance,review,asset,notice,test_only`.

| Feld | Exakter Inhalt und Bindung |
| --- | --- |
| `puzzle_id` | Registrierte `PuzzleID`, identisch zu Entry, Ursprung, Entscheidung und Ableitung. |
| `identity` | Exakt `{key,save_slot,definition,runtime_revision}`. Key/Slot wie Entry; `definition:Ref` bindet `game/<entry.definition>` und echte Livebytes, numerische Rätselrevision wie Definition. Keine Kategorie-/Added-/Ratingkopie. |
| `origin` | Exakt `{package,export_manifest_sha256,original_package,manifest,approval_ref,approval}`. `package` ist der ursprüngliche `content/packages/<id>/<revision>`-Pfad; Exporthash bindet das ursprüngliche v6-Manifest. `original_package:PackageBinding`, `manifest:StoredRef` aus der ursprünglichen geprüften Hintergrundbindung; `approval_ref:Ref` bindet die ursprünglichen `approval.json`-Bytes. `approval` ist das vollständige unveränderte Approval-v2-Objekt. Dieser Ursprung ist vom späteren physischen Receipthash getrennt. |
| `image_revision` | Positive technische Integerrevision, bei erster Integration genau `1`. Sie identifiziert den aktiven Bild-/Leerzustand für die Runtime und erzeugt keine menschliche Erklärung. Spätere tatsächlich andere aktive Übernahme benötigt HP-I1b2. |
| `candidate_revision` | Bei selected die tatsächliche unveränderte Kandidatenrevision vom Typ `Revision`, bei none null. Gleiche Zeichenketten aus verschiedenen Jobs sind keine identische aktive Übernahme. |
| `decision`, `derivation` | Vollständige unveränderte `picross-background-decision-v1` und `picross-background-derivation-v1`: reale Akteure, UTC, Wortlaut, Auswahl/Verzicht, Arbeits-/Entscheidungsrevisionen, Original-/Profil-/Tool-/Ausgabebindungen bleiben. |
| `provenance`, `review` | Bei selected exakt Herkunfts-/Rechteobjekt und die vier Q-HG-Urteile der gewählten Manifestzeile; bei none beide null. Keine Alternativen oder Prompts. |
| `asset`, `notice` | Bei selected `Ref` genau auf `game/art/backgrounds/<id>.png` und `game/art/backgrounds/<id>.txt`; bytegleich zu den frisch geprüften v6-Runtimeausgaben. Bei none beide null, keine Nulltextur oder leere Ersatznotice. |
| `test_only` | Exakt wie die geprüften Eingänge und die Registryproduktion. |

ID-/Job-/Revisions-, Auswahl-/Outcome-/Profil-/Approval- und Ausgabehashbindungen
müssen zusammenpassen. Die Hintergrundübernahme ändert weder Definition,
Runtime-Rätselrevision, Slot, Lösung, Hinweise, Palette noch Difficultyidentität.
Der Dateihash steht im äußeren Ref; kein Selbsthashfeld. Quelle höchstens
1 MiB, JSON-Tiefe höchstens 32. Inhaltsregistry und Runtime behalten 8 MiB und
10000 Entries; höchstens eine Hintergrundzeile pro Entry. Unbekannte Felder,
unerwartete Nullwerte und defekte deklarierte Quellen sind Fehler, kein Fallback.

Die Source entsteht ausschließlich aus vollständig frisch geprüfter
Erstintegration. Sie ist kein alternativer Export-/Zertifizierungseingang.
Vor Retirement müssen die ursprünglichen Paketinputs weiterhin die vollständige
normale Prüfung bestehen. Nach zulässigem Retirement sind innere alte Dateirefs
historische Identitäten, keine erneut zu öffnenden Arbeitsdateien. Reader prüfen
geschlossene Formen, interne Kreuzbindungen, Rechte, unveränderten Ursprung und
echte Livehashes anhand von Receipt, Index und aktiver Source. Sie behaupten keine
erneute Bild-/Proof-/Solverreproduktion und rufen dafür keinen alten Dateivalidator
auf. Kein dauerhaftes Original-ZIP, Kandidaten- oder Ableitungscodearchiv.
Der spätere Mainbeleg gehört in den Receipt, nicht in eine umgeschriebene Source.

### 10.3 Receipt und Runtimeprojektion

`picross-integrated-content-v2` hat exakt
`format,entry,integrated_commit,notice_sha256,background`.
Die vier alten Felder behalten ihre v1-Bedeutung. `background` ist exakt
`{origin_sha256,source}`: `origin_sha256=H(Source.origin)`, `source:Ref` bindet
die beim ersten Abschluss tatsächliche kompakte Source. HP-I1b1 verlangt dieselbe
Sourcebindung im aktuellen Hintergrundindex. `entry` bewahrt den ursprünglichen
Exportmanifesthash; der aktuelle `production.package_sha256` bindet anschließend
die echten Receiptbytes. V1 bleibt unverändert, Hintergrundproduktionen dürfen
nicht in v1 schrumpfen. Für Source v2 erweitert §11.2 diesen Vergleich ausdrücklich: der ursprüngliche
Receipt bindet initial, der aktuelle Registryref bindet die vollständige v2.
Der geschlossene Source-v1-Vertrag bleibt unverändert.

`picross-runtime-registry-v6` hat exakt `format,categories,entries`. Jeder
Eintrag behält die neun v5-Felder und ergänzt genau `background` mit exakt
`{status,image_revision,asset}`:

| Zustand | `status` | `image_revision` | `asset` |
| --- | --- | --- | --- |
| Gültiger alter Entry ohne Hintergrunddeklaration | `legacy` | null | null |
| Ausdrücklich leer | `none` | Positive aktive Integerrevision aus der Source | null |
| Gewählte Illustration | `selected` | Positive aktive Integerrevision aus der Source | `Ref`, festes `file="art/backgrounds/<id>.png"`, echte Größe/Hash der aktiven Source |

Keine Freigabetexte, Produktionsoriginale, Alternativen oder individuellen
Positionsangaben im Runtimekatalog. Defekte deklarierte Quellen erzeugen keinen
gültigen Leer-/Legacyzustand. V6 nur im kompatiblen Ziel; Godot-Reader, Darstellung A,
Mipmaps und Laden folgen dem HP-I2-Vertrag §13. Kein Werkzeugpaket migriert den
echten Katalog oder ersetzt die technische Runtimeabnahme.

### 10.4 Gemeinsame Verbraucher und erste Abschlussgrenze

Alle Full-/Quick-/API-/CLI-Verbraucher erhalten dieselbe aktive Autorität:
`content_registry`, `catalog_integration`, `catalog_transaction/publication`,
`registration_publication/verification`, `integrated_content`, `content_update`,
`catalog_reveal/reveal_source/reveal_retirement` und Rating-/Added-/Methodenpläne.
Zulässige Metadatenoperationen und Legacyziel-Update/-Revealadoption im gemischten
Katalog erhalten Hintergründe vollständig. Freie Kategorienumklassifizierung
historisch gebundener Entries/Receipts wird nicht eröffnet. Der HP-I1b1-
Grundvertrag blockiert Rasterupdate und Revealadoption eines Hintergrundziels
vor Planung oder Mutation, auch durch indirekte Aufrufe. Ausschließlich die
versionierte HP-I1c-Neubindung nach §12 öffnet diese Zieloperationen.

Erneute identische v6-Registrierung vor und nach Retirement ist nach frischer
passender Eingangs-/Checkoutprüfung ein Byte-/mtime-No-op. Der ursprüngliche
Exportanker bleibt Vergleichsgrundlage; der physische Receiptwechsel ist keine
neue Produktion. Keine alten ZIPs zurückschreiben, keine Added-Neudatierung,
keine neue Revision oder Spielidentität.

`retire-production` prüft den tatsächlichen vollständigen Main-Commit und seine
Abstammung zum aktualisierten `origin/main`. Vor dem ersten Entfernen alle
ausgewählten IDs, Arbeits-/Quellbytes und Hintergrundindex/-Source, Asset/none
und Notice gegen den bestätigten Main-Stand prüfen. Receipt v2 bewahrt den
Ursprung. Definition, Reveal, Hintergrund, Rechte, kompakte echte Auswahl-/
Ableitungs-/Freigabebindungen, Rating, Added und Runtime bleiben erhalten.

Nur belegte abgeschlossene Arbeit entfernen. Neuere/offene Geschwister, fremde
Änderungen und unbekannte Dateien erhalten; ist der ID-Baum nicht sicher trennbar,
vor Mutation konkret blockieren. Kein pauschales Löschen aller Hintergrundarbeit
und kein Wiederherstellen alter Rasterproduktion. Derselbe vollständig beendete
Zustand mit demselben Mainbeleg ist nach Prüfung No-op. Bei Teilfehlern tatsächliche
Reste benennen, keinen Erfolg behaupten. Der Befehl erzeugt einen überprüfbaren
lokalen Diff und führt weder Commit noch Merge aus. Die Authoring-Cleanupfreigabe
erteilt keine Mergefreigabe für dieses Werkzeugpaket.

## 11. HP-I1b2 · Eigenständiger Hintergrundwechsel

Vertrag vor konsumierendem Code, 10.11.2026, [Paketentscheidung HP-I1b2](https://github.com/venomenon328/picross/issues/561#issuecomment-6763700809), Basis `d28e015b701f07bceb847245fdde16a522868a44`.
Dieser Abschnitt ergänzt §10 ausdrücklich um den eigenen Änderungsweg für genau
ein bereits gültig hintergrundgebundenes Ziel. Die unveränderten §3.1-Typen gelten
für alle geschlossenen Formen; alte Generationen behalten ihre exakten Regeln.
selected→selected, selected→none und none→selected sind erlaubt. Legacy-Nachrüstung
bleibt gesperrt. Rasterupdate und Revealadoption benötigen den Rebind-Vertrag HP-I1c
in §12; Runtime/Import/Mipmaps/Laden gehören zu HP-I2. Keine reale
Bildproduktion, Katalogänderung, zusätzliche Eigentümerbestätigung oder Buchprobe.

Konkrete Grenzen: Request/Manifest/Entscheidung/Befund je 2 MiB, Source 1 MiB,
JSON-Tiefe 32; höchstens 20 Kandidaten, 64 Parameter bzw. Einträge je übriger
HP-W2-Liste und 256 Dateien/96 MiB im gebundenen Arbeitsgraph. Quellen-PNG
32 MiB, höchstens 8192 je Achse und 8.000.000 Pixel. Das Requestinventar darf
256 Dateien/96 MiB umfassen; der vollständige Plan zusätzlich genau die alte
PNG-Seite (32 MiB), höchstens 128 MiB Nutzdateien. Plan-JSON höchstens 24 MiB;
bei Überschreitung vor Mutation abbrechen. Plan-/Bildoperation/Recovery je
endlicher kooperativer Rahmen 300 s; keine RI-B/C-Ausdehnung oder Budgeterhöhung.
Die Binärjournalgrenzen unten sind ausschließlich für dessen neue Formatkennung.

### 11.1 Eigenständiger unveränderlicher Arbeitsauftrag

Die bisherige Raster-Record-v2-/Approval-v2-Form benötigt Original-ZIP/Handoff/Inventar und wird **nicht** für nachträgliche Bildarbeit umgedeutet. Eine neue Arbeitsrevision verwendet den bestehenden Pfad
`content/authoring/<puzzle_id>/<revision>/record.json`
mit **`picross-background-adoption-request-v1`**. Das ist zugleich unveränderlicher Auftrag und Arbeitsrecord; kein Dummy-ZIP, keine zweite gleichlautende Approvaldatei und kein späteres Umschreiben in einen vermeintlichen Rasterstatus.

Exakte Top-Level-Felder: `format,puzzle_id,revision,target,background,authorization,files,test_only`.

| Feld | Geschlossener Vertrag |
| --- | --- |
| `puzzle_id,revision,test_only` | Bestehende PuzzleID/Revision/Boolean-Typen. Eigene kollisionsfreie Authoringrevision, etwa `bg-r01`; kein Überschreiben bestehender Arbeit. test_only stimmt mit Ziel, Manifest, Entscheidung und Ableitung überein. |
| `target` | Exakt `{source,origin_sha256,image_revision}`. source ist der tatsächliche Ref der unmittelbar vorherigen vollständigen aktiven Source am festen Pfad `content/backgrounds/<id>.json`; origin_sha256 bindet deren unveränderten Erstursprung; image_revision ist ihre aktive positive Integerrevision. Die Source bindet zusätzlich die vollständige unveränderte Rätselidentität. |
| `background` | Bestehendes BackgroundBinding mit exakt `manifest,decision,derivation,history`. Alle drei StoredRefs sind nichtnull und ausschließlich `storage=external`; der explizite äußere Root ist die Checkoutwurzel, sämtliche Root/Ref-Kombinationen liegen innerhalb genau dieser Arbeitsrevision. history ist hier null. Vollständige benötigte Dateien einschließlich angebotener Kandidaten und Belege bleiben bis zu diesem revisionsgenauen Abschluss vorhanden; kein Paketstorage/ZIP oder impliziter historischer Fetch. |
| `authorization` | Bestehendes Human-Objekt `{actor,timestamp_utc,statement,evidence}`, mit tatsächlich erklärtem Wechsel dieses Ziels zu genau der gebundenen Auswahl/Leerentscheidung. Derselbe tatsächliche Auswahl-/Entfernungsauftrag darf zugleich Entscheidung und Autorisierung belegen. evidence ist relativ zur Arbeitsrevision. Kein approved-Flag und kein erfundener Akteur/Zeitpunkt. |
| `files` | Sortierte eindeutige Ref-Liste aller Dateien dieser Arbeitsrevision außer record.json selbst. Refs sind relativ zur Revision; sie erfassen auch alle Entscheidungs-/Rechte-/Sicht-/Kontextbelege und den vollständigen HP-W2-Ausgabeordner. Keine Globs, Selbstreferenzen, fremden Dateien, Links, Alias- oder Datei-/Verzeichniskollisionen. |
| `format` | Exakt `picross-background-adoption-request-v1`; unbekannte Felder/Versionen und falsche Null-/Scalarformen sind Fehler. |

Vorhandene Ref-/StoredRef-/Human-/kanonische JSON-, Pfad-, Datei-/Gesamt-/Pixel-/Zeitgrenzen weiterverwenden und die konkret angewandten Grenzwerte im Normtext nennen; keine generelle Größen- oder Zeitlockerung. Record höchstens 2 MiB. Der vorhandene Authoringindex v1 behält seine exakten Zeilen `{puzzle_id,revision,record}`; zuständige Reader erkennen die neue Arbeitsfamilie ausdrücklich, bewahren andere Zeilen und interpretieren sie nicht als Rasterrecord. MJ-B führt diese eigene Familie im Offline-Sheet nach §7.6; der reguläre MJ-A-Record-/Rasterpfad bleibt getrennt. Verbindliche Erstablage/Indexpflege und konkrete CLI/API in der Werkzeuganleitung dokumentieren; keine automatische Bildproduktion oder menschliche Freigabe durch einen Writer.

**Kontext nach ursprünglichem Retirement:** Eine neue Bildvorlage darf nicht die gelöschte alte Reveal-Freigabedatei voraussetzen. In der neuen Arbeitsrevision werden die aktuell gültige Hintergrundsource und das unveränderte aktuelle Live-Reveal byteidentisch als ausdrücklich gebundene Kontextbelege gesichert. `context.reveal` bindet diese Reveal-Kopie; `context.reveal_approval` darf für genau diesen neuen Änderungsweg die Kopie der kompakten aktiven Source als erhaltene echte Freigabeautorität binden. Der Reader prüft deren Bytegleichheit mit target.source, den unveränderten Ursprung/Identität und den Revealhash der ursprünglichen `origin.approval.selection.reveal` gegen Entry und aktuelle Live-/Kopiebytes. Der ursprüngliche Reveal-Dateiname muss nicht dem Runtimepfad gleichen. Es wird keine gelöschte Approvaldatei rekonstruiert und keine neue Revealfreigabe erfunden. Diese enge Auslegung gilt ausschließlich im nachfolgend gebundenen Änderungsweg; keine allgemeine Absenkung der HP-W1-Kontextbindung.

Ein neuer unabhängiger Hintergrundjob darf `previous_decision=null` verwenden; sein Austauschvorgänger ist target.source. Innerhalb desselben noch vorhandenen Jobs gelten die bisherigen wirklichen Vorgänger-/carried_from-Regeln weiter. Keine Wiederherstellung bereinigter Entscheidungsgraphen allein für einen neuen Job.

### 11.2 Aktive Source v2 und unveränderter Erstursprung

Neue **`picross-catalog-background-v2`**, exakt `{format,initial,current}`.

- `initial` enthält genau das vollständige unveränderte Source-v1-Objekt der Erstintegration, niemals eine eingebettete v2. Bei v1→v2 wird dessen kanonischer Inhalt übernommen; bei v2→v2 bleibt derselbe initial-Teil erhalten. Die bereits vorgeschriebenen kanonischen JSON-plus-LF-Bytes erlauben den ursprünglichen tatsächlichen Sourceref ohne Reproduktion alter Bilddateien zu prüfen.
- ID, identity, origin und test_only kommen ausschließlich aus initial. Kein zweiter widersprüchlicher Identitäts-/Ursprungsblock.
- `current` hat exakt `image_revision,candidate_revision,decision,derivation,provenance,review,asset,notice,adoption`. Die ersten acht Felder verwenden die vorhandenen selected/none-Typen und Kreuzbindungen, nun zur tatsächlich aktuellen Wahl. decision/derivation und tatsächliche Herkunft/Q-HG-Urteile unverändert übernehmen; bei none gelten die bisherigen Nullregeln. Feste Livepfade bleiben `game/art/backgrounds/<id>.png` und `.txt`.
- `adoption` hat exakt `{request,revision,target,background,authorization}`: request ist der Ref auf den unveränderlichen obigen record.json am festen Repositorypfad; die übrigen Felder sind die tatsächlich geprüften unveränderten Requestwerte. Keine komplette Kandidatenliste, kein voller Dateiinventarblock und keine rekursiv eingebetteten Vorläuferquellen. Historische Refbindungen bleiben nach Cleanup historische Identitäten.
- Eine tatsächlich neue aktive Auswahl-/Leer-/Rechtebindung erhält `image_revision=target.image_revision+1`, maximal die bestehende Obergrenze. Dieselben PNGbytes allein sind kein Identitätsbeweis für verschiedene Jobs/Freigaben. Eine identische Wiederholung desselben vollständig gebundenen Auftrags erhöht nichts. Keine inhaltslose none→none-Neurevision; die unveränderte bereits übernommene Leerentscheidung kann nur als geprüfte Wiederholung zurückgemeldet werden.
- Die bestehende 1-MiB-Sourcegrenze bleibt. Übergroße Source/Plan-/Journaldaten vor Mutation ablehnen; keine wachsende Historien- oder Bildgalerie.

**Registry v3 und Runtime v6 behalten ihre Feldmengen.** Der Registryref bindet die vollständige aktuelle v1/v2-Datei; Runtime projiziert den wirksamen aktuellen selected/none-Zustand mit dessen technischer Bildrevision. Ein gemeinsamer Reader bestimmt initial/aktuellen Stand für alle Full-/Quick-/API-/CLI-Verbraucher.

**Receipt v2 und ursprüngliches Produktionsergebnis behalten ihre historische Aussage.** Bei bereits beendeter Rasterproduktion bleiben Receiptbytes und `production.package_sha256` durch die Bildoperation unverändert. `receipt.background.origin_sha256` bindet initial.origin; `receipt.background.source` bindet den kanonischen ursprünglichen initial-v1-Ref, während der aktuelle Registryref v2 bindet. Das ist ein ausdrücklich versionierter Vergleich, keine Aufweichung des v1-Vertrags. Bei noch vollständigem v6-Export wird initial gegen dessen ursprüngliche geprüfte Projektion geprüft. Nach Retirement werden historische Refs nicht als wieder zu öffnende Original-/ZIP-/PNGdateien behandelt; aktuelle Livebytes werden gegen current geprüft.

Erneute ursprüngliche v6-Registrierung bleibt nach frischer passender Prüfung des Ursprungs und des gültigen aktuellen Zielstands ein echter No-op und darf nach Bildwechsel niemals das alte Bild oder alte Source zurückschreiben. Der ursprüngliche `retire-production`-Weg muss auch bei gültiger v2-Source seinen Receipt auf initial binden, den tatsächlichen aktuellen Source-/Live-/Mainstand prüfen und neuere Hintergrundarbeit erhalten oder vor Mutation konkret blockieren. Das ist Verbraucherkonsistenz, kein zweiter Bildwechselwriter.

### 11.3 Plan, Übernahme und Zielgrenze

Eigener fachlicher Einstieg für Hintergrundänderungen, `python -m tools.puzzle_production.catalog_background_change plan ...` /
`adopt ...`; gemeinsame sichere I/O-, Quellen-, Lock-, Publikations- und Recoveryimplementierung verwenden. Reveal-/Rasterbefehle erhalten ihre Bedeutung. Genau ein Ziel pro Übernahme; Batchorchestrierung bleibt #491.

Planung ist gegenüber dem Checkout lesend. Sie prüft aktuelle Zielsource/Origin/Identität, vollständige Arbeitsrevision und echte Autorisierung sowie die neue Wahl/Rechte/Q-HG und frisch reproduzierte HP-W2-Ausgabe/none. Geschriebenen Planbundle ebenfalls frisch prüfen und ohne Ersetzen an ausdrücklich gewähltem sicherem Ort außerhalb des Checkouts publizieren. Kein geplanter Erfolg ist eine Übernahme.

Neue **`picross-background-adoption-plan-v1`**, exakt
`{format,request,snapshot,old,new,files,plan_hash}`:

- request: Ref auf die unveränderten Requestbytes im Bundle unter `input/content/authoring/<id>/<revision>/record.json`; `input/` ist dessen expliziter externer Repositoryroot. Alle ursprünglichen inneren Root-/Refwerte bleiben unverändert.
- snapshot: bestehende vollständige Form `{sources,namespaces}`, einschließlich aller Katalogquellen, Capability/Abwesenheit, aktiven Hintergründe und sechs Namespaces. Kein ausgewählter Einzelhash als Ersatz für den Gesamtsnapshot.
- old/new: vollständige hergeleitete, gleichschlüsselige Textansichten T mit UTF-8-String oder null wie im Journal. Nur die unten erlaubten aktiven Deltas.
- files: exaktes sortiertes Ref-Inventar des gesamten Bundles außer plan.json. Es enthält die unveränderte Arbeitsrevision unter input/ und, falls vorhanden, die alte PNG-Rollbackseite unter `previous/background.png`. Die neue Bildseite stammt unmittelbar aus dem gebundenen HP-W2-Ausgabeordner unter input/, ohne zusätzliche Bildkopie. Keine Datei bei einer null-Seite.
- plan_hash: H der übrigen sechs Felder nach vorhandener kanonischer Funktion. Keine selbstbezogene Hashberechnung.

Adopt liest Bundlebytes frisch, validiert alle geschlossenen Formen/Inventare, rekonstruiert die vollständige alte und neue Ansicht und leitet den Plan unabhängig erneut her. Ein selbst erklärter Planhash/„verified“ genügt nicht. Vor einer neuen Mutation müssen außerdem die gebundene aktuelle Authoringrevision, alle Request-/Inventarbytes und die ausgewählte Indexzeile unverändert vorhanden sein: bei der Eingangsprüfung und erneut unter der exklusiven Kataloglockeigentümerschaft unmittelbar vor erster aktiver Mutation. Das Bundle bleibt über den ganzen Lauf frisch bytegebunden; andere Indexzeilen werden nicht geschrieben. Ein alter abgelegter Plan überschreibt keine inzwischen neu entschiedene Arbeit. Quellenwechsel, Zusatzdateien, anderes Ziel oder andere Capability machen ihn stale.

**Wiederholung:** Nur der exakt eigene vollständige Zielstand ist No-op, ohne Byte-/mtime-, Authoring-/Index-, Bildrevisions- oder Added-Änderung. Dazu aktuelle aktive Source/request-Bindung, gesamte gültige Zielansicht und die im Plan exakt erlaubten Eigenänderungen prüfen. Nach regulärem revisionsgenauem Main-Abschluss darf eine identische noch vorliegende vollständige Planlieferung nur diesen bereits übernommenen Zustand erkennen; ihre inzwischen ordnungsgemäß entfernte Arbeitsrevision wird nicht zurückgeschrieben. Dafür erhält adopt ein optionales API-/CLI-Argument `integrated_commit` / `--integrated-commit <vollständige SHA>`, das bei fehlender Arbeitsrevision zwingend ist und ausschließlich diesen No-op-Pfad zulässt: Commit ist Vorfahr des aktualisierten origin/main und lokalen HEAD, enthält den exakten Request samt Indexzeile und dessen wirkliche Source-/Liveübernahme; der aktuelle vollständige Zielzustand passt weiterhin exakt dazu, komplette Arbeitsrevision und ihre Indexzeile fehlen. Teilreste, geänderte Arbeit oder eine neuere aktive Bildrevision sind kein No-op. Ohne passenden Mainbeleg ist fehlende Arbeit ein Fehler; der Sonderpfad darf niemals publizieren oder Arbeit wiederherstellen. Ohne erhaltenes Planbundle müssen keine alten Arbeitsdateien rekonstruiert werden: der kompakte aktive Stand bleibt über Source/Receipt lesbar; `retire-background-production` hat seine eigene wiederholbare Prüfung. Keine Pflicht, Planbundle dauerhaft aufzubewahren. Der ursprüngliche `retire-production`-Paket-/Receiptwechsel ist dagegen eine andere aktive Katalogmutation und macht zuvor gebaute Hintergrundpläne stale, auch für deren No-op-Pfad. „Vor und nach ursprünglichem Retirement nutzbar“ meint jeweils frisch auf dem tatsächlichen Ausgangsstand geplante Bildoperationen; keine automatische Normalisierung eines alten Plans über den Receiptwechsel. Der bereits gültige kompakte aktuelle Bildstand bleibt lesbar, ohne eine neue Mutation oder Rekonstruktion alter Arbeit.

**BA-B: additive lesende Diagnose und spätere Batchjobs.**
[BA-B / #491](https://github.com/venomenon328/picross/issues/491#issuecomment-6782256272)
ergänzt ausschließlich die Pythonoption `adopt(..., no_op_only=True)`, ohne
neuen nativen CLI-Befehl. Sie prüft mit dem ursprünglichen vollständigen
Planbundle denselben nativen eigenen No-op. Ist dieser nicht vollständig
belegt, verwirft derselbe Kontrollfluss den Aufruf vor jeder Publikation;
ein getrennter Vorabcheck mit anschließend allgemeinem Adopt wäre unzureichend.
Plan-/Quellen-/Namespace-/Journalprüfungen und obige Main-/Retirementgrenzen
bleiben erhalten. Dieser Weg dient einem nativ abgeschlossenen Bildwechsel,
dessen Batchabschluss wegen Unterbrechung noch nicht gebucht ist.

Bei bereits dauerhaft gebuchtem Erfolg und anschließend erfolgreichen weiteren
Batchjobs ist der alte vollständige Bildplansnapshot dagegen gewöhnlich stale.
BA-B ruft ihn nicht erneut auf. Es erhält den historischen Erfolg, prüft einmal
den heutigen vollständigen Katalog über den gemeinsamen Reader und vergleicht
jobbezogen die tatsächlich erreichten Source-/Request-/Revisions-/PNG-/Notice-
bindungen. Das ist die eigene rein lesende Batchabstimmung nach
[PRODUCTION_BATCH](PRODUCTION_BATCH.md), kein gelockerter nativer No-op und
kein Zurücksetzen späterer Änderungen. Fehlende, fremde oder teilweise passende
Bytes stoppen; abgeschlossene entfernte Arbeit wird nicht rekonstruiert.

HP-I1b2 allein aktiviert die echte `game/data/background-capability.json` nicht.
Fehlend/false stoppt Planung und Mutation, ungültige Form ist Eingabefehler;
Wechsel invalidiert Plan/Recovery. Kein CLI/API/Environment-Override. Isolierte
synthetische kompatible test_only-Ziele belegen nur den Werkzeugweg. Die echte
Runtimefähigkeit folgt HP-I2 nach §13; Exportfalse-Felder, aktiver
Authoringdefault und echte Kataloginhalte bleiben unverändert.

### 11.4 Binärmutation und Rollback im gemeinsamen Writer

Neue **`picross-background-adoption-journal-v1`**, `operation="background-adoption"`, exakt bestehende acht Top-Level-Felder
`format,operation,old,new,retained,additions,report_run,replacements`.
`additions={}`, `report_run=null`. Alle Binärwechsel dieser Operation stehen in replacements; Notice/Source/Registry/Runtime sind Textansichten.

Erlaubtes Delta: genau eine aktive Hintergrundsource, ihr Registryref, ihre Live-PNG/Notice beziehungsweise deren ausdrücklich erwartete Abwesenheit und das entsprechende Runtime-background-Feld. Registry-Entryobjekte, ursprüngliches Paket/Receipt, Definition, Reveal/Revealnotice, Rating/Added und alle übrigen Quellen bleiben unverändert. Keine neue aktive Pfadfamilie.

replacements hat ausschließlich den festen PNG-Pfad des gewählten Ziels, wenn seine Bytes/Existenz tatsächlich wechseln. Paar exakt `{old,new}`; jede Seite ist der bestehende gebundene Binärdatensatz `{sha256,bytes,base64}` **oder null**. Mindestens eine Seite nichtnull, keine gleichen Binärseiten. Bei unveränderter PNG-Seite, etwa tatsächlich neu autorisierter Herkunftsbindung derselben Bytes, bleibt sie vollständig retained und replacements ist leer. None ist exakte erwartete Abwesenheit, keine Erlaubnis zur Fremddateilöschung. Altjournale behalten ihre geschlossenen Form-/Delta-/Nichtnullregeln.

Die neue Kennung ausdrücklich in Journalgrößenklassifikation, Wirelayout, Guards, Staging und Recoverydispatch berücksichtigen: bestehende 32-MiB-Binärseiten-, 96-MiB-Gesamt- und 128-MiB-Binärjournalgrenzen verwenden; gewöhnliche Journale nicht global vergrößern. Den bisherigen engen Original-ZIP-Sonderfall nicht auf Hintergrunddateien ausdehnen.

Vollständige T/K-Quellen, Capability, negative Erwartungen und alle sechs Namespaces prüfen; gemeinsame exklusive Lockeigentümerschaft; gültige vollständige Alt-/Neuansichten; Journal dauerhaft vor aktiver Mutation; Runtime letzter Datenpfad; vollständige Abschlussprüfung vor Lockentfernung. **Bestehende vollständige gemeinsame Guards beibehalten.** RI-B-Kontextwiederverwendung und RI-C-Grenzoptimierung bleiben auf Erstregistrierung beschränkt. Bildoperation und Recovery behalten die bisherigen endlichen 300-s-Rahmen; keine geerbten 1800 s, automatische Verlängerung oder neue Performancekampagne.

Neuanlage/Restore in Abwesenheit ohne Ersetzen; Ersatz nur gegen exakte eigene Altbytes; Löschung nur nach exakter Byte-/Identitätsprüfung mit anschließender Verzeichnissicherung. Tempnamen bleiben journalgebunden; nur Präfixe tatsächlich vorhandener nichtnull-Seiten dürfen eigene Reste sein. Für null wird kein scheinbares Nullbild geschrieben.

Recovery bleibt Rollback. Vor erster Recoverymutation vollständigen Altstand unabhängig rekonstruieren/prüfen. Zulässige Abwesenheit aus der konkreten old/new-Seite herleiten, nicht pauschal akzeptieren. Alte Bildbytes wiederherstellen beziehungsweise ausschließlich eigene neu angelegte Bytes entfernen; Texte/Runtime zurückführen, Temps/Lock erst nach vollständig belegtem Altstand entfernen. Bei fremden/unklaren Bytes oder erneutem Abbruch Journal und belegte Reste erhalten und tatsächlichen Status melden. Kein Locklöschen als Reparatur, kein scheinbarer Erfolg eines gemischten Zustands.

### 11.5 Revisionsgenauer Abschluss und gemeinsame Verbraucher

Eigener `retire-background-production`-Einstieg mit ausdrücklich ausgewählten `(puzzle_id,authoring_revision)` und vollständigem bestätigtem Main-Commit. Vorhandene sichere Auswahl-/Index-/Gitbaumprüfungen des Revealabschlusses verwenden, ohne den Revealwriter umzudeuten.

Aktualisiertes origin/main und lokale HEAD-Abstammung prüfen; **sämtliche ausgewählten Revisionen vor der ersten Entfernung** gegen ihren nachgewiesenen Main-Stand und tatsächliche Request-/Index-/Dateibytes abgleichen. Der dort gebundene Source-v2-adoption-Ref muss genau den ausgewählten Request/diese Autorisierung, Auswahl/Ableitung und Bildrevision führen. Bei noch aktuellem Bildzustand stimmen die wirklichen Source-/Livebindungen damit überein. Bereits durch eine spätere gültige Bildrevision abgelöste Arbeit darf ebenfalls abgeschlossen werden: ihre tatsächliche frühere Übernahme wird aus dem ausdrücklich benannten Main-Commit anhand kleiner Source-/Request-/Indexmetadaten und Gitbaumidentitäten belegt; der aktuelle Stand wird unabhängig vollständig geprüft und muss denselben unveränderten initial-/Origin-/Rätselidentitätsanker sowie eine mindestens so hohe Bildrevision haben. Bei gleicher Bildrevision muss auch dieselbe Adoption/Requestbindung vorliegen; eine widersprüchliche gleichnummerierte Übernahme gilt nicht als Nachfolger. Die neuesten Source-/PNG-oder-none-/Notice-/Runtime-/Receiptbytes bleiben unangetastet. Eine bloß geplante oder nie auf Main integrierte alte Arbeit reicht nicht. Damit entsteht weder ein Cleanup-Zwang vor jeder weiteren Bildrevision noch eine wachsende aktive Historienkette.

Nur die vollständig belegten ausgewählten Arbeitsrevisionen und ihre Indexzeilen entfernen. Keine ganze-ID-Löschung. Neuere/offene Geschwister, unbekannte/fremde Dateien, staged Änderungen und aktive Ressourcen bleiben erhalten oder blockieren vor Mutation. Historische Originalblobs nicht herunterladen, um sie danach zu löschen: Gitbaumidentitäten und kleine aktuelle/gebundene Metadaten genügen. Gleiche bereits vollständig entfernte Arbeitsrevision mit identischem nachgewiesenem Mainbeleg ist nach Prüfung ihres historischen Abschlusses und des gültigen aktuellen Standes No-op, auch wenn mittlerweile eine spätere Bildrevision aktiv ist. Behandelte Teilfehler benennen tatsächliche Restpfade; ein Abbruch ist kein erfolgreicher Gesamtabschluss.

Keine zusätzliche aktive Receiptdatei oder ständig wachsende Revisionsliste: der unveränderte Erstreceipt, initial und die aktuelle adoption-Bindung bleiben die kompakte Autorität. Der Abschluss erzeugt einen überprüfbaren lokalen Produktionsdiff, keinen automatischen Commit/Merge.

Alle erreichbaren Katalog-/Quick-/Export-/Registrierungs-/Abschluss-/Metadatenreader erhalten denselben v1/v2-Quellenvertrag. Sync, Rating/Added, zulässige Kategorienpflege und Legacyziel-Update/-Revealadoption im gemischten Katalog erhalten die aktuelle v2-Quelle samt PNG/Notice unverändert. Die bisherigen vollständigen Quellen-/Plangenerationen dürfen diese neue Source nur unter ausdrücklich dokumentierter Readerkompatibilität konsumieren; ihre exakten alten Felder/Deltas bleiben. Ein Sourcewechsel macht vorhandene Pläne stale. Keine neue Generation allein für unveränderte Pfadmengen erfinden; bei tatsächlich geändertem externem Vertrag korrekt versionieren.

## 12. HP-I1c · Aktuelle Raster-/Revealbindung

Vertrag vor konsumierendem Code, 10.11.2026,
[Paketentscheidung](https://github.com/venomenon328/picross/issues/561#issuecomment-6766500497).
Nur deklarierte gültige Hintergrundziele; keine Legacy-Erstnachrüstung.
HP-I1c allein aktiviert die echte Capability nicht; diese folgt HP-I2 nach §13.
CLI und Budgets bleiben unverändert.

### Geschlossene Source v3

`picross-catalog-background-v3` hat exakt `format,base,entry,events`.
`base` ist der unveränderte vollständige Source-v1- oder Source-v2-Ausgangsstand
(niemals v3); `entry` der damalige normalisierte Registryentry mit Exporthash
statt physischem Receipthash. Die ursprüngliche Source v1, ihre erste Freigabe
und eine vorhandene v2-Adoption bleiben vollständig erhalten. Grenzen: 1 MiB,
JSON-Tiefe 32 und 1…256 Events; bei Überschreitung vor Mutation abbrechen.

Jedes Event hat exakt `operation,previous_source,binding,image,export_source`.
`operation` ist `update`, `reveal-adoption` oder `background-adoption`.
`previous_source` ist die Ref der exakt unmittelbar vorigen kanonischen Source
(erst base, danach v3 mit dem vorigen Eventpräfix). Kein rekursiver Vorgänger.
`binding` enthält exakt `entry,identity,reveal,notice,at`: normalisierter
Registryentry; identity exakt wie Source v1 mit aktueller Definitions-Ref und
Runtime-Revision; reveal/notice sind aktuelle Live-Refs am festen Zielpfad.
`at` ist null ohne AT-Quelle, sonst exakt
`binding_revision,image_revision,record_hash` des damaligen AT-Präfixes.
Jeder gespeicherte Präfix wird gegen die aktuelle append-only AT-Quelle
rekonstruiert und geprüft; alte Arbeitsdateien werden nicht geöffnet.

`image` ist ausschließlich bei background-adoption das vollständige bisherige
v2-current-Objekt, sonst null. Die aktive Bildentscheidung stammt vom letzten
solchen Event beziehungsweise base. Eine Bildadoption erhält binding exakt.
Rasterupdate erhält effektiven Revealhash und Bildfelder, erhöht Runtime-Revision
und verwendet eine neue Paketrevision bei gleicher Identität/Kategorie/Pfaden.
Revealadoption erhält entry/identity, erhöht ausschließlich die AT-Bildrevision
mit gültiger Freigabe, Vorgängerhash und erhaltener Attribution.
Writer und Journalprüfer verlangen jeweils genau ein neues passendes Event;
keine Kombioperation und kein Umschreiben früherer Events.

`export_source` ist nur bei einem v6-Rasterupdate dessen vollständig geprüfte
Source v1, ansonsten null. Ein v5-Rasterexport erklärt keinen Hintergrundwechsel:
die gültige aktive Autorität bleibt erhalten. Ein v6-Rasterexport muss alle
aktuellen Bildfelder außer der technischen Bildrevision exakt erhalten
(auch Entscheidung, Ableitung, Rechte, Kandidat, PNG/Notice oder none).
Andernfalls vor Mutation ablehnen. Alte Exportgenerationen dürfen kein
Hintergrundziel aktualisieren; v6 an einem Legacyziel bleibt Erstnachrüstung
und gesperrt. Neue Exporte werden vollständig samt unabhängiger Stagingprüfung
geprüft; frischer Difficulty-/Proof-/Palettenvertrag bleibt bestehen.

### Leser, Abschluss und Wiederholung

Die effektive identity stammt aus dem letzten Event; Initialursprung und
Bildentscheidung bleiben getrennt. Aktuelle Produktionsbytes sind entweder
der gebundene v5/v6-Export oder Receipt v2. Dessen unveränderte background-Form
bindet weiterhin die erste Source v1; entry bindet den jeweiligen abgeschlossenen
Export. Ein vorhandener ursprünglicher Receipt wird niemals umgeschrieben.
Historische Export-/Arbeitsrefs sind nach Retirement Identitäten, keine
Dateianforderungen. Der ursprüngliche identische v6-register-Aufruf darf nach
frischer Export-/Gesamtcheckoutprüfung auch nach Neubindung ein reiner No-op sein;
er stellt keine alten Definitionen, Bilder, Pakete oder Added-Daten wieder her.
HP-I1b2 bleibt der einzige Bildwriter und erhält aktuelle Raster-/AT-Bindungen.
Full/Quick, Projektion, Metadatenwriter und beide Retirementwege prüfen denselben
aktuellen Zustand. Alte v1/v2 werden nicht gelockert.

### Tatsächlich geänderte Generationen

AT-Source `picross-catalog-reveal-v2` hat die gleiche geschlossene Form wie v1,
erlaubt zusätzlich Receipt v2 in origin und ist für Hintergrundziele bestimmt.
V1 bleibt auf Legacyziele begrenzt. Alle AT-Appendregeln bleiben gleich.

Updatejournal v7 und Revealadoptionsjournal v4 erlauben die exakt hergeleitete
Source-v3-/Indexänderung. Hintergrundadoptionsjournal v2 erlaubt v3-Fortsetzung;
v1 bleibt für v1/v2-Ziele. Die acht Felder und T/K-/Namespacegrenzen bleiben gleich.
Revealjournal v4 behält die bekannten nicht-null Binärseiten und 128-MiB-Grenze;
Hintergrundjournal v2 die ausdrücklich nullable Seiten und bisherigen Grenzen.
Update bleibt 24 MiB. Alte Generationen erhalten ihre bisherigen Zielgrenzen.
Registrierung, Metadaten-/Aktivierungsjournale, Registry v3, Runtime v6, Request
und Receipt v2 ändern weder Form noch Bedeutung und werden nicht umnummeriert.

Revealplan v4 behält die bisherigen Felder einschließlich plan_hash; zusätzlich
hat jede entries-Zeile `old_background,new_background` (TextRef oder beide null)
und der Plan `old_registry,new_registry` (TextRef). Nur diese vollständigen
Alt-/Neutexte erlauben unabhängig rekonstruierten eigenen Byte-/mtime-No-op.
V3 bleibt für Legacy-Zielauswahl. Hintergrundplan v2 verwendet die unveränderte
geschlossene v1-Form, erlaubt aber Source v3; v1 bindet nur v1/v2. Neue Writer
wählen die kleinste passende Generation. Alle Quellen/Namespaces und exakten
Planbytes werden frisch vor und unter Lock gebunden; Receipt-, Raster-, Reveal-
oder Hintergrundänderungen machen ältere Pläne stale. Kein No-op am Lock vorbei.

P0–P6/R0–R2, Journal vor Mutation, Runtime zuletzt, fremde Bytes erhalten,
vollständige unabhängige Alt-/Zielprüfung und wiederholbare Recovery bleiben
verbindlich. RI-B/C bleibt ausschließlich Erstregistrierung; kein neuer Cache.

## 13. HP-I2 · Runtime, Darstellung und Besuch

Vertrag vor konsumierendem Code, 10.11.2026,
[HP-I2-K01–K12 und Prüfplan](https://github.com/venomenon328/picross/issues/561#issuecomment-6770077470),
Basis `main@964cfe2422a45871961760e65dcd863fe68ee5e0`.
Reader, Import, Bedarfsladen und Darstellung bilden einen gemeinsamen Einzelweg.
Dieser Vertrag erteilt weder Bild-/Rätselproduktion noch Mergefreigabe; tatsächliche
Lieferung, Prüfungen und unabhängige Abnahme werden am konkreten Produkt-Head
im PR belegt. Die bestehenden Arbeits-, Export-, Source-, Receipt- und
Transaktionsformen aus §§3–12 bleiben geschlossen und unverändert.

### 13.1 Runtimeeingang und Fehlergrenze

Der Godot-Katalogreader liest zusätzlich exakt `picross-runtime-registry-v6`
nach §10.3. Die neun bisherigen v5-Felder, deren Typen und die v5-Difficulty-
Semantik bleiben erhalten; ausschließlich `background` kommt hinzu. Runtime
v2–v5 behalten ihre eigenen Feldmengen und bedeuten ohne Hintergrundfeld Legacy.
Es gibt keine neue Rätseldefinition, Difficultygeneration oder Saveidentität.

Bei v6 müssen `status,image_revision,asset` vollständig und widerspruchsfrei
vorliegen: Legacy hat beide Nullwerte, none eine positive technische Bildrevision
und asset null, selected eine positive technische Bildrevision und genau den
Ref auf `art/backgrounds/<id>.png`. ID-/Pfad-/SHA-/Byte-/Revisionsgrenzen aus
§§3.1 und 10 gelten auch im Godot-Reader. Unbekannte oder zusätzliche Felder,
falsche Typen, unzulässige Nullkombinationen und Aliaspfade sind Katalogfehler.
Eine fehlende oder nicht dekodierbare Datei bei sonst gültigem selected-Eintrag
ist dagegen ein diagnostizierbarer Ladefehler. Die Dekoration wird für den
betroffenen Besuch ausgelassen; gespeicherter Status und Logik-/Savedaten
bleiben unverändert. Kein Fehler wird als none/Legacy oder Kategorieersatz ausgegeben.

Die PNG-Refs binden die unveränderten Quellbytes. Die Produktions-/Buildprüfung
vergleicht deren echte Größe/Hashes vor dem Engineimport. Der Laufzeitlader liest
die dafür importierte beziehungsweise exportierte Texture2D, keine Produktions-
oder Freigabeunterlagen. Importparameter, remappte Ressource, 2304×576-Maße und
Mipmaps sind getrennt zu prüfen. Ein Quell-PNG-Hash ist kein Hash komprimierter
Enginebytes; rohe PNG-Verfügbarkeit im PCK wird nicht vorausgesetzt und nicht
durch eine zusätzliche Rohbildkopie erzwungen.

### 13.2 Gemeinsame papiergebundene Fläche

In der Rätselansicht ersetzt selected die Kategoriezeichnung durch genau die
gewählte transparente 4:1-Leinwand; none entfernt dort die Zeichnung ohne
Nulltextur. Legacy erhält den bisherigen Kategoriepilot einschließlich seiner
bisherigen Regeln. Hilfe, Katalog und Einstellungen bleiben unverändert.

Die neue Leinwand verwendet für jedes Rätsel denselben proportionalen Fit in
eine gemeinsame Fläche im unteren sichtbaren Papierbereich, denselben Falz-/
Randabstand und den unteren mittigen Anker. Keine per-ID-Offsets, Crops, Masken
oder sonstigen Positionsmetadaten. Variante A zeichnet dieselbe Grunddarstellung
auch hinter Raster und Zeilen-/Spaltenhinweisen. Zoom verändert weder Anker,
Deckkraft noch Bildzulassung und startet keinen weiteren Ladevorgang. Die alten
RAND-P1-Ausblendregeln gelten ausschließlich für dessen Legacyzeichnungen.

Die Ebene liegt in der wirklichen Seiten-/Capturehierarchie, bleibt passiv und
erhält keine Maus-, Fokus- oder Scrollroute. Raster, Hinweise, Werkzeuge,
Meldungen und vorhandene 44/55-px-Trefferflächen behalten ihre Geometrie.
Kein Ganzbild-Fading, B1/B2/C-Menü, Hinweisfont-/Kontrastumbau oder verdeckter
Funktionslayoutausgleich gehört zu diesem Anschluss.

### 13.3 Besuch, Publikationspunkt und begrenzte Ressourcen

Ein Besuch beginnt mit der tatsächlichen Vorbereitung eines Zielrätsels und
bindet mindestens ID, aktive technische Bildrevision und eine monotone
Besuchs-/Übergangsgeneration. Wiederholtes `open_puzzle()` bei Vorbereitung
und Settlement desselben Zielbesuchs bleibt idempotent: keine neue Generation
und kein zweiter Request. Eine tatsächliche Rückkehr nach Verlassen beginnt
einen neuen Besuch, auch bei derselben ID. Ein neuer Bildstand derselben ID
ist ebenfalls eine andere Bindung; ein gleicher Ressourcenpfad darf keinen
alten Godot-Cacheeintrag als neue Revision installieren.

**Konkrete Anschlussstellen:** `game/book/content.gd` besitzt den monotonen
Besuchstoken. `begin_background_visit()` erhöht ihn und ruft
`puzzle_background.begin_visit(entry, token)` mit dem aktuellen geprüften Entry
auf. `publish_background_visit()` ruft `publish(token)`,
`leave_background_visit()` ruft `leave()`. Die Hintergrundkomponente verarbeitet
ihre begrenzten Ladeergebnisse mit `PROCESS_MODE_ALWAYS`, auch wenn die
Content-Elternverarbeitung während des Übergangs deaktiviert ist; das erteilt
keine Eingaberoute. Ihre Sichtbarkeit bleibt an die Arbeitsansicht gebunden.

`book.request_open()` beginnt den Besuch nach erfolgreichem `activate()` und
vor `_begin()`. `content.open_puzzle()` publiziert **vor** `super.open_puzzle()`
und dem ersten Ziellayout. Die vorhandenen Aufrufe aus `_prepare()` und
`_settle()` benutzen denselben bestehenden Besuch und dieselbe einmalige
Publikationsentscheidung. `present_album()` beendet den Besuch.
`information_routes.present(settings/help)` beendet ihn nach dem Source-Capture
und vor dem Informationsziel; dessen begrenzte alte Seitencapture bleibt dem
bestehenden Übergang zugeordnet. `information_routes.request_return()` beginnt
für work/ending vor `_begin()` einen neuen Besuch. Erreicht Rückkehr oder Abbruch
die Arbeit ohne noch aktiven Besuch, legt `open_puzzle()` sicher einen neuen an
und friert ihn unmittelbar ein; eine frühere Textur wird dadurch nicht wieder
gültig. Kein zusätzlicher Frame oder Wartezustand wird für Dekoration eingefügt.

| Ereignis / Zustand | Verbindliche Wirkung |
| --- | --- |
| Zielbesuch vorbereiten | Alten Besuch invalidieren, neue ID-/Revisions-/Besuchsbindung anlegen und selected früh anfordern. Legacy/none benötigen keinen neuen Bildrequest. Buch- und Eingabephase warten nicht auf Dekoration. |
| Ergebnis vor Publikation | Nur zur aktuellen vollständigen Bindung passende, vollständig gültige Textur bereitstellen. Falsche, veraltete oder defekte Ergebnisse nicht installieren. |
| Erste sichtbare Publikation der Zielseite | Vor jedem sichtbaren Zielcapture denselben Besuch einmalig festschreiben: rechtzeitig bereitgestellte gültige Textur sichtbar, andernfalls für diesen Besuch ausgelassen. Kein zusätzlicher Wartebildschirm oder längere bestehende Eingabesperre. |
| Settlement desselben Zielbesuchs | Genau die bereits festgeschriebene Auswahl erhalten; weder Request noch Publikationsentscheidung wiederholen. |
| Verspätetes Ergebnis | Nach festgeschriebener Auslassung nicht mehr anzeigen. Kein sichtbares Nachspringen; frühestens bei einem neuen tatsächlichen Besuch erneut versuchen. |
| Verlassen, Informationswechsel oder Abbruch | Besuch invalidieren, eigene Textur-/Requestreferenzen freigeben und spätere Resultate verwerfen. Bestehende zeitlich begrenzte Übergangscaptures nach ihrem Settlement-/Abbruchende freigeben. |

Die festgeschriebene Besuchsansicht und sämtliche sichtbaren Übergangscaptures
müssen dieselbe Entscheidung zeigen. A→B→A, Rückkehr, Abbruch und Revisionwechsel
werden über die vollständige Bindung behandelt, nicht allein über Pfad oder ID.
Ein Diagnosebefund unterscheidet bereit, ausgelassen wegen Zeit und fehlgeschlagen;
er ist kein neuer persistenter Produktionsstatus oder Spielerauswahldialog.

Es gibt höchstens einen aktuellen aktiven Request und einen bereits laufenden
veralteten Request. Bei weiteren Wechseln bleibt nur der neueste Zielwunsch
vorgemerkt; keine wachsende Warteschlange oder Verlaufscache. Nicht abbrechbare
Enginearbeit darf begrenzt auslaufen, ihr Ergebnis ist nicht mehr publizierbar.
Keine bestandsweite Preload-/Prefetchliste. Eigene Referenzen und laufende
Operationen sind die beobachtbare Grenze; sofortige Rückgabe sämtlicher Engine-,
GPU- oder Allocatorbytes wird nicht behauptet.

Der native Ladeadapter verwendet die strengere konkrete Grenze **ein laufender
Engineauftrag plus ausschließlich die Metadaten des neuesten Zielwunschs**.
Wird der laufende Auftrag veraltet, startet kein weiterer parallel; erst nach
seinem Abschluss darf der aktuelle vorgemerkte Wunsch beginnen, sofern dessen
Besuch noch vor Publikation liegt. Das ist kein Cache abgeschlossener Texturen.

Das bisherige nichtthreaded Webexportprofil bleibt erhalten. Der Lade-/Auslassweg
muss damit bedarfsgesteuert funktionieren, ohne neue COOP-/COEP-/Hostingpflicht
oder ungeprüfte Threadvoraussetzung. Dauerhaft alle selected-Bilder im Web
auszulassen ist keine funktionierende Webunterstützung. Lokales Bedarfsladen
ändert nicht den gemeinsamen initialen PCK-Download und ist kein Netzwerkstreaming.

**Konkreter Webadapter:** Die verlustfreie Importkompression (Modus 0) und
Mipmaps bleiben dieselben wie nativ. `JavaScriptBridge` startet höchstens einen
gewöhnlichen Blob-Worker, ohne `SharedArrayBuffer` oder COOP-/COEP-Anforderung.
Er erhält ausschließlich die Bytes des im Spielerpaket gebundenen Import-
Remaps (`.ctex`), keine Pfade oder Dateien aus Produktionsquellen. Der Adapter
prüft den fest gebundenen Godot-`GST2`-/Version-1-Container und die Grenzen seiner
PNG-/WebP-Mipmapblöcke vor der Verarbeitung. Der Worker dekodiert sie asynchron
mit `createImageBitmap` und `OffscreenCanvas` und gibt einen gepackten RGBA-
Mipmap-`ArrayBuffer` zurück. Der Hauptthread übernimmt nur den begrenzten
Bytetransfer und den `Texture2D`-Upload; kein synchrones Web-`ResourceLoader`-
Laden, Bilddekodieren oder Warten auf den Worker. Eine externe Begleitdatei
`game/web/background_loader.js` muss im Webexport nachweisbar enthalten sein.

Der Webadapter hält dieselbe vollständige Besuchsbindung und dieselbe einmalige
Publikationsentscheidung ein. Ein veralteter Worker wird beendet und seine
Referenzen werden freigegeben; kein Verlaufscache und keine wachsende Queue.
Fehlende Browser-APIs, ungültige Importcontainer oder fehlgeschlagene Dekodierung
führen zur diagnostizierten Auslassung dieses Besuchs. Das ist kein pauschaler
Webausschluss für selected. Das Lesen der gebundenen Importbytes, der begrenzte
Transfer und der Upload der festen 2304×576-Textur samt Mipmaps bleiben reale
Hauptthreadarbeit; eine Garantie für die gesamte Framedauer wird nicht behauptet.
Günstige Node-Mechanikprüfungen und das tatsächliche Web-PCK prüfen Quellbindung
und Lieferung, ersetzen aber keine ausgeführte Browserinteraktion. HP-I2 behauptet
ohne einen solchen Lauf auch keine Browserabnahme.

### 13.4 Profilimport und Spielerexport in isolierten Kopien

Der aktive `background_assets`-Quellnamensraum enthält ausschließlich seine
gebundenen PNG-/TXT-Dateien. HP-I2 erweitert weder `catalog_background.source_paths()`
noch Writer-/Journal-/Recoveryzulassung um ungebundene `.png.import`-Dateien.
Ein gemeinsamer Importvorbereiter arbeitet ausschließlich in eigenen isolierten
Godot-/Native-/Windows-/Webkopien. Er erhält die PNG2304-Bytes, setzt verlustfreie
Texturkompression (`compress/mode=0`), Mipmaps (`mipmaps/generate=true`), keine
Alpha-Randveränderung oder Premultiplikation (`process/fix_alpha_border=false`,
`process/premult_alpha=false`), keine Größenbegrenzung (`process/size_limit=0`)
und keine 3D-Profilerkennung (`detect_3d/compress_to=0`). Passende
Mipmapfilterung gehört zum Renderer. Der Vorbereiter erzeugt technische
Nebenprodukte nur dort. Keine individuelle Retusche oder Größenentscheidung.
Direkter Editorimport im schreibenden Inhaltscheckout ist kein neuer unterstützter
Produktionsweg; den isolierten Einstieg beschreibt die Werkzeuganleitung.

Regressionskopien übernehmen keine wachsende Sammlung echter Hintergründe.
Sie verwenden nur kleine feste synthetische selected-/none-/Legacyfälle.
Vor regulärem Spielerexport sind die wirklichen aktiven Ressourcen konsistent
zum aktuellen Runtimekatalog wiederherzustellen; synthetische Dateien und
deren Importreste sind vollständig zu entfernen. Windows- und Web-PCK führen
nur aktive ausgewählte Texturen, erforderliche Notices und kompakte Runtime-
daten. Kandidaten, Produktionsoriginale, Freigabeunterlagen und Prüfprogramme
bleiben ausgeschlossen. Hintergrund-TXT-Dateien müssen im Export enthalten sein.

Quellbytes, Importbytes, jeweiliger PCK-Zuwachs und dekodierte Bild-/Mipmapbytes
sind getrennte Messungen derselben begrenzten Stichprobe. Keine Seriengarantie
oder neues hartes Größen-/Laufzeitgate. Ein tatsächlicher Windows-/Webexport
belegt seine Lieferung und das geprüfte PCK, keinen Windowsstart oder ausgeführte
Browserinteraktion. Technische Kopien und Nebenprodukte enden nach ihrer Prüfung;
benötigte Revieworiginale folgen dem befristeten Paketplan.

### 13.5 Echte Capability und Authoringaktivierung

`enabled=true` nach §10.1 darf nur zusammen mit dem funktionierenden und technisch
abgenommenen Reader-/Renderer-/Lade-/Importweg integriert werden. Die unabhängige
Vor-Merge-Abnahme HP-I2-A01 bleibt am finalen Produkt-Head offen, bis der benannte
Reviewer sie tatsächlich erklärt. Synthetische kompatible Ziele dürfen diese
Fähigkeit prüfen; ihre Freigaben legitimieren keine echte Produktion.

Vor der echten Aktivierung aktuellen Ziel-/Journalstand prüfen. Capabilitybytes
sind Quellenbindung; Änderungen machen ältere daran gebundene Pläne stale.
Offene Altjournale werden durch true nicht kompatibel. Ihre bestehenden Sperren
erhalten und einen offenen Recoveryfall regulär abschließen; kein Flagwechsel,
Umdeuten oder Löschen eines Journals als Umgehung. Der bestehende reale Katalog
und Logik-/Saveidentitäten werden für HP-I2 nicht geändert; Legacy-only bleibt v5.
Keine Legacy-Erstnachrüstung und keine neue Writer-/Journalgeneration.

Der Authoring-/Offline-Sheetdefault bleibt 0.6.0. Der unterstützte 0.7.0-Weg ist
ausdrücklich gewählt; Runtime-Capability und verpflichtender Produktionsdefault
sind verschiedene Aussagen. Nach Lieferung wird der konkrete Einzelweg mit
Versionen, PRs/Commits und tatsächlichen Restlücken in #560 nachgeführt. Die
vollständige Umstellung wird nicht aus einem true-Flag oder grünen Teiltest
abgeleitet; #490/#491 sind auch kein pauschales vorgeschaltetes Gesamtgate.
Gültige Altwege, versiegelte Originale und historische false-Exportfelder bleiben
erhalten. MJ-A ergänzt ausschließlich den regulären Sheetweg nach §7.5;
der eigenständige spätere Hintergrundänderungsjob folgt MJ-B nach Hintergrundvertrag §7.6.

### 13.6 Einmalige Entwicklung und spätere Inhaltsarbeit

HP-I2-K01–K12 präzisieren HI03–HI05/HI07–HI09 und den Runtimeanschluss der bereits
gelieferten HI01/HI02-Teile. HI06 bleibt entfallen. Der verbindliche Paketplan
bestimmt die vier ausgewählten Module, die einmaligen nativen T01-/Import-PCK-
T02-Belege, sechs unveränderte Original-PNGs und deren erreichbaren befristeten
Transport. Keine neue Dauer-Buch-/Screenshot-/Browservollsuite und keine
Umdeutung eines Screenshots zum Interaktionsnachweis.

HP-I2-A01 prüft unabhängig Diff, ausgewählte CI, T01/T02 und Originale am finalen
Produkt-Head, einschließlich gemeinsamer A-/Fit-/Transparenz-/Geometrie-/
Passivitätsabnahme. Das getrennte Selbstreview ersetzt sie nicht. Es entsteht
keine neue persönliche Buchabnahme und kein Kandidaten-Testimport pro Rätsel.
Die konkrete isolierte Eigentümerauswahl bleibt die Bildentscheidung; nur das
gewählte Asset wird im letzten regulären Integrationsschritt übernommen.
Reale Bildproduktion/HW07, Mehrjob-Sheet, Batch und Serienpilot bleiben eigene
offene Umfänge. Ein grüner Werkzeug- oder Runtimefall schließt #560/#561/#563
nicht ohne Prüfung ihrer vollständigen zuständigen Kriterien.
