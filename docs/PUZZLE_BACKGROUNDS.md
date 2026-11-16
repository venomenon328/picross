# Rätselbezogene Hintergrundzeichnungen

**RI-ONE: aktueller Integrationsstand.** Die technischen Integrations-, Quellen-
und Recoveryformen folgen [RI](PUZZLE_INTEGRATION.md) und [ZA-1](ZA1_ADAPTER.md).
Frühere generationsbezogene Einführungsabschnitte sind dafür historisch; sie
stellen keinen zweiten Integrationsweg bereit. Bildqualität, kreative Auswahl,
PNG/SVG und explizite Freigaben bleiben verbindlich.


> Aktueller Editor-Sonderweg: [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung) definiert die gezielte Transaktion, Reveal v4, Hintergrund v6 und Rasterpaket v2. Normale Editoraktionen lesen keine historische Produktion. Explizite Produktionsprüfung/Recovery alter Formen bleiben bestehen; Folgeproduktion erhält die aktuelle technische Bildbindung. Die externe Migration gehört zu #641, nicht in die Editor-App.

Der isolierte Spielerimport konsumiert auch kompakte Hintergrund-v6-Quellen
ohne `notice` oder `authority` im `current`. Vorhandene historische TXT-Dateien
am festen Hintergrundstamm bleiben unverändert und werden im technischen
Importinventar mit echten Bytes/Hashes gebunden. Ohne vorhandene TXT-Datei ist
dessen `notice` null; der Import erzeugt weder Ersatztext noch Herkunftspflichten.
Aktive PNG-Bindung, sichere Namensräume und das gemeinsame Importprofil bleiben
geprüft. Ältere Quellen behalten ihre bisherigen verpflichtenden Notice-Refs.


**PE / #576 · PE-A1 integriert, PE-A2 zur Umsetzung beauftragt:**
[PE-A2](PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag) ergänzt fertige
2304×576-Dateien ohne Neukodierung, die erste individuelle Zuordnung bei einem
Legacyrätsel und die schreibbare Auswahl Standard/eigenes Bild/kein Hintergrund.
Der geschlossene neue Vertrag steht in §14. Die bisherige Ableitung und Legacy-Sperre
beschreiben weiter ausschließlich ihre alten Generationen.
[PE-A1](PUZZLE_EDITOR.md#7-pe-a1-geschlossener-metadatenvertrag) verwendet
Runtime v7 mit identischem v6-Hintergrundteilvertrag; Capability-v1 bleibt
unverändert, Legacy-only aktiviert keine Hintergründe.
[Source v4](PUZZLE_EDITOR.md#75-geschlossene-implementierungsformen) erhält bei
einem regulären Rasterupdate mit geänderter historischer Kategorie alle bisherigen
v3-Ereignisbindungen. Metadatenpflege und Migration ändern keine Hintergrundquelle.

**PW-B · 0.8.0, 11.11.2026:** Für neue Produktionen gilt der
[fünfstufige Authoringweg](ai-workflows/PUZZLE_AUTHORING.md) mit dem geschlossenen
[PW-B-Datenvertrag](PW_B_CONTRACT.md). Hintergrundbriefing, drei Kandidaten und
Auswahl beginnen erst nach der ausdrücklichen qualifizierten Rasterwahl in Schritt 4.
Frühe Hintergrundpflichten sowie 0.6-Default/0.7-Opt-in-/Offline-Sheetbeschreibungen
weiter unten bezeichnen ihre alten Generationen und gelten nicht für neue 0.8-Jobs.
Bestehende Inhalts-, Proof-, Paletten-, Bild-, Freigabe- und Integrationsgarantien
bleiben erhalten. Der Dienst bleibt lesend; Veröffentlichung und Gitabschluss
führt der beauftragte Akteur aus. Historische Originale werden nicht migriert.

**Vertrag 1.0 · Dokumentrevision 15 · 15.11.2026 · HG-FORMAT / [#663](https://github.com/venomenon328/picross/issues/663); HP-W2-COMPAT-1 / #645; HP-W1/HP-W2 / #560; PB-H / #489; HP-I1a/HP-I1b1/HP-I1b2/HP-I1c/HP-I2 / #561; MJ-A/MJ-B / #490; BA-A/BA-B / #491; PE-A2 / #576**

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
Das feste Profil `picross-background-png2304-v1`, kanonische Hashbildung und alle
PNG-/Ressourcen-/Pfadgrenzen bleiben unverändert. Der Befund
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
| Auswahl abgelehnt oder konkrete Korrektur offen | Zustand `rejected`/`pending`, Korrektur im beauftragten Umfang; reine Formatkorrektur laufender Kandidaten ist nach [Schritt 4 §6.3.1](ai-workflows/PUZZLE_AUTHORING_STEP_4.md#631-formatkorrektur-vor-der-bildwahl) bereits vom Hintergrundproduktionsauftrag umfasst und braucht keine zusätzliche Rückfrage, auch vor der Bildwahl. Unveränderte bereits autorisierte Rasterarbeit darf fortgesetzt werden. Keine automatische erste/empfohlene Option. |
| Wiederaufnahme | Index/Record, tatsächlichen Paketstand, Hintergrundmanifest, Entscheidung, Originale, Rechte, Befund und Freigaben selbst laden/prüfen. Keine erneuten Uploads/Bestätigungen für bereits erreichbare gültige Bytes; keine stillen Versionswechsel. |
| Reiner späterer Hintergrundersatz | Gesonderter Bildauftrag mit neuen Originalen/Wahl/Ableitung und dem sicheren HP-I1b-Weg. Lösungs-, Hinweis-, Paletten-, Schwierigkeits-, Runtime-/Saveidentität, Slot, Added-Daten und gültige unveränderte Freigaben erhalten. Keine Rekonstruktion alter bereinigter Rasterproduktion oder neuen Solverläufe allein wegen des Bilds. |

Neue Auswahl auf derselben gültigen Vorlage erzeugt eine neue separate
Entscheidung mit explizitem `previous_decision`; abhängige Ableitung/Endbindung
muss genau diese Wahl verwenden. Keine alten Freigaben überschreiben. Für
`carried_from` gilt dieselbe azyklische Vorgängerregel; der neue Record kann
nicht auf sich oder einen Nachfolger zeigen. Eine Materialänderung ist darüber
nicht übertragbar. Der ursprüngliche ImageGen-Prompt allein legitimiert keine
materielle Umgestaltung. Die bereits vom Hintergrundproduktionsauftrag umfasste
Formatkorrektur nach Schritt 4 §6.3.1 erlaubt das Herstellen korrigierter Kandidatenbytes,
einschließlich
transparenter Leinwanderweiterung per Skript; ihre tatsächliche Wahl bleibt offen.
Dieser Vorwahlschritt ist keine HP-W2-Ableitung und verändert weder deren Profil
noch bereits integrierte Bilder oder historische Freigaben.

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
[Authoring §9](ai-workflows/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).
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

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Bei Erstregistrierung ist der Hintergrund ausdrücklich `selected` oder `standard`.
Ein gewähltes Bild hat 2304×576 RGBA-Pixel, exakt gebundene Bytes, Rechtehinweis
und echte Auswahl-/Endfreigabe. Standard ist eine bewusste aktuelle Entscheidung;
keine fehlende Datei ersetzt diese Entscheidung. Der separate aktuelle Editor
verwendet `picross-editor-image-request-v2`, einen unveränderlichen Bildplan und
sein eigenes Journal. Er erhöht nur die betroffene Bildrevision; ohne Änderung
bleiben Bytes, Revisionen und mtimes gleich. Ein historischer Hintergrundauftrag
oder ein Sheetstatus wird nicht als aktuelle Integrationseingabe übernommen.

## 11. HP-I1b2 · Eigenständiger Hintergrundwechsel

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Bei Erstregistrierung ist der Hintergrund ausdrücklich `selected` oder `standard`.
Ein gewähltes Bild hat 2304×576 RGBA-Pixel, exakt gebundene Bytes, Rechtehinweis
und echte Auswahl-/Endfreigabe. Standard ist eine bewusste aktuelle Entscheidung;
keine fehlende Datei ersetzt diese Entscheidung. Der separate aktuelle Editor
verwendet `picross-editor-image-request-v2`, einen unveränderlichen Bildplan und
sein eigenes Journal. Er erhöht nur die betroffene Bildrevision; ohne Änderung
bleiben Bytes, Revisionen und mtimes gleich. Ein historischer Hintergrundauftrag
oder ein Sheetstatus wird nicht als aktuelle Integrationseingabe übernommen.

## 12. HP-I1c · Aktuelle Raster-/Revealbindung

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Bei Erstregistrierung ist der Hintergrund ausdrücklich `selected` oder `standard`.
Ein gewähltes Bild hat 2304×576 RGBA-Pixel, exakt gebundene Bytes, Rechtehinweis
und echte Auswahl-/Endfreigabe. Standard ist eine bewusste aktuelle Entscheidung;
keine fehlende Datei ersetzt diese Entscheidung. Der separate aktuelle Editor
verwendet `picross-editor-image-request-v2`, einen unveränderlichen Bildplan und
sein eigenes Journal. Er erhöht nur die betroffene Bildrevision; ohne Änderung
bleiben Bytes, Revisionen und mtimes gleich. Ein historischer Hintergrundauftrag
oder ein Sheetstatus wird nicht als aktuelle Integrationseingabe übernommen.

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

## 14. PE-A2 · Fertigimport und ausdrückliche aktuelle Präferenz

Vertrag vor konsumierendem Code gemäß
[PE-A2](https://github.com/venomenon328/picross/issues/576#issuecomment-6839202555)
und [Receipt-Präzisierung](https://github.com/venomenon328/picross/issues/576#issuecomment-6839354651).
Der direkte Eingang `picross-prepared-background-png2304-v1` prüft genau 2304×576,
höchstens 32 MiB, nicht animiertes vollständig dekodierbares PNG, bereits korrekte
Orientierung und sRGB-Kompatibilität, mindestens einen vollständig transparenten
und einen sichtbaren Pixel. Die bisherigen zulässigen höchstens 8-Bit-PNG-Farbtypen
einschließlich erlaubtem tRNS und Interlacing bleiben. Quellbytes werden ohne
Neukodierung importiert; es entsteht kein HP-W2-Derivationobjekt und kein neues
HP-W2-Codec-/Modulprofil.

Die isolierte Importvorbereitung aus §13.4 erhält weiterhin Kompression 0,
Mipmaps und die bestehenden Alpha-/Größeneinstellungen. Der tatsächliche Engine-
Import des direkten Eingangs wird nach Quellenfarbtyp geprüft: Graustufe mit
Transparenz (Typ 0) und Graualpha (Typ 4) als LA8, RGB/Palette/RGBA (Typ 2/3/6)
als RGBA8; Maße, tatsächliches Alpha und Mipmaps bleiben vollständig zu prüfen.
Die alte RGBA8-Prüfung gilt weiter für den historischen HP-W2-Ableitungsausgang.
Quellprüfung, echter Godotimport und PCK-Dekodierung sind getrennte Aussagen;
PE-A2-K10/T02 bindet ihren neuen technischen Nachweis. Keine Importsidecars im
aktiven Inhaltscheckout und keine behauptete Browser-/Windows-GUI-Abnahme.

| Neue Form | Exakte Felder |
| --- | --- |
| `picross-catalog-background-v5` | `format,id,record_revision,origin,binding,current,record_hash`. |
| `origin` | `entry,identity,notice,source`; unveränderter historischer Normalanker, Source v1–v4 oder null nur bei gültigem bisher sourcefreiem Legacy. Keine eingebettete v5-Hülle. |
| `binding` | `entry,identity`; aktueller geprüfter Normalanker. Identity exakt `key,save_slot,definition,runtime_revision`, Definition als Ref. |
| `current` | `image_revision,status,asset,notice,authority`; status standard/selected/none. Nur selected besitzt feste Asset-/Notice-Refs `game/art/backgrounds/<id>.png/.txt`, sonst null/null. |
| Manuelle Autorität | `kind,decision,provenance`, kind manual; Decision/Provenienz/Notice exakt nach PE §8.1–8.2. Bildlose Auswahl hat provenance null. |
| Produktive Autorität | `kind,candidate_revision,decision,derivation,provenance,review,adoption`, kind production; vorhandene HP-W2-Teilformen vollständig prüfen. |
| Produktive v5-`adoption` | `request,revision,target,background,authorization,context`; bisherige fünf Unterformen unverändert, context exakt wie im tatsächlichen Request v2. |
| `picross-background-adoption-request-v2` | `format,puzzle_id,revision,target,background,authorization,files,test_only,context`; die bisherigen acht Felder behalten ihren Vertrag. |
| `context` | `source,production,reveal`; Source-Ref auf aktuelle Revealquelle oder sourcefreier vollständiger Produktionsanker `{entry,identity}`. Genau eines von source/production ist nicht null. reveal ist immer der aktuelle echte aktive Reveal-Ref. |
| `picross-background-adoption-plan-v3` | `format,request,snapshot,old,new,files,plan_hash`; bisherige Textansichten/Bundle-Refs, vollständiger v8-Snapshot mit sieben Namespaces. |
| `picross-background-adoption-journal-v4` | Achtfelderform des gemeinsamen Writers, operation background-adoption. Vollständig hergeleitete Text-/Binär-/Abwesenheitsdeltas aus alten/neuen Quellen; report_run null. |

Manuelle Pflege verwendet separat `picross-editor-images-request-v1` und den
gemeinsamen Editorbildplan/-writer aus [PE §8](PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag).
Reguläre Produktionsadoption verwendet weiterhin wirkliche Auswahl/Ableitung,
Endfreigabe/Autorisierung und gebundene Quelldateien; sie darf die aktuelle
Revealautorität nicht aus `origin.approval.selection.reveal` rekonstruieren.
Kontext/Target werden beim Planen und unmittelbar vor Übernahme vollständig geprüft.
Ein späterer manuell geänderter Reveal macht den alten Request stale.

Source v5 bleibt nichtrekursiv. Erste echte Pflege respektiert den bisherigen
wirksamen Bildzähler; spätere Bild-/Präferenzentscheidung erhöht image_revision
einmal, Raster-Rebind nur record_revision. Identische Wiederholung erhält Zähler,
Bytes und ursprüngliche Entscheidung/Zeit. Die genaue Zähler- und Noticeableitung
steht in PE §8.1–8.2. Originale Rechte/Freigaben werden nicht umgeschrieben.

Eine erforderliche Rebind-Überführung von BG-v1–v4 bei aktivem manuellen Reveal v3
ist ausdrücklich produktiv: vollständige alte Quelle als unveränderter origin,
exakt deren aktuelle Bild-/HP-Felder übernehmen, nur neue aktuelle binding und
record_revision, keine neue image_revision/Entscheidung. Eine vorhandene alte
fünffeldrige Adoption wird dabei unverändert durch Gleichheit mit der validierten
Ausgangsquelle bewiesen. Ohne frühere Adoption ist null ausschließlich für das
ursprüngliche Bild erlaubt, ebenfalls mit vollständigem Gleichheitsnachweis.
Neue produktive Adoptionsentscheidungen verlangen den sechsfeldrigen v2-Kontext;
alte Reader werden nicht erweitert. Die
[begründete Präzisierung](https://github.com/venomenon328/picross/issues/576#issuecomment-6839354651)
ändert keine Erstregistrierung und erzeugt keine historische Freigabe.

Für eine wirkliche reguläre Request-v2-Adoption aus noch bestehender BG-v1–v4
gilt der direkte produktive Erst-Adoptionsbuilder: neue v5-origin enthält die
vollständige alte Quelle; adoption.target bleibt deren echter Source-Ref,
damaliger Originhash und Bildzähler. Nur vollständige Gleichheit dieses Targets
mit der validierten origin.source erlaubt den Erstfall. Die neuen aktuellen
HP-Belege/context sind echt, beide Zähler steigen einmal; keine erfundene
Zwischenquelle und kein alter Request mit neuer Bedeutung. Weitere v5-Adoptionen
binden ihren regulären v5-Originhash.

Inhaltsregistry bleibt v4; der vorhandene Hintergrundindex bindet jede neue Source.
Runtime v8 behält den dreifeldrigen Hintergrund: legacy null/null, ausdrückliches
standard mit positiver Präferenzrevision und asset null, selected/none wie bisher.
Standard folgt der **aktuellen** Metadatenkategorie; fehlt deren vorhandene Zeichnung,
ist kein Hintergrund wirksam. selected/none bleiben von Kategoriewechseln unabhängig.
Alle sechs Zustandswechsel, Bildersatz, Legacy-Erstbindung und Standardrückkehr
sind erlaubt. Defekte deklarierte Quelle ist Fehler, kein stiller Standardfallback.
Legacy ohne Source beginnt optisch unverändert, ohne rückwirkende manuelle Entscheidung.

Capability v1 gilt unverändert auch für v8 und dasselbe Renderprofil. selected/none
erfordern enabled, legacy/standard allein nicht; eine vorhandene ungültige Capability
bleibt Fehler. Die bestehende passive 4:1-Darstellung, untere Zentrierung,
Besuchs-/Ladegrenzen und Spoiler-/Inputverträge bleiben. Keine neue Kategoriezeichnung.

Die vollständigen T8/K8/C8-/Namespace-/Deltamengen stehen in PE §8.4 und
[SD_CATALOG](SD_CATALOG.md#pe-a2--geschlossene-v8-quellen-pläne-und-journale).
Neue Revealendungen und Hintergrund-PNGs werden mit tatsächlichen oder negativen
Erwartungen gebunden. selected→standard/none entfernt nur eigene aktive PNG/TXT;
Rollback kann sie wiederherstellen. Fremde Dateien bleiben unangetastet und blockieren.

Für Legacy-Erstbindung mit späterem regulärem v6-Rasterupdate erhält der neue
`picross-integrated-content-v3`-Receipt exakt
`format,entry,integrated_commit,notice_sha256,background`; background exakt
`origin_sha256,export_source`. Die echte aktuelle Export-Source v1 wird vor
Retirement vollständig geprüft und gespeichert; bei sourcefreier Produktion null.
Der Originhash bindet den unveränderten v5-Erstanker. Source v5 bekommt dafür
weder fingierte Initialquelle noch weitere Historie; alte Receipt v1/v2 bleiben streng.
Aktuelle manuelle Präferenz und Rechte überleben Registrierung, Raster-Rebind,
reguläre Adoption, Sync, Batch und Produktionsabschluss.

## PW-PERF-B · Begrenzte Erstregistrierungsprüfung

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Bei Erstregistrierung ist der Hintergrund ausdrücklich `selected` oder `standard`.
Ein gewähltes Bild hat 2304×576 RGBA-Pixel, exakt gebundene Bytes, Rechtehinweis
und echte Auswahl-/Endfreigabe. Standard ist eine bewusste aktuelle Entscheidung;
keine fehlende Datei ersetzt diese Entscheidung. Der separate aktuelle Editor
verwendet `picross-editor-image-request-v2`, einen unveränderlichen Bildplan und
sein eigenes Journal. Er erhöht nur die betroffene Bildrevision; ohne Änderung
bleiben Bytes, Revisionen und mtimes gleich. Ein historischer Hintergrundauftrag
oder ein Sheetstatus wird nicht als aktuelle Integrationseingabe übernommen.

## PW-PERF-E · Gezielter Abschluss aktueller Quellen

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Bei Erstregistrierung ist der Hintergrund ausdrücklich `selected` oder `standard`.
Ein gewähltes Bild hat 2304×576 RGBA-Pixel, exakt gebundene Bytes, Rechtehinweis
und echte Auswahl-/Endfreigabe. Standard ist eine bewusste aktuelle Entscheidung;
keine fehlende Datei ersetzt diese Entscheidung. Der separate aktuelle Editor
verwendet `picross-editor-image-request-v2`, einen unveränderlichen Bildplan und
sein eigenes Journal. Er erhöht nur die betroffene Bildrevision; ohne Änderung
bleiben Bytes, Revisionen und mtimes gleich. Ein historischer Hintergrundauftrag
oder ein Sheetstatus wird nicht als aktuelle Integrationseingabe übernommen.
