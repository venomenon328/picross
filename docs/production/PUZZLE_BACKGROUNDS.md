# Technischer Vertrag für Kontextzeichnungen

Dokument-ID: `background-technical`
Status: `active`
Vertrag: 1.0 · Dokumentrevision 20 · 17.11.2026 · PROD-SLIM / [#700](https://github.com/venomenon328/picross/issues/700)

## Zuständigkeit

| Bereich | Normative Quelle |
| --- | --- |
| Stil, Inhalt, Transparenz, Komposition und Randabschluss | [BACKGROUND](images/BACKGROUND.md) |
| Sichturteile und Kriterienklassifikation | [Qualität §9](PUZZLE_QUALITY.md#9-hintergrundzeichnungen) und H-07 |
| Aktuelle Produktionsfolge und Auswahl | [Authoring Schritt 4](authoring/PUZZLE_AUTHORING_STEP_4.md) |
| Manifest, Entscheidung, HP-W2-Ableitung | §§3–4 dieses Dokuments |
| Aktuelle Integration, Quellen und Recovery | [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md), unten §10 |
| Gezielte Editortransaktion | [PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung) |
| Ältere geschlossene Paket-/Transportformen | §§2, 5, 7; frühere Editorformen nur als Herkunftsverweis in §14 |
| Bildprofile, Capability und Laufzeit | HG31, §13, technische Importgrenzen in §14 |

Neue Produktion folgt ausschließlich Authoring 0.8.0. Weiterhin konsumierte
0.6-/0.7-Paketformen behalten ausschließlich ihre tatsächlich gebundene
Lesesemantik; sie sind kein zusätzlicher aktueller Produktionsweg. Frühere
Offline-Sheet-Sitzungen und UI-Aufträge sind nur historische Herkunft nach §7.3.
Geschlossene Felder und Prüfgrenzen nicht zwischen Generationen übertragen.

Der isolierte Spielerimport konsumiert auch kompakte Hintergrund-v6-Quellen
ohne `notice` oder `authority` im `current`. Vorhandene historische TXT-Dateien
am festen Hintergrundstamm bleiben unverändert und werden im Importinventar
mit echten Bytes/Hashes gebunden. Ohne vorhandene TXT-Datei ist `notice=null`;
Import und Mainvergleich erzeugen weder Ersatztext noch Herkunftspflichten.
Eine fehlende PE-EDIT2-Hintergrund-TXT ist auch beim Produktionsabschluss kein
Fehler. Vorhandene Bytes und tatsächliche Abwesenheit bytegenau gegen Main
vergleichen. Ältere Quellen behalten ihre verpflichtenden Notice-Refs.

## Aktuelle Ergebnisform

Neue Jobs führen Briefing, Angebote, Auswahl, aktuelle Sichturteile und echte
Nutzungsgrundlagen ausschließlich im einen aktuellen Record nach
[PW-B](../tools/PW_B_CONTRACT.md). Reine Hintergrundpflege referenziert aktive
Reveal-/Definitionsbytes sicher und erzeugt keine Kopien oder neuen Rasterproofs.

Der aktuelle Helfer `python -m tools.puzzle_production.current_tools background
--input ORIGINAL.png --output AKTUELL.png` bereitet mit dem ausdrücklich gewählten
HG31-Profil ein aktuelles PNG vor. Kein Manifest, Prompt, Generator-/Codec-Hash,
Ableitungsbefund, Entscheidungsdossier oder Nullbefund als Begleitdatei. Die
aktuellen angebotenen PNGs werden selbst geprüft und vorgelegt; temporäre
Vorbereitungsdateien enden nach Erhalt des aktuellen Ergebnisses. Bei none/standard
entsteht kein Bild. Tatsächliche Wahl und Qualitätsurteile bleiben im Record.

Angebote bleiben bis zur Entscheidung erreichbar. Ersetzte, abgelehnte oder
nicht gewählte Bilder und ausschließlich zugehörige Hilfsdateien danach entfernen,
sobald keine aktuelle Nutzung mehr besteht. Kein Archivieren und kein Warten auf
Main. Materielle Änderungen übernehmen keine alte Freigabe; reine administrative
Pfadänderungen unveränderter Bytes verlangen keine neue kreative Entscheidung.

Die folgenden HP-W2-v1/v2-, Paket- und Sidecarformen dokumentieren ausdrücklich
ältere/temporäre Operationsdaten. Kein aktueller Reader darf sie für einen neuen
aktuellen Record nachfordern oder automatisch als Entstehungsarchiv neu erzeugen.
Bildprofile, aktuelle Bildqualität und technische Import-/Runtimegarantien bleiben.

## HG31 · zwei geschlossene Bildprofile

Profilvertrag aus [#675](https://github.com/venomenon328/picross/issues/675),
seit [PR #676](https://github.com/venomenon328/picross/pull/676) integriert.
Die beiden Profile sind unterschiedliche geschlossene technische Formen.
Bestehende Quellen behalten ihr gebundenes Profil und dessen Bedeutung;
neue Produktion wählt das neue Profil ausdrücklich. Gestaltung und zulässige
Kompositionskorrektur definiert ausschließlich die Bildnorm.

Das neue vollständige HP-W2-Profil lautet exakt:

```json
{
  "id": "picross-background-png2304x768-v1",
  "width": 2304,
  "height": 768,
  "format": "PNG",
  "mode": "RGBA",
  "fit": "exact",
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

H(profile) verwendet die bestehende Kanonisierung. Das bisherige Profil in §4.1
behält seinen Körper und Hash. V2-Request/Befund unterstützen genau beide Profile;
Entscheidung v1 erweitert nur ihre geschlossene {id,sha256}-Wertedomäne.
V1-Request/Befund bleiben ausschließlich beim alten Profil. Arbeitsmanifest v1
bleibt unverändert. `describe(generation=2, profile_id=...)` bzw.
`describe --profile-id ...` wählt das Profil ausdrücklich; ohne Angabe bleibt der
bisherige API-Default. Neue 3:1-Produktion gibt stets die neue ID an.
Request, Entscheidung, Befund und verify müssen dasselbe vollständige Profil
und dessen Hash binden. Keine automatische Auswahl aus zufälligen Quellmaßen.
Für das neue Profil gilt nach Orientierung exakt W=3H; sonst Abweisung vor
Publikation. Die gesamte Quelle wird auf 2304×768 skaliert, ohne Padding.
Farb-, Alpha-, Encoder-, Ressourcen- und tatsächliche Renderidentität bleiben
nach §4 gebunden; geänderter Rendercode erfordert neue echte Bindungen.
Historische Originale werden niemals umetikettiert oder neu versiegelt.

Fertigimport ergänzt `picross-prepared-background-png2304x768-v1`: exakt
2304×768 PNG RGBA8 mit den vorhandenen Farb-/Alpha-/Framinggrenzen.
`picross-prepared-background-png2304-v1` behält seine 2304×576-Bedeutung und
die zulässigen PNG-Farbtypen `0|2|3|4|6` mit höchstens 8 Bit je Kanal,
einschließlich erlaubtem tRNS und Interlacing. Exakt validierte
PNG-Geometrie bestimmt eindeutig die Fertigimport-ID. Bytes bleiben unverändert.
RI-Eingang/aktive Quellen/Registry/Runtime und Editorrequest behalten ihre
Feldformen; kein Profilfeld in Assetrefs, keine Save-/Bildrevisionsmigration.

Capability v2 enthält exakt `format,runtime_format,profile_ids,enabled`:
`format=picross-runtime-background-capability-v2`,
`runtime_format=picross-runtime-registry-v8`, boolesches enabled und exakt
`profile_ids=[picross-background-png2304-v1,picross-background-png2304x768-v1]`
in dieser Reihenfolge. V1 bleibt ausschließlich die 4:1-Zusage aus dem alten
Vertrag. 2304×768 zusammen mit v1 scheitert an Writer-, Import- und Runtimegrenzen.
Unbekannte oder widersprüchliche Formen scheitern. Die Unterstützung beider
Profile ist seit [PR #676](https://github.com/venomenon328/picross/pull/676) auf main
integriert; der technische Zwischenhalt von #671 ist beendet. Den tatsächlichen
Einführungsnachweis und die ausdrücklich erlassenen Vor-Merge-Gates A01/A02 hält
[der HG31-Abschluss](https://github.com/venomenon328/picross/issues/675#issuecomment-6919304397)
fest. Ein Nachweisverzicht gilt nicht nachträglich als bestandene Prüfung.

Beide Profile verwenden dieselbe sichere horizontale Papierfläche und den
unteren mittigen Anker aus §13.2. Mit r=4 bzw. r=3:
Breite=min(sichere Breite,sichere Höhe*r), Höhe=Breite/r. Bei genügend Platz
hat 3:1 dieselbe Breite und ein Drittel mehr Höhe, sonst vollständigen
proportionalen Fit. Kategoriezeichnungen bleiben unverändert. Deckkraft 0,48,
Mipfilterung, passive Eingabe, Capturehierarchie und Besuchspublikation bleiben.
Geometrie wird aus der frisch validierten Textur des betreffenden Ladebesuchs
gebunden; alte asynchrone Antworten dürfen keinen neuen Besuch beeinflussen.
Beide Profile haben elf zusätzliche Mipstufen. Jede ganzzahlig halbierte
Dimension und die vollständige RGBA-Kette werden geprüft: 7.077.844 bzw.
9.437.176 Bytes. Die 64-MiB-Grenze wird nicht erhöht.

HG31-T01–T03 und HG31-A01 bezeichnen die damaligen Einführungsnachweise aus #675;
ihren tatsächlichen Abschluss einschließlich der Nachweisverzichte dokumentiert
der oben verlinkte Paketabschluss. Sie eröffnen kein neues Gate je Bildserie.
Synthetic End-to-End bis Editor/RI, Import und beiden PCKs, einmaliger bytegenauer
Bestandsschutz und echte native/Web-/Editorbedienung sind getrennte Aussagen.
Headless-/Node-/HTTP-Erfolg ersetzt keine tatsächlich geöffnete Darstellung.
Revieworiginale liegen ausschließlich auf einem temporären separaten Reviewref,
binärer Download vor Übergabe geprüft; erhalten bis HG31-A01/Paketabschluss.

## 1. Geltung und tatsächlicher Unterstützungsstand

Der aktuelle Produktionsweg und sein Pflichtquellenrouting stehen in Authoring.
HP-W2 stellt die eigenständige API/CLI `describe/derive/verify` nach §§3–4 bereit.
Diese prüft Datei-/Bildableitung, weder redaktionelle Qualität noch menschliche
Bildwahl. Synthetische Werkzeugdurchstiche sind keine echte Bildproduktion.

Die Runtime verwendet Variante A nach §13: dieselbe passive Grunddarstellung
hinter Raster und Hinweisen, gemeinsamen Fit/Anker und unteren Papierbereich.
Funktionslayout und Trefferflächen bleiben erhalten; kein lokales Abblassen,
keine Unschärfe, kein deckender Rasteruntergrund und keine globale Zoom-Ausblendung.
B1/C sind verworfen; B2 ist keine eingeführte Option. Ein lokales PNG-Ergebnis
belegt keinen Engineimport, keine Mipmaps und keinen Netzwerkdownload.

Frühere Einführungspakete und Aktivierungsstände sind am
[Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md)
abrufbar. Dortige offene Statusangaben sind keine aktuellen Aufträge oder Gates.

## 2. Versionierte Bereitschaft

Aktuelle Phasen und Datenformen: [PW-B](../tools/PW_B_CONTRACT.md).
Frühe Hintergrundpflichten des folgenden Legacy-Teilvertrags gelten nicht für
neue 0.8-Jobs. Die historische Vier-Aufträge-Anleitung ist durch die aktuelle
Authoringroute ersetzt.

### Phasen für Authoring 0.7.0 / Handoff v3

Geltung: ausschließlich historische Authoring-0.7.0-/Handoff-v3-Daten.
Neue Jobs folgen der aktuellen Phasenroute; vorhandene Originale werden nicht
umetikettiert. Der folgende geschlossene Legacy-Teilvertrag bleibt erhalten.
PB-H baut die Phasen bis einschließlich `content_ready`; ein neues Original
mit finalem Abnahme-/Exportzustand wird nicht gebaut. HP-I1a darf den äußeren
Record nach frischer Prüfung bis `editorially_approved` fortschreiben und v6
exportieren. `catalog_ready`, `registered` und `integration_ready` bleiben false;
eine Phase „exportiert“ wird nicht eingeführt. Die jeweils gebundenen
0.6.0-Inhaltsgates und die ZA-1-Prüfung auf dem geschriebenen ZIP bleiben
Bestandteil dieser historischen Generation.

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
| `briefing` | `Text` zum konkreten Kontextauftrag gemäß Bildnorm; keine versteckten Positionsparameter. |
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
`{file:Path,contract:"1.0",document_revision:Integer>0,commit:Commit,sha256:SHA}`
des tatsächlich gelesenen Qualitätsregelstands. `norm.file` besitzt genau die
zwei zulässigen Werte `docs/production/PUZZLE_QUALITY.md` und
`docs/PUZZLE_QUALITY.md`. Neue Bindungen am aktuellen Dokumentbaum verwenden
den ersten Pfad; historische Bindungen behalten ihren damaligen Pfad und ihre
unveränderten Quellbytes. Der Pfad bezeichnet die Norm am gebundenen
`norm.commit`, keinen Pfad unter der Hintergrundarbeitswurzel. Ein tatsächlich
ausgeführtes Urteil bindet
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
| `profile` | Bei `selected` exakt `{id,sha256}`: `id` ist eines der beiden ausdrücklich gewählten Profile aus HG31, `sha256=H(vollständiges zugehöriges Profil)`; sonst null. Neue 3:1-Produktion wählt `picross-background-png2304x768-v1`. Die vereinbarte deterministische Ableitung ist bereits Teil des Auswahlscope. |
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

Für ein Bild müssen Q-HG01–Q-HG04 tatsächlich vorliegen. `nicht geprüft`
blockiert Hintergrundbereitschaft. `erfüllt` ist regulär positiv. `Warnung` und
`nicht erfüllt` bleiben sichtbar; ausschließlich redaktionelle Feinheiten wie
Strichgewicht, Luftigkeit oder begrenzte Kantenqualität dürfen mit derselben
Eigentümerwahl ausdrücklich angenommen werden. Dafür ist der
passende Eintrag in `accepted_deviations` erforderlich; keine weitere Dialogphase.

Unabdingbar bleiben die Kontext-/Inhaltsgrenze [HG-01](images/BACKGROUND.md#hg-01-kontext),
echte Transparenz in freien Außen-/Zwischenräumen nach
[HG-04](images/BACKGROUND.md#hg-04-transparenz),
die ausgeschlossenen technischen Kompositionsmanipulationen nach
[HG-05](images/BACKGROUND.md#hg-05-ganze-leinwand), der Randabschluss
[HG-06/H-07](images/BACKGROUND.md#hg-06-randabschluss), gültige Datei-/
Profil-/Freigabebindungen und geklärte Rechte. `accepted_deviations` darf diese
Grenzen nicht legitimieren und macht einen technischen Fehler nicht erfolgreich.
Die Bildnorm unterscheidet erlaubte dichte Objektpartien von freien Zwischenräumen;
diese Erlaubnis wird durch den technischen Alphabefund nicht eingeschränkt.
Bildwahl darf vor technischer Auflösung aufgezeichnet werden;
`selected` allein bedeutet keine Bereitschaft.

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

Request/Befund v1 erlauben ausschließlich das folgende vollständige Profil;
v2 erlaubt beide Profile nach HG31. Zusätzliche oder abweichende Parameter sind
ungültig. `profile_sha256=H(dieses Objekt)`.

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

Geltung dieses Profilkörpers: `picross-background-png2304-v1`.
Sein `contain`-Verhalten bleibt für tatsächlich daran gebundene Quellen erhalten;
es erteilt keine Gestaltungsfreigabe für neue Kandidaten. Das neue Profil und
seine exakte Eingangsdimension stehen unter HG31. Originalmaße dürfen innerhalb
der jeweiligen Profil-/Ressourcengrenzen variieren.
Quelle vollständig als ein PNG-Frame
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

Moduleinstieg [`tools.puzzle_production.background_assets`](../../tools/puzzle_production/background_assets.py):

```text
python -m tools.puzzle_production.background_assets describe
python -m tools.puzzle_production.background_assets derive --request <request.json> --source-root <quellen> --output-root <ausgaben>
python -m tools.puzzle_production.background_assets verify --request <request.json> --source-root <quellen> --output-dir <befundordner>
```

Die [Werkzeuganleitung](../../tools/puzzle_production/README.md#hp-w2-eigenständige-hintergrundableitung)
beschreibt die lokale Verwendung mit dem gebundenen Pillowstand. Neue Produktion
verwendet die unten definierte v2-Generation. Die folgende ursprüngliche v1-Form
bleibt unverändert: `describe(generation=1)` liefert exakt
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
Der v1-Auftrag `picross-background-derive-request-v1` enthält genau:

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
Hashes vollständig unverändert und werden strikt geprüft. In der Grundroute
müssen aktuelle `id`, die vollständige `versions`-Map und die exakte sortierte
Modulpfad-/Bytehashmenge dem Erzeugerstand entsprechen. Ausschließlich `commit` und `dirty`
bezeichnen die unveränderte Herkunft des Erzeugerlaufs; sie verlangen keinen
identischen HEAD oder Dirtyzustand im späteren Prüfcheckout. Geladene Modulbytes
müssen den aktuellen Dateien entsprechen; dieser vollständige aktuelle
Werkzeugstand und alle Eingangs-/Befundbytes dürfen sich während der Prüfung
nicht ändern. Ausgabe und vollständigen Befund mit dem **originalen Toolobjekt**
frisch reproduzieren und bytegenau vergleichen. Eine passende Hashliste allein
ist kein Reproduktionsnachweis.

**HP-W2-COMPAT-1 / #645:** Zusätzlich zur obigen Gleichheitsroute darf ausschließlich
lesendes `verify` eine explizit qualifizierte historische Erzeugeridentität bei
`selected` prüfen. Die geschlossene Menge in `background_assets.py` bindet über
`H(tool)` das vollständige originale Toolobjekt einschließlich Commit, dirty,
sämtlicher neun Modulpfade/-hashes und Versionsmap. Erster Eintrag ist
`23971ee3834218f28977a346e09f716de6eb18fd6fc3acb8cab25a5ad8cab691`
aus Commit `94f0fb35ab4f6623a1ddde6d0ca3b03590be0e57`, dirty=false;
Qualifizierung und Prüfplan stehen in der
[Paketentscheidung](https://github.com/venomenon328/picross/issues/645#issuecomment-6882921168).
Vor Aufnahme wurden die vollständigen gebundenen Quellen mit diesem Gitstand
abgeglichen; weitere Identitäten benötigen einen eigenen qualifizierten Nachweis.
Historischer Code wird nicht ausgeführt oder aus Git/Netz nachgeladen.

Die Menge allein akzeptiert kein Ergebnis. Aktuelle ID und vollständige
Codec-/Pythonversionsmap müssen weiterhin exakt passen. Aktuell geladene und
gespeicherte Module werden vor und nach dem Lauf vollständig gebunden. Der
aktuelle sichere Leser prüft sämtliche ursprünglichen Request-/Quell-/Entscheidungs-
und Belegbindungen und reproduziert mit dem festen Profil sowohl das PNG als auch
den vollständigen Befund einschließlich originalem Toolobjekt und Diagnostik
bytegenau. Jede Abweichung scheitert. `none` und unbekannte historische Identitäten
erhalten diese zusätzliche Route nicht. Keine pauschale Modulnamenausnahme,
kein persistenter Brückenbeleg und keine Umschreibung bestehender Bytes.
Finalizer prüft weiterhin zuerst den alten Record; Paket-/Exportreader und
Offline-`verify-export` verwenden dieselbe zentrale Prüfung ohne Sonderfreigabe.

`derive`, einschließlich seines schreibenden `reused`-Pfads, behält die strikte
vollständige aktuelle `expected_tool_sha256`-Bindung. Tatsächlich geänderte
Module außerhalb der ausdrücklich qualifizierten lesenden Route sowie geänderte
Codecs oder Profile bleiben Fehler und erfordern eine getrennte neue Ableitung;
alte Request-/Befund-/Freigabebytes werden nicht umgeschrieben.
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


### 4.7 PW-PERF-C: neue HP-W2-Beleggeneration v2

[Paketentscheidung](https://github.com/venomenon328/picross/issues/653#issuecomment-6892078406).
Neue Aufträge verwenden `picross-background-derive-request-v2`, mit exakt den
sieben v1-Feldern `format,manifest,decision,source,profile,expected_tool_sha256,output`.
Die zulässigen vollständigen Profile stehen in HG31; die kanonische Hashbildung
und PNG-/Ressourcen-/Pfadgrenzen bleiben unverändert. Der Befund
`picross-background-derivation-v2` hat exakt die bisherigen v1-Befundfelder plus
`producer`. `producer` ist exakt `{commit,dirty}`: vollständige tatsächliche
Git-HEAD-SHA und Boolean für den tatsächlichen Arbeitsbaum (einschließlich
unversionierter Dateien), ermittelt zu Beginn des Aufrufs vor eigenen Lock-/
Staging-/Ausgabeschreibvorgängen. Diese Herkunft gehört zum Befund, nicht zu
H(tool). Spätere Git-Statusänderungen, insbesondere durch eigene Arbeitsdateien,
sind kein Renderidentitätswechsel. Der Dirty-Status wird ohne zusätzliche
Pfadausnahmen ermittelt; echte Eingangs-/Zieländerungen und Renderquellenwechsel
werden weiterhin an ihren unabhängigen frischen Datei-/Bytegrenzen abgewiesen.

V2-`tool` hat exakt `id,versions,modules`, ID `picross-background-2`.
`versions` hat exakt `python,pillow,zlib,littlecms`; Pillow bleibt 12.3.0.
`modules` ist die sortierte, eindeutige Liste aus exakt zwei `{file,sha256}`-Zeilen:
`tools/puzzle_production/background_render.py` und
`tools/puzzle_production/image_normalization.py`. Der erste enthält die strikte
PNG-Prüfung, Geometrie, Alphabehandlung, Pixelbefunde und PNG-Kodierung, der zweite
die tatsächliche Farb-/EXIF-Normalisierung. Keine Diagnose-, Git-, CLI-, I/O- oder
Orchestrierungsmodule im Bildidentitätskern. Geladene Renderquellen und ihre
physischen Dateiidentitäten müssen vor/nach dem Aufruf passen; lediglich aktuelle
Dateien zu hashen genügt nicht. Profil/Codecs/Renderquellen ändern die Identität,
reine Diagnose- oder Gitänderungen tun dies nicht.

`describe`/`describe(generation=2)` liefert Profil/Tool samt Hashes und `producer`;
`describe --generation 1` / `describe(generation=1)` beschreibt ausdrücklich v1.
Der Request dispatcht derive/verify ohne Generationsraten. V1 behält seine exakten
Felder, neun Module, Tool-ID und bisherigen Reproduktionsregeln. Die qualifizierte
selected-Ausnahme aus #645 wird nicht erweitert; sie gilt weder für none noch
Produktion. Request-, Tool- und Befundgeneration müssen zusammenpassen.

Verify reproduziert Bild und den ganzen Originalbefund einschließlich ursprünglicher
Herkunft. Identischer v2-Reuse erhält ebenfalls die ursprünglichen Befundbytes;
er prüft Quellen, Ziele und aktuelle Implementierung frisch, ohne Überschreiben.
Fremde/fehlende/teilweise Ziele bleiben Fehler. Katalog-, Receipt-, Paket-,
Finalizer- und Offline-Reader dispatchen beide geschlossenen Formen. Export v6,
Record-/Registryformen und historische Originalbytes ändern sich nicht.

## 5. Paketbindung und gewöhnliche finale Endabnahme

Geltung: historische Paket-/Freigabegenerationen, deren tatsächlicher Vertrag
`picross-editorial-approval-v2` verwendet. Aktuelle Erstintegration nach §10.

Handoff/Inventar eines vorgelegten Pakets bleiben unverändert. Die spätere
Entscheidung und Ableitung liegen außen; der äußere Record führt die aktuellen
Refs und den daraus geprüften effektiven Status. Das funktioniert auch, wenn
das Originalhandoff noch `raster_ready` mit offener Bildwahl enthält. Die neue
Readergeneration muss Originalstatus und äußeren aktuellen Befund getrennt
ausgeben, statt das Original als nachträglich fertig versiegelt auszugeben.

Die geschlossene finale Form für 0.7.0 ist **`picross-editorial-approval-v2`**.
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

Fachliche Rücksprünge und Nachweiswiederverwendung:
[Authoring Schritt 3 §4.4](authoring/PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen).
Korrektur laufender Kandidaten vor Wahl:
[Schritt 4 §6.3.1](authoring/PUZZLE_AUTHORING_STEP_4.md#631-formatkorrektur-vor-der-bildwahl).
Reine spätere Hintergrundpflege: aktueller §10/PE-Weg.

Technische Entscheidungsfortschreibung:

- Neue Auswahl derselben gültigen Vorlage erzeugt eine separate Entscheidung mit explizitem `previous_decision`; abhängige Ableitung/Endbindung verwendet genau diese Wahl. Alte Freigaben nicht überschreiben.
- Nur administrative Manifestberichtigung: `carried_from` ist ausschließlich bei identischen gewählten Originalbytes, Kandidaten-ID/Bildrevision, `context` und Profil zulässig. Tatsächlicher Akteur, UTC, Wortlaut und Beleg bleiben bytegleich. Neue Manifestbindung/Berichtigungsgrund dokumentieren; geänderte Rechte getrennt prüfen.
- Für `previous_decision` und `carried_from` gilt die azyklische Vorgängerregel; kein Selbst-/Nachfolgerverweis. Materielle Bildänderungen sind darüber nicht übertragbar.
- Vereinbarte deterministische Ableitung oder bytegleicher Transport erteilt keine neue kreative Freigabe; Datei-/Profil-/Toolbindung frisch prüfen. Ein anderer Toolstand erhält seine eigene Ableitungsbindung.
- Wiederaufnahme lädt aktuelle Originale, Manifest, Entscheidung, Rechte, Befund und Freigaben. Erreichbare gültige Bytes benötigen keinen erneuten Upload; keine stillen Versionswechsel.

## 7. Transportformen ohne Datenverlust

Unveränderte Felder werden nicht neu erfunden: „Basis“ bezeichnet nachfolgend
den exakten dokumentierten und ausführbaren Vertrag an der in §1 genannten
Commitbasis. Die angegebenen Deltas sind vollständig; alte Generationen
behalten ihre eigenen geschlossenen Feldmengen. Unbekannte deklarierte Formate
und neue Felder in alten Hüllen werden abgewiesen, nicht entfernt oder als
Freitext versteckt. PB-H unterstützt §§7.1–7.2 und die **Ausgabe** von
Sheet-Update v3 nach §7.3. HP-I1a ergänzt äußere Fortschreibung nach §7.4.
Frühere Offline-Sheet-Sitzungen und MJ-A/MJ-B-UI-Protokolle besitzen hier keine
aktuelle Reader-/Writerzusage. Neue Hintergrundwechsel folgen §11.

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
[authoring_build_contract.py](../../tools/puzzle_production/authoring_build_contract.py),
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
[authoring_builder.record_for](../../tools/puzzle_production/authoring_builder.py),
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

### 7.3 Weiterhin erzeugte Sheet-Update-v3-Ausgabe

Geltung: ausschließlich die von `authoring_builder.sheet_from_record` weiterhin
erzeugte PB-H-/0.7-Ausgabe. Neue 0.8-Arbeit verwendet die aktuelle Projektion nach
[PW-B](../tools/PW_B_CONTRACT.md). Die Basisschlüssel von
`picross-cheatsheet-update-v3` entsprechen unverändert der v2-Ausgabe:

```text
format,Motiv,Rasterbreite,Rasterhöhe,Größenvorgabe,Rätselmodus,Farbanzahl,
Farbvorgabe,Verwendete Farben,Rätsel-ID,Paketrevision,Paketpfad,Abschlussbild,
Abschlussbild-Optionen,Rastervariante,Raster-Optionen,Motivvorlage,
Parameterkorridor,Inventar-SHA-256,Quellbranch / Commit,PR,Produktionsstatus,
Nächster Schritt
```

Ihre tatsächlichen phasenabhängigen Werte folgen dem geprüften Record und dem
[Baukern](../../tools/puzzle_production/authoring_builder.py), ohne eine Auswahl,
Freigabe oder Git-Sicherung zu erzeugen. V3 ergänzt genau:

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

Die früheren Sitzung-v5-/Auftrag-v4-, MJ-A-Mehrjob- und MJ-B-Adoptionsprotokolle
stehen vollständig am
[festen Vorgängerstand §§7.3–7.6](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md#73-sheet-update-v3-sitzung-v5-und-auftrag-v4).
Diese historische Beschreibung verspricht keinen heutigen UI-Importer,
Sitzungswriter, Adoptionweg oder Recoveryreader. Eine alte Formularabsicht ist
keine heutige tatsächliche Entscheidung; aktuelle Auswahl folgt Authoring.

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

## 8. Historische Einführung

Die abgeschlossenen HP-W1/W2-, PB-H-, HP-I-, MJ- und BA-Einführungsstände,
Writer-/Readerpakete und damaligen offenen Aktivierungsaufträge sind am
[Vorgängerstand §8](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md#8-konkrete-einführung-und-reader-writermatrix)
gebunden. Ihre geschlossenen Datenformen bleiben in den ausdrücklich bezeichneten
Abschnitten dieses Dokuments beziehungsweise ihren Fachverträgen erhalten.
Ein Versionsstring darf bestehende Proof-, Paletten-, Rechte- und Freigabegates
nicht abschalten. Kein alter Export wird durch Umbenennen zum aktuellen Eingang.

## 9. Aufbewahrung und Abschluss

Aktuelle Sicherung während der Auswahl und tatsächlicher Produktionsabschluss folgen
[Authoring §§6–7](authoring/PUZZLE_AUTHORING.md#6-dateien-übergabe-und-wiederaufnahme)
und [Schritt 5 §9](authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).
Aktive Nutzdaten und Rechte bleiben erhalten; abgeschlossene Produktion benötigt
kein dauerhaftes Kandidatenarchiv. Noch offene/neuere Arbeit nicht entfernen.
Historische Freigaben nicht umschreiben und bereinigte Rasterproduktion für einen
Bildwechsel nicht rekonstruieren.

Kein Generierungs-, Fehlversuchs- oder Korrekturprotokoll nach Vorliegen des
aktuellen Ergebnisses führen. Offene aktuelle Blocker bleiben im Record.

Die früheren synthetischen Vertragsfälle und vollständigen Formbeispiele sind
am [Vorgängerstand §9](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md#9-aufbewahrung-abschluss-und-vertragsfälle)
abrufbar; sie sind keine ausgeführten Produktionsnachweise oder heutigen Aufträge.

## 10. HP-I1b1 · Erste Registrierung und kompakter Produktionsabschluss

Aktuelle Erstintegration und Recovery folgen ausschließlich
[RI](PUZZLE_INTEGRATION.md) und [ZA-1](ZA1_ADAPTER.md).
`picross-integration-input-v1` bindet den tatsächlichen aktuellen Inhalt,
Identität, Livebytes, Rechte und ausdrückliche Entscheidung. Keine zusätzliche
Produktionsarchiv-, Producer- oder Regelbuch-Allowlist.

Bildlose Auswahl und gewähltes Asset gemäß aktuellem Eingang unterscheiden.
Fehlende/defekte Dateien ersetzen keine Entscheidung. Gewählte Bilder erfüllen
ihren ausdrücklich gebundenen HG31-Profilvertrag. Ein historischer
Hintergrundauftrag oder Sheetstatus wird nicht als aktueller Eingang übernommen.

Aktuelle Bild-/Raster-/Metadatenänderungen sind eigene Operationen nach
[PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Der Bildwriter verwendet den unveränderlichen geprüften Bildplan und sein Journal;
er erhöht nur die betroffene Bildrevision. Eine identische Wiederholung erhält
Bytes, Revisionen und mtimes.

## 11. HP-I1b2 · Eigenständiger Hintergrundwechsel

Ein eigenständiger Hintergrundwechsel verwendet den gezielten Bildvertrag aus
[PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung)
und die aktuellen Quellen nach §10. Herstellung und tatsächliche Bildwahl folgen
[Authoring Schritt 4](authoring/PUZZLE_AUTHORING_STEP_4.md); Sicherung und
revisionsgenauer Abschluss folgen
[Schritt 5 §9](authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).
Unveränderte Raster-/Proof-/Schwierigkeitsbindungen erhalten; frühere
Rasterproduktion nicht rekonstruieren.

Die alten HP-I1b2-Requests, Pläne und Journale sind am
[festen Vorgängerstand §11](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md#11-hp-i1b2--eigenständiger-hintergrundwechsel)
als Herkunft erhalten. Sie begründen keinen aktuellen Reader, Writer oder
Recoveryweg. Aktuelle Wiederaufnahme und Recovery folgen ausschließlich dem
wirklich verwendeten PE-/RI-Vertrag; alte Daten werden nicht umetikettiert.

## 12. HP-I1c · Aktuelle Raster-/Revealbindung

Aktueller Weg: §10 und PE. Raster-/Revealneubindung und Hintergrundrevision sind
verschiedene Operationen; unabhängige gültige Bindungen nach den dortigen
Verträgen erhalten.

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

Der historische Hintergrundteilvertrag wurde mit `picross-runtime-registry-v6`
eingeführt; Runtime v7/v8 behalten diese Hintergrundsemantik mit der späteren
`standard`-Erweiterung aus §14. Die jeweilige vollständige Registryform steht in
RI/PE. Ältere v2–v5-Formen behalten ihre eigenen Feldmengen und bedeuten ohne
Hintergrundfeld Legacy; neue Quellen werden nicht in diese Formen umetikettiert.

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
oder Freigabeunterlagen. Importparameter, remappte Ressource, die Maße des tatsächlich gebundenen
HG31-Profils und Mipmaps sind getrennt zu prüfen. Ein Quell-PNG-Hash ist kein Hash komprimierter
Enginebytes; rohe PNG-Verfügbarkeit im PCK wird nicht vorausgesetzt und nicht
durch eine zusätzliche Rohbildkopie erzwungen.

### 13.2 Gemeinsame papiergebundene Fläche

In der Rätselansicht ersetzt selected die Kategoriezeichnung durch genau die
gewählte vollständige Leinwand ihres HG31-Profils; none entfernt die Zeichnung ohne
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
Transfer und der Upload der Textur ihres gebundenen HG31-Profils samt Mipmaps bleiben reale
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
bleiben ausgeschlossen. Vorhandene beziehungsweise formatbedingt erforderliche
Hintergrund-TXT-Dateien exportieren; die eingangs geregelte zulässige Abwesenheit
bei kompakten Quellen bleibt erhalten.

Quellbytes, Importbytes, jeweiliger PCK-Zuwachs und dekodierte Bild-/Mipmapbytes
sind getrennte Messungen derselben begrenzten Stichprobe. Keine Seriengarantie
oder neues hartes Größen-/Laufzeitgate. Ein tatsächlicher Windows-/Webexport
belegt seine Lieferung und das geprüfte PCK, keinen Windowsstart oder ausgeführte
Browserinteraktion. Technische Kopien und Nebenprodukte enden nach ihrer Prüfung;
benötigte Revieworiginale folgen dem befristeten Paketplan.

### 13.5 Capability und Aktivierung

Capabilitybytes sind Quellenbindung; Änderungen machen ältere daran gebundene
Pläne stale. Ein Flagwechsel legitimiert keine unbekannten Quellen oder offenen
Journale. Bestehende Recovery-Sperren erhalten; nicht durch Umdeuten oder Löschen
eines Journals umgehen. Die geschlossenen Capability-v1/v2-Domänen stehen unter
HG31. Eine vorhandene ungültige Capability bleibt Fehler.

Die technische Fähigkeit ist geliefert; neue Produktion folgt Authoring 0.8.0.
Die frühere HP-I2-Einführungsabnahme und damaligen Aktivierungsstände stehen im
zuständigen Issue/PR, keine erneute Vor-Merge-Abnahme pro Bildserie. Reale
Bildentscheidung und technischer Runtime-/Importnachweis bleiben getrennte Aussagen.

### 13.6 Entwicklung und Inhaltsarbeit

Technische Weiterentwicklung prüft ihren tatsächlichen Diff nach dem aktuellen
Paketplan. Keine Dauer-Buch-/Screenshot-/Browservollsuite aus historischen
Einführungsbelegen ableiten. Inhaltsproduktion folgt der isolierten Sichtung
und Auswahl nach Authoring; kein Kandidaten-Testimport oder zusätzliche
persönliche Buchabnahme je Rätsel.

## 14. Fertigimport und aktuelle Editorroute

### 14.1 Unveränderte fertige PNGs

Die beiden geschlossenen Fertigimport-IDs, ihre exakten Geometrien und jeweils
zulässigen Farbtypen stehen ausschließlich unter [HG31](#hg31--zwei-geschlossene-bildprofile).
Beide Eingänge verlangen höchstens 32 MiB, ein nicht animiertes vollständig
dekodierbares PNG, bereits korrekte Orientierung, sRGB-Kompatibilität sowie
mindestens einen vollständig transparenten und einen sichtbaren Pixel.

Der Reader prüft Framing und vollständige Dekodierung unabhängig. Vorhandene
sRGB-Intents müssen 0–3 sein, vorhandenes Gamma muss innerhalb 0,0001 um 0,45455
liegen. Vorhandene Chromatizität muss komponentenweise höchstens 0,00002 von
`[0.3127,0.3290,0.6400,0.3300,0.3000,0.6000,0.1500,0.0600]` abweichen.
Ein vorhandenes ICC-Profil darf nicht leer sein; die unabhängige Normalisierung
darf weder Pixelwerte noch Orientierung oder Originalbytes ändern.
Diese Prüfungen entsprechen dem aktuellen
[`editor_image_input.validate_background`](../../tools/puzzle_production/editor_image_input.py).

Quellbytes werden ohne Skalierung, Farbkonvertierung oder Neukodierung importiert.
Es entsteht kein HP-W2-Derivationobjekt und kein neues HP-W2-Codec-/Modulprofil.
Ein unzulässiger Eingang scheitert; die Importprüfung repariert ihn nicht.

### 14.2 Isolierter Engineimport

Die Importvorbereitung folgt ausschließlich den Einstellungen aus §13.4.
Beim tatsächlichen Import der 4:1-Form werden Graustufe mit Transparenz
(PNG-Typ 0) und Graualpha (Typ 4) als LA8 geprüft; RGB/Palette/RGBA
(Typ 2/3/6) als RGBA8. Die 3:1-Form verlangt RGBA8. Die RGBA8-Prüfung eines
HP-W2-Ableitungsausgangs bleibt unter beiden Profilen erhalten.
Maße des gebundenen Profils, tatsächliches Alpha und vollständige Mipmaps
bleiben Pflicht. Quellprüfung, wirklicher Godotimport und PCK-Dekodierung sind
getrennte Nachweise. Keine Importsidecars im aktiven Inhaltscheckout und keine
behauptete Browser-/Windows-GUI-Abnahme aus einer reinen Dateiprüfung.

### 14.3 Aktuelle Pflege und historische Herkunft

Auswahl, Transaktion, Rechte und Zähler folgen [PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Aktuelle Quellen, Runtimeprojektion und Integrations-/Recoveryeingänge folgen
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Die Hintergrundzustände besitzen
[PE §4.2](../tools/PUZZLE_EDITOR.md#42-drei-verständliche-hintergrundzustände)
und RI-ONE; dieser Abschnitt führt keine zweite Editor- oder Registrynorm.

Die früheren PE-A2-Source-v5-, Adoptions-, Editorrequest-, Journal-,
T8/K8/C8- und Receiptformen sind vollständig am
[festen Vorgängerstand §14](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_BACKGROUNDS.md#14-pe-a2--fertigimport-und-ausdrückliche-aktuelle-präferenz)
erhalten. Das ist ein Herkunftsbeleg, keine Zusage eines heutigen Readers,
Writers oder Recoverywegs. Alte Quellen und Freigaben nicht in aktuelle Formen
umetikettieren oder zur neuen Integration rekonstruieren.
