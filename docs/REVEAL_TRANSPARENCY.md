# AT · Transparente Abschlussbilder

**RI-ONE: aktueller Integrationsstand.** Die technischen Integrations-, Quellen-
und Recoveryformen folgen [RI](PUZZLE_INTEGRATION.md) und [ZA-1](ZA1_ADAPTER.md).
Frühere generationsbezogene Einführungsabschnitte sind dafür historisch; sie
stellen keinen zweiten Integrationsweg bereit. Bildqualität, kreative Auswahl,
PNG/SVG und explizite Freigaben bleiben verbindlich.


**PE / #576 · PE-A1 integriert, PE-A2 zur Umsetzung beauftragt:**
Der [Bestandseditor](PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag) ergänzt
einen manuellen Dateiimport ohne Bildbearbeitung und ohne KI-Zwischenschritt.
Variable Revealmaße, Transparenzstandard und historische Herkunft bleiben;
ein Bildwechsel erhöht keine Rasterrevision. PE-A1 trennt
aktuelle Namen und Kategorien von ihren Produktionsangaben. Der unten beschriebene
AT-Weg erhält diese Metadaten über den gemeinsamen Writer; seine Bildverträge
behalten für ihre alten Generationen ihre geschlossene Bedeutung. PE-A2 führt
die folgenden zusätzlichen Formen ausdrücklich ein.

## PE-A2 · Aktueller Revealpfad und ehrliche manuelle Entscheidung

Reveal v3 hat exakt `format,id,record_revision,origin,binding,current,record_hash`.
Die vollständigen Unterformen, Zähler, technische Grenzen und das feste manuelle
Notice-Layout stehen in [PE §8.1–8.2](PUZZLE_EDITOR.md#81-gemeinsame-typen-und-aktive-quellen).
Der unveränderliche nichtrekursive `origin` enthält die vollständige alte
Reveal-v1/v2-Quelle oder einen gültigen sourcefreien Produktionsanker; die äußere
aktuelle `binding` und die aktive Darstellungsentscheidung bleiben getrennt.
Manuelle Eigentümerauswahl/Speichern erzeugt ehrliche manuelle Provenienz,
keine fingierte AT-Freigabe. Technische Prüfung ersetzt keine Motivbeurteilung.

Der bestehende Motiv-/Transparenzstandard bleibt. Zulässige vorbereitete PNGs
und lokale begrenzte SVGs werden bytegleich importiert; andere erlaubte Maße
und Seitenverhältnisse sind möglich. PNG↔SVG wechselt den verwalteten technischen
Pfad samt Source/Notice/Runtime und entfernt ausschließlich die eigene verdrängte
Live-Datei im gemeinsamen Journal. Die unveränderten Definitions-/Produktionseinträge
bleiben ihre historischen Belege. Die alten festen Pfad-/Endungsregeln werden
nur für die ausdrücklich neue Generation durch wirksame Auflösung ergänzt.

Eine spätere reguläre AT-Adoption verwendet Revealrequest v2, Revealplan v5 und
Revealjournal v6 nach [SD_CATALOG](SD_CATALOG.md#pe-a2--geschlossene-v8-quellen-pläne-und-journale).
Sie führt die aktuelle Quelle mit echter `picross-reveal-approval-v1` fort.
`authority={kind,approval,binding}` mit kind production erhält den tatsächlichen
Adoptionstand für spätere vollständige Prüfung des Definitionshashs. Ein folgender
Raster-Rebind ändert nur die äußere Bindung und keine Bildrevision; ursprüngliche
manuelle Quelle oder Approval werden nicht auf neue Bytes umversiegelt.

Katalog und Abschluss verwenden dieselbe aktuelle Datei. Neue/begonnene Rätsel
zeigen weiterhin nur erlaubte eigene Spielerdaten; keine Revealvorschau und
kein neues Preload. Reine Bildpflege erhält ID/Key/Slot, Definition-/Rasterrevision,
Matrix/Hinweise/Palette, Rating/Added, Saves/Redo/Abschluss und Recent-Marker.
Bestehende displayseitige Glättung bleibt abgeleitete Darstellung und ändert
keine Originalbytes. Keine Runtimefreistellung, neue Bildproduktion oder
zusätzliche persönliche Buchprobe durch PE-A2.

Vertragsstand: 19.10.2026 · Vertrag 2.0 / AT-A-P01 ·
[AT / #256](https://github.com/venomenon328/picross/issues/256).

**Statusfortschreibung 27.10.2026:** AT-A ist über
[PR #263](https://github.com/venomenon328/picross/pull/263) auf
`a0cb25eda49d29d3062fd3bcfeab9fda220c7aa9`, AT-B mit allen 26 freigegebenen
Bildrevisionen über [PR #264](https://github.com/venomenon328/picross/pull/264) auf
`8dac7a69d360550b0b23a202dced72698babd572` in `main` integriert.
Die folgenden Vorbereitungs-/Lieferstatus, insbesondere „AT-B-F01 beauftragt“
und „AT-B-R01 offen“, beschreiben frühere Stände und erteilen keinen erneuten
Arbeitsauftrag. Historische Nachweise und ihre damaligen Urteile bleiben gebunden.
Der Abschluss der Bildarbeitsdaten nach [CI2](CI_SLIMMING.md) und
[Authoring §9](ai-workflows/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung)
ist mit CI2-E auf `chore/417-ci2-e-cleanup` /
[Draft-PR #423](https://github.com/venomenon328/picross/pull/423) ausgeführt;
[E-T01](CI2_E_VERIFICATION.md) bindet Bereinigung und technische Nacharbeit.
Das [erste E-R01](https://github.com/venomenon328/picross/pull/423#pullrequestreview-5661141319)
ist mit den Befunden B-01/B-02 durchgeführt. Erneutes separates qualifiziertes
Review des korrigierten Heads bleibt vor Merge erforderlich; der CI2-E-Abschluss
ist noch nicht auf `main` integriert. Diese Statuspflege erteilt keinen neuen
Bereinigungs-, Merge-, Deployment- oder Releaseauftrag.

## Auftrag, Quellen und Wirksamkeit

Der Eigentümer hat transparente Abschlussbilder einschließlich ihrer verdienten
Katalogvorschau als Spezifikation freigegeben. AT-A ist nach qualifiziertem
AT-A-R01 über PR #263 auf `a0cb25eda49d29d3062fd3bcfeab9fda220c7aa9` integriert.
Umsetzungsvorbereitung V4 beauftragt ausschließlich AT-B-V01: alle 26 gebundenen
Bestandsbilder, Einzelbelege, Authoringpakete und gemeinsame Bild-/Endfreigabevorlage
im Draft-PR. [AT-B-V01-Bericht](AT_B_VERIFICATION.md) führt den aktuellen Stand.
Dieser V01-Haltepunkt wurde anschließend durch die tatsächliche
[Eigentümerabnahme aller 26 Bilder](AT_B_OWNER_APPROVAL.md) erfüllt. AT-B-F01
beauftragt jetzt die kontrollierte Übernahme über `catalog_reveal plan/adopt`
und AT-B-T01. Rasterproduktion, echte Spielstände, Merge, Deployment und
Issue-Abschluss bleiben ausgeschlossen; qualifiziertes separates AT-B-R01 offen.

Historische Spezifikationsbasis ist
`main@b019a32f8854070dfa3d7bb580fd35a3cd4a5686`; P01 synchronisiert den
bestehenden Spezifikationsbranch mit
`main@e454dd580fd1dd2690d952d8e8a9a2f8dc5e604c`, einschließlich integrierter
Chromium-/CI-258-Regeln. Der technische Vertragsabschluss aus
Umsetzungsvorbereitung V2 wurde durch PR #257 als Dokumentfortschreibung auf
`main@9cc58651518e3a28e97f46932d69554210b0abcb` integriert; dies ist die
geprüfte Basis der AT-A-Implementierung.
Das Issue führt aktuelle
Paketaufträge, Lieferstände und Abnahmen. Dieser Vertrag führt die dauerhaften
Entscheidungen. Er ergänzt gezielt [Produkt](PRODUCT_DEFINITION.md),
[Design](DESIGN_CONCEPT.md), [Katalogdarstellung](CATALOG_PRESENTATION.md),
[Rätselproduktion](PUZZLE_PRODUCTION.md),
[PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md),
[ZA-1](ZA1_ADAPTER.md), [Kategorien](CATEGORIES.md),
[gemeinsame Katalogtransaktionen](SD_CATALOG.md) und [CI-Policy](CI_POLICY.md).
Historische Lieferberichte behalten ihren damaligen Umfang und Nachweisstand.

## 1. Ausgangsbefund und Ziel

Die geprüften aktiven PNGs `knoblauch_001.png`, `japanische_teekanne_001.png`
und `warnemuende_001.png` in `game/art/content/` sind deckende RGB-Bilder.
Die ersten beiden besitzen neutrale helle Außenflächen; die Teekanne zusätzlich
einen entsprechenden Innenraum im Griff. Warnemünde ist eine vollständige Szene
mit motivisch relevanter Umgebung. Diese Stichproben begründen die Paketbildung;
sie sind keine vollständige Bestandsaufnahme oder bereits erfolgte Bildabnahme.

Die reguläre Karte in [catalog_card.gd](../game/ui/catalog_card.gd) verwendet
denselben Revealpfad wie der Abschluss. [reveal.gd](../game/ui/reveal.gd) zeichnet
in diesem Modus die Textur, ohne einen weißen Bildkasten zu ergänzen.
[completion.gd](../game/ui/completion.gd) übernimmt ebenfalls diese Textur.
Der helle rechteckige Hintergrund liegt bei den geprüften Beispielen in den
Bildbytes. Die vorhandene Alphakantenkorrektur und proportionale Glättung lösen
keine Motivfreistellung eines deckenden Bildes.

Ziel ist ein tatsächlich transparentes freigegebenes Abschlussasset: Neutrale
Außenflächen und echte Aussparungen lassen in beiden Ansichten den vorhandenen
Papieruntergrund sichtbar. Keine separate, anders bearbeitete Katalogfassung.

## 2. Verbindlicher Bildstandard

- Neutrale weiße oder helle Flächen außerhalb des Motivs und echte Aussparungen
  werden transparent. Ein Alphakanal allein genügt nicht, wenn die störende
  Fläche weiterhin deckend bleibt.
- Weiße und helle Motivteile bleiben erhalten, ebenso Farben, Konturen, feine
  Details, Pose, Perspektive, Proportionen, Ausschnitt und Komposition. Helligkeit
  allein entscheidet nicht, ob ein Pixel zum Hintergrund gehört.
- Alphakanten bleiben auch in kleiner Darstellung und Überblendung sauber.
  Produktionsprüfung am Original groß/klein, bei Bedarf auf neutralem Grund oder
  Schachbrett; keine routinemäßigen Buch-/Katalogmontagen, Fadeproben oder
  Testintegrationen, auch nicht in späteren Phasen. Bestehende Render-/Integrations-
  tests tragen die technische Garantie; kurze Urteile im vorhandenen Bericht.
  Keine hellen Matten/Säume, ausgeschnittenen Motivdetails
  oder ausgefransten Konturen; teiltransparente Randpixel bleiben möglich.
- Vollständige Szenen erhalten eine bewusste motivbezogene Bearbeitung. Prägende
  Umgebung und räumliche Beziehungen bleiben erhalten; transparente Außenfreiräume
  oder eine passende Vignette werden konkret vorgelegt und neu freigegeben.
  Himmel, Meer oder Boden werden nicht pauschal entfernt. Die Bezeichnung
  „Szene“ ist keine automatische Ausnahme für deckende Rechtecke. Erfordert eine
  Lösung weitergehende Motiv-/Kompositionsänderungen, sind diese vor Bearbeitung
  beziehungsweise Übernahme ausdrücklich zu entscheiden.
- Neue Bilder werden bereits für die Bildauswahl transparent vorbereitet und in
  diesem Stand freigegeben. Nachträgliche Freistellung ist eine neue Bildrevision,
  keine stillschweigende Änderung der bereits freigegebenen Datei.
- Die technische Kette erhält Alpha vom freigegebenen PNG beziehungsweise
  bestehenden SVG bis zu Export, Integration, Import und Darstellung. Keine
  JPEG-/deckende Zwischenstufe und kein globaler Weiß-/Farbfilter im Renderer.

Bestehende Lanczos-/Linear-Glättung, Ressourcengrenzen und proportionale Darstellung
bleiben. AT ändert weder Fragezeichen noch eigene Füllminiatur, Spoiler-/Recovery-
grenzen oder den Ablauf der transienten EA-Enthüllung von 2,15 Sekunden. Der
vorhandene Papieruntergrund wird nicht durch eine neue Ersatzfläche überdeckt.
Die früheren KE-/KU-Vorgaben unveränderter Originalassets beschreiben deren
Darstellungsarbeit; AT erlaubt gezielt separat freigegebene Bildrevisionen.

## 3. Reine Bildrevision: Identität und historische Bindungen

Eine reine Bildrevision ersetzt nur das freigegebene Abschlussbild samt den dafür
notwendigen aktuellen Revisions-/Freigabedaten. Sie ist kein Rasterupdate.

| Bereich | Verbindliche Grenze |
| --- | --- |
| Rätsel | Definitionsbytes und ihr Hash, Matrix, Hinweise und Puzzle-Runtime-Revision bleiben unverändert. Keine neue Logik-, Eindeutigkeits- oder Schwierigkeitsanalyse allein wegen der Bildänderung. |
| Identität und Auffindbarkeit | ID, Schlüssel, Save-Slot, Definitions-/Bildpfad, Kategorie und Sichtbarkeit bleiben erhalten. Die Definition bindet bereits den aktiven Bildpfad; deshalb wird am bestehenden Ressourcenpfad ersetzt. |
| Fortschritt | Vorhandene Spielstände bleiben gültig; kein Reset, keine Migration und keine Rückstufung eines begonnenen oder gelösten Rätsels. |
| Metadaten | Bestehende Schwierigkeitsbindung und `added_at` einschließlich ihrer Herkunft bleiben byte-/wertgleich; das Bild ist keine neue Katalogaufnahme. |
| Ursprüngliche Freigabe | Originalhandoff, Bildauswahl, Exportmanifest und kompakter Integrationsbeleg behalten ihre ursprünglichen Bytes und Aussage. Keine rückwirkende Umschreibung auf den neuen Bildhash. |
| Aktuelle Bildfassung | Getrennte, versionierte Bindung an Rätsel-ID, unveränderte Definition, ursprünglichen Integrationsbeleg, Vorgänger-/Neubildhash, konkrete Bildrevision und tatsächliche Freigabe. Herkunft, Nutzungsrechte und nötige neue Hinweise werden nachvollziehbar erhalten beziehungsweise ergänzt. |

Der vollständige Vergleich historischer Einträge bleibt gültig. Der Validator
prüft künftig zusätzlich, ob eine erlaubte aktive Bildrevision genau diese
historische Ausgangsbasis und die tatsächlich vorhandenen neuen Bildbytes bindet.
Er darf nicht einfach den alten Revealhash ignorieren oder den alten Beleg
neuberechnen. Die neue aktive Bindung bleibt auch nach der regulären Bereinigung
von Produktionsmaterial prüfbar; eine spätere Bildänderung verlangt keine
Rekonstruktion aller längst ausgeräumten historischen Produktionsdateien.

Die neue Bildfreigabe bindet die tatsächlichen Bytes. Bild-/Motiv-/Rasterkonsistenz
und Endkontrolle folgen PUZZLE_AUTHORING. Eine gemeinsame Freigabe mehrerer Bilder
ist möglich, wenn jede ID, Datei, Bildrevision und jeder Hash eindeutig aufgeführt
ist. Eine Freigabe der Spezifikation oder einer bloßen Vorschau ohne Dateibindung
ersetzt diese Entscheidung nicht.

## 4. Gemeinsamer technischer Vertrag für AT-A

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Der aktuelle Editor prüft den vollständigen ausgewählten Bildplan einschließlich
Vorher-/Nachherbytes, Rechtehinweis und ausdrücklicher Entscheidung. Das Reveal
bleibt PNG oder SVG gemäß §2. Reine Bildänderungen verändern weder Raster,
Schwierigkeitsbewertung, Speicherslot noch Hinzugefügt-Datum. Aktuelle Quellen
führen Bild-/Recordrevision und Identitätsbindung; ein Bildplan besitzt keine
Abhängigkeit von einem früheren Produktionspaket. Recovery prüft die aktuelle
Journalgeneration und alle gebundenen Zielbytes, bevor es eigene Daten entfernt.

## 5. Pakete und Abnahme

Standard ist ein Implementierungs-PR je Paket. AT-A wird vor AT-B integriert;
der Zwischenstand muss mit allen gültigen bisherigen Inhalten kompatibel sein.
Ein Spezifikations-PR schließt das AT-Issue und die Umsetzungsgates nicht.

| Paket | Ergebnis | Abhängigkeit und Grenze |
| --- | --- | --- |
| AT-A · Sicherer Bildrevisionsweg | Produktionsstandard, konkrete Daten-/Werkzeugverträge, gemeinsame Quellen-/Transaktionsintegration, Alpha-Erhalt und feste synthetische Regressionen einschließlich notwendiger Dokumentation/CI-Zuordnung. | Umsetzungsvorbereitung V3 beauftragt ausschließlich AT-A samt T01 und Draft-PR. Kein Austausch realer Katalogbilder; unabhängiges R01 und Merge bleiben separat. |
| AT-B · Vorhandene Bilder umstellen | Vollständiger gebundener Startbestand, konkrete Freistellungen/Szenenlösungen, neue Bildfreigaben, Konsistenzkontrollen und kontrollierte Übernahme. | Integriertes AT-A und späterer Inhaltsauftrag. Technische Vertrags-/Recoveryfehler gehen in AT-A beziehungsweise benannte technische Nacharbeit zurück. |

### AT-A · Nachweise

AT-A-T01 bindet den finalen Quell-/Basisstand, tatsächliche ausgewählte Checks und
einen getrennten Selbstreview. Die feste synthetische Prüfung umfasst:

- Gültiger Altstand, erste und weitere Bildrevision, Wiederholung als echter No-op
  sowie byte-/wertgleiche Definitionen, Identitäten, Revisionen und übrige Metadaten.
- Falsche Identität/Definition, manipulierte Freigabe/Hashes, fehlende oder defekte
  aktive Bindung, veralteter Plan und konkurrierende Änderung; keine Teilübernahme.
- Binäre Altbytesicherung, Fehler an den Schreib-/Abschlussgrenzen, unterbrochene
  Übernahme, wiederholtes Recovery und widersprüchliche Fremdquellen; außerdem
  Erhalt der aktiven Bildfassung bei späteren gemeinsamen Operationen.
- Ein synthetisches Bild mit weißem Motivteil, Innenaussparung und weichen
  Alphakanten über die tatsächliche Export-/Importkette. Kleine Katalogansicht
  einschließlich Hover, Überblendung, Abschluss und Wiederöffnung zeigen die
  erwartete Transparenz und saubere Kanten bei UI 100/125 %.
- Ein bestehender synthetischer Save bleibt über den Bild-/Exportwechsel begonnen
  beziehungsweise gelöst. Neue/gesperrte Zustände offenbaren das Bild nicht früher;
  weder Reset noch Puzzle-Revisionmigration wird ausgelöst.

Technische Darstellung und Savewechsel werden in den betroffenen nativen Windows-
und Chromiumwegen belegt. Der tatsächliche Gesamtdiff wählt weitere bestehende
Pflichtchecks gemäß CI-Policy; AT verändert keine Plattform- oder Browsermatrix
und übernimmt keine frühere paketbezogene Ausnahme als allgemeine Freigabe.
Ein bloßer Start ersetzt keinen betroffenen Darstellungs-/Persistenznachweis.
AT-A-R01 ist ein separater qualifizierter Review des finalen Heads vor Merge.

### P01-D07 · Konkrete spätere Fälle und Artefakte

Die folgende Zuordnung ist AT-A-Lieferumfang, **durch P01 nicht ausgeführt**.
Neue Tests sind allgemeine feste synthetische Fälle und lesen keine realen
Katalogbilder, Definitionen oder daraus abgeleiteten Kopien.

| Fälle | Anschlussstelle und erwartetes Ergebnis |
| --- | --- |
| AT-S01 Quellenlebenszyklus | Neuer `tests/puzzle_production/test_catalog_reveal.py`: erste/zweite Bildrevision jeweils vor/nach Cleanup, Noticeerweiterung, Quellenvalidierung. Erwartet exakt +1 Bild-/Recordrevision, unveränderte Definition/Runtime/Rating/Added/Originalbelege; Cleanup selbst ändert keinen AT-Record. |
| AT-S02 Folgeoperationen | `test_catalog_integration.py`, `test_content_update.py`, `test_integrated_content.py`: historisches `register` nach AT echter No-op; Rasterexport mit exakt aktivem Bild erzeugt nur eigene neue Produktions-/SD-Bindung plus AT-Bindungsappend. Altes/anderes Bild wird vor Mutation abgewiesen; aktive Notice und Added bleiben gleich. |
| AT-S03 Snapshot und No-op | `test_catalog_added.py`, `test_catalog_review.py`, `test_catalog_reveal.py`: SD-/Added-Adoption und Sync erhalten AT bytegleich. Ältere Pläne nach AT/Receipt-/Kategorie-/Registryänderung stoppen. Identischer AT-Plan unmittelbar nach eigener Adoption erhält sämtliche Bytes, Revisionen und Nanosekunden-mtimes; kein Lock/Temp/Rewrite. Fehlende/ähnliche/fremde Ziele sind kein No-op. |
| AT-S04 Negative Daten | `test_catalog_reveal.py`: falsche ID/Definition/Revision, Freigabe-/Notice-/Herkunft-/Kettenhash, doppelte/fremde JSON-Schlüssel, falsche Typen/null/UTC, fehlende erwartete Quelle, Alias-/Zusatz-/Fremd-ID-Dateien, Symlink/Hardlink/Reparsepunkt, Grenzen unmittelbar unter/auf/über Limit. Erwartet 2 oder Ressourcenabbruch 4, nie Teilübernahme/Fallback. |
| AT-S05 Journal und Unterbrechung | Neuer `tests/puzzle_production/test_reveal_recovery.py` plus `test_ke_recovery.py`: alle P0–P6/R0–R2-Grenzen, jedes Bild und Textziel einer Mehrfachadoption, Journalaufbau vor/nach Lock, Temp-Teilbytes, erneuter Kill während Recovery, eigenes Alt/Neu und fremde Quellen/Lock/Temps. Erwartet gültiger vollständig alter Checkout nach Recovery, fremde Daten und Journal bei Blockade unverändert. |
| AT-S06 Versionen und Limits | `test_reveal_recovery.py`: jede unterstützte/gesperrte Zeile der Journalmatrix, alte Journale mit ungebundenem AT blockieren. Zwei 32-MiB-Bildseiten, falsche Base64-Länge/Padding/Hash, 24-/128-MiB-Grenzen und zu große Mehrfachpläne. Dispatch lädt/dekodiert keine unzulässigen Größen; keine alte Grenze wird angehoben. |
| AT-N01 Darstellung | `tools/kat2_product.py` / `game/tests/kat2_probe.gd`, `tools/ea_product.py` / `game/tests/ea_probe.gd`: unabhängiges synthetisches Reveal mit hellem Motivteil, Innenaussparung und weichen Alphakanten durch tatsächliche Export-/Importkette. Kleine Karte samt Hover, EA-Überblendung, Endbild und Wiederöffnung zeigen Papierdurchsicht ohne Saum/Detailverlust. UI100/125 nach gemeinsamer Dreiermatrix, kein zusätzliches Vollkreuz. |
| AT-N02 Windows/Savewechsel | Native Windows-Probe derselben gebundenen synthetischen EXE/PCK-Folge: begonnene und gelöste Saves vor Bildwechsel erzeugen, echten zweiten Export mit neuen Bildbytes bauen, unter demselben isolierten Profil neu starten. Zell-/History-/Status-/Definitionsrevisionen bleiben gleich; Neu/gesperrt laden/zeigen das Reveal nicht vorzeitig, Reset bleibt ausdrücklich. Start/Export allein genügt nicht. |
| AT-W01 Chromium | `tools/web_tests/group_catalog.py`, `group_completion.py`, `group_persistence.py`, feste `fixtures.py` und `contract.py`: entsprechende Transparenz-/Hover-/Abschluss-/Wiederöffnungsfälle sowie begonnener/gelöster Save über zwei echte Exporte, Reload und Browserprozessneustart auf gleichem isolierten Origin/Profil. Keine vorzeitige Enthüllung, Revisionmigration oder Rückstufung. |
| AT-C01 Auswahl | `tools/test_ci_scope.py`: kanonischer neuer AT-Inhaltspfad und regulärer 100644-Modus positiv; Großschreibung, Fremdendung/-unterpfad, ausführbar/Link/Submodul, Rename und Löschung negativ beziehungsweise beide Seiten geprüft. Werkzeug-/Test-/Harnessänderung wählt die tatsächliche Vereinigung der Pflichtbereiche. |

AT-A-T01 bindet technische JSON-Berichte, erwartete/tatsächliche Bildregionen,
unveränderte Saveinhalte vor/nach Wechsel und die beiden Export-/Assethashes an
Head/Basis/Checkout und Run. Native Anschlussartefakte bleiben `kat2/summary.json`
mit kleinen Originalausschnitten und `ea/*.json`, `ea/motion.apng`,
`ea/final-*.png`; die Windows-Probe dokumentiert echte EXE/PCK-Hashes und
Profil-/Prozessfolge. Chromium bindet Buildmanifeste, Gruppenberichte,
Pflichtbilder und `web-result.json` über den bestehenden Resultprüfer.
AT-A ergänzt dafür das feste Szenario-/Artefaktinventar gemeinsam mit den
Harnessänderungen; kein bloßes neues Erfolgsflag ohne Datei-/Inhaltsprüfung.

AT-A-T01 einschließlich getrenntem Selbstreview und qualifiziertes separates
AT-A-R01 bleiben vor Implementierungsmerge. **Kein AT-A-M01 und kein neues
P01-Produktgate.** Bildbytefreigaben, Motiv-/Rasterkonsistenz und Eigentümerabnahme
des echten Bestands bleiben AT-B. Firefox wird gemäß integrierter #261-Policy
nicht automatisiert gestartet; keine alten Workflows oder historischen Reruns.

### AT-B · Bestands- und Bildabnahme

AT-B inventarisiert sämtliche aktiven Abschlussbilder eines konkret genannten
Startcommits. Je ID werden Ressourcenpfad, bisheriger Hash/Freigabebezug, Befund
und gewählte Bearbeitung geführt; spätere Umfangsänderungen werden begründet.
Jedes geänderte Bild erhält Vorher/Nachher, konkrete Dateifreigabe und Sichtkontrolle
im Katalog-/Abschlusskontext. Die drei Ausgangsstichproben begrenzen den Bestand
nicht. Szenische Motive sind vollständig einzuplanen.

Die Abschlussliste weist jede Start-ID als bereits konform oder mit neuer
freigegebener und integrierter Bildrevision aus. Offene beziehungsweise blockierte
Motive bleiben sichtbar offen; ein ungeprüfter Szenenverzicht zählt nicht als
Erfüllung. Das Paket ist erst mit vollständiger Disposition und erfülltem Ziel
abgeschlossen.

AT-B-T01 bindet Inventar, Bildfreigaben, Konsistenz-/Endkontrolle, Übernahmeplan,
Ergebnis, identische Wiederholung und Kontrolle der tatsächlich integrierten
Dateien samt getrenntem Selbstreview. Definitionen, Revisionen, Identitäten und
übrige Metadaten bleiben nachweislich unverändert. AT-B-R01 ist die separate
finale Inhalts-/Integrationsprüfung; tatsächliche Bildfreigabe und
Eigentümerabnahme werden ausdrücklich an den vorgelegten Stand gebunden.

## 6. Prüfgrenzen und Nichtziele

Die aktuelle Dokumentlieferung nutzt Dokumentvalidator, schnelle Werkzeugtests,
vollständige Diffprüfung und die ausgewählte CI samt `ci-required`. Sie ist kein
Nachweis implementierter AT-Funktionalität oder bereits transparenter Bildbytes.

AT-A verwendet feste synthetische Regressionen. AT-B prüft tatsächliche Bilder
im Inhaltsauftrag außerhalb der CI; die Sichtkontrolle wird nicht zu einem
automatischen Katalog-Replay oder einem vollständigen Probespiel je Rätsel.
Reine Inhalts-PRs erhalten den allgemeinen [Quellen-/Plankern ohne Player-Build](CI_WORKFLOW_V2.md).
Zusatzmodule werden anhand des vollständigen Diffs im aktuellen Paketplan begründet;
keine automatische Vollauswahl oder erneute Bild-/Rätselzertifizierung. Neue
Nachweispfade erhalten einen konkreten Zweck und Lebenszyklus.

Kein neues Kataloglayout, kein anderer Enthüllungsablauf, keine Neubewertung oder
Neuzertifizierung des Katalogs, keine Änderung von Rätsellogik, Saveformat oder
Hinzugefügt-Datum, keine allgemeine Registry-/Plattform-/Deploymentumstellung.
Aktuelle Paketstände und spätere Startprüfung stehen im Issue; Modellauswahl wird
erst bei ausdrücklich beauftragter Umsetzungsvorbereitung aktualitätsgebunden
vorgenommen.


## HP-I1c · Versionierte aktuelle Hintergrundbindung

RI-ONE ersetzt die frühere mehrgenerationige Integrations-/Receiptstrecke.
Maßgeblich sind [RI](PUZZLE_INTEGRATION.md), [ZA-1](ZA1_ADAPTER.md) und
[RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md). Erstregistrierung verwendet genau
`picross-integration-input-v1`, Registry v5, Revealquelle v5 und Hintergrundquelle
v7; Runtime v8 bleibt unverändert. Die aktuelle Quelle bindet Identität und
Livebytes, keine Produktionsarchive, Producer- oder Regelbuch-Allowlist.
Bild-, Raster-, Metadaten- und Hintergrundrevisionen bleiben eigene Operationen
nach [PE §13](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Historische Formbeispiele dieses Dokuments erteilen keine aktuelle Schreibbefugnis.

Der aktuelle Editor prüft den vollständigen ausgewählten Bildplan einschließlich
Vorher-/Nachherbytes, Rechtehinweis und ausdrücklicher Entscheidung. Das Reveal
bleibt PNG oder SVG gemäß §2. Reine Bildänderungen verändern weder Raster,
Schwierigkeitsbewertung, Speicherslot noch Hinzugefügt-Datum. Aktuelle Quellen
führen Bild-/Recordrevision und Identitätsbindung; ein Bildplan besitzt keine
Abhängigkeit von einem früheren Produktionspaket. Recovery prüft die aktuelle
Journalgeneration und alle gebundenen Zielbytes, bevor es eigene Daten entfernt.

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

Der aktuelle Editor prüft den vollständigen ausgewählten Bildplan einschließlich
Vorher-/Nachherbytes, Rechtehinweis und ausdrücklicher Entscheidung. Das Reveal
bleibt PNG oder SVG gemäß §2. Reine Bildänderungen verändern weder Raster,
Schwierigkeitsbewertung, Speicherslot noch Hinzugefügt-Datum. Aktuelle Quellen
führen Bild-/Recordrevision und Identitätsbindung; ein Bildplan besitzt keine
Abhängigkeit von einem früheren Produktionspaket. Recovery prüft die aktuelle
Journalgeneration und alle gebundenen Zielbytes, bevor es eigene Daten entfernt.

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

Der aktuelle Editor prüft den vollständigen ausgewählten Bildplan einschließlich
Vorher-/Nachherbytes, Rechtehinweis und ausdrücklicher Entscheidung. Das Reveal
bleibt PNG oder SVG gemäß §2. Reine Bildänderungen verändern weder Raster,
Schwierigkeitsbewertung, Speicherslot noch Hinzugefügt-Datum. Aktuelle Quellen
führen Bild-/Recordrevision und Identitätsbindung; ein Bildplan besitzt keine
Abhängigkeit von einem früheren Produktionspaket. Recovery prüft die aktuelle
Journalgeneration und alle gebundenen Zielbytes, bevor es eigene Daten entfernt.
