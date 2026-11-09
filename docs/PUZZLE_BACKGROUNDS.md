# Rätselbezogene Hintergrundzeichnungen

**Vertrag 1.0 · Dokumentrevision 2 · 09.11.2026 · HP-W1/HP-W2 / #560**

## 1. Geltung und tatsächlicher Unterstützungsstand

Dieser Vertrag schließt den noch **nicht aktivierten** Produktionsweg aus
[#560](https://github.com/venomenon328/picross/issues/560) und dem
[Paket HP-W1](https://github.com/venomenon328/picross/issues/560#issuecomment-6747196307).
Maßgeblich sind die [Eigentümerkorrektur zur isolierten Auswahl](https://github.com/venomenon328/picross/issues/560#issuecomment-6744957790)
und [#558 / D01](https://github.com/venomenon328/picross/issues/558#issuecomment-6744063800).
Die Evaluierung wird nicht übernommen; PR #559 bleibt geschlossen und ungemergt.
Der integrierte RAND-P1 ist ein Konzeptpilot. HP-W1/HP-W2 ersetzen weder dessen
Kategoriezeichnungen noch bereits ausführbare Reader oder Runtimepfade.

Geprüfte Vertragsbasis: `main@e8da5dbdc48a355a3de5888f882ce1e25843915d`.
**Aktiv bleibt Authoring 0.6.0**, mit der jeweils tatsächlich gebundenen
Dokumentrevision und dem dazugehörigen Snapshot. Auf den Dokumentvertrag HP-W1
folgt die eigenständig nutzbare Teilfähigkeit
[HP-W2](https://github.com/venomenon328/picross/issues/560#issuecomment-6748799473):
Arbeitsmanifest, Entscheidung, Ableitungsauftrag und Befund nach §§3–4 sowie
`describe`, `derive` und lesendes `verify` sind unterstützt. Der vollständige
Produktionsweg bleibt **inaktiv**. Die neuen Handoff-/Paket-/Sheetformen und
Phasen sind noch nicht unterstützt; Bildproduktion, ZA-1-Zulassung, finale
Integration und Runtime werden durch HP-W2 nicht geliefert.

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

Die spätere Runtime nach [#561](https://github.com/venomenon328/picross/issues/561)
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

Die folgende Semantik gilt ausschließlich für den zukünftigen Weg. Die heutige
0.6.0-Bedeutung von `content_ready`, ihre Inhaltsgates und die ZA-1-Prüfung auf
dem geschriebenen ZIP bleiben unverändert.

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
| Reiner späterer Hintergrundersatz | Gesonderter Bildauftrag mit neuen Originalen/Wahl/Ableitung und dem sicheren HP-I1-Weg. Lösungs-, Hinweis-, Paletten-, Schwierigkeits-, Runtime-/Saveidentität, Slot, Added-Daten und gültige unveränderte Freigaben erhalten. Keine Rekonstruktion alter bereinigter Rasterproduktion oder neuen Solverläufe allein wegen des Bilds. |

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
Freitext versteckt. Die folgenden Änderungen sind **nur spezifiziert**.

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
`build`-Versiegelung. Ihr tatsächlicher sicherer Writer gehört HP-I1.

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
leeren vorherige neue Options-/Hintergrunddaten; keine Vermischung mit einer
anderen Produktion. Import, Sitzungsbackup und Auftragsexport erhalten alle
neuen Bindungen, wirklichen Entscheidungen und offenen Werte. Alte Leser müssen
neue Generationen zurückweisen. Der heutige Record-v1-Import projiziert nur
bekannte Felder und könnte hineingeschriebene Hintergrunddaten verlieren;
deshalb niemals neue Arbeit als scheinbar kompatiblen v1-Record ausgeben.

## 8. Konkrete Einführung und Reader-/Writermatrix

| Paket / vorhandene Dateien | Fähigkeit und erlaubter Zwischenstand |
| --- | --- |
| **HP-W1 / #560:** dieser Fachvertrag, Authoring/Snapshot, Qualität, Profil, Produkt/Design, Produktions-/Werkzeugrouting | Geliefert: Sollvertrag und Dokumentrevision. Aktive Version 0.6.0, durch HP-W1 keine geänderten ausführbaren Reader/Writer. |
| **HP-W2 / #560:** `tools/puzzle_production/background_assets.py` und zugehörige Hintergrundhilfen | Geliefert: eigenständige Arbeits-/Entscheidungs-/Ableitungsformen und API/CLI `describe/derive/verify` nach §3–4. Kleine synthetische Tests sichern die Datei-/Bildfähigkeit. Frühe Bildarbeit bleibt vorbereitet; kein Handoffbau oder ZA-1-/Runtimeversprechen. |
| **PB-H / #489:** `tools/puzzle_production/authoring_build_contract.py`, `authoring_builder.py`, `authoring_package.py` | Geschlossene neue Format-/Phasenzulassung, sichere Referenzmenge für angebotene/gewählte Bilder, Builder v2, Record v2 und Sheet-v3-Projektion. Eigene Normalisierung verboten; HP-W2 verwenden. Frühe Pakete brauchen keinen finalen Adaptererfolg; `content_ready` weiterhin vollständige passende Prüfung. |
| **HP-I1 / #561:** `tools/puzzle_production/target_adapter.py`, `authoring_package.py`, `content_registry.py`, `catalog_integration.py`, `integrated_content.py` | Finale v3-/0.7.0-Eingänge samt äußerer Hintergrundentscheidung/Ableitung und Endfreigabe v2 prüfen; sichere Einzelintegration und späterer reiner Hintergrundersatz. Export-/Registry-/Receiptformen erst mit ihren tatsächlich betroffenen Deltas versionieren. Eine bloße Versionswhitelist liefert diese Fähigkeit nicht. |
| **HP-I1 gemeinsame Veröffentlichung:** `catalog_transaction.py`, `catalog_publication.py`, `catalog_io.py`, `registration_publication.py`, `registration_verification.py`, betroffene Folgeoperationen `content_update.py`, `content_registry.py`, `catalog_reveal.py`, `reveal_source.py`, `reveal_retirement.py`, `integrated_content.py` unter `tools/puzzle_production/` | Aktive Hintergrundbindung in Quellen-/Namespaceprüfung, Konflikten, No-op, Recovery, Folgeoperationen und Abschluss erhalten; fremde/defekte Daten blockieren. Genaue Writer-/Journalergänzungen gehören HP-I1, HP-W1 erfindet keine neue ausführbare Transaktion. |
| **HP-I2 / #561:** `game/model/content_registry.gd`, erzeugte `game/data/registry.json`, `game/book/content.gd`, `game/book/marginalia.gd` | Kompatibler neuer Runtimeeingang, Variante A, gemeinsames Assetlayout, verlustfreier Import/Mipmaps und Bedarfsladen. Der heutige `marginalia.gd`-Pilot mit Kategoriepreloads/individuellen Regionen ist keine Produktionsschnittstelle. Keine Kandidatenvorschau. |
| **#490:** `docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html`, insbesondere `parseTransfer`, `validateChoices`, `saveSession`, `loadSession`, `brief`, `exportPackage` und zugehörige Prompt-/Auswahlprojektion | Record v2, Update v3, Sitzung v5 und Auftrag v4 verlustfrei führen; vorhandene v1–v4-Alteingänge getrennt erhalten. In HP-W1/HP-W2 ausschließlich bytegleicher Regelwerksnapshot und Revisionsangaben, keine neue Bedien-/Importfähigkeit. |
| **#491 / #492** | Nur tatsächlich gelieferte Fähigkeiten orchestrieren beziehungsweise in gesondert beauftragter Produktion erproben. Keine parallelen Hintergrundformate oder künstliche Vollintegration durch Ergebnisflags. |

Die heute explizit an **0.6.0** gebundenen Palettengates in
`target_adapter.inspect`/`verify_export` und die Paar-/Difficultyzulassung in
`authoring_package`/`target_adapter` müssen für die neue Generation ausdrücklich
mitgeführt werden. Handoff v3/0.7.0 erbt sämtliche bisherigen 0.6.0-Garantien:
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
Rasterproduktion. Die vorhandenen Cleanupbefehle unterstützen diese neuen
Daten erst nach dem zuständigen HP-I1-Anschluss, nicht bereits durch HP-W1/HP-W2.

Die folgenden **synthetischen Vertragsfälle** sind keine erzeugten Bilder,
Freigaben, ausgeführten Programme oder Produktionsnachweise:

| Fall | Erwarteter Ausgang |
| --- | --- |
| Drei Dateien A/B/C offen | Manifest offered, Entscheidung null, keine Vorauswahl. Nach Motivfreigabe unabhängige Rasterarbeit zulässig; technisch fertiges Raster 0.7.0 nur `raster_ready`. |
| „B verwenden“ gemeinsam mit Motivfreigabe | Separate Entscheidung bindet B/Manifest/Profil; nur B ableiten, dieselbe Wahl über Rastervarianten erhalten. Keine zweite Bildbestätigung. |
| Späte Auswahl B plus Endabnahme am versiegelten Rasterpaket | `presented_package` bindet Originalbytes. Entscheidung/Ableitung/Endfreigabe v2 außen ergänzen; Originalhandoff/-inventar/-ZIP unverändert. Nach vollständiger Prüfung regulärer Auftrag 4. |
| „Bewusst ohne Hintergrund“ | none mit tatsächlicher Erklärung; vor Kandidatenproduktion zusätzlich belegte Ausnahme von drei Bildern. HP-W2-Nullbefund, keine Nulltextur. |
| Gültiges 0.6.0-Altpaket ohne Hintergrund | Nach altem Vertrag lesbar, Hintergrund als Legacy eingeordnet. Keine rückwirkende Wahl, neue Pflicht oder Migration. |
| Deklarierte Quelle fehlt, Hash falsch oder Format unbekannt | Konkreter Eingangsfehler/Blocker, kein none/Legacy und keine Integration. |
| Materielle Alpha-/Kompositionskorrektur von B | Neue Bildrevision, alte Wahl/Ableitung nicht gültig für neue Bytes; nur korrigiertes Bild erneut vorlegen. Unveränderte Rasterproofs erhalten. |
| Unveränderte Ableitung oder Paketkopie | Frische passende Byte-/Profilbindung, keine zusätzliche kreative Freigabe. Wiederholung am exakten Ziel echter No-op. |
| Reine spätere Hintergrundrevision | Bild-/Paketbindungen dürfen wechseln; Matrix, Hinweise, Palette, Difficulty, Runtime-/Saveidentität und bestehende Integrationsoriginale bleiben unverändert. |

HP-W1 prüfte diese Verträge am tatsächlichen Dokumentdiff. HP-W2 ergänzt die
ausführbare Datei-/Bildfähigkeit mit kleinen synthetischen Tests für Deterministik,
Ressourcen-/Pfad-/Alpha-/Konfliktfälle; konkrete Laufnachweise gehören in seinen PR.
Verbraucher und Runtime folgen in ihren Paketen, drei reale erreichbare Bilddateien
im gesonderten Produktionsauftrag. HP-W1/HP-W2 schließen weder #560 noch den
Gesamtplan #563.

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
