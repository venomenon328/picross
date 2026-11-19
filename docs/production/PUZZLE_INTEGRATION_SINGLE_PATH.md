# Ein aktueller Integrationsweg für neue Rätsel

Finale Produktcommits werden mit `python -m tools.publish_git BRANCH --expected SHA` veröffentlicht. Für neue Branches gilt `--expected new`. Arbeitsassets und Wiederaufnahme folgen dem [PW-B-Vertrag](../tools/PW_B_CONTRACT.md).

## Geltung und Quellen

- **Status:** aktiver fachlicher Vertrag für genau einen aktuellen Integrationsweg und eine aktuelle Inhaltsautorität.
- **Freigabe:** [RI-ONE / Issue #660](https://github.com/venomenon328/picross/issues/660). Der Vertrag erteilt keinen Mergeauftrag.
- **Geschlossene Daten-/Transaktionsformen:** [RI](PUZZLE_INTEGRATION.md); Eingangsmanifest und Befehle in [ZA-1](ZA1_ADAPTER.md).
- **Produktionsabschluss:** [Authoring Schritt 5](authoring/PUZZLE_AUTHORING_STEP_5.md).
- **Historische Einführung:** ursprüngliche Norm aus Dokumenthead `f6cad26aaa98127676eae0eae4e58927a4712497` in [PR #662](https://github.com/venomenon328/picross/pull/662), danach Mainergänzungen. Einmalige Bestandsüberführung und ihre Nachweise stehen in §§6 und 8.

## 1. Ziel und Paketgrenze

Für neue Rätsel gibt es genau eine aktuelle Integration, ihre identische
Wiederholung, ihre aktuelle Recovery und ihren Abschluss. Assistent, CLI und
Batch verwenden denselben fachlichen Kern. Lesende Planung und autorisiertes
Schreiben sind Betriebsarten; Mono/Farbe und Hintergrund selected/none/standard
sind Datenvarianten. Ein gemeinsamer Befehlsname vor mehreren alten Writern
erfüllt das Ziel nicht.

Der freigegebene Umfang umfasst gemeinsam:

- den aktuellen Eingang und Export/Übernahme;
- den Inhaltsindex und die direkt benötigten aktuellen Quellen;
- Erstregistrierung, Wiederholung, aktuelle Recovery und Abschluss;
- die einmalige Überführung integrierter Bestandsdaten und ihre direkten Leser;
- die zugehörigen Produktionsaufträge, Normtexte und gezielten Tests.

Eigenständige Editor-, Raster- und Bildänderungen behalten ihre fachliche
Bedeutung und greifen auf dieselbe aktuelle Inhaltsautorität zu. Ein neuer
Spieler, geänderte Spielmechanik, neue Solver-/Difficultyalgorithmen, Editor-UX,
Datenbank, Cacheplattform, allgemeine CI-Neuordnung und Release/Deployment
gehören nicht zum Paket. Kreative Werkzeuge dürfen unterschiedliche Verfahren
verwenden, solange sie denselben finalen Integrationsinput liefern.

## 2. Aktuelle Inhalte als einzige Bestandsautorität

Der aktuelle Inhaltsindex bleibt `content/registry.json`. Seine
Identitäts-/Pfadfelder und die bestehende Metadatenzuordnung werden weiter
verwendet; das historische `entry.production` ist keine aktuelle Bestandsautorität. Insbesondere entfallen Paketpfad/-hash,
ursprünglicher Exportanker, Produktionsrevision/-status/-blocker und
historische Produktions-Difficulty als zweite Autorität.

| Benötigte Information | Verbindliche aktuelle Autorität |
| --- | --- |
| ID, Key, Save-Slot, Definitionspfad, Sichtbarkeit | Aktueller Inhaltsindex; bisherige Identitäten bleiben erhalten |
| Runtime-Rätselrevision, Raster, Hinweise, Palette und Maße | Tatsächliche aktuelle Definition; keine Ableitung aus Produktionshistorie |
| Mono-/Farbmodus | Aktuelles Feld `mode` im Inhaltsindex und Integrationsinput; bei Überführung den vorhandenen wirksamen Modus erhalten |
| Name und Kategorie | Bestehende aktuelle Metadaten und Kategorienzuordnung |
| Reveal und Hintergrundpräferenz/-asset | Aktuelle Bildquellen und Livebytes; nur der derzeit wirksame Zustand |
| Schwierigkeit und Hinzugefügt-Datum | Aktuelle fachliche Bewertungs-/Datumdaten; kein historischer Erzeugerreplay |
| Nutzungsgrundlage | Tatsächlich benötigte aktuelle Rechte-/Attributionsangaben und Notices |

Aktuelle Reveal-/Hintergrundquellen bauen auf dem vorhandenen schlanken
`binding/current`-Prinzip auf. Die Bindung darf aktuelle ID, Definition,
Runtime-Rätselrevision und das aktuelle Asset referenzieren. Sie enthält keine
Kopie von `entry.production`, keinen Originalexport und keine historische
Integrationskette. Aktuelle Inhaltsprüfsummen zur Datei-/Änderungszuordnung
sind zulässig; sie werden nicht zu einem Herkunftsausweis ausgebaut.

`production.package` wird nicht durch eine neue obligatorische Receipt-,
Zertifikats- oder „Aktuellbeleg“-Datei ersetzt. Maße werden aus der Definition gelesen. Der Modus wird als aktuelles Feld
`mode` mit den bisherigen Werten `mono` oder `color` im Inhaltsindex erhalten;
bei der einmaligen Überführung wird der bestehende wirksame Wert aus
`production.mode` übernommen. Definitionen enthalten heute kein eindeutiges
Modusfeld: Einfarbiges Color darf nicht allein wegen der Palettengröße zu Mono
werden. Bereits bestehende aktuelle
Metadaten-, Rating- und Datumquellen werden wiederverwendet, ohne eine zweite
bearbeitbare Datenhaltung aufzubauen.

Die Runtimeprojektion `picross-runtime-registry-v8` bleibt in Form und
Bedeutung unverändert. Bei der Bestandsüberführung bleiben ihre bestehenden
Bytes erhalten; die Projektion des neuen Readers muss dieselben Werte liefern.
Aktive Definitionen/Bilder/Notices, Save-Slots, IDs und Runtime-Rätselrevisionen
werden nicht wegen der Werkzeugumstellung geändert. Auch manuelle aktuelle
Namen/Kategorien, Bewertungen, Datumwerte und Bildpräferenzen bleiben erhalten.

Die Bezeichnung einer fachlichen Difficulty-Methode bleibt zur Bedeutung
einer Bewertung erhalten. Sie verlangt keinen alten Gitcommit oder bytegleichen
historischen Werkzeugstand. Neue Rätsel erhalten weiterhin die aktuelle
fachliche Bewertung; bestehende Rätsel werden nicht ungefragt neu bewertet.

### 2.1 Geschlossene aktuelle Runtimeprojektion

`game/data/registry.json` ist die kanonische UTF-8/LF-Projektion für den Spieler.
Aktuelle Pythonwriter erzeugen ausschließlich `picross-runtime-registry-v8`.
Alle Objekte haben exakt die genannten Felder; der Spieler erhält keine
Produktionsfreitexte, Freigaben oder zusätzlichen Herkunftsfelder.

| Objekt/Feld | Geschlossene Form und Bedeutung |
| --- | --- |
| Wurzel | `format,categories,entries`; `format=picross-runtime-registry-v8`. |
| `categories` | Kategorienobjekte `id,name,order` nach [Kategorienvertrag](../game/CATEGORIES.md), aufsteigend nach `order`. |
| Runtimeeintrag | `id,key,save_slot,definition,reveal,visible,category_id,difficulty,added_at,background,name`. |
| Identität und Pfade | Aktuelle ID, Key, Save-Slot, Definition und wirksames Reveal; Ressourcenpfade relativ zu `game/`, ohne vorangestelltes `game/`. PNG/SVG-Reveal bleibt zulässig. |
| `visible` | Boolean; auch unsichtbare Einträge benötigen eine gültige Kategorie. |
| `name,category_id` | Aktuelle Metadaten; Name 1…128 Zeichen und nicht ausschließlich Whitespace. Keine Ableitung aus historischer Produktion. |
| `difficulty` | Minimale fachliche Projektion nach [SD-Catalog](../difficulty/SD_CATALOG.md) und [SD2-Integration](../difficulty/SD2_INTEGRATION.md), einschließlich dort definierter Null-/Altwerte. |
| `added_at` | Gültiger UTC-Zeitpunkt oder null nach [Katalogsortierung](../game/CATALOG_SORTING.md). |
| `background` | Exakt `status,image_revision,asset`. Aktuelle Pythonquellen verwenden `selected`, `none` oder `standard` und eine positive Revision 1…1.000.000. |
| Hintergrundasset | Nur bei `selected` ein Ref `file,bytes,sha256`, mit `file=art/backgrounds/<id>.png`; bei `none` und `standard` null. Bildgrenzen und Capability gehören ausschließlich zum [Hintergrundvertrag](PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile). |
| Grenzen | Höchstens 256 Kategorien, 10.000 Einträge und 8 MiB Dateibytes; doppelte Schlüssel, Identitäten und ungültige Referenzen sind Fehler. |

`mode` bleibt ausdrücklich in Inhaltsindex und Integrationsinput und ist kein
zusätzliches Runtimefeld. Der Loader unterscheidet einen ungültigen Katalog von
einem gültigen leeren Katalog; unbekannte Zuordnungen entfernen keine Rätsel still.

### 2.2 Spieler-Lesekompatibilität

Der Godot-Loader liest weiterhin die exakten Runtimegenerationen v2 bis v8.
Auch v8 darf einen historischen Hintergrund `legacy` mit
`image_revision=null,asset=null` lesen. Das ist eine bestehende Lesekompatibilität;
aktuelle Pythonquellen erzeugen keine neue `legacy`-Entscheidung. `standard`
ist erst unter v8 zulässig. Die jeweiligen früheren Feldmengen sind im
[gebundenen Kategorienvertrag](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CATEGORIES.md)
und [damaligen PE-Runtimevertrag](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#85-runtime-v8-projektionseinführung-und-folgegenerationen)
nachschlagbar. Diese Spielerreader reaktivieren keine alten Pythonwriter,
Integrationsinputs, Migrationsfunktionen oder Journalgenerationen.

## 3. Ein aktueller Integrationsinput

Der Eingang transportiert die ausgewählten finalen Nutzdaten, ihre benötigten
aktuellen Qualitätsnachweise und die tatsächliche Freigabe. Er besteht aus:

1. vollständiger finaler Definition einschließlich Matrix/Hinweisen/Palette,
   ausdrücklichem aktuellem Modus sowie gewünschter aktueller Identität und
   Pfad-/Save-Slotzuordnung;
2. gewähltem Reveal, Hintergrundpräferenz und gegebenenfalls gewähltem Asset,
   jeweils mit benötigter aktueller Nutzungsgrundlage;
3. Name, gültiger Kategorie und passender aktueller Difficulty;
4. vollständigem am finalen Raster prüfbarem Logiknachweis und der konkreten
   menschlichen Inhalts-/Integrationsentscheidung.

Originalauthoring-ZIP, Kandidatenbaum, Reparaturentstehung, Regelwerkssnapshot,
Producercommit, alte Tool-/Codec-/Modulhashes und der ursprüngliche Exportweg
sind keine Pflichtbestandteile. Aktuelle Arbeitsunterlagen dürfen diese
Informationen für ihre Arbeit enthalten; der Integrator benötigt und erzeugt
daraus keine Produktionsherkunftsautorität.

Es gibt genau eine aktuelle Feldstruktur. Fehlende oder ungültige Nutzdaten
führen zu einem konkreten fachlichen Fehler. Ein Formatbezeichner darf die
aktuelle Struktur benennen, steuert aber keine Liste früherer Generationen.
Keine Herkunftsallowlist, kein Fremdrätsel-Zulassungsprozess und kein
`trusted`-/`skip_checks`-Ersatz für tatsächliche Inhaltsprüfung.

Geprüft werden aktuelle Definitions-/Hinweis-/Farbkonsistenz, Logiknachweis,
Bilddaten, relevante Darstellungsvorgaben, aktuelle Kategorie/Bewertung und
die tatsächlich getroffene Freigabe. Ein gültiger vollständiger
Deduktionsnachweis darf am finalen Raster verifiziert werden; eine zusätzliche
gleiche Eindeutigkeitssuche ist nicht allein zur Herkunftsbestätigung nötig.
Weder Import, Reparatur noch frühere Bildableitung werden dazu nachgespielt.
Unveränderte Raster-/Bildauswahl verlangt keine erneute kreative Abnahme.

Die fünf Produktionsschritte liefern diesen aktuellen Eingang. Der Integrator
muss die bisherige Phasen- oder Paketgeschichte nicht verstehen. Produktive
alte Export- und Parservarianten sind abgelöst; keine parallele
Kompatibilitätsschicht stellt ihre Zulassungsregeln wieder her.

## 4. Ein Kern, begrenzte Transaktion, aktuelle Wiederholung

Der Kern verarbeitet ausschließlich die aktuelle Struktur des Zielbestands.
Er prüft gemeinsame Indizes, die betroffene ID und ihre tatsächlichen
Eingangs-/Schreibdaten. Andere Rätselarchive, alte Original-ZIPs und
unbeteiligte historische Bild-/Produktionsquellen sind keine Abhängigkeiten.
Kein vorgeschalteter Vollscan, Cacheaufbau oder versteckter Hintergrundreplay.

Eine lesende Planung verändert keine Dateien. Die autorisierte Übernahme
prüft ihre tatsächlich konsumierten aktuellen Eingänge und Ziele erneut;
ein früheres Planergebnis ist keine fremde Schreibfreigabe. Mehrfach
verwendete unveränderte Daten dürfen innerhalb des gebundenen Aufrufs
geteilt werden. Es entsteht kein dauerhafter Vertrauenscache.

Aktuelle ID-/Key-/Slot-/Pfadkollisionen, Sperre gegen konkurrierende
kooperative Writer, atomare Veröffentlichung, Journal vor Mutation,
Readback und kontrollierte Rückführung bleiben. Runtime wird zuletzt
veröffentlicht. Die bisherigen getrennten endlichen Publikations- und
Recoverybudgets bleiben, soweit keine konkret begründete Änderung im Paket
geschlossen wird. Keine historische Generationswahl und kein Rückfall in
einen allgemeinen Altwriter.

Ein Journal enthält nur den für diese aktuelle Transaktion erforderlichen
Vorher-/Nachherzustand und ihr eigenes Schreibinventar. Es ist temporäres
Recoverymaterial, kein dauerhaftes Integrationsprotokoll. Nach vollständigem
Abschluss wird es entfernt. Recovery behandelt ausschließlich Transaktionen
dieses aktuellen Kerns. Alte Journalgenerationen werden nicht als aktuelle
Recoveryeingänge interpretiert. Unklare/fremde Daten werden nicht aufgrund
einer angeblich alten Version gelöscht.

Idempotenz vergleicht das **aktuelle fachliche Ergebnis**. Identische
Nutzdaten derselben ID sind schreibfreier No-op, unabhängig von damaligem
Producer oder Integrationsweg. Abweichende aktuelle Daten einer belegten ID
sind ein Konflikt und benötigen den eigenen Revisionsauftrag. Nach einer
späteren echten Revision muss ein alter Integrationsinput nicht erneut
erfolgreich sein oder den alten Ursprung erkennen.

## 5. Completion und Produktionsabschluss

Completion bestätigt die tatsächliche Registrierung der aktuellen gewählten
Lieferung. Der Abschluss vergleicht ihren aktuellen Inhalt mit dem bestätigten
Mainstand und entfernt ausschließlich die ausdrücklich zugehörigen entbehrlichen
Arbeitsdaten. Im laufenden Job/PR darf der tatsächlich geprüfte Maincommit
genannt werden; das erzeugt keine dauerhafte Pflichtbindung im Spielkatalog.

Es wird kein neuer historischer Integrationsreceipt mit Originalexport,
Quellcommit, Integrationscommit oder Paketbaum erzeugt. Für spätere Leser
genügen die aktuellen Nutzdaten aus §2. Nicht mehr vorhandene alte
Arbeitsdateien sind kein Inhaltsdefekt. Neue/offene Arbeit derselben ID,
fremde Daten und benötigte Rechteinformationen bleiben erhalten.

Die PW-Liste und Completion bestimmen den Abschluss aus der aktuellen
Lieferung und dem tatsächlichen Mainzustand. Spätere Bild-/Rasterarbeit
bleibt als eigene offene Arbeit erkennbar.

## 6. Einmalige Bestandsüberführung

**Status: historischer Einführungsauftrag, keine laufende Migrationsfunktion.**
Die feste Startkohorte war auf `main@62401382f58adc2e3d303b19c1ecb1f1dc8a5040`
abgeschlossen. Die Überführung betraf den damaligen Bestand von 62 Einträgen.
Maßgeblich waren der Erhalt aller wirksamen Werte/Livebytes, Runtime,
Saveidentitäten, Rätselrevisionen und Rechte sowie der gezielte Vorher-/Nachherabgleich.

Der vollständige ursprüngliche Auftrag steht in der
[gebundenen Einführungsspezifikation](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_INTEGRATION_SINGLE_PATH.md#6-einmalige-bestandsüberführung)
und [Issue #660](https://github.com/venomenon328/picross/issues/660).
Es gibt keinen dauerhaft installierten Legacyimporter, keine automatische
Migration beim Editorstart und keine parallele Bestandsautorität. Neue/offene
Arbeit und Git-Historie werden durch diesen Vertrag nicht umgeschrieben.

## 7. Betroffene Verbraucher und Normablösung

Die folgenden Verbraucher teilen die aktuelle Inhaltsautorität:

| Bereich | Erforderliche Nachführung |
| --- | --- |
| `target_adapter`, `background_export`, Finalizer/Builder | Ein aktueller Endinput und Export; kein alter/neuer Integrator hinter einem Flag |
| `content_registry`, `catalog_integration` | Aktuelle Inhaltsautorität, keine Paket-/Receiptgeneration als Bestandspflicht |
| `catalog_transaction`, `catalog_publication`, `registration_*` | Genau aktuelle Erstregistrierung/Recovery; gemeinsame Writer anderer Operationen weiter funktionsfähig |
| `editor_change`, Bild-/Raster-/Rating-/Datumreader | Aktuelle Zustandsbindung ohne ursprüngliche Produktionspakete |
| `integrated_content`, Receipt-/Retirementreader | Ergebnisbezogener Abschluss ohne historischen Dauerreceipt |
| PW-Projektor, Präsentation, Lieferungs-/Listenleser, Batch | Derselbe Eingang/Kern und aktueller Abschluss; keine versteckte Ersatzroute |

RI, ZA-1, SD-Catalog, PW/PW-B, Authoring Schritt 5, Hintergrund-/Reveal-/
Editorvertrag, Batchvertrag und Werkzeuganleitung beziehen sich auf diesen einen
Integrationsweg. Laufende Arbeit verwendet genau einen aktuellen Metadatensatz
nach [PW-B](../tools/PW_B_CONTRACT.md); Ansichten und der temporäre RI-ONE-Eingang
werden daraus abgeleitet. Produktbranches übernehmen keine Arbeitsarchive.
Completion prüft die tatsächlichen gewählten Produktbytes auf dem Integrationscommit;
Retirement entfernt den gesicherten eigenen Arbeitsstand nach bestätigtem Mainergebnis,
ohne dessen vorherigen Import nach Main zu verlangen.
Historische Integrationsbeschreibungen und Lieferberichte sind keine aktuellen
Pflichtquellen und dürfen bestehende Entscheidungen nicht nachträglich umetikettieren.

Normativ entfallen im RI-ONE-Scope insbesondere: Unterstützung alter
Produktions-/Export-/Registrierungs-/Recoverygenerationen, Replay zur
Hersteller-/Versionszulassung, Reproduktion einer Integrationsherkunft sowie
dauerhafte Originalexport-/Source-/Maincommit-Receipts.
Unverändert relevant sind fachliche Inhaltsqualität, echte Entscheidungen,
aktuelle Nutzungsrechte, funktionale Datenintegrität und die allgemeinen
Befugnisse aus WORKFLOW. Der Benutzerauftrag bleibt maßgeblich.

## 8. Start, Akzeptanz und Nachweise

Die einmalige Produktionskohorte, RI-ONE-S01, K01–K08, T01–T03 und das
unabhängige Produktreview RI-ONE-A01 sind in
[Issue #660](https://github.com/venomenon328/picross/issues/660) und den dort
zugeordneten Liefernachweisen gebunden. Die frühere Dokument-CI von #662
ersetzt keinen Produkt- oder Migrationsnachweis.

Kleine aktuelle Prüfungen sichern Mono-/Farbinputs mit Hintergrundvarianten,
identische Wiederholung, relevante Inhalts-/IDkonflikte, einen unterbrochenen
aktuellen Schreibvorgang und den betroffenen Bestands-/Verbraucherabgleich.
Testkorpora früherer Integrationsgenerationen sind keine aktuelle Zulassungsprüfung.
Die konkrete Modulauswahl folgt dem aktuellen CI-Vertrag und dem Änderungsumfang.

Der einmalige Aufwandvergleich verwendet gleiche aktuelle Eingänge und Umgebung;
weniger Zweige oder Testfälle sind allein keine gemessene Zeitverbesserung.
Es entsteht keine neue allgemeine Benchmark-/Auditplattform.
